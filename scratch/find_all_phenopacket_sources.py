import os
import glob
import pandas as pd
import json

WORKSPACE_DIR = r"d:\finalresearchproject"
all_files = []
for root, dirs, files in os.walk(WORKSPACE_DIR):
    for f in files:
        if f.endswith(('.json', '.csv', '.xlsx', '.obo', '.py', '.md')):
            all_files.append(os.path.join(root, f))

print(f"Total files found in workspace: {len(all_files)}")

# Find all files with phenopacket in name or path
pheno_files = [f for f in all_files if 'phenopacket' in f.lower() or 'ankrd11' in f.lower() or 'pogz' in f.lower() or 'ahdc1' in f.lower()]
print(f"Phenopacket/gene related files: {len(pheno_files)}")
for pf in pheno_files[:30]:
    print("  ", pf)

# Let's inspect real_patient_hpo_dataset_provenance_review.csv
rev_df = pd.read_csv(os.path.join(WORKSPACE_DIR, "data", "real_patient_hpo_dataset_provenance_review.csv"))
print("\nProvenance review columns:", list(rev_df.columns))
print("Sample rows:")
print(rev_df[['Patient_ID', 'Disease', 'Source', 'Original_Cohort_Path', 'Symptom_Names_Raw']].head(20))
