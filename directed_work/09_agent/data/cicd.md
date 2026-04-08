# CI/CD in Machine Learning

Continuous Integration and Continuous Deployment (CI/CD) is a set of practices that automate the process of integrating code changes and deploying them to production. In traditional software engineering, CI/CD pipelines run unit tests, build artifacts, and deploy binaries. In machine learning, the scope is broader because the artifact is not just code but also data and a trained model.

## Why CI/CD matters for ML

A machine learning system has more moving parts than a standard web application. The model depends on training data, feature engineering code, hyperparameters, and the training infrastructure. A change to any of these can silently degrade model quality without breaking any test. CI/CD pipelines catch these regressions early by running automated checks on every commit.

## What a typical ML CI/CD pipeline does

A typical pipeline includes the following stages. First, linting and unit tests validate that the code is syntactically correct and that utility functions behave as expected. Second, data validation checks verify that the training data conforms to expected schemas, ranges, and distributions. Third, a training job runs on a small subset of data to confirm that the model converges and that metrics are within acceptable bounds. Fourth, integration tests verify that the model can be loaded by the serving infrastructure and that the API returns valid responses. Finally, deployment promotes the new model to a staging environment and, after approval, to production.

## Tools commonly used

Popular CI/CD tools for ML include GitHub Actions, GitLab CI, Jenkins, and Google Cloud Build. These tools trigger pipelines automatically when code is pushed to a repository. For ML-specific orchestration, teams often combine a general CI tool with a pipeline framework like Kubeflow Pipelines, Vertex AI Pipelines, or Airflow.

## The difference between CI/CD for code and CI/CD for models

In traditional CI/CD, the artifact is deterministic. The same source code always produces the same binary. In ML, training is stochastic. The same code and data can produce slightly different models due to random initialization, data shuffling, or GPU non-determinism. This means that ML CI/CD must include metric-based checks (for example, fail the pipeline if accuracy drops below a threshold) in addition to traditional pass/fail tests.

## Model registries

A model registry is a versioned store for trained models. After a CI/CD pipeline validates a new model, it publishes the model to a registry with metadata such as training date, dataset version, and evaluation metrics. The serving infrastructure then pulls models from the registry rather than from a local file. This decouples training from serving and makes rollbacks straightforward.
