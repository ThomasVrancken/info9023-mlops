FROM pytorch/pytorch:latest

WORKDIR /deep_app

COPY . .

RUN pip install -r /deep_app/model-training/requirements.txt

#To test the the model_training.py service alone uncoment the CMD below
#CMD ["python", "model-training/model_training.py"]