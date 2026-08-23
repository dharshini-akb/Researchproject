import os
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import train_test_split

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = r"d:\finalresearchproject"
RAW_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "raw")
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
SPLITS_DIR = os.path.join(DATA_DIR, "splits")

# 1. Load HPO term names from hp.obo
def parse_hpo_obo():
    obo_path = os.path.join(RAW_DATA_DIR, "hp.obo")
    if not os.path.exists(obo_path):
        print(f"hp.obo not found at {obo_path}")
        return {}
    hpo_map = {}
    current_id = None
    current_name = None
    with open(obo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if current_id and current_name:
                    hpo_map[current_id] = current_name
                current_id = None
                current_name = None
            elif line.startswith("id:"):
                current_id = line.split("id:")[1].strip()
            elif line.startswith("name:"):
                current_name = line.split("name:")[1].strip()
        if current_id and current_name:
            hpo_map[current_id] = current_name
    return hpo_map

hpo_names = parse_hpo_obo()
print(f"Loaded {len(hpo_names)} HPO terms from ontology.")

def element_to_text(el):
    return "".join(el.itertext()).strip() if el is not None else ""

# 2. Extract White-Sutton syndrome (PMC7713511)
ws_xml_path = os.path.join(WORKSPACE_DIR, "scratch", "pmc_7713511.xml")
ws_patients = {}
if os.path.exists(ws_xml_path):
    tree = ET.parse(ws_xml_path)
    root = tree.getroot()
    
    # Table 3 (Neurocognitive)
    t3 = None
    for tw in root.findall(".//table-wrap"):
        caption = element_to_text(tw.find("caption"))
        if "Neurocognitive" in caption:
            t3 = tw.find(".//table")
            break
    if t3 is not None:
        rows = t3.findall(".//tr")
        for tr in rows[1:]:
            cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            if len(cells) < 10:
                continue
            pid = cells[0].strip()
            sex = "FEMALE" if "F" in cells[2].upper() else ("MALE" if "M" in cells[2].upper() else "UNKNOWN_SEX")
            age = cells[4].strip() # Age at diagnosis
            
            hpos = []
            # Motor delay
            if cells[5].strip() and "−" not in cells[5] and "NR" not in cells[5].upper():
                hpos.append("HP:0001270")
            # Speech delay
            if cells[6].strip() and "−" not in cells[6] and "NR" not in cells[6].upper():
                hpos.append("HP:0000750")
            # Intellectual disability
            if cells[7].strip() and "−" not in cells[7] and "NR" not in cells[7].upper():
                hpos.append("HP:0001249")
            # Learning difficulties
            if cells[8].strip() and "−" not in cells[8] and "NR" not in cells[8].upper() and "N/A" not in cells[8].upper():
                hpos.append("HP:0001328")
            # Autism
            if cells[9].strip() and "−" not in cells[9] and "NR" not in cells[9].upper():
                hpos.append("HP:0000717")
                
            ws_patients[pid] = {
                "Patient_ID": f"WhiteSutton_{pid}",
                "Disease": "White-Sutton Syndrome",
                "Sex": sex,
                "Age": age,
                "HPO_IDs": hpos,
                "Source": "PMC7713511"
            }

    # Table 4 (Neurologic)
    t4 = None
    for tw in root.findall(".//table-wrap"):
        caption = element_to_text(tw.find("caption"))
        if "Neurologic features" in caption:
            t4 = tw.find(".//table")
            break
    if t4 is not None:
        rows = t4.findall(".//tr")
        for tr in rows[1:]:
            cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            if len(cells) < 7:
                continue
            pid = cells[0].strip()
            if pid in ws_patients:
                # Seizures
                if cells[2].strip() and "−" not in cells[2] and "NR" not in cells[2].upper():
                    ws_patients[pid]["HPO_IDs"].append("HP:0001250")
                # Eye abnormality
                if cells[4].strip() and "−" not in cells[4] and "NR" not in cells[4].upper():
                    ws_patients[pid]["HPO_IDs"].append("HP:0000490")
                    val = cells[4].lower()
                    if "exotropia" in val: ws_patients[pid]["HPO_IDs"].append("HP:0000568")
                    if "strabismus" in val: ws_patients[pid]["HPO_IDs"].append("HP:0000486")
                    if "myopia" in val: ws_patients[pid]["HPO_IDs"].append("HP:0000545")
                    if "astigmatism" in val: ws_patients[pid]["HPO_IDs"].append("HP:0000483")
                    if "nystagmus" in val: ws_patients[pid]["HPO_IDs"].append("HP:0000639")
                # Hearing loss
                if cells[5].strip() and "−" not in cells[5] and "NR" not in cells[5].upper():
                    ws_patients[pid]["HPO_IDs"].append("HP:0000365")
                    if "snhl" in cells[5].lower() or "sensorineural" in cells[5].lower():
                        ws_patients[pid]["HPO_IDs"].append("HP:0000407")
                # Microcephaly
                if cells[6].strip() and "−" not in cells[6] and "NR" not in cells[6].upper():
                    ws_patients[pid]["HPO_IDs"].append("HP:0000252")

# 3. Extract Xia-Gibbs syndrome (PMC6231716)
xg_xml_path = os.path.join(WORKSPACE_DIR, "scratch", "pmc_6231716.xml")
xg_patients = []
if os.path.exists(xg_xml_path):
    tree = ET.parse(xg_xml_path)
    root = tree.getroot()
    table = root.find(".//table-wrap//table")
    if table is not None:
        rows = table.findall(".//tr")
        row_headers = []
        patient_cols = [[] for _ in range(20)]
        for tr in rows:
            cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            if len(cells) < 21:
                continue
            row_headers.append(cells[0].strip())
            for i in range(20):
                patient_cols[i].append(cells[i + 1].strip())
                
        xg_hpo_map = {
            "Scoliosis": "HP:0002650",
            "Prior autism diagnosis": "HP:0000717",
            "Hypotonia diagnosis": "HP:0001252",
            "Sleep apnea": "HP:0002870",
            "Seizure": "HP:0001250",
            "Ataxia": "HP:0001251",
            "Strabismus": "HP:0000486",
            "Small ear lobes": "HP:0009907",
            "Upturned earlobes": "HP:0000377",
            "Low-set ears": "HP:0000369",
            "Protuberant ears": "HP:0000411",
            "Deep-set eyes": "HP:0003200",
            "Upslanting palpebral fissures": "HP:0000582",
            "Downslanting palpebral fissure": "HP:0000494",
            "Mild ptosis": "HP:0000508",
            "Esotropia": "HP:0000565",
            "Hypertelorism": "HP:0000316",
            "Flat nasal bridge": "HP:0005280",
            "Micrognathia": "HP:0000347",
            "Thin upper lip": "HP:0000219",
            "Broad forehead": "HP:0000337"
        }
        
        for i in range(20):
            p_data = patient_cols[i]
            age = p_data[5]
            sex = "FEMALE" if "F" in p_data[6].upper() else ("MALE" if "M" in p_data[6].upper() else "UNKNOWN_SEX")
            hpos = []
            for r_idx, feat in enumerate(row_headers):
                if feat in xg_hpo_map:
                    val = p_data[r_idx].strip().upper()
                    if val == "Y" or val == "YES":
                        hpos.append(xg_hpo_map[feat])
            # Language level check
            if p_data[14].strip() in ["0", "1"]:
                hpos.append("HP:0000750") # Delayed speech and language
                
            xg_patients.append({
                "Patient_ID": f"XiaGibbs_Patient_{i+1}",
                "Disease": "Xia-Gibbs Syndrome",
                "Sex": sex,
                "Age": age,
                "HPO_IDs": hpos,
                "Source": "PMC6231716"
            })

# 4. Extract KBG syndrome (PMC8948816 and PMC5435101)
kbg_patients = []

# PMC8948816 (13 patients)
kbg_xml1 = os.path.join(WORKSPACE_DIR, "scratch", "pmc_8948816.xml")
if os.path.exists(kbg_xml1):
    tree = ET.parse(kbg_xml1)
    root = tree.getroot()
    table = root.find(".//table-wrap//table")
    if table is not None:
        rows = table.findall(".//tr")
        patient_data = {f"P{i}": [] for i in range(1, 14)}
        patient_sex = {}
        patient_age = {}
        for tr in rows:
            cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            if len(cells) < 14: continue
            feat_name = cells[0].strip()
            if feat_name == "Gender":
                for i in range(1, 14): patient_sex[f"P{i}"] = cells[i].strip()
            elif feat_name == "Age at diagnosis":
                for i in range(1, 14): patient_age[f"P{i}"] = cells[i].strip()
            
            for i in range(1, 14):
                val = cells[i].strip()
                if not val or val == "−" or val == "/" or val == "Na":
                    continue
                hpo_id = None
                if "Birth history" in feat_name and "SGA" in val: hpo_id = "HP:0001508"
                elif "Perinatal issues" in feat_name and "Feeding" in val: hpo_id = "HP:0011968"
                elif "Macrodontia" in feat_name and "+" in val: hpo_id = "HP:0000696"
                elif "High palate" in feat_name and "+" in val: hpo_id = "HP:0000218"
                elif "Clinodactyly" in feat_name and "+" in val: hpo_id = "HP:0004209"
                elif "Short stature" in feat_name and "+" in val: hpo_id = "HP:0004322"
                elif "Global development delay" in feat_name and "+" in val: hpo_id = "HP:0001263"
                elif "Speech" in feat_name and "+" in val: hpo_id = "HP:0000750"
                elif "Intellectual" in feat_name and "+" in val: hpo_id = "HP:0001249"
                elif "Behavioural" in feat_name and "+" in val: hpo_id = "HP:0000708"
                elif "Delayed bone age" in feat_name and "+" in val: hpo_id = "HP:0002750"
                elif "Epilepsy" in feat_name and "+" in val: hpo_id = "HP:0001250"
                elif "Brain imaging" in feat_name and "+" in val: hpo_id = "HP:0002197"
                elif "Hearing loss" in feat_name and "+" in val: hpo_id = "HP:0000365"
                elif "CHD" in feat_name and "+" in val: hpo_id = "HP:0001627"
                elif "Cryptorchidism" in feat_name and "+" in val: hpo_id = "HP:0000028"
                if hpo_id:
                    patient_data[f"P{i}"].append(hpo_id)
        for i in range(1, 14):
            pid = f"P{i}"
            kbg_patients.append({
                "Patient_ID": f"KBG_8948816_{pid}",
                "Disease": "KBG Syndrome",
                "Sex": "MALE" if "Male" in patient_sex.get(pid, "") else "FEMALE",
                "Age": patient_age.get(pid, "Unknown"),
                "HPO_IDs": list(set(patient_data[pid])),
                "Source": "PMC8948816"
            })

# PMC5435101 (11 patients)
kbg_xml2 = os.path.join(WORKSPACE_DIR, "scratch", "pmc_5435101.xml")
if os.path.exists(kbg_xml2):
    tree = ET.parse(kbg_xml2)
    root = tree.getroot()
    table = root.find(".//table-wrap//table")
    if table is not None:
        rows = table.findall(".//tr")
        headers = [element_to_text(cell) for cell in rows[1].findall(".//td") + rows[1].findall(".//th")]
        p_count = len(headers) - 1
        patient_data2 = {f"Col_{col_idx}": [] for col_idx in range(1, p_count + 1)}
        patient_info2 = {}
        for col_idx in range(1, p_count + 1):
            h = headers[col_idx]
            patient_info2[f"Col_{col_idx}"] = {
                "ID": h.split()[0],
                "Sex": "FEMALE" if " F" in h else "MALE",
                "Age": h.replace("\n", " ").split("(")[1].split(")")[0] if "(" in h else "Unknown"
            }
        for tr in rows[2:]:
            cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            if len(cells) < p_count + 1: continue
            feat_name = cells[0].strip()
            for col_idx in range(1, len(cells)):
                val = cells[col_idx].strip().lower()
                if not val or val == "−" or val == "—" or val == "unknown":
                    continue
                hpo_id = None
                if "Macrodontia" in feat_name and "+" in val: hpo_id = "HP:0000696"
                elif "Short stature" in feat_name and "+" in val: hpo_id = "HP:0004322"
                elif "Learning difficulties" in feat_name and ("+" in val or "moderate" in val): hpo_id = "HP:0001249"
                elif "Skeletal abnormalities" in feat_name and val != "−": hpo_id = "HP:0000924"
                elif "Hand anomalies" in feat_name and "+" in val: hpo_id = "HP:0001155"
                elif "Ocular" in feat_name and "+" in val: hpo_id = "HP:0000490"
                elif "Hearing Loss" in feat_name and "+" in val: hpo_id = "HP:0000365"
                elif "Neurological" in feat_name and ("seizures" in val or "seziures" in val or "seizure" in val or "+" in val): hpo_id = "HP:0001250"
                elif "Behavioural" in feat_name and val != "−": hpo_id = "HP:0000708"
                elif "Palate" in feat_name and "+" in val: hpo_id = "HP:0000218"
                elif "Heart" in feat_name and val != "−": hpo_id = "HP:0001627"
                if hpo_id:
                    patient_data2[f"Col_{col_idx}"].append(hpo_id)
        # Deduplicate keys to avoid adding duplicates if same ID extracted
        added_ids = set()
        for col_idx in range(1, p_count + 1):
            col_key = f"Col_{col_idx}"
            p_info = patient_info2[col_key]
            p_id = f"KBG_5435101_{p_info['ID']}"
            if p_id in added_ids:
                # Append suffix if collision
                p_id = p_id + "_2"
            added_ids.add(p_id)
            kbg_patients.append({
                "Patient_ID": p_id,
                "Disease": "KBG Syndrome",
                "Sex": p_info["Sex"],
                "Age": p_info["Age"],
                "HPO_IDs": list(set(patient_data2[col_key])),
                "Source": "PMC5435101"
            })

# Combine all into one DataFrame
all_records = list(ws_patients.values()) + xg_patients + kbg_patients

# Format HPO_IDs and HPO_Terms
for r in all_records:
    # Deduplicate and sort HPO IDs
    unique_hpos = sorted(list(set(r["HPO_IDs"])))
    r["HPO_IDs"] = "|".join(unique_hpos)
    r["HPO_Terms"] = "|".join([hpo_names.get(h, "Unknown HPO Term") for h in unique_hpos])

df_real = pd.DataFrame(all_records)

# ---------------- DATA QUALITY CHECKS ----------------
print("\n--- DATA QUALITY CHECKS ---")
# 1. Duplicate Patient IDs
dup_ids = df_real[df_real.duplicated(subset=["Patient_ID"])]
print("Duplicate Patient_IDs count:", len(dup_ids))

# 2. Duplicate Phenotype Profiles
dup_phenotypes = df_real[df_real.duplicated(subset=["HPO_IDs"], keep=False)]
print("Duplicate phenotype profiles count:", len(dup_phenotypes))

# 3. Missing values
print("Missing disease labels count:", df_real["Disease"].isna().sum())
print("Missing HPO IDs count:", (df_real["HPO_IDs"] == "").sum())

# 4. Invalid disease names
print("Unique diseases found:", df_real["Disease"].unique())

# 5. Patient counts per class
counts = df_real["Disease"].value_counts()
print("Counts per disease:\n", counts)

# 6. Total count
total_count = len(df_real)
print("Total records count:", total_count)

# Verify expected values
expected_ws = 23
expected_xg = 20
expected_kbg = 24
if counts.get("White-Sutton Syndrome", 0) != expected_ws or \
   counts.get("Xia-Gibbs Syndrome", 0) != expected_xg or \
   counts.get("KBG Syndrome", 0) != expected_kbg:
    print("ERROR: Counts do not match expected values!")
    sys.exit(1)
else:
    print("SUCCESS: Patient counts match exactly!")

# Save to data/real_patient_hpo_dataset.csv
os.makedirs(os.path.dirname(os.path.join(DATA_DIR, "real_patient_hpo_dataset.csv")), exist_ok=True)
df_real.to_csv(os.path.join(DATA_DIR, "real_patient_hpo_dataset.csv"), index=False)
df_real.to_csv(os.path.join(RAW_DATA_DIR, "real_patient_hpo_dataset.csv"), index=False)
print("Saved real dataset to data/real_patient_hpo_dataset.csv")

# 7. Patient-level stratified splitting
# We split using train_test_split (stratified by disease)
# Train 60%, Val 20%, Test 20%
df_train, df_temp = train_test_split(df_real, test_size=0.4, random_state=42, stratify=df_real["Disease"])
df_val, df_test = train_test_split(df_temp, test_size=0.5, random_state=42, stratify=df_temp["Disease"])

print(f"\n--- SPLIT SIZES ---")
print(f"Train size: {len(df_train)} (WS: {sum(df_train['Disease'] == 'White-Sutton Syndrome')}, XG: {sum(df_train['Disease'] == 'Xia-Gibbs Syndrome')}, KBG: {sum(df_train['Disease'] == 'KBG Syndrome')})")
print(f"Val size: {len(df_val)} (WS: {sum(df_val['Disease'] == 'White-Sutton Syndrome')}, XG: {sum(df_val['Disease'] == 'Xia-Gibbs Syndrome')}, KBG: {sum(df_val['Disease'] == 'KBG Syndrome')})")
print(f"Test size: {len(df_test)} (WS: {sum(df_test['Disease'] == 'White-Sutton Syndrome')}, XG: {sum(df_test['Disease'] == 'Xia-Gibbs Syndrome')}, KBG: {sum(df_test['Disease'] == 'KBG Syndrome')})")

# Write split manifests
df_train[["Patient_ID"]].rename(columns={"Patient_ID": "case_id"}).to_csv(os.path.join(SPLITS_DIR, "train_manifest.csv"), index=False)
df_val[["Patient_ID"]].rename(columns={"Patient_ID": "case_id"}).to_csv(os.path.join(SPLITS_DIR, "validation_manifest.csv"), index=False)
df_test[["Patient_ID"]].rename(columns={"Patient_ID": "case_id"}).to_csv(os.path.join(SPLITS_DIR, "test_manifest.csv"), index=False)
print("Saved split manifests to data/splits/")
