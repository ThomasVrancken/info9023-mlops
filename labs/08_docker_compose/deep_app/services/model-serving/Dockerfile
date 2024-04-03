FROM nvidia/cuda:12.3.2-devel-ubi8
FROM python:3.9-slim

WORKDIR /app

COPY ./services/model-serving/ .
COPY ../../model/ ./model

RUN pip install -r requirements.txt

#CMD ["gunicorn", "model_server:app"]