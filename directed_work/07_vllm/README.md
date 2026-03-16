# Lab 7 [Sprint 4, W8]: GPU Serving with vLLM

## 0. Introduction

In production ML systems, serving large language models efficiently is one of the most challenging infrastructure problems. A naive approach, loading the model into a Python process and running forward passes one request at a time, wastes GPU memory and leaves most of the hardware idle. This lab introduces vLLM, a high-performance serving engine that solves this problem, and shows you how to deploy it on a GPU virtual machine in the cloud.

By the end of this lab you will have:
- Provisioned a GPU VM on Google Compute Engine
- Deployed Qwen3.5 9B on that VM using vLLM
- Measured the GPU throughput
- Used the OpenAI-compatible API to interact with your own hosted model

## 1. Background

### 1.1. Why a dedicated serving engine?

When you call `model.generate()` in a plain PyTorch script, each request occupies the GPU entirely while it runs and all other requests wait. As soon as traffic exceeds one request per second, this becomes a bottleneck.

vLLM solves this with two core mechanisms.

**PagedAttention.** During autoregressive generation the model maintains a KV-cache (key-value pairs for every token in the context). In standard implementations this cache is pre-allocated as one large contiguous block per sequence, wasting memory on padding. PagedAttention manages the KV-cache in small non-contiguous pages, the same idea as virtual memory in operating systems. This reduces memory waste and allows the GPU to hold more concurrent sequences.

**Continuous batching.** Instead of waiting for a fixed batch to be fully assembled before running the GPU, vLLM adds newly arrived requests to the running batch at every generation step. Sequences that finish early free their memory immediately and their slot is filled by the next waiting request. GPU utilisation stays high regardless of variable request lengths.

Together these two mechanisms allow vLLM to serve 10-20x more requests per second than a naive implementation on the same hardware.

### 1.2. The OpenAI-compatible API

In this lab you will interact with vLLM through HTTP requests, not by importing a Python library. vLLM is packaged as a Docker image (`vllm/vllm-openai`). You run that image on a GPU machine, it loads the model and starts an HTTP server on port 8000, and you send requests to it from your own machine.

The HTTP interface vLLM exposes is deliberately identical to the OpenAI API: same endpoints (`/v1/chat/completions`), same JSON request fields, same response format. This means you can use the standard `openai` Python client to talk to it, and any application already written for OpenAI works against your self-hosted server with a single line change. Nothing is sent to OpenAI. The model runs on your own infrastructure.

The only two differences you will notice in the code are:
- `base_url` is set to your server address instead of `api.openai.com`
- `api_key` is set to any non-empty string (vLLM requires the field to be present because the client library enforces it, but it ignores the value by default)

### 1.3. The model: Qwen3.5 9B

[Qwen3.5](https://huggingface.co/Qwen/Qwen3.5-9B) is Alibaba's latest open model family. The 9B variant:
- Has 9 billion parameters. In BF16 this occupies roughly 18 GB VRAM, which fits on a single L4 (24 GB) with headroom for the KV cache
- Has built-in reasoning: the model can produce a `<think>...</think>` block where it reasons step-by-step before giving its final answer, similar to OpenAI o1
- Has been fine-tuned for instruction following and tool use
- Is fully open with no gating on Hugging Face, so no token or terms acceptance is needed

## 2. Prerequisites

### 2.1. Local prerequisites

1. [uv](https://docs.astral.sh/uv/) installed
2. Initialize a project in this lab's folder and add the OpenAI client:
```bash
uv init
uv add openai
```

### 2.2. GCP prerequisites

1. A Google Cloud project with billing enabled
2. The Google Cloud CLI installed and authenticated
3. Enable the Compute Engine API:
```bash
gcloud services enable compute.googleapis.com --project=YOUR_PROJECT_ID
```

### 2.3. GPU quota

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
4. Fill in the form with your use case (e.g. "I am taking an MLOps course and need to deploy a GPU instance for a lab exercise") and submit it. You don't need to specify an exact region or GPU type at this stage, just the total number of GPUs you want to be able to use across all regions.
5. Submit the request. Approval usually takes a few minutes to a few hours.

If the limit is already 1 or more, you are good to proceed. One NVIDIA L4 counts as 1. NVIDIA L4 GPUs are available in `europe-west1-b` and `europe-west1-c` (Saint-Ghislain, Belgium).

You can check GPU availability per region and zone here: [cloud.google.com/compute/docs/gpus/gpu-regions-zones](https://cloud.google.com/compute/docs/gpus/gpu-regions-zones).

## 3. Provision a GPU VM on Compute Engine

### 3.1. Create the VM

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

### 3.2. SSH into the VM

```bash
gcloud compute ssh vllm-server --zone=europe-west1-b --project=YOUR_PROJECT_ID
```

The first time you run this, gcloud will generate an SSH key pair and upload the public key to the VM. Leave the passphrase empty when prompted. You will then see a "Welcome to the Google Deep Learning VM" banner confirming you are inside the VM.

Once inside, verify the GPU is visible:

```bash
nvidia-smi
```

You should see the NVIDIA L4 listed with 24 GB of VRAM (reported as ~23034 MiB by nvidia-smi, which is 24 GB minus a small system reservation), CUDA 12.8, and no running processes.

### 3.3. Install Docker and the NVIDIA container runtime

The Deep Learning VM image does not come with Docker or the NVIDIA container runtime pre-installed. Run the following to install Docker:

```bash
curl -fsSL https://get.docker.com | sudo sh
```

Then install the NVIDIA container toolkit. This lets Docker access the GPU:

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

### 3.4. Start vLLM on the VM

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
- `-p 8000:8000`: forwards port 8000 of the container to port 8000 of the VM, so you can reach the HTTP server from outside
- `vllm/vllm-openai:nightly`: the Docker image to use. The `nightly` tag is required for Qwen3.5 support. Note that pulling this image for the first time takes 5-10 minutes as it is around 10-15 GB. Nightly images are rebuilt daily, so if something breaks in a future session, try pinning a specific version tag (e.g. `vllm/vllm-openai:v0.9.0`) from the [vLLM Docker Hub page](https://hub.docker.com/r/vllm/vllm-openai/tags)
- `--model Qwen/Qwen3.5-9B`: the model to load. vLLM downloads it from Hugging Face on first run
- `--reasoning-parser qwen3`: tells vLLM to extract the model's internal reasoning trace (inside `<think>...</think>` tags) and surface it separately in the API response alongside the final answer
- `--quantization fp8`: quantizes the model weights from BF16 to FP8, halving the memory footprint from ~18 GB to ~9 GB. Without this flag the model weights alone consume 21 GB of the 22 GB available, leaving no room for the KV cache and causing an out-of-memory error at startup
- `--max-model-len 8192`: caps the context length at 8192 tokens. The model supports 262K but the L4 only has 24 GB VRAM, which after FP8 quantization leaves enough room for a KV cache supporting 8192 tokens with this model size

The first run downloads the Qwen3.5 9B weights (around 19 GB). Subsequent runs start immediately from the cache.

Wait until you see `INFO:     Application startup complete.`.

## 4. Interact with the model

### 4.1. Open an SSH tunnel

The vLLM server is listening on port 8000 inside the VM. That port is not exposed to the public internet, so you cannot reach it directly from your machine. Instead, you open an SSH tunnel: a connection that goes through SSH and forwards a port on your local machine to a port inside the VM. Any HTTP request you send to `localhost:8000` on your machine will travel through the encrypted SSH connection and arrive at port 8000 on the VM, where the vLLM server is listening.

At this point you have one terminal open inside the VM running the Docker container. Open a second terminal on your local machine and run:

```bash
gcloud compute ssh vllm-server \
    --zone=YOUR_ZONE \
    --project=YOUR_PROJECT_ID \
    -- -L 8000:localhost:8000 -N
```

The `-- -L 8000:localhost:8000` part is the port forwarding instruction passed to SSH: forward local port 8000 to port 8000 on the remote machine. The `-N` flag tells SSH not to open a shell, just hold the tunnel open.

**Keep this terminal open for the entire lab.** If you close it, the tunnel is gone and `localhost:8000` stops working, even though the vLLM server is still running inside the VM. Open a third terminal on your local machine to send requests in the next section.

### 4.2. Send a chat request

With the SSH tunnel running, your local machine can reach the vLLM server as if it were running locally. You send an HTTP POST request to the `/v1/chat/completions` endpoint with a JSON body describing the model, the conversation messages, and generation parameters. This is exactly the same format as the OpenAI API.

`curl` is a command-line tool for making HTTP requests. The `-H` flag adds a header, and `-d` provides the request body. The JSON body works exactly like the OpenAI API:
- `"model"`: which model to use
- `"messages"`: the conversation history, with a `role` (`user`, `assistant`, or `system`) and `content` for each turn. Here we have a single user message, which is equivalent to typing a message in ChatGPT.
- `"max_tokens"`: the maximum number of tokens the model can generate in its response
- `"temperature"`: controls randomness. 0 is fully deterministic, 1 is more creative

From your local machine:

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
- `content`: the final answer the model gives to your question. This is what you would display to a user. **If `content` is `null`**, it means `max_tokens` was reached during the thinking phase before the model started writing the answer. Qwen3.5 tends to think at length before answering, so 4096 is a safe minimum.
- `usage`: how many tokens were consumed. This is how APIs like OpenAI calculate billing.

The raw response is a single line of JSON which is hard to read. Pipe it through `jq` to extract just the message:

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

Or using the Python `openai` client:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

response = client.chat.completions.create(
    model="Qwen/Qwen3.5-9B",
    messages=[{"role": "user", "content": "Give me three concrete reasons why serving infrastructure matters in production ML systems."}],
    max_tokens=4096,
)
print(response.choices[0].message.content)
```
