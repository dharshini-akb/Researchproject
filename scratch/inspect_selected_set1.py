import pandas as pd

df = pd.read_csv(r"d:\finalresearchproject\data\raw\selected_set1_patient_records.csv")
print("Total rows:", len(df))
print(df['disease_name'].value_counts())

print("\nSample values of file_path:")
print(df['file_path'].head(5))

print("\nSample source metadata:")
print(df['source_metadata'].head(5))
