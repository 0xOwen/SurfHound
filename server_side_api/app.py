from flask import Flask, request, jsonify
import pickle
from tensorflow.keras.models import load_model
import pandas as pd
from database import db, URLStat

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/check_url', methods=['POST'])
def check_url():
    url = request.json.get('url')
    ip_address = request.remote_addr

    # Ignore URLs that start with 'chrome://', 'about:', 'file:', 'data:', or 'javascript:'
    if url.startswith(('chrome://', 'about:', 'file:', 'data:', 'javascript:')):
        return jsonify({'message': 'Ignored URL'}), 200

    is_phishing = is_phishing_url(url)

    # save the URL and its classification to the database
    url_stat = URLStat(url=url, is_phishing=1 if is_phishing else 0, ip_address=ip_address)
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
    
    # make a prediction
    prediction = model.predict(X)

    # Return True if the URL is predicted to be phishing, False otherwise
    return bool(prediction[0][0] < 0.5)

if __name__ == "__main__":
    app.run(host='localhost', port=5000)