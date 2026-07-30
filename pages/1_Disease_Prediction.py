import streamlit as st
import os
import json
import pandas as pd
import numpy as np
from config import system_config
from components import cards
from preprocessing import data_loader
from models.random_forest import RandomForestModel
from models.tabnet import TabNetModel

# Custom helper to load and inject CSS
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(system_config.WORKSPACE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    load_css(css_path)

st.title("🧬 Patient Diagnostic Prediction Panel")
st.markdown("Enter patient clinical phenotypes using the Human Phenotype Ontology (HPO) dictionary to generate diagnostic predictions.")

# Load HPO OBO mapping for autocomplete labels
@st.cache_resource
def get_hpo_terms_map():
    return data_loader.parse_hpo_obo()

hpo_map = get_hpo_terms_map()

# Load the feature vocabulary of the model
vocab_path = os.path.join(system_config.PREPROC_ARTIFACTS_DIR, "hpo_feature_vocabulary.json")
if not os.path.exists(vocab_path):
    st.error("Model feature vocabulary not found. Please run preprocessing pipeline first.")
    st.stop()
    
with open(vocab_path, "r", encoding="utf-8") as f:
    hpo_vocab = json.load(f)

# Combine vocabulary with human readable labels for search selection
hpo_choices = []
for hpo_id in hpo_vocab:
    label = hpo_map.get(hpo_id, "Unknown phenotypic feature")
    hpo_choices.append(f"{label} ({hpo_id})")
hpo_choices = sorted(hpo_choices)

# Group HPO choices by common anatomical systems for presentation
grouped_categories = {
    "Cognitive / Neurological": [],
    "Facial / Craniofacial": [],
    "Skeletal / Musculoskeletal": [],
    "Growth / Development": [],
    "Dental / Dental Anomalies": [],
    "Other Features": []
}

for choice in hpo_choices:
    lower_choice = choice.lower()
    if any(keyword in lower_choice for keyword in ["intellectual", "epilepsy", "seizure", "microcephaly", "developmental delay", "behavior", "speech"]):
        grouped_categories["Cognitive / Neurological"].append(choice)
    elif any(keyword in lower_choice for keyword in ["face", "ear", "eye", "cleft", "forehead", "nose", "mouth", "philtrum"]):
        grouped_categories["Facial / Craniofacial"].append(choice)
    elif any(keyword in lower_choice for keyword in ["joint", "digit", "finger", "toe", "scoliosis", "short stature", "limb"]):
        grouped_categories["Skeletal / Musculoskeletal"].append(choice)
    elif any(keyword in lower_choice for keyword in ["growth", "weight", "height", "fail to thrive"]):
        grouped_categories["Growth / Development"].append(choice)
    elif any(keyword in lower_choice for keyword in ["tooth", "teeth", "dental", "conical"]):
        grouped_categories["Dental / Dental Anomalies"].append(choice)
    else:
        grouped_categories["Other Features"].append(choice)

# --- Load Trained Models ---
def get_file_mtime(filepath):
    return os.path.getmtime(filepath) if os.path.exists(filepath) else 0

@st.cache_resource
def load_trained_models(rf_mtime, tabnet_mtime):
    rf_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
    rf = RandomForestModel()
    rf.load(rf_path)
    
    tabnet_path = os.path.join(system_config.ARTIFACTS_DIR, "tabnet_model.pt")
    tabnet = TabNetModel()
    tabnet.load(tabnet_path)
    
    return rf, tabnet

try:
    rf_file_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
    tabnet_file_path = os.path.join(system_config.ARTIFACTS_DIR, "tabnet_model.pt")
    rf_model, tabnet_model = load_trained_models(get_file_mtime(rf_file_path), get_file_mtime(tabnet_file_path))
except Exception as e:
    st.error(f"Failed to load trained models: {e}. Please ensure you have trained the models first.")
    st.stop()

# --- Clinician Inputs Panel ---
st.markdown("### 1. Clinical Presentation")
col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    st.markdown("#### Patient Symptoms")
    # Category filter helper
    cat_selection = st.selectbox("Filter symptoms dictionary by category:", ["Show All"] + list(grouped_categories.keys()))
    
    current_choices = hpo_choices
    if cat_selection != "Show All":
        current_choices = grouped_categories[cat_selection]
        
    # Maintain list of selected symptoms in session state to prevent loss of state on filter change
    if "selected_symptoms" not in st.session_state:
        st.session_state["selected_symptoms"] = []
        
    options = sorted(list(set(current_choices) | set(st.session_state["selected_symptoms"])))
    
    selected_symptoms_labels = st.multiselect(
        "Search and select HPO symptoms:",
        options=options,
        default=st.session_state["selected_symptoms"],
        help="Type to search through the model vocabulary of observed patient symptoms",
        key="symptoms_multiselect"
    )
    st.session_state["selected_symptoms"] = selected_symptoms_labels

with col2:
    st.markdown("#### Biological Sex & Thresholds")
    patient_sex = st.selectbox("Biological Sex:", ["MALE", "FEMALE", "UNKNOWN_SEX"])
    confidence_threshold = st.slider(
        "Confidence Diagnostic Threshold:",
        min_value=0.10,
        max_value=0.90,
        value=system_config.DEFAULT_CONFIDENCE_THRESHOLD,
        step=0.05,
        help="Minimum confidence value required to confirm a positive genetic syndromic match."
    )

# Extract HPO IDs from selected labels
selected_hpo_ids = []
for label in selected_symptoms_labels:
    # Extract ID from parenthesis
    hpo_id = label.split("(")[-1].replace(")", "").strip()
    selected_hpo_ids.append(hpo_id)

# Create input vector matching CONFIG_B (HPO + Sex)
# Vocabulary features
patient_vector = {hpo_id: 0 for hpo_id in hpo_vocab}
for hpo_id in selected_hpo_ids:
    if hpo_id in patient_vector:
        patient_vector[hpo_id] = 1

# Sex features (one-hot)
patient_vector["sex_MALE"] = 1 if patient_sex == "MALE" else 0
patient_vector["sex_FEMALE"] = 1 if patient_sex == "FEMALE" else 0
patient_vector["sex_UNKNOWN_SEX"] = 1 if patient_sex == "UNKNOWN_SEX" else 0

patient_df = pd.DataFrame([patient_vector])
# Align features exactly with the model's expected feature set
patient_df = patient_df.reindex(columns=rf_model.feature_names, fill_value=0)

# --- Trigger Prediction ---
st.write("")
if st.button("Analyze & Predict Disease"):
    if not selected_hpo_ids:
        st.warning("Please select at least one symptom to run predictions.")
    else:
        with st.spinner("Executing model inferences and computing probability distributions..."):
            # 1. Random Forest Predictions
            rf_probs = rf_model.predict_proba(patient_df)[0]
            
            # 2. TabNet Predictions
            tabnet_probs = tabnet_model.predict_proba(patient_df)[0]
            
            # Cache the current state for explanation pages
            st.session_state["patient_df"] = patient_df
            st.session_state["selected_hpo_names"] = [l.split(" (")[0] for l in selected_symptoms_labels]
            st.session_state["rf_probs"] = rf_probs
            st.session_state["tabnet_probs"] = tabnet_probs
            st.session_state["prediction_made"] = True
            
            # Use RF as the primary model (winner of evaluation)
            top_class = int(np.argmax(rf_probs))
            top_prob = float(rf_probs[top_class])
            disease_name = system_config.DISEASE_NAMES[top_class]
            disease_omim = system_config.DISEASE_OMIMS[top_class]
            
            st.toast("Predictive modeling inference complete!", icon="✅")
            
        st.markdown("### 2. Predictive Results (Random Forest - Winner Model)")
        
        # Check against diagnostic confidence threshold
        if top_prob < confidence_threshold:
            st.error("No confident prediction found.")
            st.warning(f"The highest prediction probability is {top_prob*100:.1f}%, which is below the required threshold of {confidence_threshold*100:.1f}%.")
        else:
            # Save all prediction results into Streamlit session_state
            st.session_state["disease_name"] = disease_name
            st.session_state["disease_omim"] = disease_omim
            st.session_state["top_prob"] = top_prob
            st.session_state["top_class"] = top_class
            st.session_state["selected_hpo_ids"] = selected_hpo_ids
            st.session_state["patient_sex"] = patient_sex
            st.session_state["confidence_threshold"] = confidence_threshold
            
            tab_top_class = int(np.argmax(tabnet_probs))
            tab_top_prob = float(tabnet_probs[tab_top_class])
            st.session_state["tab_top_class"] = tab_top_class
            st.session_state["tab_top_prob"] = tab_top_prob
            
            # Switch page to the Prediction Analytics Dashboard
            st.switch_page("pages/6_Prediction_Analytics_Dashboard.py")
            
            c1, c2 = st.columns([1, 1.2], gap="large")
            with c1:
                st.markdown("#### Primary Indicated Diagnosis")
                badge_type = "success" if top_prob > 0.8 else "warning"
                cards.medical_card(
                    title=disease_name,
                    content=f"Primary diagnosis matches this cohort with OMIM code: <strong>{disease_omim}</strong>. Patient manifests {len(selected_hpo_ids)} active symptoms within model scope.",
                    badge_text=f"{top_prob*100:.1f}% Confidence",
                    badge_type=badge_type
                )
                
            with c2:
                st.markdown("#### Probability Distribution Profiles")
                # Sort classes by probability rank
                sorted_ranks = np.argsort(rf_probs)[::-1]
                for rank_idx, cls in enumerate(sorted_ranks):
                    cards.prediction_probability_card(
                        disease_name=system_config.DISEASE_NAMES[cls],
                        omim_id=system_config.DISEASE_OMIMS[cls],
                        probability=rf_probs[cls],
                        rank=rank_idx + 1
                    )
                    
        st.write("")
        st.write("")
        st.markdown("### 3. Alternative Predictive Results (TabNet Model)")
        c1, c2 = st.columns([1, 1.2], gap="large")
        
        tab_top_class = int(np.argmax(tabnet_probs))
        tab_top_prob = float(tabnet_probs[tab_top_class])
        
        with c1:
            st.markdown("#### TabNet Indicated Diagnosis")
            badge_t = "success" if tab_top_prob > 0.8 else "warning"
            cards.medical_card(
                title=system_config.DISEASE_NAMES[tab_top_class],
                content=f"TabNet network predicts: <strong>{system_config.DISEASE_NAMES[tab_top_class]}</strong> (OMIM: {system_config.DISEASE_OMIMS[tab_top_class]}).",
                badge_text=f"{tab_top_prob*100:.1f}% Conf.",
                badge_type=badge_t
            )
            
        with c2:
            st.markdown("#### TabNet Probability Distribution Profiles")
            sorted_ranks_tab = np.argsort(tabnet_probs)[::-1]
            for rank_idx, cls in enumerate(sorted_ranks_tab):
                cards.prediction_probability_card(
                    disease_name=system_config.DISEASE_NAMES[cls],
                    omim_id=system_config.DISEASE_OMIMS[cls],
                    probability=tabnet_probs[cls],
                    rank=rank_idx + 1
                )
                
        st.info("💡 Tip: To inspect the feature contribution plots for this prediction, navigate to the **Explainability** page.")
