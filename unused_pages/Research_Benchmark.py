import streamlit as st
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from config import system_config
def metric_grid_card(label: str, value: str, trend: str = None, trend_type: str = "success"):
    trend_html = ""
    if trend:
        color = "#22C55E" if trend_type == "success" else "#EF4444"
        trend_html = f'<span style="font-size: 0.8rem; color: {color}; font-weight: 600; margin-left: 8px;">{trend}</span>'
    card_html = f'<div class="medical-card" style="text-align: center; padding: 18px 12px; margin-bottom: 10px;"><div class="metric-label">{label}</div><div style="display: flex; align-items: baseline; justify-content: center;"><span class="metric-value">{value}</span>{trend_html}</div></div>'
    st.markdown(card_html, unsafe_allow_html=True)

# Custom helper to load and inject CSS
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(system_config.WORKSPACE_DIR, "assets", "styles.css")
if os.path.exists(css_path):
    load_css(css_path)

# Page header
st.markdown('<div class="badge badge-info" style="font-size: 0.85rem; margin-bottom: 12px;">Scientific Validation Dashboard</div>', unsafe_allow_html=True)
st.title("🔬 Research Benchmark & Comparative Analysis")
st.markdown(
    """
    This page presents the scientific evaluation of our proposed Random Forest model 
    and provides a structured comparison against the methodology and metrics reported in the base reference paper.
    """
)

# ========================================================
# SECTION 1: Project Performance
# ========================================================
st.markdown("### 1. Proposed Project Performance")
st.markdown("#### Random Forest (Final Model)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    metric_grid_card("Accuracy", "97.78%", trend=None)
with col2:
    metric_grid_card("Precision (Macro)", "97.92%", trend=None)
with col3:
    metric_grid_card("Recall (Macro)", "97.78%", trend=None)
with col4:
    metric_grid_card("Macro F1 Score", "97.78%", trend=None)
with col5:
    metric_grid_card("5-Fold Cross Val.", "96.67%", trend="± 2.20%", trend_type="success")

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

col_p1, col_p2, col_p3, col_p4 = st.columns(4)

with col_p1:
    metric_grid_card("Sensitivity", "86.00%", trend=None)
with col_p2:
    metric_grid_card("Specificity", "90.00%", trend=None)
with col_p3:
    metric_grid_card("AUROC", "96.00%", trend=None)
with col_p4:
    metric_grid_card("AUPRC", "43.00%", trend=None)

st.info("💡 **Note:** The base paper evaluates performance using sensitivity, specificity, AUROC and AUPRC because the dataset is highly imbalanced.")

# ========================================================
# SECTION 3: Professional Comparison Table & Visualization
# ========================================================
st.write("")
st.markdown("### 3. Metric Comparison & Visualizations")

# Data preparation
comparison_data = {
    "Metric": [
        "Accuracy", 
        "Sensitivity / Recall", 
        "Specificity", 
        "Precision", 
        "Macro F1", 
        "AUROC", 
        "AUPRC",
        "Cross Validation"
    ],
    "Base Paper": [
        "Not Reported", 
        "86.00%", 
        "90.00%", 
        "Not Reported", 
        "Not Reported", 
        "96.00%", 
        "43.00%",
        "5-Fold CV used for tuning"
    ],
    "Proposed System": [
        "97.78%", 
        "97.78%", 
        "Not Evaluated", 
        "97.92%", 
        "97.78%", 
        "Not Evaluated", 
        "Not Evaluated",
        "96.67% ± 2.20%"
    ]
}

df_compare = pd.DataFrame(comparison_data)

tab1, tab2 = st.tabs(["📊 Charts & Visualizations", "📋 Structured Comparison Table"])

with tab1:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Grouped Bar Chart
        bar_metrics = ["Accuracy", "Sensitivity/Recall", "Specificity", "Precision", "Macro F1", "AUROC", "AUPRC"]
        # Numeric representation for chart, None represents missing
        base_vals = [None, 86.00, 90.00, None, None, 96.00, 43.00]
        proposed_vals = [97.78, 97.78, None, 97.92, 97.78, None, None]
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name='Base Paper',
            x=bar_metrics,
            y=base_vals,
            marker_color='#F59E0B',
            text=[f"{v:.1f}%" if v is not None else "" for v in base_vals],
            textposition='auto',
        ))
        fig_bar.add_trace(go.Bar(
            name='Proposed System',
            x=bar_metrics,
            y=proposed_vals,
            marker_color='#0F4C81',
            text=[f"{v:.1f}%" if v is not None else "" for v in proposed_vals],
            textposition='auto',
        ))
        
        fig_bar.update_layout(
            barmode='group',
            title={
                'text': "Metric-by-Metric Comparison",
                'font': {'family': 'Outfit', 'size': 16, 'color': '#0F4C81'}
            },
            yaxis=dict(title="Percentage (%)", range=[0, 115]),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=40, r=40, t=50, b=50),
            height=380
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with chart_col2:
        # Radar Chart for Common / Non-null comparison dimensions
        radar_categories = ["Sensitivity/Recall", "Specificity", "AUROC", "AUPRC", "Accuracy", "Precision", "Macro F1"]
        base_radar = [86.00, 90.00, 96.00, 43.00, 0, 0, 0]
        proposed_radar = [97.78, 0, 0, 0, 97.78, 97.92, 97.78]
        
        # Loop back to close the radar loop
        radar_categories_loop = radar_categories + [radar_categories[0]]
        base_radar_loop = base_radar + [base_radar[0]]
        proposed_radar_loop = proposed_radar + [proposed_radar[0]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=base_radar_loop,
            theta=radar_categories_loop,
            fill='toself',
            name='Base Paper',
            line_color='#F59E0B',
            fillcolor='rgba(245, 158, 11, 0.2)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=proposed_radar_loop,
            theta=radar_categories_loop,
            fill='toself',
            name='Proposed System',
            line_color='#0F4C81',
            fillcolor='rgba(15, 76, 129, 0.2)'
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
    # Render stylized HTML table to look highly professional
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
                <th>Proposed System</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Accuracy</strong></td>
                <td class="not-eval">Not Reported</td>
                <td class="highlight-val">97.78%</td>
            </tr>
            <tr>
                <td><strong>Sensitivity / Recall</strong></td>
                <td>86.00%</td>
                <td class="highlight-val">97.78%</td>
            </tr>
            <tr>
                <td><strong>Specificity</strong></td>
                <td>90.00%</td>
                <td class="not-eval">Not Evaluated</td>
            </tr>
            <tr>
                <td><strong>Precision</strong></td>
                <td class="not-eval">Not Reported</td>
                <td class="highlight-val">97.92%</td>
            </tr>
            <tr>
                <td><strong>Macro F1</strong></td>
                <td class="not-eval">Not Reported</td>
                <td class="highlight-val">97.78%</td>
            </tr>
            <tr>
                <td><strong>AUROC</strong></td>
                <td>96.00%</td>
                <td class="not-eval">Not Evaluated</td>
            </tr>
            <tr>
                <td><strong>AUPRC</strong></td>
                <td>43.00%</td>
                <td class="not-eval">Not Evaluated</td>
            </tr>
            <tr>
                <td><strong>Cross Validation</strong></td>
                <td>5-Fold CV used for tuning</td>
                <td class="highlight-val">96.67% ± 2.20%</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

# Download Button
csv_content = df_compare.to_csv(index=False)
st.write("")
st.download_button(
    label="📥 Download Comparative Benchmark Report (CSV)",
    data=csv_content,
    file_name="scientific_benchmark_report.csv",
    mime="text/csv"
)

# ========================================================
# SECTION 4: Research Conclusion Box
# ========================================================
st.write("")
st.markdown("### 4. Scientific Conclusion & Caveats")
st.markdown(
    """
    <div class="medical-card" style="background-color: #F8FAFC; border: 1px solid #CBD5E1;">
        <p style="font-size: 0.95rem; line-height: 1.7; color: #334155; margin: 0;">
            Our proposed Random Forest model achieved a test accuracy of <strong>97.78%</strong> on the synthetic HPO-derived cohort. 
            The reference paper used a different evaluation protocol based on highly imbalanced real-world EHR data, 
            reporting sensitivity (86%), specificity (90%), AUROC (96%), and AUPRC (43%).
        </p>
        <p style="font-size: 0.95rem; line-height: 1.7; color: #334155; margin: 12px 0 0 0;">
            <em>Note:</em> Since the datasets and evaluation methodologies differ, these metrics should not be interpreted as a direct superiority comparison.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.markdown("<hr style='border: 0; height: 1px; background: #E2E8F0;' />", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #94A3B8;'>Rare Disease Prediction System - Scientific Comparative Framework.</p>", unsafe_allow_html=True)
