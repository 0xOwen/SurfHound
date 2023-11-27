from flask import Flask, request, jsonify, render_template
import pickle
from tensorflow.keras.models import load_model
import pandas as pd
from database import db, URLStat
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from collections import Counter
from operator import itemgetter
from urllib.parse import urlparse
import re
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)
admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(URLStat, db.session))

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

@app.route('/dashboard')
def dashboard():
    #fetch data from db
    data = URLStat.query.all()

    chart_data = convert_to_chartjs_format(data)
    
    return render_template('dashboard.html', data=chart_data)

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

def convert_to_chartjs_format(data):
    # Number of phishing vs legitimate URLs
    phishing_count = sum(1 for d in data if d.is_phishing)
    non_phishing_count = sum(1 for d in data if not d.is_phishing)

    url_type_data = {
        'labels': ['Phishing', 'Non-Phishing'],
        'datasets': [{
            'data': [phishing_count, non_phishing_count],
            'backgroundColor': ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'],
            'borderColor': ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'],
            'borderWidth': 1
        }]
    }

    # Top phishing IP addresses
    ip_counts = Counter(d.ip_address for d in data if d.is_phishing and d.ip_address)
    top_ips = ip_counts.most_common(5)  # Get the 5 most common IPs

    ip_data = {
        'labels': [ip for ip, count in top_ips],
        'datasets': [{
            'data': [count for ip, count in top_ips],
            'backgroundColor': [generate_random_color() for _ in top_ips]
        }]
    }

    # Phishing URLs over time
    dates = [d.timestamp.date() for d in data if d.is_phishing]
    date_counts = Counter(dates)

    time_data = {
        'labels': sorted(date_counts),
        'datasets': [{
            'data': [date_counts[date] for date in sorted(date_counts)],
            'fill': False,
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        }]
    }

    # Most frequent phishing URLs
    url_counts = Counter(d.url for d in data if d.is_phishing)
    top_urls = url_counts.most_common(5)  # Get the 5 most common URLs

    url_data = {
        'labels': [url for url, count in top_urls],
        'datasets': [{
            'data': [count for url, count in top_urls],
            'backgroundColor': [generate_random_color() for _ in top_urls]
        }]
    }

    # Phishing activity by hour of the day
    hours = [d.timestamp.hour for d in data if d.is_phishing]
    hour_counts = Counter(hours)

    hour_data = {
        'labels': list(range(24)),
        'datasets': [{
            'data': [hour_counts[hour] for hour in range(24)],
            'fill': False,
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        }]
    }

    # Top-Level Domain (TLD) Distribution
    tld_counts = Counter(urlparse(d.url).netloc.split('.')[-1] for d in data if d.is_phishing)
    tld_data = {
        'labels': list(tld_counts.keys()),
        'datasets': [{
            'data': list(tld_counts.values()),
            'backgroundColor': [generate_random_color() for _ in tld_counts]
        }]
    }

    # URL Length Distribution
    url_lengths = [len(d.url) for d in data if d.is_phishing]
    length_data = {
        'labels': sorted(set(url_lengths)),
        'datasets': [{
            'data': [url_lengths.count(length) for length in sorted(set(url_lengths))],
            'backgroundColor': [generate_random_color() for _ in url_lengths]
        }]
    }

    # Most Common Words in Phishing URLs
    words = re.findall(r'\w+', ' '.join(d.url for d in data if d.is_phishing))
    word_counts = Counter(words)
    word_data = word_counts.most_common(100)  # Get the 100 most common words

    return url_type_data, ip_data, time_data, url_data, hour_data, tld_data, length_data, word_data

def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r},{g},{b})'


if __name__ == "__main__":
    app.run(host='localhost', port=5000)