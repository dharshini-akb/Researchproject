import pandas as pd
import re

df_curr = pd.read_csv(r"d:\finalresearchproject\data\raw\real_patient_hpo_dataset.csv")
kbg_curr = df_curr[df_curr['Disease'].str.lower() == 'kbg syndrome']

df_cand = pd.read_csv(r"d:\finalresearchproject\data\raw\three_disease_patient_records.csv")
kbg_cand = df_cand[df_cand['disease_name'].str.lower() == 'kbg syndrome']

# Let's extract PMIDs from file_path of candidates
# Example file_path: notebooks\ANKRD11\phenopackets\PMID_36446582_Gnazzo_2020_P24.json
# Let's see what PMIDs are mentioned in the file names or if the filenames mention the paper authors
# Let's write a parser to extract paper author, year, and patient id
def parse_candidate(row):
    filename = row['file_path'].split('\\')[-1]
    # remove PMID_36446582_
    clean_name = filename.replace('PMID_36446582_', '').replace('.json', '')
    return clean_name

kbg_cand_papers = kbg_cand.apply(parse_candidate, axis=1)
print("First 20 clean candidate identifiers:")
print(kbg_cand_papers.head(20))

# Let's see if we can find any matching paper names for our current sources:
# PMC8948816 (Chinese cases 2022)
# PMC5435101 (Low et al 2016)
print("\nChecking overlap with Low (PMC5435101) or PMC8948816:")
# Let's search for "Low" and see how many candidates match
low_candidates = kbg_cand[kbg_cand['file_path'].str.contains("Low", case=False, na=False)]
print("Low candidates count:", len(low_candidates))

# PMC8948816 authors: Genetic and Phenotypic Spectrum of KBG Syndrome: A Report of 13 New Chinese Cases.
# Let's check if the author name of PMC8948816 (Wang or other) is in the candidates
# Let's list some unique clean names from candidates
clean_unique = sorted(kbg_cand_papers.unique())
print("\nUnique papers/cases in candidate dataset (first 50):")
print(clean_unique[:50])
