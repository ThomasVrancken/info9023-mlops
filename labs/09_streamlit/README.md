# Lab W09: Streamlit

## 0. Description

In this lab, you will learn how to create a simple web application using Streamlit. Streamlit is a Python library that allows you to create web applications with minimal effort. You can use Streamlit to create interactive data visualizations, dashboards, and more.

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

- The second task will be to create an application with streamlit to predict the price of a house in California using a simple linear regression model. The user will be able to input the features of the house and the model will predict the price of the house.


## 1. Google Cloud Storage bucket

### 1.1. Create a Google Cloud Storage bucket
As a first step, you need to create a Google Cloud Storage bucket to store the datasets. You can create go the previous lab and see how it has been done.

### 1.2. Upload the datasets to the bucket
Now, you need to put the different datasets in a Google Cloud Storage bucket. You can use the code we saw in the previous lab to upload the datasets to a bucket:

```python
from google.cloud import storage

def upload_blob(service_account_path, bucket_name, source_file_path, destination_blob_name):
    """Uploads a file to the specified bucket."""
    storage_client = storage.Client.from_service_account_json(service_account_path)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)

    print(f"File {source_file_path} uploaded to {destination_blob_name}.")

# Set variables
service_account_path = '{your_svc_path}'
bucket_name = 'mlsd-bucket'
source_file_paths = ['data/housing.csv', 'data/iris.csv', 'data/all_stocks_5yr.csv', 'data/winequality-red.csv']
destination_blob_names = ['housing.csv', 'iris.csv', 'all_stocks_5yr.csv', 'winequality-red.csv']

# Example usage
for i in range(len(source_file_paths)):
    upload_blob(service_account_path, bucket_name, source_file_paths[i], destination_blob_names[i])
```
### 1.3 Access the datasets in the bucket
Either you don't want your datasets to be accessed by anyone, or you want to make them public. 


Here, we'll show you how to make the data public to be able to access it from a Streamlit application:
1. In the Google Cloud console, go to the [Cloud Storage Buckets](https://console.cloud.google.com/storage/browser) page.

2. In the list of buckets, click the name of the bucket that you want to make public.

3. Select the Permissions tab near the top of the page.

4. In the Permissions section, click the `Grant access` button.

5. The Grant access dialog box appears.

6. In the New principals field, enter `allUsers`.

7. In the Select a role drop down, enter `Storage Object Viewer` in the filter box and select the `Storage Object Viewer` from the filtered results.

8. Click Save.

9. Click Allow public access.

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

Exercise: create visualizations for the Iris and Wine Quality datasets.

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
    'https://storage.googleapis.com/bucket-lab9/housing.csv')
iris = pd.read_csv(
    'https://storage.googleapis.com/bucket-lab9/iris.csv')
stocks = pd.read_csv(
    'https://storage.googleapis.com/bucket-lab9/all_stocks_5yr.csv')
wine = pd.read_csv(
    'https://storage.googleapis.com/bucket-lab9/winequality-red.csv')

# Sidebar
dataset = st.sidebar.selectbox('Select dataset', ['California House Price', 
                                                  'S&P 500 stock data', 
                                                  'Iris dataset', 
                                                  'Wine Quality'])

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

elif dataset == 'Iris dataset':
    st.write(iris)
    # Add visualizations for Iris dataset
elif dataset == 'Wine Quality':
    st.write(wine)
    # Add visualizations for Wine Quality dataset
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

### (OPTIONAL) 2.6 Build and run the Docker container

To build the Docker container, run the following command:

```bash
docker build -t streamlit-app .
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

To deploy the Streamlit container to Google Cloud Run, you first have to tag your Docker image with a registry name. If you're using Google Container Registry (GCR) you need to first submit the docker image to Container Registry (Now Artifact Registry as Container Registry is deprecated).

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/IMAGE_NAME:TAG
```

You can verify if your docker image has been successfully submitted to the registry by running the following command:

```bash
gcloud container images list
```

Then, you can deploy the Docker image to Google Cloud Run using the following command:

```bash
gcloud run deploy CONTAINER_NAME --image gcr.io/PROJECT_ID/DOCKER_IMAGE_NAME:TAG --platform managed --region europe-west1 --allow-unauthenticated
```

To get some information about your service, you can use the following command:

```bash
gcloud run services describe CONTAINER_NAME --region europe-west1
```

To delete your Google Cloud Run service, you can use the following command:

```bash
gcloud run services delete CONTAINER_NAME --region europe-west1
```


## 3. Create a Streamlit application to predict the price of a house in California

Another thing we can do is to create a Streamlit application to use the microservices that we created in the previous lab about Docker Compose. We will not have a web-application flask app with Jinja2 templates but a Streamlit application that will use the microservices to preprocess data, train the model and predict the price of a house in California. So we will create a streamlit applcation that allows the user the same things as our web app from last week but with the following features:

- A sidebar that allows the user to input the features of the house (e.g., longitude, latitude, number of bedrooms, number of bathrooms, etc.).

- A main panel that displays the predicted price of the house.

So the code is the same as last week but we will use Streamlit to create the web application.

### 3.1 Example code

This is the code of `app.py` that we will use to create the Streamlit application:

```python
import os
import requests
import streamlit as st

# Add a logo
st.sidebar.image('./figures/uliege_faculte_sciencesappliquees_logo.svg', 
                 width=300)



# Data preprocessing endpoint (triggers preprocessing.py)
def process_data():
    response = requests.post('http://data-processing:5004/preprocess')  # replace with the correct URL
    if response.status_code == 200:
        result = response.json()['result']  # get the result from the JSON response
        st.success("Data preprocessing done. Result: " + str(result))
    else:
        st.error("Data preprocessing failed")

# Model training endpoint (triggers model_training.py)
def train_model(learning_rate, num_epochs):
    # Check if the preprocessed data exists
    if not os.path.exists('/data/X_train.csv'):
        st.error('Data is not ready. Please preprocess data first.')
        return

    
    # Make a POST request to the /train route in another Flask app
    response = requests.post('http://model-training:5003/train', 
                             json={'learning_rate': learning_rate, 
                                   'num_epochs': num_epochs})
    # Check if the request was successful
    if response.status_code == 200:
        st.success('Model trained with learning rate {} and {} epochs'.format(learning_rate, num_epochs))
    else:
        st.error('Error: {}'.format(response.content))


def serve_model(features_list):
    # Load the model
    if not os.path.exists('model/model.pth'):
        st.error('Model is not ready. Please train the model first.')

    # Make a POST request to the model serving endpoint
    response = requests.post('http://model-serving:5001/predict', json={'X': features_list})

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the prediction from the response
        prediction = response.json()['prediction']

        # Display the prediction
        st.success(f'Prediction: {prediction}')
    else:
        st.error('Prediction failed.')

# Main function to run the app
def main():
    st.title('California Housing Price application')

    st.subheader('Data Preprocessing')

    if st.button('Preprocess Data', key='preprocess_data'):
        process_data()

    st.subheader('Model Training')

    # Add sliders for learning_rate and num_epochs
    learning_rate = st.slider('Learning Rate', min_value=0.001, max_value=0.1, value=0.01, step=0.001)
    num_epochs = st.slider('Number of Epochs', min_value=1, max_value=10, value=5, step=1)

    if st.button('Train Model', key='train_model'):
        train_model(learning_rate, num_epochs)

    st.subheader('Model Serving')

     # Create input fields for the features
    feature1 = st.number_input('Longitude', value=1.0, step=1.0)
    feature2 = st.number_input('Latitude', value=2.0, step=1.0)
    feature3 = st.number_input('House Median Age', value=3.0, step=1.0)
    feature4 = st.number_input('Total Rooms', value=4.0, step=1.0)
    feature5 = st.number_input('Total Bedrooms', value=5.0, step=1.0)
    feature6 = st.number_input('Population', value=6.0, step=1.0)
    feature7 = st.number_input('Households', value=7.0, step=1.0)
    feature8 = st.number_input('Median Income', value=8.0, step=1.0)
    feature9 = st.number_input('oceam_proximity_<1H OCEAN', value=9.0, step=1.0)
    feature10 = st.number_input('ocean_proximity_INLAND', value=10.0, step=1.0)
    feature11 = st.number_input('oceam_proximity_ISLAND', value=11.0, step=1.0)
    feature12 = st.number_input('oceam_proximity_NEAR BAY', value=12.0, step=1.0)
    feature13 = st.number_input('oceam_proximity_NEAR OCEAN', value=13.0, step=1.0)

    features_list = [feature1, feature2, feature3, feature4, feature5, 
                     feature6, feature7, feature8, feature9, feature10, 
                     feature11, feature12, feature13]

    # Create a button to make predictions
    if st.button('Predict', key='predict'):
        serve_model(features_list)

# Run the app
if __name__ == "__main__":
    main()
```

In this code, you see that the difference with the Flask app is that we use the `st` object from Streamlit to create the web application. We use the same endpoints as in the Flask app to preprocess the data, train the model and predict the price of a house in California.

We can change a bit the page layout by adding a logo in the sidebar and changing the title of the page. So we added a folder `figures` in the root of the project and added the logo of the university in it. We also wanted our page to be a bit Uliège-like so we added in the `./streamlit/config.toml` file the following lines in the `[theme]` section:

```toml
[theme]
# Primary accent for interactive elements
primaryColor = "#F17C3B"
# Background color for the main content area
backgroundColor = "#FFFFFF"
# Background color for sidebar and most interactive widgets
secondaryBackgroundColor = "#8d8a83"

# Font family for all text in the app, except code blocks
# Accepted values (serif | sans serif | monospace) 
# Default: "sans serif"
font = "sans serif"
```

You can also add other configurations like the host and the port of the application in the `./streamlit/config.toml` but we will not use it in this lab.

### 3.2 Docker file

```Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

COPY ./services/web-application/ .
COPY ./model/ ./model
COPY ./data/ ./data
COPY ./figures/ ./figures
COPY ./services/web-application/.streamlit/ ./.streamlit/

RUN pip install -r requirements.txt
```

### 3.3 Requirements file

```txt
flask
pandas
torch
scikit-learn
streamlit
numpy
requests
```

### 3.4 Build and run the application
As wee have seen last week with docker-compose, we can build and run the application. Here is the modified `docker-compose.yml` file:

```yml
version: "3.9"

services:
  data-processing:
    build: 
      context: .  # Build from data-processing directory
      dockerfile: services/data-preprocessing/Dockerfile
    ports:
      - "5004:5004"  # Expose data processing port
    volumes:
      - ./data:/data  # Mount data directory from host (read-write)
    command: gunicorn -b :5004 data_preprocessing:app --access-logfile - --error-logfile -
  model-training:
    build:
      context: .  # Build from model-training directory
      dockerfile: services/model-training/Dockerfile
    ports:
      - "5003:5003"  # Expose model training port
    volumes:
      - ./data:/data  # Mount data directory from host
      - ./model:/model  # Mount output model directory from host (optional)
    command: gunicorn -b :5003 model_training:app --access-logfile - --error-logfile -
  model-serving:
    build:
      context: .  # Build from model-serving directory
      dockerfile: services/model-serving/Dockerfile
    depends_on:
      - model-training  # Wait for model training before starting serving
    ports:
      - "5001:5001"  # Expose model serving port
    command: gunicorn -b :5001 model_serving:app --access-logfile - --error-logfile - 
  web-app:
    build:
      context: .
      dockerfile: services/web-application/Dockerfile # Build from current directory (containing app.py)
    ports:
      - "0.0.0.0:8501:8501"  # Expose Flask app port
    volumes:
      - ./model:/model  # Mount model directory for predictions
      - ./data:/data  # Mount data directory for predictions
    command: streamlit run app.py

volumes:
  data:
  model: 
```

Then run it with the following commands:

```bash
docker build -t streamlit-app .
```

```bash
docker run -p 8501:8501 streamlit-app
```

The Streamlit application should now be running in a Docker container. You can access it by opening a web browser and navigating to `http://localhost:8501`.

### 3.5 Examples of Streamlit applications

You can find more examples of Streamlit applications in the [App galery](https://streamlit.io/gallery). 





