# Lab 4 [Sprint 3, W5]: Flask

## 0. Introduction

In this lab, you will learn the basics of Flask, a lightweight web framework for Python. By the end, you will be able to build a simple API that serves predictions from a machine learning model.

### Why Flask?

When you train a machine learning model, it lives inside a Python script on your machine. But other people and applications cannot use it. They would need your exact code, your exact environment, and your exact data. An API (Application Programming Interface) solves this. It wraps your model behind a web endpoint so that anyone can send a request and get a prediction back, without ever touching your code.

Flask is one of the simplest ways to build an API in Python. It requires very little boilerplate, which makes it ideal for quickly exposing an ML model.

### 0.1. Prerequisites

- You should have Python 3 installed.
- You should have completed [Lab 3 (Docker & UV)](../03_docker/README.md) and have Docker and UV installed.

Create a virtual environment and install Flask using UV

```bash
uv venv .venv
source .venv/bin/activate
uv pip install flask
```

## 1. Flask Basics

### 1.1. A Minimal Application

Create a file called `hello.py` with the following content

```python
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
```

Run it with

```bash
python hello.py
```

Then open `http://localhost:5000` in your browser. You should see "Hello, World!".

**How it works:**

- `Flask(__name__)` creates the application. The `__name__` argument tells Flask where to find resources (templates, static files) relative to your script.
- `@app.route('/')` is a **decorator** that tells Flask: "when someone visits the root URL (`/`), call this function."
- `app.run()` starts a local development server. By default, Flask listens on port `5000`, which is why we visit `localhost:5000`.

> **macOS users.** Port 5000 is used by AirPlay Receiver since macOS Monterey. If you get an "Address already in use" error, either disable AirPlay Receiver in **System Settings > General > AirDrop & Handoff**, or use a different port `app.run(port=5001)`.

### 1.2. Debug Mode

During development, you want the server to automatically reload when you change your code. Enable this with debug mode:

```python
app.run(debug=True)
```

Try it yourself! Change the return value of `hello_world()` to `'Hello from Flask!'`, save the file, and refresh your browser. The change appears immediately without restarting the server.

> **Warning** Never enable debug mode in production. The interactive debugger exposes sensitive information (variable values, source code) and allows arbitrary code execution on the server.

#### `app.run()` Parameters

| Parameter | Default       | Description |
|-----------|---------------|-------------|
| `host`    | `'127.0.0.1'` | The IP address to listen on. Use `'0.0.0.0'` to accept connections from any machine (not just localhost). |
| `port`    | `5000`        | The port number to listen on. |
| `debug`   | `False`       | Enable auto-reload and interactive debugger. |

### 1.3. Routing

**Routing** maps URLs to Python functions. Each `@app.route()` decorator creates a mapping between a URL path and a view function (the function that handles the request).

```python
@app.route('/about')
def about():
    return 'This is the about page'
```

Visit `http://localhost:5000/about` to see the result.

#### Dynamic Routes

Routes can contain **variable sections** in angle brackets. Flask passes their values as function arguments:

```python
@app.route('/hello/<username>')
def hello(username):
    return f'Hello, {username}!'
```

Visiting `http://localhost:5000/hello/Alice` returns `Hello, Alice!`. This is how you create endpoints that respond differently based on the URL, for example, an ML endpoint that takes a model name as part of the path.

### 1.4. URL Building

Instead of hardcoding URLs in your code, use `url_for()` to generate them dynamically. This way, if you rename a route, all references update automatically:

```python
from flask import Flask, redirect, url_for

app = Flask(__name__)


@app.route('/admin')
def hello_admin():
    return 'Hello Admin'


@app.route('/guest/<guest>')
def hello_guest(guest):
    return f'Hello {guest} as Guest'


@app.route('/user/<name>')
def hello_user(name):
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest=name))


if __name__ == '__main__':
    app.run(debug=True)
```

- `url_for('hello_admin')` generates the URL `/admin`.
- `url_for('hello_guest', guest='Alice')` generates `/guest/Alice`.
- `redirect()` sends the user's browser to that URL.

Visiting `http://localhost:5000/user/admin` redirects to `/admin` and shows "Hello Admin". Visiting `http://localhost:5000/user/Alice` redirects to `/guest/Alice` and shows "Hello Alice as Guest".

## 2. HTTP Methods

So far, all our routes respond to **GET** requests (the browser asking for a page). But APIs need other methods too:

| Method   | Purpose                        | Example                        |
|----------|--------------------------------|--------------------------------|
| **GET**  | Retrieve data                  | Get a list of predictions      |
| **POST** | Send data to create something  | Submit input for a prediction  |
| **PUT**  | Update existing data           | Correct a past prediction      |
| **DELETE** | Remove data                  | Delete a prediction            |

This matters for ML APIs: your `/predict` endpoint needs to receive input data (POST), not just be visited in a browser (GET).

### 2.1. GET and POST Example

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

incomes = [
    {'description': 'salary', 'amount': 5000}
]


@app.route('/incomes')
def get_incomes():
    return jsonify(incomes)


@app.route('/incomes', methods=['POST'])
def add_income():
    incomes.append(request.get_json())
    return '', 204


if __name__ == '__main__':
    app.run(debug=True)
```

- `jsonify(incomes)` converts the Python list to a JSON response, i.e., the standard format for APIs.
- `request.get_json()` parses the JSON body from the incoming POST request.
- Status code `204` means "success, no content to return."

**Test it with `curl`:**

```bash
# GET: retrieve all incomes
curl http://localhost:5000/incomes

# POST: add a new income
curl -X POST -H "Content-Type: application/json" \
     -d '{"description": "dividends", "amount": 200}' \
     http://localhost:5000/incomes

# GET again: verify the new income was added
curl http://localhost:5000/incomes
```

### 2.2. Postman (Optional)

[Postman](https://www.postman.com/) is a GUI tool for testing APIs. It lets you craft requests (GET, POST, PUT, DELETE), set headers, and inspect responses without writing `curl` commands. It can be useful for more complex testing, but `curl` is sufficient for this lab.

## 3. Jinja2 Templating

So far, our routes return plain text. But what if you want to return a full HTML page? You could build the HTML string manually, but that quickly becomes messy. Jinja2 is Flask's templating engine: it lets you write HTML files with placeholders that Flask fills in with Python values.

### 3.1. Example

Create the Flask app (`jinja_app.py`):

```python
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


if __name__ == '__main__':
    app.run(debug=True)
```

Create a `templates/` directory **next to your script** (i.e., in the same folder as `jinja_app.py`), and inside it create `hello.html`. Flask looks for templates relative to the application file, so the structure must be

```
├── jinja_app.py
└── templates/
    └── hello.html
```

```html
<!doctype html>
<html>
<head>
    <title>Hello, {{ name }}</title>
</head>
<body>
    <h1>Hello, {{ name }}</h1>
</body>
</html>
```

Visit `http://localhost:5000/hello/Alice` to see a rendered HTML page saying "Hello, Alice".

- `render_template('hello.html', name=name)` looks for `hello.html` inside the `templates/` directory and replaces `{{ name }}` with the actual value.
- Jinja2 also supports loops (`{% for ... %}`) and conditionals (`{% if ... %}`), but we won't need those for this lab.

> **Note:** For ML APIs, you will typically return JSON (using `jsonify`) rather than HTML pages. Jinja2 is more useful if you want to build a simple web interface for your model.

## 4. Docker and Flask

Now let's containerize your Flask application. Since you have already learned Docker in [Lab 3](../03_docker/README.md), this section focuses on the specifics of running Flask inside a container.

### 4.1. Requirements File

First, create a `requirements.txt` listing your dependencies:

```
flask==3.1.0
```

### 4.2. Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install UV (borrowing the binary from its official image, as seen in Lab 3)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY hello.py .

EXPOSE 8080

ENV FLASK_APP=hello.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
```

A few Flask-specific points:

- **`--host=0.0.0.0`**. By default, Flask only listens on `127.0.0.1` (localhost). Inside a container, that means only processes *inside* the container can reach it. Setting `0.0.0.0` makes Flask listen on all network interfaces, so requests from outside the container (your browser) can reach it.
- **`--port=8080`**. Flask defaults to port 5000 (as we used in the earlier sections), but port 8080 is the standard convention for containerized web applications. Without this flag, Flask would listen on 5000 inside the container, and we would need `-p 9090:5000` instead.
- **`ENV FLASK_APP=hello.py`**. Tells the `flask run` command which file contains your application.
- **`uv pip install --system`**. As you learned in Lab 3, the `--system` flag tells UV to install packages directly into the container's Python instead of creating a virtual environment.

> **Why no multi-stage build here?** \
> In Lab 3 we saw that multi-stage builds discard build-time tools (like UV) and caches to keep the final image small. That matters when your dependencies are heavy (numpy, PyTorch, etc.) and the build leftovers add hundreds of megabytes. Here, Flask is a tiny dependency and UV itself is only ~30 MB, so the size savings would be negligible. A single-stage build keeps the Dockerfile simpler without a meaningful trade-off.

### 4.3. Build and Run

```bash
# Build the image
docker build -t my-flask-app .

# Run a container, mapping host port 9090 to container port 8080
docker run -p 9090:8080 my-flask-app
```

Open `http://localhost:9090` in your browser. You should see "Hello, World!".

> Remember from Lab 3: `-p 9090:8080` maps port 9090 on your machine to port 8080 inside the container. You could use any available host port.

## 5. Assignment: Flask ML API

**Deadline:** March 2nd

**Objective:** Create a Flask API that serves predictions from a simple machine learning model, containerized with Docker.

**Requirements**

1. Create a **simple** machine learning model that takes input and returns a prediction (e.g., a linear regression or decision tree).
2. Create a Flask application with the following routes:
    - **GET** `/`. Returns a welcome message. Use a Jinja2 template to render the page.
    - **POST** `/predict`. Accepts a JSON payload with input data and returns a JSON response with the model's prediction.
    - *(Optional)* **GET** `/past_predictions`. Returns a list of past predictions (stored in memory or in a file).
    - *(Optional)* **PUT** `/past_predictions/<id>`. Updates an existing past prediction by ID.
3. Create a Dockerfile for your application and build a Docker image.
4. Run a container and test the `/predict` route using `curl` or Postman.

**Deliverables**

Submit the following files on **Gradescope**:
1. `app.py` — Your Flask application
2. `Dockerfile` — Your container definition
3. `requirements.txt` — List of Python dependencies
4. Any additional files needed (model training script, templates, etc.)

## 6. Resources

- [Flask Documentation](https://flask.palletsprojects.com/en/stable/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/en/stable/)
- [Flask Tutorial — TutorialsPoint](https://www.tutorialspoint.com/flask/index.htm)
- [Developing RESTful APIs with Python and Flask — Auth0](https://auth0.com/blog/developing-restful-apis-with-python-and-flask/)
