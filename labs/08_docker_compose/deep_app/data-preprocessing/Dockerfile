FROM python:3.9-slim

WORKDIR /app

# Copy the data-preprocessing folder which is in the parent directory into the container
COPY ./data-preprocessing/ .
COPY ./data/ ./data

# Install the required libraries
RUN pip install -r requirements.txt

#To test the the data_preprocessing.py service alone decoment the CMD below and uncomment the CMD below
#CMD ["python", "data-preprocessing/data_preprocessing.py"]
