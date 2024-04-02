import sys
import torch

from flask import Flask, request, jsonify, render_template
from subprocess import run

# adding Folder_2 to the system path
sys.path.insert(0, '/deep_app/model/')
from model import Model

app = Flask(__name__)

# Load the model
model = Model(13)  # replace with the number of input features
model.load_state_dict(torch.load('/deep_app/model/model.pth'))
model.eval()

#Data preprocessing endpoint (triggeres preprocessing.py)
@app.route('/preprocess_data', methods=['POST'])
def process_data():
    run(['python', 'data-preprocessing/data_preprocessing.py'])
    return "Data preprocessing done"

#Model training endpoint (triggeres model_training.py)
@app.route('/train_model', methods=['POST'])
def train_model():
    run(['python', 'model-training/model_training.py'])
    return "Model trained"

@app.route('/predict', methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    X = torch.tensor(data['input'], dtype=torch.float32)
    # Make prediction using model loaded from disk as per the data.
    with torch.no_grad():
        prediction = model(X)
    return jsonify(prediction.item())

# Home page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)