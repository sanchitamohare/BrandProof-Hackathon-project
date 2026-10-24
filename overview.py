"""
Overview Dashboard for BrandProof
Displays workspace KPIs, recent checks, severity breakdown, and audit activity.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database.models import (
    get_dashboard_metrics, get_submissions, get_recent_activities,
    get_claims
)
from database.seed_data import load_demo_data
from modules.ui_components import (
    render_metric_card, get_risk_badge_html, get_status_badge_html,
    render_empty_state
)
from config.settings import THEME_COLORS

def render_overview():
    # Welcoming Banner
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-size: 1.8rem; font-weight: 700; color: #0F172A; margin-bottom: 0.2rem;">Good to have you here.</h1>
            <p style="font-size: 0.95rem; color: #64748B; margin: 0;">Your brand compliance, all in one place.</p>
        </div>
    """, unsafe_allow_html=True)

    # Primary & Secondary Call to Action Row
    col_cta1, col_cta2, col_cta_spacer, col_demo = st.columns([1.5, 1.5, 3, 2])
    with col_cta1:
        if st.button("➕ Check New Content", type="primary", use_container_width=True):
            st.session_state["nav_selection"] = "Content Checker"
            st.rerun()
    with col_cta2:
        if st.button("🛡 View Claim Passport", use_container_width=True):
            st.session_state["nav_selection"] = "Claim Passport"
            st.rerun()
    with col_demo:
        if st.button("🔄 Reload Demo Data", help="Safely reload standard demonstration records without duplicating"):
            load_demo_data(force_reload=True)
            st.success("Demo workspace refreshed successfully!")
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Metrics Row
    metrics = get_dashboard_metrics()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Content Checks", metrics["total_checks"], "Submissions analyzed")
    with c2:
        render_metric_card("Flagged Claims", metrics["flagged_claims"], "Pending or unsupported")
    with c3:
        render_metric_card("Pending Reviews", metrics["pending_reviews"], "Awaiting human review")
    with c4:
        render_metric_card("Approved Content", metrics["approved_content"], "Cleared for publication")

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Charts & Breakdown Row
    col_chart1, col_chart2 = st.columns([1.2, 1])

    with col_chart1:
        st.markdown("<h3 style='font-size: 1.05rem; font-weight: 700; margin-bottom: 0.5rem;'>Findings by Severity</h3>", unsafe_allow_html=True)
        sev_data = metrics["issues_by_severity"]
        sev_df = pd.DataFrame([
            {"Severity": "High Risk", "Issues": sev_data["High"], "Color": THEME_COLORS["danger"]},
            {"Severity": "Medium Risk", "Issues": sev_data["Medium"], "Color": THEME_COLORS["warning"]},
            {"Severity": "Low / Tone", "Issues": sev_data["Low"], "Color": THEME_COLORS["brand_light"]}
        ])
        if sev_df["Issues"].sum() > 0:
            fig = px.bar(
                sev_df,
                x="Severity",
                y="Issues",
                color="Severity",
                color_discrete_map={
                    "High Risk": THEME_COLORS["danger"],
                    "Medium Risk": THEME_COLORS["warning"],
                    "Low / Tone": THEME_COLORS["brand_light"]
                },
                text="Issues"
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=10, b=20),
                height=240,
                showlegend=False,
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            render_empty_state("No Issues Flagged", "All analyzed content meets compliance standards.", "✨")

    with col_chart2:
        st.markdown("<h3 style='font-size: 1.05rem; font-weight: 700; margin-bottom: 0.5rem;'>Claim Passport Verification</h3>", unsafe_allow_html=True)
        claim_counts = metrics["claim_counts"]
        if claim_counts and sum(claim_counts.values()) > 0:
            c_df = pd.DataFrame([{"Status": k, "Count": v} for k, v in claim_counts.items()])
            fig_pie = px.pie(
                c_df,
                names="Status",
                values="Count",
                hole=0.55,
                color="Status",
                color_discrete_map={
                    "Verified": THEME_COLORS["success"],
                    "Pending Verification": THEME_COLORS["brand_light"],
                    "Needs Reverification": THEME_COLORS["warning"],
                    "Unsupported": THEME_COLORS["danger"]
                }
            )
            fig_pie.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=240,
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            render_empty_state("No Claims Recorded", "Register brand claims in Claim Passport to view breakdown.", "🛡")

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Recent Submissions and Activity Feed Row
    col_subs, col_feed = st.columns([1.6, 1])

    with col_subs:
        st.markdown("<h3 style='font-size: 1.05rem; font-weight: 700; margin-bottom: 0.6rem;'>Recent Content Submissions</h3>", unsafe_allow_html=True)
        recent_subs = get_submissions()[:5]

        if not recent_subs:
            render_empty_state("No Content Submissions Yet", "Use the Content Checker to analyze your first marketing asset.", "📄")
        else:
            for sub in recent_subs:
                risk_badge = get_risk_badge_html(sub.get("risk_assessment", "Draft"))
                status_badge = get_status_badge_html(sub.get("review_status", "Draft"))
                
                with st.container():
                    st.markdown(f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
                            <div>
                                <strong style="font-size: 14px; color: #0F172A;">{sub.get('title')}</strong>
                                <span style="font-size: 11px; color: #64748B; margin-left: 8px;">({sub.get('content_type')})</span>
                            </div>
                            <div>{risk_badge} {status_badge}</div>
                        </div>
                        <div style="font-size: 12px; color: #64748B; margin-bottom: 6px;">
                            Campaign: <strong>{sub.get('campaign_name', 'Global')}</strong> • Updated: {sub.get('updated_at', '')[:16]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with col_feed:
        st.markdown("<h3 style='font-size: 1.05rem; font-weight: 700; margin-bottom: 0.6rem;'>Recent Workspace Activity</h3>", unsafe_allow_html=True)
        activities = get_recent_activities(limit=6)

        if not activities:
            st.info("No activity recorded yet.")
        else:
            for act in activities:
                st.markdown(f"""
                <div style="border-left: 2px solid #CBD5E1; padding-left: 10px; margin-bottom: 10px; font-size: 12px;">
                    <span style="font-weight: 600; color: #1E3A8A;">[{act.get('event_type')}]</span>
                    <span style="color: #334155;">{act.get('description')}</span>
                    <div style="color: #94A3B8; font-size: 10px;">{act.get('timestamp')[:16]} by {act.get('user_name')}</div>
                </div>
                """, unsafe_allow_html=True)
