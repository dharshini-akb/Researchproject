import pandas as pd
import glob
import os

df_rev = pd.read_csv("data/real_patient_hpo_dataset_provenance_review.csv")
print("=== KBG SYNDROME LITERATURE PAPERS IN REVIEW CSV ===")
print("Total rows:", len(df_rev))
papers = {}
for src in df_rev['Source']:
    # Clean paper name
    p = src.replace('PMID:36446582_Published_', '')
    base_p = p.split('_P')[0].split('_Patient')[0]
    papers[base_p] = papers.get(base_p, 0) + 1

for p, count in sorted(papers.items(), key=lambda x: x[1], reverse=True):
    print(f"  {p}: {count} patients")
