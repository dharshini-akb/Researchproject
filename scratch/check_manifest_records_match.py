import pandas as pd

df_man = pd.read_csv("data/raw/selected_set1_provenance_manifest.csv")
df_rec = pd.read_csv("data/raw/selected_set1_patient_records.csv")

print("Manifest length:", len(df_man))
print("Records length:", len(df_rec))

# Check overlap of case_id
common_ids = set(df_man['final_case_id']).intersection(set(df_rec['case_id']))
print("Common case IDs:", len(common_ids))

# Let's inspect records that match manifest
df_valid_records = df_rec[df_rec['case_id'].isin(df_man['final_case_id'])].copy()
print("Valid records count:", len(df_valid_records))
print("Valid records by disease:\n", df_valid_records['disease_name'].value_counts())

# Check sample rows
print("\nSample White-Sutton records:")
ws_recs = df_valid_records[df_valid_records['disease_name'].str.lower().str.contains('white-sutton')]
print(ws_recs[['case_id', 'patient_id', 'sex', 'age', 'pmid', 'hpo_count', 'hpo_ids']].head(10))

print("\nSample Xia-Gibbs records:")
xg_recs = df_valid_records[df_valid_records['disease_name'].str.lower().str.contains('xia-gibbs')]
print(xg_recs[['case_id', 'patient_id', 'sex', 'age', 'pmid', 'hpo_count', 'hpo_ids']].head(10))
