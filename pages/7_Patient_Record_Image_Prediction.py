import streamlit as st
import os
import json
import sys
import pandas as pd
import numpy as np
import cv2
from PIL import Image
from config import system_config
from components import cards
from preprocessing import data_loader
from models.random_forest import RandomForestModel
from models.tabnet import TabNetModel
from utils import ocr_helper

# Ensure stdout/stderr uses UTF-8 encoding on Windows to prevent charmap encoding errors
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Custom helper to load and inject CSS
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(system_config.WORKSPACE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    load_css(css_path)

st.title("📋 Patient Record Image Prediction")
st.markdown("Upload an image of a patient medical record (e.g. OP sheet, clinical notes, discharge summary) to extract symptoms via OCR, map them to HPO terms, and predict syndromes.")

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
hpo_id_to_choice = {}
for hpo_id in hpo_vocab:
    label = hpo_map.get(hpo_id, "Unknown phenotypic feature")
    choice_str = f"{label} ({hpo_id})"
    hpo_choices.append(choice_str)
    hpo_id_to_choice[hpo_id] = choice_str
hpo_choices = sorted(hpo_choices)

# --- Load synonym expanded mappings ---
@st.cache_data
def get_cached_synonyms():
    return ocr_helper.load_hpo_synonyms(vocab_path, os.path.join(system_config.RAW_DATA_DIR, "hp.obo"))

hpo_synonyms = get_cached_synonyms()

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

# --- Layout ---
col_config, col_main = st.columns([1, 3.2], gap="large")

with col_config:
    st.markdown("### 🛠️ Configuration")
    patient_sex = st.selectbox("Biological Sex:", ["MALE", "FEMALE", "UNKNOWN_SEX"], key="img_patient_sex")
    confidence_threshold = st.slider(
        "Diagnostic Threshold:",
        min_value=0.10,
        max_value=0.90,
        value=system_config.DEFAULT_CONFIDENCE_THRESHOLD,
        step=0.05,
        help="Minimum confidence value required to confirm a positive genetic syndromic match.",
        key="img_conf_threshold"
    )

with col_main:
    st.markdown("### 📤 Upload Patient Record Image")
    uploaded_file = st.file_uploader(
        "Choose patient record image (PNG, JPG, JPEG)...",
        type=["png", "jpg", "jpeg"],
        help="Upload patient OP sheets, case notes, or handwritten records"
    )

    if uploaded_file is not None:
        # Save uploaded image to temp directory/bytes
        img = Image.open(uploaded_file)
        
        # Display image preview in an expander
        with st.expander("🖼️ Patient Record Image Preview", expanded=True):
            st.image(img, use_container_width=True)
            
        # Button to run/rerun OCR to prevent running it automatically on every interaction
        run_ocr = st.button("🔍 Extract Text & Detect Symptoms")
        
        # Check if we have cached OCR results for the current file
        file_hash = f"{uploaded_file.name}_{uploaded_file.size}"
        is_new_file = "last_file_hash" not in st.session_state or st.session_state["last_file_hash"] != file_hash
        
        if is_new_file or run_ocr:
            # Clear all previous prediction state, widget state, and SHAP results to prevent stale data usage
            state_keys_to_clear = [
                "manual_hpo_multiselect", "manual_hpo_selections", "verified_hpo_ids", 
                "extracted_hpo_ids", "raw_text", "ocr_confidence", "mapped_details", 
                "unmatched_lines", "ignored_demographics", "ignored_administrative", 
                "rejected_non_clinical", "prediction_made", "disease_name", 
                "disease_omim", "top_prob", "top_class", "rf_probs", "tabnet_probs", 
                "patient_df", "selected_hpo_names", "selected_hpo_ids", "patient_sex"
            ]
            for key in state_keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
                    
        if "raw_text" not in st.session_state or run_ocr:
            if run_ocr:
                with st.spinner("Extracting text using OCR engine..."):
                    # Save PIL image temporarily or convert to numpy array
                    img_np = np.array(img)
                    
                    try:
                        reader = ocr_helper.get_ocr_reader()
                        ocr_results = reader.readtext(img_np)
                        
                        raw_text = "\n".join([res[1] for res in ocr_results])
                        confidences = [res[2] for res in ocr_results]
                        avg_conf = np.mean(confidences) if confidences else 0.0
                        
                        st.session_state["raw_text"] = raw_text
                        st.session_state["ocr_confidence"] = avg_conf
                        
                        # Process and map text
                        mapped, unmatched_lines, ignored_demographics, ignored_administrative, rejected_non_clinical = ocr_helper.extract_and_map_ocr_text(raw_text, hpo_synonyms)
                        
                        # Initial selection of mapped HPOs
                        st.session_state["extracted_hpo_ids"] = list(mapped.keys())
                        st.session_state["last_file_hash"] = file_hash
                        st.session_state["mapped_details"] = mapped
                        st.session_state["unmatched_lines"] = unmatched_lines
                        st.session_state["ignored_demographics"] = ignored_demographics
                        st.session_state["ignored_administrative"] = ignored_administrative
                        st.session_state["rejected_non_clinical"] = rejected_non_clinical
                        st.toast("OCR extraction and HPO mapping completed successfully!", icon="✅")
                    except Exception as ex:
                        import logging
                        logger_internal = logging.getLogger("streamlit_app")
                        logger_internal.exception("Detailed OCR failure exception:")
                        st.error("OCR processing failed.\nPlease check OCR configuration.")
                        st.stop()

        if "raw_text" in st.session_state:
            raw_text = st.session_state["raw_text"]
            avg_conf = st.session_state["ocr_confidence"]
            mapped = st.session_state["mapped_details"]
            
            # --- Layout for Results ---
            c_text, c_stats = st.columns([2, 1], gap="medium")
            
            with c_text:
                st.markdown("#### 📝 Extracted Clinical Text")
                st.text_area("OCR Raw Transcript:", value=raw_text, height=200, disabled=True)
                
            with c_stats:
                st.markdown("#### 📊 OCR & Ontology Stats")
                st.metric("OCR Confidence Score", f"{avg_conf * 100:.1f}%")
                st.metric("Symptom Matches Detected", f"{len(mapped)}")
                
            # --- Doctor Validation Panel ---
            st.markdown("---")
            st.markdown("### 🧑‍⚕️ Doctor Verification Panel")
            
            # Display Ignored Metadata and Rejections in clean hospital-style tabs
            tab_metadata, tab_rejections = st.tabs(["📝 Ignored Demographic & Admin Info", "🚫 Rejected Matches (Negation/Demographics)"])
            
            with tab_metadata:
                col_dem, col_adm = st.columns(2)
                with col_dem:
                    st.markdown("##### 👤 Ignored Demographic Fields")
                    ignored_dem = st.session_state.get("ignored_demographics", [])
                    if ignored_dem:
                        for item in ignored_dem:
                            st.info(f"Ignored: **{item}**")
                    else:
                        st.write("No demographic fields ignored.")
                        
                with col_adm:
                    st.markdown("##### 🏢 Ignored Administrative Fields")
                    ignored_adm = st.session_state.get("ignored_administrative", [])
                    if ignored_adm:
                        for item in ignored_adm:
                            st.warning(f"Ignored: **{item}**")
                    else:
                        st.write("No administrative fields ignored.")
                        
            with tab_rejections:
                st.markdown("##### ❌ Rejected Non-clinical & Administrative Terms")
                rejected_list = st.session_state.get("rejected_non_clinical", [])
                if rejected_list:
                    rej_data = []
                    for r in rejected_list:
                        rej_data.append({
                            "Extracted Text Fragment": r["phrase"],
                            "Rejection Reason": r["reason"],
                            "Action Taken": r["target"]
                        })
                    st.table(pd.DataFrame(rej_data))
                else:
                    st.write("No terms were rejected.")
                    
            st.write("")
            st.markdown("#### Detected Clinical Symptoms")
            st.markdown("Verify the extracted clinical symptoms below before submitting the prediction.")
            
            # Initialize verified list if not already present
            if "verified_hpo_ids" not in st.session_state or run_ocr:
                st.session_state["verified_hpo_ids"] = list(mapped.keys())
                
            # Render Checkboxes for Detected Symptoms
            if not mapped:
                st.info("No matching HPO symptoms were automatically detected in the text. Please add symptoms manually below.")
            else:
                updated_selections = []
                for hpo_id, details in mapped.items():
                    name = details["name"]
                    phrase = details["matched_phrase"]
                    matched_synonym = details["matched_synonym"]
                    confidence = details["confidence"]
                    # Checkbox for each term
                    is_checked = hpo_id in st.session_state["verified_hpo_ids"]
                    val = st.checkbox(
                        label=f"**{name}** ({hpo_id}) — Matched via *'{phrase}'* (Synonym: *'{matched_synonym}'*) — Confidence: **{confidence}%**",
                        value=is_checked,
                        key=f"chk_{hpo_id}"
                    )
                    if val:
                        updated_selections.append(hpo_id)
                st.session_state["verified_hpo_ids"] = updated_selections

            # Manual search and add additional symptoms
            st.markdown("#### Add Missing Symptoms Manually")
            # Determine default selections for multiselect
            # These are the ones verified from checkboxes + manually added ones
            if "manual_hpo_selections" not in st.session_state or run_ocr:
                st.session_state["manual_hpo_selections"] = []
                
            # Show a multiselect search for HPO terms
            all_current_choices = []
            for hpo_id in st.session_state["verified_hpo_ids"]:
                all_current_choices.append(hpo_id_to_choice.get(hpo_id))
            for choice in st.session_state["manual_hpo_selections"]:
                if choice not in all_current_choices:
                    all_current_choices.append(choice)
                    
            # Ensure no None elements
            all_current_choices = [c for c in all_current_choices if c]
            
            options_pool = sorted(list(set(hpo_choices) | set(all_current_choices)))
            
            doctor_selections = st.multiselect(
                "Search and select HPO symptoms manually:",
                options=options_pool,
                default=all_current_choices,
                help="Type to search and add any observed patient symptoms that were missed by OCR.",
                key="manual_hpo_multiselect"
            )
            
            # Update verified_hpo_ids based on final multiselect input
            final_hpo_ids = []
            for choice in doctor_selections:
                hpo_id = choice.split("(")[-1].replace(")", "").strip()
                final_hpo_ids.append(hpo_id)
            st.session_state["verified_hpo_ids"] = final_hpo_ids
            st.session_state["manual_hpo_selections"] = doctor_selections
            
            # --- Quality Check & Metrics ---
            st.markdown("---")
            st.markdown("### 🔍 Quality Check")
            num_matched = len(final_hpo_ids)
            coverage_pct = (num_matched / len(hpo_vocab)) * 100 if hpo_vocab else 0
            
            col_qc1, col_qc2 = st.columns(2)
            with col_qc1:
                st.metric("OCR Confidence Score", f"{avg_conf * 100:.1f}%")
                st.metric("Matched Symptoms", f"{num_matched}")
                st.metric("Ontology Coverage", f"{coverage_pct:.2f}%")
            with col_qc2:
                st.metric("Feature Vector Size", f"{len(rf_model.feature_names)}")
                
            unmatched_lines = st.session_state.get("unmatched_lines", [])
            if unmatched_lines:
                with st.expander("⚠️ Unmatched Clinical Terms", expanded=False):
                    for ul in unmatched_lines:
                        st.markdown(f"- {ul}")
            
            # --- Temporary Debug Panel ---
            with st.expander("🛠️ OCR Pipeline Debug Panel (Active Validation)", expanded=True):
                st.write(f"**Uploaded Filename**: `{uploaded_file.name}`")
                st.write(f"**OCR Raw Text Preview**: `{raw_text[:300]}...`" if len(raw_text) > 300 else f"**OCR Raw Text**: `{raw_text}`")
                
                # Extracted clinical entities
                extracted_entities = st.session_state.get("extracted_clinical_entities", [])
                st.write(f"**Extracted Clinical Entities**: `{extracted_entities}`")
                
                # Ignored administrative text
                ignored_admin_list = st.session_state.get("ignored_administrative", [])
                st.write(f"**Ignored Administrative Text**: `{ignored_admin_list}`")
                
                # Ignored demographic text
                ignored_demo_list = st.session_state.get("ignored_demographics", [])
                st.write(f"**Ignored Demographic Text**: `{ignored_demo_list}`")
                
                # Accepted HPO IDs
                st.write(f"**Final HPO IDs**: `{final_hpo_ids}`")
                
                # Rejected demographic matches
                rejected_demo = [r["phrase"] for r in st.session_state.get("rejected_non_clinical", []) if "demographic" in r["reason"].lower() or "metadata" in r["reason"].lower()]
                st.write(f"**Rejected Demographic Matches**: `{rejected_demo}`")
                
                # Active feature indices in the 325-feature vector (rf_model.feature_names)
                active_indices = []
                active_features = []
                for idx, col in enumerate(rf_model.feature_names):
                    if col in final_hpo_ids:
                        active_indices.append(idx)
                        active_features.append(col)
                    elif col == "sex_MALE" and patient_sex == "MALE":
                        active_indices.append(idx)
                        active_features.append(col)
                    elif col == "sex_FEMALE" and patient_sex == "FEMALE":
                        active_indices.append(idx)
                        active_features.append(col)
                    elif col == "sex_UNKNOWN_SEX" and patient_sex == "UNKNOWN_SEX":
                        active_indices.append(idx)
                        active_features.append(col)
                        
                st.write(f"**Active Feature Indices**: `{active_indices}`")
                st.write(f"**Final Feature Vector (Active Features)**: `{active_features}`")
                
                # Feature vector checksum/hash to verify uniqueness
                import hashlib
                vector_str = f"{sorted(final_hpo_ids)}_{patient_sex}"
                vector_hash = hashlib.sha256(vector_str.encode('utf-8')).hexdigest()[:12]
                st.write(f"**Feature Vector Hash**: `{vector_hash}`")
            
            # --- Trigger Prediction ---
            st.write("")
            if st.button("Predict Disease from Record"):
                if not final_hpo_ids:
                    st.warning("Please select or verify at least one symptom to run predictions.")
                else:
                    with st.spinner("Executing model inferences and computing probability distributions..."):
                        # Create input vector matching CONFIG_B (HPO + Sex)
                        patient_vector = {hpo_id: 0 for hpo_id in hpo_vocab}
                        for hpo_id in final_hpo_ids:
                            if hpo_id in patient_vector:
                                patient_vector[hpo_id] = 1
                                
                        patient_vector["sex_MALE"] = 1 if patient_sex == "MALE" else 0
                        patient_vector["sex_FEMALE"] = 1 if patient_sex == "FEMALE" else 0
                        patient_vector["sex_UNKNOWN_SEX"] = 1 if patient_sex == "UNKNOWN_SEX" else 0
                        
                        patient_df = pd.DataFrame([patient_vector])
                        patient_df = patient_df.reindex(columns=rf_model.feature_names, fill_value=0)
                        
                        # 1. Random Forest Predictions
                        rf_probs = rf_model.predict_proba(patient_df)[0]
                        
                        # 2. TabNet Predictions
                        tabnet_probs = tabnet_model.predict_proba(patient_df)[0]
                        
                        # Cache the current state for explanation pages
                        st.session_state["patient_df"] = patient_df
                        st.session_state["selected_hpo_names"] = [hpo_map.get(h, "Unknown phenotypic feature") for h in final_hpo_ids]
                        st.session_state["rf_probs"] = rf_probs
                        st.session_state["tabnet_probs"] = tabnet_probs
                        st.session_state["prediction_made"] = True
                        
                        # Use RF as the primary model
                        top_class = int(np.argmax(rf_probs))
                        top_prob = float(rf_probs[top_class])
                        disease_name = system_config.DISEASE_NAMES[top_class]
                        disease_omim = system_config.DISEASE_OMIMS[top_class]
                        
                        st.session_state["disease_name"] = disease_name
                        st.session_state["disease_omim"] = disease_omim
                        st.session_state["top_prob"] = top_prob
                        st.session_state["top_class"] = top_class
                        st.session_state["selected_hpo_ids"] = final_hpo_ids
                        st.session_state["patient_sex"] = patient_sex
                        st.session_state["confidence_threshold"] = confidence_threshold
                        
                        tab_top_class = int(np.argmax(tabnet_probs))
                        tab_top_prob = float(tabnet_probs[tab_top_class])
                        st.session_state["tab_top_class"] = tab_top_class
                        st.session_state["tab_top_prob"] = tab_top_prob
                        
                        st.toast("Predictive modeling inference complete!", icon="✅")
                        
                    if top_prob < confidence_threshold:
                        st.error("No confident prediction found.")
                        st.warning(f"The highest prediction probability is {top_prob*100:.1f}%, which is below the required threshold of {confidence_threshold*100:.1f}%.")
                    else:
                        st.switch_page("pages/6_Prediction_Analytics_Dashboard.py")
