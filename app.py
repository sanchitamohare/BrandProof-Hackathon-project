"""
BrandProof — AI-Powered Brand Governance Platform
Main Application Entry Point & Multi-Page Controller
"""
import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import time
import streamlit as st

# Configure page metadata
st.set_page_config(
    page_title="BrandProof — Trust Every Brand Claim",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config.settings import APP_NAME, APP_TAGLINE, DEFAULT_WORKSPACE, VERSION
from database.db import init_db
from database.seed_data import load_demo_data
from modules.ui_components import inject_custom_styles, render_top_header
from modules.pages.overview import render_overview
from modules.pages.content_checker import render_content_checker
from modules.pages.claim_passport import render_claim_passport
from modules.pages.review_center import render_review_center
from modules.pages.analytics import render_analytics
from modules.pages.settings_page import render_settings
from modules.pages.help_guide import render_help_guide

def main():
    # Inject CSS
    inject_custom_styles()

    # Initial App Boot & Loading Experience (Only runs once per browser session)
    if "brandproof_booted" not in st.session_state:
        init_db()
        load_demo_data(force_reload=False)
        st.session_state["brandproof_booted"] = True
        st.session_state["nav_selection"] = "Overview"

        boot_placeholder = st.empty()
        with boot_placeholder.container():
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; text-align: center;">
                <div style="width: 52px; height: 52px; background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); color: #FFF; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: 800; box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3); margin-bottom: 1rem;">
                    ✓
                </div>
                <h1 style="font-size: 2rem; font-weight: 800; color: #0F172A; margin: 0 0 0.4rem 0;">{APP_NAME}</h1>
                <p style="font-size: 1rem; color: #64748B; margin: 0 0 1.5rem 0; font-weight: 500;">{APP_TAGLINE}</p>
                <div style="color: #1E3A8A; font-size: 0.9rem; font-weight: 600;">Preparing your brand workspace...</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.35)
        boot_placeholder.empty()

    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 0.5rem 0.2rem 1.2rem 0.2rem; border-bottom: 1px solid #E2E8F0; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.65rem;">
                <div style="width: 32px; height: 32px; background: #1E3A8A; color: #FFF; border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: 800;">
                    ✓
                </div>
                <div>
                    <strong style="font-size: 1.15rem; color: #0F172A; letter-spacing: -0.01em;">{APP_NAME}</strong>
                    <div style="font-size: 0.72rem; color: #64748B;">{APP_TAGLINE}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        nav_options = [
            "Overview",
            "Content Checker",
            "Claim Passport",
            "Review Center",
            "Reports and Analytics",
            "Settings",
            "Help and Demo Guide"
        ]

        # Ensure session state has a valid selection
        if "nav_selection" not in st.session_state:
            st.session_state["nav_selection"] = "Overview"

        current_idx = nav_options.index(st.session_state["nav_selection"]) if st.session_state["nav_selection"] in nav_options else 0

        selected_page = st.radio(
            "Main Navigation",
            options=nav_options,
            index=current_idx,
            label_visibility="collapsed"
        )
        st.session_state["nav_selection"] = selected_page

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 12px; font-size: 0.75rem; color: #64748B;">
            <div style="font-weight: 700; color: #334155; margin-bottom: 2px;">Active Workspace</div>
            <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{DEFAULT_WORKSPACE}</div>
            <div style="margin-top: 6px; color: #94A3B8;">Engine: <strong>Deterministic + AI Opt-in</strong></div>
            <div style="color: #94A3B8;">Version: {VERSION}</div>
        </div>
        """, unsafe_allow_html=True)

    # Render Active Top Header
    render_top_header(current_page=st.session_state["nav_selection"])

    # Router logic
    page = st.session_state["nav_selection"]
    if page == "Overview":
        render_overview()
    elif page == "Content Checker":
        render_content_checker()
    elif page == "Claim Passport":
        render_claim_passport()
    elif page == "Review Center":
        render_review_center()
    elif page == "Reports and Analytics":
        render_analytics()
    elif page == "Settings":
        render_settings()
    elif page == "Help and Demo Guide":
        render_help_guide()

if __name__ == "__main__":
    main()
