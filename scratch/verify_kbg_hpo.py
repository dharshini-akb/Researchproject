import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load HPO terms from hp.obo to map descriptions to HPO IDs
def parse_hpo_obo():
    import os
    obo_path = r"d:\finalresearchproject\data\raw\hp.obo"
    if not os.path.exists(obo_path):
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
print(f"Parsed {len(hpo_names)} HPO terms.")

# 1. Parse PMC8948816 (13 patients)
# Rows to map to HPOs:
# Birth history SGA -> HP:0001508
# Perinatal issues Feeding difficulties -> HP:0011968
# Macrodontia -> HP:0000696
# High palate -> HP:0000218
# Clinodactyly of the 5th finger -> HP:0004209
# Short stature -> HP:0004322
# Global development delay -> HP:0001263
# Speech and language development delay -> HP:0000750
# Intellectual disability/learning difficulties -> HP:0001249
# Behavioural anomalies (Hyperactivity/Anxiety/Aggressive) -> HP:0000708
# Delayed bone age -> HP:0002750
# Epilepsy -> HP:0001250
# Brain imaging anomalies -> HP:0002197
# Hearing loss -> HP:0000365
# CHD (PDA/VSD) -> HP:0001627
# Cryptorchidism -> HP:0000028

pmc8948816_hpos = []
tree = ET.parse("scratch/pmc_8948816.xml")
root = tree.getroot()
table = root.find(".//table-wrap//table")
if table is not None:
    rows = table.findall(".//tr")
    headers = ["".join(cell.itertext()).strip() for cell in rows[0].findall(".//td") + rows[0].findall(".//th")]
    # P1 to P13 are columns 1 to 13
    patient_data = {f"P{i}": [] for i in range(1, 14)}
    patient_sex = {}
    patient_age = {}
    
    # Extract Row data
    for tr in rows[1:]:
        cells = ["".join(cell.itertext()).strip() for cell in tr.findall(".//td") + tr.findall(".//th")]
        if not cells:
            continue
        feat_name = cells[0].strip()
        if feat_name == "Gender":
            for i in range(1, 14):
                patient_sex[f"P{i}"] = cells[i].strip()
        elif feat_name == "Age at diagnosis":
            for i in range(1, 14):
                patient_age[f"P{i}"] = cells[i].strip()
                
        # Feature checks
        for i in range(1, 14):
            val = cells[i].strip()
            if not val or val == "−" or val == "/" or val == "Na":
                continue
            
            # Map features
            hpo_id = None
            if "Birth history" in feat_name and "SGA" in val:
                hpo_id = "HP:0001508"
            elif "Perinatal issues" in feat_name and "Feeding" in val:
                hpo_id = "HP:0011968"
            elif "Macrodontia" in feat_name and "+" in val:
                hpo_id = "HP:0000696"
            elif "High palate" in feat_name and "+" in val:
                hpo_id = "HP:0000218"
            elif "Clinodactyly" in feat_name and "+" in val:
                hpo_id = "HP:0004209"
            elif "Short stature" in feat_name and "+" in val:
                hpo_id = "HP:0004322"
            elif "Global development delay" in feat_name and "+" in val:
                hpo_id = "HP:0001263"
            elif "Speech" in feat_name and "+" in val:
                hpo_id = "HP:0000750"
            elif "Intellectual" in feat_name and "+" in val:
                hpo_id = "HP:0001249"
            elif "Behavioural" in feat_name and "+" in val:
                hpo_id = "HP:0000708"
            elif "Delayed bone age" in feat_name and "+" in val:
                hpo_id = "HP:0002750"
            elif "Epilepsy" in feat_name and "+" in val:
                hpo_id = "HP:0001250"
            elif "Brain imaging" in feat_name and "+" in val:
                hpo_id = "HP:0002197"
            elif "Hearing loss" in feat_name and "+" in val:
                hpo_id = "HP:0000365"
            elif "CHD" in feat_name and "+" in val:
                hpo_id = "HP:0001627"
            elif "Cryptorchidism" in feat_name and "+" in val:
                hpo_id = "HP:0000028"
                
            if hpo_id:
                patient_data[f"P{i}"].append(hpo_id)
                
    for i in range(1, 14):
        pid = f"P{i}"
        pmc8948816_hpos.append({
            "Patient_ID": f"KBG_8948816_{pid}",
            "Sex": "MALE" if "Male" in patient_sex.get(pid, "") else "FEMALE",
            "Age": patient_age.get(pid, "Unknown"),
            "HPO_IDs": list(set(patient_data[pid]))
        })

# 2. Parse PMC5435101 (11 patients)
# Patient headers: '19 (9y 6m) M DDD', '26 (9y 9m) F', '4 (13y 3m) M DDD', '5 (21y) F*', '6 (19y) F*', '7 (12y) F*', '8 (47y) M*', '33 (3y 3m) M DDD', 'Ockeloen et al. [2015] pt 6 (38y) F' etc.
pmc5435101_hpos = []
tree2 = ET.parse("scratch/pmc_5435101.xml")
root2 = tree2.getroot()
table2 = root2.find(".//table-wrap//table")
if table2 is not None:
    rows2 = table2.findall(".//tr")
    headers2 = ["".join(cell.itertext()).strip() for cell in rows2[1].findall(".//td") + rows2[1].findall(".//th")]
    # Columns 1 to 11 are patient records
    p_count = len(headers2) - 1 # first col is feature name
    patient_data2 = {f"Col_{col_idx}": [] for col_idx in range(1, p_count + 1)}
    patient_info2 = {}
    
    # Process headers
    for col_idx in range(1, p_count + 1):
        h = headers2[col_idx]
        patient_info2[f"Col_{col_idx}"] = {
            "ID": h.split()[0],
            "Sex": "FEMALE" if " F" in h else "MALE",
            "Age": h.replace("\n", " ").split("(")[1].split(")")[0] if "(" in h else "Unknown"
        }
        
    for tr in rows2[2:]:
        cells = ["".join(cell.itertext()).strip() for cell in tr.findall(".//td") + tr.findall(".//th")]
        if not cells:
            continue
        feat_name = cells[0].strip()
        for col_idx in range(1, len(cells)):
            val = cells[col_idx].strip().lower()
            if not val or val == "−" or val == "—" or val == "unknown":
                continue
            
            hpo_id = None
            if "Macrodontia" in feat_name and "+" in val:
                hpo_id = "HP:0000696"
            elif "Short stature" in feat_name and "+" in val:
                hpo_id = "HP:0004322"
            elif "Learning difficulties" in feat_name and "+" in val or "moderate" in val:
                hpo_id = "HP:0001249"
            elif "Skeletal abnormalities" in feat_name and val != "−":
                hpo_id = "HP:0000924"
            elif "Hand anomalies" in feat_name and "+" in val:
                hpo_id = "HP:0001155"
            elif "Ocular" in feat_name and "+" in val:
                hpo_id = "HP:0000490"
            elif "Hearing Loss" in feat_name and "+" in val:
                hpo_id = "HP:0000365"
            elif "Neurological" in feat_name and ("seizures" in val or "seziures" in val or "seizure" in val or "+" in val):
                hpo_id = "HP:0001250"
            elif "Behavioural" in feat_name and val != "−":
                hpo_id = "HP:0000708"
            elif "Palate" in feat_name and "+" in val:
                hpo_id = "HP:0000218"
            elif "Heart" in feat_name and val != "−":
                hpo_id = "HP:0001627"
                
            if hpo_id:
                patient_data2[f"Col_{col_idx}"].append(hpo_id)
                
    for col_idx in range(1, p_count + 1):
        col_key = f"Col_{col_idx}"
        p_info = patient_info2[col_key]
        pmc5435101_hpos.append({
            "Patient_ID": f"KBG_5435101_{p_info['ID']}",
            "Sex": p_info["Sex"],
            "Age": p_info["Age"],
            "HPO_IDs": list(set(patient_data2[col_key]))
        })

# Combine
combined = pmc8948816_hpos + pmc5435101_hpos
print(f"Total Combined Patients: {len(combined)}")

# Count unique HPO IDs
all_hpo_ids = set()
for p in combined:
    all_hpo_ids.update(p["HPO_IDs"])
print(f"Unique HPO terms count: {len(all_hpo_ids)}")

# Check counts
count_1 = 0
count_5 = 0
count_10 = 0
for p in combined:
    n_hpo = len(p["HPO_IDs"])
    if n_hpo >= 1:
        count_1 += 1
    if n_hpo >= 5:
        count_5 += 1
    if n_hpo >= 10:
        count_10 += 1
        
print(f"≥ 1 HPO: {count_1}")
print(f"≥ 5 HPO: {count_5}")
print(f"≥ 10 HPO: {count_10}")

# Print list of patient IDs to verify uniqueness
print("Patient IDs list:")
for p in combined:
    print(f"  {p['Patient_ID']} - HPOs count: {len(p['HPO_IDs'])}")
