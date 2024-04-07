import requests
import torch

from flask import Flask, request, jsonify, render_template
from subprocess import run

# adding Folder_2 to the system path
#sys.path.insert(0, '/deep_app/model/')
from model.model import Model

app = Flask(__name__)

# Load the model
model = Model(13)  # replace with the number of input features
model.load_state_dict(torch.load('./model/model.pth'))
model.eval()

#Data preprocessing endpoint (triggeres preprocessing.py)
@app.route('/preprocess_data', methods=['POST'])
def process_data():
    response = requests.post('http://data-processing:5004/preprocess')  # replace with the correct URL
    if response.status_code == 200:
        result = response.json()['result']  # get the result from the JSON response
        return "Data preprocessing done. Result: " + str(result)
    else:
        return "Data preprocessing failed", 500

#Model training endpoint (triggeres model_training.py)
@app.route('/train_model', methods=['POST'])
def train_model():
    #get learning rate provided by the user. Default to 0.001 if not provided
    learning_rate = float(request.form.get('learning_rate', 0.001))
    #get number of epochs provided by the user. Default to 10 if not provided
    num_epochs = int(request.form.get('num_epochs', 10))

    # Make a POST request to the /train route in model_training.py 
    #       with the learning rate and number of epochs
    response = requests.post('http://model-training:5003/train', 
                             json={'learning_rate': learning_rate, 
                                   'num_epochs': num_epochs})

    # Check if the request was successful
    if response.status_code == 200:
        return 'Model trained with learning rate {} and {} \
            epochs'.format(learning_rate, num_epochs)
    else:
        return 'Error: {}'.format(response.content), response.status_code

@app.route('/predict', methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    # Make a POST request to the /predict route in another Flask app
    response = requests.post('http://model-serving:5001/predict', json=data)

    # Check if the request was successful
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return 'Error: {}'.format(response.content), response.status_code

# Home page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)