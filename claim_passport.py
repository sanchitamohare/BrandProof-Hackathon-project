"""
Claim Passport Module for BrandProof
Connects marketing claims directly to evidence, audit trails, and verification lifecycles.
"""
import streamlit as st
import pandas as pd
from config.settings import CLAIM_STATUSES, THEME_COLORS
from database.models import (
    get_claims, get_claim_by_id, add_claim, update_claim, delete_claim,
    get_claim_audit_history
)
from modules.ui_components import get_status_badge_html, render_empty_state
from modules.export_utils import export_to_csv

CATEGORIES = [
    "Performance & Speed",
    "Financial & ROI",
    "Safety & Compliance",
    "Product Quality & Composition",
    "Scientific & Health",
    "Comparative / Superiority",
    "Market Leadership"
]

def render_claim_passport():
    st.markdown("""
        <div>
            <h1 class="bp-page-title">Claim Passport</h1>
            <p class="bp-page-desc">Keep every important brand claim connected to its evidence and verification history.</p>
        </div>
    """, unsafe_allow_html=True)

    # Top Action & Filter Row
    col_search, col_status, col_camp, col_new = st.columns([2.5, 1.5, 1.5, 1.5])
    with col_search:
        search_query = st.text_input("🔍 Search Claims", placeholder="Keyword, claim ID, evidence, owner...", key="clm_search")
    with col_status:
        status_filter = st.selectbox("Status Filter", ["All"] + CLAIM_STATUSES, key="clm_stat_flt")
    with col_camp:
        all_claims_raw = get_claims()
        campaigns = sorted(list(set(c.get("product_or_campaign", "General Brand") for c in all_claims_raw)))
        camp_filter = st.selectbox("Product / Campaign", ["All"] + campaigns, key="clm_camp_flt")
    with col_new:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        open_create_modal = st.button("➕ Add New Claim", type="primary", use_container_width=True)

    # Modal / Expandable form for adding a claim
    if "show_new_claim_form" not in st.session_state:
        st.session_state["show_new_claim_form"] = False
    if open_create_modal:
        st.session_state["show_new_claim_form"] = not st.session_state["show_new_claim_form"]

    if st.session_state["show_new_claim_form"]:
        with st.form("new_claim_form"):
            st.markdown("<h4 style='font-size: 1.05rem; margin-bottom: 0.5rem;'>Register New Brand Claim</h4>", unsafe_allow_html=True)
            new_text = st.text_area("Exact Claim Statement *", placeholder="e.g. Reduces brand audit time by up to 64%")
            
            c_f1, c_f2, c_f3 = st.columns(3)
            with c_f1:
                new_cat = st.selectbox("Category", CATEGORIES)
            with c_f2:
                new_prod = st.text_input("Associated Product / Campaign *", value="Apex Horizon Platform")
            with c_f3:
                new_owner = st.text_input("Claim Owner *", value="Sarah Lin (Brand Director)")

            new_ev_desc = st.text_area("Supporting Evidence Description", placeholder="Summary of data, research paper, benchmark, or customer trial...")
            new_ev_source = st.text_input("Evidence Source / Reference Document", placeholder="e.g. Forrester TEI Report, Oct 2024, Ref #FOR-2024-882")
            
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                new_status = st.selectbox("Initial Verification Status", CLAIM_STATUSES, index=1)
            with c_s2:
                new_notes = st.text_input("Internal Governance Notes", placeholder="e.g. Requires reverification in Q4")

            submit_claim = st.form_submit_button("Save Claim to Passport", type="primary")
            if submit_claim:
                if not new_text.strip():
                    st.error("Please provide the exact claim statement.")
                else:
                    new_id = add_claim({
                        "claim_text": new_text.strip(),
                        "product_or_campaign": new_prod.strip(),
                        "category": new_cat,
                        "evidence_description": new_ev_desc.strip(),
                        "evidence_source": new_ev_source.strip(),
                        "verification_status": new_status,
                        "owner": new_owner.strip(),
                        "notes": new_notes.strip()
                    })
                    st.success(f"Claim successfully saved with ID {new_id}!")
                    st.session_state["show_new_claim_form"] = False
                    st.rerun()

    # Query filtered claims
    claims = get_claims(search=search_query, status=status_filter, campaign=camp_filter)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    col_count, col_exp = st.columns([4, 1.5])
    with col_count:
        st.markdown(f"<span style='font-size: 0.9rem; color: #64748B; font-weight: 600;'>Showing {len(claims)} Registered Brand Claims</span>", unsafe_allow_html=True)
    with col_exp:
        if claims:
            csv_bytes = export_to_csv(claims)
            st.download_button(
                label="📥 Export Claims (CSV)",
                data=csv_bytes,
                file_name="brandproof_claims_passport.csv",
                mime="text/csv",
                use_container_width=True
            )

    if not claims:
        render_empty_state("No Claims Found", "No claims matched your search filters. Click 'Add New Claim' to register one.", "🛡")
        return

    # Claim Cards / Table
    for claim in claims:
        cid = claim["id"]
        status = claim.get("verification_status", "Pending")
        status_badge = get_status_badge_html(status)
        
        with st.container():
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                    <div>
                        <span style="font-family: monospace; font-weight: 700; color: #1E3A8A; background: #EFF6FF; padding: 2px 8px; border-radius: 4px; font-size: 0.85rem;">{cid}</span>
                        <span style="font-size: 0.82rem; color: #64748B; margin-left: 8px;">{claim.get('category')} • {claim.get('product_or_campaign')}</span>
                    </div>
                    <div>{status_badge}</div>
                </div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin: 6px 0 8px 0;">
                    "{claim.get('claim_text')}"
                </div>
                <div style="font-size: 0.84rem; color: #475569; margin-bottom: 4px;">
                    <strong>Evidence:</strong> {claim.get('evidence_description') or 'No supporting evidence description provided.'}
                </div>
                <div style="font-size: 0.82rem; color: #1E3A8A; margin-bottom: 4px;">
                    <strong>Source:</strong> {claim.get('evidence_source') or 'Unspecified reference'}
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 6px;">
                    Owner: <strong>{claim.get('owner')}</strong> • Verified Date: {claim.get('verified_date') or 'Pending'} • Updated: {claim.get('updated_at')[:16]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Expandable inspection & editing drawer
            with st.expander(f"Manage Claim {cid} & Audit History"):
                tab_edit, tab_audit = st.tabs(["Edit Claim & Status", "Verification Audit Trail"])
                
                with tab_edit:
                    with st.form(f"edit_form_{cid}"):
                        e_text = st.text_area("Claim Statement", value=claim.get("claim_text", ""))
                        e_c1, e_c2, e_c3 = st.columns(3)
                        with e_c1:
                            e_cat = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(claim.get("category")) if claim.get("category") in CATEGORIES else 0)
                        with e_c2:
                            e_prod = st.text_input("Product / Campaign", value=claim.get("product_or_campaign", ""))
                        with e_c3:
                            e_owner = st.text_input("Responsible Owner", value=claim.get("owner", ""))

                        e_desc = st.text_area("Evidence Description", value=claim.get("evidence_description", ""))
                        e_src = st.text_input("Evidence Source Document / URL", value=claim.get("evidence_source", ""))
                        
                        e_s1, e_s2 = st.columns(2)
                        with e_s1:
                            stat_idx = CLAIM_STATUSES.index(status) if status in CLAIM_STATUSES else 0
                            e_stat = st.selectbox("Verification Status", CLAIM_STATUSES, index=stat_idx)
                        with e_s2:
                            e_notes = st.text_input("Internal Governance Notes", value=claim.get("notes", ""))

                        e_b1, e_b2 = st.columns([1, 4])
                        with e_b1:
                            save_edit = st.form_submit_button("Update Claim", type="primary")
                        if save_edit:
                            update_claim(cid, {
                                "claim_text": e_text,
                                "product_or_campaign": e_prod,
                                "category": e_cat,
                                "evidence_description": e_desc,
                                "evidence_source": e_src,
                                "verification_status": e_stat,
                                "owner": e_owner,
                                "notes": e_notes
                            })
                            st.success(f"Claim {cid} updated successfully!")
                            st.rerun()

                    # Danger zone delete
                    if st.button(f"🗑 Delete Claim {cid}", key=f"del_{cid}"):
                        delete_claim(cid)
                        st.warning(f"Deleted claim {cid}.")
                        st.rerun()

                with tab_audit:
                    history = get_claim_audit_history(cid)
                    if not history:
                        st.caption("No audit entries recorded for this claim.")
                    else:
                        for h in history:
                            st.markdown(f"""
                            <div style="border-left: 2px solid #3B82F6; padding-left: 8px; margin-bottom: 8px; font-size: 0.8rem;">
                                <strong style="color: #1E3A8A;">{h.get('action')}</strong> — {h.get('details')}
                                <div style="color: #94A3B8; font-size: 0.72rem;">{h.get('timestamp')} by {h.get('changed_by')}</div>
                            </div>
                            """, unsafe_allow_html=True)
