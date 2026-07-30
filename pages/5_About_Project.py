import streamlit as st
import os
from config import system_config

# Custom helper to load and inject CSS
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(system_config.WORKSPACE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    load_css(css_path)

st.title("📘 About the Project & Research Methodology")

st.markdown(
    """
    ### 1. Research Motivation
    Rare diseases affect approximately 300 million people worldwide. Due to their low individual prevalence, diagnosing a rare disease can take several years—a challenge commonly referred to as the **diagnostic odyssey**. 
    
    By representing clinical presentations using standardized ontologies (such as the **Human Phenotype Ontology**), artificial intelligence can scan thousands of candidate genetic profiles and phenotypes simultaneously. This research aims to prove how structured feature representations coupled with explainable ML/DL can accurately map phenotypes to rare disease categories.
    
    ---
    
    ### 2. Methodology & Algorithm Framework
    
    #### Random Forest (Machine Learning)
    - **Classification Model**: An ensemble of decision trees trained with bagging.
    - **Characteristics**: Extremely robust against overfitting in high-dimensional sparse tabular data regimes. Handles multi-hot features naturally.
    - **Calibration**: Calibrated via Platt scaling (sigmoid mapping) using 5-fold cross-validation, aligning model confidence directly with empirical class distributions.
    
    #### TabNet (Deep Learning)
    - **Classification Model**: A deep neural network utilizing sequential attention steps to choose salient tabular features.
    - **Characteristics**: Combines the parameter efficiency and interpretability of decision trees with the end-to-end optimization of deep architectures.
    - **Sparsity**: Governed by an entropy penalty encouraging sparse feature selection masks at each decision node.
    
    #### SHAP (Explainable AI)
    - **Mechanism**: Based on cooperative game theory (Shapley values). Computes the marginal contribution of each symptom to the final diagnostic probability.
    - **Clinical Value**: Demystifies black-box classifiers, enabling geneticists to verify which specific phenotypes drove the model's prediction.
    
    ---
    
    ### 3. Technology Stack
    - **Language**: Python 3.11+
    - **Deep Learning**: PyTorch 2.0+
    - **Machine Learning**: Scikit-Learn 1.3+
    - **Explainability**: SHAP 0.44+
    - **Interactive Frontend**: Streamlit 1.30+
    - **Visualizations**: Plotly 5.18+
    
    ---
    
    ### 4. Future System Integrations
    The system is designed with modular microservices in mind to support:
    - **Electronic Health Record (EHR) Integration**: Automated parsing of clinical notes via NLP to map free-text clinical symptoms directly to HPO terms.
    - **FHIR API Integration**: Ingestion of patient profiles through standard HL7 FHIR structures.
    - **Syndromic Scaling**: Expanding class training to support thousands of OMIM diseases.
    """
)
