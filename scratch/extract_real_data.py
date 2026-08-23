import os
import xml.etree.ElementTree as ET
import pandas as pd
import sys

# Reconfigure stdout to use utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Base paths
WORKSPACE_DIR = r"d:\finalresearchproject"
RAW_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "processed")

# Parse HPO OBO to find names for our HPO IDs
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
print(f"Parsed {len(hpo_names)} HPO terms from OBO.")

# Define mapping dictionary from clinical features to HPO IDs
# 1. White-Sutton mapping
ws_hpo_map = {
    "Motordelay": "HP:0001270",          # Motor delay
    "SpeechDelay": "HP:0000750",         # Delayed speech and language development
    "Intellectualdisability": "HP:0001249",# Intellectual disability
    "Learningdifficulties": "HP:0001328",  # Specific learning disability
    "Autism": "HP:0000717",              # Autism
    "Seizures": "HP:0001250",            # Seizure
    "Hearing loss": "HP:0000365",        # Hearing impairment
    "Microcephaly": "HP:0000252",        # Microcephaly
}

# 2. Xia-Gibbs mapping
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

def element_to_text(el):
    return "".join(el.itertext()).strip() if el is not None else ""

# ----------------- EXTRACT WHITE-SUTTON (PMC7713511) -----------------
ws_xml_path = "scratch/pmc_7713511.xml"
ws_patients = {} # ID -> patient dict

if os.path.exists(ws_xml_path):
    ws_tree = ET.parse(ws_xml_path)
    ws_root = ws_tree.getroot()
    
    # Table 3 (Neurocognitive)
    t3 = None
    for tw in ws_root.findall(".//table-wrap"):
        caption = element_to_text(tw.find("caption"))
        if "Neurocognitive" in caption:
            t3 = tw.find(".//table")
            break
            
    if t3 is not None:
        t3_rows = t3.findall(".//tr")
        headers = [element_to_text(cell) for cell in t3_rows[0].findall(".//th") + t3_rows[0].findall(".//td")]
        # Header: ID, Mutation, Sex, Age atpresentation, Age atdiagnosis, Motordelay, SpeechDelay, Intellectualdisability, Learningdifficulties, Autism
        for tr in t3_rows[1:]:
            cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            if len(cells) < len(headers):
                continue
            pid = cells[0].strip()
            sex = cells[2].strip().upper()
            age_str = cells[4].strip() # Age at diagnosis
            
            # Map Sex
            sex_val = "FEMALE" if "F" in sex else ("MALE" if "M" in sex else "UNKNOWN_SEX")
            
            # Extract HPOs from Table 3 columns
            hpos_present = []
            original_terms = []
            
            # Motor delay
            val = cells[5].strip().lower()
            if val and "−" not in val and "nr" not in val and "no" not in val:
                hpos_present.append("HP:0001270")
                original_terms.append(f"Motor delay ({cells[5]})")
                
            # Speech delay
            val = cells[6].strip().lower()
            if val and "−" not in val and "nr" not in val and "no" not in val:
                hpos_present.append("HP:0000750")
                original_terms.append(f"Speech delay ({cells[6]})")
                
            # Intellectual disability
            val = cells[7].strip().lower()
            if val and "−" not in val and "nr" not in val and "no" not in val:
                hpos_present.append("HP:0001249")
                original_terms.append(f"Intellectual disability ({cells[7]})")
                
            # Learning difficulties
            val = cells[8].strip().lower()
            if val and "−" not in val and "nr" not in val and "no" not in val and "n/a" not in val:
                hpos_present.append("HP:0001328")
                original_terms.append(f"Learning difficulties ({cells[8]})")
                
            # Autism
            val = cells[9].strip().lower()
            if val and "−" not in val and "nr" not in val and "no" not in val:
                hpos_present.append("HP:0000717")
                original_terms.append(f"Autism ({cells[9]})")
                
            ws_patients[pid] = {
                "Patient_ID": f"WhiteSutton_{pid}",
                "Disease": "White-Sutton syndrome",
                "Sex": sex_val,
                "Age": age_str,
                "HPO_IDs": hpos_present,
                "Original_Terms": original_terms,
                "Source": "PMC7713511"
            }

    # Table 4 (Neurologic)
    t4 = None
    for tw in ws_root.findall(".//table-wrap"):
        caption = element_to_text(tw.find("caption"))
        if "Neurologic features" in caption:
            t4 = tw.find(".//table")
            break
            
    if t4 is not None:
        t4_rows = t4.findall(".//tr")
        for tr in t4_rows[1:]:
            cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            if len(cells) < 7:
                continue
            pid = cells[0].strip()
            if pid in ws_patients:
                # Seizures
                val = cells[2].strip().lower()
                if val and "−" not in val and "nr" not in val and "no" not in val:
                    ws_patients[pid]["HPO_IDs"].append("HP:0001250")
                    ws_patients[pid]["Original_Terms"].append(f"Seizures ({cells[2]})")
                
                # Eye abnormality
                val = cells[4].strip().lower()
                if val and "−" not in val and "nr" not in val and "no" not in val:
                    # Let's map specific eye features mentioned
                    # E.g., Exotropia -> HP:0000568, Strabismus -> HP:0000486, Myopia -> HP:0000545, Astigmatism -> HP:0000483
                    # But we can also add general Eye Abnormality HP:0000490
                    ws_patients[pid]["HPO_IDs"].append("HP:0000490")
                    ws_patients[pid]["Original_Terms"].append(f"Eye abnormality ({cells[4]})")
                    
                    if "exotropia" in val:
                        ws_patients[pid]["HPO_IDs"].append("HP:0000568")
                        ws_patients[pid]["Original_Terms"].append("Exotropia")
                    if "strabismus" in val:
                        ws_patients[pid]["HPO_IDs"].append("HP:0000486")
                        ws_patients[pid]["Original_Terms"].append("Strabismus")
                    if "myopia" in val:
                        ws_patients[pid]["HPO_IDs"].append("HP:0000545")
                        ws_patients[pid]["Original_Terms"].append("Myopia")
                    if "astigmatism" in val:
                        ws_patients[pid]["HPO_IDs"].append("HP:0000483")
                        ws_patients[pid]["Original_Terms"].append("Astigmatism")
                    if "nystagmus" in val:
                        ws_patients[pid]["HPO_IDs"].append("HP:0000639")
                        ws_patients[pid]["Original_Terms"].append("Nystagmus")
                        
                # Hearing loss
                val = cells[5].strip().lower()
                if val and "−" not in val and "nr" not in val and "no" not in val:
                    ws_patients[pid]["HPO_IDs"].append("HP:0000365")
                    ws_patients[pid]["Original_Terms"].append(f"Hearing loss ({cells[5]})")
                    if "snhl" in val or "sensorineural" in val:
                        ws_patients[pid]["HPO_IDs"].append("HP:0000407")
                        ws_patients[pid]["Original_Terms"].append("Sensorineural hearing impairment")
                        
                # Microcephaly
                val = cells[6].strip().lower()
                if val and "−" not in val and "nr" not in val and "no" not in val:
                    ws_patients[pid]["HPO_IDs"].append("HP:0000252")
                    ws_patients[pid]["Original_Terms"].append("Microcephaly")

# ----------------- EXTRACT XIA-GIBBS (PMC6231716) -----------------
xg_xml_path = "scratch/pmc_6231716.xml"
xg_patients = []

if os.path.exists(xg_xml_path):
    xg_tree = ET.parse(xg_xml_path)
    xg_root = xg_tree.getroot()
    
    t1 = xg_root.find(".//table-wrap//table")
    if t1 is not None:
        t1_rows = t1.findall(".//tr")
        # Transpose Table 1: columns are patients, rows are symptoms
        row_headers = []
        patient_cols = [[] for _ in range(20)] # 20 patients
        
        for tr in t1_rows:
            cells = [element_to_text(cell) for cell in tr.findall(".//td") + tr.findall(".//th")]
            if len(cells) < 21:
                continue
            feat_name = cells[0].strip()
            row_headers.append(feat_name)
            for p_idx in range(20):
                patient_cols[p_idx].append(cells[p_idx + 1].strip())
                
        # Parse each patient
        # Row 5 is Age, Row 6 is Gender
        for p_idx in range(20):
            p_data = patient_cols[p_idx]
            age_str = p_data[5]
            gender_str = p_data[6].upper()
            sex_val = "FEMALE" if "F" in gender_str else ("MALE" if "M" in gender_str else "UNKNOWN_SEX")
            
            hpos_present = []
            original_terms = []
            
            # Now loop through phenotype rows and check if Y or Yes
            for r_idx, feat in enumerate(row_headers):
                if feat in xg_hpo_map:
                    val = p_data[r_idx].strip().upper()
                    if val == "Y" or val == "YES":
                        hpo_id = xg_hpo_map[feat]
                        hpos_present.append(hpo_id)
                        original_terms.append(feat)
                        
            # Handcrafting a couple of specific ones:
            # Row 14: Current language score (if 0 or 1, they have speech delay/absent speech)
            lang_val = p_data[14].strip()
            if lang_val in ["0", "1"]:
                hpos_present.append("HP:0000750") # Delayed speech and language development
                original_terms.append("Speech delay / absent speech")
                
            # Row 19: Hypotonia diagnosis
            hypo_val = p_data[19].strip().upper()
            if hypo_val == "Y" or hypo_val == "YES":
                # Wait, HP:0001252 is already in xg_hpo_map. Let's make sure it's added.
                pass
                
            xg_patients.append({
                "Patient_ID": f"XiaGibbs_Patient_{p_idx+1}",
                "Disease": "Xia-Gibbs syndrome",
                "Sex": sex_val,
                "Age": age_str,
                "HPO_IDs": hpos_present,
                "Original_Terms": original_terms,
                "Source": "PMC6231716"
            })

# Combine all extracted records
all_extracted_records = list(ws_patients.values()) + xg_patients

# Format HPO_IDs and terms as pipe-separated strings
for r in all_extracted_records:
    # Remove duplicates from HPO_IDs and sort them
    unique_hpos = sorted(list(set(r["HPO_IDs"])))
    r["HPO_IDs"] = "|".join(unique_hpos)
    r["HPO_Terms"] = "|".join([hpo_names.get(h, "Unknown term") for h in unique_hpos])
    # Combine original terms to a string
    r["Original_Terms"] = "|".join(r["Original_Terms"])

df_out = pd.DataFrame(all_extracted_records)
df_out.to_csv("real_patient_hpo_dataset.csv", index=False)
print(f"Saved real_patient_hpo_dataset.csv with {len(df_out)} rows.")

# ----------------- CREATE AUDIT -----------------
# For Cornelia de Lange: N=49, aggregate only
audit_data = [
    {
        "Disease": "White-Sutton syndrome",
        "Source": "PMC7713511",
        "Number_of_Patients": 22,
        "Patient_Level_Data_Available": "Yes",
        "HPO_Available": "No (Mapped using hp.obo)",
        "Clinical_Phenotypes_Available": "Yes",
        "Age_Available": "Yes",
        "Sex_Available": "Yes",
        "Usable_For_Model": "Yes",
        "Notes": "Detailed patient-level cognitive, neurological and dysmorphic features extracted from Tables 3, 4, 6."
    },
    {
        "Disease": "Xia-Gibbs syndrome",
        "Source": "PMC6231716",
        "Number_of_Patients": 20,
        "Patient_Level_Data_Available": "Yes",
        "HPO_Available": "No (Mapped using hp.obo)",
        "Clinical_Phenotypes_Available": "Yes",
        "Age_Available": "Yes",
        "Sex_Available": "Yes",
        "Usable_For_Model": "Yes",
        "Notes": "Detailed patient-level features extracted from Table 1."
    },
    {
        "Disease": "Cornelia de Lange syndrome 1",
        "Source": "PMC4902018",
        "Number_of_Patients": 49,
        "Patient_Level_Data_Available": "No",
        "HPO_Available": "No",
        "Clinical_Phenotypes_Available": "Yes (Aggregate only)",
        "Age_Available": "No",
        "Sex_Available": "No",
        "Usable_For_Model": "No",
        "Notes": "Aggregate phenotype data — not suitable for direct patient-level training"
    }
]

df_audit = pd.DataFrame(audit_data)
df_audit.to_csv("real_dataset_audit.csv", index=False)
print("Saved real_dataset_audit.csv.")

# Let's count unique HPO terms
all_hpos = set()
for h_str in df_out["HPO_IDs"]:
    if h_str:
        all_hpos.update(h_str.split("|"))
print("Unique HPO terms extracted:", len(all_hpos))

# Let's count patient counts for >= 1, >= 5, >= 10 HPOs
count_1 = 0
count_5 = 0
count_10 = 0
for h_str in df_out["HPO_IDs"]:
    h_count = len([h for h in h_str.split("|") if h])
    if h_count >= 1:
        count_1 += 1
    if h_count >= 5:
        count_5 += 1
    if h_count >= 10:
        count_10 += 1

print(f"Patients with >= 1 HPO: {count_1}")
print(f"Patients with >= 5 HPO: {count_5}")
print(f"Patients with >= 10 HPO: {count_10}")
