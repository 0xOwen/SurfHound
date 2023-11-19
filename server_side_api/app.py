from flask import Flask, request, jsonify
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import numpy as np
import pandas as pd
import tldextract
import re
import os
from database import db, URLStat, User, Admin
from werkzeug.security import generate_password_hash``


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Hash the password for security
    hashed_password = generate_password_hash(password)

    # Create a new User instance
    user = User(username=username, password=hashed_password)

    # Add the new User instance to the session
    db.session.add(user)

    # Commit the session to save the changes
    db.session.commit()

    return jsonify({'message': 'Registered successfully'}), 200
@app.route('/check_phishing', methods=['POST'])
def check_phishing():
    data = request.get_json()
    url = data.get('url')
    # Ignore URLs that start with 'chrome://', 'about:', 'file:', 'data:', or 'javascript:'
    if url.startswith(('chrome://', 'about:', 'file:', 'data:', 'javascript:')):
        return jsonify({'message': 'Ignored URL'}), 200
    is_phishing = is_phishing_url(url)
    # save the URL and its classification to the database
    url_stat = URLStat(url=url, is_phishing=lambda x: 1 if is_phishing else 0)
    db.session.add(url_stat)
    db.session.commit()

    return jsonify({'url': url, 'is_phishing': is_phishing})

def is_phishing_url(url):
    with open('preprocessor.pkl', 'rb') as f:
        preprocessor = pickle.load(f)
    model = load_model('surfhound.h5')

    # Preprocess the URL
    df = pd.DataFrame([[url, None ]], columns=['url','label'])
    X = preprocessor.transform(df)
    print(df)
    
    # make a prediction
    prediction = model.predict(X)

    # Return True if the URL is predicted to be phishing, False otherwise
    if prediction[0][0] < 0.5:
      return True
    else:
        return False

if __name__ == "__main__":
    app.run(host='localhost', port=5000)