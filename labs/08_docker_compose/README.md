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

- **Image** : The image to use for the service. You can use an existing image from Docker Hub or a custom image built from a Dockerfile. If we want our machine learning pipeline to use a pre-built image from Docker Hub for the data processing service we could write in the `docker-compose.yml` file:

```yaml
version: '3.9'
services:
  data-processing:
    image: name:version
```

*Note:* You see that we used the `image` key to specify the image to use for the service. Not as before where we used the `build` key to specify the path to the Dockerfile.

## 2. Machine learning microservices

We will take the ["California House dataset](https://www.kaggle.com/datasets/shibumohapatra/house-price?resource=download) from Kaggle and create services around it. We will create a machine learning pipeline with 4 services:

- **Data processing service**: This service will read the dataset, preprocess the data, and save the preprocessed data to a file.

- **Model training service**: This service will read the preprocessed data, train a machine learning model, and save the trained model to a file.

- **Model serving service**: This service will read the trained model, expose a REST API to make predictions, and serve the predictions.

- **Web application service**: This service will allow the user to use the other microservices through a web interface. 

The structure of your folder should look like this:

```bash
.
├── data
│   └── housing.csv
├── docker-compose.yml
├── model
│   └── model.py
└── services
    ├── data-preprocessing
    │   ├── Dockerfile
    │   ├── data_preprocessing.py
    │   └── requirements.txt
    ├── model-serving
    │   ├── Dockerfile
    │   ├── model_server.py
    │   └── requirements.txt
    ├── model-training
    │   ├── Dockerfile
    │   ├── model_training.py
    │   └── requirements.txt
    └── web-application
        ├── Dockerfile
        ├── app.py
        ├── requirements.txt
        └── templates
            └── index.html
```

To create this structure, you can type in the terminal.
For the folders:
```bash
mkdir -p deep_app/data deep_app/model deep_app/services/data-preprocessing deep_app/services/model-training deep_app/services/model-serving deep_app/services/web-application deep_app/services/web-application/templates
```
For the files:
```bash
touch deep_app/docker-compose.yml deep_app/model/model.py deep_app/services/data-preprocessing/Dockerfile deep_app/services/data-preprocessing/data_preprocessing.py deep_app/services/data-preprocessing/requirements.txt deep_app/services/model-training/Dockerfile deep_app/services/model-training/model_training.py deep_app/services/model-training/requirements.txt deep_app/services/model-serving/Dockerfile deep_app/services/model-serving/model_serving.py deep_app/services/model-serving/requirements.txt deep_app/services/web-application/Dockerfile deep_app/services/web-application/app.py deep_app/services/web-application/requirements.txt deep_app/services/web-application/templates/index.html
```



### 2.1 Data preprocessing service

In the `services/data-preprocessing` directory we modify the `data_preprocessing.py`. It is there to showcase how to create a service that processes, this is not a guide on how to preprocess data. If you want more information on how to preprocess data in the right way, you can check the [Machine Learning course](https://people.montefiore.uliege.be/lwh/AIA/) given by Prof. Pierre Geurts and Prof. Louis Wehenkel.

#### 2.1.1. Data preprocessing service code

```python
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
```

As we want the differents services to communicate with each other, we need to create Flask API endpoints. In the `data_preprocessing.py` file, we create a `/preprocess` endpoint that triggers the data preprocessing. The data preprocessing service reads the dataset, preprocesses the data, and saves the preprocessed data to files. The data is saved as CSV files in the `data` directory.


#### 2.1.2 Data preprocessing service requirements

We modify the `requirements.txt` file to specify the dependencies for the data processing service.

```txt
flask
gunicorn
numpy
pandas
scikit-learn
```

#### 2.1.3 Data preprocessing service Dockerfile

We create a Dockerfile associated with this service. This will be used to build the image for the data processing service.

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy the data-preprocessing folder which is in the parent directory into the container
COPY ./services/data-preprocessing/ .
COPY ../../data/ ./data

# Install the required libraries
RUN pip install -r requirements.txt
```

In this Dockerfile:
- the `FROM` command to specify the base image for the container. We use the `python:3.9-slim` image as the base image. This image provides a Python environment for running the Flask application.
- the `COPY` command copies the entire `data-preprocessing` folder with the `.` at the end. This copies the `data_preprocessing.py`, `requirements.txt`. 
- The second `COPY` copies the `data` folder from the parent directory into the container because the goal is to read the dataset from the `data` folder and preprocess it, then save the preprocessed data to the `data` folder once again. The `./data` specifies the destination directory in the container. This means that it creates a `data` directory in the container and copies the contents of the `data` directory from the parent directory into the `data` directory in the container.
- the `RUN` command to install the required libraries specified in the `requirements.txt` file.

### 2.2 Model 

In the `model` folder, we will create a `model.py` file that defines a simple machine learning model (here a MLP) using PyTorch. 

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

In the `services/model-training` folder, we will create a very simple `model-training.py` file that exposes a REST API endpoint `/train` that triggers the model training. This service reads the preprocessed data from the `data` directory, trains a machine learning model, and saves the trained model to the `model` directory. The model is saved as a PyTorch state dictionary file (`model.pth`). This file exposes a REST API endpoint `/train` that triggers the model training. The model training service reads the preprocessed data from the `data` directory, trains a machine learning model, and saves the trained model to the `model` directory. The model is saved as a PyTorch state dictionary file (`model.pth`).

Once again, this is a simple example of model training. The aim is to show how to create a service that trains a model, not how to train a model in the best way. See the [Machine Learning course](https://people.montefiore.uliege.be/lwh/AIA/) given by Prof. Pierre Geurts and Prof. Louis Wehenkel or the course of [Deep learning](https://github.com/glouppe/info8010-deep-learning) given by Prof. Gilles Louppe for more information on how to effectively train a model.

#### 2.3.1 Model training service code

```python
import pandas as pd
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
    learning_rate = request.json.get('learning_rate')
    num_epochs = request.json.get('num_epochs')   
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
    torch.save(model.state_dict(), '/model/model.pth')
    return jsonify({'result': 'Model trained'})

if __name__ == "__main__":
    app.run(debug=True)
```

#### 2.3.2 Model training service requirements

We create a `requirements.txt` file to specify the dependencies for the model training service.

```txt
flask
gunicorn
pandas
torch
```

#### 2.3.3 Model training service Dockerfile

We now create a Dockerfile associated with this service. This will be used to build the image for the model training service.

```Dockerfile
FROM pytorch/pytorch:latest

WORKDIR /app

COPY ./services/model-training/ .
COPY ../../model/ ./model
COPY ../../data/ ./data

RUN pip install -r requirements.txt
```

In this Dockerfile:
- the `FROM` command to specify the base image for the container. We use the `pytorch/pytorch:latest` which provides a PyTorch environment for running the model training service.
- the `COPY` command copies the entire `model-training` folder with the `.` at the end. This copies the `model_training.py`, `requirements.txt`.
- the second and third `COPY` copy the `model` and `data` folders from the parent directory into the container. The `./model` and `./data` specify the destination directories in the container. This means that it creates a `model` and `data` directories in the container and copies the contents of the `model` and `data` directories from the parent directory into the `model` and `data` directories in the container. 
- the `RUN` command to install the required libraries specified in the `requirements.txt` file.

### 2.4 Model serving service

In the `model-serving` directory, we modify the `model_serving.py` file. This service reads the trained model from the `model` directory, exposes a REST API endpoint `/predict` that makes predictions, and serves the predictions. 

#### 2.4.1 Model serving service code

```python
import torch
from flask import Flask, request, jsonify

from model.model import Model

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    # Load the trained model
    model = Model(13)
    model.load_state_dict(torch.load('./model/model.pth'))
    model.eval()
    data = request.get_json(force=True)
    X = torch.tensor(data['X'], dtype=torch.float32)
    with torch.no_grad():
        output = model(X)
    print('Prediction:', output.item())
    return jsonify({'prediction': output.item()})

if __name__ == '__main__':
    app.run(debug=True)
```

#### 2.4.2 Model serving service requirements

We modify the `requirements.txt` file to specify the dependencies for the model serving service.

```txt
flask
gunicorn
numpy
torch
```

#### 2.4.3 Model serving service Dockerfile

We now modify the Dockerfile associated with this service. This will be used to build the image for the model serving service.

```Dockerfile
FROM nvidia/cuda:12.3.2-devel-ubi8
FROM python:3.9-slim

WORKDIR /app

COPY ./services/model-serving/ .
COPY ../../model/ ./model

RUN pip install -r requirements.txt
```

In this Dockerfile : 
- the `FROM` command to specify the base image for the container. We use the `nvidia/cuda:12.3.2-devel-ubi8` image as the base image. This image provides a CUDA-enabled environment for running PyTorch with GPU support. 
- the `FROM` command is again used to specify the base image for the container. We use the `python:3.9-slim` to provide a Python environment for running the Flask application.
- the `WORKDIR` command sets the active directory in the container to `/app`. 
- the `COPY` command to copies the entire `model-serving` folder with the `.` at the end. This copies the `model_serving.py`, `requirements.txt`. 
- the second `COPY` copies the `model` folder from the parent directory into the container. The `./model` specifies the destination directory in the container. This means that it creates a `model` directory in the container and copies the contents of the `model` directory from the parent directory into the `model` directory in the container. 
- the `RUN` command to install the required libraries specified in the `requirements.txt` file.

### 2.5 Web application service

In the `services/web-application` directory, we will create a `app.py` file. The web application service will allow the user to use the other microservices through a web interface. The user can trigger the data processing, model training, and model serving services through the web interface and the different endpoints.

The web application will have a home page with buttons to trigger the data processing and model training services. It will also have a form to input data and make predictions using the model serving service.

#### 2.5.1 Web application service code

```python
import os
import requests

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Load the model
model = Model(13)  # replace with the number of input features
model.load_state_dict(torch.load('./model/model.pth'))
model.eval()

#Data preprocessing endpoint (triggeres preprocessing.py)
@app.route('/preprocess_data', methods=['POST'])
def process_data():
    response = requests.post('http://data-processing:5004/preprocess')  # replace with the correct URL
    if response.status_code == 200:
        result = response.json()['result']  # get the result from the JSON response
        return "Data preprocessing done. Result: " + str(result)
    else:
        return "Data preprocessing failed", 500

#Model training endpoint (triggeres model_training.py)
@app.route('/train_model', methods=['POST'])
def train_model():
    # Check if the preprocessed data exists
    if not os.path.exists('/data/X_train.csv'):
        return jsonify({'error': 
                        'Data is not ready. Please preprocess data first.'}
                        ), 400
    #get learning rate provided by the user. Default to 0.001 if not provided
    learning_rate = request.form.get('learning_rate')
    learning_rate = float(learning_rate) if learning_rate else 0.001
    #get number of epochs provided by the user. Default to 10 if not provided
    num_epochs = request.form.get('num_epochs')
    num_epochs = int(num_epochs) if num_epochs else 10

    # Make a POST request to the /train route in model_training.py 
    #       with the learning rate and number of epochs
    response = requests.post('http://model-training:5003/train', 
                             json={'learning_rate': learning_rate, 
                                   'num_epochs': num_epochs})

    # Check if the request was successful
    if response.status_code == 200:
        return 'Model trained with learning rate {} and {} \
            epochs'.format(learning_rate, num_epochs)
    else:
        return 'Error: {}'.format(response.content), response.status_code

@app.route('/predict', methods=['POST'])
def predict():
    # Check if the model exists
    if not os.path.exists('/model/model.pth'):
        return jsonify({'error': 
                        'Model is not ready. Please train the model first.'}
                        ),400
    
    # Get the data from the POST request.
    data = request.get_json(force=True)
    # Make a POST request to the /predict route in another Flask app
    response = requests.post('http://model-serving:5001/predict', json=data)

    # Check if the request was successful
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return 'Error: {}'.format(response.content), response.status_code

# Home page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

#### 2.5.2 Web application using Jinja2 templates

Until now we didn't really used Jinja2 templates. You can see in the file above that we use `render_template('index.html')` in the home route. This is a way to render HTML templates in Flask. Jinja2 is a templating engine for Python, which allows you to embed Python code in HTML templates. We therefore modify the `index.html` file in the `services/web-application/templates` directory. This file will contain the HTML code for the home page of the web application. The home page will have buttons to trigger the data processing and model training services, and a form to input data and make predictions using the model serving service.

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f0f0f0;
        }
        .container {
            text-align: center;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        button {
            margin: 10px;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #007BFF;
            color: #fff;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        label, input {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Machine Learning Pipeline</h1>
        <form action="/preprocess_data" method="post">
            <button type="submit">Process Data</button><br>
        </form>
        <form action="/train_model" method="post">
            <label for="learning_rate">Learning Rate:</label><br>
            <input type="text" id="learning_rate" name="learning_rate"><br>
            <label for="num_epochs">Number of Epochs:</label><br>
            <input type="text" id="num_epochs" name="num_epochs"><br>
            <button type="submit">Train Model</button>
        </form>
        <h2>Make a prediction</h2>

        <form id="predictionForm">
          <label for="inputData1">Feature 1:</label><br>
          <input type="text" id="inputData1" name="inputData1"><br>
          <!-- Repeat the above two lines for inputData2 through inputData13 -->
          <label for="inputData2">Feature 2:</label><br>
          <input type="text" id="inputData2" name="inputData2"><br>
          <label for="inputData3">Feature 3:</label><br>
          <input type="text" id="inputData3" name="inputData3"><br>
          <label for="inputData4">Feature 4:</label><br>
          <input type="text" id="inputData4" name="inputData4"><br>
          <label for="inputData5">Feature 5:</label><br>
          <input type="text" id="inputData5" name="inputData5"><br>
          <label for="inputData6">Feature 6:</label><br>
          <input type="text" id="inputData6" name="inputData6"><br>
          <label for="inputData7">Feature 7:</label><br>
          <input type="text" id="inputData7" name="inputData7"><br>
          <label for="inputData8">Feature 8:</label><br>
          <input type="text" id="inputData8" name="inputData8"><br>
          <label for="inputData9">Feature 9:</label><br>
          <input type="text" id="inputData9" name="inputData9"><br>
          <label for="inputData10">Feature 10:</label><br>
          <input type="text" id="inputData10" name="inputData10"><br>
          <label for="inputData11">Feature 11:</label><br>
          <input type="text" id="inputData11" name="inputData11"><br>
          <label for="inputData12">Feature 12:</label><br>
          <input type="text" id="inputData12" name="inputData12"><br>
          <label for="inputData13">Feature 13:</label><br>
          <input type="text" id="inputData13" name="inputData13"><br>
          <input type="submit" value="Predict">
      </form>
    </div>

    <script>
    document.getElementById('predictionForm').addEventListener('submit', async function(event) {
        event.preventDefault();

        let inputData = [];
        for (let i = 1; i <= 13; i++) {
            inputData.push(parseFloat(document.getElementById('inputData' + i).value));
        }

        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({X: inputData}) // Changed 'input' to 'X'
        });
        const prediction = await response.json();
        alert('Prediction: ' + JSON.stringify(prediction)); // Use JSON.stringify to convert prediction object to string
    });
    </script>
</body>
</html>
```

#### 2.5.3 Web application service requirements


```txt
gunicorn
flask
pandas
torch
scikit-learn
numpy
requests
```

#### 2.5.4 Web application service Dockerfile

The Dockerfile associated with this service is the following: 

```Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

COPY ./services/web-application/ .
COPY ../../model/ ./model
COPY ../../data/ ./data

RUN pip install -r requirements.txt
```

In this Dockerfile:
- the `FROM` command to specify the base image for the container. We use the `python:3.9-slim` image as the base image. This image provides a Python environment for running the Flask application.
- the `COPY` command copies the entire `web-application` folder with the `.` at the end. This copies the `app.py`, `requirements.txt`, and the `templates` directory.
- the second and third `COPY` copy the `model` and `data` folders from the parent directory into the container. The `./model` and `./data` specify the destination directories in the container. This means that it creates a `model` and `data` directories in the container and copies the contents of the `model` and `data` directories from the parent directory into the `model` and `data` directories in the container.
- the `RUN` command to install the required libraries specified in the `requirements.txt` file.

### 2.6 Docker Compose file

We will now write the `docker-compose.yml` file to define the services of our machine learning application. The `docker-compose.yml` file will define the following services:

- **data-processing**: The data processing service that reads the dataset, preprocesses the data, and saves the preprocessed data to a file.

- **model-training**: The model training service that reads the preprocessed data, trains a machine learning model, and saves the trained model to a file.

- **model-serving**: The model serving service that reads the trained model, exposes a REST API to make predictions, and serves the predictions.

- **web-application**: The web application service that allows the user to use the other microservices through a web interface.

```yaml
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
      - "5002:5002"  # Expose Flask app port
    volumes:
      - ./model:/model  # Mount model directory for predictions
      - ./data:/data  # Mount data directory for predictions
    command: gunicorn -b :5002 app:app --access-logfile - --error-logfile -

volumes:
  data:
  model:
```

In this `docker-compose.yml` file:
- the `version` key specifies the version of the Docker Compose file format.
- the `services` key defines the services for the machine learning application.
  - the `data-processing`, `model-training`, `model-serving`, and `web-application` services are defined in the file.
  - the `build` key specifies the build context for each service. 
      - The `context` key specifies the directory that Docker will use to build context. We use `.` to specify the current directory as the build context. We need that because for example the `data-preprocessing` service needs to access the `data` directory which is in the parent directory. So we could not use the `services/data-preprocessing` directory as the build context otherwise the `data` directory would not be accessible.
      - The `dockerfile` key specifies the path to the Dockerfile for the service.
  - the `ports` key specifies the ports to expose for each service. The format is `host_port:container_port`. For example, the `data-processing` service is exposed on port 5004 on the host machine and port 5004 in the container.
  - the `volumes` key specifies the volumes to mount for each service. The format is `host_path:container_path`. For example, the `data-processing` service mounts the `data` directory from the host machine to the `/data` directory in the container.
  - the `command` key specifies the command to run when the container starts. We use `gunicorn` to run the Flask application in each service. The `--access-logfile -` and `--error-logfile -` options are used to log the access and error logs to the console.
  - the `depends_on` key specifies the dependencies between services. The `model-serving` service depends on the `model-training` service. This means that in our case, the `model-serving` service will wait for the `model-training` service to be up and running before starting.

### 2.7 Running all services with Docker Compose

Now that we created everything we can run the services with Docker Compose. In the `deep_app` directory, run the following command:

```bash
docker-compose up
```

This command will search for the `docker-compose.yml` file in the current directory, create the images for the services defined in the file, and run the containers.

Once the services are up and running, you can access the web application at `http://localhost:5002`. You can trigger the data processing and model training services through the web interface. You can also input data and make predictions using the model serving service.

Once you are done, you can stop the services with the following command:

```bash
docker-compose down
```
If you don't use this command, the containers will still be in use and keep running in the background even if you close the terminal. This is a problem because it takes up resources on your machine. So this command will stop the containers created from the `docker-compose up` command and remove the containers defined in the `docker-compose.yml` file. What we mean by remove is that the containers are stopped and removed. The images are not removed. If you want to remove the images you can use the `docker rmi` command.





