# Directed work 4 [Sprint 4, W08]: Vertex

## 0. Introduction
The goal of this directed work is to make you familiar with the Vertex AI platform.

## 1. Prerequisites

1. Have a working version of [python](https://www.python.org/downloads/)
2. Have a working version of [Docker Desktop](https://docs.docker.com/desktop/)
3. Docker daemon running.

## 2. Vertex AI

### 2.1. Presentation of Vertex AI

Vertex AI is a platform that allows you to build, train, and deploy machine learning models i.e. to orchestrate your ML workflow. It is a fully managed platform that allows you to focus on building your model and not the infrastructure. i.e. in a serverless way.

How does it work?

We will need first to define components of our workflow using Kubeflow Pipeline SDK. Each of these components can be a custom code or a pre-built component. They will all have their own Docker container that we will push to a Artifact Registry.

Then we will chain these components together using a pipeline.

We will then deploy this pipeline to a Vertex AI Pipeline.


### 2.2. Components of a Vertex AI workflow

- Kubeflow Pipeline SDK
- Docker container
- Artifact Registry
- Storage bucket
- Vertex AI Pipeline

## 3. Example with the house price prediction dataset

The dataset is available [here on Kaggle](https://www.kaggle.com/datasets/yasserh/housing-prices-dataset?resource=download).

### 3.1. Import requirements

For this example, we will use the house price prediction dataset. We will need the `kfp` library to build the pipeline.

```python
from kfp.v2 import dsl
from kfp.v2.dsl import (Artifact,
                        Dataset,
                        Input,
                        Model,
                        Output,
                        Metrics,
                        Markdown,
                        HTML,
                        component,
                        OutputPath,
                        InputPath)
                    
from kfp.v2 import compiler
from google.cloud.aiplatform import pipeline_jobs
```

`dsl` is the domain specific language of Kubeflow Pipeline. It is used to define the components of the pipeline and interact with it.

`compiler` is used to compile the pipeline into a JSON file.

`pipeline_jobs` is used to deploy the pipeline to a Vertex AI Pipeline.

We can then define a PIPELINE_ROOT constant to store the pipeline and the artifacts.

```python
PIPELINE_ROOT = f"{BUCKET_NAME}/{PIPELINE_ROOT_FOLDER}"
```

### 3.2. Define the components

We will need to define the components of the pipeline.
1. We first need to define the base image that will be used to run the pipeline. This is mandatory because the components will be run in a container.
    ```python
    BASE_IMAGE = f"europe-west1-docker.pkg.dev/{PROJECT_NAME}/vertex-ai-pipeline-example/training:latest"
    ```

    This image can be defined as:

    ```Dockerfile
    FROM mirror.gcr.io/library/python:3.8
    WORKDIR /app
    COPY requirements.txt /app/requirements.txt
    COPY src /app/src
    RUN pip install -r /app/requirements.txt
    ENTRYPOINT ["bash"]
    ```

    - Here `mirror.gcr.io/library/python:3.8` has several advantages compared to the default `python:3.8` image as we are working on a GCP project.

        1. It is faster to pull because it is a Google Container Registry (GCR) mirror which caches popular Docker Hub images. 
        2. It reduces external dependencies because it is a Google maintained image.
        3. There is no functional difference with `python:3.8` image.

    - `ENTRYPOINT ["bash"]` is used to keep the container running after the execution of the component because the default behavior is to stop the container after the execution of the component.

2. Build this image

    ```bash
    docker build -t $BASE_IMAGE .
    docker tag $BASE_IMAGE $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_TAG
    ```

3. Create a repository in Artifact Registry

    ```bash
    gcloud beta artifacts repositories create $REPOSITORY --repository-format=docker --location=$REGION
    ```

4. Configure Docker to authenticate to Artifact Registry

    ```bash
    gcloud auth configure-docker $REGION-docker.pkg.dev
    ```

5. Push the image to Artifact Registry

    ```bash
    docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_TAG
    ```

Now you should have the image in the Artifact Registry. Ypu can therefore use it as a base image for the components of the pipeline.

```python
@component(
    base_image="<REGION>-docker.pkg.dev/<PROJECT_ID>/<REPOSITORY>/<IMAGE_TAG>"
)
```
![artifact_registry](img/1.png)



#### 3.2.1. Data ingestion

```python
BASE_IMAGE = f"{REGION}-docker.pkg.dev/{PROJECT_NAME}/vertex-ai-pipeline-example/training:latest"

@component(
    base_image=BASE_IMAGE,
    output_component_file="data_ingestion.yaml",
)

def get_house_data(
    data_path: str,
    dataset: Output[Dataset],
):
    import pandas as pd

    df_data = pd.read_csv(data_path + "/housing.csv")
    df_data.to_csv(dataset.path, index=False)
```

The first part of the code is the definition of the component. The `@component` decorator is used to define the docker image. The `base_image` parameter is used to define the base image of the component. The `output_component_file` parameter is used to define the name of the file that will be generated by the component. 

Once this code is run, a `data_ingestion.yaml` file will be generated. This file will be used to define the component in the pipeline. We will be able to access the output of the component using the `dataset` parameter.




