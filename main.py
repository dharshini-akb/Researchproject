import streamlit as st
import os
from config import system_config
from components import cards

# Set up page configurations
st.set_page_config(
    page_title="Rare Disease Prediction System",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom helper to load and inject CSS
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Path to styles
css_path = os.path.join(system_config.WORKSPACE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    load_css(css_path)

# --- Sidebar Configuration ---
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <span style="font-size: 3rem;">🧬</span>
        <h2 style="margin: 5px 0 0 0; font-size: 1.4rem; color: #0F4C81;">RarePredict AI</h2>
        <span style="font-size: 0.8rem; color: #64748B; font-weight: 500;">Clinician Decision Dashboard</span>
    </div>
    <hr style="border: 0; height: 1px; background: #E2E8F0; margin-bottom: 20px;" />
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("### Navigation")
st.sidebar.info("Select a workspace page above to explore the prediction system.")

# Version and developer credits
st.sidebar.markdown(
    """
    <div style="position: fixed; bottom: 20px; font-size: 0.8rem; color: #64748B; line-height: 1.4;">
        <strong>System Version:</strong> v1.0.0<br/>
        <strong>OS Compatibility:</strong> Windows Server / Local<br/>
        <strong>Developer:</strong> Senior AI Architect Team<br/>
        <span style="font-size: 0.75rem; color: #94A3B8;">Research-Grade Software</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Main Landing Page Content ---
col1, col2 = st.columns([1.2, 0.8], gap="large")

with col1:
    st.markdown(
        """
        <span class="badge badge-info" style="font-size: 0.85rem; margin-bottom: 12px;">Research Publication Grade System</span>
        """,
        unsafe_allow_html=True
    )
    st.title("Rare Disease Prediction System using Human Phenotype Ontology (HPO)")
    
    st.markdown(
        """
        ### Project Overview
        This advanced clinical decision-support system leverages machine learning and deep learning architectures to predict selected rare diseases from patient phenotypic profiles. By utilizing the official **Human Phenotype Ontology (HPO)** vocabulary alongside **Orphanet** annotations, the system analyzes complex, sparse symptom arrays to assist clinical researchers and geneticists.
        
        ### Scientific Objectives
        - **Accurate Cohort Mapping**: Multi-hot encode hundreds of sparse phenotypic terms to classify patients into target cohorts.
        - **Architectural Benchmark**: Compare the performance of classical algorithms (**Random Forest**) with tabular deep learning models (**TabNet**).
        - **Explainable Diagnostics**: Utilize **SHAP (SHapley Additive exPlanations)** values and deep attention masks to trace predictions back to discrete clinical manifestations, providing full transparency.
        
        ### Target Cohorts
        Currently trained to differentiate and recognize three complex rare genetic syndromes:
        1. **White-Sutton syndrome** (`OMIM:616364`)
        2. **Xia-Gibbs syndrome** (`OMIM:615829`)
        3. **KBG syndrome** (`OMIM:148050`)
        """
    )
    
    st.write("")
    if st.button("Begin Diagnostic Prediction"):
        st.write("👈 Please select **Disease Prediction** or **Patient Record Image Prediction** in the sidebar menu to get started!")

with col2:
    st.write("")
    st.write("")
    st.write("")
    
    # Load and display the generated medical illustration
    illustration_path = os.path.join(system_config.WORKSPACE_DIR, "assets", "medical_illustration.png")
    if os.path.exists(illustration_path):
        st.image(illustration_path, use_container_width=True, caption="🧬 DNA Phenotypic Feature Representation")
    else:
        st.info("🧬 RarePredict Genotyping System")
        
    st.markdown(
        """
        <div class="medical-card" style="margin-top: 20px;">
            <h4 style="margin-top: 0; color: #0F4C81;">Key Features</h4>
            <ul style="padding-left: 20px; font-size: 0.9rem; line-height: 1.6; color: #334155; margin-bottom: 0;">
                <li>Interactive HPO Symptom Auto-search & Selection</li>
                <li>Dynamic Probability Confidence Meters</li>
                <li>Real-Time SHAP Waterfall & Feature Plots</li>
                <li>Side-by-Side Model Performance Profiling</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
st.write("")
st.write("")
st.markdown("<hr style='border: 0; height: 1px; background: #E2E8F0;' />", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #94A3B8;'>Rare Disease Prediction System - Developed for Clinical and Scientific Research Purposes Only.</p>", unsafe_allow_html=True)
