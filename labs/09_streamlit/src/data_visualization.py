import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import streamlit as st

from sklearn.preprocessing import MinMaxScaler

SERVICE_ACCOUNT_PATH = '{your_svc_path}'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_PATH
# Load the datasets
housing = pd.read_csv('gs://bucket-lab9/housing.csv')
iris = pd.read_csv('gs://bucket-lab9/iris.csv')
stocks = pd.read_csv('gs://bucket-lab9/all_stocks_5yr.csv')
wine = pd.read_csv('gs://bucket-lab9/winequality-red.csv')

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
    sns.histplot(housing['median_house_value'], bins=50, ax=ax, edgecolor='black')
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
    stock_symbol = st.selectbox('Select a stock symbol', stocks['Name'].unique())
    #get a subset of the dataset for the selected stock
    stock_data = stocks[stocks['Name'] == stock_symbol]
    #plot the stock volume and close price over time on the same plot with 2 y-axes
    st.line_chart(stock_data['close'])

    # Scatter plot of stock price vs volume
    st.scatter_chart(stock_data[['close', 'volume']])

elif dataset == 'Iris dataset':
    st.write(iris)
    # Add visualizations for Iris dataset
elif dataset == 'Wine Quality':
    st.write(wine)
    # Add visualizations for Wine Quality dataset