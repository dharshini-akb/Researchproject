import pandas as pd

# Load current real patient dataset
df_current = pd.read_csv(r"d:\finalresearchproject\data\raw\real_patient_hpo_dataset.csv")
kbg_current = df_current[df_current['Disease'].str.lower() == 'kbg syndrome']
print(f"Current KBG patients: {len(kbg_current)}")

# Load the candidate KBG patients from three_disease_patient_records.csv
df_candidates = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg_candidates = df_candidates[df_candidates['disease_name'].str.lower() == 'kbg syndrome']
print(f"Candidate KBG patients: {len(kbg_candidates)}")

# Let's inspect some candidate records to see what papers they are from (using file_path)
# Example file_path: notebooks\ANKRD11\phenopackets\PMID_36446582_Gnazzo_2020_P24.json
# Let's extract the author name / paper year from patient_id and file_path
paper_names = kbg_candidates['file_path'].apply(lambda x: x.split('\\')[-1].split('_')[2] if len(x.split('\\')[-1].split('_')) > 2 else 'Unknown')
print("\nCandidate papers count:")
print(paper_names.value_counts())

# Let's check if any candidate matches current patient IDs or clinical features
# Let's check for overlap based on:
# 1. HPO profiles (sorted list of HPO IDs)
# 2. Patient ID patterns
current_hpo_sets = set(frozenset(h.split('|')) for h in kbg_current['HPO_IDs'] if pd.notna(h))
candidate_hpo_sets = [frozenset(h.split('|')) for h in kbg_candidates['hpo_ids'] if pd.notna(h)]

overlap_count = 0
for hs in candidate_hpo_sets:
    if hs in current_hpo_sets:
        overlap_count += 1
print(f"\nNumber of candidate profiles that EXACTLY match a current KBG profile's HPO set: {overlap_count}")

# Check if the papers PMC8948816 and PMC5435101 are in the candidate dataset.
# PMC8948816 is a 2022 paper on Chinese cases by Wang et al. (or another Chinese author).
# PMC5435101 is a 2017 paper by Low et al.
# Let's see if files contain "Wang" or "Low"
contains_low = kbg_candidates['file_path'].str.contains("Low", case=False).sum()
contains_wang = kbg_candidates['file_path'].str.contains("Wang", case=False).sum()
print(f"Candidates containing 'Low': {contains_low}")
print(f"Candidates containing 'Wang': {contains_wang}")
