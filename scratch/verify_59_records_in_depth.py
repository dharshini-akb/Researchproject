import os
import pandas as pd
import numpy as np

DATA_DIR = r"d:\finalresearchproject\data"
REPORTS_DIR = r"d:\finalresearchproject\reports"

# 1. Load excluded log
df_excl = pd.read_csv(os.path.join(DATA_DIR, "excluded_duplicate_patients_log.csv"))
print(f"Total rows in excluded_duplicate_patients_log.csv: {len(df_excl)}")
print("Columns in excluded log:", list(df_excl.columns))

# Print all 59 rows
print("\n--- ALL 59 ROWS IN EXCLUDED LOG ---")
for idx, row in df_excl.iterrows():
    print(f"{idx+1:02d}. Patient_ID: {row['Patient_ID']:<20} | Source: {row['Source']:<20} | Disease: {row['Disease']:<15} | Reason: {row['Reason']}")

# Categorize the 59 rows
low_2016_rows = df_excl[df_excl['Source'].str.startswith('Low_2016')]
low_2017_rows = df_excl[df_excl['Source'] == 'Low2017']
ockeloen_rows = df_excl[df_excl['Source'].str.startswith('Ockeloen2015')]
walz_rows = df_excl[df_excl['Source'].str.startswith('Walz2015')]

print(f"\nBreakdown of 59 rows:")
print(f"  - Low_2016 rows:     {len(low_2016_rows)}")
print(f"  - Low2017 rows:      {len(low_2017_rows)}")
print(f"  - Ockeloen2015 rows: {len(ockeloen_rows)}")
print(f"  - Walz2015 rows:     {len(walz_rows)}")
print(f"  - TOTAL:             {len(low_2016_rows) + len(low_2017_rows) + len(ockeloen_rows) + len(walz_rows)}")

# Let's inspect the Low_2016 rows in detail
print("\nLow_2016 patient IDs:")
print(low_2016_rows['Patient_ID'].tolist())

# Let's inspect where the '27 Low cases' vs '32 Low cases' and '6 insufficient' narrative originated in earlier scratch scripts!
# Let's check real_patient_hpo_dataset_provenance_review.csv
rev_df = pd.read_csv(os.path.join(DATA_DIR, "real_patient_hpo_dataset_provenance_review.csv"))
print(f"\nTotal rows in review file: {len(rev_df)}")

# Check HPO terms in review file
rev_low = rev_df[rev_df['Source'].str.contains('Low', case=False, na=False)]
print(f"Low rows in review file: {len(rev_low)}")
rev_ock = rev_df[rev_df['Source'].str.contains('Ockeloen', case=False, na=False)]
print(f"Ockeloen rows in review file: {len(rev_ock)}")
rev_walz = rev_df[rev_df['Source'].str.contains('Walz', case=False, na=False)]
print(f"Walz rows in review file: {len(rev_walz)}")

# Check if any rows in review file had 0 valid HPO terms
no_hpo_rows = []
for idx, row in rev_df.iterrows():
    hpo_str = str(row['HPO_IDs']).strip() if pd.notna(row['HPO_IDs']) else ""
    hpos = [h.strip() for h in hpo_str.split('|') if h.strip().startswith('HP:')]
    if len(hpos) < 1:
        no_hpo_rows.append(row)
print(f"Rows in review file with < 1 HPO terms: {len(no_hpo_rows)}")
