import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import tldextract
import re
import pickle
from tensorflow.keras.models import load_model

class Preprocessor:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.scaler = StandardScaler()
        self.sequences_len = None

    def fit(self, df):
        urls = df['url']

        # Tokenizing the URLs
        print("Tokenizing the URLs...")
        self.tokenizer.fit_on_texts(urls)
        sequences = self.tokenizer.texts_to_sequences(urls)
        self.sequences_len = max([len(seq) for seq in sequences]) # measure the maximum number of pad sequences
        sequences = pad_sequences(sequences, maxlen=self.sequences_len) # set the maximum length
        # Extract features
        print("Extracting features...")
        features = self.extract_features(df)

        print("concatenating all features")
        all_data = np.concatenate([sequences, features], axis=1)
        
        # Scale the data
        self.scaler.fit(all_data)
        return

    def transform(self, df):
        urls = df['url']
        tlds = urls.apply(lambda x: tldextract.extract(x).suffix)
        # Tokenizing the URLs
        print("Tokenizing the URLs...")
        sequences = self.tokenizer.texts_to_sequences(urls)
        sequences = pad_sequences(sequences, maxlen=self.sequences_len) # set the maximum length
        
        # Extract features
        print("Extracting features...")
        features = self.extract_features(df)

        print("concatenating all features")
        all_data = np.concatenate([sequences, features], axis=1)

        # Scale the data
        return self.scaler.transform(all_data)

    def fit_transform(self, df):
        self.fit(df)
        return self.transform(df)
        

    def extract_features(self, df):
        df['url_length'] = df['url'].apply(len)
        df['num_digits'] = df['url'].apply(lambda x: sum(c.isdigit() for c in x))
        df['num_letters'] = df['url'].apply(lambda x: sum(c.isalpha() for c in x))
        df['num_special_chars'] = df['url'].apply(lambda x: len(re.findall('[^a-zA-Z0-9]', x)))
        df['num_dots'] = df['url'].apply(lambda x: x.count('.'))
        df['num_slashes'] = df['url'].apply(lambda x: x.count('/'))
        df['num_hyphens'] = df['url'].apply(lambda x: x.count('-'))

        # Additional features
        df['num_subdomains'] = df['url'].apply(lambda x: x.count('.'))
        df['has_https'] = df['url'].apply(lambda x: 1 if x.startswith('https://') else 0)
        df['tld_length'] = df['url'].apply(lambda x: len(tldextract.extract(x).suffix) if '.' in x else 0)
        df['has_ip'] = df['url'].apply(lambda x: 1 if re.match(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", x) else 0)
        df['has_redirects'] = df['url'].apply(lambda x: 1 if '//' in x else 0)

        return np.array(df.drop(columns=['url', 'label']))


def is_phishing_url(url):
    # Load the preprocessor and the model
    with open('preprocessor.pkl', 'rb') as f:
        preprocessor = pickle.load(f)
    model = load_model('surfhound.h5')

    # Preprocess the URL
    df = pd.DataFrame([[url, None ]], columns=['url','label'])
    X = preprocessor.transform(df)
    print(df)

    # Make a prediction
    prediction = model.predict(X)

    # Return True if the URL is predicted to be phishing, False otherwise
    if prediction[0][0] < 0.5:
      return True
    else:
      return False