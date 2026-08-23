import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_paths = {
    "White-Sutton": "scratch/pmc_7713511.xml",
    "Xia-Gibbs": "scratch/pmc_6231716.xml"
}

for name, path in xml_paths.items():
    print(f"\n=================== {name} ({path}) ===================")
    if not os.path.exists(path):
        print("XML not found.")
        continue
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        tables = root.findall(".//table-wrap")
        print(f"Found {len(tables)} table-wrap elements.")
        for idx, tw in enumerate(tables):
            label = tw.find("label")
            label_text = label.text if label is not None else "No label"
            caption = tw.find("caption")
            caption_text = "".join(caption.itertext()).strip() if caption is not None else "No caption"
            print(f"Table {idx+1}: Label: {label_text}, Caption: {caption_text[:150]}")
            table_el = tw.find(".//table")
            if table_el is not None:
                rows = table_el.findall(".//tr")
                print(f"  Rows count: {len(rows)}")
                if len(rows) > 0:
                    headers = ["".join(td.itertext()).strip() for td in rows[0].findall(".//th") + rows[0].findall(".//td")]
                    print(f"  Header (first row): {headers[:10]}")
    except Exception as e:
        print("Error parsing XML:", e)
