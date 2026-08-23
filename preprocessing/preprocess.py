import os
import json
import hashlib
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from config import system_config
from utils import logger
from preprocessing import data_loader

log = logger.get_logger("preprocess")

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw patient records: standardizes sex, deduplicates HPOs.
    """
    log.info("Cleaning patient records...")
    df = df.copy()
    
    # Map capitalized real dataset columns if they exist
    if 'Patient_ID' in df.columns:
        df['case_id'] = df['Patient_ID']
    if 'Sex' in df.columns:
        df['sex'] = df['Sex']
    if 'HPO_IDs' in df.columns:
        df['hpo_ids'] = df['HPO_IDs']
    if 'HPO_Terms' in df.columns:
        df['symptom_names'] = df['HPO_Terms']
    if 'Disease' in df.columns:
        disease_omim_map = {
            "White-Sutton Syndrome": "OMIM:616364",
            "Xia-Gibbs Syndrome": "OMIM:615829",
            "KBG Syndrome": "OMIM:148050"
        }
        df['disease_id'] = df['Disease'].map(disease_omim_map)
    
    # Standardize sex
    df['sex'] = df['sex'].astype(str).str.upper().str.strip()
    df['sex'] = df['sex'].replace({
        'NAN': 'UNKNOWN_SEX',
        'NONE': 'UNKNOWN_SEX',
        '': 'UNKNOWN_SEX',
        'UNKNOWN': 'UNKNOWN_SEX'
    })
    df['sex'] = df['sex'].fillna('UNKNOWN_SEX')
    
    # Deduplicate and sort HPO symptom list for each patient to prevent leakage and guarantee clean vectors
    cleaned_hpo_ids = []
    cleaned_symptom_names = []
    
    for idx, row in df.iterrows():
        hpo_str = str(row['hpo_ids']).strip()
        sym_str = str(row['symptom_names']).strip()
        
        if hpo_str == "" or hpo_str == "nan" or pd.isna(row['hpo_ids']):
            cleaned_hpo_ids.append("")
            cleaned_symptom_names.append("")
            continue
            
        hpos = [h.strip() for h in hpo_str.split('|')]
        symptoms = [s.strip() for s in sym_str.split('|')]
        
        seen = set()
        aligned = []
        for h, s in zip(hpos, symptoms):
            if h not in seen:
                seen.add(h)
                aligned.append((h, s))
                
        aligned.sort(key=lambda x: x[0])
        cleaned_hpo_ids.append("|".join([x[0] for x in aligned]))
        cleaned_symptom_names.append("|".join([x[1] for x in aligned]))
        
    df['hpo_ids'] = cleaned_hpo_ids
    df['symptom_names'] = cleaned_symptom_names
    
    return df

def generate_vocabulary(df_train: pd.DataFrame) -> List[str]:
    """
    Fits the HPO feature vocabulary using the training set ONLY to avoid data leakage.
    """
    log.info("Fitting HPO feature vocabulary on train split...")
    train_hpo_terms = set()
    for idx, row in df_train.iterrows():
        h_ids = str(row['hpo_ids']).strip().split('|')
        for h in h_ids:
            if h.strip() and h.strip() != "nan":
                train_hpo_terms.add(h.strip())
                
    hpo_vocab = sorted(list(train_hpo_terms))
    log.info(f"Generated HPO vocabulary of size {len(hpo_vocab)}")
    return hpo_vocab

def get_sha256_checksum(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def execute_pipeline():
    """
    Executes the data cleaning, vocabulary generation, split partition, and vectorization.
    """
    # 1. Load data
    df_raw = data_loader.load_patient_records()
    df_train_manifest, df_val_manifest, df_test_manifest = data_loader.load_splits_manifests()
    
    # 2. Clean data
    df_cleaned = clean_data(df_raw)
    
    # 3. Partition data based on manifests
    df_train = df_cleaned[df_cleaned['case_id'].isin(df_train_manifest['case_id'])].reset_index(drop=True)
    df_val = df_cleaned[df_cleaned['case_id'].isin(df_val_manifest['case_id'])].reset_index(drop=True)
    df_test = df_cleaned[df_cleaned['case_id'].isin(df_test_manifest['case_id'])].reset_index(drop=True)
    
    log.info(f"Cleaned split sizes - Train: {len(df_train)}, Val: {len(df_val)}, Test: {len(df_test)}")
    
    # Save cleaned cohort
    cleaned_cohort_path = os.path.join(system_config.PROCESSED_DATA_DIR, "cleaned_patient_records.csv")
    df_cleaned.to_csv(cleaned_cohort_path, index=False)
    log.info(f"Saved cleaned cohort patient records to {cleaned_cohort_path}")
    
    # 4. Fit vocabulary on training data only
    hpo_vocab = generate_vocabulary(df_train)
    
    # Create preprocess metadata directories
    os.makedirs(system_config.PREPROC_ARTIFACTS_DIR, exist_ok=True)
    vocab_path = os.path.join(system_config.PREPROC_ARTIFACTS_DIR, "hpo_feature_vocabulary.json")
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump(hpo_vocab, f, indent=4)
        
    vocab_json_str = json.dumps(hpo_vocab)
    vocab_checksum = get_sha256_checksum(vocab_json_str)
    log.info(f"Saved vocabulary dictionary to {vocab_path} (Checksum: {vocab_checksum})")
    
    # Map target variables
    # Filter only target diseases
    y_train = df_train['disease_id'].map(system_config.DISEASE_MAP)
    y_val = df_val['disease_id'].map(system_config.DISEASE_MAP)
    y_test = df_test['disease_id'].map(system_config.DISEASE_MAP)
    
    # Check for NaN in targets
    if y_train.isna().any() or y_val.isna().any() or y_test.isna().any():
        log.warning("Detected out-of-scope/unmapped disease targets in splits! Removing them.")
        df_train = df_train[~y_train.isna()].reset_index(drop=True)
        df_val = df_val[~y_val.isna()].reset_index(drop=True)
        df_test = df_test[~y_test.isna()].reset_index(drop=True)
        
        y_train = df_train['disease_id'].map(system_config.DISEASE_MAP)
        y_val = df_val['disease_id'].map(system_config.DISEASE_MAP)
        y_test = df_test['disease_id'].map(system_config.DISEASE_MAP)
        
    # Helper to multi-hot encode HPOs
    def encode_hpos(df_split: pd.DataFrame) -> pd.DataFrame:
        encoded = []
        for idx, row in df_split.iterrows():
            patient_hpos = set(str(row['hpo_ids']).strip().split('|'))
            vec = [1 if term in patient_hpos else 0 for term in hpo_vocab]
            encoded.append(vec)
        return pd.DataFrame(encoded, columns=hpo_vocab)
        
    # Helper to one-hot encode Sex
    sex_categories = ["MALE", "FEMALE", "UNKNOWN_SEX"]
    sex_mapping = {cat: idx for idx, cat in enumerate(sex_categories)}
    
    def encode_sex(df_split: pd.DataFrame) -> pd.DataFrame:
        encoded = []
        for idx, row in df_split.iterrows():
            sex_val = str(row['sex']).strip().upper()
            if sex_val not in sex_categories:
                sex_val = "UNKNOWN_SEX"
            vec = [0] * len(sex_categories)
            vec[sex_mapping[sex_val]] = 1
            encoded.append(vec)
        return pd.DataFrame(encoded, columns=[f"sex_{cat}" for cat in sex_categories])
        
    # Generate CONFIG A features (HPO only)
    X_train_hpo = encode_hpos(df_train)
    X_val_hpo = encode_hpos(df_val)
    X_test_hpo = encode_hpos(df_test)
    
    # Generate CONFIG B features (HPO + Sex)
    X_train_sex = encode_sex(df_train)
    X_val_sex = encode_sex(df_val)
    X_test_sex = encode_sex(df_test)
    
    X_train_plus = pd.concat([X_train_hpo, X_train_sex], axis=1)
    X_val_plus = pd.concat([X_val_hpo, X_val_sex], axis=1)
    X_test_plus = pd.concat([X_test_hpo, X_test_sex], axis=1)
    
    # Output paths
    hpo_only_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_only")
    hpo_plus_sex_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex")
    
    os.makedirs(hpo_only_dir, exist_ok=True)
    os.makedirs(hpo_plus_sex_dir, exist_ok=True)
    
    # Save CONFIG A datasets
    X_train_hpo.to_csv(os.path.join(hpo_only_dir, "X_train.csv"), index=False)
    X_val_hpo.to_csv(os.path.join(hpo_only_dir, "X_validation.csv"), index=False)
    X_test_hpo.to_csv(os.path.join(hpo_only_dir, "X_test.csv"), index=False)
    
    # Save CONFIG B datasets
    X_train_plus.to_csv(os.path.join(hpo_plus_sex_dir, "X_train.csv"), index=False)
    X_val_plus.to_csv(os.path.join(hpo_plus_sex_dir, "X_validation.csv"), index=False)
    X_test_plus.to_csv(os.path.join(hpo_plus_sex_dir, "X_test.csv"), index=False)
    
    # Save target matrices
    y_train.to_csv(os.path.join(hpo_only_dir, "y_train.csv"), index=False, header=["target"])
    y_val.to_csv(os.path.join(hpo_only_dir, "y_validation.csv"), index=False, header=["target"])
    y_test.to_csv(os.path.join(hpo_only_dir, "y_test.csv"), index=False, header=["target"])
    
    y_train.to_csv(os.path.join(hpo_plus_sex_dir, "y_train.csv"), index=False, header=["target"])
    y_val.to_csv(os.path.join(hpo_plus_sex_dir, "y_validation.csv"), index=False, header=["target"])
    y_test.to_csv(os.path.join(hpo_plus_sex_dir, "y_test.csv"), index=False, header=["target"])
    
    # 5. Extract statistics of unseen HPO terms
    unseen_val = set()
    unseen_test = set()
    
    for idx, row in df_val.iterrows():
        patient_hpos = set([h.strip() for h in str(row['hpo_ids']).strip().split('|') if h.strip()])
        unseen_val.update(patient_hpos - set(hpo_vocab))
        
    for idx, row in df_test.iterrows():
        patient_hpos = set([h.strip() for h in str(row['hpo_ids']).strip().split('|') if h.strip()])
        unseen_test.update(patient_hpos - set(hpo_vocab))
        
    # Write preprocessing configuration summary
    preproc_summary = {
        "hpo_vocabulary_size": len(hpo_vocab),
        "vocabulary_checksum": vocab_checksum,
        "sex_encoder": {
            "mapping": sex_mapping,
            "one_hot_columns": [f"sex_{cat}" for cat in sex_categories]
        },
        "configs": {
            "CONFIG_A": {
                "name": "HPO Features Only",
                "dimensions": len(hpo_vocab)
            },
            "CONFIG_B": {
                "name": "HPO Features + Sex",
                "dimensions": len(hpo_vocab) + len(sex_categories)
            }
        },
        "unseen_hpo_terms": {
            "validation_count": len(unseen_val),
            "test_count": len(unseen_test)
        },
        "shapes": {
            "CONFIG_A": {
                "X_train": list(X_train_hpo.shape),
                "X_val": list(X_val_hpo.shape),
                "X_test": list(X_test_hpo.shape)
            },
            "CONFIG_B": {
                "X_train": list(X_train_plus.shape),
                "X_val": list(X_val_plus.shape),
                "X_test": list(X_test_plus.shape)
            },
            "targets": {
                "y_train": len(y_train),
                "y_val": len(y_val),
                "y_test": len(y_test)
            }
        }
    }
    
    summary_path = os.path.join(system_config.PREPROC_ARTIFACTS_DIR, "preprocessing_configuration.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(preproc_summary, f, indent=4)
        
    log.info(f"Preprocessing pipeline completed successfully. Config metadata saved to {summary_path}")
    print("Preprocessing execution completed successfully.")

if __name__ == "__main__":
    execute_pipeline()
