import requests
import pandas as pd

BASE_URL = 'https://api.openalex.org/works'

# Parameters
params = {
    'mailto': 'rjgc.richard@gmail.com',
    'per_page': 25
}

# Request
response = requests.get(BASE_URL, params=params)
json = response.json()

works = json['results']

data = pd.DataFrame(works)

print(data.head())