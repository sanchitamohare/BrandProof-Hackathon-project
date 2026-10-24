"""
Content Checker Page for BrandProof
Allows marketing teams to check copy against brand rules, detect claim violations,
review suggested corrections, apply edits interactively, and send to the review workflow.
"""
import time
import streamlit as st
from config.settings import CONTENT_TYPES, THEME_COLORS
from database.models import (
    create_content_submission, save_analysis_result,
    update_submission_content, update_submission_review_status,
    get_brand_rules, get_claims, get_submission_by_id,
    get_latest_analysis_for_submission
)
from modules.checker_engine import run_content_analysis
from modules.ai_assistant import get_ai_status, request_ai_enhancement
from modules.ui_components import (
    get_risk_badge_html, get_severity_badge_html, render_empty_state
)
from modules.export_utils import generate_html_compliance_report

SAMPLE_PRESETS = {
    "Select an example to auto-fill...": "",
    "High-Risk Promotional Copy (Violates Multiple Rules)": (
        "Experience revolutionary breakthrough with the Apex Horizon Platform! "
        "Our autonomous engine guarantees 100% risk-free return on marketing spend and is unmatched by anyone in the world. "
        "Enterprise customers experience a 64% reduction in brand compliance audit time with zero risk. "
        "Upgrade your Legacy Cloud today."
    ),
    "Clean & Compliant Copy (Pre-Verified Claims)": (
        "Apex Horizon delivers dependable enterprise brand governance for growing organizations. "
        "Backed by SOC 2 Type II and ISO 27001 certifications, our platform helps marketing leaders maintain "
        "brand consistency across multi-channel campaigns."
    ),
    "Unregistered Numerical Claim (Needs Claim Passport)": (
        "Switching to Apex Horizon boosts social media engagement by 35% in the first 14 days. "
        "Join hundreds of high-growth marketing teams achieving unprecedented brand clarity."
    )
}

def render_content_checker():
    st.markdown("""
        <div>
            <h1 class="bp-page-title">Content Checker</h1>
            <p class="bp-page-desc">Review marketing content against your brand guidelines before publishing.</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize session state variables for content checker
    if "checker_text" not in st.session_state:
        st.session_state["checker_text"] = ""
    if "checker_title" not in st.session_state:
        st.session_state["checker_title"] = ""
    if "checker_type" not in st.session_state:
        st.session_state["checker_type"] = "Advertisement"
    if "checker_campaign" not in st.session_state:
        st.session_state["checker_campaign"] = "Q4 Enterprise Campaign"
    if "last_analysis" not in st.session_state:
        st.session_state["last_analysis"] = None
    if "current_submission_id" not in st.session_state:
        st.session_state["current_submission_id"] = None

    # Top sample loader helper
    col_preset, col_clear = st.columns([4, 1])
    with col_preset:
        selected_preset = st.selectbox(
            "Load Sample Content for Testing:",
            options=list(SAMPLE_PRESETS.keys()),
            key="preset_selector"
        )
        if selected_preset != "Select an example to auto-fill..." and SAMPLE_PRESETS[selected_preset]:
            st.session_state["checker_text"] = SAMPLE_PRESETS[selected_preset]
            if not st.session_state["checker_title"]:
                st.session_state["checker_title"] = selected_preset.split("(")[0].strip()

    with col_clear:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Clear Form", use_container_width=True):
            st.session_state["checker_text"] = ""
            st.session_state["checker_title"] = ""
            st.session_state["last_analysis"] = None
            st.session_state["current_submission_id"] = None
            st.rerun()

    # Input Form
    with st.container():
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem;">
            <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 0.85rem; color: #0F172A;">Content Submission Details</div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 1.5, 1.5])
        with col1:
            title_input = st.text_input(
                "Content Name or Asset Title *",
                value=st.session_state["checker_title"],
                placeholder="e.g. Q4 Growth Email Campaign — Variant A"
            )
            st.session_state["checker_title"] = title_input

        with col2:
            type_idx = CONTENT_TYPES.index(st.session_state["checker_type"]) if st.session_state["checker_type"] in CONTENT_TYPES else 0
            type_input = st.selectbox("Content Type", options=CONTENT_TYPES, index=type_idx)
            st.session_state["checker_type"] = type_input

        with col3:
            campaign_input = st.text_input(
                "Campaign / Product Name",
                value=st.session_state["checker_campaign"],
                placeholder="e.g. Enterprise Q4"
            )
            st.session_state["checker_campaign"] = campaign_input

        # Content Text Area
        content_input = st.text_area(
            "Marketing Copy to Analyze *",
            value=st.session_state["checker_text"],
            height=160,
            placeholder="Paste your marketing content, advertisement text, email draft, or social post here..."
        )
        st.session_state["checker_text"] = content_input

        col_opt1, col_opt2 = st.columns([2, 1])
        with col_opt1:
            policy_selector = st.selectbox(
                "Applicable Governance Policy",
                ["Standard Enterprise Global Policy", "Regulated Financial Services Policy", "B2B SaaS Growth Guidelines"]
            )
        with col_opt2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            analyze_clicked = st.button("🔍 Analyze Content", type="primary", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Trigger Analysis
    if analyze_clicked:
        if not content_input.strip():
            st.error("Please enter marketing text to analyze.")
            return

        final_title = title_input.strip() or "Untitled Marketing Draft"

        # Branded real-stage loading indicators
        progress_placeholder = st.empty()
        with progress_placeholder.container():
            st.markdown("""
            <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 1.25rem; text-align: center; margin: 1rem 0;">
                <div style="font-weight: 700; color: #1E3A8A; font-size: 1.05rem; margin-bottom: 0.3rem;">BrandProof Governance Engine</div>
                <div style="color: #64748B; font-size: 0.9rem;" id="bp-stage-text">Step 1/4: Reading content structure...</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.2)

        with progress_placeholder.container():
            st.markdown("""
            <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 1.25rem; text-align: center; margin: 1rem 0;">
                <div style="font-weight: 700; color: #1E3A8A; font-size: 1.05rem; margin-bottom: 0.3rem;">BrandProof Governance Engine</div>
                <div style="color: #64748B; font-size: 0.9rem;">Step 2/4: Checking brand rules & prohibited phrases...</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.2)

        with progress_placeholder.container():
            st.markdown("""
            <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 1.25rem; text-align: center; margin: 1rem 0;">
                <div style="font-weight: 700; color: #1E3A8A; font-size: 1.05rem; margin-bottom: 0.3rem;">BrandProof Governance Engine</div>
                <div style="color: #64748B; font-size: 0.9rem;">Step 3/4: Cross-referencing Claim Passport records...</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.2)

        # Run Engine
        rules = get_brand_rules(active_only=True)
        claims = get_claims()
        analysis = run_content_analysis(content_input, rules=rules, claims=claims)

        # Save to database
        sub_id = create_content_submission({
            "title": final_title,
            "content_type": type_input,
            "campaign_name": campaign_input,
            "content_text": content_input,
            "policy_applied": policy_selector,
            "risk_assessment": analysis["risk_assessment"],
            "review_status": "Draft"
        })
        analysis["submission_id"] = sub_id
        save_analysis_result(analysis, analysis["issues"])

        st.session_state["current_submission_id"] = sub_id
        st.session_state["last_analysis"] = analysis
        progress_placeholder.empty()
        st.success(f"Analysis completed and recorded under ID {sub_id}!")

    # Display Analysis Results if available
    if st.session_state["last_analysis"]:
        analysis = st.session_state["last_analysis"]
        sub_id = st.session_state["current_submission_id"]
        sub = get_submission_by_id(sub_id) if sub_id else {}

        st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
        st.markdown("<h2 style='font-size: 1.3rem; font-weight: 700; color: #0F172A; margin-bottom: 1rem;'>Compliance Report & Detected Findings</h2>", unsafe_allow_html=True)

        # Disclaimer banner
        st.markdown("""
        <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 0.65rem 1rem; margin-bottom: 1.25rem; font-size: 0.82rem; color: #1E40AF;">
            ℹ <strong>Brand Governance Assessment:</strong> This report represents an internal policy verification check against your active brand rules and Claim Passport entries. It is not an automated guarantee of legal or regulatory compliance.
        </div>
        """, unsafe_allow_html=True)

        # Executive Summary Box
        risk = analysis.get("risk_assessment", "Ready for Review")
        risk_badge = get_risk_badge_html(risk)
        score = analysis.get("compliance_score", 100.0)

        col_box1, col_box2, col_box3, col_box4 = st.columns(4)
        with col_box1:
            st.markdown(f"""
            <div class="bp-metric-box">
                <div class="bp-metric-label">Assessment</div>
                <div style="margin-top: 6px;">{risk_badge}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_box2:
            st.markdown(f"""
            <div class="bp-metric-box">
                <div class="bp-metric-label">Compliance Score</div>
                <div class="bp-metric-val" style="color: {'#059669' if score > 80 else ('#D97706' if score > 50 else '#DC2626')};">{score}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col_box3:
            st.markdown(f"""
            <div class="bp-metric-box">
                <div class="bp-metric-label">Total Findings</div>
                <div class="bp-metric-val">{analysis.get('total_issues', 0)}</div>
                <div class="bp-metric-sub">{analysis.get('high_severity_count', 0)} High • {analysis.get('medium_severity_count', 0)} Medium</div>
            </div>
            """, unsafe_allow_html=True)
        with col_box4:
            st.markdown(f"""
            <div class="bp-metric-box">
                <div class="bp-metric-label">Claims Needing Evidence</div>
                <div class="bp-metric-val">{analysis.get('evidence_needed_count', 0)}</div>
                <div class="bp-metric-sub">Action required in Claim Passport</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0;">
            <strong style="color: #0F172A; font-size: 0.92rem;">Executive Governance Summary:</strong>
            <p style="color: #475569; font-size: 0.88rem; margin: 0.4rem 0 0 0;">{analysis.get('executive_summary', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Detailed Issues List
        issues = analysis.get("issues", [])
        st.markdown(f"<h3 style='font-size: 1.1rem; font-weight: 700; margin: 1.2rem 0 0.6rem 0;'>Detected Issues ({len(issues)})</h3>", unsafe_allow_html=True)

        if not issues:
            st.success("✓ No violations detected! Content meets all active brand guidelines.")
        else:
            for idx, iss in enumerate(issues, 1):
                sev = iss.get("severity", "Medium")
                sev_badge = get_severity_badge_html(sev)
                excerpt = iss.get("excerpt", "")
                reason = iss.get("reason", "")
                rule_name = iss.get("applicable_rule", "")
                correction = iss.get("suggested_correction", "")
                ev_status = iss.get("evidence_status", "Not Required")

                st.markdown(f"""
                <div class="bp-issue-card {sev}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">#{idx}. {iss.get('title')}</span>
                        <span>{sev_badge}</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #334155; margin-bottom: 6px;">
                        <strong>Flagged Excerpt:</strong> <span class="bp-excerpt">"{excerpt}"</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #475569; margin-bottom: 4px;">
                        <strong>Governance Reason:</strong> {reason}
                    </div>
                    <div style="font-size: 0.83rem; color: #1E3A8A; margin-bottom: 4px;">
                        <strong>Applicable Policy:</strong> {rule_name}
                    </div>
                    <div style="font-size: 0.85rem; color: #065F46; margin-bottom: 4px;">
                        <strong>Suggested Correction:</strong> {correction}
                    </div>
                    <div style="font-size: 0.8rem; color: #64748B;">
                        <strong>Evidence Status:</strong> {ev_status}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Suggested Corrections & Side-by-Side Review
        st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700; margin: 1.5rem 0 0.6rem 0;'>Suggested Corrections & Revision</h3>", unsafe_allow_html=True)
        col_orig, col_rev = st.columns(2)
        with col_orig:
            st.markdown("<strong style='font-size: 0.88rem; color: #64748B;'>Original Submitted Copy</strong>", unsafe_allow_html=True)
            st.text_area("Original Copy", value=content_input, height=140, disabled=True, key="orig_disp")

        with col_rev:
            st.markdown("<strong style='font-size: 0.88rem; color: #059669;'>Proposed Compliant Draft</strong>", unsafe_allow_html=True)
            suggested_draft = analysis.get("suggested_content", content_input)
            revised_editor = st.text_area("Compliant Revision (Editable)", value=suggested_draft, height=140, key="rev_disp")

        # Interactive "Apply Suggestion to Workspace"
        col_act1, col_act2, col_act3 = st.columns([1.5, 1.5, 3])
        with col_act1:
            if st.button("Apply to Editor & Reanalyze", type="primary", use_container_width=True):
                st.session_state["checker_text"] = revised_editor
                # Re-run analysis on revised text
                re_rules = get_brand_rules(active_only=True)
                re_claims = get_claims()
                re_analysis = run_content_analysis(revised_editor, rules=re_rules, claims=re_claims)
                if sub_id:
                    update_submission_content(sub_id, revised_editor)
                    re_analysis["submission_id"] = sub_id
                    save_analysis_result(re_analysis, re_analysis["issues"])
                    st.session_state["last_analysis"] = re_analysis
                st.success("Applied correction and re-analyzed updated draft!")
                st.rerun()

        with col_act2:
            if st.button("🚀 Send for Review", use_container_width=True):
                if sub_id:
                    update_submission_review_status(sub_id, "Submitted for Review", "Demo Marketer", "Submitted from Content Checker after automated governance pass.")
                    st.success("Content successfully submitted to the Review Center!")
                    st.session_state["nav_selection"] = "Review Center"
                    st.rerun()

        with col_act3:
            # Downloadable HTML Compliance Report
            if sub_id:
                html_rep = generate_html_compliance_report(sub or {"title": final_title, "content_type": type_input, "campaign_name": campaign_input, "content_text": content_input}, analysis)
                st.download_button(
                    label="📄 Download Official Compliance Report (HTML)",
                    data=html_rep,
                    file_name=f"BrandProof_Report_{sub_id}.html",
                    mime="text/html",
                    use_container_width=True
                )

        # Optional AI Deep Reasoning Assistant Section
        with st.expander("🤖 Optional AI Reasoning & Deep Rewriting (Configurable API)"):
            ai_stat = get_ai_status()
            st.markdown(f"**Provider Status:** `{ai_stat['status_text']}`")
            if not ai_stat["configured"]:
                st.info("No external AI key configured in `.env`. BrandProof operates transparently using 100% deterministic rule-based checks. You can add an OpenAI-compatible API key in **Settings** if desired.")
            else:
                if st.button("Request AI Deep Rewrite via API"):
                    with st.spinner("Connecting to external AI provider..."):
                        ai_res = request_ai_enhancement(content_input, issues, "Authoritative, accurate, evidence-backed")
                        if ai_res["success"]:
                            st.success("AI Rewriting Completed!")
                            st.text_area("AI-Generated Version", value=ai_res["enhanced_text"], height=120)
                            st.caption(f"Reasoning: {ai_res['ai_insights']}")
                        else:
                            st.warning(ai_res["message"])
