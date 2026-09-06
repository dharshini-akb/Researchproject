import pandas as pd

df = pd.read_csv("data/raw/three_disease_patient_records.csv")
print("Total rows:", len(df))
print("Columns:", df.columns.tolist())
print("\nDisease distribution:")
print(df['disease_name'].value_counts())
print("\nSample rows:")
print(df.head(10))
