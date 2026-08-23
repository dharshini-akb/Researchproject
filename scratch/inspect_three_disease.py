import pandas as pd
import os

path = r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv"
df = pd.read_csv(path)
print("Unique diseases in three_disease_patient_records.csv:")
print(df['disease_name'].value_counts())

print("\nSample values of file_path:")
print(df['file_path'].head(10))

print("\nSample values of disease_id:")
print(df['disease_id'].value_counts())
