# Lab W04: Virtual environment, Docker and Kubernetes

The goal of this lab is to get you started with three tools that were seen in todays' lecture.
- Virtual environments
- Docker
- Kubernetes

## Prerequisites

1. Have a working version of [python](https://www.python.org/downloads/)
2. Install [Docker Desktop](https://docs.docker.com/desktop/)  
3. Install [minikube](https://minikube.sigs.k8s.io/docs/start/)
4. Install [kubectl](https://kubernetes.io/docs/tasks/tools/)


## 1. Setup your virtual environment

We will first install a virtual environment to keep the dependencies of this tutorial clean and isolated.

You can find the exact steps for each OS [here](https://docs.python.org/3/library/venv.html).

1. Create a directory for this lab (for example just `lab_04/` in this location).
2. Create a terminal and navigate to the directory you just created.
3. Run `python -m venv {your_env_name}` (note that it is common to name your venv `.venv`, this would lead to `python -m venv .venv`)
   1. Alternatively, you can use conda: `conda create --name {your_env_name} python=3.12`
4. Activate your virtual environment. :warning: this is different per OS / shell ! See full breakdown [here](https://docs.python.org/3/library/venv.html#how-venvs-work).
   1. bash/zsh: `source {your_env_name}/bin/activate`
   2. PowerShell: `PS C:\> {your_env_name}\Scripts\Activate.ps1`

:bulb: Note that in [lecture W02](../../lectures/02_project_organization.pdf) we learned to ignore some file from git using the `.gitignore` file. If you include a line there with `**/{your_env_name}/` you'll make sure to not accidentally push your venv.

## 2. Run app locally

Before we dive into Docker, let's create a super simple app and run it locally.

:see_no_evil: Ok we will actually use [Flask](https://flask.palletsprojects.com/en/3.0.x/) for this. Note that we will explain how Flask work in week 05 ! For now you can just run this very simple python script and we'll go more in depth over how it works and how to create more robust apps in week 05.

1. Copy paste the `hello_world.py` and `requirements.txt` files to the directory you created.
2. Install the dependencies to your virtual environment by running `pip install -r requirements.txt` in your terminal.
3. Run the application by running `python hello_world.py` in your terminal.
4. Check that the application works by entering this url in any of your web browser (e.g. chrome): `http://localhost:8080`. A lovely engaging message should prompt up.
5. You can then stop the app by stopping the current terminal command (e.g. `CMD+C` or `CTRL+C`)

:bulb: Flask is not the purpose of this lab. However, you can mingle around by changing the input string on line 8 of the `hello_world.py` file.

:warning: This app does not much - next week we'll see how to get more out of it.

## 3. Docker

Now we will create a docker container for our app, build it and run it locally.

1. Make sure to have [Docker Desktop](https://docs.docker.com/desktop/) installed and running
2. Create an empty file called `Dockerfile` in your current working repository
3. Write the following lines of codes in it:
   1. `FROM python:3.12` - To start from the publicly available base image running python 3.12. Otherwise you would have to install it too (an image starts from nothing).
   2. `COPY hello_world.py .` and `COPY requirements.txt .` - To copy the files needed for the application to run (note that more simply you could have used `COPY . .` but this would have also included other files such as your venv or this markdown file).
   3. `EXPOSE 8080` - To make the port 8080 available outside your container (e.g. to access it once the container is running).
   4. `RUN pip install -r requirements.txt` - To run a command to install the dependencies in the container.
   5. `ENV FLASK_APP=hello_world.py` - To define the environment variable to run that specific flask app.
   6. `CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]` - To run the command that will actually run the flask app on the exposed port.
   7. Your file should now have the same commands as the `Dockerfile` in this directory :bulb:
4. You will now build your container by running in your terminal: `docker build -t mlsd-hello-world .` . Breaking down this command:
   1. The `-t` (tag) argument let's you name and optionally tag your image (to have different versions). Note that you could name it anything else than `mlsd-hello-world`
   2. The `.` just specifies the location of your `Dockerfile` (should be in the directory you are currently running your terminal from).
5. And now, we'll run our container by running in the terminal: `docker run -p 9090:8080 mlsd-hello-world`
   1. The `-p 9090:8080` argument is to do a port mapping from the container's port 8080 to your local port 9090.
6. Check that your container is running by entering this url in any of your web browser (e.g. chrome): `http://localhost:9090`. Note that it has a different port (9090) than our local flask app (8080), showing that indeed this is now running from our local container.

:raised_hands: You ran your local continer!

## 4. Kubernetes

We will now run our application on a local kubernetes cluster.

1. Make sure to have installed [minikube](https://minikube.sigs.k8s.io/docs/start/) and [kubectl](https://kubernetes.io/docs/tasks/tools/)
2. Start a local kubernetes cluster with minikube :construction_worker:
   1. Open a new terminal and run `minikube start`. This command actually starts a local Kubernetes cluster. The process may take a few minutes as it sets up the virtual machine and downloads necessary components.
3. Create a Docker image 
   1. Make sure to be in the same directory as all the files you previously used (python script, dependencies and Dockerfile)
   2. Build your Docker image as before, but we will use Minikube's Docker environment this time, so the image is available to your local Kubernetes cluster:
      1. `eval $(minikube docker-env)`
      2. `docker build -t k8-mlsd-hello-world .`
4. Create a kubernetes deployment
   1.  Copy the `app_deployment.yaml` file from the lab's files in github to your working repository. That file is a manifest used by Kubernetes to create and manage your application's deployment. Key parts are
       1.  `apiVersion: apps/v1`: Specifies the version of the Kubernetes API you're using to create the object. 
       2.  `kind: Deployment`: The type of Kubernetes resource you want to create. In this case, it's a Deployment, which helps you manage applications on your cluster.
       3.  `metadata: name: k8-mlsd-hello-world`: Metadata about the deployment, such as its name.
       4.  `spec: replicas: 2`: The specification of the deployment. Replicas specifies the number of instances of your application you want to run. In this case, it's set to 2.
       5.  `selector: matchLabels: app: k8-mlsd-hello-world`: Used to find the Pods that should be part of this deployment. Here, it matches Pods with the label app: k8-mlsd-hello-world.
       6.  `spec: containers:`: The name and Docker image to use for the container. Also includes the port on which the container is listening. Very importantly, it inlcudes `imagePullPolicy: Never` which tells Kubernetes not to try pulling the image from a registry, and instead use the image available locally. Without it you could have interferences breaking kubernetes from pulling the image.
   2.  Let's actually deploy the app from our locally built docker image by using the deployment configuration YAML: `kubectl apply -f app_deployment.yaml`
5.  Expose the Flask application
    1.  We now need to make our application accessible outside the cluster. We will expose it as a service: `kubectl expose deployment k8-mlsd-hello-world --type=NodePort --port=8080`
    2.  Find out the URL to access your application: `minikube service k8-mlsd-hello-world --url`
6.  Visit the URL indicated and voila, your app works!
7.  You can check the deployments and pods you have running on your local cluster by running
    1.  `kubectl get deployments`
    2.  `kubectl get pods`
8.  Stop minikube by running: `minikube stop`

:muscle: This is the end, hope you learned something interesting!
