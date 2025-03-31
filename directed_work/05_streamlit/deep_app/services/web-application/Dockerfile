FROM python:3.9-slim

# Set working directory
WORKDIR /app

COPY ./services/web-application/ .
COPY ./model/ ./model
COPY ./data/ ./data
COPY ./figures/ ./figures
COPY ./services/web-application/.streamlit/ ./.streamlit/

RUN pip install -r requirements.txt
