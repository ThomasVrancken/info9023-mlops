# Lab W10: GitHub Actions for CI/CD

## 0. Overview
In this lab, you will learn how to set up a Continuous Integration and Continuous Deployment (CI/CD) pipeline using GitHub Actions for a Python project. By the end of this lab, you will have a basic understanding of how to automate the build, test, and deployment processes for your projects on GitHub. So the objectives are to set up GitHub Actions for CI/CD and then, define a workflow for building, testing, and deploying a Python project. 

Compared to previous laboratories, this lab is more a hands-on lab. You will follow the instructions here yourself and we will move into the benchess to (try to) help you if you have any issues.

## 1. Linting your code

### 1.1 What is linting?

Linting is the process of running a program that will analyze your code for potential errors, bugs, stylistic issues, and other problems. Linters are tools that can help you find and fix issues in your code before you run it. They can help you catch errors early in the development process and ensure that your code is clean, consistent, and maintainable.

### 1.2 Why lint your code?

Linting your code has several benefits:

1. It helps you catch errors early in the development process.
2. It ensures that your code is clean, consistent, and maintainable.
3. It helps you enforce coding standards and best practices.
4. It can help you identify potential security vulnerabilities in your code.

### 1.3 Popular linters for Python

There are several popular linters for Python that you can use to lint your code:

`Pylint`: Pylint is a tool that checks for codestyle mistakes in Python code, tries to enforce a coding standard like PEP8 and looks for code smells (a code smell is for example a piece of code that is too long, not necessarily wrong, but that could be refactored to make it more readable and maintainable). It can also look for certain type errors, it can recommend suggestions about how particular blocks can be refactored and can offer you details about the code's complexity. This without running the code itself.

To use Pylint, you need to install it first. You can do this by running the following command:

```bash
pip install pylint
```

After installing Pylint, you can run it on your Python code by running the following command:

```bash
pylint <your_python_file>.py
```

This will give you a score for your Python file. The score is based on the Pylint conventions. The score is between 0 and 10. The higher the score, the better the code is.

For example with this bad code snippet:

```python
def   disgusting_code ( ) :
    import random,os
    # This function prints out a random number of stars to the console
    for _ in range(random.randint(1,10)):
        print('*', end=' ')
    print('\n') ; print('This is disgusting code');print('You can\'t even read it')
```

You will get a score of 0.00/10.00. This is because the code is not readable att all and has a lot of issues. The output of Pylint will be:

```bash
************* Module bad_code
bad_code.py:7:0: C0305: Trailing newlines (trailing-newlines)
bad_code.py:1:0: C0114: Missing module docstring (missing-module-docstring)
bad_code.py:1:0: C0116: Missing function or method docstring (missing-function-docstring)
bad_code.py:2:4: C0415: Import outside toplevel (random, os) (import-outside-toplevel)
bad_code.py:2:4: C0410: Multiple imports on one line (random, os) (multiple-imports)
bad_code.py:6:18: C0321: More than one statement on a single line (multiple-statements)
bad_code.py:2:4: W0611: Unused import os (unused-import)

------------------------------------------------------------------
Your code has been rated at 0.00/10 (previous run: 0.00/10, +0.00)
```

But, of course, Pylint can highlight a great number of various other issues like trailing whitespaces, missing spaces around operators, missing spaces after commas, etc. 



`Flake8`: Flake8 is a tool that checks Python code for style and quality issues. It is a wrapper around PyFlakes, pycodestyle, and McCabe. It can be used to enforce a coding standard like PEP8 and look for code smells (a code smell is for example a piece of code that is too long, not necessarily wrong, but that could be refactored to make it more readable and maintainable). It can also look for certain type errors, it can recommend suggestions about how particular blocks can be refactored and can offer you details about the code's complexity. This without running the code itself.

`Ruff`: Ruff stands out with its features and fast execution, making it a wise choice for your development projects.

All these linters have the same goal: to help you write better code but they don't have the same features and the same way to lint your code. So it is up to you to choose the one that fits your needs the best or to use a combination of them.

Next to these linters you can also use a code formatter like `Black`or `autopep8` to format your code. A code formatter is a tool that automatically formats your code to make it PEP8 compliant. It is a great tool to use in your CI/CD pipeline to make sure that all your Python code is formatted correctly.

To use `Black`, you need to install it first. You can do this by running the following command:

```bash
pip install black
```

After installing Black, you can run it on your Python code by running the following command:

```bash
black <your_python_file>.py
```

This will format your Python code to make it PEP8 compliant.

For example with this bad code snippet:

```python
def   disgusting_code ( ) :
    import random,os
    # This function prints out a random number of stars to the console
    for _ in range(random.randint(1,10)):
        print('*', end=' ')
    print('\n') ; print('This is disgusting code');print('You can\'t even read it')
```

After running `Black` on this code snippet, you will get the following code:

```python
def disgusting_code():
    import random, os

    # This function prints out a random number of stars to the console
    for _ in range(random.randint(1, 10)):
        print("*", end=" ")
    print("\n")
    print("This is disgusting code")
    print("You can't even read it")
```

You have other options than Black to format your code like `autopep8` or `yapf`.

Finally, you can use a tool like `MyPy` to check the types in your Python code. MyPy is a static type checker for Python that can help you find type errors in your code before you run it.

## 2. Overview of GitHub Actions
### 2.1. What is GitHub Actions?

GitHub Actions is a feature of GitHub that allows you to automate your software development workflows. With GitHub Actions, you can create custom workflows that build, test, package, release, and deploy your code right from GitHub. You can also use GitHub Actions to automate your workflow based on events that occur in your repository.

### 2.2 How to use GitHub Actions?

To use GitHub Actions, you need to create a `.github/workflows` directory in your repository. In this directory, you can create one or more YAML files that define your workflows. A workflow is a configurable automated process made up of one or more jobs. You can then configure a GitHub Actions workflow to run on specific events, such as pushes, pull requests, or issue comments or you can trigger a workflow manually by scheduling it.

### 2.3 Workflows

A workflow contains one or more jobs that can be run in parallel or sequentially. 
 - Each job runs inside its own virtual machine or container. 
 - Each job run an action or a script. 

A job is a set of steps in a workflow that is executed on the same runner. You can define a job's dependencies to run after another job in the same workflow.

An action is a custom application for GitHub Actions that can be run in a workflow. Actions are the smallest portable building block of a workflow. You can use actions defined in the GitHub Marketplace or create your own actions.

```yaml
name: Python CI

on: [push]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
```
In the above example:

1. `name: Python CI`: The name of the workflow is `Python CI`.
2. `on: [push]`: The workflow is triggered on every push to the repository. You could change this to only trigger it on every pushes on specific branches or tags by using `on: [push]` and `branches: [main]`. You can also only trigger it on pull requests by using `on: [pull_request]`.
3. `jobs`: The workflow contains one job named `build`.
4. `runs-on: ubuntu-latest`: The job runs on the latest version of Ubuntu. You can also use others or even multiple operating systems see [here](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python#excluding-a-version).
5. `steps`: The job consists of four steps:
    - `actions/checkout@v4`: This is an action that checks out your repository onto the runner, allowing you to run scripts or other actions against your code (such as build and test tools). You should use the checkout action any time your workflow will use the repository's code.
    - `actions/setup-python@v4`: It sets up Python 3.x. toegether with the `python-version: '3.x'` flag.
    - `run: |`: This is a multi-line string that contains the commands to be executed in the step. The `|` character is used to indicate a multi-line string.
        - `python -m pip install --upgrade pip`: It upgrades the `pip` package manager.
        - `pip install -r requirements.txt`: It installs the dependencies listed in the `requirements.txt` file. This file should contain the dependencies required by your project.


### 2.4 Your turn

Now it is your turn to create a workflow for your Python project. You can create a new workflow file in the `.github/workflows` directory of your repository and paste the above code into it. You can then commit and push the changes to trigger the workflow.

You are asked here to integrate the linters and formatter in your workflow.

## 3. Pytest

### 3.1 What is Pytest?

Pytest is a testing framework for Python that makes it easy to write simple and scalable tests. It allows you to write test functions using the `assert` statement and provides a rich set of features for writing and running tests. Pytest is widely used in the Python community and is the recommended testing framework for Python projects.

### 3.2 How to use Pytest?

To use Pytest, you need to install it first. You can do this by running the following command:

```bash
pip install pytest
```

After installing Pytest, you can write test functions using the `assert` statement and save them in a file with the name `test_<your_module>.py`. You can then run the tests using the following command:

```bash
pytest
```

This will run all the test functions in the `test_<your_module>.py` file and display the results.

For example, if you have a Python module `math.py` with the following code:

```python
def add(x, y):
    return x + y
```

You can write a test function in a file named `test_math.py` with the following code:

```python
from math import add

def test_add():
    assert add(1, 2) == 3
    assert add(3, 4) == 7
```

You can then run the tests using the following command:

```bash
pytest
```

This will run the test functions in the `test_math.py` file and display the results.

### 3.3 Your turn

Now it is your turn to integrate Pytest in your workflow. You can create a new workflow file in the `.github/workflows` directory. You can then commit and push the changes to trigger the workflow.


## 4. Docker

### 4.1 Your turn

After integrating the linters, formatter, and Pytest in your workflow, you can now integrate Docker in your workflow. You can create a `Dockerfile` in the root directory of your project and build the Docker image as part of the workflow. You can then push the Docker image to a container registry and deploy the image to a container orchestration platform like Google Artifact Registry or Docker Hub.

## 5. Deploy

Again we will use GCP to deploy our application.

### 5.1 Your turn

You are now asked to deploy your application to Google Cloud Platform (GCP) as part of the workflow.

## Resources

- https://docs.github.com/en/actions/quickstart
- https://pypi.org/project/pylint
- https://docs.astral.sh/ruff






