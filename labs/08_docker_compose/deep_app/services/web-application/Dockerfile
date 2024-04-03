# Base image for Python environment (adjust based on your requirements)
FROM python:3.9-slim

# Set working directory
WORKDIR /app

COPY ./services/web-application/ .
COPY ../../model/ ./model
COPY ../../data/ ./data

RUN pip install -r requirements.txt

# Expose the port where the Flask app runs (usually 5000)
#EXPOSE 5002

# Run the Flask app using Gunicorn (production server)
#CMD ["gunicorn", "--bind", "0.0.0.0:5002", "web-application.app:app"]
