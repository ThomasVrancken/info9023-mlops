# Model Monitoring

Model monitoring is the practice of continuously observing a deployed machine learning model to detect degradation in its performance, shifts in the input data, or unexpected behavior. Unlike traditional software, which either works or crashes, a model can silently return worse predictions without any error. Monitoring catches this before it impacts users.

## Why models degrade over time

The world changes. A model trained on 2024 data may not perform well on 2026 data because user behavior, market conditions, or language patterns have shifted. This phenomenon is called data drift. There is also concept drift, where the relationship between features and the target variable changes. For example, a house price model trained before a housing crisis will overestimate prices after the crash.

## What to monitor

There are three main categories. First, model performance metrics such as accuracy, precision, recall, F1, RMSE, or R2 measured on live traffic or a holdout set. A drop in these metrics signals that the model is underperforming. Second, data quality metrics such as missing value rates, feature distributions, and schema compliance. A sudden increase in null values or a shift in the distribution of a key feature can indicate a data pipeline issue. Third, operational metrics such as latency, throughput, error rates, and resource utilization. These track whether the serving infrastructure is healthy.

## Alerting

Monitoring without alerting is just logging. Teams configure alerts that fire when a metric crosses a threshold. For example, an alert might trigger if the median prediction latency exceeds 200 milliseconds or if the distribution of a key feature diverges from the training distribution by more than a specified statistical distance (often measured with KL divergence or the Population Stability Index).

## Tools commonly used

Google Cloud offers Vertex AI Model Monitoring, which can automatically detect data drift and feature skew by comparing serving data against the training baseline. Other popular tools include Evidently AI (open source, generates drift reports), Arize AI, and WhyLabs. For custom monitoring, teams often send metrics to a time-series database like Prometheus and visualize them in Grafana.

## Retraining triggers

Monitoring feeds into retraining decisions. When monitoring detects that model performance has dropped below an acceptable threshold, it can trigger a retraining pipeline automatically. This closes the loop between serving and training and is a hallmark of mature MLOps practices. The retraining pipeline pulls fresh data, trains a new model, validates it against the degraded model, and promotes it to production if it performs better.
