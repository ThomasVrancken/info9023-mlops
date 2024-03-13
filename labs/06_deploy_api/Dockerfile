FROM python:3.9-slim

# set the environment variable to ensure that the python output is set straight and not buffered
ENV PYTHONUNBUFFERED True

# set the working directory in the container
WORKDIR /src

#copy all files from the current directory to the container
COPY /src/hello.py .
COPY /src/requirements.txt .

ENV PORT 5001

#install the requirements
RUN pip install -r requirements.txt

# Define environment variable to tell the container where the app is (i.e. the file to run)
ENV FLASK_APP=hello.py

# Run hello.py when the container launches
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 hello:app