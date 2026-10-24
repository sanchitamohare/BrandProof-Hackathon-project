"""
Help & Demo Guide for BrandProof
Provides hackathon judges and new users with a step-by-step walkthrough of the platform.
"""
import streamlit as st
from database.seed_data import load_demo_data

def render_help_guide():
    st.markdown("""
        <div>
            <h1 class="bp-page-title">Help & Demonstration Guide</h1>
            <p class="bp-page-desc">Complete end-to-end walkthrough designed for hackathon judges and enterprise compliance teams.</p>
        </div>
    """, unsafe_allow_html=True)

    # Quick Demo Reset
    col_info, col_reset = st.columns([3, 1.2])
    with col_info:
        st.markdown("""
        BrandProof is designed to be explored independently. Every button, form, audit log, and chart is backed by real SQLite persistent storage.
        """)
    with col_reset:
        if st.button("🔄 Reload Demonstration Data", type="primary", use_container_width=True):
            load_demo_data(force_reload=True)
            st.success("Demo dataset reloaded successfully! (All sample claims and analyses restored)")
            st.rerun()

    st.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    # 12-Step Judge Evaluation Walkthrough
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 700; color: #0F172A; margin-bottom: 0.8rem;'>Judge Walkthrough — 12-Step Verification Workflow</h3>", unsafe_allow_html=True)

    steps = [
        ("Step 1: Open the Dashboard", "Review workspace high-level KPIs: Total Content Checks, Flagged Claims, Pending Reviews, and Approved Content. View severity distributions and live activity logs."),
        ("Step 2: Navigate to Content Checker", "Click **Content Checker** in the sidebar. This is the core governance analysis engine."),
        ("Step 3: Load Sample Copy", "Use the dropdown at the top to select **'High-Risk Promotional Copy (Violates Multiple Rules)'** to instantly load realistic enterprise copy."),
        ("Step 4: Click 'Analyze Content'", "Notice the branded multi-stage progress indicator: reading content ➔ checking rules ➔ cross-referencing Claim Passport ➔ preparing report."),
        ("Step 5: Inspect Detected Issues", "Examine flagged issues: absolute risk-free claims, unsupported superlatives, and deprecated nomenclature, each with exact excerpts, reasons, and policy links."),
        ("Step 6: Review Suggested Corrections", "Scroll to the side-by-side comparison showing the original submitted text alongside the automatically generated compliant draft."),
        ("Step 7: Apply Correction & Reanalyze", "Click **'Apply to Editor & Reanalyze'**. Watch the engine update the score and recalculate risk in real time!"),
        ("Step 8: Submit for Formal Review", "Click **'Send for Review'**. The asset transitions from draft state to the formal review pipeline."),
        ("Step 9: Open Review Center", "Navigate to **Review Center** in the sidebar. Select your reviewer identity (e.g., Sarah Lin, Brand Director)."),
        ("Step 10: Record Approval Decision", "Inspect the submission, review side-by-side copy, and submit formal approval or feedback with reviewer notes."),
        ("Step 11: Inspect Claim Passport", "Navigate to **Claim Passport**. Search for claims (e.g. '64% reduction'), inspect audit histories, or edit evidence documentation."),
        ("Step 12: Verify Reports & Dashboard", "Return to **Overview** and **Reports & Analytics** to see the metric counters, bar charts, and audit activity reflect your exact actions.")
    ]

    for title, desc in steps:
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
            <strong style="color: #1E3A8A; font-size: 0.95rem;">{title}</strong>
            <p style="color: #475569; font-size: 0.86rem; margin: 0.25rem 0 0 0;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    # Core Principles & Reliability FAQ
    st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 0.8rem;'>Frequently Asked Questions & Governance Principles</h3>", unsafe_allow_html=True)

    with st.expander("Why does BrandProof use transparent rule-based checks by default?"):
        st.write("""
        In enterprise brand governance and legal compliance, predictability, explainability, and reproducibility are paramount. 
        LLM hallucinations or stochastic responses can miss critical regulatory violations. 
        BrandProof guarantees that every configured brand rule, prohibited phrase, and required evidence citation is checked with 100% deterministic accuracy.
        Optional LLM reasoning can be toggled on when creative rewriting is desired.
        """)

    with st.expander("How does the Claim Passport connect to content checking?"):
        st.write("""
        When marketing content contains quantitative metrics or superiority claims (e.g., '64% reduction in audit time'), the engine automatically searches the Claim Passport. 
        If a matching claim is verified, the engine prompts the marketer to cite the official evidence source. 
        If the claim is unsupported or missing, it flags the phrase as a high governance risk requiring substantiation.
        """)

    with st.expander("How is data persisted?"):
        st.write("""
        All brand profiles, rules, claims, audit trails, content submissions, and review actions are persistently stored in a local SQLite database (`brandproof.db`). 
        Refreshing your browser or restarting the application preserves all your data.
        """)
