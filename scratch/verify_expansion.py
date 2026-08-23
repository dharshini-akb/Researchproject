import pandas as pd
import os

data_dir = r"d:\finalresearchproject\data"
path = os.path.join(data_dir, "real_patient_hpo_dataset_expanded.csv")

if os.path.exists(path):
    df = pd.read_csv(path)
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("\nDisease counts:")
    print(df['Disease'].value_counts())
    print("\nSource counts:")
    print(df['Source'].value_counts())
    print("\nUnique HPOs in expanded dataset:")
    all_hpos = set()
    for h_str in df['HPO_IDs']:
        if pd.notna(h_str):
            all_hpos.update(h_str.split('|'))
    print("Unique HPO terms:", len(all_hpos))
else:
    print("Expanded file not found")
