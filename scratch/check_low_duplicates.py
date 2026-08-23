import pandas as pd

df_curr = pd.read_csv(r"d:\finalresearchproject\data\raw\real_patient_hpo_dataset.csv")
kbg_curr_low = df_curr[df_curr['Source'] == 'PMC5435101']
print("Current PMC5435101 patients count:", len(kbg_curr_low))

df_cand = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg_cand_low = df_cand[df_cand['file_path'].str.contains("Low", case=False, na=False)]
print("Candidate Low patients count:", len(kbg_cand_low))

# Let's see if we can find exact matching files or patient IDs
for idx, row in kbg_curr_low.iterrows():
    # Current ID is like KBG_5435101_19
    curr_id_num = row['Patient_ID'].split('_')[-1]
    
    # Search candidate Low records where patient_id has that number at the end, e.g. Low_2016_P1_19 or Low_2016_30_28
    matched = None
    for c_idx, c_row in kbg_cand_low.iterrows():
        c_id = c_row['patient_id']
        # Extract number in parentheses or at the end
        if f"({curr_id_num})" in c_id or c_id.endswith(f"_{curr_id_num}"):
            matched = c_row
            break
            
    if matched is not None:
        print(f"Current: {row['Patient_ID']} ({row['Sex']}, {row['Age']}) matched with Candidate: {matched['patient_id']} ({matched['sex']}, {matched['age']})")
    else:
        # Search by HPO overlap
        print(f"Current: {row['Patient_ID']} ({row['Sex']}, {row['Age']}) NOT matched by ID.")
