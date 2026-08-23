import pandas as pd

df = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg = df[df['disease_name'] == 'KBG syndrome']

kbg_ids = kbg[kbg['patient_id'].str.startswith('KBG', na=False)]
print("Number of KBGxx patients:", len(kbg_ids))
print("Sample KBGxx patient rows:")
print(kbg_ids[['patient_id', 'file_path', 'source_metadata']].head(10))
