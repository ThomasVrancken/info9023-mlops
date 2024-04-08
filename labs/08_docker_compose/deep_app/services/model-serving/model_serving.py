import torch
from flask import Flask, request, jsonify

from model.model import Model

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    # Load the trained model
    model = Model(input_dim=13)
    model.load_state_dict(torch.load('./model/model.pth'))
    model.eval()
    data = request.get_json(force=True)
    X = torch.tensor(data['X'], dtype=torch.float32)
    with torch.no_grad():
        output = model(X)
    print('Prediction:', output.item())
    return jsonify({'prediction': output.item()})

if __name__ == '__main__':
    app.run(debug=True)
