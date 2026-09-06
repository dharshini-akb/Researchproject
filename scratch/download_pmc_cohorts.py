import urllib.request
import os
import time

WORKSPACE_DIR = r"d:\finalresearchproject"
SCRATCH_DIR = os.path.join(WORKSPACE_DIR, "scratch")

pmc_ids = [
    # White-Sutton syndrome
    ("PMC8775410", "pmc_8775410_ws_tan2022.xml"),
    ("PMC8738758", "pmc_8738758_ws_murch2021.xml"),
    ("PMC4890241", "pmc_4890241_ws_stessman2016.xml"),
    ("PMC4702300", "pmc_4702300_ws_white2016.xml"),
    ("PMC4850885", "pmc_4850885_ws_ye2015.xml"),
    
    # Xia-Gibbs syndrome
    ("PMC4067559", "pmc_4067559_xg_xia2014.xml"),
    ("PMC4850891", "pmc_4850891_xg_yang2015.xml"),
    ("PMC8694554", "pmc_8694554_xg_khayat2021.xml"),
    ("PMC9545659", "pmc_9545659_xg_romano2022.xml"),
    ("PMC6465669", "pmc_6465669_xg_cheng2019.xml"),
    
    # KBG syndrome
    ("PMC9180463", "pmc_9180463_kbg_bestetti2022.xml")
]

print("Downloading PMC full text XMLs...")
for pmc, filename in pmc_ids:
    target_path = os.path.join(SCRATCH_DIR, filename)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        print(f"Already exists: {filename} ({os.path.getsize(target_path)} bytes)")
        continue
        
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc}&retmode=xml"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read()
            with open(target_path, "wb") as f:
                f.write(content)
            print(f"Downloaded {pmc} -> {filename} ({len(content)} bytes)")
    except Exception as e:
        print(f"Error downloading {pmc}: {e}")
    time.sleep(0.4)

print("Done downloading PMC XMLs.")
