import pandas as pd
import numpy as np
import json
import os
import math
from scipy import stats

print("=== 1. VERIFY FINAL DATASET ===")
data_path = r"d:\finalresearchproject\data\expanded_real_patient_hpo_dataset.csv"
df = pd.read_csv(data_path)
print(f"RAW ROWS: {len(df)}")
print(f"COLUMNS: {list(df.columns)}")
print(f"UNIQUE Patient_IDs: {df['Patient_ID'].nunique()}")
print(f"Duplicate Patient_IDs count: {df['Patient_ID'].duplicated().sum()}")
disease_counts = df['Disease'].value_counts()
print(f"DISEASE COUNTS:\n{disease_counts}")

# Check missing values
missing_per_col = df.isnull().sum()
print(f"Total missing cells across dataset: {missing_per_col.sum()}")
if missing_per_col.sum() > 0:
    print(f"Columns with missing values:\n{missing_per_col[missing_per_col > 0]}")

# Check HPO profile uniqueness
hpo_cols = [c for c in df.columns if c.startswith("HP:")]
print(f"Total HPO columns in dataset: {len(hpo_cols)}")
profile_strings = df[hpo_cols].astype(str).agg(''.join, axis=1)
print(f"Unique HPO phenotype profiles: {profile_strings.nunique()}")
print(f"Duplicate HPO phenotype profiles: {len(df) - profile_strings.nunique()}")

# Check for aggregate rows (like 'Total' or containing 'Total' in Patient_ID)
agg_rows = df[df['Patient_ID'].str.contains("total|summary|aggregate", case=False, na=False)]
print(f"Aggregate rows in dataset: {len(agg_rows)}")

# Check sex column
if 'Sex' in df.columns:
    print(f"Sex counts:\n{df['Sex'].value_counts(dropna=False)}")

print("\n=== 2. VERIFY 59 EXCLUDED RECORDS ===")
excl_path = r"d:\finalresearchproject\data\excluded_duplicate_patients_log.csv"
if os.path.exists(excl_path):
    df_excl = pd.read_csv(excl_path)
    print(f"EXCLUDED ROWS: {len(df_excl)}")
    print(f"Columns in exclusion log: {list(df_excl.columns)}")
    if 'Status' in df_excl.columns:
        print(f"Status distribution in exclusions:\n{df_excl['Status'].value_counts(dropna=False)}")
    if 'Reason' in df_excl.columns:
        print(f"Reason distribution in exclusions:\n{df_excl['Reason'].value_counts(dropna=False)}")
    if 'Disease' in df_excl.columns:
        print(f"Disease distribution in exclusions:\n{df_excl['Disease'].value_counts(dropna=False)}")
else:
    print("Excluded file not found!")

print("\n=== 3. VERIFY PUBLICATION COUNT ===")
pub_path = r"d:\finalresearchproject\reports\publication_inventory.csv"
if os.path.exists(pub_path):
    df_pub = pd.read_csv(pub_path)
    print(f"PUBLICATION INVENTORY ROWS: {len(df_pub)}")
    print(df_pub[['Publication', 'Disease', 'Total_Patients_Extracted', 'Status']])
    
    # Check literature case reports entry
    lit_row = df_pub[df_pub['Publication'].str.contains("Literature Case Reports", case=False, na=False)]
    if not lit_row.empty:
        print(f"Literature case reports entry specifies: {lit_row['Publication'].values[0]}")
        
    print(f"Sum of Total_Patients_Extracted in inventory: {df_pub['Total_Patients_Extracted'].sum()}")
