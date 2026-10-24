"""
Settings and Brand Governance Rule Management Page for BrandProof
Allows administrators to manage brand profile, configure custom governance rules,
adjust severity ratings, and configure optional external AI keys.
"""
import os
import streamlit as st
import pandas as pd
from config.settings import RULE_CATEGORIES, SEVERITY_LEVELS, THEME_COLORS
from database.models import (
    get_brand_profile, update_brand_profile,
    get_brand_rules, add_brand_rule, update_brand_rule, delete_brand_rule
)
from modules.ai_assistant import get_ai_status

def render_settings():
    st.markdown("""
        <div>
            <h1 class="bp-page-title">Brand Guidelines & Governance Rules</h1>
            <p class="bp-page-desc">Configure the brand voice, prohibited language patterns, and evidence rules that power the Content Checker.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_profile, tab_rules, tab_ai = st.tabs(["Brand Profile & Voice", "Rule Management", "AI Configuration"])

    # ========================================================
    # TAB 1: Brand Profile
    # ========================================================
    with tab_profile:
        profile = get_brand_profile()
        with st.form("brand_profile_form"):
            st.markdown("<h4 style='font-size: 1.05rem; margin-bottom: 0.8rem;'>Enterprise Brand Identity</h4>", unsafe_allow_html=True)
            
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                b_name = st.text_input("Brand Name", value=profile.get("brand_name", ""))
            with c_p2:
                b_ind = st.text_input("Industry / Vertical", value=profile.get("industry", ""))

            b_tag = st.text_input("Official Brand Tagline", value=profile.get("tagline", ""))
            b_voice = st.text_area(
                "Brand Voice & Tone Guidelines",
                value=profile.get("voice_and_tone", ""),
                height=100,
                help="Describe voice principles, e.g. authoritative, empathetic, avoid hyperbole."
            )
            b_disc = st.text_area(
                "Default Enterprise Legal Disclaimer",
                value=profile.get("primary_disclaimer", ""),
                height=80,
                help="Standard legal footnote required on high-impact customer collateral."
            )

            save_profile = st.form_submit_button("Save Brand Profile", type="primary")
            if save_profile:
                update_brand_profile({
                    "brand_name": b_name,
                    "tagline": b_tag,
                    "voice_and_tone": b_voice,
                    "industry": b_ind,
                    "primary_disclaimer": b_disc
                })
                st.success("Brand profile updated successfully! All future analyses will reflect these guidelines.")
                st.rerun()

    # ========================================================
    # TAB 2: Governance Rules (Add / Edit / Delete)
    # ========================================================
    with tab_rules:
        st.markdown("<h4 style='font-size: 1.05rem; margin-bottom: 0.5rem;'>Active Governance Checking Rules</h4>", unsafe_allow_html=True)
        st.caption("These rules are executed automatically by the BrandProof engine during content evaluation.")

        # Add Rule Expander
        with st.expander("➕ Create New Custom Governance Rule"):
            with st.form("new_rule_form"):
                r_title = st.text_input("Rule Title *", placeholder="e.g. Disallow 'Guaranteed ROI'")
                
                r_c1, r_c2, r_c3 = st.columns(3)
                with r_c1:
                    r_cat = st.selectbox("Rule Category", RULE_CATEGORIES)
                with r_c2:
                    r_sev = st.selectbox("Severity Rating", SEVERITY_LEVELS, index=1)
                with r_c3:
                    r_is_regex = st.checkbox("Regex Pattern (Advanced)", value=False)

                r_pattern = st.text_input("Target Phrase or Pattern *", placeholder="e.g. guaranteed ROI or \\b(100%\\s*risk-free)\\b")
                r_explain = st.text_area("Governance Explanation *", placeholder="Why this phrasing is prohibited or regulated...")
                r_fix = st.text_input("Suggested Replacement / Action", placeholder="e.g. Replace with 'projected efficiency improvement'")
                r_ev = st.text_input("Required Supporting Evidence Type", placeholder="e.g. Audited client case study")

                save_rule = st.form_submit_button("Add Rule to Engine", type="primary")
                if save_rule:
                    if not r_title.strip() or not r_pattern.strip() or not r_explain.strip():
                        st.error("Please fill in Rule Title, Target Phrase, and Explanation.")
                    else:
                        rule_id = add_brand_rule({
                            "title": r_title.strip(),
                            "category": r_cat,
                            "severity": r_sev,
                            "is_regex": r_is_regex,
                            "pattern_or_phrase": r_pattern.strip(),
                            "explanation": r_explain.strip(),
                            "suggested_fix": r_fix.strip(),
                            "required_evidence_type": r_ev.strip(),
                            "is_active": True
                        })
                        st.success(f"New governance rule added ({rule_id})!")
                        st.rerun()

        # Display Existing Rules
        rules = get_brand_rules(active_only=False)
        st.markdown(f"<span style='font-size: 0.88rem; color: #64748B; font-weight: 600;'>{len(rules)} Configured Brand Rules</span>", unsafe_allow_html=True)

        for rule in rules:
            rid = rule["id"]
            sev = rule.get("severity", "Medium")
            sev_color = "#DC2626" if sev == "High" else ("#D97706" if sev == "Medium" else "#2563EB")
            
            with st.container():
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid {sev_color}; border-radius: 6px; padding: 12px 16px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <div>
                            <span style="font-family: monospace; font-size: 0.8rem; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; color: #1E3A8A; font-weight: 700;">{rid}</span>
                            <strong style="margin-left: 8px; font-size: 0.95rem; color: #0F172A;">{rule.get('title')}</strong>
                            <span style="font-size: 0.8rem; color: #64748B; margin-left: 8px;">({rule.get('category')})</span>
                        </div>
                        <span style="font-size: 0.72rem; font-weight: 700; color: {sev_color}; border: 1px solid {sev_color}; padding: 1px 6px; border-radius: 4px;">{sev.upper()}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #334155; margin-bottom: 4px;">
                        <strong>Target:</strong> <code style="background: #F1F5F9; padding: 1px 5px; border-radius: 3px;">{rule.get('pattern_or_phrase')}</code>
                    </div>
                    <div style="font-size: 0.83rem; color: #475569;">
                        <strong>Why:</strong> {rule.get('explanation')}
                    </div>
                    <div style="font-size: 0.83rem; color: #065F46;">
                        <strong>Correction:</strong> {rule.get('suggested_fix')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"Edit / Delete Rule {rid}"):
                    with st.form(f"edit_rule_{rid}"):
                        e_title = st.text_input("Title", value=rule.get("title", ""))
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            e_cat = st.selectbox("Category", RULE_CATEGORIES, index=RULE_CATEGORIES.index(rule.get("category")) if rule.get("category") in RULE_CATEGORIES else 0)
                        with c2:
                            e_sev = st.selectbox("Severity", SEVERITY_LEVELS, index=SEVERITY_LEVELS.index(sev) if sev in SEVERITY_LEVELS else 1)
                        with c3:
                            e_active = st.checkbox("Rule is Active", value=bool(rule.get("is_active", 1)))

                        e_pat = st.text_input("Pattern / Phrase", value=rule.get("pattern_or_phrase", ""))
                        e_exp = st.text_area("Explanation", value=rule.get("explanation", ""))
                        e_sug = st.text_input("Suggested Correction", value=rule.get("suggested_fix", ""))
                        
                        save_u = st.form_submit_button("Update Rule", type="primary")
                        if save_u:
                            update_brand_rule(rid, {
                                "title": e_title,
                                "category": e_cat,
                                "severity": e_sev,
                                "pattern_or_phrase": e_pat,
                                "explanation": e_exp,
                                "suggested_fix": e_sug,
                                "is_regex": rule.get("is_regex", 0),
                                "required_evidence_type": rule.get("required_evidence_type", ""),
                                "is_active": e_active
                            })
                            st.success(f"Rule {rid} updated!")
                            st.rerun()

                    if st.button(f"🗑 Delete Rule {rid}", key=f"del_rule_{rid}"):
                        delete_brand_rule(rid)
                        st.warning(f"Deleted rule {rid}.")
                        st.rerun()

    # ========================================================
    # TAB 3: AI Configuration
    # ========================================================
    with tab_ai:
        st.markdown("<h4 style='font-size: 1.05rem;'>Optional External AI Integration</h4>", unsafe_allow_html=True)
        st.markdown("""
        BrandProof uses **transparent, deterministic, explainable rule-based algorithms** as its default core engine.
        Optionally, you can connect an OpenAI-compatible API key for advanced natural language rewrites and tone alignment.
        """)

        ai_status = get_ai_status()
        st.markdown(f"**Current Status:** `{ai_status['status_text']}`")

        with st.form("ai_key_form"):
            api_key_input = st.text_input(
                "OpenAI API Key (Optional)",
                type="password",
                value=os.environ.get("OPENAI_API_KEY", ""),
                help="Enter your sk-... API key. Stored only in current session environment."
            )
            model_input = st.selectbox(
                "AI Model Selection",
                ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                index=0
            )

            save_ai = st.form_submit_button("Save AI Settings", type="primary")
            if save_ai:
                if api_key_input.strip():
                    os.environ["OPENAI_API_KEY"] = api_key_input.strip()
                    os.environ["OPENAI_MODEL"] = model_input
                    os.environ["AI_PROVIDER"] = "openai"
                    st.success("AI API Key configured successfully for this session!")
                else:
                    os.environ.pop("OPENAI_API_KEY", None)
                    os.environ["AI_PROVIDER"] = "none"
                    st.info("Operating in 100% deterministic rule-based verification mode.")
                st.rerun()
