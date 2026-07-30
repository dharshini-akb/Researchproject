import os
import json
import hashlib
import pandas as pd
import numpy as np
from config import system_config
from models.random_forest import RandomForestModel
from models.tabnet import TabNetModel

def main():
    # 1. Load models
    rf_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
    rf_model = RandomForestModel()
    rf_model.load(rf_path)
    
    tabnet_path = os.path.join(system_config.ARTIFACTS_DIR, "tabnet_model.pt")
    tabnet_model = TabNetModel()
    tabnet_model.load(tabnet_path)
    
    # 2. Load vocabulary
    vocab_path = os.path.join(system_config.PREPROC_ARTIFACTS_DIR, "hpo_feature_vocabulary.json")
    with open(vocab_path, "r", encoding="utf-8") as f:
        hpo_vocab = json.load(f)
        
    # 3. Load some patient records
    csv_path = os.path.join(system_config.RAW_DATA_DIR, "selected_set1_patient_records.csv")
    df = pd.read_csv(csv_path)
    
    # Let's run diagnosis for the first 10 records
    prev_vector = None
    prev_probs = None
    
    print("=== PIPELINE DIAGNOSTIC VERIFICATION ===")
    
    for idx, row in df.head(10).iterrows():
        case_id = row['case_id']
        sex = row['sex']
        hpo_ids_str = str(row['hpo_ids'])
        
        # 1. Print accepted HPO IDs
        hpo_ids = [h.strip() for h in hpo_ids_str.split('|') if h.strip()]
        print(f"\n--- Patient Record {idx+1}: {case_id} ---")
        print(f"Accepted HPO IDs: {hpo_ids}")
        
        # 2. Build feature vector
        patient_vector = {hpo_id: 0 for hpo_id in hpo_vocab}
        for hpo_id in hpo_ids:
            if hpo_id in patient_vector:
                patient_vector[hpo_id] = 1
        
        patient_vector["sex_MALE"] = 1 if sex == "MALE" else 0
        patient_vector["sex_FEMALE"] = 1 if sex == "FEMALE" else 0
        patient_vector["sex_UNKNOWN_SEX"] = 1 if sex == "UNKNOWN_SEX" else 0
        
        patient_df = pd.DataFrame([patient_vector])
        patient_df = patient_df.reindex(columns=rf_model.feature_names, fill_value=0)
        
        # 3. Active feature indices
        active_indices = [i for i, val in enumerate(patient_df.values[0]) if val == 1]
        print(f"Active Feature Indices: {active_indices}")
        
        # 4. SHA256 hash of the feature vector
        feat_array = patient_df.values[0]
        hash_object = hashlib.sha256(feat_array.tobytes())
        feat_hash = hash_object.hexdigest()
        print(f"SHA256 Hash of Feature Vector: {feat_hash}")
        
        # 5. Model predicts
        rf_pred = rf_model.predict(patient_df)[0]
        rf_probs = rf_model.predict_proba(patient_df)[0]
        print(f"model.predict(): {rf_pred} ({system_config.DISEASE_NAMES[rf_pred]})")
        print(f"model.predict_proba(): {rf_probs.tolist()}")
        
        # 6. Top 3 probabilities
        sorted_indices = np.argsort(rf_probs)[::-1]
        top_3 = [(idx, rf_probs[idx], system_config.DISEASE_NAMES[idx]) for idx in sorted_indices[:3]]
        print(f"Top 3 Probabilities:")
        for rank, (cls_idx, prob, name) in enumerate(top_3):
            print(f"  {rank+1}. {name} (Class {cls_idx}): {prob:.4f}")
            
        # 7. Check if feature vector differs from previous
        if prev_vector is not None:
            vec_differs = not np.array_equal(feat_array, prev_vector)
            print(f"Feature vector differs from previous prediction: {vec_differs}")
            if not vec_differs:
                print("WARNING: Feature vector is identical to previous!")
            
            probs_identical = np.allclose(rf_probs, prev_probs)
            if vec_differs and probs_identical:
                print("WARNING: Feature vector changed, but predict_proba() remains identical!")
        else:
            print("Feature vector differs from previous prediction: N/A (First record)")
            
        prev_vector = feat_array
        prev_probs = rf_probs

if __name__ == "__main__":
    main()
