import xml.etree.ElementTree as ET
import os
import re

xml_path = r"d:\finalresearchproject\scratch\pmc_9180463.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

text = "".join(root.itertext())
print("Total text length:", len(text))

# Search for PT1, PT2, PT3, etc.
for pt in ["PT1", "PT2", "PT3", "PT4", "PT5", "PT12"]:
    matches = [m.start() for m in re.finditer(pt, text)]
    print(f"Occurrences of {pt}: {len(matches)}")
    if matches:
        print(f"Sample around first occurrence of {pt}:")
        idx = matches[0]
        print(text[max(0, idx-100):min(len(text), idx+200)])
        print("-" * 50)
