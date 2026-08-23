import pandas as pd
import os

raw_dir = r"d:\finalresearchproject\data\raw"
for f in ["three_disease_patient_records.csv", "selected_set1_patient_records.csv", "selected_set1_provenance_manifest.csv"]:
    path = os.path.join(raw_dir, f)
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"\nFile: {f}, Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print(df.head(3))
        # Check if there are real or synthetic indicators or sources
        if 'Source' in df.columns:
            print("Unique Sources:", df['Source'].value_counts().head(10))
        elif 'provenance' in df.columns:
            print("Unique Provenance:", df['provenance'].value_counts().head(10))
