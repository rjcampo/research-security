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
            country = inst.get('country_code')
            name = inst.get('display_name')
            
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
    'per_page': 200
}

# Request
response = requests.get(BASE_URL, params=params)
results = response.json()['results']

scored_data = []

for paper in results:
    authors = []
    institutions = []
    
    for a in paper['authorships']:
        if a.get('author'):
            author_info = a.get('author')
            name = author_info['display_name']
            orcid = author_info['orcid']
            authors.append((name, orcid))
        
        if a.get('institutions'):
            for inst in a['institutions']:
                name = inst.get('display_name')
                institutions.append(name)
    
    pubs_data = {
        'title': paper['title'],
        'authors': authors,
        'institutions': institutions,
        'year': paper['publication_year'],
        'score': risk_calc(paper)
    }
    scored_data.append(pubs_data)
    
author_risks = {}

for paper in scored_data:
    authors = paper['authors']
    score = paper['score']
    
    for author in authors:
        if author not in author_risks:
            author_risks[author] = {
                'total_score': 0,
                'num_papers': 0
            }
        author_risks[author]['total_score'] += score
        author_risks[author]['num_papers'] += 1

author_risk_list = []

for (name, orcid), data in author_risks.items():
    author_dict = {
        'name': name,
        'orcid': orcid,
        'total_score': data['total_score'],
        'num_papers': data['num_papers'],
        'average_score': data['total_score'] / data['num_papers']
    }
    author_risk_list.append(author_dict)

author_risk_df = pd.DataFrame(author_risk_list)

author_risk_df = author_risk_df.sort_values(by='average_score', ascending=False)

print(author_risk_df.head())