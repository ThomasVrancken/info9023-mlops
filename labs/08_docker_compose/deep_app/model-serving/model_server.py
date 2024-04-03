import sys
import torch
import torch.nn as nn
from flask import Flask, request, jsonify

# adding Folder_2 to the system path
sys.path.insert(0, '/deep_app/model/')
from model import Model

app = Flask(__name__)

# Load the trained model
model = Model(input_dim=13)
model.load_state_dict(torch.load('/deep_app/model/model.pth'))
model.eval()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    X = torch.tensor(data['X'], dtype=torch.float32)
    with torch.no_grad():
        output = model(X)
    print('Prediction:', output.item())
    return jsonify({'prediction': output.item()})

if __name__ == '__main__':
    app.run(debug=True)
