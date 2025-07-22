import requests
import pandas as pd

def risk_calc(paper):
    score = 0
    scored_countries = {'cn': 2, 'ru': 2, 'ir': 3, 'kp': 5}
    keywords = ['defense', 'defence', 'surveillance', 'military', 'army'
                'navy', 'air force', 'artificial intelligence', 'quantum',
                'semiconductor', 'microelectronic']

    for author in paper.get('authorships', []):
        inst = author.get('institution', {})
        country = inst.get('country_code')
        name = inst.get("display_name", "").lower()
        
        if country in scored_countries:
            score += scored_countries[country]

        for k in keywords:
            if k in name:
                score += 5
        
        if not author.get('author', {}).get('orcid'):
            score += 1

    return score


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