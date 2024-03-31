FROM nvidia/cuda:12.3.2-devel-ubi8
FROM python:3.9-slim

WORKDIR /deep_app

COPY . .

RUN pip install -r /deep_app/model-serving/requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "model_server:app"]