import urllib.request
import xml.etree.ElementTree as ET

url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=7713511"
try:
    print("Fetching XML from eutils...")
    with urllib.request.urlopen(url) as response:
        xml_data = response.read()
    print("Success. Size of XML:", len(xml_data))
    
    # Save a small snippet
    with open("scratch/pmc_test.xml", "wb") as f:
        f.write(xml_data)
    print("Saved to scratch/pmc_test.xml")
except Exception as e:
    print("Error:", e)
