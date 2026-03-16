# Lab 6 [Sprint 4, W7]: Vertex AI Pipelines

## 0. Introduction
The goal of this directed work is to make you familiar with the Vertex AI platform.

## 1. Prerequisites

1. Have a working version of [python](https://www.python.org/downloads/)
2. Have a working version of [Docker Desktop](https://docs.docker.com/desktop/)
3. Docker daemon running.
4. Enable the required GCP APIs:
```bash
gcloud services enable aiplatform.googleapis.com artifactregistry.googleapis.com --project=YOUR_PROJECT_ID
```

## 2. Vertex AI

### 2.1. Presentation of Vertex AI
Vertex AI is Google Cloud's unified platform for building, training, and deploying machine learning models. It provides a comprehensive suite of tools and services that allow data scientists and ML engineers to:

- Build and train models using AutoML or custom training
- Deploy models for online prediction or batch prediction
- Manage ML workflows and pipelines
- Monitor model performance and detect model drift
- Collaborate across teams with shared notebooks and datasets

The key advantage of Vertex AI is that it's a fully managed platform, meaning you can focus on the ML aspects rather than infrastructure management. It handles scaling, security, and maintenance automatically in a serverless way.

### 2.2. Required IAM permissions

As seen in Lab 5, GCP services do not run as you: they run under a service account, a non-human identity that must be granted explicit permissions to access resources. Vertex AI is no exception. When it runs your pipeline, it uses its own Google-managed service account called the Vertex AI service agent.

In this lab, each pipeline component runs inside a Docker container stored in Artifact Registry. Vertex AI pulls that image on your behalf using its service agent identity. Because the service agent is the one making the request, not you, it needs read access to your Artifact Registry repository. Without that permission, the pipeline fails before a single line of your component code ever runs.

Run these two commands in order to create the service identity and grant it that access.

First, create the service identity (this also prints its email)
```bash
gcloud beta services identity create --service=aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

It will print something like
```
Service identity created: service-YOUR_PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com
```

Then grant it the Artifact Registry Reader role using that email
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member="serviceAccount:service-YOUR_PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com" --role="roles/artifactregistry.reader"
```

Without this, the pipeline will fail with a permission error when trying to pull your component image from Artifact Registry.

The same principle applies to any other GCP service your components touch. In this pipeline, the data ingestion component calls the BigQuery API under the service agent's identity to export a table to GCS. BigQuery separates data-level permissions from job-level permissions, which is why two roles are needed.

`roles/bigquery.dataViewer` grants read access to table data. It includes the `bigquery.tables.export` permission, which is the one BigQuery checks when you call `extract_table`.

`roles/bigquery.jobUser` grants the right to create and submit jobs in the project. It includes `bigquery.jobs.create`. Without this role, BigQuery will refuse to create the export job even if the service agent can read the table.

Grant both to the service agent.

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:service-YOUR_PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:service-YOUR_PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"
```

Whenever you add a new component that calls a GCP API, check the [predefined roles reference](https://cloud.google.com/bigquery/docs/access-control) for that service to find which role covers the operation you need. Each GCP product has an equivalent page listing its predefined roles and the permissions each one includes.

### 2.3. How does Vertex AI Pipelines work?
The typical workflow in Vertex AI consists of several steps:

1. Components Definition. First, we define the individual steps of our ML workflow as components using the Kubeflow Pipelines SDK. These components can be
   - Custom code components that you write.
   - Pre-built components from Vertex AI's component library.
   - Each component runs in its own container instance. All components share the same base image, which is pushed once to Google Cloud's Artifact Registry.

2. Pipeline Creation. We chain these components together to create a pipeline. The pipeline defines
   - The sequence of component execution.
   - Data flow between components.
   - Required resources and configurations.

3. Pipeline Deployment. The pipeline is deployed to Vertex AI Pipelines, where it
   - Runs in a fully managed environment.
   - Can be scheduled or triggered on demand.
   - Provides monitoring and logging capabilities.
   - Maintains versioning and reproducibility.

4. Monitoring & Management: Once deployed, Vertex AI provides tools to
   - Track pipeline executions.
   - Monitor model performance.
   - Manage model versions.
   - Handle model updates and rollbacks.

## 3. Example with the house price prediction dataset

### 3.1. Dataset setup

We will be using the [Housing Prices Dataset](https://www.kaggle.com/datasets/yasserh/housing-prices-dataset?resource=download) from Kaggle. It contains information about house prices and features such as square footage, number of bedrooms, number of bathrooms, and year built.

1. Download the dataset from Kaggle and place the CSV at `data/Housing.csv`.

2. Make sure you have a GCS bucket for pipeline artifacts. Vertex AI uses GCS to store intermediate outputs passed between components (the ingested CSV, the preprocessed dataset, the trained model) and the compiled pipeline JSON. If you do not have one from Lab 2, create it.

    ```bash
    gsutil mb -l europe-west1 -p YOUR_PROJECT_ID gs://YOUR_BUCKET_NAME
    ```

3. Load the dataset into BigQuery. This is how data lives in production ML systems, not as local CSV files. First create a BigQuery dataset, then load the CSV into a table.

    ```bash
    bq mk --location=europe-west1 --project_id=YOUR_PROJECT_ID housing_dataset
    bq load --project_id=YOUR_PROJECT_ID --autodetect --source_format=CSV housing_dataset.housing data/Housing.csv
    ```

The pipeline will query this BigQuery table directly. Think of BigQuery as the data source and GCS as the shared workspace between pipeline steps.

### 3.2. Understanding the pipeline

Before installing anything, read through the pipeline design so you understand what you are building and what each component needs.

The pipeline trains a house price prediction model. It follows a production-realistic pattern. BigQuery exports the raw data to GCS as Parquet files, a preprocessing component cleans and encodes the data, a PyTorch MLP trains on it in mini-batches, and an evaluation component measures performance.

> This dataset has only 500 rows, which makes mini-batch training overkill. A single forward pass would be fast enough. The architecture is deliberately chosen to teach the production pattern. In a real system with millions of rows you would not load everything into memory, so the DataLoader-based approach generalizes. Keep that in mind as you implement.

The pipeline is made of four components that run in sequence.

1. **Data ingestion** triggers a BigQuery export job that writes the raw table to GCS as Parquet files. No data passes through Python memory.
2. **Preprocessing** reads the Parquet files, scales numerical features, encodes categorical ones, and writes the result back to GCS as Parquet.
3. **Training** reads the preprocessed Parquet, wraps it in a PyTorch `Dataset` and `DataLoader`, trains a simple MLP, and saves the model weights.
4. **Evaluation** reloads the model, runs predictions, and logs metrics. Optionally generates an HTML report.

Each component is a Python function decorated with `@component`. When you run `compiler.Compiler().compile()` locally, KFP serializes each function's source code and encodes it into a pipeline spec (the `houseprice_pipeline.json` file). When the pipeline runs on Vertex AI, for each component it pulls the `base_image` specified in `@component`, starts a container from it, injects the serialized function code as a temporary script, and executes it. Artifact references are passed automatically between components.

There is one critical rule about imports. Each component file has two distinct import zones.

At the top of the file, you place the KFP imports needed to define the component and its type annotations. These run on your local machine when Python parses the file.

```python
from kfp.dsl import component, Input, Output, Dataset, Model, Metrics, HTML
from config import BASE_IMAGE
```

Inside the function body, you place everything else (pandas, torch, bigquery, scikit-learn, etc.). These run inside the container on Vertex AI. The container has no knowledge of your local environment, so any library the function needs must be imported locally inside it.

In KFP v2, each artifact has two properties. `.uri` is the GCS URI (`gs://bucket/...`). `.path` is the local filesystem path inside the container, backed by a GCS FUSE mount at `/gcs/`. For all file reads and writes inside a component (pandas, torch, open), always use `.path`. The only exception is `data_ingestion`, where the BigQuery export API needs the GCS URI to write files directly. If you pass `.uri` to pandas, pyarrow will strip the `gs://` prefix and look for a local file that does not exist.

#### 3.2.1. Data ingestion

Uses the BigQuery client to trigger a native export job. BigQuery writes the table directly to GCS as Parquet files in parallel, without loading any data into Python memory. The GCS prefix where the files land is stored as an `Output[Dataset]` artifact so the next component can find them. This component is already fully implemented.

#### 3.2.2. Preprocessing

Reads the Parquet files from the ingestion artifact using pandas, applies transformations, and writes the preprocessed result back as Parquet. You need to implement the following.

- Identify numerical and categorical columns.
- Scale numerical features using `StandardScaler`.
- Encode categorical features using `OneHotEncoder`.
- Create the output directory with `os.makedirs(preprocessed_dataset.path, exist_ok=True)`.
- Save the result with `df_processed.to_parquet(preprocessed_dataset.path + "/data.parquet")`.

#### 3.2.3. Training

Reads the preprocessed Parquet from GCS, builds a PyTorch `Dataset` and `DataLoader`, defines a simple MLP, and trains it using Adam and MSE loss. You need to implement the following.

- A `torch.utils.data.Dataset` subclass that loads the Parquet and returns `(features, target)` tensors.
- A train/validation split.
- The MLP architecture using `nn.Linear` layers with `nn.ReLU` activations.
- The training loop.
- Logging MSE and R2 to the `metrics` artifact.
- Saving the checkpoint with `torch.save({...}, model.path)`. Save `input_size` and `hidden_size` alongside the state dict so evaluation can rebuild the architecture without hardcoding.

#### 3.2.4. Evaluation

Rebuilds the same MLP architecture, loads the saved weights, runs predictions on the validation set, and logs metrics. You need to implement the following.

- Rebuild the MLP using `input_size` and `hidden_size` read from the checkpoint (the architecture must match training exactly).
- Load weights with `torch.load(model.path)` which returns the dict you saved.
- Run predictions.
- Compute and log MSE and R2.
- (Optional) Generate an HTML report and write it to `html.path`.

### 3.3. Project setup

Now that you know what the pipeline does and what each component needs, install the dependencies. From inside your project directory:

```bash
uv init --no-package .
uv add kfp google-cloud-aiplatform google-cloud-bigquery google-cloud-bigquery-storage google-cloud-storage google-auth pandas pyarrow gcsfs scikit-learn torch matplotlib seaborn
```

This generates a `pyproject.toml` and a `uv.lock` file. Both are used by the Dockerfile in the next step to install dependencies reproducibly inside the pipeline containers.

At the top of `run_pipeline.py`, add the necessary imports and configuration constants.

```python
from kfp import dsl, compiler
from kfp.dsl import Dataset, Input, Model, Output, Metrics, HTML, component
from google.cloud import aiplatform

PROJECT_ID    = "your-project-id"
BUCKET_NAME   = "gs://your-bucket-name"
BQ_DATASET    = "housing_dataset"
BQ_TABLE      = "housing"
LOCATION      = "europe-west1"
PIPELINE_ROOT = f"{BUCKET_NAME}/pipeline_root_houseprice/"
BASE_IMAGE    = f"{LOCATION}-docker.pkg.dev/{PROJECT_ID}/vertex-ai-pipeline-example/pipeline-base:latest"
```

A few notes on the imports:
- `from kfp import ...` is the correct KFP v2 style. The old `from kfp.v2 import ...` is deprecated.
- `Dataset`, `Model`, `Metrics`, `HTML` are special artifact types that Vertex AI tracks and passes between components.
- `PIPELINE_ROOT` tells Vertex AI where to write all intermediate artifacts in GCS.

`houseprice_pipeline.json` will also be generated at runtime: it is the compiled pipeline definition produced by `compiler.Compiler().compile()`. It is read immediately by `PipelineJob` in the same script and is stale after every run, so there is no point committing it. Add it to `.gitignore`.

### 3.4. Setting up the Docker base image

Now that you know what the pipeline components need, you can build a Docker image that contains all their dependencies. This is the image Vertex AI will pull and use to run each component.

1. Create the following Dockerfile at the root of your project directory.

```Dockerfile
FROM mirror.gcr.io/library/python:3.11-slim

WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies system-wide (no venv: this is a base image for pipeline components)
RUN uv export --frozen --no-dev --no-hashes -o /tmp/requirements.txt && \
    uv pip install --system -r /tmp/requirements.txt

ENTRYPOINT ["bash"]
```

Key points about this Dockerfile:

- **`mirror.gcr.io/library/python:3.11-slim`** is a mirror of the official Python image hosted on GCR (Google Container Registry), Google's own Docker image registry. It is faster to pull inside GCP than pulling from Docker Hub, and it avoids Docker Hub rate limits.
- **UV** is copied from its official image, as seen in Lab 3.
- The two-step `RUN` installs your dependencies system-wide.
  - `uv sync` always creates a virtual environment (`.venv`). That is the right behavior for a developer machine or an application container (as in Labs 3, 4, and 5) because it keeps dependencies isolated. Here it would be wrong. This image is not a self-contained application. It is a base image that Vertex AI uses as a runtime environment. When Vertex AI runs a component, it injects the component's code into the container at runtime and executes it directly, without activating any virtual environment. If packages live inside a `.venv`, Vertex AI cannot find them and the component fails with `ModuleNotFoundError`.
  - `uv export` reads `uv.lock` and writes a flat `requirements.txt` with exact pinned versions. `--no-hashes` removes the hash annotations that `pip` does not need here. `--frozen` means uv will fail rather than silently update any package.
  - `uv pip install --system` installs into the system Python directly, without creating a `.venv`. Packages end up in `/usr/local/lib/python3.11/site-packages/`, which is where any `python` invocation finds them regardless of who called it.
  - `--no-dev` skips development dependencies (test frameworks, linters, etc.) that have no place in a production image.
- **`ENTRYPOINT ["bash"]`** is required by Vertex AI. It keeps the container alive so the platform can inject and execute each component's script inside it.

> **Note on per-component images.** This lab uses a single shared base image for all components. This is the abstraction that KFP's `@component` decorator provides. You write a Python function and KFP handles injecting it into the container at runtime. In raw Kubeflow Pipelines, without that abstraction, each component is a fully self-contained Docker image with its own `Dockerfile` and entrypoint. That approach gives finer dependency isolation (each component installs only what it needs) but requires building and pushing one image per component. The `@component` pattern trades that flexibility for convenience.

2. Create an Artifact Registry repository. As seen in Lab 5, Artifact Registry is GCP's private container registry: the place where Docker images are stored before being pulled and run. In Lab 5, Cloud Run used it automatically in the background. Here, you interact with it directly: you push your base image to it, and Vertex AI pulls it from there whenever it runs a pipeline component.

```bash
gcloud beta artifacts repositories create vertex-ai-pipeline-example \
    --repository-format=docker \
    --location=europe-west1 \
    --project=YOUR_PROJECT_ID \
    --description="Repository for Vertex AI pipeline components"
```

3. Configure Docker to authenticate with Artifact Registry. By default, Docker does not know how to authenticate against GCP registries. This command tells Docker to use your gcloud credentials whenever it talks to `europe-west1-docker.pkg.dev`. It does not touch any specific project, it configures authentication for the registry hostname. Your project ID will appear later, in the image path itself.

```bash
gcloud auth configure-docker europe-west1-docker.pkg.dev
```

4. Build and tag the base image. Run this from the directory containing your Dockerfile.

```bash
docker build --platform linux/amd64 -t pipeline-base:latest .
```

> The `--platform linux/amd64` flag is mandatory. GCP runs on Linux x86-64. If you are on an Apple Silicon Mac (M1, M2, M3, M4), your machine builds ARM images by default. Vertex AI cannot run an ARM image and the pipeline will fail at startup with a cryptic error. Always specify the platform explicitly, regardless of what machine you are on.

Then tag the image with its full Artifact Registry path so Docker knows where to push it.

```bash
docker tag pipeline-base:latest \
    europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/vertex-ai-pipeline-example/pipeline-base:latest
```

5. Push the image to Artifact Registry.

```bash
docker push europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/vertex-ai-pipeline-example/pipeline-base:latest
```

You can verify the image was pushed correctly by navigating to Artifact Registry in the GCP console.

## 4. Implementing the components

With the Docker image pushed, you can now write the component code. Each component goes in its own file inside `src/`. Start by creating `src/config.py` with the `BASE_IMAGE` constant so every component file can import it.

```python
# src/config.py
BASE_IMAGE = "europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/vertex-ai-pipeline-example/pipeline-base:latest"
```

### 4.1. Data ingestion

This component is already fully implemented. Read it carefully and pay attention to how `dataset.uri` gives the GCS path that BigQuery exports to, and how the BigQuery project, dataset, and table are passed as parameters rather than hardcoded.

```python
# src/data_ingestion.py
from kfp.dsl import component, Output, Dataset
from config import BASE_IMAGE

@component(base_image=BASE_IMAGE)
def data_ingestion(
    bq_project: str,
    bq_dataset: str,
    bq_table: str,
    dataset: Output[Dataset]
):
    from google.cloud import bigquery

    client = bigquery.Client(project=bq_project)
    extract_job = client.extract_table(
        f"{bq_project}.{bq_dataset}.{bq_table}",
        destination_uris=[f"{dataset.uri}/*.parquet"],
        job_config=bigquery.ExtractJobConfig(
            destination_format=bigquery.DestinationFormat.PARQUET
        )
    )
    extract_job.result()
    print(f"Exported to {dataset.uri}")
```

### 4.2. Preprocessing

```python
# src/preprocessing.py
from kfp.dsl import component, Input, Output, Dataset
from config import BASE_IMAGE

@component(base_image=BASE_IMAGE)
def preprocessing(
    input_dataset: Input[Dataset],
    preprocessed_dataset: Output[Dataset],
):
    import os
    import pandas as pd
    from sklearn.preprocessing import StandardScaler, OneHotEncoder

    df = pd.read_parquet(input_dataset.path)

    # TODO: identify numerical and categorical columns
    # TODO: scale numerical features with StandardScaler
    # TODO: encode categorical features with OneHotEncoder
    # TODO: os.makedirs(preprocessed_dataset.path, exist_ok=True)
    # TODO: df_processed.to_parquet(preprocessed_dataset.path + "/data.parquet")
```

### 4.3. Training

```python
# src/training.py
from kfp.dsl import component, Input, Output, Dataset, Model, Metrics
from config import BASE_IMAGE

@component(base_image=BASE_IMAGE)
def training(
    preprocessed_dataset: Input[Dataset],
    model: Output[Model],
    metrics: Output[Metrics],
    hyperparameters: dict
):
    import pandas as pd
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    from sklearn.metrics import mean_squared_error, r2_score

    df = pd.read_parquet(preprocessed_dataset.path + "/data.parquet")

    # TODO: define a Dataset subclass returning (features, target) tensors
    # TODO: split into train and validation sets
    # TODO: create DataLoaders using hyperparameters["batch_size"]
    # TODO: define the MLP (nn.Linear + nn.ReLU layers)
    # TODO: train with Adam (hyperparameters["lr"]) and MSE loss for hyperparameters["epochs"] epochs
    # TODO: compute MSE and R2 on the validation set and log them to metrics
    # TODO: torch.save({'state_dict': mlp.state_dict(), 'input_size': input_size, 'hidden_size': hidden_size}, model.path)
```

### 4.4. Evaluation

```python
# src/evaluation.py
from kfp.dsl import component, Input, Output, Dataset, Model, Metrics, HTML
from config import BASE_IMAGE

@component(base_image=BASE_IMAGE)
def evaluation(
    model: Input[Model],
    preprocessed_dataset: Input[Dataset],
    metrics: Output[Metrics],
    html: Output[HTML]
):
    import pandas as pd
    import torch
    import torch.nn as nn
    import matplotlib.pyplot as plt
    from sklearn.metrics import mean_squared_error, r2_score

    df = pd.read_parquet(preprocessed_dataset.path + "/data.parquet")

    # TODO: rebuild the MLP architecture (must match training exactly)
    # TODO: checkpoint = torch.load(model.path, weights_only=False) then rebuild MLP from checkpoint['input_size'] and checkpoint['hidden_size']
    # TODO: run predictions
    # TODO: compute and log MSE and R2 to metrics
    # TODO (optional): generate HTML report and write to html.path
```

### 4.5. Assembling the pipeline

Once all components are implemented, assemble them into a pipeline using `@dsl.pipeline`. This function does not run any ML code itself. It describes the execution graph by specifying which outputs flow into which inputs, and Vertex AI handles the scheduling and data passing.

```python
@dsl.pipeline(
    name="houseprice_pipeline",
    pipeline_root=PIPELINE_ROOT
)
def houseprice_pipeline(
    bq_project: str = PROJECT_ID,
    bq_dataset: str = BQ_DATASET,
    bq_table: str = BQ_TABLE,
):
    ingestion_task = data_ingestion(
        bq_project=bq_project,
        bq_dataset=bq_dataset,
        bq_table=bq_table,
    )

    preprocessing_task = preprocessing(
        input_dataset=ingestion_task.outputs["dataset"]
    )

    training_task = training(
        preprocessed_dataset=preprocessing_task.outputs["preprocessed_dataset"],
        hyperparameters={
            "lr": 0.001,
            "epochs": 50,
            "batch_size": 32,
            "hidden_size": 64
        }
    )

    evaluation_task = evaluation(
        model=training_task.outputs["model"],
        preprocessed_dataset=preprocessing_task.outputs["preprocessed_dataset"]
    )
```

### 4.6. Configuring compute resources per component

By default, Vertex AI runs each component on a small CPU machine. You can override this on any task inside the pipeline function by chaining resource methods on the task object. For example, since training is the only step that benefits from a GPU, you can attach the accelerator there and leave the other components on CPU.

```python
training_task = training(
    preprocessed_dataset=preprocessing_task.outputs["preprocessed_dataset"],
    hyperparameters={...}
).set_accelerator_type("NVIDIA_TESLA_T4") \
 .set_accelerator_limit(1) \
 .set_machine_type("n1-standard-4")
```

Common methods are `.set_cpu_limit()`, `.set_memory_limit()`, `.set_machine_type()`, `.set_accelerator_type()`, and `.set_accelerator_limit()`. The available accelerator types depend on your region. This is entirely independent of which Docker image is used: all components can share the same base image while running on different hardware.

## 5. Running the Pipeline

Make sure you have updated the configuration variables at the top of `run_pipeline.py` (`PROJECT_ID`, `BUCKET_NAME`, `BQ_DATASET`, `BQ_TABLE`), then run:

```bash
uv run python run_pipeline.py
```

This compiles the pipeline to `houseprice_pipeline.json` and submits it to Vertex AI. You can then monitor execution in the GCP console under Vertex AI > Pipelines.

> **Note on IAM permissions**: the first run may fail with a permission error. If so, follow the steps in section 2.2 to grant the Artifact Registry Reader role to the Vertex AI service agent, then run again.

## 6. Monitoring and analyzing results

After running your pipeline, you can:

1. Monitor pipeline execution in the Google Cloud Console:
   - Navigate to Vertex AI > Pipelines
   - Find your pipeline run and click on it
   - View the DAG visualization and execution status
   - Check logs for each component

2. Analyze the results:
   - Review the MSE and R2 metrics logged by the training and evaluation components. Clicking a component node in the DAG shows its logged metrics in the side panel.
   - The evaluation component writes an HTML artifact containing an actual vs predicted price scatter plot and a residual distribution histogram, both embedded as a base64-encoded PNG. GCS does not serve HTML files directly in the browser, so download it first and then open the local file.
     ```bash
     gsutil cp gs://YOUR_BUCKET_NAME/pipeline_root_houseprice/PROJECT_NUMBER/RUN_ID/evaluation_HASH/html.html /tmp/evaluation_report.html
     open /tmp/evaluation_report.html
     ```
   - Check the R2 score and MSE on both the training and evaluation components to spot overfitting.

3. Access artifacts:
   - All artifacts (the exported Parquet files, the preprocessed dataset, the model checkpoint, and the HTML evaluation report) are stored in your GCS bucket under the pipeline root. The path follows the pattern `gs://YOUR_BUCKET/pipeline_root_houseprice/PROJECT_NUMBER/RUN_ID/COMPONENT_HASH/`.
   - You can browse them in the GCS console or download them locally with `gsutil cp`.
   - Vertex AI tracks the full lineage of each artifact, so clicking a node in the pipeline DAG shows exactly which GCS path holds its output.

## 7. Cleaning up resources

To avoid unnecessary costs, clean up your resources when you're done:

1. Delete pipeline artifacts from GCS:
```bash
gsutil rm -r gs://YOUR_BUCKET_NAME/pipeline_root_houseprice/
```

2. Delete the BigQuery dataset:
```bash
bq rm -r -f YOUR_PROJECT_ID:housing_dataset
```

3. Delete the Docker image from Artifact Registry:
```bash
gcloud artifacts docker images delete \
    europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/vertex-ai-pipeline-example/pipeline-base:latest \
    --quiet
```

4. Delete the Artifact Registry repository:
```bash
gcloud artifacts repositories delete vertex-ai-pipeline-example \
    --location=europe-west1 \
    --project=YOUR_PROJECT_ID \
    --quiet
```

5. Optional: Delete the entire GCS bucket if no longer needed:
```bash
gsutil rm -r gs://YOUR_BUCKET_NAME
```

Use `--quiet` to skip confirmation prompts. Some deletions take a few minutes to propagate.

## 8. Your turn.

Now that we have our environment set up, you need to:

1. Submit the following on **Gradescope**:
   - Screenshot of your pipeline DAG running successfully in the Vertex AI console
   ![pipeline](img/4.png)
   - The HTML evaluation report (`html.html`) downloaded from GCS
   - Screenshot of performance metrics (MSE and R2) visible in the Vertex AI pipeline console
   - Your component code (`src/` directory)

You have until 16/03/2026 23:59 to submit your work on **Gradescope**.







