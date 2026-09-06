import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import time

WORKSPACE_DIR = r"d:\finalresearchproject"
SCRATCH_DIR = os.path.join(WORKSPACE_DIR, "scratch")

# Test NCBI e-fetch for key PMIDs
pmids_to_fetch = [
    # White-Sutton syndrome
    ("31782611", "Batzir_2020_PMC7713511"),
    ("35052493", "Tan_2022_PMC8771146"),
    ("33277917", "Ferretti_2021"),
    ("34645992", "Drivas_2021"),
    ("26942287", "Stessman_2016_PMC4862413"),
    ("26739615", "White_2016"),
    ("27148570", "Ye_2016"),
    
    # Xia-Gibbs syndrome
    ("29696776", "Jiang_2018_PMC6231716"),
    ("24791903", "Xia_2014_PMC4014193"),
    ("27148574", "Yang_2016"),
    ("30152016", "Goyal_2018_PMC6105436"),
    ("34950897", "Khayat_2022_PMC8719875"),
    ("35716097", "He_2022_PMC9198642"),
    ("34229113", "Cheng_2021_PMC8256247"),
    ("30729726", "Ritter_2019_PMC6393664"),
    
    # KBG syndrome
    ("35330407", "Gao_2022_PMC8948816"),
    ("27667800", "Low_2016_PMC5435101"),
    ("36446582", "Martinez_2023"),
    ("32767702", "Gnazzo_2020_PMC7496668"),
    ("27783388", "Goldenberg_2016_PMC5379893"),
    ("33804868", "Parenti_2021"),
    ("33671236", "Kutkowska_2021"),
    ("25979630", "Ockeloen_2015_PMC4463503"),
    ("28130835", "Murray_2017_PMC5322971"),
    ("35682590", "Bestetti_2022_PMC9180463")
]

print(f"Testing access to {len(pmids_to_fetch)} target PMIDs...")

results = []
for pmid, label in pmids_to_fetch:
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            doc = data['result'][pmid]
            title = doc.get('title', '')
            source = doc.get('source', '')
            pubdate = doc.get('pubdate', '')
            authors = [a.get('name', '') for a in doc.get('authors', [])]
            pmc = doc.get('articleids', [])
            pmc_id = [x['value'] for x in pmc if x['idtype'] == 'pmc']
            doi = [x['value'] for x in pmc if x['idtype'] == 'doi']
            
            print(f"PMID {pmid} ({label}):")
            print(f"  Title: {title}")
            print(f"  Journal: {source} ({pubdate})")
            print(f"  Authors: {authors[:3]} (Total: {len(authors)})")
            print(f"  PMC: {pmc_id[0] if pmc_id else 'None'}, DOI: {doi[0] if doi else 'None'}")
            print("-" * 50)
            results.append({
                "pmid": pmid,
                "label": label,
                "title": title,
                "journal": source,
                "pubdate": pubdate,
                "first_author": authors[0] if authors else "Unknown",
                "pmc": pmc_id[0] if pmc_id else None,
                "doi": doi[0] if doi else None
            })
    except Exception as e:
        print(f"Error fetching PMID {pmid}: {e}")
    time.sleep(0.35)

with open(os.path.join(SCRATCH_DIR, "pmid_search_results.json"), "w") as f:
    json.dump(results, f, indent=2)

print(f"Saved {len(results)} summary results.")
