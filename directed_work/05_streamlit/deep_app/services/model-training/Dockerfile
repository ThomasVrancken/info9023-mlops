FROM pytorch/pytorch:latest

WORKDIR /app

COPY ./services/model-training/ .
COPY ../../model/ ./model
COPY ../../data/ ./data

RUN pip install -r requirements.txt