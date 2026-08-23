import xml.etree.ElementTree as ET
import os

xml_path = r"d:\finalresearchproject\scratch\pmc_9180463.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

# Search for any tag containing table-wrap
all_table_wraps = root.findall(".//table-wrap")
print("Total table-wraps:", len(all_table_wraps))
for i, tw in enumerate(all_table_wraps):
    label = tw.find("label")
    caption = tw.find("caption")
    label_txt = "".join(label.itertext()) if label is not None else "No label"
    caption_txt = "".join(caption.itertext()) if caption is not None else "No caption"
    print(f"Table-wrap {i+1}: {label_txt} - {caption_txt[:150]}")

# Search for supplementary-material
supps = root.findall(".//supplementary-material")
print("\nTotal supplementary materials:", len(supps))
for i, s in enumerate(supps):
    label = s.find("label")
    caption = s.find("caption")
    label_txt = "".join(label.itertext()) if label is not None else "No label"
    caption_txt = "".join(caption.itertext()) if caption is not None else "No caption"
    print(f"Supp {i+1}: {label_txt} - {caption_txt[:150]}")
