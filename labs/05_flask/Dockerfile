# Use the official image as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /src

# Copy our files in the container
COPY /src/hello.py .
COPY /src/requirements.txt .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Define environment variable
ENV FLASK_APP=hello.py

# Run hello.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]