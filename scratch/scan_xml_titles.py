import os
import xml.etree.ElementTree as ET

def get_title(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        # Find title
        title_el = root.find(".//article-title")
        if title_el is not None:
            return "".join(title_el.itertext()).strip()
    except Exception as e:
        return f"Error: {e}"
    return "No title found"

scratch_dir = r"d:\finalresearchproject\scratch"
for name in sorted(os.listdir(scratch_dir)):
    if name.startswith("pmc_") and name.endswith(".xml"):
        path = os.path.join(scratch_dir, name)
        title = get_title(path)
        print(f"{name}: {title}")
