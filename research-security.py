import requests
import pandas as pd
import certifi
print(certifi.where())

BASE_URL = "https://api.openalex.org/works"

# Parameters
params = {
    "mailto": "rjgc.richard@gmail.com",
}

# Request
response = requests.get(BASE_URL, params=params, verify=certifi.where())
data = response.json()

print(data)