import pandas as pd

df_man = pd.read_csv("data/raw/selected_set1_provenance_manifest.csv")
print("=== MANIFEST COLUMNS ===")
print(df_man.columns.tolist())
print(df_man.head())

df_rec = pd.read_csv("data/raw/selected_set1_patient_records.csv")
print("\n=== PATIENT RECORDS COLUMNS ===")
print(df_rec.columns.tolist())
print(df_rec.head())

print("\n--- White-Sutton in Set 1 Manifest ---")
ws_man = df_man[df_man['disease_name'].str.lower().str.contains('white-sutton')]
print(f"Total WS cases in manifest: {len(ws_man)}")
print(ws_man['pmid'].value_counts())

print("\n--- Xia-Gibbs in Set 1 Manifest ---")
xg_man = df_man[df_man['disease_name'].str.lower().str.contains('xia-gibbs')]
print(f"Total XG cases in manifest: {len(xg_man)}")
print(xg_man['pmid'].value_counts())
