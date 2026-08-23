import urllib.request
import os

pmc_ids = {
    "White-Sutton": "7713511",
    "Xia-Gibbs": "6231716",
    "CdLS": "4902018"
}

for name, pmcid in pmc_ids.items():
    dest_path = f"scratch/pmc_{pmcid}.xml"
    if os.path.exists(dest_path):
        print(f"{name} (PMC{pmcid}) already downloaded.")
        continue
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&retmode=xml"
    print(f"Downloading {name} (PMC{pmcid}) from {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
        with open(dest_path, "wb") as f:
            f.write(xml_data)
        print(f"Saved {name} XML. Size: {len(xml_data)} bytes")
    except Exception as e:
        print(f"Error downloading {name}: {e}")
