# Experiment Tracking

Experiment tracking is the practice of systematically recording the parameters, code, data, and results of every model training run. It answers the question "what did I change and what happened?" across dozens or hundreds of experiments.

## Why experiment tracking matters

Machine learning development is inherently iterative. You try different architectures, hyperparameters, feature sets, and data preprocessing steps. Without tracking, it is impossible to remember what you tried, what worked, and why. Teams that do not track experiments waste time re-running configurations they already tested, lose the ability to reproduce their best model, and cannot explain to stakeholders why they chose one model over another.

## What to track

A good experiment tracking system records several pieces of information for every run. Parameters include hyperparameters (learning rate, batch size, number of layers), data versions, and preprocessing configurations. Metrics include training loss, validation loss, accuracy, F1, RMSE, or any other evaluation measure. Artifacts include the trained model weights, plots, confusion matrices, and evaluation reports. Environment information includes the Python version, library versions, GPU type, and random seed. Code version includes the git commit hash or a snapshot of the training script.

## Popular tools

MLflow is the most widely used open-source experiment tracking tool. It provides a tracking server with a web UI where you can compare runs, filter by metrics, and download artifacts. Weights and Biases (W&B) is a commercial tool with a generous free tier that offers real-time dashboards, hyperparameter sweeps, and team collaboration features. Other options include Neptune, Comet ML, and TensorBoard (limited to metric visualization). Google Cloud offers Vertex AI Experiments, which integrates with Vertex AI Pipelines and stores experiment metadata alongside pipeline runs.

## How experiment tracking fits into MLOps

Experiment tracking is the foundation of reproducibility. When a model is promoted to production, the tracking system provides a complete record of how it was trained. If a production model degrades, the team can look up its training parameters, reproduce the run, and compare it against new experiments. This audit trail is also important for regulatory compliance in industries like healthcare and finance, where model decisions must be explainable and reproducible.

## Best practices

Tag experiments with meaningful names that describe the hypothesis being tested, not just "run_42". Log metrics at every epoch, not just the final value, so you can diagnose training dynamics. Version your data alongside your code, because a model is only reproducible if both the code and the data are pinned. Use the tracking system's comparison features to make decisions rather than eyeballing individual runs. Finally, clean up failed or irrelevant experiments to keep the tracking dashboard useful.
