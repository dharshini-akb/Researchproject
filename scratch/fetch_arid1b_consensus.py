import urllib.request
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

pmcid = "6752273"
url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&retmode=xml"
dest_path = f"scratch/pmc_{pmcid}.xml"

print(f"Downloading PMC{pmcid} XML...")
try:
    with urllib.request.urlopen(url) as response:
        xml_data = response.read()
    with open(dest_path, "wb") as f:
        f.write(xml_data)
    print("Success. File size:", len(xml_data))
    
    # Let's inspect the tables in this XML
    tree = ET.parse(dest_path)
    root = tree.getroot()
    
    tables = root.findall(".//table-wrap")
    print(f"Found {len(tables)} tables.")
    
    def element_to_text(el):
        return "".join(el.itertext()).strip() if el is not None else ""
        
    for i, tw in enumerate(tables):
        label = element_to_text(tw.find("label"))
        caption = element_to_text(tw.find("caption"))
        print(f"\nTable {i+1}: {label} - {caption[:200]}")
        table_el = tw.find(".//table")
        if table_el is not None:
            rows = table_el.findall(".//tr")
            print("Rows count:", len(rows))
            # print first 5 rows
            for tr_idx, tr in enumerate(rows[:5]):
                cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
                print(f"  Row {tr_idx}: {cells[:10]}")
except Exception as e:
    print("Error:", e)
