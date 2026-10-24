"""
Reusable SaaS UI components and HTML/CSS builders for BrandProof
"""
from typing import Any, Dict, List, Optional
import streamlit as st
from config.settings import APP_NAME, APP_TAGLINE, DEFAULT_WORKSPACE, THEME_COLORS

def inject_custom_styles():
    """Injects core SaaS theme styles into the Streamlit app."""
    css = f"""
    <style>
    /* Global Background and Typography */
    .stApp {{
        background-color: {THEME_COLORS['bg_main']};
        color: {THEME_COLORS['text_main']};
    }}
    
    /* Top Header Bar */
    .bp-header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.9rem 1.4rem;
        background-color: {THEME_COLORS['bg_card']};
        border: 1px solid {THEME_COLORS['border']};
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }}
    .bp-brand-group {{
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }}
    .bp-logo-icon {{
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, {THEME_COLORS['brand']} 0%, {THEME_COLORS['primary']} 100%);
        color: #FFFFFF;
        border-radius: 9px;
        font-weight: 800;
        font-size: 1.15rem;
        box-shadow: 0 2px 4px rgba(30, 58, 138, 0.25);
    }}
    .bp-brand-title {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {THEME_COLORS['primary']};
        margin: 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }}
    .bp-brand-tagline {{
        font-size: 0.78rem;
        color: {THEME_COLORS['text_muted']};
        margin: 0;
        font-weight: 500;
    }}
    .bp-workspace-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.35rem 0.85rem;
        background-color: #F1F5F9;
        border: 1px solid {THEME_COLORS['border']};
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #334155;
    }}
    .bp-workspace-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: {THEME_COLORS['success']};
    }}

    /* Metric Cards */
    .bp-metric-box {{
        background: {THEME_COLORS['bg_card']};
        border: 1px solid {THEME_COLORS['border']};
        border-radius: 10px;
        padding: 1.15rem 1.3rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        margin-bottom: 0.5rem;
    }}
    .bp-metric-label {{
        font-size: 0.8rem;
        font-weight: 600;
        color: {THEME_COLORS['text_muted']};
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.25rem;
    }}
    .bp-metric-val {{
        font-size: 1.9rem;
        font-weight: 700;
        color: {THEME_COLORS['text_main']};
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }}
    .bp-metric-sub {{
        font-size: 0.76rem;
        color: {THEME_COLORS['text_muted']};
    }}

    /* Issue Box */
    .bp-issue-card {{
        background-color: #FFFFFF;
        border: 1px solid {THEME_COLORS['border']};
        border-left-width: 5px;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.25rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02);
    }}
    .bp-issue-card.High {{
        border-left-color: {THEME_COLORS['danger']};
        background-color: #FFFDFD;
    }}
    .bp-issue-card.Medium {{
        border-left-color: {THEME_COLORS['warning']};
        background-color: #FFFFFE;
    }}
    .bp-issue-card.Low {{
        border-left-color: {THEME_COLORS['brand_light']};
        background-color: #FDFEFF;
    }}

    /* Excerpt Pill */
    .bp-excerpt {{
        background-color: #FEF08A;
        color: #713F12;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.88rem;
        font-weight: 600;
    }}

    /* Section Headings */
    .bp-page-title {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {THEME_COLORS['primary']};
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }}
    .bp-page-desc {{
        font-size: 0.92rem;
        color: {THEME_COLORS['text_muted']};
        margin-bottom: 1.5rem;
    }}

    /* Empty state */
    .bp-empty-box {{
        background: {THEME_COLORS['bg_card']};
        border: 1px dashed {THEME_COLORS['border']};
        border-radius: 10px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_top_header(current_page: str):
    """Renders the top application header with logo, title, and workspace."""
    header_html = f"""
    <div class="bp-header-container">
        <div class="bp-brand-group">
            <div class="bp-logo-icon">✓</div>
            <div>
                <div class="bp-brand-title">{APP_NAME} <span style="font-size: 0.8rem; font-weight: 500; color: #64748B;">/ {current_page}</span></div>
                <div class="bp-brand-tagline">{APP_TAGLINE}</div>
            </div>
        </div>
        <div class="bp-workspace-badge">
            <span class="bp-workspace-dot"></span>
            <span>{DEFAULT_WORKSPACE}</span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_metric_card(label: str, value: Any, subtext: str = ""):
    """Renders a styled metric card."""
    card_html = f"""
    <div class="bp-metric-box">
        <div class="bp-metric-label">{label}</div>
        <div class="bp-metric-val">{value}</div>
        <div class="bp-metric-sub">{subtext}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def get_risk_badge_html(risk: str) -> str:
    """Returns HTML badge for risk assessment."""
    if risk == "Ready for Review":
        return f'<span style="background-color: {THEME_COLORS["success_bg"]}; color: {THEME_COLORS["success"]}; border: 1px solid #A7F3D0; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.78rem;">✓ Ready for Review</span>'
    elif risk == "Needs Attention":
        return f'<span style="background-color: {THEME_COLORS["warning_bg"]}; color: {THEME_COLORS["warning"]}; border: 1px solid #FDE68A; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.78rem;">⚠ Needs Attention</span>'
    elif risk == "High-Risk Content":
        return f'<span style="background-color: {THEME_COLORS["danger_bg"]}; color: {THEME_COLORS["danger"]}; border: 1px solid #FECACA; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.78rem;">✖ High-Risk Content</span>'
    else:
        return f'<span style="background-color: #F1F5F9; color: #475569; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.78rem;">{risk}</span>'

def get_severity_badge_html(severity: str) -> str:
    """Returns HTML badge for issue severity."""
    if severity == "High":
        return f'<span style="background-color: {THEME_COLORS["danger_bg"]}; color: {THEME_COLORS["danger"]}; border: 1px solid #FECACA; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem;">HIGH RISK</span>'
    elif severity == "Medium":
        return f'<span style="background-color: {THEME_COLORS["warning_bg"]}; color: {THEME_COLORS["warning"]}; border: 1px solid #FDE68A; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem;">MEDIUM</span>'
    else:
        return f'<span style="background-color: {THEME_COLORS["brand_pale"]}; color: {THEME_COLORS["brand_light"]}; border: 1px solid #BFDBFE; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem;">LOW / TONE</span>'

def get_status_badge_html(status: str) -> str:
    """Returns HTML badge for claim verification status or review status."""
    if status in ["Verified", "Approved"]:
        return f'<span style="background-color: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.75rem;">● {status}</span>'
    elif status in ["Pending Verification", "Submitted for Review"]:
        return f'<span style="background-color: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.75rem;">● {status}</span>'
    elif status in ["Needs Reverification", "Changes Requested"]:
        return f'<span style="background-color: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.75rem;">● {status}</span>'
    elif status in ["Unsupported", "Rejected"]:
        return f'<span style="background-color: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.75rem;">● {status}</span>'
    else:
        return f'<span style="background-color: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.75rem;">● {status}</span>'

def render_empty_state(title: str, description: str, icon: str = "📋"):
    """Renders a clean empty state card."""
    html = f"""
    <div class="bp-empty-box">
        <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 1.05rem; font-weight: 700; color: #1E293B; margin-bottom: 0.3rem;">{title}</div>
        <div style="font-size: 0.85rem; color: #64748B; max-width: 480px; margin: 0 auto;">{description}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
