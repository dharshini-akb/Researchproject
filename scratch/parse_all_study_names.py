import pandas as pd
import numpy as np
import os
import re

DATA_DIR = r"d:\finalresearchproject\data"
rev_df = pd.read_csv(os.path.join(DATA_DIR, "real_patient_hpo_dataset_provenance_review.csv"))
df_master = pd.read_csv(os.path.join(DATA_DIR, "expanded_real_patient_hpo_dataset.csv"))
df_excl = pd.read_csv(os.path.join(DATA_DIR, "excluded_duplicate_patients_log.csv"))

print("=== ALL SOURCES IN PROVENANCE REVIEW FILE (266 rows) ===")
# Parse the author and year from Source
sources_raw = rev_df['Source'].apply(lambda x: str(x).replace('PMID:36446582_Published_', ''))

def extract_study_name(src):
    # e.g., Goldenberg2016_P1 -> Goldenberg 2016
    # Gnazzo, 2020_P1 -> Gnazzo 2020
    # Kutkowska-Kazmierczak2021_P1 -> Kutkowska-Kazmierczak 2021
    # Low_2016_P1_19 -> Low 2016
    # Alves_2019 -> Alves 2019
    s = src.replace('_', ' ').replace(',', ' ')
    # Match author + 4-digit year
    m = re.search(r'([A-Za-z\-]+)\s*(\d{4})', s)
    if m:
        return f"{m.group(1)} et al. ({m.group(2)})"
    return s

study_names = sources_raw.apply(extract_study_name)
print(study_names.value_counts())
print(f"Total unique study groupings in review file: {study_names.nunique()}")

print("\n=== SOURCES IN EXCLUSIONS (59 rows) ===")
excl_studies = df_excl['Source'].apply(extract_study_name)
print(excl_studies.value_counts())

print("\n=== SOURCES IN RETAINED NEW PATIENTS FROM REVIEW (207 rows) ===")
retained_rev_sources = df_master[df_master['Source'].str.startswith('Literature cohort')]['Source']
retained_studies = retained_rev_sources.apply(lambda x: extract_study_name(str(x).replace('Literature cohort (', '').replace(')', '')))
print(retained_studies.value_counts())
print(f"Total distinct study groupings in retained review cases: {retained_studies.nunique()}")
print(f"Sum of patients from these retained review studies: {len(retained_rev_sources)}")
