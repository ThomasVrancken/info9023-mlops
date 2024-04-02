# Lab W08: Docker Compose

## 0. Description

Until now, we only used single containers to run our applications. However, in real-world scenarios, applications are often composed of multiple containers. For example, a web application might consist of a web server, a database, and a cache. A machine learning pipeline might consist of a data processing container, a model training container, and a model serving container.

Manually managing multiple containers can be cumbersome. Docker Compose is a tool that allows you to define and run multi-container applications with a single configuration file and a single command to start the application services.

In this lab, you will learn how to use Docker Compose to manage multi-container applications. You will define a multi-container application using a `docker-compose.yml` file and run the application using `docker-compose up`.

### 0.1 What is docker compose?

Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application's services. Then, with a single command, you create and start all the services from your configuration.

### 0.2 Why use docker compose?

- **Single configuration file**: Docker Compose allows you to define your application's services in a single configuration file. This makes it easy to manage and deploy multi-container applications.

- **Automated setup**: With Docker Compose, you can automate the setup of multi-container applications. This makes it easy to deploy your application on different environments.

- **Dependency management**: Docker Compose allows you to define dependencies between your application's services. This ensures that services are started in the correct order.

### 0.3 How does docker compose work?

Docker Compose uses a YAML file called `docker-compose.yml` to define your application's services. Each service is defined as a separate section in the file. You can specify the image to be used or custom Dockerfiles to build the image, ports to expose, volumes to mount, environment variables, and other settings for each service.

When you run `docker-compose up`, Docker Compose reads the `docker-compose.yml` file and creates the services defined in the file. It then starts the services in the correct order, based on their dependencies.

## 1. Prerequisites

Before you start this lab, you should:

- Be familiar with Docker containers and images.
- Have Docker installed on your machine (Docker Compose is included with Docker Desktop for Windows and macOS).
- Have a basic understanding of Docker Compose.


### 1.1 Getting Started

We will create a file named `app.py`. This file contains a simple Flask API that we have seen many times before in the previous labs.

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

We create the `requirements.txt` file to specify the dependencies for the Flask application.

```txt
Flask
```

Now we will create the `Dockerfile` for this application.

```Dockerfile
# Use the official Python image as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /src

# Copy the current directory contents into the container at /app
COPY  src/ .

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Define environment variable to tell the container where the app is (i.e. the file to run)
ENV FLASK_APP=app.py

# Run app.py when the container launches

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
```


Now we will build the Docker image for this application.

```bash
docker build -t flask-app .
```

Now we will run the Docker container for this application.

```bash
docker run -p 5001:5001 flask-app
```

### 1.2 Docker compose file structure

We will now write a `docker-compose.yml` file so that we can run the Flask application using Docker Compose.

```yaml
version: '3.9'
services:
  flask-app:
    build: .
    container_name: flask-app
    ports:
      - "5001:5001"
```

Now we can run the Flask application using Docker Compose.

```bash
docker-compose up
```

This command will search for the `docker-compose.yml` file in the current directory, create the imagages written in the services section, and run the containers. So if you go to `http://localhost:5001` you will see the Flask application running.

So now with only one command, we can build an image and run the container. Everything is defined in the `docker-compose.yml` file even the ports to expose.

```bash
docker-compose down
```

This command will stop the container created from the command `docker-compose up` and remove the container

 and remove the containers defined in the `docker-compose.yml` file.

## 1.3. Services 

In the `docker-compose.yml` file, you can define multiple services for your application. Each service is defined as a separate section in the file. You can specify the image to be used or custom Dockerfiles to build the image, ports to expose, volumes to mount, environment variables, and other settings for each service.

- **Service** : A service is a container that runs a specific application or process. For example, in a machine learning pipeline, you might have a data processing service, a model training service, and a model serving service.

- **Build** : The build configuration allows you to build a custom image for the service using a Dockerfile. You can specify the path to the Dockerfile and the context for the build. Here the `Dockerfile` and the `docker-compose.yml` file are in the same directory, so we use `.` for the build path.

- **Image** : The image to use for the service. You can use an existing image from Docker Hub or a custom image built from a Dockerfile. If we our machine learning pipeline to use a pre-built image from Docker Hub for the data processing service we could write in the `docker-compose.yml` file:

```yaml
version: '3.9'
services:
  data-processing:
    image: name:version
```

*Note:* You see that we used the `image` key to specify the image to use for the service. Not as before where we used the `build` key to specify the path to the Dockerfile.

## 2. Machine learning pipeline

We will take the ["California House dataset](https://www.kaggle.com/datasets/shibumohapatra/house-price?resource=download) from Kaggle and create a model to output the price of a house based on the features of this house. 

For this we will create a machine learning pipeline with 4 services:

- **Data processing service**: This service will read the dataset, preprocess the data, and save the preprocessed data to a file.

- **Model training service**: This service will read the preprocessed data, train a machine learning model, and save the trained model to a file.

- **Model serving service**: This service will read the trained model, expose a REST API to make predictions, and serve the predictions.

- **Web application service**: This service will allow the user to use the other microservices through a web interface. 

### 2.1 Data preprocessing service

In the `data-preprocessing` directory we create a `data_preprocessing.py` file that reads the dataset, preprocesses the data, and saves the preprocessed data to a file. This is a simple example of data preprocessing, where we drop rows with missing values, split the data into training and test sets, standardize the data, and save the preprocessed data to files. It is there to showcase how to create a service that processes data not how to preprocess data.

```python
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
```

We create a `requirements.txt` file to specify the dependencies for the data processing service.

```txt
numpy
pandas
scikit-learn
```

We now create a Dockerfile associated with this service. This will be used to build the image for the data processing service.

```Dockerfile
FROM python:3.9-slim

WORKDIR /deep_app

COPY . .

RUN pip install -r /deep_app/data-preprocessing/requirements.txt

#To test the the data_preprocessing.py service alone decoment the CMD below and uncomment the CMD below
#CMD ["python", "data-preprocessing/data_preprocessing.py"]
```

#### 2.1.1 Building the data processing service (OPTIONAL)

To test if we didn't make any mistakes in the Dockerfile, don't forget to uncomment the `CMD` line in the Dockerfile, then we can build the image for the data processing service alone. In the `deep_app` directory, run the following command:

```bash
docker build -f data_preprocessing/Dockerfile -t data-preprocessing .
```

**Reminder**: The `-f data_preprocessing/Dockerfile` option specifies the path to the Dockerfile to use for building the image. The `-t data-processing` option specifies the name of the image to build.

```bash
docker run data-preprocessing
```

### 2.2 Model 

In the model folder, we will create a `model.py` file that defines a very simple neural network model using PyTorch.

```python
import torch
import torch.nn as nn

class Model(nn.Module):
    def __init__(self, input_dim):
        super(Model, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x
```

### 2.3 Model training service

In the `model-training folder`, we will create a very simple `model-training.py` file that reads the preprocessed data, trains a machine learning model, and saves the trained model to a file. Once again, this is a simple example of model training. The aim is to show how to create a service that trains a model, not how to train a model. See the [Machine Learning course](https://people.montefiore.uliege.be/lwh/AIA/) given by Prof. Pierre Geurts and Prof. Louis Wehenkel or the course of [Deep learning](https://github.com/glouppe/info8010-deep-learning) given by Prof. Gilles Louppe for more information on how to effectively train a model.

```python
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
```

We create a `requirements.txt` file to specify the dependencies for the model training service.

```txt
torch
pandas
```

We now create a Dockerfile associated with this service. This will be used to build the image for the model training service.

```Dockerfile
FROM pytorch/pytorch:latest

WORKDIR /deep_app

COPY . .

RUN pip install -r deep_app/model-training/requirements.txt

#CMD ["python", "model-training/model_training.py"]
```

#### 2.3.1 Building the model training service (OPTIONAL)

To test if we didn't make any mistakes in the Dockerfile, don't forget to uncomment the `CMD` line in the Dockerfile, then we can build the image for the model training service alone. In the `deep_app` directory, run the following commands:

```bash
docker build -f model-training/Dockerfile -t model-training .
```

```bash
docker run model-training
```

### 2.4 Model serving service

In the `model-serving` directory, we will create a `model_serving.py` file that reads the trained model, exposes a REST API to make predictions, and serves the predictions. 

```python
import sys
import torch
import torch.nn as nn
from flask import Flask, request, jsonify

# adding Folder_2 to the system path
sys.path.insert(0, '/deep_app/model/')
from model import Model

app = Flask(__name__)

# Load the trained model
model = Model(input_dim=13)
model.load_state_dict(torch.load('model/model.pth'))
model.eval()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    X = torch.tensor(data['X'], dtype=torch.float32)
    with torch.no_grad():
        output = model(X)
    return jsonify({'prediction': output.item()})

if __name__ == '__main__':
    app.run(host='0.0 .0.0', port=5001)
```

We create a `requirements.txt` file to specify the dependencies for the model serving service.

```txt
torch
flask
gunicorn
```

We now create a Dockerfile associated with this service. This will be used to build the image for the model serving service.

```Dockerfile
FROM nvidia/cuda:12.3.2-devel-ubi8
FROM python:3.9-slim

WORKDIR /deep_app

COPY . .

RUN pip install -r docker/model_serving/requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "model_server:app"]
```

### 2.5 Web application service

In the `web-application` directory, we will create a `app.py` file that allows the user to use the other microservices through a web interface. 

```python
import torch

from flask import Flask, request, jsonify, render_template
from subprocess import run

# adding Folder_2 to the system path
sys.path.insert(0, '/deep_app/model/')
from model import Model

app = Flask(__name__)

# Load the model
model = Model(13)  # replace with the number of input features
model.load_state_dict(torch.load('model/model.pth'))
model.eval()

#Data preprocessing endpoint (triggeres preprocessing.py)
@app.route('/preprocess_data', methods=['POST'])
def process_data():
    run(['python', 'data_preprocessing.py'])
    return "Data preprocessing done"

#Model training endpoint (triggeres model_training.py)
@app.route('/train_model', methods=['POST'])
def train_model():
    run(['python', 'model_training.py'])
    return "Model trained"

@app.route('/predict', methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force=True)

    # Make prediction using model loaded from disk as per the data.
    prediction = model(torch.tensor(data['input']))

    # Take the first value of prediction
    output = prediction.item()

    return jsonify(output)

# Home page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
```

We create the `index.html` file in the `web-application\templates` directory. This file contains the HTML code for the home page of the web application.

```html
<!DOCTYPE html>
<html>
<body>
  <h1>Machine Learning Pipeline</h1>
  <form action="/preprocess_data" method="post">
    <button type="submit">Process Data</button>
  </form>
  <form action="/train_model" method="post">
    <button type="submit">Train Model</button>
  </form>
  <h2>Make a prediction</h2>

<form id="predictionForm">
    <label for="inputData">Input data:</label><br>
    <input type="text" id="inputData" name="inputData"><br>
    <input type="submit" value="Predict">
</form>

<script>
document.getElementById('predictionForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const inputData = document.getElementById('inputData').value.split(',').map(Number);

    const response = await fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({input: inputData})
    });
    const prediction = await response.json();
    alert('Prediction: ' + prediction);
});
</script>
</body>
</html>
```

We create a `requirements.txt` file to specify the dependencies for the web application service.

```txt
gunicorn
flask
pandas
torch
scikit-learn
numpy
```

We now create a Dockerfile associated with this service. This will be used to build the image for the web application service.

```Dockerfile
# Base image for Python environment (adjust based on your requirements)
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your Flask application code
COPY . .

# Expose the port where the Flask app runs (usually 5000)
EXPOSE 5002

# Run the Flask app using Gunicorn (production server)
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]
```

### 2.6 Docker Compose file

We will now write a `docker-compose.yml` file to define the services for the machine learning pipeline. The `docker-compose.yml` file will define the following services:

- **data-processing**: The data processing service that reads the dataset, preprocesses the data, and saves the preprocessed data to a file.

- **model-training**: The model training service that reads the preprocessed data, trains a machine learning model, and saves the trained model to a file.

- **model-serving**: The model serving service that reads the trained model, exposes a REST API to make predictions, and serves the predictions.

- **web-application**: The web application service that allows the user to use the other microservices through a web interface.

```yaml
version: '3.9'

version: "3.9"

services:
  data-processing:
    build: 
      context: .
      dockerfile: docker/data_preprocessing/Dockerfile
    volumes:
      - ./data:/app/data  # Mount data directory from host
  model-training:
    build:
      context: .
      dockerfile: docker/model_training/Dockerfile
    volumes:
      - ./data:/app/data  # Mount data directory from host
      - ./model:/app/model  # Mount output model directory from host (optional)
  model-serving:
    build:
      context: .
      dockerfile: docker/model_serving/Dockerfile
    depends_on:
      - model-training  # Wait for model training before starting serving
    ports:
      - "5001:5001"  # Expose model serving port
  app:
    build: .  # Build from current directory (containing app.py)
    ports:
      - "5002:5002"  # Expose Flask app port
    volumes:
      - ./model:/app/model  # Mount model directory for predictions
      - .:/app  # Mount current directory for code access

volumes:
  # Define a named volume to share the model directory between services
  model: {}
```

### 2.7 Running the machine learning pipeline

Now we can run the machine learning pipeline using Docker Compose. In the `deep_app` directory, run the following command:

```bash
docker-compose up
```

This command will search for the `docker-compose.yml` file in the current directory, create the images for the services defined in the file, and run the containers. The `data-processing` service will read the dataset, preprocess the data, and save the preprocessed data to a file. The `model-training` service will read the preprocessed data, train a machine learning model, and save the trained model to a file. The `model-serving` service will read the trained model, expose a REST API to make predictions, and serve the predictions. The `web-application` service will allow the user to use the other microservices through a web interface.











### Predictions
1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0
