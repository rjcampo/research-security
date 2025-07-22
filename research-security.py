import requests
import pandas as pd

BASE_URL = 'https://api.openalex.org/works'

# Parameters
params = {
    'filters': 'publication_year:2024',
    'mailto': 'rjgc.richard@gmail.com',
    'per_page': 25
}

# Request
response = requests.get(BASE_URL, params=params)
works = response.json()['results']

data = pd.DataFrame(works)

print(data.head())