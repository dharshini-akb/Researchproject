import xml.etree.ElementTree as ET
import os

xml_path = r"d:\finalresearchproject\scratch\pmc_9180463.xml"
if not os.path.exists(xml_path):
    print("Not found")
    exit()

tree = ET.parse(xml_path)
root = tree.getroot()

tables = root.findall(".//table-wrap")
print("Found tables:", len(tables))

def element_to_text(el):
    return "".join(el.itertext()).strip() if el is not None else ""

for i, tw in enumerate(tables):
    label = element_to_text(tw.find("label"))
    caption = element_to_text(tw.find("caption"))
    print(f"\nTable {i+1}: {label} - {caption[:100]}")
    t = tw.find(".//table")
    if t is not None:
        rows = t.findall(".//tr")
        print("Rows count:", len(rows))
        for r_idx, tr in enumerate(rows[:5]):
            cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            print(f"  Row {r_idx}: {cells[:10]}")
