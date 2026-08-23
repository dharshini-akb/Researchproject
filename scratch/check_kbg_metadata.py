import pandas as pd

df = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg = df[df['disease_name'] == 'KBG syndrome']

# Find candidate records containing "Low" or "Crippa" or "8948816" or "5435101"
print("Candidate patient IDs containing Crippa:")
print(kbg[kbg['patient_id'].str.contains("Crippa", case=False, na=False)]['patient_id'].unique())

print("\nCandidate patient IDs containing Low:")
print(kbg[kbg['patient_id'].str.contains("Low", case=False, na=False)]['patient_id'].unique())

print("\nComparing a current patient from Low et al. (PMC5435101) with candidates:")
df_curr = pd.read_csv(r"d:\finalresearchproject\data\raw\real_patient_hpo_dataset.csv")
kbg_curr = df_curr[df_curr['Source'] == 'PMC5435101']
print("Current patient 1 from PMC5435101:")
print(kbg_curr.iloc[0])

# Find matching candidate for the first current patient based on sex and age
print("\nMatching candidates from 'Low_2016' or similar:")
low_candidates = kbg[kbg['file_path'].str.contains("Low", case=False, na=False)]
print(low_candidates[['patient_id', 'sex', 'age', 'hpo_ids']].head(10))
