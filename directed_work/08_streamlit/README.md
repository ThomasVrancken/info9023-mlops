# Lab 8 [Sprint 5, W9]: Streamlit

## 0. Introduction

In this lab you will build and deploy a data visualization web application using [Streamlit](https://streamlit.io/). Streamlit is a Python library that turns a plain script into an interactive web app with minimal boilerplate. It is widely used in the ML community for dashboards, model demos, and data exploration tools.

By the end of this lab you will have:
- Built a Streamlit app that reads datasets from a public GCS bucket and displays interactive visualizations
- Migrated the data source from GCS to BigQuery
- Packaged the app in a Docker container using `uv`
- Deployed it to Google Cloud Run so it is accessible from the web

## 1. Prerequisites

1. [uv](https://docs.astral.sh/uv/) installed
2. Docker Desktop installed and running
3. The Google Cloud CLI installed and authenticated
4. Enable the required APIs.
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com --project=YOUR_PROJECT_ID
```

Initialize a project in this lab's folder and add the dependencies.
```bash
uv init
uv add streamlit gcsfs matplotlib numpy pandas scikit-learn seaborn
```

## 2. GCS bucket setup

The example app in section 3 reads four CSV datasets from a public GCS bucket. You create the bucket once and the app reads from it on every request.

Create the bucket.
```bash
gcloud storage buckets create gs://YOUR_PROJECT_ID-streamlit-data \
    --project=YOUR_PROJECT_ID \
    --location=europe-west1
```

Upload the datasets from `data/`.
```bash
gcloud storage cp data/* gs://YOUR_PROJECT_ID-streamlit-data/ \
    --project=YOUR_PROJECT_ID
```

Make the bucket publicly readable so the app can fetch files over HTTPS without authentication.
```bash
gcloud storage buckets add-iam-policy-binding gs://YOUR_PROJECT_ID-streamlit-data \
    --project=YOUR_PROJECT_ID \
    --member=allUsers \
    --role=roles/storage.objectViewer
```

The public URL for each file follows the pattern `https://storage.googleapis.com/YOUR_PROJECT_ID-streamlit-data/filename.csv`.

## 3. The example app

Create `src/data_visualization.py` with the following starter code. It visualizes four datasets loaded from your GCS bucket.

```python
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

BUCKET = "https://storage.googleapis.com/YOUR_PROJECT_ID-streamlit-data"

housing = pd.read_csv(f"{BUCKET}/housing.csv")
iris    = pd.read_csv(f"{BUCKET}/iris.csv")
stocks  = pd.read_csv(f"{BUCKET}/all_stocks_5yr.csv")
wine    = pd.read_csv(f"{BUCKET}/winequality-red.csv")

dataset = st.sidebar.selectbox("Select dataset", [
    "California House Price",
    "S&P 500 stock data",
    "Iris dataset",
    "Wine Quality",
])
theme = st.sidebar.selectbox("Select theme", ["Dark", "Light"])

if theme == "Dark":
    sns.set(style="ticks", context="talk")
    plt.style.use("dark_background")
else:
    sns.set_style("whitegrid")
    plt.style.use("default")

color_map = {
    "NEAR BAY":   "#a6cee3",
    "INLAND":     "#b2df8a",
    "NEAR OCEAN": "#fb9a99",
    "ISLAND":     "#fdbf6f",
    "<1H OCEAN":  "#cab2d6",
}
scaler = MinMaxScaler(feature_range=(1, 100))
housing["size"]  = scaler.fit_transform(housing[["median_house_value"]])
housing["color"] = housing["ocean_proximity"].map(color_map)

if dataset == "California House Price":
    st.write(housing)
    fig, ax = plt.subplots()
    sns.histplot(housing["median_house_value"], bins=50, ax=ax, edgecolor="black")
    ax.set_xlabel("Median House Value")
    ax.set_ylabel("Number of Houses")
    ax.set_title("Histogram of Median House Values")
    st.pyplot(fig)
    st.map(housing, latitude="latitude", longitude="longitude",
           size="size", color="color")

elif dataset == "S&P 500 stock data":
    stock_symbol = st.selectbox("Select a stock symbol", stocks["Name"].unique())
    stock_data   = stocks[stocks["Name"] == stock_symbol]
    st.write(stock_data)
    st.line_chart(stock_data["close"])
    st.scatter_chart(stock_data[["close", "volume"]])

elif dataset == "Iris dataset":
    st.write(iris)
    # TODO: add visualizations

elif dataset == "Wine Quality":
    st.write(wine)
    # TODO: add visualizations
```

Replace `YOUR_PROJECT_ID` with your actual project ID, then run the app locally.
```bash
uv run streamlit run src/data_visualization.py
```

The app opens at `http://localhost:8501`. Study how `st.sidebar`, `st.write`, `st.pyplot`, `st.map`, `st.line_chart`, and `st.selectbox` work before moving on.

## 4. Package and deploy

### 4.1. Dockerfile

The Dockerfile follows the same `uv`-based pattern as Lab 6. Dependencies are exported from the lock file and installed system-wide so the container can run the Streamlit command without a virtual environment.

```Dockerfile
FROM mirror.gcr.io/library/python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv export --frozen --no-dev --no-hashes -o /tmp/requirements.txt && \
    uv pip install --system -r /tmp/requirements.txt

COPY src/ ./src/

ENV PORT=8501

CMD streamlit run src/data_visualization.py --server.port $PORT --server.address=0.0.0.0
```

Build the image.
```bash
docker build --platform linux/amd64 -t streamlit-app:latest .
```

Test it locally before pushing.
```bash
docker run -p 8501:8501 streamlit-app:latest
```

### 4.2. Push to Artifact Registry

Create a repository.
```bash
gcloud artifacts repositories create streamlit-repo \
    --repository-format=docker \
    --location=europe-west1 \
    --project=YOUR_PROJECT_ID
```

Authenticate Docker, tag, and push.
```bash
gcloud auth configure-docker europe-west1-docker.pkg.dev
docker tag streamlit-app:latest \
    europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/streamlit-repo/streamlit-app:latest
docker push europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/streamlit-repo/streamlit-app:latest
```

### 4.3. Deploy to Cloud Run

```bash
gcloud run deploy streamlit-app \
    --project=YOUR_PROJECT_ID \
    --image=europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/streamlit-repo/streamlit-app:latest \
    --region=europe-west1 \
    --port=8501 \
    --allow-unauthenticated
```

Once deployed, Cloud Run prints the service URL. Open it in your browser to verify the app is live.

## 5. Your turn

Build your own Streamlit application and deploy it to Cloud Run. You can extend the example app or start from scratch.

The app must:
- Be visual. A plain data table does not count. Include charts, maps, or other interactive visualizations.
- Read data from BigQuery instead of a public GCS bucket. You have done this in Labs 2 and 6, and you know how to grant the right IAM roles to a service account.
- Read any additional files (images, CSVs, model outputs) from a **private** GCS bucket, with the Cloud Run service account granted access. You have done this in previous labs too.
- Be deployed to Cloud Run and publicly accessible.

Some ideas:
- Complete the Iris and Wine Quality sections in the example app with meaningful plots (pair plots, correlation heatmaps, violin plots)
- Build a dashboard around your project dataset
- Add sidebar filters that update the visualizations dynamically
- Connect to the Flask API from Lab 4 and display model predictions live
- Expose the house price model from Lab 6 through a form where the user enters features and sees the predicted price

You can find inspiration in the [Streamlit app gallery](https://streamlit.io/gallery).

### 5.1. Deliverables

Submit the following on **Gradescope**:
- A screenshot of your deployed app running on Cloud Run (show the URL in the browser)
- The URL of your deployed Cloud Run service
- Your `src/` directory with the app code

The app must be deployed and accessible on **Monday April 14th at 9:00 AM**.

A pass grade requires the app to be accessible from the web, read data from BigQuery, and include at least two meaningful visualizations.

## 6. Cleanup

Once graded, delete all resources to avoid ongoing costs.

Delete the Cloud Run service.
```bash
gcloud run services delete streamlit-app --project=YOUR_PROJECT_ID --region=europe-west1
```

Remove the Artifact Registry repository.
```bash
gcloud artifacts repositories delete streamlit-repo \
    --location=europe-west1 \
    --project=YOUR_PROJECT_ID \
    --quiet
```

Empty and remove the GCS bucket.
```bash
gcloud storage rm -r gs://YOUR_PROJECT_ID-streamlit-data --project=YOUR_PROJECT_ID
```

Delete the BigQuery dataset.
```bash
bq rm -r -f YOUR_PROJECT_ID:streamlit_dataset
```
