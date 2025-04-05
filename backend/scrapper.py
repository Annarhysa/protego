import os
import requests

# Define the URL of the dataset (Replace with actual dataset link)
dataset_url = '#'

# Define the directory and filename
save_dir = 'scrape_data'
os.makedirs(save_dir, exist_ok=True)  # Create directory if it doesn't exist
local_filename = os.path.join(save_dir, 'crime_data.csv')

# Download and save the dataset
response = requests.get(dataset_url)
if response.status_code == 200:
    with open(local_filename, 'wb') as file:
        file.write(response.content)
    print(f'Dataset saved at {local_filename}')
else:
    print(f'Failed to download dataset. Status code: {response.status_code}')
