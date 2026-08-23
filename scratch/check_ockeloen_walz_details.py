import pandas as pd

df_cand = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg_cand = df_cand[df_cand['disease_name'].str.lower() == 'kbg syndrome']

# Filter candidates matching Ockeloen or Walz
ock_cand = kbg_cand[kbg_cand['file_path'].str.contains("Ockeloen", case=False, na=False)]
print(f"Ockeloen candidates: {len(ock_cand)}")
print(ock_cand[['patient_id', 'sex', 'age', 'hpo_ids']].head(5))

walz_cand = kbg_cand[kbg_cand['file_path'].str.contains("Walz", case=False, na=False)]
print(f"\nWalz candidates: {len(walz_cand)}")
print(walz_cand[['patient_id', 'sex', 'age', 'hpo_ids']].head(5))
