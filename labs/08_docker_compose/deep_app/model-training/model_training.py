# this code is used to train the model with pytorch

import pickle
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# adding Folder_2 to the system path
sys.path.insert(0, '/deep_app/model/')
from model import Model

# Open the .pkl file for reading in binary mode
with open('data/X_train.pkl', 'rb') as f:
    # Load the object from the file
    X_train = pickle.load(f)

with open('data/y_train.pkl', 'rb') as f:
    y_train = pickle.load(f)

with open('data/X_test.pkl', 'rb') as f:
    X_test = pickle.load(f)

with open('data/y_test.pkl', 'rb') as f:
    y_test = pickle.load(f)


# Convert the data to PyTorch tensors
X_train = torch.tensor(X_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_train = torch.tensor(y_train.values, dtype=torch.float32).view(-1, 1)
y_test = torch.tensor(y_test.values, dtype=torch.float32).view(-1, 1)

# Create a DataLoader for the training data
train_data = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_data, batch_size=32, shuffle=True)

# Create the model
model = Model(X_train.shape[1])

# Define the loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

def train_model(model, train_loader, criterion, optimizer, num_epochs=100):
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
    torch.save(model.state_dict(), 'model/model.pth')
    return model

if __name__ == "__main__":
    train_model(model, train_loader, criterion, optimizer, num_epochs=10)