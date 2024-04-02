FROM python:3.9-slim

WORKDIR /deep_app

ENV FLASK_APP=data_preprocessing.py

# Copy the data-preprocessing folder which is in the parent directory into the container
COPY . .

# Install the required libraries
RUN pip install -r /deep_app/data-preprocessing/requirements.txt

#To test the the data_preprocessing.py service alone decoment the CMD below and uncomment the CMD below
#CMD ["python", "data-preprocessing/data_preprocessing.py"]
