import os
import pandas as pd
from typing import Dict, Tuple, List, Set
from config import system_config
from utils import logger

log = logger.get_logger("data_loader")

def parse_hpo_obo(obo_path: str = None) -> Dict[str, str]:
    """
    Parses the hp.obo file and returns a mapping from HPO ID (e.g. HP:0001249)
    to its human-readable term name (e.g. Intellectual disability).
    """
    if obo_path is None:
        obo_path = os.path.join(system_config.RAW_DATA_DIR, "hp.obo")
        
    log.info(f"Parsing HPO ontology from {obo_path}...")
    if not os.path.exists(obo_path):
        log.warning(f"hp.obo not found at {obo_path}. Returning empty vocabulary mapping.")
        return {}
        
    hpo_map = {}
    current_id = None
    current_name = None
    
    with open(obo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if current_id and current_name:
                    hpo_map[current_id] = current_name
                current_id = None
                current_name = None
            elif line.startswith("id:"):
                current_id = line.split("id:")[1].strip()
            elif line.startswith("name:"):
                current_name = line.split("name:")[1].strip()
                
        # Add the last term
        if current_id and current_name:
            hpo_map[current_id] = current_name
            
    log.info(f"Loaded {len(hpo_map)} HPO term definitions from ontology.")
    return hpo_map

def load_patient_records(csv_path: str = None) -> pd.DataFrame:
    """
    Loads raw three disease patient records.
    """
    if csv_path is None:
        # We prefer using selected_set1_patient_records.csv or three_disease_patient_records.csv
        csv_path = os.path.join(system_config.RAW_DATA_DIR, "selected_set1_patient_records.csv")
        
    log.info(f"Loading patient records from {csv_path}...")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Patient records file not found at {csv_path}")
        
    df = pd.read_csv(csv_path)
    log.info(f"Loaded {len(df)} records with columns: {list(df.columns)}")
    return df

def load_splits_manifests() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads train, validation, and test split manifests containing case IDs.
    """
    train_path = os.path.join(system_config.SPLITS_DIR, "train_manifest.csv")
    val_path = os.path.join(system_config.SPLITS_DIR, "validation_manifest.csv")
    test_path = os.path.join(system_config.SPLITS_DIR, "test_manifest.csv")
    
    log.info("Loading train/val/test manifests...")
    
    if not (os.path.exists(train_path) and os.path.exists(val_path) and os.path.exists(test_path)):
        raise FileNotFoundError("One or more split manifests are missing from data/splits/ directory.")
        
    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)
    
    log.info(f"Loaded manifests - Train: {len(df_train)}, Val: {len(df_val)}, Test: {len(df_test)}")
    return df_train, df_val, df_test
