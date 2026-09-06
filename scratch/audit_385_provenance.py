import os
import pandas as pd
import numpy as np

WORKSPACE_DIR = r"d:\finalresearchproject"
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "reports")

df_385 = pd.read_csv(os.path.join(DATA_DIR, "expanded_real_patient_hpo_dataset.csv"))
print(f"Total rows in expanded_real_patient_hpo_dataset.csv: {len(df_385)}")
print(df_385.info())

# Disease breakdown
print("\n--- Disease Breakdown ---")
print(df_385['Disease'].value_counts())

# Source breakdown
print("\n--- Source Breakdown ---")
print(df_385['Source'].value_counts())

# Sex breakdown
print("\n--- Sex Breakdown ---")
print(df_385['Sex'].value_counts(dropna=False))

# Age breakdown
print("\n--- Age Info ---")
print("Non-null Age count:", df_385['Age'].notna().sum())
print("Unique Age samples:", df_385['Age'].dropna().unique()[:15])

# Check duplicate Patient_IDs
print("\n--- Patient ID Uniqueness ---")
print("Unique Patient_IDs:", df_385['Patient_ID'].nunique())
print("Duplicate Patient_IDs count:", df_385['Patient_ID'].duplicated().sum())

# Check duplicate HPO profile strings
print("\n--- Phenotypic Profile Uniqueness ---")
df_385['profile_key'] = df_385['Disease'] + "_" + df_385['Sex'].fillna("UNKNOWN") + "_" + df_385['HPO_IDs'].fillna("")
print("Unique (Disease + Sex + HPO_IDs) profiles:", df_385['profile_key'].nunique())

# Check HPO count per patient
hpo_counts = df_385['HPO_IDs'].apply(lambda x: len([h for h in str(x).split('|') if h.strip()]))
print("\nHPO count stats per patient:")
print(f"Min: {hpo_counts.min()}, Max: {hpo_counts.max()}, Mean: {hpo_counts.mean():.2f}, Median: {hpo_counts.median()}")
print(f"Patients with 0 HPOs: {(hpo_counts == 0).sum()}")
print(f"Patients with 1-3 HPOs: {(hpo_counts <= 3).sum()}")

# Check all unique HPOs
all_hpos = set([h.strip() for h_str in df_385['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])
print(f"Total unique HPO terms across all 385 patients: {len(all_hpos)}")

# Check HPO ontology file
obo_path = os.path.join(DATA_DIR, "raw", "hp.obo")
with open(obo_path, "r", encoding="utf-8") as f:
    obo_lines = [f.readline() for _ in range(15)]
print("\nHPO obo header:")
print("".join(obo_lines[:5]))

# Validate every single HPO ID against hp.obo
valid_hpos = set()
with open(obo_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("id: HP:"):
            valid_hpos.add(line.strip().split("id: ")[1])

invalid_hpos = all_hpos - valid_hpos
print(f"Invalid HPO IDs in dataset: {len(invalid_hpos)} ({invalid_hpos})")
