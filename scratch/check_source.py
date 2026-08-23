import pandas as pd
df = pd.read_csv(r"d:\finalresearchproject\data\raw\real_patient_hpo_dataset.csv")
print("Unique Diseases in real_patient_hpo_dataset.csv:")
print(df['Disease'].value_counts())
print("\nUnique Sources in real_patient_hpo_dataset.csv:")
print(df['Source'].value_counts())
