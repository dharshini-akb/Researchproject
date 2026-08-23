import pandas as pd
df_cand = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg_cand = df_cand[df_cand['disease_name'].str.lower() == 'kbg syndrome']
def parse_candidate(row):
    filename = row['file_path'].split('\\')[-1]
    clean_name = filename.replace('PMID_36446582_', '').replace('.json', '')
    return clean_name

kbg_cand_papers = kbg_cand.apply(parse_candidate, axis=1)
clean_unique = sorted(kbg_cand_papers.unique())
print("Unique papers (50 to 106):")
for item in clean_unique[50:]:
    print(item)
