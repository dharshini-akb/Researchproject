import os
import re
import sys
import xml.etree.ElementTree as ET
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = r"d:\finalresearchproject"
SCRATCH_DIR = os.path.join(WORKSPACE_DIR, "scratch")
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")

# Load HPO ontology names
def parse_hpo_obo():
    obo_path = os.path.join(RAW_DATA_DIR, "hp.obo")
    if not os.path.exists(obo_path):
        return {}
    hpo_map = {}
    current_id, current_name = None, None
    with open(obo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if current_id and current_name:
                    hpo_map[current_id] = current_name
                current_id, current_name = None, None
            elif line.startswith("id:"):
                current_id = line.split("id:")[1].strip()
            elif line.startswith("name:"):
                current_name = line.split("name:")[1].strip()
        if current_id and current_name:
            hpo_map[current_id] = current_name
    return hpo_map

hpo_names = parse_hpo_obo()
print(f"Loaded {len(hpo_names)} HPO terms from hp.obo (release 2026-06-23).")

def element_to_text(el):
    return "".join(el.itertext()).strip() if el is not None else ""

# 1. Base 133 clean patients (without WhiteSutton_Total)
df_base = pd.read_csv(os.path.join(DATA_DIR, "final_real_patient_hpo_dataset.csv"))
df_clean_base = df_base[df_base['Patient_ID'] != 'WhiteSutton_Total'].copy()
print(f"\n1. Baseline genuine individual patients: {len(df_clean_base)}")
print(df_clean_base['Disease'].value_counts())

# Fix Xia-Gibbs baseline sex if needed (Jiang 2018 XML table had age/sex parsed into Age column)
for idx, row in df_clean_base.iterrows():
    if row['Disease'] == 'Xia-Gibbs Syndrome' and row['Sex'] == 'UNKNOWN_SEX':
        age_val = str(row['Age']).strip().upper()
        if age_val == 'F':
            df_clean_base.at[idx, 'Sex'] = 'FEMALE'
            df_clean_base.at[idx, 'Age'] = 'Unknown'
        elif age_val == 'M':
            df_clean_base.at[idx, 'Sex'] = 'MALE'
            df_clean_base.at[idx, 'Age'] = 'Unknown'

print("Fixed baseline Xia-Gibbs sex values.")
print(df_clean_base['Sex'].value_counts())
