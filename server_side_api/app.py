from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import numpy as np
import pandas as pd
import tldextract
import re
from tensorflow.keras.models import load_model


app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/check_phishing', methods=['POST'])
def check_phishing():
    data = request.get_json()
    url = data.get('url')
    is_phishing = is_phishing_url(url)
    return jsonify({'url': url, 'is_phishing': is_phishing})

def is_phishing_url(url):
    with open('preprocessor.pkl', 'rb') as f:
        preprocessor = pickle.load(f)
    model = load_model('surfhound.h5')

    # Preprocess the URL
    df = pd.DataFrame([[url, None ]], columns=['url','label'])
    X = preprocessor.transform(df)
    
    # make a prediction
    prediction = model.predict(X)

    # Return True if the URL is predicted to be phishing, False otherwise
    if prediction[0][0] < 0.5:
      return True
    else:
        return False

if __name__ == "__main__":
    app.run(host='localhost', port=5000)