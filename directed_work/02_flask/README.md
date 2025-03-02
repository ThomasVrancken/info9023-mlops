# Directed work 2 [Sprint 3, W5] : Flask

## 0. Introduction
In this lab, you will learn the basics of Flask, a web framework for Python. You will learn how to create a simple web application that can be used to serve a machine learning model.

## 0.1. Prerequisites
With last week's directed work, you should have a basic understanding of Docker and should have re-read the Docker lecture slides or at least directed work.

You should also have a virtual environment set up.

Reminder: to create a virtual environment and activate it, you can use the following command:
```bash
python3 -m venv {your_env_name}
source {your_env_name}/bin/activate
``` 

## 1. Flask
With the previous directed work, the Flask installation should already work and you should be able to run your Flask application.

### 1.1. Understanding the code

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
```

- The `@app.route('/')` decorator tells Flask to call the `hello_world` function when someone visits the root URL of the website.
- The `app.run()` function starts the Flask development server. By default, the server runs on port 5000. You can change the port by passing a `port` argument to `app.run()`.

### 1.2. Debug mode
When you are developing a Flask application, you can enable debug mode by setting the `debug` argument to `True` in the `app.run()` function. This will automatically reload the server when you make changes to the code.

For example if you modify the `hello_world` function to return 'Hello, World! from Flask!', you can see the changes by refreshing the page in your browser. If the debug mode is not enabled, you will need to stop the server and restart it to see the changes.

The `run()` function in Flask is used to run the Flask application. It starts a development server that listens for incoming requests and handles them accordingly. It can take several parameters to customize the behavior of the server. Let's go through each parameter:

- `host` (default: `127.0.0.1`): This parameter specifies the hostname or IP address on which the server should listen for incoming requests. You can change it to `0.0.0.0` to allow requests from any IP address an not only from your local machine.

- `port` (default: `5000`): This parameter specifies the port number on which the server should listen for incoming requests.

- `debug` (default: `False`): We already talked about but note that, in production, it's important to set `debug=False` for 2 main security reasons.

    - Exposure of sensitive information: The interactive debugger can expose sensitive information from your application, including variable values, server configuration, or parts of the source code.

    - Arbitrary code execution: The debugger includes a feature that allows you to execute arbitrary Python code in the context of the server. This means that if an attacker can trigger an error page, they could potentially execute malicious code on your server.

- `options` (optional): This parameter allows you to pass additional options to the underlying server. For example, you can specify an SSL certificate or key file using the `ssl_context` option.

### 1.3. Routing

In Flask, routing refers to the process of mapping URLs to view functions. A view function is a Python function that returns a response to a request. You can define a view function using the `@app.route()` decorator.

For example, if you want to run a certain piece of code when a user visits the `/about` URL, you can define a view function like this:

```python
@app.route('/about')
def about():
    return 'This is the about page'
```

After saving and running your application, you can access the URL `http://localhost:5000/about` in your browser and see the message 'This is the about page'.

Routes can also contain variable sections, which are specified with angle brackets `< >`. The variable sections are passed as keyword arguments to the function. For example:

```python
@app.route('/hello/<username>')
def hello(username):
    return f'Hello, {username}'
``` 

In this example, the `hello` function takes a `username` argument and returns a personalized greeting. When you visit the URL `http://localhost:5000/hello/john`, the function will return 'Hello, john'.

This allows you to create dynamic routes that can handle different inputs.

### 1.4. URL building

The `url_for()`function is used in Flask to generate URLs for a specific function. This is useful because it means you don't have to hard code your URLs into your templates. Instead, you can just use the `url_for()` function and Flask will figure out the URL for you.

Here's an example of how you can use `url_for()`:

```python
from flask import Flask, redirect, url_for
app = Flask(__name__)

@app.route('/admin')
def hello_admin():
   return 'Hello Admin'

@app.route('/guest/<guest>')
def hello_guest(guest):
   return 'Hello %s as Guest' % guest

@app.route('/user/<name>')
def hello_user(name):
   if name =='admin':
      return redirect(url_for('hello_admin'))
   else:
      return redirect(url_for('hello_guest',guest = name))

if __name__ == '__main__':
   app.run(debug = True)
```

The above script will redirect the user to the `hello_admin()` and the application response in browser is: 
```
Hello Admin
```
if the URL is `http://localhost:5000/user/admin`, and to the `hello_guest()` function if the URL is `http://localhost:5000/user/guest`.

The `url_for()` function takes the name of a function as its first argument, and any number of keyword arguments, each corresponding to a variable part of the URL rule. Here's the syntax for the `url_for()` function:

```python
url_for('function_name', variable=value, ...)
```

## 2. HTTP Methods

Flask routes respond to GET requests by default, but they can be configured to respond to other HTTP methods as well, such as POST, PUT, DELETE, etc. You can use the `methods` argument of the `route()` decorator to specify which HTTP methods your route should respond to.

Here's an example:

```python
from flask import Flask, jsonify, request
app = Flask(__name__)

incomes = [
    { 'description': 'salary', 'amount': 5000 }
]


@app.route('/incomes')
def get_incomes():
    return jsonify(incomes)


@app.route('/incomes', methods=['POST'])
def add_income():
    incomes.append(request.get_json())
    return '', 204
```
In this example, the `/incomes` route responds to GET requests by returning a list of incomes in JSON format. It also responds to POST requests by adding a new income to the list.

If we want to see in the terminal the `incomes`, we can run the following `curl` command:

```bash 
curl http://localhost:5000/incomes
```

Now, if we want to add a new income, we can use once again the `curl` command to send a POST request to the server:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"description":"dividends", "amount": 200}' http://localhost:5000/incomes
```

After running the above command, the `incomes` list will contain two items: the original salary income and the new dividends income.

### 2.1. Postman
Postman is a popular API client that makes it easy to test and document APIs. It allows you to send requests to your API and inspect the responses. You can also use it to create and save collections of requests, which can be shared with your team.

You can download Postman from the official website: [https://www.postman.com/](https://www.postman.com/)

## 3. Jinja2 templating
Flask uses the Jinja2 templating engine to render HTML templates. Jinja2 is a powerful and flexible templating engine that allows you to embed Python code in your HTML templates. This makes it easy to generate dynamic content in your web pages.

Here's an example of how you can use Jinja2 templates in Flask:

```python
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, the `hello()` function renders the `hello.html` template and passes the `name` variable to the template. 

The `hello.html` template should be created in a directory named `templates` in the same directory as your Flask application. The `hello.html` file might look something like this:

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

When you navigate to `http://localhost:5000/hello/john` in your web browser, you should see a web page that says "Hello, john".



Jinja2 templates use double curly braces `{{ }}` to embed Python code in the HTML. You can use this syntax to display variables, call functions, and perform other operations in your templates. Jinja2 also supports control structures like loops and conditionals, so you can use it to generate complex HTML content.


## 4. Docker and Flask
Now that you have a basic understanding of Flask, let's see how to run a Flask application in a Docker container.

### 4.1. Dockerfile
Create a new file named `Dockerfile` in the same directory as your Flask application. The `Dockerfile` is a text file that contains a set of instructions for building a Docker image. Here's an example of a `Dockerfile` for a Flask application:

```Dockerfile
# Use the official image as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /src

# Copy our files in the container
COPY /src/hello.py
COPY /src/requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Define environment variable
ENV FLASK_APP=hello.py

# Run hello.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
```

### 4.2. Building the Docker Image

Open Docker Desktop and make sure that the Docker daemon is running.

To build the Docker image, navigate to the directory containing your `Dockerfile` and run the following command:

```bash
docker build -t my-flask-app .
```

The `-t` flag is used to tag the image with a name, in this case `my-flask-app`. The `.` at the end of the command specifies the build context, which is the current directory.

### 4.3. Running the Docker Container
After building the Docker image, you can run a container from the image using the following command:

```bash
docker run -p 9090:8080 my-flask-app
```

The `-p` flag is used to map the host port to the container port. In this case, the Flask application is running on port 8080 inside the container, and we are mapping it to port 9090 on the host machine.

After running the above command, you should be able to access your Flask application by navigating to `http://localhost:9090` in your web browser.

## 5. Your turn - Inverted classroom
### 5.1. Explanation
As explained last week, you are now asked to do the tasks explained in the following subsection. 
You are asked to do it by groups (same groups as for your project). You have approximately 1 hour to do it.
Then 2 groups will present their work to the rest of the class. This will be followed by a debriefing with the teaching staff.

### 5.2. Tasks
Strict instructions:
- Create a **simple** machine learning model that takes input and returns a single output. You can use any model you like, such as a linear regression model or a decision tree model.
- Create a new Flask application that has the following routes:
    - GET `/` : Returns a welcome message. Use a Jinja2 template to render the HTML content.
    - POST `/predict` : Accept a JSON payload containing input data and returns a JSON response with the model's predicted output.
    - (optional) GET `/past_predictions` : Returns a list of past predictions. These can be stored in memory or in a file.
    - (optional) PUT `/past_predictions/{id}` : Updates an existing past prediction by ID.
    - (optional) PUT `/past_predictions/last` : Updates the most recent past prediction.
- Create a Dockerfile for your Flask application and build a Docker image.
- Run a Docker container from the image and test the `/predict` route using Postman or `curl`.

## 5.3. Useful links for your code
- [Flask template](https://github.com/app-generator/flask-template)
- [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/en/3.0.x/)
- [Hugging Face API](https://huggingface.co/api)


## 6. References
- [Flask tutorial](https://www.tutorialspoint.com/flask/index.htm)
- [Flask tutorial 2](https://auth0.com/blog/developing-restful-apis-with-python-and-flask/)
