import requests
import pandas as pd

def risk_calc(paper):
    score = 0
    scored_countries = {'CN': 2, 'RU': 2, 'IR': 3, 'KP': 5}
    keywords = ['defense', 'defence', 'surveillance', 'military', 'army',
                'navy', 'air force', 'artificial intelligence', 'quantum',
                'semiconductor', 'microelectronic']

    risky_authors = 0
    total_authors = 0

    for author in paper.get('authorships', []):
        total_authors += 1
        institutions = author.get('institutions', [])
        has_scored_country = False

        for inst in institutions:
            country = inst.get('country_code', '').upper()
            name = inst.get('display_name', '').lower()
            
            for k in keywords:
                if k in name:
                    score += 5
                    
            if not has_scored_country and country in scored_countries:
                score += scored_countries[country]
                risky_authors += 1
                has_scored_country = True

    if total_authors > 0:
        proportion = risky_authors / total_authors
        score += proportion * 10
        
    return score


BASE_URL = 'https://api.openalex.org/works'

# Parameters
params = {
    'filter': 'publication_year:2024,authorships.institutions.country_code:cn|ru|ir|kp',
    'mailto': 'rjgc.richard@gmail.com',
    'per_page': 25
}

# Request
response = requests.get(BASE_URL, params=params)
results = response.json()['results']

scored_data = []

for paper in results:
    authors = []
    institutions = []
    
    for a in paper["authorships"]:
        if a.get("author"):
            name = a["author"]["display_name"]
            authors.append(name)
        
        if a.get("institutions"):
            for inst in a["institutions"]:
                name = inst.get("display_name")
                institutions.append(name)
    
    pubs_data = {
        "title": paper["title"],
        "institutions": institutions,
        "year": paper["publication_year"],
        "score": risk_calc(paper)
    }
    scored_data.append(pubs_data)

df = pd.DataFrame(scored_data)

print(df.head())