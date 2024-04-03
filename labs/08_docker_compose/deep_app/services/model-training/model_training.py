# this code is used to train the model with pytorch

import pandas as pd
import sys
import torch
import torch.nn as nn
import torch.optim as optim

from flask import Flask, request, jsonify
from torch.utils.data import DataLoader, TensorDataset


from model.model import Model

app = Flask(__name__)

@app.route('/train', methods=['POST'])
def train_model():
    # Get the learning rate and number of epochs from the request data
    learning_rate = request.json.get('learning_rate', 0.001)  # Default to 0.001 if not provided
    num_epochs = request.json.get('num_epochs', 10)  # Default to 10 if not provided    
    # Open the .csv files
    X_train = pd.read_csv('/data/X_train.csv')
    X_test = pd.read_csv('/data/X_test.csv')
    y_train = pd.read_csv('/data/y_train.csv')
    y_test = pd.read_csv('/data/y_test.csv')


    # Convert the dataframe to PyTorch tensors
    X_train = torch.tensor(X_train.values, dtype=torch.float32)
    X_test = torch.tensor(X_test.values, dtype=torch.float32)
    y_train = torch.tensor(y_train.values, dtype=torch.float32).view(-1, 1)
    y_test = torch.tensor(y_test.values, dtype=torch.float32).view(-1, 1)

    # Create a DataLoader for the training data
    train_data = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_data, batch_size=32, shuffle=True)

    # Create the model
    model = Model(X_train.shape[1])

    # Define the loss function and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), learning_rate)

    # Train the model
    for epoch in range(num_epochs):
        for i, (inputs, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        print(f'Epoch {epoch+1}, Loss: {loss.item()}')

    # Save the trained model
    torch.save(model.state_dict(), './model/model.pth')
    return jsonify({'result': 'Model trained'})

if __name__ == "__main__":
    app.run(debug=True)