import os
import requests
import streamlit as st

# Add a logo
st.sidebar.image('./figures/uliege_faculte_sciencesappliquees_logo.svg', 
                 width=300)



# Data preprocessing endpoint (triggers preprocessing.py)
def process_data():
    response = requests.post('http://data-processing:5004/preprocess')  # replace with the correct URL
    if response.status_code == 200:
        result = response.json()['result']  # get the result from the JSON response
        st.success("Data preprocessing done. Result: " + str(result))
    else:
        st.error("Data preprocessing failed")

# Model training endpoint (triggers model_training.py)
def train_model(learning_rate, num_epochs):
    # Check if the preprocessed data exists
    if not os.path.exists('/data/X_train.csv'):
        st.error('Data is not ready. Please preprocess data first.')
        return

    
    # Make a POST request to the /train route in another Flask app
    response = requests.post('http://model-training:5003/train', 
                             json={'learning_rate': learning_rate, 
                                   'num_epochs': num_epochs})
    # Check if the request was successful
    if response.status_code == 200:
        st.success('Model trained with learning rate {} and {} epochs'.format(learning_rate, num_epochs))
    else:
        st.error('Error: {}'.format(response.content))


def serve_model(features_list):
    # Load the model
    if not os.path.exists('model/model.pth'):
        st.error('Model is not ready. Please train the model first.')

    # Make a POST request to the model serving endpoint
    response = requests.post('http://model-serving:5001/predict', json={'X': features_list})

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the prediction from the response
        prediction = response.json()['prediction']

        # Display the prediction
        st.success(f'Prediction: {prediction}')
    else:
        st.error('Prediction failed.')

# Main function to run the app
def main():
    st.title('California Housing Price application')

    st.subheader('Data Preprocessing')

    if st.button('Preprocess Data', key='preprocess_data'):
        process_data()

    st.subheader('Model Training')

    # Add sliders for learning_rate and num_epochs
    learning_rate = st.slider('Learning Rate', min_value=0.001, max_value=0.1, value=0.01, step=0.001)
    num_epochs = st.slider('Number of Epochs', min_value=1, max_value=10, value=5, step=1)

    if st.button('Train Model', key='train_model'):
        train_model(learning_rate, num_epochs)

    st.subheader('Model Serving')

     # Create input fields for the features
    feature1 = st.number_input('Longitude', value=1.0, step=1.0)
    feature2 = st.number_input('Latitude', value=2.0, step=1.0)
    feature3 = st.number_input('House Median Age', value=3.0, step=1.0)
    feature4 = st.number_input('Total Rooms', value=4.0, step=1.0)
    feature5 = st.number_input('Total Bedrooms', value=5.0, step=1.0)
    feature6 = st.number_input('Population', value=6.0, step=1.0)
    feature7 = st.number_input('Households', value=7.0, step=1.0)
    feature8 = st.number_input('Median Income', value=8.0, step=1.0)
    feature9 = st.number_input('oceam_proximity_<1H OCEAN', value=9.0, step=1.0)
    feature10 = st.number_input('ocean_proximity_INLAND', value=10.0, step=1.0)
    feature11 = st.number_input('oceam_proximity_ISLAND', value=11.0, step=1.0)
    feature12 = st.number_input('oceam_proximity_NEAR BAY', value=12.0, step=1.0)
    feature13 = st.number_input('oceam_proximity_NEAR OCEAN', value=13.0, step=1.0)

    features_list = [feature1, feature2, feature3, feature4, feature5, 
                     feature6, feature7, feature8, feature9, feature10, 
                     feature11, feature12, feature13]

    # Create a button to make predictions
    if st.button('Predict', key='predict'):
        serve_model(features_list)

# Run the app
if __name__ == "__main__":
    main()