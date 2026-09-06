import xml.etree.ElementTree as ET
import glob
import os

WORKSPACE_DIR = r"d:\finalresearchproject"
SCRATCH_DIR = os.path.join(WORKSPACE_DIR, "scratch")

def element_to_text(el):
    return "".join(el.itertext()).strip() if el is not None else ""

xml_files = [
    # White-Sutton
    "pmc_8775410_ws_tan2022.xml",
    "pmc_4702300_ws_white2016.xml",
    "pmc_4850885_ws_ye2015.xml",
    
    # Xia-Gibbs
    "pmc_4850891_xg_yang2015.xml",
    "pmc_8694554_xg_khayat2021.xml",
    "pmc_9545659_xg_romano2022.xml",
    "pmc_6465669_xg_cheng2019.xml",
    
    # KBG
    "pmc_9180463_kbg_bestetti2022.xml"
]

for xml_name in xml_files:
    path = os.path.join(SCRATCH_DIR, xml_name)
    if not os.path.exists(path):
        continue
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        title = element_to_text(root.find(".//article-title"))
        tables = root.findall(".//table-wrap")
        print("=" * 60)
        print(f"File: {xml_name}")
        print(f"Title: {title}")
        print(f"Table count: {len(tables)}")
        for idx, tw in enumerate(tables):
            label = element_to_text(tw.find("label"))
            caption = element_to_text(tw.find("caption"))
            table = tw.find(".//table")
            row_count = len(table.findall(".//tr")) if table is not None else 0
            print(f"  Table [{idx+1}] Label: '{label}' | Caption: '{caption[:80]}...' | Rows: {row_count}")
    except Exception as e:
        print(f"Error parsing {xml_name}: {e}")
