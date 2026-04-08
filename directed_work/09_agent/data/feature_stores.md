# Feature Stores

A feature store is a centralized repository for storing, managing, and serving machine learning features. It sits between raw data sources and model training or serving, providing a consistent and reusable set of engineered features that multiple teams and models can share.

## The problem feature stores solve

In most organizations, feature engineering is repeated independently by different teams. One team computes "average transaction amount over the last 30 days" for fraud detection. Another team computes nearly the same feature for credit scoring. Without a feature store, both teams write their own pipelines, maintain their own code, and risk computing slightly different values from the same underlying data. This leads to duplicated effort, inconsistent features, and training-serving skew.

## Training-serving skew

Training-serving skew is one of the most common bugs in production ML systems. It happens when the features used at training time are computed differently from the features used at serving time. For example, the training pipeline might compute a rolling average using a batch SQL query, while the serving pipeline computes it using a streaming window with slightly different logic. The model sees different feature values in production than it saw during training, and its predictions degrade. A feature store eliminates this by providing a single implementation for each feature that is used in both contexts.

## How a feature store works

A feature store typically has two layers. The offline store is optimized for batch reads and is used during training. It stores historical feature values, often in a data warehouse like BigQuery or a columnar format like Parquet on GCS. The online store is optimized for low-latency lookups and is used during serving. It stores the latest feature values in a fast key-value store like Redis, Bigtable, or DynamoDB. An ingestion pipeline keeps both stores in sync.

## Popular feature store tools

Feast is the most widely used open-source feature store. It supports BigQuery, Snowflake, and Redshift as offline stores and Redis or DynamoDB as online stores. Google Cloud offers Vertex AI Feature Store, which is fully managed and integrates natively with BigQuery and Vertex AI Pipelines. Other options include Tecton (commercial, built by the creators of Uber's Michelangelo), Hopsworks (open source), and Databricks Feature Store.

## When to use a feature store

A feature store adds value when multiple models share features, when training-serving skew is a concern, or when feature computation is expensive and should not be repeated. For a single model with simple features, a feature store may be overkill. The decision depends on the scale of the organization and the number of models in production.
