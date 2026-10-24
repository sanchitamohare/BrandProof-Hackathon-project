"""
Reports & Analytics Page for BrandProof
Visualizes real stored application data, issue frequencies, approval trends, and CSV data exports.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database.models import (
    get_submissions, get_claims, get_dashboard_metrics,
    get_recent_activities, get_connection
)
from modules.ui_components import render_empty_state
from modules.export_utils import export_to_csv
try:
    from config.settings import THEME_COLORS
except (ImportError, ModuleNotFoundError):
    from settings import THEME_COLORS

def render_analytics():
    st.markdown("""
        <div>
            <h1 class="bp-page-title">Reports & Analytics</h1>
            <p class="bp-page-desc">Comprehensive brand governance intelligence, risk frequency distributions, and audit reports.</p>
        </div>
    """, unsafe_allow_html=True)

    metrics = get_dashboard_metrics()
    submissions = get_submissions()
    claims = get_claims()
    activities = get_recent_activities(limit=50)

    # Export Bar
    st.markdown("<h4 style='font-size: 1rem; margin-bottom: 0.5rem;'>Data Export Center</h4>", unsafe_allow_html=True)
    c_e1, c_e2, c_e3 = st.columns(3)
    with c_e1:
        if submissions:
            sub_csv = export_to_csv(submissions)
            st.download_button(
                label="📥 Export All Submissions (CSV)",
                data=sub_csv,
                file_name="brandproof_submissions.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📥 Export All Submissions (CSV)", disabled=True, use_container_width=True)

    with c_e2:
        if claims:
            clm_csv = export_to_csv(claims)
            st.download_button(
                label="📥 Export Claim Passport (CSV)",
                data=clm_csv,
                file_name="brandproof_claim_passport.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📥 Export Claim Passport (CSV)", disabled=True, use_container_width=True)

    with c_e3:
        if activities:
            act_csv = export_to_csv(activities)
            st.download_button(
                label="📥 Export Audit History (CSV)",
                data=act_csv,
                file_name="brandproof_audit_logs.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📥 Export Audit History (CSV)", disabled=True, use_container_width=True)

    st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    # Chart Grid
    ch_col1, ch_col2 = st.columns(2)

    with ch_col1:
        st.markdown("<h4 style='font-size: 1rem; font-weight: 700;'>Findings Distribution by Severity</h4>", unsafe_allow_html=True)
        sev_counts = metrics.get("issues_by_severity", {})
        if sum(sev_counts.values()) > 0:
            sev_df = pd.DataFrame([
                {"Severity": "High Risk", "Count": sev_counts.get("High", 0)},
                {"Severity": "Medium Risk", "Count": sev_counts.get("Medium", 0)},
                {"Severity": "Low / Tone", "Count": sev_counts.get("Low", 0)}
            ])
            fig_bar = px.bar(
                sev_df,
                x="Severity",
                y="Count",
                color="Severity",
                color_discrete_map={
                    "High Risk": THEME_COLORS["danger"],
                    "Medium Risk": THEME_COLORS["warning"],
                    "Low / Tone": THEME_COLORS["brand_light"]
                },
                text="Count"
            )
            fig_bar.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor="#FFFFFF")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            render_empty_state("No Issues Logged", "No governance issues have been flagged across submissions.", "📊")

    with ch_col2:
        st.markdown("<h4 style='font-size: 1rem; font-weight: 700;'>Review Pipeline Status</h4>", unsafe_allow_html=True)
        status_counts = metrics.get("status_counts", {})
        if sum(status_counts.values()) > 0:
            st_df = pd.DataFrame([{"Status": k, "Count": v} for k, v in status_counts.items()])
            fig_pie = px.pie(
                st_df,
                names="Status",
                values="Count",
                hole=0.45,
                color="Status",
                color_discrete_map={
                    "Approved": THEME_COLORS["success"],
                    "Submitted for Review": THEME_COLORS["brand_light"],
                    "Changes Requested": THEME_COLORS["warning"],
                    "Rejected": THEME_COLORS["danger"],
                    "Draft": "#94A3B8"
                }
            )
            fig_pie.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            render_empty_state("No Submissions", "No content submissions to display status distribution.", "📈")

    # Issue Categories Breakdown & Recent Timeline
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    ch_col3, ch_col4 = st.columns(2)

    with ch_col3:
        st.markdown("<h4 style='font-size: 1rem; font-weight: 700;'>Most Common Violation Categories</h4>", unsafe_allow_html=True)
        # Query database for issue categories
        conn = get_connection()
        cat_rows = conn.execute("SELECT category, COUNT(*) as count FROM detected_issues GROUP BY category ORDER BY count DESC").fetchall()
        conn.close()

        if cat_rows:
            cat_df = pd.DataFrame([{"Category": r["category"], "Count": r["count"]} for r in cat_rows])
            fig_cat = px.bar(cat_df, x="Count", y="Category", orientation="h", color="Count", color_continuous_scale="Blues")
            fig_cat.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            render_empty_state("No Categories Flagged", "No issues detected yet to aggregate categories.", "🔍")

    with ch_col4:
        st.markdown("<h4 style='font-size: 1rem; font-weight: 700;'>Claim Passport Verification Health</h4>", unsafe_allow_html=True)
        claim_counts = metrics.get("claim_counts", {})
        if sum(claim_counts.values()) > 0:
            clm_df = pd.DataFrame([{"Verification Status": k, "Total Claims": v} for k, v in claim_counts.items()])
            fig_clm = px.bar(
                clm_df,
                x="Verification Status",
                y="Total Claims",
                color="Verification Status",
                color_discrete_map={
                    "Verified": THEME_COLORS["success"],
                    "Pending Verification": THEME_COLORS["brand_light"],
                    "Needs Reverification": THEME_COLORS["warning"],
                    "Unsupported": THEME_COLORS["danger"]
                },
                text="Total Claims"
            )
            fig_clm.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor="#FFFFFF")
            st.plotly_chart(fig_clm, use_container_width=True)
        else:
            render_empty_state("No Claims", "No claims logged in Claim Passport.", "🛡")

    # Audit Trail Table
    st.markdown("<h4 style='font-size: 1rem; font-weight: 700; margin-top: 1.5rem;'>Workspace Governance Audit Log</h4>", unsafe_allow_html=True)
    if activities:
        act_df = pd.DataFrame(activities)[["timestamp", "event_type", "entity_type", "entity_id", "description", "user_name"]]
        act_df.columns = ["Timestamp", "Action", "Entity", "ID", "Description", "User"]
        st.dataframe(act_df, use_container_width=True, height=240)
    else:
        st.info("No audit activity logged.")
