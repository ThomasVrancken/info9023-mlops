import pandas as pd
import numpy as np

from flask import Flask, request, jsonify
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

app = Flask(__name__)

@app.route('/preprocess', methods=['POST'])
def preprocess_data():
    print('Data preprocessing started')
    data_path = '/data/housing.csv'
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

    # Get the column names after one-hot encoding
    column_names = pd.get_dummies(X, columns=['ocean_proximity']).columns
    
    #standardize the data
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Convert the numpy arrays back to pandas DataFrames
    X_train_df = pd.DataFrame(X_train, columns=column_names)
    X_test_df = pd.DataFrame(X_test, columns=column_names)
    y_train_df = pd.DataFrame(y_train, columns=['median_house_value'])
    y_test_df = pd.DataFrame(y_test, columns=['median_house_value'])

    # Save the data as CSV files
    X_train_df.to_csv('/data/X_train.csv', index=False)
    X_test_df.to_csv('/data/X_test.csv', index=False)
    y_train_df.to_csv('/data/y_train.csv', index=False)
    y_test_df.to_csv('/data/y_test.csv', index=False)

    return jsonify({'result': [X_train.shape, X_test.shape, 
                               y_train.shape, y_test.shape]})

if __name__ == "__main__":
    app.run(debug=True)
    


