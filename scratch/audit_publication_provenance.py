import pandas as pd
import numpy as np
import os
import glob

DATA_DIR = r"d:\finalresearchproject\data"
REPORTS_DIR = r"d:\finalresearchproject\reports"

df_master = pd.read_csv(os.path.join(DATA_DIR, "expanded_real_patient_hpo_dataset.csv"))
print(f"Master dataset rows: {len(df_master)}")
print("Master dataset sources and counts:")
print(df_master['Source'].value_counts(dropna=False))

print("\nMaster dataset Provenance unique values:")
print(df_master['Provenance'].value_counts(dropna=False))

df_orig = pd.read_csv(os.path.join(DATA_DIR, "original_133_patient_dataset_backup.csv"))
print(f"\nOriginal 133 dataset sources:")
print(df_orig['Source'].value_counts(dropna=False))

df_new = pd.read_csv(os.path.join(DATA_DIR, "newly_added_patients_only.csv"))
print(f"\nNewly added dataset sources:")
print(df_new['Source_Publication'].value_counts(dropna=False))

df_rev = pd.read_csv(os.path.join(DATA_DIR, "real_patient_hpo_dataset_provenance_review.csv"))
print(f"\nProvenance review file ({len(df_rev)} rows) sources:")
print(df_rev['Source'].value_counts(dropna=False))

df_excl = pd.read_csv(os.path.join(DATA_DIR, "excluded_duplicate_patients_log.csv"))
print(f"\nExcluded log ({len(df_excl)} rows) sources:")
print(df_excl['Source'].value_counts(dropna=False))
