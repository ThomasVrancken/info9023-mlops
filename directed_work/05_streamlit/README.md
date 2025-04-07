# Directed work 5 [Sprint 5, W09]: Streamlit

## 0. Description

In this lab, you will learn how to create a simple web application using [Streamlit](https://streamlit.io/). Streamlit is a Python library that allows you to create web applications with minimal effort. You can use Streamlit to create interactive data visualizations, dashboards, and more.

### 0.1. Objectives

- Learn how to create a simple web application using Streamlit.
- Learn how to create interactive data visualizations using Streamlit.

### 0.2. Prerequisites

- Install Streamlit by running the following command:

```bash
pip install streamlit
```

You will also need to install the following library to import bucket cloud storage data:

```bash
pip install gcsfs
```

### 0.3 Tasks

In the lab:
- We will first create a streamlit application that allows data vizualization of several datasets that the user can pick from a bucket in Google Cloud Storage. To showcase the power of Streamlit, we will show multiple types of visualizations such as histograms, scatter plots, line plots, geographic maps, and more. The datasets are the following:

    1. [California House Price](https://www.kaggle.com/datasets/shibumohapatra/house-price?resource=download)

    2. [S&P 500 stock data](https://www.kaggle.com/datasets/camnugent/sandp500)

    3. [Iris dataset](https://www.kaggle.com/datasets/uciml/iris)

    4. [Wine Quality](https://www.kaggle.com/datasets/uciml/red-wine-quality-cortez-et-al-2009)

- The second task will be to create an application with streamlit either based on the app you used in the 3rd directed work or based on your project.


## 1. Google Cloud Storage bucket

### 1.1. Create a Google Cloud Storage bucket
As a first step, you need to create a Google Cloud Storage bucket to store the datasets.

```bash
export BUCKET_NAME="{replace_with_your_bucket_name}"
gsutil mb -l europe-west1 gs://$BUCKET_NAME
```

### 1.2. Upload the datasets to the bucket
Now, you need to put the different datasets in a Google Cloud Storage bucket. You can use the code we saw in the previous lab to upload the datasets to a bucket:

```python
from google.cloud import storage

def upload_blob(bucket_name, source_file_path, destination_blob_name):
    """Uploads a file to the specified bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)

    print(f"File {source_file_path} uploaded to {destination_blob_name}.")

# Set variables
bucket_name = '{your_bucket_name}'
file_mapping = {
    'data/housing.csv': 'housing.csv',
    'data/iris.csv': 'iris.csv',
    'data/all_stocks_5yr.csv': 'all_stocks_5yr.csv',
    'data/winequality-red.csv': 'winequality-red.csv'
}

# Example usage
for source_path, dest_name in file_mapping.items():
    upload_blob(bucket_name, source_path, dest_name)
```
### 1.3 Access the datasets in the bucket
Either you don't want your datasets to be accessed by anyone, or you want to make them public. 


Here, we'll show you how to make the data public to be able to access it from a Streamlit application:
1. In the Google Cloud console, go to the [Cloud Storage Buckets](https://console.cloud.google.com/storage/browser) page.

2. In the list of buckets, click the name of the bucket that you want to make public.

3. Select the `Permissions` tab near the top of the page.

4. In the Permissions section, click the `Grant access` button.

5. The Grant access dialog box appears.

6. In the New principals field, enter `allUsers`.

7. In the Select a role drop down, enter `Storage Bucket Viewer` in the filter box and select the `Storage Bucket Viewer` from the filtered results.

8. Click `Save`.

9. Click `Allow public access`.

Once public access has been granted, `Copy URL` appears for each object in the public access column. You can click this button to get the public URL for the object.


Or you can use this command in your terminal: 
    
```bash
gcloud storage buckets add-iam-policy-binding gs://BUCKET_NAME --member=allUsers --role=roles/storage.objectViewer
```

where `BUCKET_NAME` is the name of your bucket.


## 2. Create a Streamlit application to visualize the datasets

Create a Streamlit application that allows data visualization of the datasets. The application should have the following features:

- A sidebar that allows the user to select the dataset to visualize.
- A main panel that displays the selected dataset.
- The main panel should display multiple types of visualizations such as histograms, scatter plots, line plots, geographic maps, and more.
- The user should be able to interact with the visualizations (e.g., zoom in, zoom out, pan, etc.).

### 2.1. Visualizations

Here are some examples of visualizations you can create for each dataset:

- California House Price:
    - Data table.
    - Histogram of house prices.
    - Geographic map of houses with a point size proportional to the house price.

- S&P 500 stock data:
    - Data table.
    - Sidebar to choose a stock
    - Line plot of the chosen stock prices over time.
    - Scatter plot of stock prices vs. trading volume.

### 2.2. Example code

Here is an example of how you can create a Streamlit application that allows the user to select a dataset and visualize it.

```python
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import streamlit as st

from sklearn.preprocessing import MinMaxScaler

# Load the datasets
housing = pd.read_csv(
    'https://storage.googleapis.com/{BUCKET_NAME}/housing.csv')
iris = pd.read_csv(
    'https://storage.googleapis.com/{BUCKET_NAME}/iris.csv')

# Sidebar
dataset = st.sidebar.selectbox('Select dataset', ['California House Price', 
                                                  'S&P 500 stock data'])

theme = st.sidebar.selectbox('Select theme', ['Dark', 'Light'])

# Set the background color based on the selected theme
if theme == 'Dark':
    sns.set(style="ticks", context="talk")
    plt.style.use("dark_background")
else:
    sns.set_style('whitegrid')
    plt.style.use('default')


# Define a mapping from categories to colors
color_map = {
    'NEAR BAY': '#a6cee3',  # pastel blue
    'INLAND': '#b2df8a',  # pastel green
    'NEAR OCEAN': '#fb9a99',  # pastel red
    'ISLAND': '#fdbf6f',  # pastel orange
    '<1H OCEAN': '#cab2d6',  # pastel purple
}

# Normalize the 'median_house_value' column to a range between 1 and 100
scaler = MinMaxScaler(feature_range=(1, 100))
housing['size'] = scaler.fit_transform(housing[['median_house_value']])

# Apply the mapping to the 'ocean_proximity' column
housing['color'] = housing['ocean_proximity'].map(color_map)

# Main panel
if dataset == 'California House Price':
    st.write(housing)

    # Create a histogram for the 'median_house_value' column with seaborn
    fig, ax = plt.subplots()
    sns.histplot(housing['median_house_value'], bins=50, ax=ax, 
                 edgecolor='black')
    ax.set_xlabel('Median House Value')
    ax.set_ylabel('Number of Houses')
    ax.set_title('Histogram of Median House Values')
    st.pyplot(fig)

    st.map(housing,
    latitude='latitude',
    longitude='longitude',
    size='size',
    color='color',)

elif dataset == 'S&P 500 stock data':
    st.write(stocks)
    # Add visualizations for S&P 500 stock data dataset

    #Add a box to select a stock symbol
    stock_symbol = st.selectbox('Select a stock symbol',
                                stocks['Name'].unique())
    #get a subset of the dataset for the selected stock
    stock_data = stocks[stocks['Name'] == stock_symbol]
    #plot the stock close price over time 
    st.line_chart(stock_data['close'])

    # Scatter plot of stock price vs volume
    st.scatter_chart(stock_data[['close', 'volume']])
``` 

### 2.3 Docker file

Now that we have our Streamlit application, we can create a Dockerfile to run it in a container. 

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY data_visualization.py /app/src/
COPY requirements.txt /app/src/

ENV PORT=8501

RUN pip install -r src/requirements.txt

CMD streamlit run src/data_visualization.py --server.port $PORT --server.address=0.0.0.0
```

### 2.5 Requirements file

Create a requirements.txt file with the following content:

```txt
fsspec
gcsfs
matplotlib
numpy
pandas
scikit-learn
seaborn
streamlit
```

### 2.6 Build and run the Docker container

To build the Docker container, run the following command:

```bash
export IMAGE_NAME="{IMAGE_NAME}"
export IMAGE_TAG="latest"
```

```bash
docker build --platform linux/amd64-t $IMAGE_NAME:$IMAGE_TAG
```

To run the Docker container, run the following command:

```bash
docker run -p 8501:8501 streamlit-app
```

The Streamlit application should now be running in a Docker container. You can access it by opening a web browser and navigating to `http://localhost:8501`.

## 3. Deploy the Streamlit application to Google Cloud Run

To see the list of your projects you can the following command in your terminal:

```bash
gcloud projects list
```

To set the project you want to work with, you can use the following command:

```bash
gcloud config set project PROJECT_ID
```
To deploy the Streamlit container to Google Cloud Run, you first have to tag your Docker image with a registry name. If you're using Google Artifact Registry you need to first submit the docker image to Artifact Registry as.

```bash
gcloud builds submit --tag PROJECT_ID/IMAGE_NAME:TAG
```

You can verify if your docker image has been successfully submitted to the registry by running the following command:

```bash
gcloud container images list
```

Then, you can deploy the Docker image to Google Cloud Run using the following command:

```bash
gcloud run deploy SERVICE_NAME --image PROJECT_ID/IMAGE_NAME:TAG --platform managed --region europe-west1 --allow-unauthenticated
```

To get some information about your service, you can use the following command:

```bash
gcloud run services describe SERVICE_NAME --region europe-west1
```

To delete your Google Cloud Run service, you can use the following command:

```bash
gcloud run services delete SERVICE_NAME --region europe-west1
```


## 3. Your turn

Create a Streamlit application to visualize the dataset of your choice (Other than the ones we used in the lab). 
:warning: Choose a dataset that have nice features to visualize. 

For an easier start, you can either base your app on the app you used in the 3rd directed work (IF IT HAS NICE VISUALIZATION-POTENTIAL) or based on your project.

For example, you can:
- Put a button to visualize the evolution of the stock market over time.
- Put a train button with a sidebar for the number of epochs, the learning rate and have a progress bar.
- Visualize a categorical output with probabilities of belonging to a class.
- Visualize a confusion matrix after the training of your model.
- Visualize the output of your model in a dashboard.
- etc.

Either your streamlit application should manipulate data from a dataset or it should be a dashboard to visualize the output of your model or manipulate outputs of another service i.e. communicate with another service in cloud run or predictions made by this other service.

### 3.1. Deliverables

You need to deploy the Streamlit application to Google Cloud Run. We will check the app and the deployment.
What we ask you: 
- Make sure the app is working as expected.
- Make sure the app is deployed to Google Cloud Run.
- Make sure the app is accessible from the web.
- Your streamlit app should be VISUAL. We don't want to see a 'hello world' app. Make a cool dashboard with plots, maps, etc.

We will check the app on Monday April 7th at 9:00 AM.

It will be a pass grade if we can access the app from the web and use it with some vizualizations.


### 3.1 Examples of Streamlit applications

You can find more examples of Streamlit applications in the [App galery](https://streamlit.io/gallery). 





