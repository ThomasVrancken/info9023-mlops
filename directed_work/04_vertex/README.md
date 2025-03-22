# Directed work 4 [Sprint 4, W08]: Vertex

## 0. Introduction
The goal of this directed work is to make you familiar with the Vertex AI platform.

## 1. Prerequisites

1. Have a working version of [python](https://www.python.org/downloads/)
2. Have a working version of [Docker Desktop](https://docs.docker.com/desktop/)
3. Docker daemon running.

## 2. Vertex AI

### 2.1. Presentation of Vertex AI
Vertex AI is Google Cloud's unified platform for building, training, and deploying machine learning models. It provides a comprehensive suite of tools and services that allow data scientists and ML engineers to:

- Build and train models using AutoML or custom training
- Deploy models for online prediction or batch prediction
- Manage ML workflows and pipelines
- Monitor model performance and detect model drift
- Collaborate across teams with shared notebooks and datasets

The key advantage of Vertex AI is that it's a fully managed platform, meaning you can focus on the ML aspects rather than infrastructure management. It handles scaling, security, and maintenance automatically in a serverless way.

How does it work?

The typical workflow in Vertex AI consists of several steps:

1. Components Definition: First, we define the individual steps of our ML workflow as components using the Kubeflow Pipelines SDK. These components can be:
   - Custom code components that you write
   - Pre-built components from Vertex AI's component library
   - Each component runs in its own Docker container, which we push to Google Cloud's Artifact Registry

2. Pipeline Creation: We chain these components together to create a pipeline. The pipeline defines:
   - The sequence of component execution
   - Data flow between components
   - Required resources and configurations

3. Pipeline Deployment: The pipeline is deployed to Vertex AI Pipelines, where it:
   - Runs in a fully managed environment
   - Can be scheduled or triggered on demand
   - Provides monitoring and logging capabilities
   - Maintains versioning and reproducibility

4. Monitoring & Management: Once deployed, Vertex AI provides tools to:
   - Track pipeline executions
   - Monitor model performance
   - Manage model versions
   - Handle model updates and rollbacks

## 3. Example with the House Price Prediction Dataset

### 3.1. Dataset and Requirements Setup

#### Dataset Overview
We'll be using the [Housing Prices Dataset](https://www.kaggle.com/datasets/yasserh/housing-prices-dataset?resource=download) from Kaggle. This dataset contains information about house prices and various features including:
- Square footage
- Number of bedrooms
- Number of bathrooms
- Year built
- And other relevant features

#### Required Dependencies
First, let's set up our Python environment with the necessary packages. Create a `requirements.txt` file with the following dependencies:

```txt
kfp==2.7.0
google-cloud-aiplatform==1.42.1
pandas==2.1.0
scikit-learn==1.3.0
numpy==1.24.0
```

#### Project Structure
Create the following directory structure for your project:
```
house_prediction/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── data_ingestion.py
│   ├── preprocessing.py
│   ├── training.py
│   └── evaluation.py
└── house_prediction.ipynb
```

#### Initial Setup Code
Before we start building our pipeline components, we need to import the necessary libraries and set up our environment:

```python
from kfp.v2 import dsl
from kfp.v2.dsl import (
    Artifact,    # For handling ML artifacts
    Dataset,     # For handling datasets
    Input,       # For component inputs
    Model,       # For handling ML models
    Output,      # For component outputs
    Metrics,     # For tracking metrics
    Markdown,    # For documentation
    HTML,        # For visualization
    component,   # For creating pipeline components
    OutputPath,  # For specifying output paths
    InputPath    # For specifying input paths
)
from kfp.v2 import compiler
from google.cloud.aiplatform import pipeline_jobs

# Define the pipeline root for storing artifacts
PIPELINE_ROOT = f"{BUCKET_NAME}/{PIPELINE_ROOT_FOLDER}"
```

Key points about the imports:
- `kfp.v2`: The Kubeflow Pipelines SDK v2 for defining ML pipelines
- `dsl`: Domain Specific Language for defining pipeline components and workflows
- `Artifact`, `Dataset`, etc.: Special types for handling ML-specific data and artifacts
- `compiler`: For converting pipeline definitions to Vertex AI-compatible format
- `pipeline_jobs`: For managing pipeline executions in Vertex AI

The `PIPELINE_ROOT` constant defines where all pipeline artifacts (datasets, models, metrics) will be stored in Google Cloud Storage.

### 3.2. Setting up the Docker Base Image

Before we can create our pipeline components, we need to set up a Docker base image that will be used to run all our components. This image needs to be stored in Google Cloud's Artifact Registry. Here's how to do it step by step:

1. First, create a Dockerfile that will serve as our base image:
```Dockerfile
FROM mirror.gcr.io/library/python:3.8
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY src /app/src
RUN pip install -r /app/requirements.txt
ENTRYPOINT ["bash"]
```

Key points about this Dockerfile:
- We use `mirror.gcr.io/library/python:3.8` instead of `python:3.8` because:
  - It's faster to pull as it's a Google Container Registry (GCR) mirror
  - It reduces external dependencies
  - It's maintained by Google
- `ENTRYPOINT ["bash"]` keeps the container running after component execution
- The image includes our Python dependencies and source code

2. Set up your environment variables:
```bash
# Your Google Cloud project ID
PROJECT_ID="your-project-id"
# Region where you want to store your artifacts
REGION="europe-west1"
# Name for your Artifact Registry repository
REPOSITORY="vertex-ai-pipeline-example"
# Name for your Docker image
IMAGE_NAME="training"
# Tag for your image
IMAGE_TAG="latest"
```

3. Create an Artifact Registry repository:
```bash
gcloud beta artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --description="Repository for Vertex AI pipeline components"
```

4. Configure Docker to authenticate with Artifact Registry:
```bash
gcloud auth configure-docker $REGION-docker.pkg.dev
```

5. Build and tag your Docker image:
```bash
# Build the image
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Tag the image for Artifact Registry
docker tag $IMAGE_NAME:$IMAGE_TAG \
    $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$IMAGE_TAG
```

6. Push the image to Artifact Registry:
```bash
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$IMAGE_TAG
```

7. Now you can use this image in your components:
```python
@component(
    base_image=f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPOSITORY}/{IMAGE_NAME}:{IMAGE_TAG}"
)
def your_component():
    # Your component code here
    pass
```

Important notes:
- Make sure you have the necessary permissions in your Google Cloud project
- The Artifact Registry repository must be in the same region as your Vertex AI resources
- Keep your Docker image lightweight and only include necessary dependencies
- Consider using specific version tags instead of 'latest' for better reproducibility
- You can verify your image in the Google Cloud Console under Artifact Registry
![Artifact Registry](./img/1.png)

## 4. Understanding the Notebook Cells

Let's go through each cell in the `house_prediction.ipynb` notebook and understand what they do:

### Cell 1: Import Dependencies
```python
from typing import Optional
import google.auth
from kfp.v2 import dsl
from kfp.v2.dsl import (Artifact, Dataset, Input, Model, Output, Metrics,
                        Markdown, HTML, component, OutputPath, InputPath)
from kfp.v2 import compiler
from kfp.v2.dsl import component, pipeline
from google.cloud import aiplatform
from google.cloud.aiplatform import pipeline_jobs
import kfp.v2 as kfp
import vertexai.preview
```
This cell imports all necessary libraries for working with Vertex AI:
- `kfp.v2`: The Kubeflow Pipelines SDK v2, used for defining ML pipelines
- `google.cloud.aiplatform`: The main Vertex AI SDK
- Various data types from `kfp.v2.dsl` for handling artifacts, datasets, and pipeline components

### Cell 2: Project Configuration
```python
PROJECT_NAME = "flask-app-2025"
LOCATION = "europe-west1"
BUCKET_NAME = "gs://lab04-bucket"
PIPELINE_ROOT = f"{BUCKET_NAME}/pipeline_root_houseprice/"
BASE_IMAGE = "europe-west1-docker.pkg.dev/flask-app-2025/houseprice/training:latest"
```
This cell sets up the basic configuration for your Vertex AI project:
- `PROJECT_NAME`: Your Google Cloud project ID
- `LOCATION`: The region where your resources will be deployed
- `BUCKET_NAME`: The Google Cloud Storage bucket for storing pipeline artifacts
- `PIPELINE_ROOT`: The root directory in the bucket where pipeline artifacts will be stored
- `BASE_IMAGE`: The Docker image that will be used to run your pipeline components

### Cell 3: Component Definition
```python
@component(base_image=BASE_IMAGE)
def your_component(param1: str, param2: int):
    # Component implementation
    pass
```
This cell shows the basic structure of a pipeline component:
- The `@component` decorator marks a function as a pipeline component
- `base_image` specifies the Docker image to use
- The function parameters define the component's inputs
- The function body contains the component's logic

### Cell 4: Pipeline Definition
```python
@pipeline(
    name="houseprice_pipeline",
    pipeline_root=PIPELINE_ROOT
)
def houseprice_pipeline():
    step1 = your_component(param1="value1", param2=123)
    # Add more steps as needed
```
This cell defines the main pipeline:
- The `@pipeline` decorator marks a function as a pipeline
- `name` specifies the pipeline's name
- `pipeline_root` defines where pipeline artifacts will be stored
- The function body defines the pipeline steps and their connections

### Cell 5: Pipeline Compilation
```python
compiler.Compiler().compile(
    pipeline_func=houseprice_pipeline,
    package_path='houseprice_pipeline.json'
)
```
This cell compiles the pipeline into a JSON file:
- The compiler converts the Python pipeline definition into a format Vertex AI can understand
- The compiled pipeline is saved as 'houseprice_pipeline.json'

### Cell 6: Vertex AI Initialization
```python
aiplatform.init(project=PROJECT_NAME, location=LOCATION)
```
This cell initializes the Vertex AI SDK:
- Sets up the connection to your Google Cloud project
- Configures the region for Vertex AI services

### Cell 7: Pipeline Execution
```python
pipeline_job = aiplatform.PipelineJob(
    display_name="houseprice_pipeline_job",
    template_path="houseprice_pipeline.json",
    pipeline_root=PIPELINE_ROOT
)
pipeline_job.run()
```
This cell creates and runs the pipeline job:
- Creates a `PipelineJob` object with the compiled pipeline
- `display_name` sets a human-readable name for the job
- `template_path` points to the compiled pipeline JSON
- `pipeline_root` specifies where to store job artifacts
- `run()` starts the pipeline execution

The error you see in the notebook is because the example component (`your_component`) is just a placeholder. In a real implementation, you would replace it with actual components for data ingestion, preprocessing, training, and evaluation as described in the previous sections.




