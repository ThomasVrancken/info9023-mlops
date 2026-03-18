# Lab 7 [Sprint 4, W8]: GPU Serving with vLLM

## 0. Introduction

In production ML systems, serving large language models efficiently is one of the most challenging infrastructure problems. A naive approach, loading the model into a Python process and running forward passes one request at a time, wastes GPU memory and leaves most of the hardware idle. This lab introduces vLLM, a high-performance serving engine that solves this problem, and walks you through three deployment strategies for it on Google Cloud, going from raw infrastructure to fully managed.

By the end of this lab you will have:
- Deployed Qwen3.5 9B on a GPU VM (IaaS) using vLLM
- Used the OpenAI-compatible API to interact with your own hosted model
- Stored model weights in GCS and mounted them into a serverless container
- Deployed the same model on Google Cloud Run with a GPU and scale-to-zero behaviour

A third strategy, Google Vertex AI, is presented in the comparison below but not implemented in this lab. It represents the fully managed end of the spectrum, where Google handles not just the infrastructure but also model versioning, traffic splitting, and monitoring out of the box.

| Feature | Part 1: GPU VM (IaaS) | Part 2: Cloud Run (Serverless) | (Reference) Vertex AI |
| :--- | :--- | :--- | :--- |
| Service Model | Infrastructure as a Service (IaaS) | Platform as a Service (PaaS) | Machine Learning as a Service (MLaaS) |
| Responsibility | You manage OS, drivers, and runtimes | Google manages the host and drivers | Google manages everything |
| Scalability | Manual | Automatic, scales to zero when idle | Automatic, with built-in autoscaling |
| Networking | Manual (firewalls, SSH tunnels) | Automated (built-in HTTPS endpoint) | Automated, with VPC support |
| Cost structure | Flat hourly rate, always-on | Pay-per-use, billed per second | Pay-per-use, higher per-hour rate |

---

### 0.1. Background

#### Why a dedicated serving engine?

When you call `model.generate()` in a plain PyTorch script, each request occupies the GPU entirely while it runs and all other requests wait. As soon as traffic exceeds one request per second, this becomes a bottleneck.

vLLM solves this with two core mechanisms.

**PagedAttention.** During autoregressive generation the model maintains a KV-cache (key-value pairs for every token in the context). In standard implementations this cache is pre-allocated as one large contiguous block per sequence, wasting memory on padding. PagedAttention manages the KV-cache in small non-contiguous pages, the same idea as virtual memory in operating systems. This reduces memory waste and allows the GPU to hold more concurrent sequences.

**Continuous batching.** Instead of waiting for a fixed batch to be fully assembled before running the GPU, vLLM adds newly arrived requests to the running batch at every generation step. Sequences that finish early free their memory immediately and their slot is filled by the next waiting request. GPU utilisation stays high regardless of variable request lengths.

Together these two mechanisms allow vLLM to serve 10-20x more requests per second than a naive implementation on the same hardware.

#### The OpenAI-compatible API

In this lab you will interact with vLLM through HTTP requests, not by importing a Python library. vLLM is packaged as a Docker image (`vllm/vllm-openai`). You run that image on a GPU machine, it loads the model and starts an HTTP server on port 8000, and you send requests to it from your own machine.

The HTTP interface vLLM exposes is deliberately identical to the OpenAI API: same endpoints (`/v1/chat/completions`), same JSON request fields, same response format. This means you can use the standard `openai` Python client to talk to it, and any application already written for OpenAI works against your self-hosted server with a single line change. Nothing is sent to OpenAI. The model runs on your own infrastructure.

The only two differences you will notice in the code are:
- `base_url` is set to your server address instead of `api.openai.com`
- `api_key` is set to any non-empty string (vLLM requires the field to be present because the client library enforces it, but it ignores the value by default)

#### The model: Qwen3.5 9B

[Qwen3.5](https://huggingface.co/Qwen/Qwen3.5-9B) is Alibaba's latest open model family. The 9B variant:
- Has 9 billion parameters. In BF16 this occupies roughly 18 GB VRAM, which fits on a single L4 (24 GB) with headroom for the KV cache
- Has built-in reasoning: the model can produce a `<think>...</think>` block where it reasons step-by-step before giving its final answer, similar to OpenAI o1
- Has been fine-tuned for instruction following and tool use
- Is fully open with no gating on Hugging Face, so no token or terms acceptance is needed

---

### 0.2. Prerequisites

#### GCP prerequisites

1. A Google Cloud project with billing enabled
2. The Google Cloud CLI installed and authenticated
3. Enable the required APIs. It should already be enabled if you completed previous labs, but if not, welcome to these labs sessions... Better late than never!
```bash
gcloud services enable compute.googleapis.com run.googleapis.com storage.googleapis.com --project=YOUR_PROJECT_ID
```

---

### 0.3. Cost warning

This lab uses GPU resources that are billed by the minute. Read this before you start.

**GPU VM (Part 1).** A `g2-standard-8` with one L4 costs roughly $0.70/hour. The VM is billed as long as it is in the `RUNNING` state, even if no requests are coming in. Stop or delete it as soon as you are done with Part 1.

**Cloud Run with GPU (Part 2).** An L4 on Cloud Run costs roughly $0.65/hour of active GPU time. You are only billed while the container is actually running (i.e. handling a request or starting up). However, every failed deployment attempt that reaches the startup phase still consumes GPU time. If the container fails to start repeatedly, those minutes add up. Keep an eye on your billing dashboard if something is not working.

**Practical tips to avoid surprises:**
- Delete failed Cloud Run revisions if you are iterating on the deployment command.
- Do not leave a Cloud Run service deployed overnight if you are not using it; delete it and redeploy when needed.
- Check your current spend at any time with:
```bash
gcloud billing accounts list
```
Then visit [console.cloud.google.com/billing](https://console.cloud.google.com/billing) to see a breakdown by service.

---

## Part 1: GPU VM on Compute Engine

In this part you provision a virtual machine with an NVIDIA L4 GPU, start vLLM inside a Docker container on that machine, and talk to it over an SSH tunnel. You are in full control of the underlying infrastructure: the OS, the GPU driver, Docker, and the network configuration are all yours to manage.

### 1. GPU quota

Compute Engine GPU instances require available quota in your project. Check your current quota:
```bash
gcloud compute project-info describe --project=YOUR_PROJECT_ID | grep -A2 GPUS
```

You should see something like:
```
metric: GPUS_ALL_REGIONS
usage: 0.0
- limit: 5.0
```

Look at the `GPUS_ALL_REGIONS` entry. If the limit is 0, you need to request a quota increase before you can create a GPU VM:
1. Go to [console.cloud.google.com/iam-admin/quotas](https://console.cloud.google.com/iam-admin/quotas).
2. Filter by `GPUS_ALL_REGIONS`.
3. Click **Edit quotas** and request a limit of at least 1.
4. Fill in the form with your use case (e.g. "I am taking an MLOps course and need to deploy a GPU instance for a lab exercise").
5. Submit the request. Approval usually takes a few minutes to a few hours.

If the limit is already 1 or more, you are good to proceed. One NVIDIA L4 counts as 1. NVIDIA L4 GPUs are available in `europe-west1-b` and `europe-west1-c` (Saint-Ghislain, Belgium).

You can check GPU availability per region and zone here: [cloud.google.com/compute/docs/gpus/gpu-regions-zones](https://cloud.google.com/compute/docs/gpus/gpu-regions-zones).

### 2. Provision the VM

Google Cloud provides Deep Learning VM images that come with CUDA drivers and Docker pre-installed. Create a VM using one of those images with an NVIDIA L4 GPU attached:

```bash
gcloud compute instances create vllm-server \
    --project=YOUR_PROJECT_ID \
    --zone=europe-west1-b \
    --machine-type=g2-standard-8 \
    --accelerator=type=nvidia-l4,count=1 \
    --image-family=pytorch-2-7-cu128-ubuntu-2204-nvidia-570 \
    --image-project=deeplearning-platform-release \
    --boot-disk-size=100GB \
    --metadata=install-nvidia-driver=True \
    --maintenance-policy=TERMINATE \
    --scopes=https://www.googleapis.com/auth/cloud-platform
```

The `g2-standard-8` machine type has 8 vCPUs, 32 GB RAM, and one NVIDIA L4 GPU (24 GB VRAM). The `--boot-disk-size=100GB` is needed to store the model weights (the Qwen3.5 9B checkpoint is about 19 GB) and the Docker image.

This takes a couple of minutes. You can watch the status in the console: [console.cloud.google.com/compute/instances](https://console.cloud.google.com/compute/instances).

If you get a `ZONE_RESOURCE_POOL_EXHAUSTED` error, the zone has no available L4s at that moment. Try `europe-west1-c` or `europe-west4-a` instead by changing the `--zone` flag.

SSH into the VM:
```bash
gcloud compute ssh vllm-server --zone=europe-west1-b --project=YOUR_PROJECT_ID
```

The first time you run this, gcloud will generate an SSH key pair and upload the public key to the VM. Leave the passphrase empty when prompted. You will then see a "Welcome to the Google Deep Learning VM" banner confirming you are inside the VM.

Once inside, verify the GPU is visible:
```bash
nvidia-smi
```

You should see the NVIDIA L4 listed with 24 GB of VRAM (reported as ~23034 MiB by nvidia-smi), CUDA 12.8, and no running processes.

### 3. Install Docker and the NVIDIA container runtime

The Deep Learning VM image does not come with Docker or the NVIDIA container runtime pre-installed. Run the following to install Docker:

```bash
curl -fsSL https://get.docker.com | sudo sh
```

Then install the NVIDIA container toolkit, which lets Docker access the GPU:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 4. Start vLLM

You do not need to install anything else. The vLLM team publishes a ready-to-use Docker image called `vllm/vllm-openai` on Docker Hub. Running the command below will pull that image automatically if it is not already present, start a container from it, and launch the vLLM HTTP server inside that container.

```bash
sudo docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 8000:8000 \
    vllm/vllm-openai:nightly \
    --model Qwen/Qwen3.5-9B \
    --reasoning-parser qwen3 \
    --quantization fp8 \
    --max-model-len 8192
```

What each part does:
- `--runtime nvidia --gpus all`: gives the container access to the GPU on the VM
- `-v ~/.cache/huggingface:/root/.cache/huggingface`: mounts a folder from the VM disk into the container. Model weights downloaded from Hugging Face are stored on the VM disk rather than inside the container. Without this, every time you restart the container it would re-download the 19 GB of weights from scratch
- `-p 8000:8000`: forwards port 8000 of the container to port 8000 of the VM
- `vllm/vllm-openai:nightly`: the Docker image to use. The `nightly` tag is required for Qwen3.5 support. Note that pulling this image for the first time takes 5-10 minutes as it is around 10-15 GB. Nightly images are rebuilt daily, so if something breaks in a future session, try pinning a specific version tag (e.g. `vllm/vllm-openai:v0.9.0`) from the [vLLM Docker Hub page](https://hub.docker.com/r/vllm/vllm-openai/tags)
- `--model Qwen/Qwen3.5-9B`: the model to load. vLLM downloads it from Hugging Face on first run
- `--reasoning-parser qwen3`: tells vLLM to extract the model's internal reasoning trace (inside `<think>...</think>` tags) and surface it separately in the API response alongside the final answer
- `--quantization fp8`: quantizes the model weights from BF16 to FP8, halving the memory footprint from ~18 GB to ~9 GB. Without this flag the model weights alone consume 21 GB of the 22 GB available, leaving no room for the KV cache and causing an out-of-memory error at startup
- `--max-model-len 8192`: caps the context length at 8192 tokens. The model supports 262K but the L4 only has 24 GB VRAM, which after FP8 quantization leaves enough room for a KV cache supporting 8192 tokens with this model size

The first run downloads the Qwen3.5 9B weights (around 19 GB). Subsequent runs start immediately from the cache.

Wait until you see `INFO:     Application startup complete.`.

### 5. Interact with the model

The vLLM server is listening on port 8000 inside the VM. That port is not exposed to the public internet, so you cannot reach it directly from your machine. Instead, you open an SSH tunnel: a connection that goes through SSH and forwards a port on your local machine to a port inside the VM. Any HTTP request you send to `localhost:8000` on your machine will travel through the encrypted SSH connection and arrive at port 8000 on the VM.

At this point you have one terminal open inside the VM running the Docker container. Open a second terminal on your local machine and run:

```bash
gcloud compute ssh vllm-server \
    --zone=europe-west1-b \
    --project=YOUR_PROJECT_ID \
    -- -L 8000:localhost:8000 -N
```

The `-- -L 8000:localhost:8000` part is the port forwarding instruction: forward local port 8000 to port 8000 on the remote machine. The `-N` flag tells SSH not to open a shell, just hold the tunnel open.

**Keep this terminal open.** If you close it, the tunnel is gone and `localhost:8000` stops working, even though the vLLM server is still running inside the VM. Open a third terminal on your local machine to send requests.

With the tunnel running, send a chat request:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.5-9B",
    "messages": [{"role": "user", "content": "What is vLLM and why is it useful?"}],
    "max_tokens": 4096,
    "temperature": 0.7
  }'
```

The server responds with a JSON object. The structure looks like this:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "reasoning": "... the model's internal thinking ...",
      "content": "... the final answer ..."
    }
  }],
  "usage": {
    "prompt_tokens": 21,
    "completion_tokens": 256,
    "total_tokens": 277
  }
}
```

- `reasoning`: the model's step-by-step thinking process, exposed because of the `--reasoning-parser qwen3` flag. This is the model reasoning before it writes its answer, similar to OpenAI's o1 thinking traces.
- `content`: the final answer the model gives to your question. **If `content` is `null`**, it means `max_tokens` was reached during the thinking phase before the model started writing the answer. Qwen3.5 tends to think at length before answering, so 4096 is a safe minimum.
- `usage`: how many tokens were consumed. This is how APIs like OpenAI calculate billing.

Pipe the response through `jq` to extract just the message:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.5-9B",
    "messages": [{"role": "user", "content": "What is vLLM and why is it useful?"}],
    "max_tokens": 4096,
    "temperature": 0.7
  }' | jq '.choices[0].message.content'
```

### 6. Stop or delete the VM

A GPU VM costs money as long as it is running, even if idle. Once you are done with Part 1, stop or delete the VM before moving on.

If you plan to continue with Part 2 and may want to return to the VM later, stop it. The disk is preserved, and you can restart it at any time:

```bash
gcloud compute instances stop vllm-server --project=YOUR_PROJECT_ID --zone=europe-west1-b
```

If you are done with the VM entirely, delete it to avoid storage charges on the boot disk as well:

```bash
gcloud compute instances delete vllm-server --project=YOUR_PROJECT_ID --zone=europe-west1-b
```

---

## Part 2: Serverless GPU Serving with Google Cloud Run

Managing a VM works, but it has real operational costs. If your VM crashes, your API goes down. If you have no traffic, you still pay for the idle GPU. You are responsible for OS updates, driver compatibility, and firewall rules.

Google Cloud Run is a serverless platform that runs containers. It supports NVIDIA L4 GPUs natively and scales to zero: when no requests are coming in, the container is stopped and you pay nothing. When a request arrives, Cloud Run provisions a GPU instance, starts your container, and routes traffic to it automatically.

### 1. Store model weights in GCS

The main challenge with serverless GPUs is the cold start. If vLLM downloads 19 GB of weights from Hugging Face every time a container starts, the first request after a period of inactivity would take many minutes. Instead, we store the weights in a GCS bucket once and mount it directly into the container on every startup using GCS FUSE. Cloud Run reads the weights from GCS on the same network, which is much faster than downloading from the internet.

**Create a bucket:**
```bash
gcloud storage buckets create gs://YOUR_PROJECT_ID-vllm-weights \
    --project=YOUR_PROJECT_ID \
    --location=europe-west4
```

**Grant the default Compute Engine service account access to the bucket.** Cloud Run Jobs run under this identity and need permission to mount and write to the bucket:
```bash
gcloud storage buckets add-iam-policy-binding gs://YOUR_PROJECT_ID-vllm-weights \
    --project=YOUR_PROJECT_ID \
    --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/storage.objectAdmin
```

To find your project number:
```bash
gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"
```

**Download the model weights into the bucket.** Run a one-time Cloud Run Job to fetch the weights from Hugging Face and write them directly to the bucket via the GCS FUSE mount:
```bash
gcloud beta run jobs create download-weights \
    --project=YOUR_PROJECT_ID \
    --region=europe-west4 \
    --image=python:3.11-slim \
    --cpu=8 \
    --memory=32Gi \
    --task-timeout=3600 \
    --max-retries=0 \
    --add-volume=name=model-weights,type=cloud-storage,bucket=YOUR_PROJECT_ID-vllm-weights \
    --add-volume-mount=volume=model-weights,mount-path=/models \
    --args="sh,-c,pip install huggingface_hub && python3 -c \"kwargs={};kwargs['repo_id']='Qwen/Qwen3.5-9B';kwargs['local_dir']='/models';kwargs['local_dir_use_symlinks']=False;kwargs['max_workers']=1;from huggingface_hub import snapshot_download;snapshot_download(**kwargs)\""
```

Execute the job and wait for it to complete:
```bash
gcloud beta run jobs execute download-weights \
    --project=YOUR_PROJECT_ID \
    --region=europe-west4 \
    --wait
```

This takes around 10-15 minutes. Once it completes, the weights are stored in the bucket.

### 2. Deploy to Cloud Run

Cloud Run can pull public images directly from Docker Hub, so no private registry is needed. We use the official `vllm/vllm-openai:nightly` image as-is. If you ever need a customized image (baked-in dependencies, a private model, etc.), you would push it to Google Artifact Registry first and point `--image` at that instead.

```bash
gcloud beta run deploy vllm-qwen-service \
    --project=YOUR_PROJECT_ID \
    --image=vllm/vllm-openai:nightly \
    --region=europe-west4 \
    --cpu=8 \
    --memory=32Gi \
    --gpu=1 \
    --gpu-type=nvidia-l4 \
    --no-cpu-throttling \
    --no-gpu-zonal-redundancy \
    --allow-unauthenticated \
    --port=8000 \
    --add-volume=name=model-weights,type=cloud-storage,bucket=YOUR_PROJECT_ID-vllm-weights,readonly=true \
    --add-volume-mount=volume=model-weights,mount-path=/models \
    --startup-probe=tcpSocket.port=8000,initialDelaySeconds=240,failureThreshold=30,timeoutSeconds=25,periodSeconds=30 \
    --args="--model","/models","--quantization","fp8","--max-model-len","8192","--enforce-eager"
```

**Key flags explained:**

- `--gpu=1` and `--gpu-type=nvidia-l4`: attach a dedicated NVIDIA L4 (24 GB VRAM).
- `--no-cpu-throttling`: prevents CPU suspension between requests. This is mandatory for GPU workloads; without it, the CPU can be throttled while the GPU is active, causing hangs.
- `--no-gpu-zonal-redundancy`: required if your project does not have GPU zonal redundancy quota. The deployment will fail with a quota error without this flag if you have not requested that quota.
- `--allow-unauthenticated`: makes the endpoint publicly accessible. For a lab this is convenient; in production you would remove this and use identity tokens or Workload Identity Federation instead.
- `--add-volume` / `--add-volume-mount`: mounts the GCS bucket at `/models` inside the container via GCS FUSE. The weights are read directly from the bucket on every cold start.
- `--startup-probe`: Cloud Run kills the container if it has not passed the health check within the probe window. The L4 needs about 5 minutes to load the model shards; `initialDelaySeconds=240` tells Cloud Run to wait 4 minutes before it even starts checking, and `failureThreshold=30` allows 30 more failures at 30-second intervals (another 15 minutes), giving the container a total of about 19 minutes to become healthy.
- `--enforce-eager` (in `--args`): disables `torch.compile` and CUDA graph capture. These optimizations improve steady-state throughput but add 2-4 minutes to cold start. Skipping them on Cloud Run is a good trade-off because cold starts happen frequently on a scale-to-zero service.

Once the deployment finishes, the CLI prints the service URL. You can retrieve it at any time with:
```bash
gcloud run services describe vllm-qwen-service \
    --project=YOUR_PROJECT_ID \
    --region=europe-west4 \
    --format='value(status.url)'
```

### 3. Interact with the serverless API

You no longer need an SSH tunnel. Your model is now a globally accessible HTTPS endpoint.

Note that the model name exposed by vLLM is `/models` (the local path it was given at startup), not `Qwen/Qwen3.5-9B`. You can confirm this by calling the models endpoint:

```bash
curl https://YOUR_SERVICE_URL/v1/models
```

Send a chat request with curl:

```bash
curl https://YOUR_SERVICE_URL/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "/models",
    "messages": [{"role": "user", "content": "What is MLOps? Answer in two sentences."}],
    "max_tokens": 200
  }'
```


---

## Cleanup

To avoid ongoing costs, delete all resources once you have finished the lab.

**Delete the Cloud Run service:**
```bash
gcloud run services delete vllm-qwen-service --project=YOUR_PROJECT_ID --region=europe-west4
```

**Delete the Cloud Run job:**
```bash
gcloud run jobs delete download-weights --project=YOUR_PROJECT_ID --region=europe-west4
```

**Delete the GCS bucket:**
```bash
gcloud storage rm -r gs://YOUR_PROJECT_ID-vllm-weights --project=YOUR_PROJECT_ID
```

**Delete the VM** (if you did not already delete it at the end of Part 1):
```bash
gcloud compute instances delete vllm-server --project=YOUR_PROJECT_ID --zone=europe-west1-b
```
