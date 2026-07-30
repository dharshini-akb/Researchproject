import streamlit as st
import os
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from config import system_config
from explainability.shap_explainer import RareDiseaseExplainer
from models.random_forest import RandomForestModel
from models.tabnet import TabNetModel
from preprocessing import data_loader

# Custom helper to load and inject CSS
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(system_config.WORKSPACE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    load_css(css_path)

st.title("🔍 Model Explainability & Interpretability")
st.markdown("Inspect global feature representations and trace individual patient predictions back to underlying phenotypic features using SHAP and neural attention.")

# --- Load Models & Initialize Explainer ---
def get_file_mtime(filepath):
    return os.path.getmtime(filepath) if os.path.exists(filepath) else 0

@st.cache_resource
def load_models_and_explainer(rf_mtime, tabnet_mtime, xtrain_mtime):
    base_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex")
    X_train = pd.read_csv(os.path.join(base_dir, "X_train.csv"))
    
    rf_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
    rf = RandomForestModel()
    rf.load(rf_path)
    
    tabnet_path = os.path.join(system_config.ARTIFACTS_DIR, "tabnet_model.pt")
    tabnet = TabNetModel()
    tabnet.load(tabnet_path)
    
    explainer = RareDiseaseExplainer()
    # Fit background on training dataset
    explainer.initialize_rf_explainer(rf, X_train)
    
    return rf, tabnet, explainer, X_train

rf_file_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
tabnet_file_path = os.path.join(system_config.ARTIFACTS_DIR, "tabnet_model.pt")
xtrain_file_path = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex", "X_train.csv")

rf_model, tabnet_model, explainer, X_train = load_models_and_explainer(
    get_file_mtime(rf_file_path),
    get_file_mtime(tabnet_file_path),
    get_file_mtime(xtrain_file_path)
)
hpo_map = data_loader.parse_hpo_obo()

# Tab navigation
tab1, tab2 = st.tabs(["Local Prediction Explanation", "Global Feature Importance"])

with tab1:
    st.subheader("Individual Patient Diagnostics Breakdown")
    
    # Check if a prediction has been cached in the session state
    if "prediction_made" not in st.session_state or not st.session_state["prediction_made"]:
        st.info("💡 No active patient prediction session found. Please run a prediction on the **Disease Prediction** page first.")
        
        # Load sample patient for demonstration
        st.markdown("#### Preview with Sample Test Case")
        base_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex")
        X_test = pd.read_csv(os.path.join(base_dir, "X_test.csv"))
        y_test = pd.read_csv(os.path.join(base_dir, "y_test.csv"))["target"]
        
        sample_idx = st.selectbox("Select sample test patient to inspect:", range(len(X_test)))
        demo_patient_df = X_test.iloc[[sample_idx]]
        demo_rf_probs = rf_model.predict_proba(demo_patient_df)[0]
        demo_tabnet_probs = tabnet_model.predict_proba(demo_patient_df)[0]
        
        patient_df = demo_patient_df
        rf_probs = demo_rf_probs
        tabnet_probs = demo_tabnet_probs
        st.markdown(f"**Sample Actual Target Class**: {system_config.DISEASE_NAMES[int(y_test.iloc[sample_idx])]} ({system_config.DISEASE_OMIMS[int(y_test.iloc[sample_idx])]})")
    else:
        patient_df = st.session_state["patient_df"]
        rf_probs = st.session_state["rf_probs"]
        tabnet_probs = st.session_state["tabnet_probs"]
        st.success("Loaded active clinical patient prediction from diagnostic panel.")
        
    # Class selector for SHAP values
    pred_class = int(np.argmax(rf_probs))
    selected_class = st.selectbox(
        "Explain decision logic for syndrome:",
        options=[0, 1, 2],
        format_func=lambda x: f"{system_config.DISEASE_NAMES[x]} ({system_config.DISEASE_OMIMS[x]})",
        index=pred_class
    )
    
    # 1. Random Forest SHAP Explanations
    st.markdown("#### Random Forest Local SHAP Contribution (Waterfall Representation)")
    with st.spinner("Calculating SHAP values..."):
        rf_explanations = explainer.explain_patient_rf(patient_df)
        class_shap = rf_explanations[selected_class]
        
    # Map feature names to human descriptions
    shap_rows = []
    for col, val in class_shap.items():
        if col.startswith("sex_"):
            desc = col.replace("sex_", "Biological sex: ")
        else:
            desc = f"{hpo_map.get(col, 'Unknown feature')} ({col})"
        
        is_active = patient_df[col].values[0] == 1
        shap_rows.append({
            "feature": desc,
            "shap_value": val,
            "active": "Active (Present)" if is_active else "Inactive (Absent)"
        })
        
    df_shap = pd.DataFrame(shap_rows)
    # Filter non-zero or top contributors
    df_shap["abs_val"] = df_shap["shap_value"].abs()
    top_shap = df_shap.sort_values(by="abs_val", ascending=False).head(15)
    
    # Plot Local SHAP Contributions
    colors = ['#22C55E' if v >= 0 else '#EF4444' for v in top_shap["shap_value"]]
    
    fig = go.Figure(go.Bar(
        x=top_shap["shap_value"],
        y=top_shap["feature"],
        orientation='h',
        marker_color=colors,
        text=[f"{v:+.4f}" for v in top_shap["shap_value"]],
        textposition='outside',
        hoverinfo="y+x"
    ))
    
    fig.update_layout(
        title={
            'text': f"Symptom Impact on: {system_config.DISEASE_NAMES[selected_class]}",
            'font': {'family': 'Outfit', 'size': 16, 'color': '#0F4C81'}
        },
        xaxis_title="SHAP Value (Positive drives classification, Negative opposes)",
        yaxis=dict(autorange="reversed", gridcolor='#F1F5F9'),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=250, r=40, t=50, b=50),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. TabNet Attention Explanation
    st.markdown("#### TabNet Native Neural Attention Weights")
    with st.spinner("Extracting attention masks..."):
        tab_explanation = explainer.explain_patient_tabnet(tabnet_model, patient_df)
        
    tab_rows = []
    for col, val in tab_explanation.items():
        if col.startswith("sex_"):
            desc = col.replace("sex_", "Biological sex: ")
        else:
            desc = f"{hpo_map.get(col, 'Unknown feature')} ({col})"
        is_active = patient_df[col].values[0] == 1
        tab_rows.append({
            "feature": desc,
            "attention_weight": val,
            "active": "Active (Present)" if is_active else "Inactive (Absent)"
        })
        
    df_tab = pd.DataFrame(tab_rows)
    top_tab = df_tab.sort_values(by="attention_weight", ascending=False).head(10)
    
    # Plot TabNet Attention Weights
    fig_tab = go.Figure(go.Bar(
        x=top_tab["attention_weight"],
        y=top_tab["feature"],
        orientation='h',
        marker_color='#2A9D8F',
        text=[f"{v:.4f}" for v in top_tab["attention_weight"]],
        textposition='outside',
        hoverinfo="y+x"
    ))
    
    fig_tab.update_layout(
        title={
            'text': "Neural Gate Attention Coefficient (Top Features)",
            'font': {'family': 'Outfit', 'size': 16, 'color': '#0F4C81'}
        },
        xaxis_title="Selection Weight (Importance in neural network path)",
        yaxis=dict(autorange="reversed", gridcolor='#F1F5F9'),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=250, r=40, t=50, b=50),
        height=380
    )
    st.plotly_chart(fig_tab, use_container_width=True)

with tab2:
    st.subheader("Global Cohort Feature Importance")
    st.markdown("Analyze which symptoms are globally significant across the entire training dataset splits.")
    
    col_g1, col_g2 = st.columns([1, 1], gap="medium")
    
    with col_g1:
        st.markdown("#### Random Forest Global SHAP Importance")
        with st.spinner("Compiling global SHAP importance..."):
            # Sample background to speed up global calculation
            bg_sample = X_train.sample(n=min(len(X_train), 100), random_state=42)
            global_shaps = explainer.get_global_importance_rf(bg_sample)
            
        g_selected_class = st.selectbox(
            "Select syndrome for global SHAP:",
            options=[0, 1, 2],
            format_func=lambda x: f"{system_config.DISEASE_NAMES[x]} ({system_config.DISEASE_OMIMS[x]})"
        )
        
        rf_g_importance = global_shaps[g_selected_class]
        rf_g_rows = []
        for col, val in rf_g_importance.items():
            if col.startswith("sex_"):
                desc = col.replace("sex_", "Sex: ")
            else:
                desc = f"{hpo_map.get(col, col)} ({col})"
            rf_g_rows.append({"feature": desc, "mean_abs_shap": val})
            
        df_rf_g = pd.DataFrame(rf_g_rows).sort_values(by="mean_abs_shap", ascending=False).head(15)
        
        # Plot
        fig_rf_g = go.Figure(go.Bar(
            x=df_rf_g["mean_abs_shap"],
            y=df_rf_g["feature"],
            orientation='h',
            marker_color='#0F4C81',
            hoverinfo="y+x"
        ))
        fig_rf_g.update_layout(
            title={"text": "Mean Absolute SHAP Value", "font": {"family": "Outfit", "size": 15}},
            yaxis=dict(autorange="reversed", gridcolor='#F1F5F9'),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=220, r=20, t=40, b=40),
            height=400
        )
        st.plotly_chart(fig_rf_g, use_container_width=True)
        
    with col_g2:
        st.markdown("#### TabNet Global Attention Importance")
        with st.spinner("Extracting global neural attention..."):
            tabnet_g_importance = tabnet_model.get_feature_importance_from_masks(X_train)
            
        tab_g_rows = []
        features = list(X_train.columns)
        for i in range(len(features)):
            col = features[i]
            if col.startswith("sex_"):
                desc = col.replace("sex_", "Sex: ")
            else:
                desc = f"{hpo_map.get(col, col)} ({col})"
            tab_g_rows.append({"feature": desc, "importance": tabnet_g_importance[i]})
            
        df_tab_g = pd.DataFrame(tab_g_rows).sort_values(by="importance", ascending=False).head(15)
        
        # Plot
        fig_tab_g = go.Figure(go.Bar(
            x=df_tab_g["importance"],
            y=df_tab_g["feature"],
            orientation='h',
            marker_color='#2A9D8F',
            hoverinfo="y+x"
        ))
        fig_tab_g.update_layout(
            title={"text": "Normalized Attention Weight", "font": {"family": "Outfit", "size": 15}},
            yaxis=dict(autorange="reversed", gridcolor='#F1F5F9'),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=220, r=20, t=40, b=40),
            height=400
        )
        st.plotly_chart(fig_tab_g, use_container_width=True)
