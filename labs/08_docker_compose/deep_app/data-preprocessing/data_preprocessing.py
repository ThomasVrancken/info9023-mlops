# This file is used to preprocess the data before training the model

import pandas as pd
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def preprocess_data(data_path):
    #read the data
    data = pd.read_csv(data_path)
    #drop the rows with missing values
    data = data.dropna()
    #drop the target column
    X = data.drop('median_house_value', axis=1)
    y = data['median_house_value']
    #split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    #standardize the data
    scaler = StandardScaler()
    #change 'ocean_proximity' column with scikit-learn's one-hot encoder
    X_train = pd.get_dummies(X_train, columns=['ocean_proximity'])
    X_test = pd.get_dummies(X_test, columns=['ocean_proximity'])
    #standardize the data
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = preprocess_data('data/housing.csv')
    print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
    # save as pkl files
    with open('data/X_train.pkl', 'wb') as f:
        pickle.dump(X_train, f)
    with open('data/X_test.pkl', 'wb') as f:
        pickle.dump(X_test, f)
    with open('data/y_train.pkl', 'wb') as f:
        pickle.dump(y_train, f)
    with open('data/y_test.pkl', 'wb') as f:
        pickle.dump(y_test, f)


