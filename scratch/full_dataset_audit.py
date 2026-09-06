import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

WORKSPACE_DIR = r"d:\finalresearchproject"
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")

# 1. Load final dataset
df_final = pd.read_csv(os.path.join(DATA_DIR, "final_real_patient_hpo_dataset.csv"))
print(f"Total rows in final_real_patient_hpo_dataset.csv: {len(df_final)}")
print(f"Columns: {df_final.columns.tolist()}")

# 2. Check Disease distribution & Sources
print("\n--- Disease & Source Crosstab ---")
print(pd.crosstab(df_final['Disease'], df_final['Source'], margins=True))

# 3. Check Sex distribution
print("\n--- Sex Distribution ---")
print(pd.crosstab(df_final['Disease'], df_final['Sex'], margins=True))

# 4. Check Age distribution
print("\n--- Age Info Summary ---")
for disease in df_final['Disease'].unique():
    subset = df_final[df_final['Disease'] == disease]
    print(f"{disease}: Non-null age count = {subset['Age'].notna().sum()}/{len(subset)}")
    print(f"Sample ages: {subset['Age'].dropna().unique()[:8]}")

# 5. Check HPO terms count across whole dataset
all_hpos = set()
for h_str in df_final['HPO_IDs']:
    if pd.notna(h_str):
        all_hpos.update([h.strip() for h in str(h_str).split('|') if h.strip()])
print(f"\nTotal unique HPO terms across all 134 patients: {len(all_hpos)}")

# Check HPOs per patient
hpo_counts_per_pt = df_final['HPO_IDs'].apply(lambda x: len([h for h in str(x).split('|') if h.strip()]))
print(f"HPO terms per patient: Min={hpo_counts_per_pt.min()}, Max={hpo_counts_per_pt.max()}, Mean={hpo_counts_per_pt.mean():.2f}, Median={hpo_counts_per_pt.median()}")

# Disease wise HPO count
for d in df_final['Disease'].unique():
    sub = df_final[df_final['Disease'] == d]
    sub_counts = sub['HPO_IDs'].apply(lambda x: len([h for h in str(x).split('|') if h.strip()]))
    sub_unique_hpos = set()
    for h_str in sub['HPO_IDs']:
        sub_unique_hpos.update([h.strip() for h in str(h_str).split('|') if h.strip()])
    print(f"{d} (n={len(sub)}): Unique HPOs={len(sub_unique_hpos)}, per patient mean={sub_counts.mean():.2f} (range {sub_counts.min()}-{sub_counts.max()})")

# 6. Check duplicates & uniqueness
print("\n--- Uniqueness & Duplication Check ---")
print(f"Unique Patient_IDs: {df_final['Patient_ID'].nunique()} / {len(df_final)}")
# Check identical phenotype-sex profiles
df_final['profile_key'] = df_final['Disease'] + "_" + df_final['Sex'].fillna("UNKNOWN") + "_" + df_final['HPO_IDs'].fillna("")
print(f"Unique Phenotype-Sex-Disease Profiles: {df_final['profile_key'].nunique()} / {len(df_final)}")
dup_profiles = df_final[df_final.duplicated(subset=['profile_key'], keep=False)]
print(f"Rows sharing identical Profile: {len(dup_profiles)}")
if len(dup_profiles) > 0:
    print("Identical profile rows:")
    print(dup_profiles[['Patient_ID', 'Disease', 'Sex', 'Source', 'HPO_IDs']])

# 7. Check Training / Val / Test split reproduction
disease_id_map = {
    "White-Sutton Syndrome": 0, "White-Sutton syndrome": 0,
    "Xia-Gibbs Syndrome": 1, "Xia-Gibbs syndrome": 1,
    "KBG Syndrome": 2, "KBG syndrome": 2
}
df_final['target'] = df_final['Disease'].map(disease_id_map)
df_final['group_key'] = df_final['target'].astype(str) + "_" + df_final['Sex'].fillna("UNKNOWN") + "_" + df_final['HPO_IDs'].fillna("")

groups = df_final.groupby('group_key')
group_summaries = []
for key, group in groups:
    target = group['target'].iloc[0]
    group_summaries.append({'group_key': key, 'target': target})
df_groups = pd.DataFrame(group_summaries)

train_keys, temp_keys = train_test_split(
    df_groups['group_key'], test_size=0.4, random_state=42, stratify=df_groups['target']
)
df_temp_groups = df_groups[df_groups['group_key'].isin(temp_keys)]
val_keys, test_keys = train_test_split(
    df_temp_groups['group_key'], test_size=0.5, random_state=42, stratify=df_temp_groups['target']
)

df_train = df_final[df_final['group_key'].isin(train_keys)].copy()
df_val = df_final[df_final['group_key'].isin(val_keys)].copy()
df_test = df_final[df_final['group_key'].isin(test_keys)].copy()

print(f"\nSplit sizes: Train={len(df_train)}, Val={len(df_val)}, Test={len(df_test)}")
print("Train disease counts:\n", df_train['Disease'].value_counts())
print("Val disease counts:\n", df_val['Disease'].value_counts())
print("Test disease counts:\n", df_test['Disease'].value_counts())

train_hpos = set()
for h_str in df_train['HPO_IDs']:
    train_hpos.update([h.strip() for h in str(h_str).split('|') if h.strip()])
print(f"\nUnique HPOs in Training set (Vocabulary size): {len(train_hpos)}")

val_hpos = set()
for h_str in df_val['HPO_IDs']:
    val_hpos.update([h.strip() for h in str(h_str).split('|') if h.strip()])
val_oov = val_hpos - train_hpos
print(f"Val unique HPOs: {len(val_hpos)}, Val OOV HPOs: {len(val_oov)} ({val_oov})")

test_hpos = set()
for h_str in df_test['HPO_IDs']:
    test_hpos.update([h.strip() for h in str(h_str).split('|') if h.strip()])
test_oov = test_hpos - train_hpos
print(f"Test unique HPOs: {len(test_hpos)}, Test OOV HPOs: {len(test_oov)} ({test_oov})")

# 8. Check vocabulary list
print(f"\nTraining HPO Vocabulary (76 features):")
print(sorted(list(train_hpos)))
