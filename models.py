"""
Database models and data access operations for BrandProof
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
from database.db import get_connection

def generate_id(prefix: str) -> str:
    """Generate a clean, readable identifier."""
    short = str(uuid.uuid4())[:8].upper()
    return f"{prefix}-{short}"

def get_current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# Brand Profile Operations
# ==========================================

def get_brand_profile() -> Dict[str, Any]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM brand_profiles ORDER BY id LIMIT 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "brand_name": "Apex Horizon",
        "tagline": "Empowering Next-Generation Enterprise Growth",
        "voice_and_tone": "Authoritative, transparent, research-backed, and empathetic. Strictly avoid hyperbolic, unsubstantiated absolute promises.",
        "industry": "B2B SaaS & Enterprise Health",
        "primary_disclaimer": "Results may vary based on deployment scale. Consult product documentation for full methodology.",
        "updated_at": get_current_timestamp()
    }

def update_brand_profile(data: Dict[str, Any]):
    conn = get_connection()
    now = get_current_timestamp()
    existing = conn.execute("SELECT id FROM brand_profiles LIMIT 1").fetchone()
    if existing:
        conn.execute("""
            UPDATE brand_profiles
            SET brand_name = ?, tagline = ?, voice_and_tone = ?, industry = ?, primary_disclaimer = ?, updated_at = ?
            WHERE id = ?
        """, (data.get("brand_name"), data.get("tagline"), data.get("voice_and_tone"),
              data.get("industry"), data.get("primary_disclaimer"), now, existing["id"]))
    else:
        conn.execute("""
            INSERT INTO brand_profiles (brand_name, tagline, voice_and_tone, industry, primary_disclaimer, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data.get("brand_name"), data.get("tagline"), data.get("voice_and_tone"),
              data.get("industry"), data.get("primary_disclaimer"), now))
    conn.commit()
    conn.close()
    log_activity("UPDATE", "BrandProfile", "1", "Updated brand profile guidelines", "Workspace Admin")

# ==========================================
# Brand Rules Operations
# ==========================================

def get_brand_rules(active_only: bool = True) -> List[Dict[str, Any]]:
    conn = get_connection()
    query = "SELECT * FROM brand_rules"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY severity DESC, title ASC"
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_rule_by_id(rule_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM brand_rules WHERE id = ?", (rule_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_brand_rule(rule_data: Dict[str, Any]) -> str:
    conn = get_connection()
    rule_id = rule_data.get("id") or generate_id("RULE")
    now = get_current_timestamp()
    conn.execute("""
        INSERT INTO brand_rules (id, category, title, pattern_or_phrase, is_regex, severity, explanation, suggested_fix, required_evidence_type, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rule_id,
        rule_data.get("category", "Prohibited Phrase"),
        rule_data.get("title", "Untitled Rule"),
        rule_data.get("pattern_or_phrase", ""),
        1 if rule_data.get("is_regex") else 0,
        rule_data.get("severity", "Medium"),
        rule_data.get("explanation", ""),
        rule_data.get("suggested_fix", ""),
        rule_data.get("required_evidence_type", ""),
        1 if rule_data.get("is_active", True) else 0,
        now
    ))
    conn.commit()
    conn.close()
    log_activity("CREATE", "BrandRule", rule_id, f"Created rule: {rule_data.get('title')}", "Workspace Admin")
    return rule_id

def update_brand_rule(rule_id: str, rule_data: Dict[str, Any]):
    conn = get_connection()
    conn.execute("""
        UPDATE brand_rules
        SET category = ?, title = ?, pattern_or_phrase = ?, is_regex = ?, severity = ?, explanation = ?, suggested_fix = ?, required_evidence_type = ?, is_active = ?
        WHERE id = ?
    """, (
        rule_data.get("category"),
        rule_data.get("title"),
        rule_data.get("pattern_or_phrase"),
        1 if rule_data.get("is_regex") else 0,
        rule_data.get("severity"),
        rule_data.get("explanation"),
        rule_data.get("suggested_fix"),
        rule_data.get("required_evidence_type"),
        1 if rule_data.get("is_active", True) else 0,
        rule_id
    ))
    conn.commit()
    conn.close()
    log_activity("UPDATE", "BrandRule", rule_id, f"Updated rule: {rule_data.get('title')}", "Workspace Admin")

def delete_brand_rule(rule_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM brand_rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    log_activity("DELETE", "BrandRule", rule_id, f"Deleted rule {rule_id}", "Workspace Admin")

# ==========================================
# Claim Passport Operations
# ==========================================

def get_claims(search: str = "", status: str = "", campaign: str = "") -> List[Dict[str, Any]]:
    conn = get_connection()
    query = "SELECT * FROM claims WHERE 1=1"
    params = []
    if search:
        query += " AND (claim_text LIKE ? OR id LIKE ? OR owner LIKE ? OR evidence_description LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])
    if status and status != "All":
        query += " AND verification_status = ?"
        params.append(status)
    if campaign and campaign != "All":
        query += " AND product_or_campaign = ?"
        params.append(campaign)
    query += " ORDER BY updated_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_claim_by_id(claim_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM claims WHERE id = ?", (claim_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_claim(data: Dict[str, Any]) -> str:
    conn = get_connection()
    claim_id = data.get("id") or generate_id("CLM")
    now = get_current_timestamp()
    conn.execute("""
        INSERT INTO claims (id, claim_text, product_or_campaign, category, evidence_description, evidence_source, verification_status, owner, verified_date, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        claim_id,
        data.get("claim_text", ""),
        data.get("product_or_campaign", "General Brand"),
        data.get("category", "Performance & Speed"),
        data.get("evidence_description", ""),
        data.get("evidence_source", ""),
        data.get("verification_status", "Pending Verification"),
        data.get("owner", "Compliance Team"),
        data.get("verified_date", now if data.get("verification_status") == "Verified" else None),
        data.get("notes", ""),
        now,
        now
    ))
    # Add initial audit entry
    conn.execute("""
        INSERT INTO claim_audit_logs (claim_id, action, changed_by, details, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (claim_id, "CLAIM_CREATED", data.get("owner", "User"), f"Registered claim with status: {data.get('verification_status')}", now))
    conn.commit()
    conn.close()
    log_activity("CREATE", "Claim", claim_id, f"Added claim: {data.get('claim_text')[:40]}...", data.get("owner", "User"))
    return claim_id

def update_claim(claim_id: str, data: Dict[str, Any], changed_by: str = "Compliance Lead"):
    conn = get_connection()
    now = get_current_timestamp()
    current = conn.execute("SELECT verification_status FROM claims WHERE id = ?", (claim_id,)).fetchone()
    old_status = current["verification_status"] if current else "Unknown"

    verified_date = data.get("verified_date")
    if data.get("verification_status") == "Verified" and not verified_date:
        verified_date = now

    conn.execute("""
        UPDATE claims
        SET claim_text = ?, product_or_campaign = ?, category = ?, evidence_description = ?, evidence_source = ?, verification_status = ?, owner = ?, verified_date = ?, notes = ?, updated_at = ?
        WHERE id = ?
    """, (
        data.get("claim_text"),
        data.get("product_or_campaign"),
        data.get("category"),
        data.get("evidence_description"),
        data.get("evidence_source"),
        data.get("verification_status"),
        data.get("owner"),
        verified_date,
        data.get("notes"),
        now,
        claim_id
    ))

    # Audit log
    details = f"Status changed from {old_status} to {data.get('verification_status')}" if old_status != data.get("verification_status") else "Claim details updated"
    conn.execute("""
        INSERT INTO claim_audit_logs (claim_id, action, changed_by, details, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (claim_id, "CLAIM_UPDATED", changed_by, details, now))

    conn.commit()
    conn.close()
    log_activity("UPDATE", "Claim", claim_id, f"Updated claim {claim_id}: {details}", changed_by)

def delete_claim(claim_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM claims WHERE id = ?", (claim_id,))
    conn.commit()
    conn.close()
    log_activity("DELETE", "Claim", claim_id, f"Deleted claim record {claim_id}", "Compliance Lead")

def get_claim_audit_history(claim_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM claim_audit_logs WHERE claim_id = ? ORDER BY timestamp DESC", (claim_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==========================================
# Content Submissions & Analysis Operations
# ==========================================

def create_content_submission(data: Dict[str, Any]) -> str:
    conn = get_connection()
    sub_id = data.get("id") or generate_id("SUB")
    now = get_current_timestamp()
    conn.execute("""
        INSERT INTO content_submissions (id, title, content_type, campaign_name, content_text, description, policy_applied, risk_assessment, review_status, assigned_reviewer, author, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sub_id,
        data.get("title", "Untitled Marketing Draft"),
        data.get("content_type", "Advertisement"),
        data.get("campaign_name", "Global Campaign"),
        data.get("content_text", ""),
        data.get("description", ""),
        data.get("policy_applied", "Apex Standard Global Policy"),
        data.get("risk_assessment", "Pending Analysis"),
        data.get("review_status", "Draft"),
        data.get("assigned_reviewer", "Sarah Lin (Brand Director)"),
        data.get("author", "Demo Marketer"),
        now,
        now
    ))
    conn.commit()
    conn.close()
    log_activity("CREATE", "Submission", sub_id, f"Created draft: {data.get('title')}", data.get("author", "Marketer"))
    return sub_id

def save_analysis_result(analysis_data: Dict[str, Any], issues: List[Dict[str, Any]]) -> str:
    conn = get_connection()
    anl_id = analysis_data.get("id") or generate_id("ANL")
    now = get_current_timestamp()
    sub_id = analysis_data.get("submission_id")

    conn.execute("""
        INSERT INTO analysis_results (id, submission_id, total_issues, high_severity_count, medium_severity_count, low_severity_count, evidence_needed_count, compliance_score, executive_summary, suggested_content, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        anl_id,
        sub_id,
        analysis_data.get("total_issues", len(issues)),
        analysis_data.get("high_severity_count", 0),
        analysis_data.get("medium_severity_count", 0),
        analysis_data.get("low_severity_count", 0),
        analysis_data.get("evidence_needed_count", 0),
        analysis_data.get("compliance_score", 100.0),
        analysis_data.get("executive_summary", ""),
        analysis_data.get("suggested_content", ""),
        now
    ))

    # Insert detected issues
    for iss in issues:
        iss_id = iss.get("id") or generate_id("ISS")
        conn.execute("""
            INSERT INTO detected_issues (id, analysis_id, rule_id, title, category, severity, excerpt, reason, applicable_rule, suggested_correction, evidence_status, position_start, position_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            iss_id,
            anl_id,
            iss.get("rule_id", "GENERAL"),
            iss.get("title", "Issue"),
            iss.get("category", "General"),
            iss.get("severity", "Medium"),
            iss.get("excerpt", ""),
            iss.get("reason", ""),
            iss.get("applicable_rule", ""),
            iss.get("suggested_correction", ""),
            iss.get("evidence_status", "Not Required"),
            iss.get("position_start", 0),
            iss.get("position_end", 0)
        ))

    # Update submission risk assessment
    risk = analysis_data.get("risk_assessment", "Needs Attention")
    conn.execute("""
        UPDATE content_submissions
        SET risk_assessment = ?, updated_at = ?
        WHERE id = ?
    """, (risk, now, sub_id))

    conn.commit()
    conn.close()
    log_activity("ANALYZE", "Submission", sub_id, f"Completed compliance check (Risk: {risk}, {len(issues)} issues)", "BrandProof Engine")
    return anl_id

def get_submission_by_id(submission_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM content_submissions WHERE id = ?", (submission_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_submissions(status: str = "", risk: str = "", campaign: str = "") -> List[Dict[str, Any]]:
    conn = get_connection()
    query = "SELECT * FROM content_submissions WHERE 1=1"
    params = []
    if status and status != "All":
        query += " AND review_status = ?"
        params.append(status)
    if risk and risk != "All":
        query += " AND risk_assessment = ?"
        params.append(risk)
    if campaign and campaign != "All":
        query += " AND campaign_name = ?"
        params.append(campaign)
    query += " ORDER BY updated_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_latest_analysis_for_submission(submission_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM analysis_results WHERE submission_id = ? ORDER BY created_at DESC LIMIT 1", (submission_id,)).fetchone()
    if not row:
        conn.close()
        return None
    res = dict(row)
    issues_rows = conn.execute("SELECT * FROM detected_issues WHERE analysis_id = ? ORDER BY CASE severity WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END", (res["id"],)).fetchall()
    res["issues"] = [dict(i) for i in issues_rows]
    conn.close()
    return res

def update_submission_content(submission_id: str, new_text: str):
    conn = get_connection()
    now = get_current_timestamp()
    conn.execute("""
        UPDATE content_submissions
        SET content_text = ?, updated_at = ?
        WHERE id = ?
    """, (new_text, now, submission_id))
    conn.commit()
    conn.close()
    log_activity("EDIT", "Submission", submission_id, "Updated content text with corrections", "Editor")

def update_submission_review_status(submission_id: str, new_status: str, reviewer: str, comments: str = ""):
    conn = get_connection()
    now = get_current_timestamp()
    sub = conn.execute("SELECT review_status FROM content_submissions WHERE id = ?", (submission_id,)).fetchone()
    prev_status = sub["review_status"] if sub else "Draft"

    conn.execute("""
        UPDATE content_submissions
        SET review_status = ?, updated_at = ?
        WHERE id = ?
    """, (new_status, now, submission_id))

    # Add review history log
    conn.execute("""
        INSERT INTO review_records (submission_id, action, reviewer_name, comments, previous_status, new_status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (submission_id, f"STATUS_CHANGE_{new_status.upper()}", reviewer, comments, prev_status, new_status, now))

    conn.commit()
    conn.close()
    log_activity("REVIEW", "Submission", submission_id, f"Review status updated to '{new_status}' by {reviewer}", reviewer)

def get_review_history(submission_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM review_records WHERE submission_id = ? ORDER BY timestamp DESC", (submission_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==========================================
# Activity Logging
# ==========================================

def log_activity(event_type: str, entity_type: str, entity_id: str, description: str, user_name: str = "System"):
    try:
        conn = get_connection()
        now = get_current_timestamp()
        conn.execute("""
            INSERT INTO activity_logs (event_type, entity_type, entity_id, description, user_name, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event_type, entity_type, entity_id, description, user_name, now))
        conn.commit()
        conn.close()
    except Exception as e:
        # Avoid crashing primary operations if activity logging encounters lock
        print(f"Activity logging exception: {e}")

def get_recent_activities(limit: int = 15) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==========================================
# Dashboard Metrics & Aggregations
# ==========================================

def get_dashboard_metrics() -> Dict[str, Any]:
    conn = get_connection()
    total_checks = conn.execute("SELECT COUNT(*) as count FROM content_submissions").fetchone()["count"]
    flagged_claims = conn.execute("SELECT COUNT(*) as count FROM claims WHERE verification_status IN ('Pending Verification', 'Unsupported', 'Needs Reverification')").fetchone()["count"]
    pending_reviews = conn.execute("SELECT COUNT(*) as count FROM content_submissions WHERE review_status IN ('Submitted for Review', 'Changes Requested')").fetchone()["count"]
    approved_content = conn.execute("SELECT COUNT(*) as count FROM content_submissions WHERE review_status = 'Approved'").fetchone()["count"]

    # Severity distribution across all detected issues
    high_issues = conn.execute("SELECT COUNT(*) as count FROM detected_issues WHERE severity = 'High'").fetchone()["count"]
    med_issues = conn.execute("SELECT COUNT(*) as count FROM detected_issues WHERE severity = 'Medium'").fetchone()["count"]
    low_issues = conn.execute("SELECT COUNT(*) as count FROM detected_issues WHERE severity = 'Low'").fetchone()["count"]

    # Review status breakdown
    status_counts = {}
    for row in conn.execute("SELECT review_status, COUNT(*) as count FROM content_submissions GROUP BY review_status").fetchall():
        status_counts[row["review_status"]] = row["count"]

    # Claim verification status breakdown
    claim_counts = {}
    for row in conn.execute("SELECT verification_status, COUNT(*) as count FROM claims GROUP BY verification_status").fetchall():
        claim_counts[row["verification_status"]] = row["count"]

    conn.close()
    return {
        "total_checks": total_checks,
        "flagged_claims": flagged_claims,
        "pending_reviews": pending_reviews,
        "approved_content": approved_content,
        "issues_by_severity": {
            "High": high_issues,
            "Medium": med_issues,
            "Low": low_issues
        },
        "status_counts": status_counts,
        "claim_counts": claim_counts
    }
