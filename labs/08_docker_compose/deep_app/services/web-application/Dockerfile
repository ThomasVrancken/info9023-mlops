FROM python:3.9-slim

# Set working directory
WORKDIR /app

COPY ./services/web-application/ .
COPY ../../model/ ./model
COPY ../../data/ ./data

RUN pip install -r requirements.txt
