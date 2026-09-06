import os
import pandas as pd

REPORTS_DIR = r"d:\finalresearchproject\reports"

f1 = pd.read_csv(os.path.join(REPORTS_DIR, "final_publication_provenance_audit.csv"))
f2 = pd.read_csv(os.path.join(REPORTS_DIR, "final_patient_to_publication_map.csv"))
f3 = pd.read_csv(os.path.join(REPORTS_DIR, "final_excluded_publication_audit.csv"))
f4 = pd.read_csv(os.path.join(REPORTS_DIR, "publication_duplicate_resolution.csv"))
f5 = pd.read_csv(os.path.join(REPORTS_DIR, "publication_patient_overlap_matrix.csv"))

print(f"1. final_publication_provenance_audit.csv rows: {len(f1)}")
print(f"   Included publications: {len(f1[f1['Status'] == 'INCLUDED'])}")
print(f"   Excluded publications: {len(f1[f1['Status'] == 'EXCLUDED'])}")
print(f"   Sum of retained patients: {f1['Retained_Patients'].sum()}")
print(f"   Sum of excluded patients: {f1['Excluded_Patients'].sum()}")

print(f"\n2. final_patient_to_publication_map.csv rows: {len(f2)}")
print(f"   Unique Patient_IDs: {f2['Patient_ID'].nunique()}")
print(f"   Disease breakdown:\n{f2['Disease'].value_counts()}")

print(f"\n3. final_excluded_publication_audit.csv rows: {len(f3)}")
print(f"   Disease breakdown:\n{f3['Disease'].value_counts()}")

print(f"\n4. publication_duplicate_resolution.csv rows: {len(f4)}")
print(f"\n5. publication_patient_overlap_matrix.csv rows: {len(f5)}")
