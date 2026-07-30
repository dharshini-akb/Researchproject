import os
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import precision_recall_curve, auc
from config import system_config
from components import charts

def plot_pr_curves(y_test, y_probs, classes):
    """
    Plots multiclass Precision-Recall curves.
    """
    from sklearn.preprocessing import label_binarize
    y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
    
    fig = go.Figure()
    colors = ['#0F4C81', '#2A9D8F', '#F59E0B']
    
    for i, class_name in enumerate(classes):
        precision, recall, _ = precision_recall_curve(y_test_bin[:, i], y_probs[:, i])
        pr_auc = auc(recall, precision)
        
        fig.add_trace(go.Scatter(
            x=recall, y=precision,
            mode='lines',
            name=f"{class_name} (AUC = {pr_auc:.3f})",
            line=dict(color=colors[i % len(colors)], width=2.5)
        ))
        
    fig.update_layout(
        title={'text': "Precision-Recall (PR) Curves", 'font': {'family': 'Outfit', 'size': 18, 'color': '#0F4C81'}},
        xaxis_title="Recall",
        yaxis_title="Precision",
        xaxis=dict(gridcolor='#F1F5F9', range=[-0.02, 1.02]),
        yaxis=dict(gridcolor='#F1F5F9', range=[-0.02, 1.02]),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=40, t=50, b=80),
        height=400
    )
    return fig

def main():
    # Load test data and metrics
    base_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex")
    X_test = pd.read_csv(os.path.join(base_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(base_dir, "y_test.csv"))["target"]
    
    # Load Random Forest model to get probabilities for PR curve
    from models.random_forest import RandomForestModel
    rf = RandomForestModel()
    rf.load(os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib"))
    rf_probs = rf.predict_proba(X_test)
    
    classes = [system_config.DISEASE_NAMES[i] for i in range(3)]
    
    # 1. Generate PR Curve Plotly Object
    fig_pr = plot_pr_curves(y_test, rf_probs, classes)
    
    # Save Plotly figures as HTML in assets
    assets_dir = system_config.ASSETS_DIR
    os.makedirs(assets_dir, exist_ok=True)
    
    fig_pr.write_html(os.path.join(assets_dir, "pr_curve.html"))
    print("Saved Precision-Recall curves plot to assets/pr_curve.html")

if __name__ == "__main__":
    main()
