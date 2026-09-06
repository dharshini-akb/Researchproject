import os

WORKSPACE_DIR = r"d:\finalresearchproject"
RAW_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "raw")

# Check hp.obo header
obo_path = os.path.join(RAW_DATA_DIR, "hp.obo")
if os.path.exists(obo_path):
    print("=== HP.OBO HEADER ===")
    with open(obo_path, "r", encoding="utf-8") as f:
        for i in range(25):
            print(f.readline().strip())

# Check phenotype.hpoa header
hpoa_path = os.path.join(RAW_DATA_DIR, "phenotype.hpoa")
if os.path.exists(hpoa_path):
    print("\n=== PHENOTYPE.HPOA HEADER ===")
    with open(hpoa_path, "r", encoding="utf-8") as f:
        for i in range(15):
            print(f.readline().strip())
