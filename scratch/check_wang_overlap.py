import pandas as pd

df_curr = pd.read_csv(r"d:\finalresearchproject\data\raw\real_patient_hpo_dataset.csv")
kbg_curr_894 = df_curr[df_curr['Source'] == 'PMC8948816']
print("Current PMC8948816 patients count:", len(kbg_curr_894))

df_cand = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg_cand = df_cand[df_cand['disease_name'].str.lower() == 'kbg syndrome']

# Print details of current PMC8948816 patients
print("\nCurrent PMC8948816 Patients:")
print(kbg_curr_894[['Patient_ID', 'Sex', 'Age', 'HPO_IDs']])

# Find candidates that have overlapping HPO_IDs
for idx, row in kbg_curr_894.iterrows():
    hpos = set(row['HPO_IDs'].split('|'))
    # Search candidates for high overlap of HPO_IDs
    best_overlap = 0
    best_candidate = None
    for c_idx, c_row in kbg_cand.iterrows():
        c_hpos = set(c_row['hpo_ids'].split('|')) if pd.notna(c_row['hpo_ids']) else set()
        overlap = len(hpos.intersection(c_hpos))
        if overlap > best_overlap:
            best_overlap = overlap
            best_candidate = c_row
            
    if best_candidate is not None:
        print(f"\nCurrent patient: {row['Patient_ID']} ({row['Sex']}, {row['Age']}) - HPOs: {len(hpos)}")
        print(f"Best matching candidate: {best_candidate['patient_id']} - HPOs: {len(set(best_candidate['hpo_ids'].split('|')))} - Overlap: {best_overlap}")
        print(f"File Path: {best_candidate['file_path']}")
        print(f"Candidate HPOs: {best_candidate['hpo_ids']}")
