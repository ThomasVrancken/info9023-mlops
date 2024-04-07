FROM python:3.9-slim

WORKDIR /app

# Copy the data-preprocessing folder which is in the parent directory into the container
COPY ./services/data-preprocessing/ .
COPY ../../data/ ./data

# Install the required libraries
RUN pip install -r requirements.txt
