import os
import re
import pandas as pd
import json

DATA_DIR = r"d:\finalresearchproject\data"
REPORTS_DIR = r"d:\finalresearchproject\reports"

df_master = pd.read_csv(os.path.join(DATA_DIR, "expanded_real_patient_hpo_dataset.csv"))
df_excl = pd.read_csv(os.path.join(DATA_DIR, "excluded_duplicate_patients_log.csv"))

print(f"Master dataset: {len(df_master)} rows")
print(f"Exclusion dataset: {len(df_excl)} rows")

# Let's map every patient in df_master to their specific publication
patient_map = []
for idx, row in df_master.iterrows():
    pid = str(row['Patient_ID']).strip()
    disease = str(row['Disease']).strip()
    src = str(row['Source']).strip()
    prov = str(row['Provenance']).strip()
    
    # Determine First_Author, Year, Publication, PMID, PMCID, DOI, Type
    first_author = ""
    year = ""
    pub_title = ""
    pmid = ""
    pmcid = ""
    doi = ""
    pub_type = ""
    pub_id = ""
    
    if src == "PMC7713511":
        pub_id = "PUB_WS_01"
        first_author = "Assia Batzir"
        year = "2020"
        pub_title = "Am J Med Genet A"
        pmid = "31782611"
        pmcid = "PMC7713511"
        doi = "10.1002/ajmg.a.61380"
        pub_type = "primary cohort study"
    elif src == "PMC6231716":
        pub_id = "PUB_XG_01"
        first_author = "Jiang"
        year = "2018"
        pub_title = "Am J Med Genet A"
        pmid = "29696776"
        pmcid = "PMC6231716"
        doi = "10.1002/ajmg.a.38699"
        pub_type = "primary cohort study"
    elif src == "PMC8948816":
        pub_id = "PUB_KBG_02"
        first_author = "Gao"
        year = "2022"
        pub_title = "J Pers Med"
        pmid = "35330407"
        pmcid = "PMC8948816"
        doi = "10.3390/jpm12030407"
        pub_type = "primary cohort study"
    elif src == "PMC5435101":
        pub_id = "PUB_KBG_03"
        first_author = "Low"
        year = "2016"
        pub_title = "Am J Med Genet A"
        pmid = "27667800"
        pmcid = "PMC5435101"
        doi = "10.1002/ajmg.a.37842"
        pub_type = "multicenter cohort"
    elif src == "PMID:36446582":
        pub_id = "PUB_KBG_01"
        first_author = "Martinez-Cayuelas"
        year = "2023"
        pub_title = "J Med Genet"
        pmid = "36446582"
        pmcid = "PMC10155694"
        doi = "10.1136/jmg-2022-108865"
        pub_type = "multicenter cohort"
    elif "Nagy / Tan et al." in src or "Nagy2022" in pid:
        pub_id = "PUB_WS_02"
        first_author = "Nagy / Tan"
        year = "2022"
        pub_title = "Genes (Basel)"
        pmid = "35052493"
        pmcid = "PMC8775410"
        doi = "10.3390/genes13010154"
        pub_type = "primary cohort study"
    elif "White et al." in src or "White2016" in pid:
        pub_id = "PUB_WS_03"
        first_author = "White"
        year = "2016"
        pub_title = "Genome Med"
        pmid = "26739615"
        pmcid = "PMC4702300"
        doi = "10.1186/s13073-015-0253-0"
        pub_type = "primary cohort study"
    elif "Ye et al." in src or "Ye2015" in pid:
        pub_id = "PUB_WS_04"
        first_author = "Ye"
        year = "2015"
        pub_title = "Cold Spring Harb Mol Case Stud"
        pmid = "27148570"
        pmcid = "PMC4850885"
        doi = "10.1101/mcs.a000455"
        pub_type = "familial/small series"
    elif "Khayat et al." in src or "Khayat2021" in pid:
        pub_id = "PUB_XG_02"
        first_author = "Khayat"
        year = "2021"
        pub_title = "HGG Adv"
        pmid = "34950897"
        pmcid = "PMC8694554"
        doi = "10.1016/j.xhgg.2021.100049"
        pub_type = "primary cohort study"
    elif "Yang et al." in src or "Yang2015" in pid:
        pub_id = "PUB_XG_03"
        first_author = "Yang"
        year = "2015"
        pub_title = "Cold Spring Harb Mol Case Stud"
        pmid = "27148574"
        pmcid = "PMC4850891"
        doi = "10.1101/mcs.a000562"
        pub_type = "familial/small series"
    elif "Romano et al." in src or "Romano2022" in pid:
        pub_id = "PUB_XG_04"
        first_author = "Romano"
        year = "2022"
        pub_title = "Birth Defects Res"
        pmid = "35716097"
        pmcid = "PMC9545659"
        doi = "10.1002/bdr2.2058"
        pub_type = "familial/small series"
    elif "Cheng et al." in src or "Cheng2019" in pid:
        pub_id = "PUB_XG_05"
        first_author = "Cheng"
        year = "2019"
        pub_title = "Mol Genet Genomic Med"
        pmid = "30729726"
        pmcid = "PMC6465669"
        doi = "10.1002/mgg3.596"
        pub_type = "case report"
    elif "Literature cohort" in src:
        # Match author and year from src
        sub = src.replace("Literature cohort (", "").replace(")", "").replace("_", " ")
        m = re.search(r'([A-Za-z\-]+)\s*(\d{4})', sub)
        if m:
            first_author = m.group(1).capitalize()
            year = m.group(2)
        else:
            first_author = sub
            year = "Unknown"
            
        pub_id = f"PUB_KBG_LIT_{first_author.upper()}_{year}"
        pub_title = f"{first_author} et al. ({year})"
        doi = "Various"
        pmid = "Various"
        pmcid = "N/A"
        pub_type = "case report / cohort study"
    else:
        pub_id = f"PUB_UNKNOWN_{idx}"
        first_author = "Unknown"
        year = "Unknown"
        pub_title = src
        pub_type = "other"
        
    patient_map.append({
        "Patient_ID": pid,
        "Disease": disease,
        "Publication_ID": pub_id,
        "First_Author": first_author,
        "Year": year,
        "Publication": pub_title,
        "Source": src,
        "Provenance": prov,
        "Retained": "YES"
    })

df_pt_map = pd.DataFrame(patient_map)
print("\nUnique Publication_IDs in patient map:")
print(df_pt_map['Publication_ID'].value_counts())
print(f"Total distinct Publication_IDs: {df_pt_map['Publication_ID'].nunique()}")
print(f"Total mapped patients: {len(df_pt_map)}")
