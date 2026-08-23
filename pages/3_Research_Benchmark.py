import streamlit as st
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from config import system_config

# Custom helper to load and inject CSS
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(system_config.WORKSPACE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    load_css(css_path)

def metric_grid_card(label: str, value: str, trend: str = None, trend_type: str = "success"):
    trend_html = ""
    if trend:
        color = "#22C55E" if trend_type == "success" else "#EF4444"
        trend_html = f'<span style="font-size: 0.8rem; color: {color}; font-weight: 600; margin-left: 8px;">{trend}</span>'
    card_html = f'<div class="medical-card" style="text-align: center; padding: 18px 12px; margin-bottom: 10px;"><div class="metric-label">{label}</div><div style="display: flex; align-items: baseline; justify-content: center;"><span class="metric-value">{value}</span>{trend_html}</div></div>'
    st.markdown(card_html, unsafe_allow_html=True)

# Page header
st.markdown('<div class="badge badge-info" style="font-size: 0.85rem; margin-bottom: 12px;">Scientific Validation Dashboard</div>', unsafe_allow_html=True)
st.title("🔬 Research Benchmark & Comparative Analysis")
st.markdown(
    """
    This page presents the scientific evaluation of our proposed Random Forest model 
    on the verified real-world patient cohort and provides a structured comparison against the base reference paper.
    """
)

st.warning("⚠️ **Evaluation Note:** Model evaluation is based on a small real-patient cohort. Results require validation on larger independent cohorts.")

# ========================================================
# SECTION 1: Project Performance
# ========================================================
st.markdown("### 1. Proposed Project Performance")
st.markdown("#### Random Forest (Final Model)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    metric_grid_card("Accuracy", "100.00%", trend=None)
with col2:
    metric_grid_card("Precision (Macro)", "100.00%", trend=None)
with col3:
    metric_grid_card("Recall (Macro)", "100.00%", trend=None)
with col4:
    metric_grid_card("Macro F1 Score", "100.00%", trend=None)
with col5:
    metric_grid_card("5-Fold Cross Val.", "100.00%", trend="± 0.0%", trend_type="success")

# ========================================================
# SECTION 2: Base Paper Evaluation Metrics
# ========================================================
st.write("")
st.markdown("### 2. Base Paper Evaluation")
st.markdown(
    """
    <div class="medical-card" style="border-left: 5px solid #0F4C81;">
        <div style="font-size: 0.85rem; color: #64748B; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">Reference Literature</div>
        <h4 style="margin: 0 0 8px 0; color: #0F4C81; font-family: 'Outfit', sans-serif;">
            Performance and Clinical Utility of a New Supervised Machine Learning Pipeline in Detecting Rare Ciliopathy Patients Based on Deep Phenotyping from Electronic Health Records and Semantic Similarity
        </h4>
        <div style="font-size: 0.9rem; color: #334155; margin-bottom: 12px;">
            <strong>Journal:</strong> Orphanet Journal of Rare Diseases (2024)
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

col_bp1, col_bp2, col_bp3 = st.columns(3)
with col_bp1:
    metric_grid_card("Sensitivity (Recall)", "86.00%")
with col_bp2:
    metric_grid_card("Specificity", "90.00%")
with col_bp3:
    metric_grid_card("AUROC / AUPRC", "96.00% / 43.00%")

# ========================================================
# SECTION 3: Side-by-Side Comparative Metrics
# ========================================================
st.write("")
st.markdown("### 3. Methodology & Performance Contrast")

tab1, tab2 = st.tabs(["📊 Metric Analysis", "📋 Comparison Table"])

with tab1:
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        # Radar Chart for Performance Contrast
        categories = ['Sensitivity', 'Specificity', 'AUROC', 'AUPRC']
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[86.0, 90.0, 96.0, 43.0],
            theta=categories,
            fill='toself',
            name='Base Paper (Real EHR)',
            line_color='#64748B'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[100.0, 100.0, 100.0, 100.0],
            theta=categories,
            fill='toself',
            name='Proposed (Real Patients)',
            line_color='#0F4C81'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
            ),
            title={
                'text': "Multi-Dimensional Metric Signature",
                'font': {'family': 'Outfit', 'size': 16, 'color': '#0F4C81'}
            },
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=40, r=40, t=50, b=50),
            height=380
        )
        st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    table_style = """
    <style>
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 0.95rem;
            font-family: 'Inter', sans-serif;
            min-width: 400px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border-radius: 8px;
            overflow: hidden;
        }
        .custom-table thead tr {
            background-color: #0F4C81;
            color: #ffffff;
            text-align: left;
            font-weight: bold;
        }
        .custom-table th, .custom-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #E2E8F0;
        }
        .custom-table tbody tr {
            background-color: #ffffff;
        }
        .custom-table tbody tr:nth-of-type(even) {
            background-color: #F8FAFC;
        }
        .custom-table tbody tr:last-of-type {
            border-bottom: 2px solid #0F4C81;
        }
        .highlight-val {
            font-weight: 600;
            color: #0F4C81;
        }
        .not-eval {
            color: #94A3B8;
            font-style: italic;
        }
    </style>
    """
    st.markdown(table_style, unsafe_allow_html=True)
    
    html_table = """
    <table class="custom-table">
        <thead>
            <tr>
                <th>Metric</th>
                <th>Base Paper</th>
                <th>Proposed System (Real Data)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Dataset</strong></td>
                <td>Real EHR (N=7,261)</td>
                <td class="highlight-val">Real Patient Cohort (N=67)</td>
            </tr>
            <tr>
                <td><strong>Test Patients</strong></td>
                <td>30 Cases / 7,231 Controls</td>
                <td class="highlight-val">14 Held-out Cases</td>
            </tr>
            <tr>
                <td><strong>Accuracy</strong></td>
                <td class="not-eval">Not Reported</td>
                <td class="highlight-val">100.00%</td>
            </tr>
            <tr>
                <td><strong>Sensitivity / Recall</strong></td>
                <td>86.00%</td>
                <td class="highlight-val">100.00%</td>
            </tr>
            <tr>
                <td><strong>Specificity</strong></td>
                <td>90.00%</td>
                <td class="highlight-val">100.00%</td>
            </tr>
            <tr>
                <td><strong>Precision</strong></td>
                <td class="not-eval">Not Reported</td>
                <td class="highlight-val">100.00%</td>
            </tr>
            <tr>
                <td><strong>Macro F1</strong></td>
                <td class="not-eval">Not Reported</td>
                <td class="highlight-val">100.00%</td>
            </tr>
            <tr>
                <td><strong>AUROC</strong></td>
                <td>96.00%</td>
                <td class="highlight-val">1.0000</td>
            </tr>
            <tr>
                <td><strong>AUPRC</strong></td>
                <td>43.00%</td>
                <td class="highlight-val">1.0000</td>
            </tr>
            <tr>
                <td><strong>Cross Validation</strong></td>
                <td>5-Fold CV used for tuning</td>
                <td class="highlight-val">100.00% ± 0.0%</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

# ========================================================
# SECTION 4: Research Conclusion Box
# ========================================================
st.write("")
st.markdown("### 4. Scientific Conclusion & Caveats")
st.markdown(
    """
    <div class="medical-card" style="background-color: #F8FAFC; border: 1px solid #CBD5E1;">
        <p style="font-size: 0.95rem; line-height: 1.7; color: #334155; margin: 0;">
            Our proposed Random Forest model achieved a test accuracy of <strong>100.00%</strong> on the real patient held-out test cohort. 
            The reference paper used a different evaluation protocol based on highly imbalanced real-world EHR data, 
            reporting sensitivity (86%), specificity (90%), AUROC (96%), and AUPRC (43%).
        </p>
        <p style="font-size: 0.95rem; line-height: 1.7; color: #334155; margin: 12px 0 0 0;">
            <em>Note:</em> Since the datasets, disease cohorts, and evaluation methodologies differ, these metrics should not be interpreted as a direct superiority comparison. Because of the small cohort size and disease-specific phenotype structure, these results must be interpreted cautiously and require validation on larger independent patient cohorts.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.markdown("<hr style='border: 0; height: 1px; background: #E2E8F0;' />", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #94A3B8;'>Rare Disease Prediction System - Scientific Comparative Framework.</p>", unsafe_allow_html=True)
