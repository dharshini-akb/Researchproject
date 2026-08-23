import pandas as pd

df = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg = df[df['disease_name'] == 'KBG syndrome']
print("KBG patient records count:", len(kbg))
print("First 10 unique patient IDs in KBG:")
print(kbg['patient_id'].unique()[:20])

# Let's count how many have different file_path prefixes
print("\nUnique file path prefixes:")
print(kbg['file_path'].apply(lambda x: x.split('\\')[2] if len(x.split('\\')) > 2 else x).value_counts())

# Check a sample of file_path values to see the actual filenames
print("\nSample file paths:")
for path in kbg['file_path'].sample(10, random_state=42):
    print(path)
