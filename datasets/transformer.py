import pandas as pd

# Load the new dataset
new_data = pd.read_csv('test.txt', sep='\t', header=None, names=['label', 'url'])

# Map the labels to match the old dataset
label_mapping = {'phishing': 'bad', 'legitimate': 'good'}
new_data['label'] = new_data['label'].map(label_mapping)

# Reorder the columns to match the old dataset
new_data = new_data[['url', 'label']]

# Save the transformed dataset
new_data.to_csv('phishing_site_urls.csv', index=False)