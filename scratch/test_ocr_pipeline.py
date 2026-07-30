import os
import json
import hashlib
import pandas as pd
import numpy as np
from config import system_config
from utils import ocr_helper
from models.random_forest import RandomForestModel
from models.tabnet import TabNetModel

def main():
    # Load vocabulary and synonyms
    vocab_path = os.path.join(system_config.PREPROC_ARTIFACTS_DIR, "hpo_feature_vocabulary.json")
    obo_path = os.path.join(system_config.RAW_DATA_DIR, "hp.obo")
    hpo_synonyms = ocr_helper.load_hpo_synonyms(vocab_path, obo_path)
    
    # Load RF model
    rf_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
    rf_model = RandomForestModel()
    rf_model.load(rf_path)
    
    # Let's define three different patient clinical notes
    patient_notes = [
        # Patient 1: White-Sutton syndrome symptoms
        """
        Patient Name: John Doe
        Age: 5 years
        Sex: Male
        Chief Complaints:
        - The child has developmental delay and speech delay.
        - We noticed microcephaly and hypotonia during examination.
        - Patient shows autistic behavior.
        """,
        # Patient 2: Xia-Gibbs syndrome symptoms
        """
        Patient Name: Jane Smith
        Age: 7 years
        Sex: Female
        Chief Complaints:
        - The child has sleep disturbance and global developmental delay.
        - Hypotonia is present.
        - Patient prefers to be alone.
        """,
        # Patient 3: Cornelia de Lange syndrome symptoms
        """
        Patient Name: Baby Bob
        Age: 2 years
        Sex: Male
        Chief Complaints:
        - Patient presents with cleft palate and microcephaly.
        - Feeding difficulties are observed.
        - No speech delay or developmental delay detected.
        """,
        # Patient 4: Negation Test Case
        """
        Patient Name: Negation Tester
        Age: 4 years
        Sex: Female
        Chief Complaints:
        - No hypotonia.
        - Speech delay absent.
        - Microcephaly is present.
        """
    ]
    
    prev_hash = None
    prev_probs = None
    
    print("=== OCR TO PREDICTION PIPELINE DIAGNOSIS ===")
    
    for i, note in enumerate(patient_notes):
        print(f"\n--- Patient {i+1} Note ---")
        print(note.strip())
        
        # 1. Run extract and map text using the new OCR pipeline
        mapped, unmatched, ignored_dem, ignored_adm, rejected = ocr_helper.extract_and_map_ocr_text(note, hpo_synonyms)
        final_hpo_ids = list(mapped.keys())
        
        # Determine sex
        sex = "UNKNOWN_SEX"
        if "sex: male" in note.lower() or "male" in note.lower():
            sex = "MALE"
        elif "sex: female" in note.lower() or "female" in note.lower():
            sex = "FEMALE"
            
        print(f"\n1. Final Accepted HPO IDs: {final_hpo_ids}")
        
        # 2. Build feature vector
        patient_vector = {hpo_id: 0 for hpo_id in rf_model.feature_names} # Use feature_names directly
        for hpo_id in final_hpo_ids:
            if hpo_id in patient_vector:
                patient_vector[hpo_id] = 1
        patient_vector["sex_MALE"] = 1 if sex == "MALE" else 0
        patient_vector["sex_FEMALE"] = 1 if sex == "FEMALE" else 0
        patient_vector["sex_UNKNOWN_SEX"] = 1 if sex == "UNKNOWN_SEX" else 0
        
        patient_df = pd.DataFrame([patient_vector])
        patient_df = patient_df.reindex(columns=rf_model.feature_names, fill_value=0)
        
        # Active feature indices
        active_indices = [idx for idx, val in enumerate(patient_df.values[0]) if val == 1]
        print(f"2. Final Active Feature Indices: {active_indices}")
        
        # 3. SHA256 hash of the feature vector
        feat_array = patient_df.values[0]
        hash_object = hashlib.sha256(feat_array.tobytes())
        feat_hash = hash_object.hexdigest()
        print(f"3. SHA256 Hash of Feature Vector: {feat_hash}")
        
        # 4. model.predict()
        pred = rf_model.predict(patient_df)[0]
        print(f"4. model.predict(): {pred} ({system_config.DISEASE_NAMES[pred]})")
        
        # 5. model.predict_proba()
        probs = rf_model.predict_proba(patient_df)[0]
        print(f"5. model.predict_proba(): {probs.tolist()}")
        
        # 6. Top 3 probabilities
        sorted_indices = np.argsort(probs)[::-1]
        print(f"6. Top 3 Probabilities:")
        for rank, cls_idx in enumerate(sorted_indices[:3]):
            print(f"  {rank+1}. {system_config.DISEASE_NAMES[cls_idx]} (Class {cls_idx}): {probs[cls_idx]:.4f}")
            
        # 7. Print whether the feature vector differs from the previous prediction
        if prev_hash is not None:
            vec_differs = (feat_hash != prev_hash)
            print(f"7. Feature vector differs from previous prediction: {vec_differs}")
            
            probs_identical = np.allclose(probs, prev_probs)
            if vec_differs and probs_identical:
                print("WARNING: Feature vector changed, but predict_proba() remains identical!")
        else:
            print("7. Feature vector differs from previous prediction: N/A (First record)")
            
        prev_hash = feat_hash
        prev_probs = probs

if __name__ == "__main__":
    main()
