import pandas as pd
import json

df = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
print("Total rows:", len(df))
print(df['disease_name'].value_counts())

# Filter for KBG syndrome
kbg = df[df['disease_name'] == 'KBG syndrome']
print("\nKBG syndrome rows:", len(kbg))
print("First 5 rows of KBG:")
print(kbg[['patient_id', 'sex', 'age', 'hpo_count', 'file_path']].head(5))

# Check source metadata
print("\nUnique source metadata values (top 10):")
print(kbg['source_metadata'].value_counts().head(10))

# Try to extract PMC/PMID from file_path or source_metadata
print("\nExtracting PMIDs:")
pmids = kbg['file_path'].apply(lambda x: x.split('\\')[-1].split('_')[1] if 'PMID_' in x else 'Unknown')
print(pmids.value_counts())
