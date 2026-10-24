"""
Review Center and Approval Workflow Page for BrandProof
Supports human review, status progression, audit trails, and reviewer comments.
"""
import streamlit as st
from config.settings import REVIEW_STATUSES, THEME_COLORS
from database.models import (
    get_submissions, get_submission_by_id, get_latest_analysis_for_submission,
    update_submission_review_status, get_review_history
)
from modules.ui_components import (
    get_risk_badge_html, get_status_badge_html, get_severity_badge_html,
    render_empty_state
)
from modules.export_utils import generate_html_compliance_report

REVIEWERS = [
    "Sarah Lin (Brand Director)",
    "Marcus Vance (Chief Security Officer)",
    "David Chen (Senior Legal Counsel)",
    "Elena Rostova (VP of Marketing)"
]

def render_review_center():
    st.markdown("""
        <div>
            <h1 class="bp-page-title">Review Center</h1>
            <p class="bp-page-desc">Review submitted marketing assets, inspect governance findings, and record formal approval decisions.</p>
        </div>
    """, unsafe_allow_html=True)

    # Reviewer Workspace Identity Selector
    col_id, col_flt_stat, col_flt_risk = st.columns([2, 1.5, 1.5])
    with col_id:
        active_reviewer = st.selectbox("Current Reviewer Identity:", REVIEWERS, index=0)
    with col_flt_stat:
        status_flt = st.selectbox("Filter Status:", ["All"] + REVIEW_STATUSES, index=0)
    with col_flt_risk:
        risk_flt = st.selectbox("Filter Risk:", ["All", "High-Risk Content", "Needs Attention", "Ready for Review"])

    submissions = get_submissions(status=status_flt, risk=risk_flt)

    st.markdown(f"<span style='font-size: 0.9rem; color: #64748B; font-weight: 600;'>{len(submissions)} Assets in Review Pipeline</span>", unsafe_allow_html=True)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if not submissions:
        render_empty_state("No Submissions Match Filter", "All submissions are either resolved or none meet the current filter criteria.", "📋")
        return

    for sub in submissions:
        sid = sub["id"]
        title = sub.get("title", "Untitled Asset")
        ctype = sub.get("content_type", "General")
        camp = sub.get("campaign_name", "Global")
        risk = sub.get("risk_assessment", "Draft")
        status = sub.get("review_status", "Draft")
        author = sub.get("author", "Marketing Lead")
        updated = sub.get("updated_at", "")[:16]

        risk_badge = get_risk_badge_html(risk)
        status_badge = get_status_badge_html(status)

        with st.container():
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                    <div>
                        <span style="font-family: monospace; font-weight: 700; color: #1E3A8A; background: #EFF6FF; padding: 2px 8px; border-radius: 4px; font-size: 0.85rem;">{sid}</span>
                        <strong style="font-size: 1rem; color: #0F172A; margin-left: 8px;">{title}</strong>
                        <span style="font-size: 0.82rem; color: #64748B; margin-left: 6px;">({ctype} • {camp})</span>
                    </div>
                    <div>{risk_badge} {status_badge}</div>
                </div>
                <div style="font-size: 0.82rem; color: #64748B; margin-top: 4px;">
                    Submitted by: <strong>{author}</strong> • Last Updated: {updated}
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Inspect Asset & Record Decision ({sid})"):
                analysis = get_latest_analysis_for_submission(sid)
                
                tab_findings, tab_copy, tab_action, tab_history = st.tabs(["Compliance Analysis", "Content Comparison", "Review Decision", "Audit History"])

                # Tab 1: Compliance Analysis
                with tab_findings:
                    if not analysis:
                        st.info("No compliance analysis recorded for this submission yet.")
                    else:
                        st.markdown(f"**Score:** `{analysis.get('compliance_score', 0)}/100` | **Total Issues:** `{analysis.get('total_issues', 0)}`")
                        st.markdown(f"**Executive Summary:** {analysis.get('executive_summary', '')}")
                        
                        issues = analysis.get("issues", [])
                        if not issues:
                            st.success("No active violations detected.")
                        else:
                            for idx, iss in enumerate(issues, 1):
                                sev_badge = get_severity_badge_html(iss.get("severity", "Medium"))
                                st.markdown(f"""
                                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid {'#DC2626' if iss.get('severity') == 'High' else '#D97706'}; padding: 10px 14px; margin-bottom: 8px; border-radius: 4px;">
                                    <div style="display: flex; justify-content: space-between;">
                                        <strong>#{idx}. {iss.get('title')}</strong>
                                        <span>{sev_badge}</span>
                                    </div>
                                    <div style="font-size: 0.85rem; color: #334155; margin: 4px 0;">Excerpt: <span class="bp-excerpt">"{iss.get('excerpt')}"</span></div>
                                    <div style="font-size: 0.83rem; color: #475569;">Reason: {iss.get('reason')}</div>
                                    <div style="font-size: 0.83rem; color: #065F46;">Correction: {iss.get('suggested_correction')}</div>
                                </div>
                                """, unsafe_allow_html=True)

                # Tab 2: Copy Comparison
                with tab_copy:
                    c_col1, c_col2 = st.columns(2)
                    with c_col1:
                        st.markdown("**Submitted Marketing Copy:**")
                        st.text_area(f"Copy_{sid}", value=sub.get("content_text", ""), height=150, disabled=True)
                    with c_col2:
                        st.markdown("**Recommended Compliant Draft:**")
                        sugg = analysis.get("suggested_content", sub.get("content_text", "")) if analysis else sub.get("content_text", "")
                        st.text_area(f"Sugg_{sid}", value=sugg, height=150, disabled=True)

                    if analysis:
                        html_cert = generate_html_compliance_report(sub, analysis)
                        st.download_button(
                            label=f"📄 Download Compliance Audit Certificate ({sid})",
                            data=html_cert,
                            file_name=f"BrandProof_Compliance_Certificate_{sid}.html",
                            mime="text/html",
                            key=f"dl_rep_{sid}"
                        )

                # Tab 3: Formal Review Action
                with tab_action:
                    with st.form(f"review_action_form_{sid}"):
                        st.markdown(f"<strong style='font-size: 0.95rem;'>Record Decision as {active_reviewer}:</strong>", unsafe_allow_html=True)
                        review_comments = st.text_area(
                            "Reviewer Feedback / Directives *",
                            placeholder="Enter review notes, required revisions, or reasons for approval/rejection..."
                        )

                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        with col_btn1:
                            btn_approve = st.form_submit_button("✅ Approve Content", type="primary")
                        with col_btn2:
                            btn_changes = st.form_submit_button("⚠️ Request Changes")
                        with col_btn3:
                            btn_reject = st.form_submit_button("❌ Reject Content")

                        if btn_approve:
                            if risk == "High-Risk Content" and not review_comments.strip():
                                st.error("Explicit justification comments are required to approve high-risk content.")
                            else:
                                update_submission_review_status(sid, "Approved", active_reviewer, review_comments.strip() or "Approved by brand review lead.")
                                st.success(f"Submission {sid} Approved!")
                                st.rerun()

                        if btn_changes:
                            if not review_comments.strip():
                                st.error("Please provide comments describing the changes requested.")
                            else:
                                update_submission_review_status(sid, "Changes Requested", active_reviewer, review_comments.strip())
                                st.warning(f"Changes requested for {sid}.")
                                st.rerun()

                        if btn_reject:
                            update_submission_review_status(sid, "Rejected", active_reviewer, review_comments.strip() or "Rejected for brand policy non-compliance.")
                            st.error(f"Submission {sid} Rejected.")
                            st.rerun()

                # Tab 4: Audit & Decision History
                with tab_history:
                    history = get_review_history(sid)
                    if not history:
                        st.caption("No previous review actions logged for this asset.")
                    else:
                        for h in history:
                            st.markdown(f"""
                            <div style="border-left: 2px solid #1E3A8A; padding-left: 10px; margin-bottom: 8px; font-size: 0.82rem;">
                                <strong>{h.get('action')}</strong> — {h.get('comments') or 'No comments entered.'}
                                <div style="color: #94A3B8; font-size: 0.74rem;">{h.get('timestamp')} by {h.get('reviewer_name')} (Status: {h.get('previous_status')} ➔ {h.get('new_status')})</div>
                            </div>
                            """, unsafe_allow_html=True)
