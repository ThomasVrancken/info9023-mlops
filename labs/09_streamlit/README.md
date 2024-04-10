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


## 1. Put the different datasets in a Google Cloud Storage bucket

First, you need to put the different datasets in a Google Cloud Storage bucket. You can use the code we saw in the previous lab to upload the datasets to a bucket:

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

## 2. Create a Streamlit application to visualize the datasets

Create a Streamlit application that allows data visualization of the datasets. The application should have the following features:

- A sidebar that allows the user to select the dataset to visualize.
- A main panel that displays the selected dataset.
- The main panel should display multiple types of visualizations such as histograms, scatter plots, line plots, geographic maps, and more.
- The user should be able to interact with the visualizations (e.g., zoom in, zoom out, pan, etc.).

### 2.1. Visualizations

Here are some examples of visualizations you can create for each dataset:

- California House Price:
    - Histogram of house prices.
    - Scatter plot of house prices vs. square footage.
    - Geographic map of houses with a point size proportional to the house price.

- S&P 500 stock data:
    - Line plot of stock prices over time.
    - Scatter plot of stock prices vs. trading volume.

- Iris dataset:
    - Scatter plot of sepal length vs. sepal width.
    - Scatter plot of petal length vs. petal width.
    - Histogram of sepal length.
    - Histogram of petal length.

- Wine Quality:
    - Histogram of wine quality.
    - Scatter plot of wine quality vs. alcohol content.
    - Scatter plot of wine quality vs. pH.
    - Line plot of wine quality over time.

### 2.2. Example code

Here is an example of how you can create a Streamlit application that allows the user to select a dataset and visualize it.

```python
import streamlit as st
import pandas as pd

# Load the datasets
housing = pd.read_csv('gs://mlsd-bucket/housing.csv')
iris = pd.read_csv('gs://mlsd-bucket/iris.csv')
stocks = pd.read_csv('gs://mlsd-bucket/all_stocks_5yr.csv')
wine = pd.read_csv('gs://mlsd-bucket/winequality-red.csv')

# Sidebar
dataset = st.sidebar.selectbox('Select dataset', ['California House Price', 'S&P 500 stock data', 'Iris dataset', 'Wine Quality'])

# Main panel
if dataset == 'California House Price':
    st.write(housing)
    # Add visualizations for California House Price dataset
    # Histogram of house prices
    st.write(housing['price'].hist())
    # Scatter plot of house prices vs. square footage
    st.write(housing.plot.scatter(x='sqft', y='price'))
    # Line plot of house prices over time
    st.write(housing.plot.line(x='date', y='price'))
    # Geographic map of house prices by location
    st.map(housing)
elif dataset == 'S&P 500 stock data':
    st.write(stocks)
    # Add visualizations for S&P 500 stock data dataset
    # Add box to select a stock and display its price over time
    stock = st.selectbox('Select stock', stocks['Name'].unique())
    st.line_chart(stocks[stocks['Name'] == stock], x='date', y='close')
    # Add scatter plot of `highest` - `lowest` vs. `trading volume``
    st.write(stocks.plot.scatter(x='volume', y='high' - 'low'))
    

elif dataset == 'Iris dataset':
    st.write(iris)
    # Add visualizations for Iris dataset
elif dataset == 'Wine Quality':
    st.write(wine)
    # Add visualizations for Wine Quality dataset
``` 


## 3. Create a Streamlit application to predict the price of a house in California

Create a Streamlit application that allows the user to input the features of a house and predicts the price of the house using a simple linear regression model. The application should have the following features:

- A sidebar that allows the user to input the features of the house (e.g., number of bedrooms, number of bathrooms, square footage, etc.).

- A main panel that displays the predicted price of the house.

- The user should be able to interact with the application (e.g., input the features of the house, view the predicted price, etc.).


[App galery](https://streamlit.io/gallery)





