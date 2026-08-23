import pandas as pd

df_curr = pd.read_csv(r"d:\finalresearchproject\data\raw\real_patient_hpo_dataset.csv")
kbg_curr = df_curr[df_curr['Disease'].str.lower() == 'kbg syndrome']

df_cand = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg_cand = df_cand[df_cand['disease_name'].str.lower() == 'kbg syndrome']

unmatched = ['KBG_5435101_Ockeloen', 'KBG_5435101_Walz']
for name in unmatched:
    row = kbg_curr[kbg_curr['Patient_ID'] == name].iloc[0]
    hpos = set(row['HPO_IDs'].split('|'))
    print(f"\nSearching match for: {name} (Sex: {row['Sex']}, Age: {row['Age']}) - HPOs: {row['HPO_IDs']}")
    
    # Search candidates
    matches = []
    for c_idx, c_row in kbg_cand.iterrows():
        c_hpos = set(c_row['hpo_ids'].split('|')) if pd.notna(c_row['hpo_ids']) else set()
        overlap = len(hpos.intersection(c_hpos))
        if overlap >= 2:
            matches.append((c_row['patient_id'], c_row['sex'], c_row['age'], c_row['hpo_ids'], overlap))
            
    matches.sort(key=lambda x: x[4], reverse=True)
    print("Top matches in candidates:")
    for m in matches[:5]:
        print(f"  {m[0]} (Sex: {m[1]}, Age: {m[2]}) - Overlap: {m[4]} - HPOs: {m[3]}")
