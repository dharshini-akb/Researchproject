import os
import re
import json
import random
import pandas as pd
import numpy as np
from config import system_config
from utils import logger

log = logger.get_logger("generate_cohort")

# Frequency term mappings to probability values (based on HPO specifications)
FREQUENCY_MAP = {
    "HP:0040280": 1.0,   # Obligate (100%)
    "HP:0040281": 0.90,  # Very frequent (80-99%)
    "HP:0040282": 0.56,  # Frequent (33-79%)
    "HP:0040283": 0.17,  # Occasional (5-29%)
    "HP:0040284": 0.02,  # Very rare (1-4%)
    "HP:0040285": 0.0,   # Excluded (0%)
}

def parse_frequency_to_fraction(freq_str: str) -> tuple:
    """
    Parses various HPO frequency formats (percentages, fractions, or term IDs) 
    into a tuple of (numerator, denominator) float values.
    """
    if pd.isna(freq_str) or not isinstance(freq_str, str) or freq_str == "":
        return (0.30 * 100.0, 100.0)  # Default baseline frequency if not annotated (30%)
        
    freq_str = freq_str.strip()
    
    # Check HPO term IDs
    if freq_str in FREQUENCY_MAP:
        prob = FREQUENCY_MAP[freq_str]
        return (prob * 100.0, 100.0)
        
    # Check percentage (e.g. 75% or 80%)
    if "%" in freq_str:
        try:
            val = float(freq_str.replace("%", "").strip())
            return (val, 100.0)
        except ValueError:
            pass
            
    # Check fraction (e.g. 3/4 or 12/15)
    match = re.match(r"^(\d+)\s*/\s*(\d+)$", freq_str)
    if match:
        try:
            num = float(match.group(1))
            denom = float(match.group(2))
            if denom > 0:
                return (num, denom)
        except ValueError:
            pass
            
    return (0.30 * 100.0, 100.0)  # Default fallback

def build_disease_phenotype_profiles() -> dict:
    """
    Reads phenotype.hpoa and builds a profile for our three target diseases:
    { disease_id: [ (hpo_id, probability), ... ] }
    """
    hpoa_path = os.path.join(system_config.RAW_DATA_DIR, "phenotype.hpoa")
    df = pd.read_csv(hpoa_path, sep="\t", comment="#")
    
    target_omims = list(system_config.DISEASE_MAP.keys())
    profiles = {}
    
    for omim in target_omims:
        sub_df = df[df["database_id"] == omim]
        if sub_df.empty:
            log.warning(f"Disease {omim} has no annotations in phenotype.hpoa!")
            continue
            
        hpo_groups = {}
        for idx, row in sub_df.iterrows():
            # Skip if negated qualifier present (e.g. NOT HP:xxxxxx)
            qualifier = str(row.get("qualifier", "")).strip().upper()
            if "NOT" in qualifier:
                continue
                
            hpo_id = row["hpo_id"]
            freq_str = str(row.get("frequency", ""))
            num, denom = parse_frequency_to_fraction(freq_str)
            
            if hpo_id not in hpo_groups:
                hpo_groups[hpo_id] = []
            hpo_groups[hpo_id].append((num, denom))
            
        symptom_probs = []
        for hpo_id, fractions in hpo_groups.items():
            total_num = sum(f[0] for f in fractions)
            total_denom = sum(f[1] for f in fractions)
            prob = total_num / total_denom if total_denom > 0 else 0.30
            
            # Exclude HPO terms with 0.0 probability (e.g. if the aggregated frequency is 0%)
            if prob > 0.0:
                symptom_probs.append((hpo_id, prob))
            
        profiles[omim] = symptom_probs
        log.info(f"Built profile for {omim} with {len(symptom_probs)} clinical symptom links (aggregated).")
        
    return profiles

def generate_cohort():
    """
    Generates synthetic patient profiles based on disease symptom probabilities,
    creates split manifests, and saves raw files.
    """
    np.random.seed(42)
    random.seed(42)
    
    profiles = build_disease_phenotype_profiles()
    
    patient_records = []
    case_counter = 1
    
    # Generate 200 patient records per disease
    patients_per_disease = 200
    sexes = ["MALE", "FEMALE", "UNKNOWN_SEX"]
    sex_weights = [0.48, 0.48, 0.04]  # realistic distribution
    
    # Retrieve symptom definitions map from hp.obo for clean labeling
    from preprocessing import data_loader
    hpo_map = data_loader.parse_hpo_obo()
    
    log.info(f"Generating {patients_per_disease} patient cases per disease cohort...")
    
    for omim, symptom_probs in profiles.items():
        for _ in range(patients_per_disease):
            case_id = f"CASE_{case_counter:04d}"
            sex = np.random.choice(sexes, p=sex_weights)
            age = str(np.random.randint(1, 18))  # rare pediatric syndromes mostly
            
            # Partition symptoms into clinical categories
            clusters = {0: [], 1: [], 2: []}
            for h_id, p in symptom_probs:
                name = hpo_map.get(h_id, "").lower()
                if any(kw in name for kw in ["intellectual", "epilepsy", "seizure", "microcephaly", "developmental delay", "behavior", "speech", "brain", "cerebellar", "motor", "learning"]):
                    clusters[0].append((h_id, p))
                elif any(kw in name for kw in ["face", "ear", "eye", "cleft", "forehead", "nose", "mouth", "philtrum", "tooth", "teeth", "dental", "lip"]):
                    clusters[1].append((h_id, p))
                else:
                    clusters[2].append((h_id, p))
            
            # Balance empty clusters
            all_symptom_probs = list(symptom_probs)
            for c in [0, 1, 2]:
                if len(clusters[c]) == 0:
                    clusters[c] = all_symptom_probs
            
            # Determine symptom count realistically (between 4 and 25, average 10)
            n_syms = int(np.clip(np.random.normal(10, 3), 4, min(25, len(symptom_probs))))
            
            # Subgroup generation: choose a random primary manifest category
            primary_cat = np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
            secondary_cat = (primary_cat + 1) % 3
            
            weighted_hpos = []
            weighted_probs = []
            for c in [0, 1, 2]:
                boost = 3.5 if c == primary_cat else (1.8 if c == secondary_cat else 0.6)
                for h_id, p in clusters[c]:
                    weighted_hpos.append(h_id)
                    weighted_probs.append(p * boost)
            
            probs_normalized = np.array(weighted_probs) / sum(weighted_probs)
            
            # Weighted random choice without replacement
            selected_hpos = np.random.choice(weighted_hpos, size=n_syms, replace=False, p=probs_normalized).tolist()
            selected_names = [hpo_map.get(h_id, "Phenotypic feature") for h_id in selected_hpos]
            
            # Join lists with pipe delimiter
            hpo_ids_str = "|".join(selected_hpos)
            symptom_names_str = "|".join(selected_names)
            
            patient_records.append({
                "case_id": case_id,
                "file_path": f"synthetic/{case_id}.json",
                "phenopacket_id": f"PP_{case_id}",
                "patient_id": f"PT_{case_id}",
                "sex": sex,
                "age": age,
                "disease_id": omim,
                "disease_name": system_config.DISEASE_NAMES[system_config.DISEASE_MAP[omim]],
                "hpo_count": len(selected_hpos),
                "hpo_ids": hpo_ids_str,
                "symptom_names": symptom_names_str,
                "excluded_hpo_ids": "",
                "excluded_symptom_names": "",
                "age_of_onset": "Pediatric",
                "pmid": "SYNTHETIC_GENERATOR_V1",
                "source_metadata": json.dumps({"gen_seed": 42})
            })
            case_counter += 1
            
    df_cohort = pd.DataFrame(patient_records)
    
    # Save the synthetic patients file as our new raw patient CSV
    raw_csv_path = os.path.join(system_config.RAW_DATA_DIR, "selected_set1_patient_records.csv")
    os.makedirs(os.path.dirname(raw_csv_path), exist_ok=True)
    df_cohort.to_csv(raw_csv_path, index=False)
    log.info(f"Saved {len(df_cohort)} synthetic patient profiles to {raw_csv_path}")
    
    # Create train, validation, and test split manifests (70% train, 15% val, 15% test)
    # Stratify by disease to maintain balanced classes
    df_train_list = []
    df_val_list = []
    df_test_list = []
    
    for omim in profiles.keys():
        sub_df = df_cohort[df_cohort["disease_id"] == omim]
        shuffled = sub_df.sample(frac=1.0, random_state=42).reset_index(drop=True)
        
        n_val = int(len(shuffled) * 0.15)
        n_test = int(len(shuffled) * 0.15)
        n_train = len(shuffled) - n_val - n_test
        
        df_train_list.append(shuffled.iloc[:n_train])
        df_val_list.append(shuffled.iloc[n_train:n_train+n_val])
        df_test_list.append(shuffled.iloc[n_train+n_val:])
        
    df_train_manifest = pd.concat(df_train_list).sample(frac=1.0, random_state=42).reset_index(drop=True)
    df_val_manifest = pd.concat(df_val_list).sample(frac=1.0, random_state=42).reset_index(drop=True)
    df_test_manifest = pd.concat(df_test_list).sample(frac=1.0, random_state=42).reset_index(drop=True)
    
    # Save split manifests
    os.makedirs(system_config.SPLITS_DIR, exist_ok=True)
    df_train_manifest[["case_id"]].to_csv(os.path.join(system_config.SPLITS_DIR, "train_manifest.csv"), index=False)
    df_val_manifest[["case_id"]].to_csv(os.path.join(system_config.SPLITS_DIR, "validation_manifest.csv"), index=False)
    df_test_manifest[["case_id"]].to_csv(os.path.join(system_config.SPLITS_DIR, "test_manifest.csv"), index=False)
    
    log.info(f"Split sizes created - Train: {len(df_train_manifest)}, Val: {len(df_val_manifest)}, Test: {len(df_test_manifest)}")
    print("Cohort generation and split manifest configuration finished.")

if __name__ == "__main__":
    generate_cohort()
