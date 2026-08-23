import xml.etree.ElementTree as ET
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

def element_to_text(el):
    return "".join(el.itertext()).strip() if el is not None else ""

# 1. White-Sutton
print("\n--- WHITE-SUTTON (PMC7713511) ---")
tree = ET.parse("scratch/pmc_7713511.xml")
root = tree.getroot()

for i, tw in enumerate(root.findall(".//table-wrap")):
    label = element_to_text(tw.find("label"))
    caption = element_to_text(tw.find("caption"))
    print(f"\nTable wrap {i+1}: {label} - {caption[:100]}")
    table = tw.find(".//table")
    if table is not None:
        rows = []
        for tr in table.findall(".//tr"):
            row = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            rows.append(row)
        print("Rows count:", len(rows))
        for r in rows[:10]:
            print(r)

# 2. Xia-Gibbs
print("\n--- XIA-GIBBS (PMC6231716) ---")
tree = ET.parse("scratch/pmc_6231716.xml")
root = tree.getroot()
for i, tw in enumerate(root.findall(".//table-wrap")):
    label = element_to_text(tw.find("label"))
    caption = element_to_text(tw.find("caption"))
    print(f"\nTable wrap {i+1}: {label} - {caption[:100]}")
    table = tw.find(".//table")
    if table is not None:
        rows = []
        for tr in table.findall(".//tr"):
            row = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            rows.append(row)
        print("Rows count:", len(rows))
        for r in rows[:10]:
            print(r)
