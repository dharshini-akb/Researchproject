import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Any

def plot_confusion_matrix(cm: List[List[int]], classes: List[str]) -> go.Figure:
    """
    Renders an interactive Plotly heatmap for the Confusion Matrix.
    """
    z = np.array(cm)
    
    # Custom hover text
    hover_text = []
    for i in range(len(classes)):
        row = []
        for j in range(len(classes)):
            row.append(f"Actual: {classes[i]}<br>Predicted: {classes[j]}<br>Count: {z[i, j]}")
        hover_text.append(row)
        
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=classes,
        y=classes,
        hoverinfo="text",
        text=hover_text,
        colorscale=[[0, '#F8FAFC'], [0.2, '#E2E8F0'], [0.6, '#93C5FD'], [1, '#0F4C81']],
        showscale=True
    ))
    
    # Annotations
    annotations = []
    for i in range(len(classes)):
        for j in range(len(classes)):
            annotations.append(dict(
                x=classes[j],
                y=classes[i],
                text=str(z[i, j]),
                font=dict(family="Inter", size=15, color="#1E293B" if z[i, j] < z.max()/2 else "#FFFFFF"),
                showarrow=False
            ))
            
    fig.update_layout(
        title={
            'text': "Confusion Matrix",
            'font': {'family': 'Outfit', 'size': 18, 'color': '#0F4C81'}
        },
        xaxis_title="Predicted Disease Class",
        yaxis_title="Actual Disease Class",
        annotations=annotations,
        font=dict(family="Inter", size=12, color="#475569"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=40, t=50, b=50),
        height=380
    )
    return fig

def plot_roc_curves(roc_data: Dict[str, Any], classes: List[str]) -> go.Figure:
    """
    Renders a multi-class ROC curve chart using Plotly.
    """
    fig = go.Figure()
    
    # Palette matching theme
    colors = ['#0F4C81', '#2A9D8F', '#F59E0B']
    
    for idx, class_name in enumerate(classes):
        # The key in json is string index "0", "1", "2"
        key = str(idx)
        if key in roc_data:
            fpr = roc_data[key]["fpr"]
            tpr = roc_data[key]["tpr"]
            auc_val = roc_data[key]["auc"]
            
            fig.add_trace(go.Scatter(
                x=fpr,
                y=tpr,
                mode='lines',
                name=f"{class_name} (AUC = {auc_val:.3f})",
                line=dict(color=colors[idx % len(colors)], width=2.5),
                hoverinfo="text+name",
                hovertext=[f"FPR: {f:.3f}<br>TPR: {t}" for f, t in zip(fpr, tpr)]
            ))
            
    # Reference diagonal line
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        name='Random Classifier',
        line=dict(color='#94A3B8', width=1.5, dash='dash'),
        hoverinfo='none'
    ))
    
    fig.update_layout(
        title={
            'text': "Receiver Operating Characteristic (ROC)",
            'font': {'family': 'Outfit', 'size': 18, 'color': '#0F4C81'}
        },
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        xaxis=dict(gridcolor='#F1F5F9', range=[-0.02, 1.02]),
        yaxis=dict(gridcolor='#F1F5F9', range=[-0.02, 1.02]),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter", size=11)
        ),
        margin=dict(l=60, r=40, t=50, b=80),
        height=400
    )
    return fig

def plot_metrics_comparison(metrics_compare: Dict[str, Dict[str, float]]) -> go.Figure:
    """
    Plots side-by-side comparison of ML vs DL model metrics.
    """
    models = list(metrics_compare.keys())
    metric_keys = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
    metric_names = ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1 Score"]
    
    fig = go.Figure()
    
    # Model 1 color: #0F4C81, Model 2 color: #2A9D8F
    colors = ['#0F4C81', '#2A9D8F']
    
    for idx, model in enumerate(models):
        y_vals = [metrics_compare[model][m] for m in metric_keys]
        fig.add_trace(go.Bar(
            name=model,
            x=metric_names,
            y=y_vals,
            marker_color=colors[idx % 2],
            text=[f"{v*100:.1f}%" for v in y_vals],
            textposition='auto',
            hoverinfo="name+x+y"
        ))
        
    fig.update_layout(
        barmode='group',
        title={
            'text': "Model Performance Profile Comparison",
            'font': {'family': 'Outfit', 'size': 18, 'color': '#0F4C81'}
        },
        yaxis=dict(gridcolor='#F1F5F9', range=[0, 1.15], tickformat=".0%"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter", size=12)
        ),
        margin=dict(l=60, r=40, t=50, b=50),
        height=380
    )
    return fig
