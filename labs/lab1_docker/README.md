# Lab 1 [Sprint 2, W4] : Docker

## 0. Introduction

This lab will introduce you to Docker. You will get hands-on experience in containerizing a simple Python application in class, then you will need to apply these concepts by building a container for a basic machine learning model.

## 1. Understanding virtual environments, virtual machines and containers

### 1.1. Virtual environment

A virtual environment is a self-contained directory that contains a Python installation for a particular version of Python, plus a number of additional packages. It allows you to work on a specific project without worrying about the dependencies of other projects.

You can maintain dependencies of your project in a `requirements.txt` file and install them using `pip install -r requirements.txt`.

Pros: 
- Reproducibility: you can share your `requirements.txt` file with others to ensure they have the same dependencies.
- Dependency management: forces you to specify the dependencies of your project in a `requirements.txt` file.

Cons:
- Effort to maintain: you need to update the `requirements.txt` file when you add or remove dependencies.
- Storage space: each virtual environment takes up space on your hard drive and you may have duplicate dependencies across different virtual environments.
- Compatibility between OS: the dependencies in your `requirements.txt` file may not work on different operating systems.

### 1.2. Virtual machine (VM)

A virtual machine emulates a physical computer. It allows you to run multiple operating systems on a single physical machine. Each virtual machine has its own virtual hardware, including CPU, memory, storage, and network interfaces. You can install an operating system on a virtual machine and run software on it as if it were a physical computer.

Pros:
- Isolation: software running on a virtual machine is isolated from the host operating system.
- Compatibility: you can run software that requires a different operating system than the one you are currently using.
- Sharing: you can share a virtual machine image with others to ensure they have the same environment.

Cons:
- Resource intensive: each virtual machine requires its own CPU, memory, storage, and network interfaces so in general you can only run a few virtual machines on a single physical machine.
- Storage space: each virtual machine takes up space on your hard drive.
- Slow to start: starting a virtual machine can take several minutes.

### 1.3. Container

A container is a lightweight, standalone, executable package of software that includes everything needed to run an application: code, runtime, system tools, system libraries, and settings.

The difference with a VM is that Docker does not embed a full operating system. Instead, on Linux, it uses the host operating system's kernel and on Windows and macOS, it uses a lightweight virtual machine to run Linux. This ensures that a containerized application always runs in the same environment, regardless of the host operating system.

Pros:
- Portability: you can run a container on any machine that has Docker installed.
- Speed: containers start in seconds, fast to modify and iterates on.
- Efficiency: containers share the host operating system's kernel so they are lightweight and use less resources than a virtual machine.
- Modularity: you can build a container for each component of your application and run them together.
- Isolation: containers are isolated from each other. So if one container crashes, it does not affect other containers.
- Ease of management: you can manage containers using the Docker CLI or a container orchestration tool like Kubernetes.

Cons:
- Security: containers share the host operating system's kernel so if an attacker gains access to the kernel, they can access all containers running on the host.
- Complexity: containers are more complex to set up than virtual environments.


## 2. Getting started with Docker

### 2.1. Prerequisites
1. Have a working version of [python](https://www.python.org/downloads/) installed on your machine.
2. Have a working version of [Docker Desktop](https://docs.docker.com/desktop/) installed on your machine.

### 2.2. Docker basics

### 2.2.1. Image
An image is a read-only template with instructions for creating a Docker container. Often, an image is based on another image, with some additional customization. For example, you may build an image that is based on the `python:3.9` image, but installs additional dependencies using `pip`.
You can think of an image as a class.


### 2.2.2. Container
A container is a runnable instance of an image. You can create, start, stop, move, or delete a container using the Docker API or CLI. You can connect a container to one or more networks, attach storage to it, or even create a new image based on its current state.
You can think of a container as an instance of a class which is an image here.

### 2.2.3. Dockerfile
A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image. Using `docker build`, users can create an automated build that executes several command-line instructions in succession.
You can think of a Dockerfile as a blueprint to build an image.

### 2.3. Hands-on

Now we will create a docker container for a Flask app, build it and run it locally. Flask is the subject of the next lab so don't worry too much about it for now. Just know that Flask is a web framework for Python.


#### 2.3.1. Step 1: Create your Dockerfile

Make sure to have [Docker Desktop](https://docs.docker.com/desktop/) installed and :warning: **RUNNING** :warning: on your machine.

For this small example, the tree structure of your project should look like this:
```
.
├── Dockerfile
├── app.py
└── requirements.txt
```


In the file named `Dockerfile`, add the following content:
```Dockerfile
FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8080
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
```

- `FROM python:3.9`: tells Docker to use the official Python image as the base image. You can find more official images or well-known community images on [Docker Hub](https://hub.docker.com/).
For example `tiangolo/uwsgi-nginx-flask:python3.9` is a well-known community production-ready stack with uWSGI, Nginx to serve your Flask application on Python 3.9.

- `WORKDIR /app`: sets the working directory **in the container** to `/app`. This means that any subsequent commands will be executed relative to this directory.

- `COPY . /app`: copies the current directory of your computer (where the Dockerfile is located so be sure to be in the root of your project when you run the Docker command) contents  **INTO** the container at `/app`. This is useful to copy your source code, `requirements.txt`, etc. into the container.

- `RUN pip install -r requirements.txt`: installs any needed packages specified in `requirements.txt`.\

    :warning: **Note**:
There are pros and cons of using base images compared to installing packages in the Dockerfile.\
Pros:
    - Speed: using a base image with pre-installed packages is faster than installing packages in the Dockerfile
    - Caching: Docker caches the layers of the image. If you change your source code but not your dependencies, Docker will use the cached layers and only rebuild the layers that have changed.
    - Conflict: if you install packages in the Dockerfile, you may run into conflicts between packages. For example, if you install `numpy==1.20` in your Dockerfile but another package requires `numpy==1.19`, you will have a conflict. Official images are well-tested and do not have conflicts between packages.

    Cons:
    - Large image: the base image may contain packages that you do not need. This will make your image larger than necessary.
    - Security: the base image may contain packages that have security vulnerabilities. You need to keep the base image up-to-date to ensure that you are not using packages with known vulnerabilities.
    - Version: the base image may contain packages that are not the version you need. For example, if you need `numpy==1.20` but the base image contains `numpy==1.19`, you will need to install `numpy==1.20` in the Dockerfile.

- `EXPOSE 8080`: makes port 8080 available to the world outside this container. This is useful to access the Flask app once the container is running.

- `ENV FLASK_APP=app.py`: defines an environment variable `FLASK_APP` with the value `app.py` to tell Flask which file to run.

- `CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]`: this line runs `flask run --host=0.0.0.0 --port=8080` when the container launches. This is useful to start the Flask app when the container starts.

#### 2.3.2. Step 2: Create the `requirements.txt` file
In the file named `requirements.txt` add the following content:
```txt
flask
```
This file specifies the dependencies of your project. In this case, we only need Flask.

#### 2.3.3. Step 3: Create the `app.py` file
In the file named `app.py` add the following content:
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to the Simple Computation Flask App!"
```

This file contains a simple Flask app that returns a welcome message when you access the root URL.

#### 2.3.4. Step 4: Build the Docker image and run it

```bash
docker build -t simple-app .
```

This command builds the Docker image using the Dockerfile in the current directory and tags the image with the name `simple-app`. So now, if you go to your Docker Desktop, you should see in the images, the `simple-app` image.

Alternatively, you can see in the terminal the list of images by running the following command:

```bash
docker images
```

Run the Docker container by running the following command:
```bash
docker run -p 4000:8080 simple-app
```

`4000:8080` means that we are mapping port 8080 of the container to port 4000 of the host machine. You can access the app by going to http://localhost:4000 in your browser.

Why are there 2 ports ? The first one is the port of the host machine and the second one is the port of the container.
You can view the first port as the door of your house and the second port as the door of your room. You can access your room through the door of your house.

#### 2.3.5. Step 5: Stop and remove the container and image

Stop the container by running the following command:
```bash
docker stop <container_id>
```

or use ctrl+c in the terminal where the container is running.

You can see the list of running containers by running the following command:
```bash
docker ps
```

To see all containers (including stopped ones), run the following command:
```bash
docker ps -a
```

To Remove the container from your machine, run the following command:
```bash
docker rm <container_id>
```

Finally to remove the image, run the following command:
```bash
docker rmi simple-app
```

You need first to remove the container before removing the image even if the container is stopped. This is because the container is linked to the image and you can't remove an image that is linked to a container.


## 3. Your turn (ML container)

The deliverable you need to provide is a Dockerfile that builds a container for a simple machine learning model. You should download a dataset, train a model on this dataset, and then make predictions with this model. You can use any machine learning library you want (scikit-learn, PyTorch, ...). 

Flask is **not mandatory** here because this is the subject of the next lab but you can use it if you want to serve your model. Your docker can just output the training loss of your model and then the predictions on a test set.
