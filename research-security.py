import requests
import pandas as pd
import time
import os
import json

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

def get_author_metadata(orcid):
    url = f"https://api.openalex.org/authors/ORCID:{orcid}"
    response = requests.get(url, params={'mailto': 'rjgc.richard@gmail.com'})
    
    if response.status_code != 200:
        return None

    data = response.json()
    return {
        'orcid': orcid,
        'works_count': data.get('works_count'),
        'cited_by_count': data.get('cited_by_count'),
        'last_known_institution': data.get('last_known_institution', {}).get('display_name'),
        'h_index': data.get('summary_stats', {}).get('h_index'),
        'display_name': data.get('display_name'),
    }


BASE_URL = 'https://api.openalex.org/works'

# Parameters
params = {
    'filter': 'publication_year:2024,authorships.institutions.country_code:cn|ru|ir|kp',
    'mailto': 'rjgc.richard@gmail.com',  
    'per_page': 5
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
            name = author_info.get('display_name')
            orcid = author_info.get('orcid')
            authors.append((name, orcid))
        
        if a.get('institutions'):
            for inst in a.get('institutions'):
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

unique_orcids = author_risk_df['orcid'].dropna().unique()

metadata_file = 'author_metadata.json'

if os.path.exists(metadata_file):
    with open(metadata_file, 'r') as f:
        saved_metadata = json.load(f)
else:
    saved_metadata = []
    
saved_metadata_dict = {item['orcid']: item for item in saved_metadata}

unique_orcids = [o for o in unique_orcids if o]
orcids_to_fetch = [o for o in unique_orcids if o not in saved_metadata_dict]

for orcid in orcids_to_fetch:
    metadata = get_author_metadata(orcid)
    if metadata:
        saved_metadata_dict[orcid] = metadata
    time.sleep(1)

updated_metadata_list = list(saved_metadata_dict.values())

with open(metadata_file, 'w') as f:
    json.dump(updated_metadata_list, f, indent=2)

author_metadata_df = pd.DataFrame(updated_metadata_list)
merged_df = author_risk_df.merge(author_metadata_df, on='orcid', how='left')

print(merged_df.sort_values('average_score', ascending='False'))