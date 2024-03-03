# The following line will download a Docker image that already is set up with python 3.12, so that we can run our
# simple application. 
FROM python:3.12

# Copy our files over to the Docker container.
COPY hello_world.py .
COPY requirements.txt .

# Make port 8080 available to the world outside this container.
EXPOSE 8080

# Download and install depedencies (libraries)
RUN pip install -r requirements.txt

# Define environment variable
ENV FLASK_APP=hello_world.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
