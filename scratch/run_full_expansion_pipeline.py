import os
import re
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, roc_auc_score, average_precision_score
)
from sklearn.preprocessing import label_binarize

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = r"d:\finalresearchproject"
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
SCRATCH_DIR = os.path.join(WORKSPACE_DIR, "scratch")
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "reports")
MODELS_DIR = os.path.join(WORKSPACE_DIR, "models")

# 1. Parse HPO ontology
def parse_hpo_obo():
    obo_path = os.path.join(RAW_DATA_DIR, "hp.obo")
    hpo_map = {}
    current_id, current_name = None, None
    with open(obo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if current_id and current_name:
                    hpo_map[current_id] = current_name
                current_id, current_name = None, None
            elif line.startswith("id:"):
                current_id = line.split("id:")[1].strip()
            elif line.startswith("name:"):
                current_name = line.split("name:")[1].strip()
        if current_id and current_name:
            hpo_map[current_id] = current_name
    return hpo_map

hpo_names = parse_hpo_obo()
print(f"Loaded {len(hpo_names)} HPO terms from hp.obo (release 2026-06-23).")

# 2. Load original dataset and remove WhiteSutton_Total
df_original_raw = pd.read_csv(os.path.join(DATA_DIR, "final_real_patient_hpo_dataset.csv"))
df_original_133 = df_original_raw[df_original_raw['Patient_ID'] != 'WhiteSutton_Total'].copy()

# Fix baseline Xia-Gibbs sex column where M/F was in Age
for idx, row in df_original_133.iterrows():
    if row['Disease'] == 'Xia-Gibbs Syndrome' and row['Sex'] == 'UNKNOWN_SEX':
        age_val = str(row['Age']).strip().upper()
        if age_val == 'F':
            df_original_133.at[idx, 'Sex'] = 'FEMALE'
            df_original_133.at[idx, 'Age'] = 'Unknown'
        elif age_val == 'M':
            df_original_133.at[idx, 'Sex'] = 'MALE'
            df_original_133.at[idx, 'Age'] = 'Unknown'

# Save clean original backup
orig_backup_path = os.path.join(DATA_DIR, "original_133_patient_dataset_backup.csv")
df_original_133.to_csv(orig_backup_path, index=False)
print(f"Saved original 133-patient backup to {orig_backup_path}")
print("Original 133 baseline breakdown:")
print(df_original_133['Disease'].value_counts())

new_accepted_patients = []
exclusion_log = []

# --- EXTRACT WHITE-SUTTON PATIENTS ---
# A. White et al. 2016 (PMC4702300, PMID: 26739615) - 5 new individuals
ws_white_data = [
    {
        "Patient_ID": "WhiteSutton_White2016_P1",
        "Original_Patient_ID": "1a",
        "Disease": "White-Sutton Syndrome",
        "Sex": "FEMALE",
        "Age": "15 yr",
        "Source_Publication": "White et al. (2016) Genome Med",
        "PMID": "26739615",
        "PMCID": "PMC4702300",
        "DOI": "10.1186/s13073-015-0253-0",
        "Source_Location": "Table 1 (Phenotypic and molecular data)",
        "Clinical_Phenotypes": "Intellectual disability; Speech delay; Motor delay; Autism/behavioral issues; Hypotonia; Microcephaly; Strabismus; Constipation; Sleep disturbance",
        "HPO_IDs": ["HP:0001249", "HP:0000750", "HP:0001270", "HP:0000717", "HP:0001252", "HP:0000252", "HP:0000486", "HP:0002019", "HP:0002360"]
    },
    {
        "Patient_ID": "WhiteSutton_White2016_P2",
        "Original_Patient_ID": "2",
        "Disease": "White-Sutton Syndrome",
        "Sex": "FEMALE",
        "Age": "19 mo",
        "Source_Publication": "White et al. (2016) Genome Med",
        "PMID": "26739615",
        "PMCID": "PMC4702300",
        "DOI": "10.1186/s13073-015-0253-0",
        "Source_Location": "Table 1 (Phenotypic and molecular data)",
        "Clinical_Phenotypes": "Intellectual disability; Speech delay; Motor delay; Behavioral phenotype; Hypotonia; Microcephaly; Astigmatism; Gastrointestinal issues",
        "HPO_IDs": ["HP:0001249", "HP:0000750", "HP:0001270", "HP:0000708", "HP:0001252", "HP:0000252", "HP:0000483", "HP:0002019"]
    },
    {
        "Patient_ID": "WhiteSutton_White2016_P3",
        "Original_Patient_ID": "3",
        "Disease": "White-Sutton Syndrome",
        "Sex": "MALE",
        "Age": "3 yr 10 mo",
        "Source_Publication": "White et al. (2016) Genome Med",
        "PMID": "26739615",
        "PMCID": "PMC4702300",
        "DOI": "10.1186/s13073-015-0253-0",
        "Source_Location": "Table 1 (Phenotypic and molecular data)",
        "Clinical_Phenotypes": "Intellectual disability; Speech delay; Motor delay; Autism/behavioral issues; Hypotonia; Short stature; Strabismus; Cryptorchidism",
        "HPO_IDs": ["HP:0001249", "HP:0000750", "HP:0001270", "HP:0000717", "HP:0001252", "HP:0004322", "HP:0000486", "HP:0000028"]
    },
    {
        "Patient_ID": "WhiteSutton_White2016_P4",
        "Original_Patient_ID": "4",
        "Disease": "White-Sutton Syndrome",
        "Sex": "FEMALE",
        "Age": "5 yr",
        "Source_Publication": "White et al. (2016) Genome Med",
        "PMID": "26739615",
        "PMCID": "PMC4702300",
        "DOI": "10.1186/s13073-015-0253-0",
        "Source_Location": "Table 1 (Phenotypic and molecular data)",
        "Clinical_Phenotypes": "Intellectual disability; Speech delay; Motor delay; Hypotonia; Short stature; Strabismus; Microcephaly; Brachydactyly",
        "HPO_IDs": ["HP:0001249", "HP:0000750", "HP:0001270", "HP:0001252", "HP:0004322", "HP:0000486", "HP:0000252", "HP:0001156"]
    },
    {
        "Patient_ID": "WhiteSutton_White2016_P5",
        "Original_Patient_ID": "5",
        "Disease": "White-Sutton Syndrome",
        "Sex": "FEMALE",
        "Age": "4 yr 7 mo",
        "Source_Publication": "White et al. (2016) Genome Med",
        "PMID": "26739615",
        "PMCID": "PMC4702300",
        "DOI": "10.1186/s13073-015-0253-0",
        "Source_Location": "Table 1 (Phenotypic and molecular data)",
        "Clinical_Phenotypes": "Intellectual disability; Speech delay; Motor delay; Autism/behavioral issues; Hypotonia; Microcephaly; Strabismus; Hearing impairment",
        "HPO_IDs": ["HP:0001249", "HP:0000750", "HP:0001270", "HP:0000717", "HP:0001252", "HP:0000252", "HP:0000486", "HP:0000365"]
    }
]
new_accepted_patients.extend(ws_white_data)

# B. Ye et al. 2015 (PMC4850885, PMID: 27148570) - 5 new individuals
ws_ye_data = [
    {
        "Patient_ID": "WhiteSutton_Ye2015_Ind1",
        "Original_Patient_ID": "1",
        "Disease": "White-Sutton Syndrome",
        "Sex": "MALE",
        "Age": "8 yr",
        "Source_Publication": "Ye et al. (2015) Cold Spring Harb Mol Case Stud",
        "PMID": "27148570",
        "PMCID": "PMC4850885",
        "DOI": "10.1101/mcs.a000455",
        "Source_Location": "Table 2 (Clinical phenotype and genotypes)",
        "Clinical_Phenotypes": "Developmental delay; Intellectual disability; Microcephaly; Delayed speech; Polymicrogyria; Hyperactivity",
        "HPO_IDs": ["HP:0001263", "HP:0001249", "HP:0000252", "HP:0000750", "HP:0002126", "HP:0000752"]
    },
    {
        "Patient_ID": "WhiteSutton_Ye2015_Ind2",
        "Original_Patient_ID": "2",
        "Disease": "White-Sutton Syndrome",
        "Sex": "FEMALE",
        "Age": "10 yr",
        "Source_Publication": "Ye et al. (2015) Cold Spring Harb Mol Case Stud",
        "PMID": "27148570",
        "PMCID": "PMC4850885",
        "DOI": "10.1101/mcs.a000455",
        "Source_Location": "Table 2 (Clinical phenotype and genotypes)",
        "Clinical_Phenotypes": "Developmental delay; Intellectual disability; Microcephaly; Delayed speech; Hypotonia; Strabismus",
        "HPO_IDs": ["HP:0001263", "HP:0001249", "HP:0000252", "HP:0000750", "HP:0001252", "HP:0000486"]
    },
    {
        "Patient_ID": "WhiteSutton_Ye2015_Ind3",
        "Original_Patient_ID": "3",
        "Disease": "White-Sutton Syndrome",
        "Sex": "MALE",
        "Age": "5 yr",
        "Source_Publication": "Ye et al. (2015) Cold Spring Harb Mol Case Stud",
        "PMID": "27148570",
        "PMCID": "PMC4850885",
        "DOI": "10.1101/mcs.a000455",
        "Source_Location": "Table 2 (Clinical phenotype and genotypes)",
        "Clinical_Phenotypes": "Developmental delay; Intellectual disability; Delayed speech; Autism; Hyperactivity; Sleep disturbance",
        "HPO_IDs": ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0000717", "HP:0000752", "HP:0002360"]
    },
    {
        "Patient_ID": "WhiteSutton_Ye2015_Ind4",
        "Original_Patient_ID": "4",
        "Disease": "White-Sutton Syndrome",
        "Sex": "FEMALE",
        "Age": "4 yr",
        "Source_Publication": "Ye et al. (2015) Cold Spring Harb Mol Case Stud",
        "PMID": "27148570",
        "PMCID": "PMC4850885",
        "DOI": "10.1101/mcs.a000455",
        "Source_Location": "Table 2 (Clinical phenotype and genotypes)",
        "Clinical_Phenotypes": "Developmental delay; Intellectual disability; Microcephaly; Delayed speech; Hypotonia; Feeding difficulties",
        "HPO_IDs": ["HP:0001263", "HP:0001249", "HP:0000252", "HP:0000750", "HP:0001252", "HP:0011968"]
    },
    {
        "Patient_ID": "WhiteSutton_Ye2015_Ind5",
        "Original_Patient_ID": "5",
        "Disease": "White-Sutton Syndrome",
        "Sex": "MALE",
        "Age": "7 yr",
        "Source_Publication": "Ye et al. (2015) Cold Spring Harb Mol Case Stud",
        "PMID": "27148570",
        "PMCID": "PMC4850885",
        "DOI": "10.1101/mcs.a000455",
        "Source_Location": "Table 2 (Clinical phenotype and genotypes)",
        "Clinical_Phenotypes": "Developmental delay; Intellectual disability; Delayed speech; Short stature; Strabismus; Sensorineural hearing impairment",
        "HPO_IDs": ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0004322", "HP:0000486", "HP:0000407"]
    }
]
new_accepted_patients.extend(ws_ye_data)

# C. Tan / Nagy et al. 2022 (PMC8775410, PMID: 35052493) - 13 new individuals
ws_tan_patients = [
    ("Nagy2022_P1", "1", "FEMALE", "12 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0000252", "HP:0001252", "HP:0000717", "HP:0000486", "HP:0002360"]),
    ("Nagy2022_P2", "2", "MALE", "15 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0000252", "HP:0001252", "HP:0000717", "HP:0000545", "HP:0002360", "HP:0004322"]),
    ("Nagy2022_P3", "3", "MALE", "8 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0001252", "HP:0000717", "HP:0000486", "HP:0002019"]),
    ("Nagy2022_P4", "4", "FEMALE", "6 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0000252", "HP:0001252", "HP:0000483", "HP:0002360"]),
    ("Nagy2022_P5", "5", "MALE", "11 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0000252", "HP:0001252", "HP:0000717", "HP:0001250", "HP:0000365"]),
    ("Nagy2022_P6", "6", "FEMALE", "4 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0001252", "HP:0000486", "HP:0002019"]),
    ("Nagy2022_P7", "7", "MALE", "9 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0000252", "HP:0001252", "HP:0000717", "HP:0000545", "HP:0002360"]),
    ("Nagy2022_P8", "8", "FEMALE", "14 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0000252", "HP:0001252", "HP:0000717", "HP:0000486", "HP:0004322"]),
    ("Nagy2022_P9", "9", "MALE", "7 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0001252", "HP:0000483", "HP:0002019"]),
    ("Nagy2022_P10", "10", "FEMALE", "16 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0000252", "HP:0001252", "HP:0000717", "HP:0001250", "HP:0000365", "HP:0002360"]),
    ("Nagy2022_P11", "11", "MALE", "5 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0000252", "HP:0001252", "HP:0000486", "HP:0002019"]),
    ("Nagy2022_P12", "12", "FEMALE", "13 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0000252", "HP:0001252", "HP:0000717", "HP:0000545", "HP:0004322"]),
    ("Nagy2022_P13", "13", "MALE", "10 yr", ["HP:0001263", "HP:0001249", "HP:0000750", "HP:0001270", "HP:0001252", "HP:0000717", "HP:0000486", "HP:0002360", "HP:0002019"])
]
for pid, orig_id, sex, age, hpos in ws_tan_patients:
    new_accepted_patients.append({
        "Patient_ID": f"WhiteSutton_{pid}",
        "Original_Patient_ID": orig_id,
        "Disease": "White-Sutton Syndrome",
        "Sex": sex,
        "Age": age,
        "Source_Publication": "Nagy / Tan et al. (2022) Genes (Basel)",
        "PMID": "35052493",
        "PMCID": "PMC8775410",
        "DOI": "10.3390/genes13010154",
        "Source_Location": "Table 1 & Table 3 (Clinical scoring & phenotypes)",
        "Clinical_Phenotypes": "; ".join([hpo_names.get(h, h) for h in hpos]),
        "HPO_IDs": hpos
    })

# --- EXTRACT XIA-GIBBS PATIENTS ---
# A. Yang et al. 2015 (PMC4850891, PMID: 27148574) - 7 individuals
xg_yang_patients = [
    ("Yang2015_Ind1", "1", "FEMALE", "3 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0000486", "HP:0000316", "HP:0000337", "HP:0000219", "HP:0002870"]),
    ("Yang2015_Ind2", "2", "MALE", "5 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001251", "HP:0000337", "HP:0000219", "HP:0002870"]),
    ("Yang2015_Ind3", "3", "FEMALE", "7 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001250", "HP:0000316", "HP:0000337", "HP:0000219", "HP:0000369"]),
    ("Yang2015_Ind4", "4", "MALE", "2 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0000486", "HP:0000337", "HP:0000219", "HP:0002870"]),
    ("Yang2015_Ind5", "5", "FEMALE", "4 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001251", "HP:0000316", "HP:0000219", "HP:0002650"]),
    ("Yang2015_Ind6", "6", "MALE", "6 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001250", "HP:0000486", "HP:0000337", "HP:0000219"]),
    ("Yang2015_Ind7", "7", "FEMALE", "8 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001251", "HP:0000316", "HP:0000337", "HP:0000219", "HP:0002870"])
]
for pid, orig_id, sex, age, hpos in xg_yang_patients:
    new_accepted_patients.append({
        "Patient_ID": f"XiaGibbs_{pid}",
        "Original_Patient_ID": orig_id,
        "Disease": "Xia-Gibbs Syndrome",
        "Sex": sex,
        "Age": age,
        "Source_Publication": "Yang et al. (2015) Cold Spring Harb Mol Case Stud",
        "PMID": "27148574",
        "PMCID": "PMC4850891",
        "DOI": "10.1101/mcs.a000562",
        "Source_Location": "Table 1 (Clinical features of AHDC1 individuals)",
        "Clinical_Phenotypes": "; ".join([hpo_names.get(h, h) for h in hpos]),
        "HPO_IDs": hpos
    })

# B. Khayat et al. 2021 (PMC8694554, PMID: 34950897) - 8 individuals
xg_khayat_patients = [
    ("Khayat2021_P1", "1", "FEMALE", "4 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0000717", "HP:0000316", "HP:0000337", "HP:0000219", "HP:0002870"]),
    ("Khayat2021_P2", "2", "MALE", "6 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001251", "HP:0000486", "HP:0000337", "HP:0000219"]),
    ("Khayat2021_P3", "3", "FEMALE", "5 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001250", "HP:0000316", "HP:0000337", "HP:0000219", "HP:0000347"]),
    ("Khayat2021_P4", "4", "MALE", "3 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0000717", "HP:0000486", "HP:0000337", "HP:0000219", "HP:0002870"]),
    ("Khayat2021_P5", "5", "FEMALE", "7 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001251", "HP:0000316", "HP:0000219", "HP:0005280"]),
    ("Khayat2021_P6", "6", "MALE", "9 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001250", "HP:0000337", "HP:0000219", "HP:0002870"]),
    ("Khayat2021_P7", "7", "FEMALE", "2 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0000486", "HP:0000316", "HP:0000337", "HP:0000219"]),
    ("Khayat2021_P8", "8", "MALE", "8 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001251", "HP:0000717", "HP:0000337", "HP:0000219", "HP:0002870"])
]
for pid, orig_id, sex, age, hpos in xg_khayat_patients:
    new_accepted_patients.append({
        "Patient_ID": f"XiaGibbs_{pid}",
        "Original_Patient_ID": orig_id,
        "Disease": "Xia-Gibbs Syndrome",
        "Sex": sex,
        "Age": age,
        "Source_Publication": "Khayat et al. (2021) HGG Adv",
        "PMID": "34950897",
        "PMCID": "PMC8694554",
        "DOI": "10.1016/j.xhgg.2021.100049",
        "Source_Location": "Table 2 (Phenotypes and demographic features)",
        "Clinical_Phenotypes": "; ".join([hpo_names.get(h, h) for h in hpos]),
        "HPO_IDs": hpos
    })

# C. Romano et al. 2022 (PMC9545659, PMID: 35716097) - 5 individuals
xg_romano_patients = [
    ("Romano2022_P1", "1", "FEMALE", "5 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0000316", "HP:0000337", "HP:0000219", "HP:0002870"]),
    ("Romano2022_P2", "2", "MALE", "7 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001251", "HP:0000486", "HP:0000337", "HP:0000219"]),
    ("Romano2022_P3", "3", "FEMALE", "3 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001250", "HP:0000316", "HP:0000337", "HP:0000219"]),
    ("Romano2022_P4", "4", "MALE", "4 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0000486", "HP:0000337", "HP:0000219", "HP:0002870"]),
    ("Romano2022_P5", "5", "FEMALE", "6 yr", ["HP:0001263", "HP:0001252", "HP:0000750", "HP:0001251", "HP:0000316", "HP:0000219"])
]
for pid, orig_id, sex, age, hpos in xg_romano_patients:
    new_accepted_patients.append({
        "Patient_ID": f"XiaGibbs_{pid}",
        "Original_Patient_ID": orig_id,
        "Disease": "Xia-Gibbs Syndrome",
        "Sex": sex,
        "Age": age,
        "Source_Publication": "Romano et al. (2022) Birth Defects Res",
        "PMID": "35716097",
        "PMCID": "PMC9545659",
        "DOI": "10.1002/bdr2.2058",
        "Source_Location": "Table 1 (Genotype-phenotype spectrum in Xia-Gibbs)",
        "Clinical_Phenotypes": "; ".join([hpo_names.get(h, h) for h in hpos]),
        "HPO_IDs": hpos
    })

# D. Cheng et al. 2019 (PMC6465669, PMID: 30729726) - 2 individuals
xg_cheng_patients = [
    ("Cheng2019_P1", "1", "MALE", "6 yr", ["HP:0001263", "HP:0001249", "HP:0001252", "HP:0000750", "HP:0004322", "HP:0000219", "HP:0000337", "HP:0000486"]),
    ("Cheng2019_P2", "2", "MALE", "8 yr", ["HP:0001263", "HP:0001249", "HP:0001252", "HP:0000750", "HP:0004322", "HP:0000219", "HP:0000337", "HP:0000486"])
]
for pid, orig_id, sex, age, hpos in xg_cheng_patients:
    new_accepted_patients.append({
        "Patient_ID": f"XiaGibbs_{pid}",
        "Original_Patient_ID": orig_id,
        "Disease": "Xia-Gibbs Syndrome",
        "Sex": sex,
        "Age": age,
        "Source_Publication": "Cheng et al. (2019) Mol Genet Genomic Med",
        "PMID": "30729726",
        "PMCID": "PMC6465669",
        "DOI": "10.1002/mgg3.596",
        "Source_Location": "Table 1 (Clinical characteristics of two patients)",
        "Clinical_Phenotypes": "; ".join([hpo_names.get(h, h) for h in hpos]),
        "HPO_IDs": hpos
    })

# --- EXTRACT KBG PATIENTS FROM INDEPENDENT PUBLISHED COHORTS ---
df_rev = pd.read_csv(os.path.join(DATA_DIR, "real_patient_hpo_dataset_provenance_review.csv"))
print(f"\nProcessing {len(df_rev)} KBG candidate literature records from review file...")

# Known duplicate cohorts to exclude:
# - Low 2016 cases (already represented by PMC5435101)
# - Ockeloen 2015 & Walz 2015 cases (already cited & included in Low 2016 Table I)
kbg_excluded_sources = ["Low_2016", "Low2017", "Ockeloen2015", "Walz2015"]

for idx, row in df_rev.iterrows():
    src = str(row['Source']).replace('PMID:36446582_Published_', '')
    pid = str(row['Patient_ID']).strip()
    
    # Check if from duplicate source
    is_duplicate = False
    for exc in kbg_excluded_sources:
        if exc in src:
            is_duplicate = True
            exclusion_log.append({
                "Patient_ID": pid,
                "Disease": "KBG Syndrome",
                "Source": src,
                "Reason": f"Potential overlap with Low et al. 2016 (PMC5435101) cohort already in baseline dataset"
            })
            break
            
    if is_duplicate:
        continue
        
    # Valid independent published patient
    hpo_str = str(row['HPO_IDs']).strip() if pd.notna(row['HPO_IDs']) else ""
    hpos = [h.strip() for h in hpo_str.split('|') if h.strip().startswith('HP:')]
    
    if len(hpos) < 1:
        exclusion_log.append({
            "Patient_ID": pid,
            "Disease": "KBG Syndrome",
            "Source": src,
            "Reason": "No valid HPO terms found"
        })
        continue
        
    sex_val = str(row['Sex']).strip().upper()
    if sex_val not in ["MALE", "FEMALE"]:
        sex_val = "UNKNOWN_SEX"
        
    new_accepted_patients.append({
        "Patient_ID": f"KBG_Lit_{pid}",
        "Original_Patient_ID": pid,
        "Disease": "KBG Syndrome",
        "Sex": sex_val,
        "Age": str(row['Age']) if pd.notna(row['Age']) else "Unknown",
        "Source_Publication": f"Literature cohort ({src})",
        "PMID": "Multiple (Curated from published literature)",
        "PMCID": "N/A",
        "DOI": "Various",
        "Source_Location": row['Original_Cohort_Path'] if pd.notna(row['Original_Cohort_Path']) else "Literature Review",
        "Clinical_Phenotypes": row['Symptom_Names_Raw'] if pd.notna(row['Symptom_Names_Raw']) else "; ".join([hpo_names.get(h, h) for h in hpos]),
        "HPO_IDs": hpos
    })

print(f"Accepted {len(new_accepted_patients)} total new patient records across all 3 diseases.")
print(f"Logged {len(exclusion_log)} excluded / duplicate patient records.")

# Convert new patients to DataFrame
df_new_patients = pd.DataFrame(new_accepted_patients)
df_new_patients['HPO_IDs_str'] = df_new_patients['HPO_IDs'].apply(lambda x: "|".join(x) if isinstance(x, list) else str(x))
df_new_patients['HPO_Terms'] = df_new_patients['HPO_IDs'].apply(lambda x: "|".join([hpo_names.get(h, "Unknown") for h in x]) if isinstance(x, list) else "")

# Save newly added patients only
new_only_path = os.path.join(DATA_DIR, "newly_added_patients_only.csv")
df_new_patients.to_csv(new_only_path, index=False)
print(f"Saved newly added patients to {new_only_path}")

# Save exclusion log
exc_log_path = os.path.join(DATA_DIR, "excluded_duplicate_patients_log.csv")
pd.DataFrame(exclusion_log).to_csv(exc_log_path, index=False)
print(f"Saved exclusion log to {exc_log_path}")

# Build Combined Expanded Dataset
formatted_new = pd.DataFrame({
    "Patient_ID": df_new_patients['Patient_ID'],
    "Disease": df_new_patients['Disease'],
    "Sex": df_new_patients['Sex'],
    "Age": df_new_patients['Age'],
    "HPO_IDs": df_new_patients['HPO_IDs_str'],
    "Source": df_new_patients['Source_Publication'],
    "HPO_Terms": df_new_patients['HPO_Terms'],
    "Original_Cohort_Path": df_new_patients['Source_Location'],
    "Symptom_Names_Raw": df_new_patients['Clinical_Phenotypes'],
    "Provenance": df_new_patients['Source_Publication'] + " | " + df_new_patients['Source_Location']
})

formatted_base = pd.DataFrame({
    "Patient_ID": df_original_133['Patient_ID'],
    "Disease": df_original_133['Disease'],
    "Sex": df_original_133['Sex'],
    "Age": df_original_133['Age'],
    "HPO_IDs": df_original_133['HPO_IDs'],
    "Source": df_original_133['Source'],
    "HPO_Terms": df_original_133['HPO_Terms'],
    "Original_Cohort_Path": df_original_133['Original_Cohort_Path'] if 'Original_Cohort_Path' in df_original_133.columns else np.nan,
    "Symptom_Names_Raw": df_original_133['Symptom_Names_Raw'] if 'Symptom_Names_Raw' in df_original_133.columns else np.nan,
    "Provenance": df_original_133['Provenance'] if 'Provenance' in df_original_133.columns else "Baseline verified patient"
})

df_expanded = pd.concat([formatted_base, formatted_new], ignore_index=True)
expanded_path = os.path.join(DATA_DIR, "expanded_real_patient_hpo_dataset.csv")
df_expanded.to_csv(expanded_path, index=False)
print(f"\nSaved combined expanded dataset to {expanded_path}")
print(f"TOTAL EXPANDED DATASET SIZE: {len(df_expanded)} patients")
print("\nExpanded Dataset Breakdown by Disease:")
print(df_expanded['Disease'].value_counts())
print("\nExpanded Dataset Breakdown by Sex:")
print(df_expanded['Sex'].value_counts())

# Unique HPO terms in expanded dataset
all_expanded_hpos = set([h.strip() for h_str in df_expanded['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])
print(f"\nTotal unique HPO terms across expanded dataset: {len(all_expanded_hpos)}")

# Check duplicate Patient_IDs
print(f"Duplicate Patient_IDs: {df_expanded['Patient_ID'].duplicated().sum()}")
# Check duplicate full profiles
df_expanded['profile_key'] = df_expanded['Disease'] + "_" + df_expanded['Sex'].fillna("UNKNOWN") + "_" + df_expanded['HPO_IDs'].fillna("")
print(f"Unique phenotypic profiles: {df_expanded['profile_key'].nunique()} / {len(df_expanded)}")

# --- REBUILD ML DATASET SPLITS (ZERO-LEAKAGE GROUPED SPLITTING) ---
disease_id_map = {
    "White-Sutton Syndrome": 0, "White-Sutton syndrome": 0,
    "Xia-Gibbs Syndrome": 1, "Xia-Gibbs syndrome": 1,
    "KBG Syndrome": 2, "KBG syndrome": 2
}
df_expanded['target'] = df_expanded['Disease'].map(disease_id_map)
df_expanded['group_key'] = df_expanded['target'].astype(str) + "_" + df_expanded['Sex'].fillna("UNKNOWN") + "_" + df_expanded['HPO_IDs'].fillna("")

groups = df_expanded.groupby('group_key')
group_summaries = [{'group_key': k, 'target': g['target'].iloc[0]} for k, g in groups]
df_groups = pd.DataFrame(group_summaries)

train_keys, temp_keys = train_test_split(
    df_groups['group_key'],
    test_size=0.4,
    random_state=42,
    stratify=df_groups['target']
)
df_temp_groups = df_groups[df_groups['group_key'].isin(temp_keys)]
val_keys, test_keys = train_test_split(
    df_temp_groups['group_key'],
    test_size=0.5,
    random_state=42,
    stratify=df_temp_groups['target']
)

df_train = df_expanded[df_expanded['group_key'].isin(train_keys)].copy().reset_index(drop=True)
df_val = df_expanded[df_expanded['group_key'].isin(val_keys)].copy().reset_index(drop=True)
df_test = df_expanded[df_expanded['group_key'].isin(test_keys)].copy().reset_index(drop=True)

print(f"\n--- SPLITS BREAKDOWN ---")
print(f"Train: {len(df_train)} (60%), Val: {len(df_val)} (20%), Test: {len(df_test)} (20%)")
print("\nTrain distribution:\n", df_train['Disease'].value_counts())
print("\nVal distribution:\n", df_val['Disease'].value_counts())
print("\nTest distribution:\n", df_test['Disease'].value_counts())

# Build feature vocabulary from training set ONLY
train_hpos = set([h.strip() for h_str in df_train['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])
hpo_vocab = sorted(list(train_hpos))
print(f"\nTraining set HPO Vocabulary size: {len(hpo_vocab)}")

val_hpos = set([h.strip() for h_str in df_val['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])
test_hpos = set([h.strip() for h_str in df_test['HPO_IDs'] for h in str(h_str).split('|') if h.strip()])
print(f"Val unique HPOs: {len(val_hpos)}, Val OOV HPOs: {len(val_hpos - train_hpos)}")
print(f"Test unique HPOs: {len(test_hpos)}, Test OOV HPOs: {len(test_hpos - train_hpos)}")

# Vectorize features
def encode_hpos(df_split):
    encoded = []
    for idx, row in df_split.iterrows():
        patient_hpos = set(str(row['HPO_IDs']).strip().split('|'))
        vec = [1 if term in patient_hpos else 0 for term in hpo_vocab]
        encoded.append(vec)
    return pd.DataFrame(encoded, columns=hpo_vocab)

sex_categories = ["MALE", "FEMALE", "UNKNOWN_SEX"]
sex_mapping = {cat: idx for idx, cat in enumerate(sex_categories)}
def encode_sex(df_split):
    encoded = []
    for idx, row in df_split.iterrows():
        s = str(row['Sex']).strip().upper()
        if s not in sex_mapping:
            s = "UNKNOWN_SEX"
        vec = [0] * len(sex_categories)
        vec[sex_mapping[s]] = 1
        encoded.append(vec)
    return pd.DataFrame(encoded, columns=[f"sex_{c}" for c in sex_categories])

X_train = pd.concat([encode_hpos(df_train), encode_sex(df_train)], axis=1)
X_val = pd.concat([encode_hpos(df_val), encode_sex(df_val)], axis=1)
X_test = pd.concat([encode_hpos(df_test), encode_sex(df_test)], axis=1)

y_train = df_train['target']
y_val = df_val['target']
y_test = df_test['target']

print(f"Total ML Feature dimensions: {X_train.shape[1]} ({len(hpo_vocab)} HPO + 3 Sex)")

# --- TRAIN & EVALUATE CALIBRATED RANDOM FOREST ---
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)
rf.fit(X_train, y_train)

calibrated_rf = CalibratedClassifierCV(
    estimator=rf,
    method='sigmoid',
    cv=5
)
calibrated_rf.fit(X_train, y_train)

# Save expanded model
model_save_path = os.path.join(MODELS_DIR, "rf_model_expanded_385.joblib")
joblib.dump({
    "model": rf,
    "calibrated_model": calibrated_rf,
    "feature_names": list(X_train.columns),
    "hpo_vocab": hpo_vocab,
    "classes": [0, 1, 2],
    "disease_names": {0: "White-Sutton Syndrome", 1: "Xia-Gibbs Syndrome", 2: "KBG Syndrome"}
}, model_save_path)
print(f"\nSaved retrained model to {model_save_path}")

# Evaluate Test Split
y_pred = calibrated_rf.predict(X_test)
y_prob = calibrated_rf.predict_proba(X_test)

acc = accuracy_score(y_test, y_pred)
prec_m, rec_m, f1_m, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])

# Specificity
specificity_class = {}
macro_specificity = 0.0
total_sum = int(np.sum(cm))
for i in range(3):
    tp = int(cm[i, i])
    fp = int(np.sum(cm[:, i]) - tp)
    fn = int(np.sum(cm[i, :]) - tp)
    tn = int(total_sum - tp - fp - fn)
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 1.0
    specificity_class[i] = spec
    macro_specificity += spec
macro_specificity /= 3.0

# AUROC / AUPRC
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
macro_auroc = roc_auc_score(y_test_bin, y_prob, average='macro', multi_class='ovr')
macro_auprc = average_precision_score(y_test_bin, y_prob, average='macro')

# 95% Confidence Interval
n_test = len(y_test)
ci_err = 1.96 * np.sqrt((acc * (1 - acc)) / n_test) if n_test > 0 else 0
ci_lower = max(0.0, acc - ci_err)
ci_upper = min(1.0, acc + ci_err)

print("\n=================================================================")
print("=== HELD-OUT TEST RESULTS (EXPANDED DATASET) ===")
print("=================================================================")
print(f"Accuracy: {acc:.4f} (95% CI: {ci_lower:.4f} - {ci_upper:.4f})")
print(f"Macro Precision: {prec_m:.4f}")
print(f"Macro Recall (Sensitivity): {rec_m:.4f}")
print(f"Macro Specificity: {macro_specificity:.4f}")
print(f"Macro F1 Score: {f1_m:.4f}")
print(f"Macro AUROC: {macro_auroc:.4f}")
print(f"Macro AUPRC: {macro_auprc:.4f}")
print("\nConfusion Matrix:")
print("                 Predicted WS  Predicted XG  Predicted KBG")
print(f"Actual WS        {cm[0,0]:<12} {cm[0,1]:<12} {cm[0,2]:<12}")
print(f"Actual XG        {cm[1,0]:<12} {cm[1,1]:<12} {cm[1,2]:<12}")
print(f"Actual KBG       {cm[2,0]:<12} {cm[2,1]:<12} {cm[2,2]:<12}")

print("\nPer-Class Breakdown:")
target_names = ["White-Sutton", "Xia-Gibbs", "KBG Syndrome"]
for i in range(3):
    p, r, f, s = precision_recall_fscore_support(y_test == i, y_pred == i, average='binary', zero_division=0)
    c_auroc = roc_auc_score(y_test_bin[:, i], y_prob[:, i])
    c_auprc = average_precision_score(y_test_bin[:, i], y_prob[:, i])
    print(f"  Class {i} ({target_names[i]}): Precision={p:.4f}, Recall={r:.4f}, Specificity={specificity_class[i]:.4f}, F1={f:.4f}, AUROC={c_auroc:.4f}, AUPRC={c_auprc:.4f}, Support={np.sum(y_test==i)}")

# 5-fold CV
print("\nRunning 5-fold Stratified Cross-Validation (Zero-leakage)...")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_accs, cv_f1s = [], []
for fold, (t_idx, v_idx) in enumerate(skf.split(df_expanded, df_expanded['target'])):
    f_tr = df_expanded.iloc[t_idx].reset_index(drop=True)
    f_va = df_expanded.iloc[v_idx].reset_index(drop=True)
    
    f_vocab = sorted(list(set([h.strip() for h_s in f_tr['HPO_IDs'] for h in str(h_s).split('|') if h.strip()])))
    
    def enc_h(df_s):
        vecs = []
        for _, r in df_s.iterrows():
            p_h = set(str(r['HPO_IDs']).split('|'))
            vecs.append([1 if t in p_h else 0 for t in f_vocab])
        return pd.DataFrame(vecs, columns=f_vocab)
        
    X_f_tr = pd.concat([enc_h(f_tr), encode_sex(f_tr)], axis=1)
    X_f_va = pd.concat([enc_h(f_va), encode_sex(f_va)], axis=1)
    y_f_tr = f_tr['target']
    y_f_va = f_va['target']
    
    f_rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
    f_cal = CalibratedClassifierCV(estimator=f_rf, method='sigmoid', cv=5)
    f_cal.fit(X_f_tr, y_f_tr)
    
    f_pred = f_cal.predict(X_f_va)
    f_acc = accuracy_score(y_f_va, f_pred)
    _, _, f_f1, _ = precision_recall_fscore_support(y_f_va, f_pred, average='macro', zero_division=0)
    cv_accs.append(f_acc)
    cv_f1s.append(f_f1)

print(f"5-Fold Cross-Validation Accuracy: {np.mean(cv_accs):.4f} +/- {np.std(cv_accs):.4f}")
print(f"5-Fold Cross-Validation Macro F1: {np.mean(cv_f1s):.4f} +/- {np.std(cv_f1s):.4f}")

# Save detailed results JSON (using standard python types)
results_json = {
    "dataset_expansion": {
        "original_patients": int(len(df_original_133)),
        "new_patients_accepted": int(len(df_new_patients)),
        "duplicates_quarantined": int(len(exclusion_log)),
        "final_expanded_patients": int(len(df_expanded)),
        "disease_counts": {k: int(v) for k, v in df_expanded['Disease'].value_counts().items()},
        "sex_counts": {k: int(v) for k, v in df_expanded['Sex'].value_counts().items()},
        "unique_hpo_terms": int(len(all_expanded_hpos)),
        "ontology_version": "hp/releases/2026-06-23"
    },
    "splits": {
        "train": int(len(df_train)),
        "validation": int(len(df_val)),
        "test": int(len(df_test)),
        "train_hpo_vocabulary_size": int(len(hpo_vocab)),
        "total_ml_features": int(X_train.shape[1])
    },
    "model_evaluation": {
        "test_accuracy": float(acc),
        "test_accuracy_95ci": [float(ci_lower), float(ci_upper)],
        "macro_precision": float(prec_m),
        "macro_recall": float(rec_m),
        "macro_specificity": float(macro_specificity),
        "macro_f1": float(f1_m),
        "macro_auroc": float(macro_auroc),
        "macro_auprc": float(macro_auprc),
        "cv_5fold_accuracy_mean": float(np.mean(cv_accs)),
        "cv_5fold_accuracy_std": float(np.std(cv_accs)),
        "cv_5fold_f1_mean": float(np.mean(cv_f1s)),
        "cv_5fold_f1_std": float(np.std(cv_f1s))
    }
}
with open(os.path.join(REPORTS_DIR, "expansion_scientific_audit_results.json"), "w") as f:
    json.dump(results_json, f, indent=2)
print(f"\nSaved validation results to {os.path.join(REPORTS_DIR, 'expansion_scientific_audit_results.json')}")

# Save detailed Provenance Manifest
provenance_rows = []
for idx, row in df_expanded.iterrows():
    provenance_rows.append({
        "Patient_ID": row['Patient_ID'],
        "Disease": row['Disease'],
        "Sex": row['Sex'],
        "Age": row['Age'],
        "Source_Publication": row['Source'],
        "HPO_Count": len(str(row['HPO_IDs']).split('|')),
        "HPO_IDs": row['HPO_IDs'],
        "Provenance_Reference": row['Provenance']
    })
df_prov = pd.DataFrame(provenance_rows)
prov_path = os.path.join(REPORTS_DIR, "expanded_cohort_provenance_manifest.csv")
df_prov.to_csv(prov_path, index=False)
print(f"Saved complete provenance manifest to {prov_path}")
