import streamlit as st
import os
import json
import pandas as pd
from config import system_config
from components import cards

# Custom helper to load and inject CSS
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(system_config.WORKSPACE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    load_css(css_path)

st.title("🗂️ Cohort Dataset & Preprocessing Pipeline")
st.markdown("Details regarding HPO phenotypic vocabulary scale, split manifest distributions, and visual pipeline topology.")

# --- Load Preprocessing Config Metadata ---
preproc_path = os.path.join(system_config.PREPROC_ARTIFACTS_DIR, "preprocessing_configuration.json")
if not os.path.exists(preproc_path):
    st.warning("Preprocessing metadata not found. Please run preprocessing pipeline first.")
    st.stop()
    
with open(preproc_path, "r") as f:
    config_metadata = json.load(f)

vocab_size = config_metadata["hpo_vocabulary_size"]
shapes = config_metadata["shapes"]

# Metrics cards
st.markdown("### 1. Cohort and Feature Dictionary Size")
col1, col2, col3 = st.columns(3)
with col1:
    cards.metric_grid_card("Target Rare Diseases", "3", "OMIM cohort scope")
with col2:
    cards.metric_grid_card("HPO Vocabulary Size", f"{vocab_size}", "Unique HPO terms fit")
with col3:
    cards.metric_grid_card("Total Features (HPO+Sex)", f"{vocab_size + 3}", "CONFIG_B Dimensions")

# Train/Val/Test split distribution
st.markdown("### 2. Dataset Split Allocations")
split_data = {
    "Split": ["Training Set", "Validation Set", "Test Set"],
    "Sample Count": [
        shapes["targets"]["y_train"],
        shapes["targets"]["y_val"],
        shapes["targets"]["y_test"]
    ],
    "Percentage": [
        f"{shapes['targets']['y_train'] / 2.47:.1f}%",
        f"{shapes['targets']['y_val'] / 2.47:.1f}%",
        f"{shapes['targets']['y_test'] / 2.47:.1f}%"
    ],
    "Input Dimension": [
        shapes["CONFIG_B"]["X_train"][1],
        shapes["CONFIG_B"]["X_val"][1],
        shapes["CONFIG_B"]["X_test"][1]
    ]
}
df_split = pd.DataFrame(split_data)
st.dataframe(df_split, hide_index=True, use_container_width=True)

# Unseen HPOs stats
st.markdown("### 3. Out-of-Vocabulary Symptom Analysis")
st.markdown(
    """
    To prevent data leakage, the symptom vocabulary is fit strictly on the **Training set**. 
    Symptoms that appear only in the validation/test splits are classified as **Unseen Phenotypes** and are automatically zero-masked at evaluation.
    """
)
unseen_stats = config_metadata["unseen_hpo_terms"]
col_u1, col_u2 = st.columns(2)
with col_u1:
    cards.metric_grid_card("Unseen Symptoms (Validation)", f"{unseen_stats['validation_count']}", "OOD terms masked")
with col_u2:
    cards.metric_grid_card("Unseen Symptoms (Test)", f"{unseen_stats['test_count']}", "OOD terms masked")

# Mermaid Pipeline Visualization
st.markdown("### 4. Data Processing & Feature Pipeline Topology")
st.markdown(
    """
    The diagram below shows the raw to model-ready ingestion pipeline workflow:
    """
)
mermaid_diagram = """
mermaid
flowchart TD
    A[Raw Patient Records CSV] --> B[Standardize Sex Column MALE/FEMALE/UNKNOWN_SEX]
    A --> C[Split HPO ID & Symptom lists]
    C --> D[De-duplicate & Sort HPO arrays]
    B & D --> E[Join into Cleaned Cohort DataFrame]
    E --> F[Partition Splits using train/val/test Case IDs]
    F --> G[Extract unique HPO terms from Training split ONLY]
    G --> H[Fit Model HPO Feature Vocabulary size=206]
    H & F --> I[Binary Multi-hot encode symptoms for Splits]
    H & F --> J[One-hot encode patient Biological Sex]
    I & J --> K[Concatenate: CONFIG_B Dimensions = 209]
    K --> L[Save X_train, y_train, X_validation, etc.]
"""
st.markdown(f"```{mermaid_diagram}```")
