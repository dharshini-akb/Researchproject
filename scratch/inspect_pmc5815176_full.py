import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse("scratch/pmc_5815176.xml")
root = tree.getroot()

# Search for supplementary material links or text
supp_elements = root.findall(".//supplementary-material")
print(f"Found {len(supp_elements)} supplementary-material elements.")
for s in supp_elements:
    print("Element:", ET.tostring(s, encoding='utf-8').decode('utf-8'))

# Let's inspect Table 3 fully
t3 = root.find(".//table-wrap[label='Table 3']")
if t3 is not None:
    print("\n--- TABLE 3 FULL ---")
    table = t3.find(".//table")
    if table is not None:
        for r_idx, tr in enumerate(table.findall(".//tr")):
            cells = ["".join(cell.itertext()).strip() for cell in tr.findall(".//td") + tr.findall(".//th")]
            print(f"Row {r_idx}: {cells}")
