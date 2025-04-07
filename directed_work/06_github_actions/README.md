# Directed work 6 [Sprint 6, W11]: GitHub Actions

# O. Description
GitHub Actions is a CI/CD tool that allows you to automate your software development workflows. It enables you to build, test, and deploy your code directly from your GitHub repository. With GitHub Actions, you can create custom workflows that are triggered by specific events, such as pushing code to a repository or creating a pull request.

GitHub Actions is integrated with GitHub, making it easy to set up and manage your workflows without needing to use external CI/CD tools.

# 1. How to use GitHub Actions

To use GitHub Actions, you need to first create a `.github/workflows` directory in your repository. In this directory you need to create one or more YAML files that define your workflows. Each workflow file can contain one or more jobs, which are the individual tasks that will be executed as part of the workflow.

You can configure a GitHub Actions workflow to be triggered by specific events, such as pushes, pull requests, issue comments or scheduled events. You can also define conditions for when a job should run, such as only running on specific branches or when certain files are changed.

# 2. Workflows

A workflow contains one or more jobs that run in parallel or sequentially. Each job runs inside its own virtual environment or container. Each job runs an action or a script. 

You can either use predefined actions from the GitHub Marketplace or create your own custom actions. You can also define job's dependencies to run after another job has completed in the same workflow.

# 3. Pytest

Pytest is a testing framework for Python that makes it easy to write simple and scalable test cases. It is widely used in the Python community and is known for its simplicity and flexibility.
To use pytest, you first need to install it. 
```bash
pip install pytest
```
Once it is installed, you can write test functions using the `assert` statement and save them in a file with the name `test_<your_module>.py`.

You can the run the tests using the command:
```bash
pytest
```

This is really useful and will even be mandatory if you begin a project in your future work.

# 3.1. Example of a pytest test

For example, if you have a really simple functions that does addition:
```python
def add(a, b):
    return a + b
```
You can write a test for this function like this:
```python
def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```
You can save this test in a file called `test_add.py` and run it using pytest:
```bash
pytest test_add.py
```
This will run the test and report any failures.

# 4. Example of a workflow

Now, we will write a simple workflow that runs pytest on every push and pull requests to the main branch. This workflow will also run pre-commit hooks to check for code quality and formatting issues before running the tests.

```yaml
name: Python CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
    pre-commit:
        runs-on: ubuntu-latest
    
        steps:
            - uses: actions/checkout@v4
            - name: Run pre-commit hooks
              uses: pre-commit/action@v3.0.1
              with:
                extra_args: --all-files --config pre_commit.yml

    pytest:
        runs-on: ubuntu-latest
        needs: pre-commit

        steps:
            - name: Checkout code
              uses: actions/checkout@v4

            - name: Set up Python
              uses: actions/setup-python@v5
              with:
                python-version: '3.11'

            - name: Install dependencies
              run: |
                python -m pip install --upgrade pip install pytest
                pip install -r requirements.txt

            - name: Run tests
              run: |
                pytest tests/
```

# 5. Your turn

What we ask you to do now is to create a GitHub Actions workflow that runs pytest on every push and pull request to the main branch. This workflow should also run pre-commit hooks to check for code quality and formatting issues before running the tests.

For the 21st of March, you should have created a pytest test for one of your project functions and a GitHub Actions workflow that runs pytest on every push and pull request to the main branch. This workflow should also run pre-commit hooks to check for code quality and formatting issues before running the tests.
We will want you to push some code to your GitHub repository and create a pull request to test the workflow.

What we will check is to see if the workflow has run successfully and if the tests have passed. We will also check if the pre-commit hooks have run successfully and if there are any code quality or formatting issues.