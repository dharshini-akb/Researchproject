import os

workspace = r"d:\finalresearchproject"
print("Scanning for json or xml files...")
for root, dirs, files in os.walk(workspace):
    # print folders if they contain phenopackets or notebooks
    for d in dirs:
        if "phenopacket" in d.lower() or "notebook" in d.lower():
            print("Found directory:", os.path.join(root, d))
    # print sample json files
    json_files = [f for f in files if f.endswith(".json")]
    if json_files:
        print(f"Found {len(json_files)} json files in {root}. Sample: {json_files[:5]}")
