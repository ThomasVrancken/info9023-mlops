# Use the official Python image as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY  ./src .

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Define environment variable to tell the container where the app is (i.e. the file to run)
ENV FLASK_APP=app.py

# Run app.py when the container launches

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]