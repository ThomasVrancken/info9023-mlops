# Lab 3 [Sprint 2, W4]: Docker & UV

## 0. Introduction

This lab will introduce you to Docker but also to UV, a modern Python packaging tool. You will get hands-on experience in containerizing a simple Python application in class, then you will need to apply these concepts by building a container for a basic machine learning model.

**Learning objectives**
- understand the differences between virtual environments, virtual machines, and containers,
- learn Docker basics (images, containers, Dockerfiles),
- containerize a Python Flask application,
- explore modern Python package management with UV,
- build optimized Docker images for ML applications.

> **Note about deployment** \
> This lab focuses on containerization fundamentals. In the next lab, you will deploy these containers to Google Cloud Run.

## 1. Understanding virtual environments, virtual machines, and containers

### 1.1. Virtual environment

A virtual environment is a self-contained directory that contains a Python installation for a particular version of Python, plus a number of additional packages. It allows you to work on a specific project without worrying about the dependencies of other projects.

Traditionally, Python developers use multiple tools to manage their projects: `venv` for environment isolation, `pip` for package installation, `pip-tools` for dependency locking, and `pyenv` for Python version management. This multi-tool approach works but can be slow and complex.

**Pros of virtual environments**
- **Reproducibility**. You can share your `requirements.txt` file with others to ensure they have the same dependencies.
- **Dependency management**. It forces you to specify the dependencies of your project.
- **Isolation**. It prevents conflicts between different projects.

**Cons of virtual environments**
- **Effort to maintain**. You need to update the `requirements.txt` file when you add or remove packages.
- **Storage space**. Each virtual environment takes up disk space with duplicate dependencies across different virtual environments.
- **OS compatibility**. Dependencies in your `requirements.txt` file may not work identically across different operating systems.

### 1.2. Virtual machine (VM)

A virtual machine emulates a physical computer. It allows you to run multiple operating systems on a single physical machine. Each virtual machine has its own virtual hardware, including CPU, memory, storage, and network interfaces. You can install an operating system on a virtual machine and run software on it as if it were a physical computer.

**Pros**
- **Isolation**. Software running on a virtual machine is isolated from the host operating system.
- **Compatibility**. You can run software that requires a different operating system than the one you are currently using.
- **Sharing**. You can share a virtual machine image with others to ensure they have the same environment.

**Cons**
- **Resource intensive**. Each virtual machine requires its own CPU, memory, storage, and network interfaces, so in general you can only run a few virtual machines on a single physical machine.
- **Storage space**. Each virtual machine takes up space on your hard drive.
- **Slow to start**. Starting a virtual machine can take several minutes.

### 1.3. Container

A container is a lightweight, standalone, executable package of software that includes everything needed to run an application: code, runtime, system tools, system libraries, and settings.

The difference with a VM is that Docker does not embed a full operating system. Docker containers are based on Linux kernel features (namespaces, cgroups). On Linux hosts, containers directly use the host's Linux kernel. On Windows and macOS, Docker Desktop runs a lightweight Linux VM to provide a Linux kernel for the containers. This architecture ensures that containerized applications run consistently across different host operating systems.

**Pros**
- **Portability**. You can run a container on any machine that has Docker installed.
- **Fast startup**. Once built, containers start in seconds (unlike VMs which take minutes). However, building containers can be slow depending on dependencies.
- **Efficiency**. Containers share the host operating system's kernel so they are lightweight and use fewer resources than a virtual machine.
- **Modularity**. You can build a container for each component of your application and run them together.
- **Isolation**. Containers are isolated from each other. So if one container crashes, it does not affect other containers.
- **Ease of management**. You can manage containers using the Docker CLI or a container orchestration tool like Kubernetes.

**Cons**
- **Security**. Containers share the host operating system's kernel so if an attacker gains access to the kernel, they can access all containers running on the host.
- **Complexity**. Containers are more complex to set up than virtual environments.
- **Slow build times**. Building Docker images can be slow, especially for large applications with many dependencies.

## 2. Getting started with Docker

### 2.1. Prerequisites

1. Have a working version of [Python](https://www.python.org/downloads/) installed on your machine
2. Have a working version of [Docker Desktop](https://docs.docker.com/desktop/) installed on your machine
3. Ensure Docker Desktop is **RUNNING** on your machine

### 2.2. Docker basics

Docker relies on three core concepts that build on each other: you write a **Dockerfile**, build it into an **image**, and run that image as a **container**.

```
Dockerfile  ──build──>  Image  ──run──>  Container
(recipe)                (snapshot)       (running app)
```

#### 2.2.1. Dockerfile

A Dockerfile is a text document that lists, step by step, everything needed to set up your application: which base system to start from, which files to copy, which packages to install, and which command to run at startup. Using `docker build`, Docker reads this file and produces an image from it.

You can think of a Dockerfile as a recipe.

#### 2.2.2. Image

An image is the read-only snapshot produced by building a Dockerfile. It captures the full result of every step in the recipe: the operating system, libraries, application code, and configuration. Images are composed of layers, where each layer corresponds to an instruction in the Dockerfile. Often, an image starts from a pre-existing base image. For example, you may start from the `python:3.13` base image and add your own code and dependencies on top.

You can think of an image as a class in object-oriented programming.

#### 2.2.3. Container

A container is what you get when you run an image. While the image is a static snapshot, the container is a live, isolated process with its own filesystem, network, and environment. You can start, stop, or delete containers using the Docker CLI.

You can run multiple containers from the same image, each independent of the others. For example, if your image contains a web server, you could run three containers from it to handle more traffic, each listening on a different port.

You can think of a container as an instance of a class, where the class is an image.

## 3. Hands-on Docker example

Now we will create a Docker container for a Flask app, build it and run it locally. Flask is the subject of the next lab so don't worry too much about it for now. Just know that Flask is a lightweight web framework for Python that we will use to create a simple API.

### 3.1. Project structure

Create a new directory for your project with the following structure:

```
.
├── Dockerfile
├── app.py
└── requirements.txt
```

> **Important: Dockerfile naming** \
> The file must be named exactly `Dockerfile` (capital D, no extension). The `docker build` command looks for this exact filename by default. If you use a different name like `dockerfile` or `DockerFile`, you'll need to specify it with the `-f` flag: `docker build -f yourname .`

### 3.2. Flask application

In the `app.py` file, add the following content:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to the Simple Flask App!"

@app.route("/health")
def health():
    return {"status": "healthy"}
```

This file contains a simple Flask app with two endpoints:
- `/` returns a welcome message
- `/health` returns a health check status (useful for deployment)

### 3.3. Requirements file

In the `requirements.txt` file, add the following content:

```txt
flask==3.1.0
```

This file specifies the dependencies of your project. We're pinning Flask to a specific version for reproducibility.

### 3.4. Dockerfile

In the `Dockerfile`, add the following content:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
```

#### 3.4.1. Dockerfile instructions explained

- `FROM python:3.13-slim`: every Dockerfile starts with a `FROM` instruction that sets the base image. Here we use the official Python 3.13 image in its `slim` variant, which includes Python and essential system libraries but leaves out extras like a C compiler or documentation. This keeps the image small (~150 MB vs ~1 GB for the full image). You can browse available base images on [Docker Hub](https://hub.docker.com/).

- `WORKDIR /app`: sets the working directory **inside the container** to `/app`. All subsequent instructions (`COPY`, `RUN`, `CMD`) will run relative to this path. Without this, files would end up in the root `/` directory, which is messy and error-prone.

- `COPY . /app`: copies everything from your local project directory (where the Dockerfile lives) **into** the container at `/app`. This is how your source code, `requirements.txt`, and other files get into the image. Note that the container has its own filesystem: it cannot see your local files unless you explicitly copy them in.

- `RUN pip install --no-cache-dir -r requirements.txt`: executes a command **during the build** to install your Python dependencies. The key difference between `RUN` and `CMD` is that `RUN` runs at build time (and the result is baked into the image), while `CMD` runs when the container starts. The `--no-cache-dir` flag tells pip not to store downloaded packages locally, since we won't need them again and it would just bloat the image.

- `EXPOSE 8080`: documents that the application inside the container will listen on port 8080. This is purely informational for anyone reading the Dockerfile: it does **not** actually open the port. To make the port accessible from your host machine, you need the `-p` flag when running the container (covered in section 3.5).

- `ENV FLASK_APP=app.py`: sets an environment variable inside the container. Flask uses the `FLASK_APP` variable to know which Python file contains the application. Without this, Flask wouldn't know what to run.

- `CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]`: defines the default command that runs when the container starts. This launches the Flask development server. The `--host=0.0.0.0` is important: by default, Flask only listens on `localhost` (127.0.0.1), which would make it unreachable from outside the container. Setting it to `0.0.0.0` tells Flask to accept connections from any network interface, including the host machine.

### 3.5. Build and run the Docker container

#### 3.5.1. Build the image

```bash
docker build -t flask-app .
```

This command builds the Docker image using the Dockerfile in the current directory (`.`) and tags the image with the name `flask-app`.

You can verify the image was created:

```bash
docker images
```

You should see `flask-app` in the list of images. You can also check Docker Desktop to see the image in the Images section.

#### 3.5.2. Run the container

```bash
docker run -p 4000:8080 flask-app
```

Because the container runs in its own isolated network, your host machine cannot reach it by default. The `-p` flag creates a bridge between a port on your machine and a port inside the container, so that requests to `localhost:4000` on your machine are forwarded to port `8080` inside the container.

**Port mapping explained**: `-p 4000:8080`
- `4000` is the port on your **host machine** (your computer)
- `8080` is the port **inside the container** (the one Flask is listening on)
- We intentionally use a different host port (4000 instead of 8080) to show that they don't have to match. You could use `-p 8080:8080` if you prefer, as long as the host port is not already in use.

**Test the application**

Open your browser and go to:
- http://localhost:4000 should show the welcome message
- http://localhost:4000/health should show the health status

Or use curl:

```bash
curl http://localhost:4000
curl http://localhost:4000/health
```

### 3.6. Docker container management

Containers don't clean up after themselves. A running container keeps consuming CPU and memory, and even stopped containers stay on disk until you explicitly remove them. Over time, forgotten containers and unused images can eat up significant disk space. Here are the essential commands to keep things tidy.

#### 3.6.1. View running containers

```bash
# Show running containers
docker ps

# Show all containers (including stopped)
docker ps -a
```

#### 3.6.2. Stop the container

```bash
# Option 1: Press Ctrl+C in the terminal where the container is running

# Option 2: Stop by container ID
docker stop <container_id>

# Option 3: Stop by container name
docker stop <container_name>
```

#### 3.6.3. Remove containers

```bash
# Remove a specific container
docker rm <container_id>

# Remove all stopped containers
docker container prune
```

#### 3.6.4. Remove images

```bash
# Remove a specific image
docker rmi flask-app

# Remove all unused images
docker image prune -a
```

> **Important**: You must remove containers before removing their images, even if the containers are stopped.

#### 3.6.5. Other useful commands

```bash
# Run a container in detached mode (background), so it doesn't block your terminal
docker run -d -p <host_port>:<container_port> <image_name>

# View the logs of a container (useful for debugging, especially in detached mode)
docker logs <container_id>

# Open a shell inside a running container (useful for inspecting files or debugging)
docker exec -it <container_id> /bin/bash

# Remove all unused containers, images, and networks at once (use with caution!)
docker system prune -a
```

## 4. Modern Python packaging with UV

Now that you understand Docker basics, let's explore UV, a modern Python package manager that significantly improves upon traditional `pip` and `venv` workflows.

### 4.1. What is UV?

[UV](https://github.com/astral-sh/uv) is a fast Python package installer and resolver written in Rust. It's designed to be a drop-in replacement for `pip` and `pip-tools`, but with significantly better performance and user experience.

**Key benefits**
- **Much faster installation**. Installing packages like `numpy`, `pandas`, and `scikit-learn` takes seconds instead of minutes.
- **Automatic lockfiles**. When you install `flask`, it also installs sub-dependencies like `werkzeug` and `jinja2`. UV's lockfile automatically captures exact versions of ALL packages (both direct and transitive), not just the ones you explicitly list. This means true reproducibility without manual work.
- **Fewer dependency conflicts**. Solves complex dependency puzzles that pip often gets wrong.
- **Single tool**. One command (`uv`) replaces `venv`, `pip`, and `pip-tools`.
- **Faster Docker builds**. Reduces Docker image build time from minutes to seconds during development.

### 4.2. Installing UV

Install UV on your local machine:

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# using pip
pip install uv
```

Verify the installation:

```bash
uv --version
```

### 4.3. Basic UV commands

UV supports two workflows. The **pip-compatibility mode** is a drop-in replacement for pip and still uses `requirements.txt`. The **native project mode** is UV's recommended approach and uses `pyproject.toml` + `uv.lock`.

**Pip-compatibility mode** (familiar, works with existing `requirements.txt`):

```bash
# create a new Python virtual environment
uv venv

# activate the virtual environment
source .venv/bin/activate # macOS/Linux
.venv\Scripts\activate # Windows

# install packages
uv pip install flask numpy pandas

# install from requirements.txt
uv pip install -r requirements.txt

# sync environment to match requirements exactly
uv pip sync requirements.txt
```

**Native project mode** (recommended. Uses `pyproject.toml` + `uv.lock`):

```bash
# initialize a new project (creates pyproject.toml)
uv init my-project  # creates a new directory called my-project
uv init .           # or: initialize in the current directory

# add packages (updates pyproject.toml and uv.lock automatically)
uv add flask numpy pandas

# install all dependencies from uv.lock (exact versions, fully reproducible)
uv sync

# install without updating uv.lock (e.g. in CI or Docker)
uv sync --frozen
```

The key difference: `uv.lock` captures the exact version of every package (including transitive dependencies) automatically, without any manual step. With pip, you need to manually run `pip freeze > requirements.txt` to get the same level of reproducibility.

## 5. Optimizing Docker builds with UV

UV shines in Docker environments because it dramatically reduces build times. Here's how to use UV in your Dockerfiles.

### 5.1. Traditional approach with pip

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Notice that we `COPY requirements.txt` **before** copying the rest of the code. Docker caches each layer: if your `requirements.txt` hasn't changed, Docker will reuse the cached layer with all your installed dependencies and skip the slow `pip install` step entirely. If we had used `COPY . .` first, any change to any file (even a comment in `app.py`) would invalidate the cache and force a full reinstall.

### 5.2. Modern approach with UV

```dockerfile
FROM python:3.13-slim
WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock .

# Install dependencies with UV (much faster)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY . .

# Add the virtual environment created by uv sync to PATH
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "app.py"]
```

Two things are new here:

- `COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv`: we need UV inside our container, but it's not included in the Python base image. Instead of downloading and installing it (with `curl` or `pip`), we use `--from=` to copy the UV binary straight from an existing image that already contains it (`ghcr.io/astral-sh/uv:latest`). Think of it as borrowing a tool from another container's toolbox.

- `uv sync --frozen --no-dev --no-install-project`: installs all dependencies from `uv.lock` exactly as pinned (`--frozen` prevents any lock file update), skipping development-only packages (`--no-dev`). The `--no-install-project` flag is important. By default, `uv sync` also tries to install your project itself as a package, but at this point in the Dockerfile only `pyproject.toml` and `uv.lock` have been copied. Your source files (`train.py`, etc.) are not there yet. Without this flag, UV cannot find the source and exits with an error. UV automatically creates a `.venv` virtual environment, which we then expose via `ENV PATH`.

### 5.3. Multi-stage build with UV (recommended for production)

```dockerfile
# Stage 1: Build dependencies
FROM python:3.13-slim AS builder
WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies into a virtual environment
COPY pyproject.toml uv.lock .
RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime
FROM python:3.13-slim
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "app.py"]
```

**The problem with single-stage builds**. In Docker, everything you do during the build stays in the final image. In section 5.2, we installed UV and used it to install our packages but UV itself is still sitting in the final image, even though we only needed it during the build. The same goes for any compiler, cache files, or temporary downloads. For a small Flask app this barely matters, but for an ML project with heavy dependencies (numpy, scikit-learn, PyTorch...), this build-time baggage can add hundreds of megabytes to your image.

**How multi-stage builds solve this**: the Dockerfile above uses two `FROM` statements, which creates two separate stages. The first stage (`builder`) is a temporary workspace where we install UV and all our dependencies. The second stage starts from a **fresh, clean** Python image and only copies over the installed packages leaving UV, caches, and all build-time leftovers behind. The builder stage is then discarded.

> **Why use a virtual environment here?** \
> In section 5.2 we said containers don't need virtual environments and that's still true. But here the virtual environment serves a practical purpose. It puts all installed packages into a single folder (`/app/.venv`). This makes it easy to copy them from stage 1 to stage 2 with one `COPY` command. Without it, packages would be scattered across system directories (`/usr/local/lib/`, `/usr/local/bin/`, etc.) and much harder to transfer.

## 6. Assignment: ML model container

**Objective**: Create a Docker container for a simple machine learning workflow.

**Requirements**

Your container should:
1. Load a dataset (you can use built-in datasets from scikit-learn, such as Iris or Wine)
2. Train a machine learning model on this dataset (any algorithm: logistic regression, decision tree, random forest, etc.)
3. Evaluate the model and display metrics (accuracy, confusion matrix, etc.)
4. Save the trained model to a file

**Deadline**: February 23, 2026 23:59

**Deliverables**

Submit the following files on **Gradescope**:
1. `Dockerfile` - your container definition
2. `train.py` - Python script that trains and evaluates your model
3. dependency file, either `requirements.txt` (if using pip) **or** `pyproject.toml` + `uv.lock` (if using UV)

**Optional challenges**

- Use UV instead of pip for faster builds
- Implement a multi-stage build to reduce image size
- Add Flask endpoints to serve predictions
- Use a more complex dataset (download from the internet)
- Compare multiple models and select the best one

**Example structure**

With pip:
```
ml-container/
├── Dockerfile
├── train.py
└── requirements.txt
```

With UV:
```
ml-container/
├── Dockerfile
├── train.py
├── pyproject.toml
└── uv.lock
```

**Example `train.py` skeleton**

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

# Load dataset
data = load_iris()
X = data.data
y = data.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=data.target_names))

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\nModel saved as model.pkl")
```

**Tips**

- Test your code locally before containerizing
- Use `python:3.13-slim` as your base image to keep the image size reasonable
- Install only the packages you need (scikit-learn, numpy, pandas)
- If using UV, `pyproject.toml` and `uv.lock` are **generated automatically** i.e., you don't write them by hand. From inside your project directory, run:
  ```bash
  uv init .          # creates pyproject.toml in the current directory
  uv add scikit-learn numpy  # adds packages and generates uv.lock
  ```
  Note the `.` in `uv init .`: this initializes UV in your **existing** directory, instead of creating a new subdirectory.
- If using UV, you **must** add a `.dockerignore` to exclude your local `.venv/`, otherwise `COPY . .` will overwrite the venv built inside the container with your local one (which uses a different Python version and will crash). Create a `.dockerignore` file with at minimum:
  ```
  .venv
  __pycache__
  *.pyc
  ```

## 7. Additional resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/) - find official and community images
- [UV Documentation](https://github.com/astral-sh/uv)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

## 8. Troubleshooting

**Docker Desktop not running**
- Error: `Cannot connect to the Docker daemon`
- Solution: Ensure Docker Desktop is running

**Port already in use**
- Error: `Bind for 0.0.0.0:4000 failed: port is already allocated`
- Solution: Either stop the process using that port or use a different port: `docker run -p 4001:8080 flask-app`

**Image too large**
- Problem: Docker image is several GB
- Solution: Use `python:3.13-slim` instead of `python:3.13`, add `.dockerignore`, use multi-stage builds

**Slow builds**
- Problem: `pip install` takes a long time
- Solution: Use UV for faster package installation, leverage Docker layer caching

**Permission denied**
- Error: `Permission denied` when running Docker commands
- Solution: On Linux, you may need to add your user to the docker group: `sudo usermod -aG docker $USER`

**Cannot find module**
- Error: `ModuleNotFoundError: No module named 'flask'`
- Solution (pip): Ensure your `requirements.txt` lists all dependencies and the `RUN pip install` step completed successfully
- Solution (UV): Ensure your `pyproject.toml` lists all dependencies, that `uv.lock` is up-to-date (`uv sync`), and that the `ENV PATH` line exposes the virtual environment
