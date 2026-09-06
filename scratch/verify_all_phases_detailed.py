import pandas as pd
import numpy as np
import json
import os
import math
from scipy import stats
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_auc_score, average_precision_score,
    brier_score_loss
)

data_path = r"d:\finalresearchproject\data\expanded_real_patient_hpo_dataset.csv"
df = pd.read_csv(data_path)

print("--- HPO Profile & Term Inspection ---")
def parse_hpo_list(val):
    if pd.isna(val):
        return []
    val = str(val).strip()
    if val.startswith("[") and val.endswith("]"):
        import ast
        try:
            return ast.literal_eval(val)
        except:
            pass
    # Split by comma or semicolon
    items = [x.strip().strip("'").strip('"') for x in val.replace(";", ",").split(",") if x.strip()]
    return items

df['hpo_list'] = df['HPO_IDs'].apply(parse_hpo_list)
all_hpos = [term for sublist in df['hpo_list'] for term in sublist]
unique_hpos = sorted(list(set(all_hpos)))
print(f"Total HPO annotations across all patients: {len(all_hpos)}")
print(f"Total Unique HPO terms across dataset: {len(unique_hpos)}")

# Check HPO terms per disease
for d in df['Disease'].unique():
    d_hpos = [term for sublist in df[df['Disease'] == d]['hpo_list'] for term in sublist]
    print(f"  Disease {d}: {len(set(d_hpos))} unique HPO terms, mean {np.mean([len(x) for x in df[df['Disease'] == d]['hpo_list']]):.2f} terms/patient")

# Profile uniqueness
df['profile_hash'] = df['hpo_list'].apply(lambda x: tuple(sorted(x)))
print(f"Total unique HPO profiles: {df['profile_hash'].nunique()}")
print(f"Duplicate HPO profiles: {len(df) - df['profile_hash'].nunique()}")

# Demographic check
print("\n--- Demographic Check ---")
print(df['Sex'].value_counts(dropna=False))
print(f"Age not null: {df['Age'].notnull().sum()}, Age null: {df['Age'].isnull().sum()}")

# Provenance Manifest Inspection
print("\n--- Provenance Manifest Inspection ---")
prov_path = r"d:\finalresearchproject\reports\expanded_cohort_provenance_manifest.csv"
df_prov = pd.read_csv(prov_path)
print(f"Provenance manifest row count: {len(df_prov)}")
print(f"Columns: {list(df_prov.columns)}")
print(f"Missing values in provenance:\n{df_prov.isnull().sum()}")
if 'Status' in df_prov.columns:
    print(f"Provenance status counts:\n{df_prov['Status'].value_counts(dropna=False)}")

# Publications Breakdown
print("\n--- Publication Inventory Detail ---")
pub_path = r"d:\finalresearchproject\reports\publication_inventory.csv"
df_pub = pd.read_csv(pub_path)
print(f"Publication rows: {len(df_pub)}")
print(df_pub[['Publication', 'Disease', 'Total_Patients_Extracted', 'Status']])
print(f"Total sum of patients: {df_pub['Total_Patients_Extracted'].sum()}")

# Check source column in dataset
print("\n--- Sources in Main Dataset ---")
print(df['Source'].value_counts(dropna=False))
print(f"Unique source entries in main dataset: {df['Source'].nunique()}")

# Splits & Leakage Check
print("\n--- Splits and Leakage Verification ---")
# Let's inspect preprocessing/train_evaluate_expanded.py to replicate the exact split
import importlib.util
spec = importlib.util.spec_from_file_location("train_eval", r"d:\finalresearchproject\preprocessing\train_evaluate_expanded.py")
train_eval = importlib.util.module_from_spec(spec)

# Let's run train_evaluate_expanded logic or inspect the saved model
