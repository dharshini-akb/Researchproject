import os
import re
import json
import pandas as pd
import numpy as np

WORKSPACE_DIR = r"d:\finalresearchproject"
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")

df_final = pd.read_csv(os.path.join(DATA_DIR, "final_real_patient_hpo_dataset.csv"))
df_orig = pd.read_csv(os.path.join(RAW_DATA_DIR, "real_patient_hpo_dataset.csv"))
df_expanded = pd.read_csv(os.path.join(DATA_DIR, "real_patient_hpo_dataset_expanded.csv"))
df_review = pd.read_csv(os.path.join(DATA_DIR, "real_patient_hpo_dataset_provenance_review.csv"))
df_three = pd.read_csv(os.path.join(RAW_DATA_DIR, "three_disease_patient_records.csv"))

print("=================================================================")
print("=== 1. OVERALL DATASET SIZE & COMPOSITION ===")
print("=================================================================")
print(f"Total rows in final_real_patient_hpo_dataset.csv: {len(df_final)}")
print("\nBreakdown by Disease and Source:")
print(pd.crosstab(df_final['Disease'], df_final['Source'], margins=True))

print("\nBreakdown by Disease and Sex:")
print(pd.crosstab(df_final['Disease'], df_final['Sex'], margins=True))

print("\n=================================================================")
print("=== 2. DETAILED SOURCE BREAKDOWN FOR EACH DISEASE ===")
print("=================================================================")
for disease in ["White-Sutton Syndrome", "Xia-Gibbs Syndrome", "KBG Syndrome"]:
    sub = df_final[df_final['Disease'] == disease]
    print(f"\n--- {disease} (N = {len(sub)}) ---")
    for src in sub['Source'].unique():
        sub_src = sub[sub['Source'] == src]
        print(f"  Source: {src} (N = {len(sub_src)})")
        print(f"    Patient IDs: {sub_src['Patient_ID'].tolist()[:5]} ... {sub_src['Patient_ID'].tolist()[-2:]}")
        print(f"    Sex counts: {dict(sub_src['Sex'].value_counts())}")
        print(f"    Age range / samples: {sub_src['Age'].unique()[:5]}")
        hpo_counts = sub_src['HPO_IDs'].apply(lambda x: len(str(x).split('|')))
        print(f"    HPO count per patient: min={hpo_counts.min()}, max={hpo_counts.max()}, mean={hpo_counts.mean():.2f}")

print("\n=================================================================")
print("=== 3. PATIENT-LEVEL UNIQUENESS & INTEGRITY AUDIT ===")
print("=================================================================")
print(f"Unique Patient IDs: {df_final['Patient_ID'].nunique()} / {len(df_final)}")
print(f"Duplicate Patient IDs: {df_final['Patient_ID'].duplicated().sum()}")

# Check identical HPO profile strings
print(f"\nUnique HPO profile strings: {df_final['HPO_IDs'].nunique()} / {len(df_final)}")
dup_hpo_strings = df_final[df_final.duplicated(subset=['HPO_IDs'], keep=False)]
print(f"Patients sharing identical HPO strings: {len(dup_hpo_strings)}")
for hpo_str, group in df_final.groupby('HPO_IDs'):
    if len(group) > 1:
        print(f"\n  Shared HPO set: {hpo_str}")
        print(group[['Patient_ID', 'Disease', 'Sex', 'Age', 'Source']])

# Check identical (Disease + Sex + HPO_IDs)
df_final['full_profile'] = df_final['Disease'] + "__" + df_final['Sex'].fillna("UNKNOWN") + "__" + df_final['HPO_IDs'].fillna("")
print(f"\nUnique (Disease + Sex + HPO): {df_final['full_profile'].nunique()} / {len(df_final)}")

print("\n=================================================================")
print("=== 4. HPO VOCABULARY & FEATURE AUDIT ===")
print("=================================================================")
# All unique HPOs in full dataset
all_hpos = set()
for h_str in df_final['HPO_IDs']:
    for h in str(h_str).split('|'):
        if h.strip():
            all_hpos.add(h.strip())
print(f"Total unique HPO terms across entire 134-patient dataset: {len(all_hpos)}")

# Check HPO terms by disease
ws_hpos = set([h.strip() for h_str in df_final[df_final['Disease']=='White-Sutton Syndrome']['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])
xg_hpos = set([h.strip() for h_str in df_final[df_final['Disease']=='Xia-Gibbs Syndrome']['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])
kbg_hpos = set([h.strip() for h_str in df_final[df_final['Disease']=='KBG Syndrome']['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])

print(f"Unique HPO terms in White-Sutton (N=23): {len(ws_hpos)}")
print(f"Unique HPO terms in Xia-Gibbs (N=20): {len(xg_hpos)}")
print(f"Unique HPO terms in KBG (N=91): {len(kbg_hpos)}")

# Overlap between diseases
print(f"Overlap WS & XG: {len(ws_hpos.intersection(xg_hpos))} ({ws_hpos.intersection(xg_hpos)})")
print(f"Overlap WS & KBG: {len(ws_hpos.intersection(kbg_hpos))} ({ws_hpos.intersection(kbg_hpos)})")
print(f"Overlap XG & KBG: {len(xg_hpos.intersection(kbg_hpos))} ({xg_hpos.intersection(kbg_hpos)})")
print(f"Overlap all 3: {len(ws_hpos.intersection(xg_hpos).intersection(kbg_hpos))} ({ws_hpos.intersection(xg_hpos).intersection(kbg_hpos)})")

# Check train/val/test split HPO counts
disease_id_map = {"White-Sutton Syndrome": 0, "Xia-Gibbs Syndrome": 1, "KBG Syndrome": 2}
df_final['target'] = df_final['Disease'].map(disease_id_map)
df_final['profile_key'] = df_final['target'].astype(str) + "_" + df_final['Sex'].fillna("UNKNOWN") + "_" + df_final['HPO_IDs'].fillna("")

from sklearn.model_selection import train_test_split
groups = df_final.groupby('profile_key')
group_summaries = [{'profile_key': k, 'target': g['target'].iloc[0]} for k, g in groups]
df_groups = pd.DataFrame(group_summaries)

train_keys, temp_keys = train_test_split(df_groups['profile_key'], test_size=0.4, random_state=42, stratify=df_groups['target'])
df_temp_groups = df_groups[df_groups['profile_key'].isin(temp_keys)]
val_keys, test_keys = train_test_split(df_temp_groups['profile_key'], test_size=0.5, random_state=42, stratify=df_temp_groups['target'])

df_train = df_final[df_final['profile_key'].isin(train_keys)]
df_val = df_final[df_final['profile_key'].isin(val_keys)]
df_test = df_final[df_final['profile_key'].isin(test_keys)]

train_hpos = set([h.strip() for h_str in df_train['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])
val_hpos = set([h.strip() for h_str in df_val['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])
test_hpos = set([h.strip() for h_str in df_test['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])

print(f"\nTraining set HPOs (ML Features): {len(train_hpos)}")
print(f"Validation set HPOs: {len(val_hpos)} (OOV: {val_hpos - train_hpos})")
print(f"Test set HPOs: {len(test_hpos)} (OOV: {test_hpos - train_hpos})")
print(f"Total union of train + val + test = {len(train_hpos | val_hpos | test_hpos)}")

print("\n=================================================================")
print("=== 5. CHECK SAVED MODEL FEATURES ===")
print("=================================================================")
import joblib
rf_data = joblib.load(os.path.join(WORKSPACE_DIR, "models", "rf_model_expanded.joblib"))
print(f"Number of features in saved rf_model_expanded.joblib: {len(rf_data['feature_names'])}")
print("Feature names:")
print(rf_data['feature_names'])
