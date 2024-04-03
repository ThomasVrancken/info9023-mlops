FROM pytorch/pytorch:latest

WORKDIR /app

COPY ./model-training/ .
COPY ./model/ ./model
COPY ./data/ ./data

RUN pip install -r requirements.txt

#To test the the model_training.py service alone uncoment the CMD below
#CMD ["python", "model-training/model_training.py"]