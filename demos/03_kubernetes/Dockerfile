# Use the slim variant of Python 3.12 which is much smaller but still includes
# essential Python functionality
FROM python:3.12-slim

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
