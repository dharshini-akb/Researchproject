import xml.etree.ElementTree as ET
import os

xml_path = r"d:\finalresearchproject\scratch\pmc_9180463.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

all_tables = root.findall(".//table-wrap")
print("Total tables in XML:", len(all_tables))
for i, t in enumerate(all_tables):
    print(f"Table {i+1}: ID={t.get('id')}, Label={t.findtext('label')}")
    # Print the table caption
    caption = t.find("caption")
    caption_txt = "".join(caption.itertext()).strip() if caption is not None else ""
    print(f"Caption: {caption_txt[:150]}")
    print("-" * 50)
