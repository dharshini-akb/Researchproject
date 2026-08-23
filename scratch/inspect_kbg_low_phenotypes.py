import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse("scratch/pmc_5435101.xml")
root = tree.getroot()

table = root.find(".//table-wrap//table")
if table is not None:
    rows = table.findall(".//tr")
    print("Table I total rows:", len(rows))
    for i, tr in enumerate(rows):
        cells = ["".join(cell.itertext()).strip() for cell in tr.findall(".//td") + tr.findall(".//th")]
        print(f"Row {i:02d}: {cells[:5]} ... (len={len(cells)})")
