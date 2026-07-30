import os
import sys
import json
import joblib
import pandas as pd

# Add workspace to path
WORKSPACE_DIR = r"d:\finalresearchproject"
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from preprocessing import data_loader
from config import system_config

PROCESSED_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "processed")
PREPROC_ARTIFACTS_DIR = os.path.join(PROCESSED_DATA_DIR, "metadata")
MODEL_PATH = os.path.join(WORKSPACE_DIR, "models", "rf_model.joblib")
OUTPUT_EXCEL = os.path.join(WORKSPACE_DIR, "project_hpo_feature_audit.xlsx")

def main():
    print("Starting HPO feature audit...")
    
    # 1. Parse HPO OBO definitions
    hpo_map = data_loader.parse_hpo_obo()
    
    # 2. Load model feature names
    state = joblib.load(MODEL_PATH)
    model_features = state["feature_names"]
    
    # 3. Load HPO feature vocabulary
    vocab_path = os.path.join(PREPROC_ARTIFACTS_DIR, "hpo_feature_vocabulary.json")
    with open(vocab_path, "r", encoding="utf-8") as f:
        hpo_vocab = json.load(f)
    hpo_vocab_set = set(hpo_vocab)
    
    # 4. Load patient records
    records_path = os.path.join(PROCESSED_DATA_DIR, "cleaned_patient_records.csv")
    df = pd.read_csv(records_path)
    
    # Clean disease IDs and maps
    disease_names_map = {
        "OMIM:616364": "White-Sutton syndrome",
        "OMIM:615829": "Xia-Gibbs syndrome",
        "OMIM:122470": "Cornelia de Lange syndrome 1"
    }
    
    # Group HPOs by disease from records
    hpo_to_diseases = {}
    disease_to_hpos = {name: set() for name in disease_names_map.values()}
    
    for _, row in df.iterrows():
        dis_id = row['disease_id']
        dis_name = disease_names_map.get(dis_id)
        if not dis_name:
            continue
        
        h_ids = str(row['hpo_ids']).strip().split('|')
        for h in h_ids:
            h = h.strip()
            if not h or h == "nan":
                continue
            
            # Map HPO -> Diseases
            if h not in hpo_to_diseases:
                hpo_to_diseases[h] = set()
            hpo_to_diseases[h].add(dis_name)
            
            # Map Disease -> HPOs
            disease_to_hpos[dis_name].add(h)
            
    # Compile the complete set of HPOs used/encountered in the project
    all_hpos = sorted(list(set(hpo_vocab) | set(hpo_to_diseases.keys())))
    
    # Create the rows for All HPO Features
    all_features_data = []
    
    for term in all_hpos:
        # Determine feature index in vocabulary/model (N/A for out of vocab)
        feature_idx = "N/A"
        if term in hpo_vocab:
            feature_idx = hpo_vocab.index(term)
            
        name = hpo_map.get(term, "Unknown Phenotypic Feature")
        
        # Check training, feature vector, streamlit search usage
        used_training = "Yes" if term in hpo_vocab else "No"
        present_vector = "Yes" if term in model_features else "No"
        streamlit_search = "Yes" if term in hpo_vocab else "No"
        
        # Associated diseases
        assoc_diseases_set = hpo_to_diseases.get(term, set())
        assoc_diseases_str = ", ".join(sorted(list(assoc_diseases_set))) if assoc_diseases_set else "None"
        
        # Determine uniqueness
        num_diseases = len(assoc_diseases_set)
        if num_diseases == 1:
            sharing_type = "Unique to one disease"
        elif num_diseases == 2:
            sharing_type = "Shared by two diseases"
        elif num_diseases == 3:
            sharing_type = "Shared by all three diseases"
        else:
            sharing_type = "Unassociated"
            
        all_features_data.append({
            "Feature Index": feature_idx,
            "HPO ID": term,
            "HPO Name": name,
            "Used During Training (Yes/No)": used_training,
            "Present in Feature Vector (Yes/No)": present_vector,
            "Appears in Streamlit Search (Yes/No)": streamlit_search,
            "Sharing Type": sharing_type,
            "Diseases Associated With": assoc_diseases_str
        })
        
    df_all_features = pd.DataFrame(all_features_data)
    
    # Filter for disease specific sheets
    def make_disease_df(dis_name):
        hpos_for_dis = disease_to_hpos[dis_name]
        data = []
        for term in sorted(list(hpos_for_dis)):
            row_data = df_all_features[df_all_features["HPO ID"] == term].iloc[0]
            data.append({
                "HPO ID": term,
                "HPO Name": row_data["HPO Name"],
                "Feature Index": row_data["Feature Index"],
                "Sharing Type": row_data["Sharing Type"],
                "All Associated Diseases": row_data["Diseases Associated With"]
            })
        return pd.DataFrame(data)
        
    df_white_sutton = make_disease_df("White-Sutton syndrome")
    df_xia_gibbs = make_disease_df("Xia-Gibbs syndrome")
    df_cornelia = make_disease_df("Cornelia de Lange syndrome 1")
    
    # Shared HPOs sheet
    df_shared = df_all_features[df_all_features["Sharing Type"].isin(["Shared by two diseases", "Shared by all three diseases"])].copy()
    df_shared = df_shared[["HPO ID", "HPO Name", "Feature Index", "Sharing Type", "Diseases Associated With"]].reset_index(drop=True)
    
    # Counts and Validation Summary Sheet
    total_hpos = len(all_hpos)
    unique_ws = len(df_all_features[df_all_features["Sharing Type"] == "Unique to one disease"][df_all_features["Diseases Associated With"] == "White-Sutton syndrome"])
    unique_xg = len(df_all_features[df_all_features["Sharing Type"] == "Unique to one disease"][df_all_features["Diseases Associated With"] == "Xia-Gibbs syndrome"])
    unique_cdl = len(df_all_features[df_all_features["Sharing Type"] == "Unique to one disease"][df_all_features["Diseases Associated With"] == "Cornelia de Lange syndrome 1"])
    shared_hpos_count = len(df_shared)
    
    unused_hpos = df_all_features[df_all_features["Diseases Associated With"] == "None"]
    unused_hpos_count = len(unused_hpos)
    
    # Consistency validations
    mismatches = []
    for term in all_hpos:
        in_vocab = term in hpo_vocab
        in_model = term in model_features
        in_streamlit = in_vocab # Streamlit loads from hpo_feature_vocabulary.json
        
        # We expect terms used during training to be in the model feature vector
        if in_vocab != in_model:
            mismatches.append(f"{term} ({hpo_map.get(term, 'Unknown')}): Vocab state ({in_vocab}) != Model feature state ({in_model})")
        if in_vocab != in_streamlit:
            mismatches.append(f"{term} ({hpo_map.get(term, 'Unknown')}): Vocab state ({in_vocab}) != Streamlit state ({in_streamlit})")
            
    # Check out-of-vocabulary terms in records
    oov_terms = [t for t in all_hpos if t not in hpo_vocab]
    if oov_terms:
        print(f"Found {len(oov_terms)} Out-of-Vocabulary HPO terms in patient records: {oov_terms}")
        for t in oov_terms:
            mismatches.append(f"Out-of-Vocabulary term in dataset: {t} ({hpo_map.get(t, 'Unknown')}) - Present in data but NOT in training vocabulary/model features/Streamlit UI.")
            
    validation_status = "PASSED" if not mismatches else "WARNING / ANOMALIES DETECTED"
    
    summary_data = {
        "Metric": [
            "Total HPO Features Evaluated",
            "Unique White-Sutton HPOs",
            "Unique Xia-Gibbs HPOs",
            "Unique Cornelia de Lange HPOs",
            "Shared HPOs (Associated with 2+ diseases)",
            "Unused HPOs in Dataset (Associated with 0 diseases)",
            "Validation Status",
            "Total Mismatches/Anomalies Detected"
        ],
        "Value": [
            total_hpos,
            unique_ws,
            unique_xg,
            unique_cdl,
            shared_hpos_count,
            unused_hpos_count,
            validation_status,
            len(mismatches)
        ]
    }
    df_summary = pd.DataFrame(summary_data)
    
    df_mismatches = pd.DataFrame({
        "Mismatch/Anomaly Details": mismatches if mismatches else ["None. All feature counts, mappings, and pipeline steps are fully consistent."]
    })
    
    # 7. Write to Excel
    print(f"Writing audit output to Excel file: {OUTPUT_EXCEL}")
    with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
        df_all_features.to_excel(writer, sheet_name="All HPO Features", index=False)
        df_white_sutton.to_excel(writer, sheet_name="White-Sutton HPOs", index=False)
        df_xia_gibbs.to_excel(writer, sheet_name="Xia-Gibbs HPOs", index=False)
        df_cornelia.to_excel(writer, sheet_name="Cornelia de Lange HPOs", index=False)
        df_shared.to_excel(writer, sheet_name="Shared HPOs", index=False)
        
        # Write validation summary
        df_summary.to_excel(writer, sheet_name="Validation Summary", index=False, startrow=0)
        df_mismatches.to_excel(writer, sheet_name="Validation Summary", index=False, startrow=len(df_summary) + 3)
        
    print("HPO Feature Audit completed successfully!")

if __name__ == "__main__":
    main()
