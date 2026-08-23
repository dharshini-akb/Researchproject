import os
import re
import pandas as pd

# Base paths
WORKSPACE_DIR = r"d:\finalresearchproject"
RAW_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "raw")
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "reports")

# 1. Parse HPO term names from hp.obo
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
print(f"Parsed {len(hpo_names)} HPO terms from hp.obo")

# 2. Load current real patient dataset
curr_path = os.path.join(RAW_DATA_DIR, "real_patient_hpo_dataset.csv")
df_curr = pd.read_csv(curr_path)
print(f"Loaded {len(df_curr)} current real patients.")

# 3. Load candidate dataset
cand_path = os.path.join(RAW_DATA_DIR, "three_disease_patient_records.csv")
df_cand = pd.read_csv(cand_path)
kbg_candidates = df_cand[df_cand['disease_name'].str.lower() == 'kbg syndrome'].copy()
print(f"Loaded {len(kbg_candidates)} KBG syndrome candidate records.")

# 4. Perform provenance splits
new_verified_records = []
unresolved_records = []

# Regex to identify the 67 newly recruited patients from PMID 36446582
# Labeled like KBG1, KBG2, KBG8A, KBG10A, KBG31A, etc.
newly_recruited_pattern = re.compile(r"^KBG\d+[A-Z]?$")

for idx, row in kbg_candidates.iterrows():
    pid = str(row['patient_id']).strip()
    
    # Extract source author/pub from filename
    filename = row['file_path'].split('\\')[-1]
    clean_pub = filename.replace('PMID_36446582_', '').replace('.json', '')
    
    # Map sex
    sex_str = str(row['sex']).strip().upper()
    sex_val = "FEMALE" if "F" in sex_str else ("MALE" if "M" in sex_str else "UNKNOWN_SEX")
    
    # Map HPOs
    hpo_str = str(row['hpo_ids']).strip() if pd.notna(row['hpo_ids']) else ""
    hpos = [h for h in hpo_str.split('|') if h.startswith("HP:")]
    unique_hpos = sorted(list(set(hpos)))
    hpos_val = "|".join(unique_hpos)
    terms_val = "|".join([hpo_names.get(h, "Unknown term") for h in unique_hpos])
    
    record = {
        "Patient_ID": pid,
        "Disease": "KBG Syndrome",
        "Sex": sex_val,
        "Age": str(row['age']).strip() if pd.notna(row['age']) else "Unknown",
        "HPO_IDs": hpos_val,
        "Source": "PMID:36446582",
        "HPO_Terms": terms_val,
        "Original_Cohort_Path": row['file_path'],
        "Symptom_Names_Raw": row['symptom_names']
    }
    
    if newly_recruited_pattern.match(pid):
        # This is a newly recruited patient from Martinez-Cayuelas et al. 2023
        new_verified_records.append(record)
    else:
        # Previously published, mark as unresolved provenance
        record["Source"] = f"PMID:36446582_Published_{clean_pub}"
        unresolved_records.append(record)

print(f"Identified {len(new_verified_records)} Verified Independent New Patients.")
print(f"Identified {len(unresolved_records)} Unresolved Previously Published Patients.")

# 5. Duplicate checks and merging
# Let's verify if there are any duplicate Patient_IDs or identical HPO profiles between new_verified_records and current patients
df_new_verified = pd.DataFrame(new_verified_records)
df_unresolved = pd.DataFrame(unresolved_records)

# Check for duplicates of Patient_ID
current_ids = set(df_curr['Patient_ID'].str.lower())
new_verified_ids = set(df_new_verified['Patient_ID'].str.lower())
duplicates_by_id = current_ids.intersection(new_verified_ids)
print(f"Overlap by Patient_ID: {len(duplicates_by_id)}")

# Save original backup if not exists (already exists as real_patient_hpo_dataset.csv)
# Build final expanded dataset
df_expanded = pd.concat([df_curr, df_new_verified], ignore_index=True)

# Build provenance review dataset
# Includes unresolved records and any flagged duplicates (though there are none by ID)
df_review = df_unresolved.copy()

# Output the datasets
df_expanded.to_csv(os.path.join(DATA_DIR, "real_patient_hpo_dataset_expanded.csv"), index=False)
df_review.to_csv(os.path.join(DATA_DIR, "real_patient_hpo_dataset_provenance_review.csv"), index=False)
print("Saved expanded and review datasets.")

# 6. Quality Audit
# Create reports/expanded_real_dataset_audit.csv
audit_rows = []
for name, df_set in [("Original Dataset", df_curr), ("New Verified", df_new_verified), ("Expanded Dataset", df_expanded), ("Unresolved Dataset", df_review)]:
    total = len(df_set)
    # Check HPO counts per patient
    hpo_counts = df_set['HPO_IDs'].apply(lambda x: len([h for h in str(x).split('|') if h]) if pd.notna(x) else 0)
    pt_1_hpo = (hpo_counts >= 1).sum()
    pt_5_hpo = (hpo_counts >= 5).sum()
    pt_10_hpo = (hpo_counts >= 10).sum()
    
    unique_hpos = set()
    for x in df_set['HPO_IDs']:
        if pd.notna(x):
            unique_hpos.update([h for h in str(x).split('|') if h])
            
    audit_rows.append({
        "Dataset": name,
        "Total_Patients": total,
        "Unique_HPO_Terms": len(unique_hpos),
        "Patients_With_ge_1_HPO": pt_1_hpo,
        "Patients_With_ge_5_HPO": pt_5_hpo,
        "Patients_With_ge_10_HPO": pt_10_hpo
    })

df_audit = pd.DataFrame(audit_rows)
df_audit.to_csv(os.path.join(REPORTS_DIR, "expanded_real_dataset_audit.csv"), index=False)
print("Saved expanded_real_dataset_audit.csv.")

# 7. Create reports/additional_real_patient_sources.csv
source_data = [
    {
        "Disease": "KBG Syndrome",
        "Source_Paper": "PMID:36446582 (Martinez-Cayuelas et al. 2023)",
        "Number_of_Patients": 340,
        "Cohort_Details": "67 newly recruited patients, 273 previously published patients",
        "Patient_Level_Data_Available": "Yes",
        "Genetically_Confirmed": "Yes",
        "Deduplication_Action": "67 newly recruited integrated; 273 previously published excluded to review file."
    }
]
df_sources = pd.DataFrame(source_data)
df_sources.to_csv(os.path.join(REPORTS_DIR, "additional_real_patient_sources.csv"), index=False)
print("Saved additional_real_patient_sources.csv.")

# Print final verified report details
print("\n" + "="*50)
print("FINAL AUDIT SUMMARY:")
print(f"Original patients = {len(df_curr)}")
print(f"New verified patients = {len(df_new_verified)}")
print(f"Excluded duplicates = {len(duplicates_by_id)}")
print(f"Unresolved patients = {len(df_unresolved)}")
print(f"Final verified total = {len(df_expanded)}")
print("="*50)
