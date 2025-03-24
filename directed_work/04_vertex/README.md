# Directed work 4 [Sprint 4, W08]: Vertex

## 0. Introduction
The goal of this directed work is to make you familiar with the Vertex AI platform.

## 1. Prerequisites

1. Have a working version of [python](https://www.python.org/downloads/)
2. Have a working version of [Docker Desktop](https://docs.docker.com/desktop/)
3. Docker daemon running.
4. Enable Vertex AI API in your Google Cloud project.

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
   - Custom code components that you write.
   - Pre-built components from Vertex AI's component library.
   - Each component runs in its own Docker container, which we push to Google Cloud's Artifact Registry.

2. Pipeline Creation: We chain these components together to create a pipeline. The pipeline defines:
   - The sequence of component execution.
   - Data flow between components.
   - Required resources and configurations.

3. Pipeline Deployment: The pipeline is deployed to Vertex AI Pipelines, where it:
   - Runs in a fully managed environment.
   - Can be scheduled or triggered on demand.
   - Provides monitoring and logging capabilities.
   - Maintains versioning and reproducibility.

4. Monitoring & Management: Once deployed, Vertex AI provides tools to:
   - Track pipeline executions.
   - Monitor model performance.
   - Manage model versions.
   - Handle model updates and rollbacks.

## 3. Example with the House Price Prediction Dataset

### 3.1. Dataset and Requirements Setup

#### Dataset Overview
We'll be using the [Housing Prices Dataset](https://www.kaggle.com/datasets/yasserh/housing-prices-dataset?resource=download) from Kaggle. This dataset contains information about house prices and various features including:
- Square footage;
- Number of bedrooms;
- Number of bathrooms;
- Year built;
- And other relevant features.

Before starting with the pipeline, you need to:
1. Download the dataset from Kaggle
2. Create a Google Cloud Storage bucket (if you don't have one already):
```bash
gsutil mb -l europe-west1 gs://lab04-bucket
```
3. Upload the dataset to your bucket:
```bash
gsutil cp Housing.csv gs://lab04-bucket/data/
```

The dataset will be accessed by the pipeline at `gs://lab04-bucket/data/Housing.csv`.

#### Required Dependencies
First, let's set up our Python environment with the necessary packages. Create a `requirements.txt` file with the following dependencies:

```txt
kfp==2.7.0
google-cloud-aiplatform==1.42.1
google-cloud-storage==2.14.0
google-auth==2.27.0
google-auth-oauthlib==1.2.0
gcsfs==2024.2.0
numpy>=1.22.4,<2
pandas==2.1.0
scikit-learn==1.3.0
matplotlib==3.8.0
seaborn==0.13.0
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
└── run_pipeline.py
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
    HTML,        # For visualization
    component,   # For creating pipeline components
    pipeline     # For defining the pipeline
)
from kfp.v2 import compiler
from google.cloud.aiplatform import pipeline_jobs

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

Before we can create our pipeline components, we need to set up a Docker image that will be used as a base image to run all our components. This image needs to be stored in Google Cloud's Artifact Registry. Here's how to do it step by step:

1. First, create a Dockerfile that will serve as our base image for the components:
```Dockerfile
FROM mirror.gcr.io/library/python:3.9
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY src /app/src
RUN pip install -r /app/requirements.txt
ENTRYPOINT ["bash"]
```

Key points about this Dockerfile:
- We use `mirror.gcr.io/library/python:3.9` instead of `python:3.9` because:
  - It's faster to pull as it's a Google Container Registry (GCR) mirror
  - It reduces external dependencies
  - It's maintained by Google
- `ENTRYPOINT ["bash"]` keeps the container running after component execution
- The image includes our Python dependencies and source code

2. Set up your environment variables:
```bash
PROJECT_ID="your-project-id"
REGION="europe-west1"
REPOSITORY="vertex-ai-pipeline-example"
IMAGE_NAME="training"
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
# For macOS users, specify the platform explicitly
docker build --platform linux/amd64 -t $IMAGE_NAME:$IMAGE_TAG .
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
- When building on macOS, use the `--platform linux/amd64` flag to ensure compatibility with Google Cloud
- You can verify your image in the Google Cloud Console under Artifact Registry

## 4. Understanding the Components

Let's go through each component in our pipeline:

### 4.1: Data Ingestion Component
This component downloads and prepares the initial dataset:

```python
@component(
    base_image=BASE_IMAGE,
    output_component_file="data_ingestion.yaml"
)
def data_ingestion(
    dataset: Output[Dataset]
):
    """
    Loads and prepares the house price dataset.
    
    Args:
        dataset: Output artifact to store the prepared dataset
    """
    import pandas as pd
    import os
    import sys
    import traceback
    import fsspec
    
    try:
        print("Starting data ingestion...")
        
        # TO DO:
        # 1. Load the dataset from the GCS bucket.
        # 2. Save the dataset to the output artifact.
        
        # Save the dataset
        print(f"Saving dataset to {dataset.path}...")
        df.to_csv(dataset.path, index=False)
```

### 4.2: Data Preprocessing Component
This component cleans and prepares the data for training:

```python
@component(
    base_image=BASE_IMAGE,
    output_component_file="preprocessing.yaml"
)
def preprocessing(
    input_dataset: Input[Dataset],
    preprocessed_dataset: Output[Dataset],
):
    """
    Preprocesses the dataset for training.
    
    Args:
        input_dataset: Input dataset from the data ingestion step
        preprocessed_dataset: Output artifact for the preprocessed dataset
    """
    import pandas as pd
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    
    # Load the dataset
    df = pd.read_csv(input_dataset.path)

    # TO DO:
    # 2. Scale numerical features.
    # 3. Encode categorical features.
    # 4. Save the preprocessed dataset to the output artifact.
    
    # Save preprocessed dataset
    df_processed.to_csv(preprocessed_dataset.path, index=False)
    print(f"Preprocessed dataset saved to: {preprocessed_dataset.path}")
```

### 4.3: Model Training Component
This component trains the model using the preprocessed data:

```python
@component(
    base_image=BASE_IMAGE,
    output_component_file="training.yaml"
)
def training(
    preprocessed_dataset: Input[Dataset],
    model: Output[Model],
    metrics: Output[Metrics],
    hyperparameters: dict
):
    """
    Trains the model on the preprocessed dataset.
    
    Args:
        preprocessed_dataset: Input preprocessed dataset
        model: Output artifact for the trained model
        metrics: Output artifact for training metrics
        hyperparameters: Dictionary of hyperparameters
    """
    import pandas as pd
    import joblib
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score
    
    # Load preprocessed dataset
    df = pd.read_csv(preprocessed_dataset.path)

    # TO DO:
    # 1. Split features and target.
    # 2. Split into train and validation sets.
    # 3. Initialize and train the model.
    # 4. Make predictions.
    # 5. Calculate metrics.
    # 6. Save the model.

    joblib.dump(rf_model, model.path)
    print(f"Model saved to: {model.path}")
    print(f"Validation MSE: {mse:.2f}")
    print(f"Validation R2: {r2:.2f}") 

```

### 4.4: Model Evaluation Component
This component evaluates the model's performance:

```python
@component(
    base_image=BASE_IMAGE,
    output_component_file="evaluation.yaml"
)
def evaluation(
    model: Input[Model],
    preprocessed_dataset: Input[Dataset],
    metrics: Output[Metrics],
    html: Output[HTML]
):
    """
    Evaluates the model's performance and generates visualizations.
    
    Args:
        model: Input trained model
        preprocessed_dataset: Input preprocessed dataset
        metrics: Output artifact for evaluation metrics
        html: Output artifact for visualization HTML
    """
    import pandas as pd
    import joblib
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import mean_squared_error, r2_score

    # TO DO:
    # 1. Load the model and dataset.
    # 2. Make predictions.
    # 3. Calculate metrics.
    # 4. Save the metrics.
    # OPTIONAL: 5. Create visualizations.
    # OPTIONAL:6. Save the HTML report.
    
    # Load the model and dataset
    rf_model = joblib.load(model.path)
   
    # ...
    
    with open(html.path, 'w') as f:
        f.write(html_content)
    
    print(f"Evaluation report saved to: {html.path}")
```

### 4.5: Assembling the Pipeline
Now that we have all our components, let's assemble them into a pipeline:

```python
@pipeline(
    name="houseprice_pipeline",
    pipeline_root=PIPELINE_ROOT
)
def houseprice_pipeline():
    # Define the components
    ingestion_task = data_ingestion()
    
    preprocessing_task = preprocessing(
        input_dataset=ingestion_task.outputs["dataset"]
    )
    
    training_task = training(
        preprocessed_dataset=preprocessing_task.outputs["preprocessed_dataset"],
        hyperparameters={
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        }
    )
    
    evaluation_task = evaluation(
        model=training_task.outputs["model"],
        preprocessed_dataset=preprocessing_task.outputs["preprocessed_dataset"]
    )
```

## 5. Running the Pipeline

1. First, compile the pipeline:
```python
compiler.Compiler().compile(
    pipeline_func=houseprice_pipeline,
    package_path='houseprice_pipeline.json'
)
```

2. Initialize Vertex AI:
```python
aiplatform.init(project=PROJECT_NAME, location=LOCATION)
```

3. Run the pipeline:
```python
pipeline_job = aiplatform.PipelineJob(
    display_name="houseprice_pipeline_job",
    template_path="houseprice_pipeline.json",
    pipeline_root=PIPELINE_ROOT
)
pipeline_job.run()
```

## 6. Your turn.

Now that we have our environment set up, you need to:

1. Submit 3 pictures as evidence of your work:
   - Screenshot of pipeline
   - Screenshot of output data
   - Screenshot of performance metrics

2. Provide the code for the components.

You have until 06/04/2025 23:59 to submit your work.







