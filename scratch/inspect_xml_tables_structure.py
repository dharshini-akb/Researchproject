import xml.etree.ElementTree as ET
import os

SCRATCH_DIR = r"d:\finalresearchproject\scratch"

def element_to_text(el):
    return "".join(el.itertext()).strip() if el is not None else ""

def print_table_details(xml_filename):
    path = os.path.join(SCRATCH_DIR, xml_filename)
    if not os.path.exists(path):
        print(f"Missing {xml_filename}")
        return
    tree = ET.parse(path)
    root = tree.getroot()
    print("=" * 70)
    print(f"FILE: {xml_filename}")
    tables = root.findall(".//table-wrap")
    for t_idx, tw in enumerate(tables):
        caption = element_to_text(tw.find("caption"))
        table = tw.find(".//table")
        if table is None: continue
        rows = table.findall(".//tr")
        print(f"\n--- Table {t_idx+1}: {caption[:100]} (Rows: {len(rows)}) ---")
        for r_idx, tr in enumerate(rows[:10]):
            cells = [element_to_text(c).replace("\n", " ") for c in tr.findall(".//th") + tr.findall(".//td")]
            print(f"Row {r_idx:2d} ({len(cells)} cols): {cells[:7]}")

print_table_details("pmc_4702300_ws_white2016.xml")
print_table_details("pmc_4850885_ws_ye2015.xml")
print_table_details("pmc_4850891_xg_yang2015.xml")
print_table_details("pmc_8694554_xg_khayat2021.xml")
print_table_details("pmc_6465669_xg_cheng2019.xml")
