import streamlit as st

def medical_card(title: str, content: str, badge_text: str = None, badge_type: str = "success"):
    """
    Renders a premium medical-themed layout card with an optional status badge.
    """
    badge_html = ""
    if badge_text:
        badge_html = f'<span class="badge badge-{badge_type}">{badge_text}</span>'
        
    card_html = f"""
    <div class="medical-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <h3 style="margin: 0; font-size: 1.2rem; color: #0F4C81;">{title}</h3>
            {badge_html}
        </div>
        <div style="font-size: 0.95rem; line-height: 1.6; color: #334155;">
            {content}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def prediction_probability_card(disease_name: str, omim_id: str, probability: float, rank: int):
    """
    Renders a probability distribution card for a prediction.
    """
    pct = probability * 100
    color_class = "prob-primary" if rank == 1 else "prob-secondary"
    
    card_html = f"""
    <div class="medical-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div>
                <span style="font-size: 0.8rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Rank #{rank}</span>
                <h4 style="margin: 0; font-size: 1.15rem; color: #0F4C81;">{disease_name}</h4>
                <code style="font-size: 0.8rem; color: #0284c7; background-color: #f0f9ff; padding: 2px 6px; border-radius: 4px;">{omim_id}</code>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 1.75rem; font-weight: 700; color: #0F4C81;">{pct:.1f}%</span>
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 500;">Confidence Probability</div>
            </div>
        </div>
        <div class="probability-bar-container">
            <div class="probability-bar-fill {color_class}" style="width: {pct}%;"></div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def metric_grid_card(label: str, value: str, trend: str = None, trend_type: str = "success"):
    """
    Renders a single metric box in a grid configuration.
    """
    trend_html = ""
    if trend:
        color = "#22C55E" if trend_type == "success" else "#EF4444"
        trend_html = f'<span style="font-size: 0.8rem; color: {color}; font-weight: 600; margin-left: 8px;">{trend}</span>'
        
    card_html = f'<div class="medical-card" style="text-align: center; padding: 18px 12px; margin-bottom: 10px;"><div class="metric-label">{label}</div><div style="display: flex; align-items: baseline; justify-content: center;"><span class="metric-value">{value}</span>{trend_html}</div></div>'
    st.markdown(card_html, unsafe_allow_html=True)

