# Lab 5: Introduction to Flask

In this lab, you will learn the basics of Flask. Flask is a lightweight and flexible web framework for Python designed to make building web applications quick and easy. It provides the tools and libraries needed to create web applications with minimal boilerplate code, allowing developers to focus on the core logic of their applications.

## 0. Set your environment

Create a virtual environment and install the dependencies. You can also re-use the venv from last week as the dependencies are the same.

For bash/zsh:
```bash
python -m venv {your_env_name}
source {your_env_name}/bin/activate
pip install -r requirements.txt
```

For PowerShell:
```bash
python -m venv {your_env_name}
PS C:\> {your_env_name}\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 1. Flask Installation Test

To test Flask installation, follow these steps:

1. Create a new Python file named `hello.py` and paste the following code into it:

    ```python
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
       return 'Hello World'

    if __name__ == '__main__':
       app.run()
    ```

2. Save the file and execute it from your terminal:

    ```bash
    python hello.py
    ```

3. After running the script, you will see a message in your Python shell indicating that the Flask application is running:

    ```
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    ```

4. Open your web browser and navigate to `http://localhost:5000`. You should see the message "Hello World" displayed in the browser window.

## 2. Understanding the Code

- **Defining Routes**: The `@app.route()` decorator tells Flask which URL should call the associated function. In this case, when the root URL `'/'` is accessed, the `hello_world()` function is executed.

- **Running the Application**: The `app.run()` method starts the Flask development server. By default, it runs on `http://127.0.0.1:5000`.

### 2.1 Debug Mode

Now, try to modify your `hello_world()` function by printing `'Hello world! Welcome to the course of MLOps'`, save your file and refresh the local server `http://127.0.0.1:5000`. Do you see the changes ? 

During development, it's convenient to enable debug mode in Flask. This allows the server to automatically reload when code changes are detected (when you save your modified file), and it provides a helpful debugger for tracking errors.

To enable debug mode:

1. Set the `debug` property of the `app` object to `True`:

    ```python
    app.debug = True
    ```

2. Run the application with debug mode enabled:

    ```python
    app.run(debug=True)
    ```

The `run()` function in Flask is used to run the Flask application. It starts a development server that listens for incoming requests and handles them accordingly. It can take several parameters to customize the behavior of the server. Let's go through each parameter:

- `host` (default: `'127.0.0.1'`): This parameter specifies the hostname or IP address on which the server should listen for incoming requests. You can change it to `'0.0.0.0'` to allow requests from any IP address an not only from your local machine.

- `port` (default: `5000`): This parameter specifies the port number on which the server should listen for incoming requests.

- `debug` (default: `False`): We already talked about but note that, in production, it's important to set `debug=False` for 2 main security reasons.

    1. **Exposure of sensitive information**: The interactive debugger can expose sensitive information from your application, including variable values, server configuration, or parts of the source code.

    2. **Arbitrary code execution**: The debugger includes a feature that allows you to execute arbitrary Python code in the context of the server. This means that if an attacker can trigger an error page, they could potentially execute malicious code on your server.

- `options` (optional): This parameter allows you to pass additional options to the underlying server. For example, you can specify an SSL certificate or key file using the `ssl_context` option.


## 3. Routing
Flask uses a system of routes to determine what code to run when a particular URL is accessed. This is done using the `@app.route()` decorator. 

For example, if you want to run a certain piece of code when the user accesses the URL `'http://localhost:5000/hello'`, you would define a route like this:

```python
@app.route('/hello')
def hello():
    return 'Hello, User!'
```
After saving and running your application, when you navigate to `http://localhost:5000/hello` in your web browser, you should see the message "Hello, User!" displayed.

Routes can also contain variable sections, which are specified with angle brackets `< >`. The variable sections are passed as keyword arguments to the function. For example:

```python
@app.route('/hello/<username>')
def show_user_profile(username):
    return 'Hello %s!' % username
```

In this case, if you navigate to `http://localhost:5000/hello/john`, you will see the message `"Hello john"` displayed. The `<username>` section in the route is a variable, and Flask will pass whatever value is in that section of the URL to the `show_user_profile()` function as the `username` argument.

This allows you to create dynamic routes that can display different content based on the URL. You can use any valid Python variable name in your route variables.

## 4. URL Building

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

## 5. HTTP Methods

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

### 5.1 Postman
Postman is a popular API client that makes it easy to test and document APIs. It allows you to send requests to your API and inspect the responses. You can also use it to create and save collections of requests, which can be shared with your team.

You can download Postman from the official website: [https://www.postman.com/](https://www.postman.com/)

### 5.2 Jinja2 Templating
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


## 6. Docker and Flask
Now that you have a basic understanding of Flask, let's see how to run a Flask application in a Docker container.

### 6.1 Dockerfile
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

### 6.2 Building the Docker Image

Open Docker Desktop and make sure that the Docker daemon is running.

To build the Docker image, navigate to the directory containing your `Dockerfile` and run the following command:

```bash
docker build -t my-flask-app .
```

The `-t` flag is used to tag the image with a name, in this case `my-flask-app`. The `.` at the end of the command specifies the build context, which is the current directory.

### 6.3 Running the Docker Container
After building the Docker image, you can run a container from the image using the following command:

```bash
docker run -p 9090:8080 my-flask-app
```

The `-p` flag is used to map the host port to the container port. In this case, the Flask application is running on port 8080 inside the container, and we are mapping it to port 9090 on the host machine.

After running the above command, you should be able to access your Flask application by navigating to `http://localhost:9090` in your web browser.

## 7. Your turn
Now go to the [hugging face website]( https://huggingface.co/tasks ) and use a NLP model to create a new route in your Flask application. For example you can use a text classification model.

You could also use the new gemma-7b model developped by google and create a new route in your Flask application that takes a text as input and returns the response from the model. You can use the `requests` library to make a request to the API and return the response to the user.

**Note:** you need to accept the terms and conditions of Google before using it so if you want to do it with another model please feel free to do it. 

It takes a lot of time to download the model so you can use another model from the hugging face website.

To utilize the model, it's necessary to authenticate with the Hugging Face API. This can be accomplished by executing the following command in your terminal:

```bash
huggingface-cli login
```

After running the command, you will be prompted to enter your acess tokens. You can find them in your Hugging Face account settings.

## 8. Next week 
As said before these LLM models are very powerful but also very heavy when it comes to computation on a cpu. That's why next week, we will see how to use them in a cloud environment. We will use the Google Cloud Platform to deploy our Flask application and use the gemma-7b model to make predictions. :wink:

## Other flask examples applications
- [Flask template](https://github.com/app-generator/flask-template)

## 9. References
- [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/en/3.0.x/)
- [Hugging Face API](https://huggingface.co/api)
- [Flask tutorial](https://www.tutorialspoint.com/flask/index.htm)
- [Flask tutorial 2](https://auth0.com/blog/developing-restful-apis-with-python-and-flask/)







    



    





 






