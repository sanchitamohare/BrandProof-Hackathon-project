"""
Idempotent Demo Data Seeder for BrandProof
Ensures sample rules, claims, submissions, and reviews can be safely loaded without duplication.
"""
from database.db import get_connection, init_db
from database.models import (
    update_brand_profile, add_brand_rule, add_claim,
    create_content_submission, save_analysis_result,
    update_submission_review_status, log_activity, get_current_timestamp
)

DEMO_BRAND_PROFILE = {
    "brand_name": "Apex Horizon Technologies",
    "tagline": "Enterprise Precision. Uncompromising Trust.",
    "voice_and_tone": "Authoritative, accurate, evidence-backed, and empathetic. Strictly avoid hyperbolic absolutes (e.g. '100% risk-free', 'miracle', 'revolutionary') without verifiable empirical documentation.",
    "industry": "B2B Cloud & Marketing Intelligence",
    "primary_disclaimer": "Metrics and operational performance based on verified customer cohort benchmarks. Individual enterprise results may vary depending on existing workflow complexity.",
    "updated_at": get_current_timestamp()
}

DEMO_RULES = [
    {
        "id": "RULE-101",
        "category": "Prohibited Phrase",
        "title": "Absolute Risk-Free Claims",
        "pattern_or_phrase": r"\b(100%\s*risk[- ]?free|guaranteed\s*risk[- ]?free|zero\s*risk)\b",
        "is_regex": 1,
        "severity": "High",
        "explanation": "Absolute guarantees of zero financial or operational risk violate standard consumer protection regulations and company policy.",
        "suggested_fix": "Replace with qualified statements like 'low-friction onboarding' or 'backed by our 30-day satisfaction commitment'.",
        "required_evidence_type": "None (Absolute claims prohibited)"
    },
    {
        "id": "RULE-102",
        "category": "Evidence Required",
        "title": "Numerical Performance & ROI Claims",
        "pattern_or_phrase": r"\b(\d{1,3}%\s*(increase|boost|savings|reduction|faster|more|outperform)|\d+x\s*(faster|growth|roi|speed))\b",
        "is_regex": 1,
        "severity": "High",
        "explanation": "Any specific quantitative metric or multiplier claims (e.g., '10x faster', '64% reduction') must link to a verified Claim Passport record.",
        "suggested_fix": "Add verification reference or soften to 'demonstrated significant speed improvements in customer case studies'.",
        "required_evidence_type": "Empirical benchmark study or audited third-party trial"
    },
    {
        "id": "RULE-103",
        "category": "Prohibited Phrase",
        "title": "Unsubstantiated Superlatives",
        "pattern_or_phrase": r"\b(the\s+best\s+in\s+the\s+world|unmatched\s+by\s+anyone|miracle\s+solution|incomparable)\b",
        "is_regex": 1,
        "severity": "Medium",
        "explanation": "Broad superlatives without clear comparative criteria expose the brand to competitor dispute and regulatory scrutiny.",
        "suggested_fix": "Use defensible positioning such as 'industry-recognized' or 'ranked among leading solutions'.",
        "required_evidence_type": "Independent market evaluation (e.g. Gartner Magic Quadrant)"
    },
    {
        "id": "RULE-104",
        "category": "Brand Terminology",
        "title": "Deprecated Product Naming",
        "pattern_or_phrase": r"\b(Legacy\s*Cloud|Apex\s*V1|ApexClassic)\b",
        "is_regex": 1,
        "severity": "Medium",
        "explanation": "Older nomenclature confusing users. Always refer to our current enterprise line.",
        "suggested_fix": "Refer to 'Apex Horizon Platform' or 'Apex Enterprise Cloud'.",
        "required_evidence_type": "Brand style guide nomenclature"
    },
    {
        "id": "RULE-105",
        "category": "Required Disclaimer",
        "title": "Forward-Looking Financial Statement",
        "pattern_or_phrase": r"\b(revenue\s*growth|guaranteed\s*roi|profit\s*multiplication)\b",
        "is_regex": 1,
        "severity": "High",
        "explanation": "Discussing ROI or future revenue requires standard forward-looking and disclaimer notices.",
        "suggested_fix": "Include standard footnote: 'Projections are illustrative and not a guarantee of financial outcomes.'",
        "required_evidence_type": "Legal compliance disclaimer"
    },
    {
        "id": "RULE-106",
        "category": "Tone & Superlative",
        "title": "Hyperbolic Buzzwords",
        "pattern_or_phrase": r"\b(revolutionary\s*breakthrough|game-changing\s*magic|effortless\s*wealth)\b",
        "is_regex": 1,
        "severity": "Low",
        "explanation": "Overused sensationalism detracts from our authoritative, enterprise-grade brand voice.",
        "suggested_fix": "Rephrase using precise value propositions: 'automated workflow optimization'.",
        "required_evidence_type": "Brand tone guidelines"
    }
]

DEMO_CLAIMS = [
    {
        "id": "CLM-801",
        "claim_text": "Reduces brand compliance audit time by up to 64%",
        "product_or_campaign": "Apex Horizon Platform",
        "category": "Performance & Speed",
        "evidence_description": "2024 Customer Benchmarking Study of 45 enterprise marketing teams, audited by Forrester Consulting.",
        "evidence_source": "Forrester TEI Benchmark Report, Oct 2024, Ref #FOR-2024-882",
        "verification_status": "Verified",
        "owner": "Sarah Lin (Brand Director)",
        "notes": "Annual reverification scheduled for November 2025."
    },
    {
        "id": "CLM-802",
        "claim_text": "Processes over 50,000 marketing assets monthly with 99.9% uptime",
        "product_or_campaign": "Apex Horizon Platform",
        "category": "Product Quality & Composition",
        "evidence_description": "Datadog production cluster logs & AWS CloudWatch Q3 2024 SLA audit.",
        "evidence_source": "Internal Infrastructure SLA Portal https://status.apexhorizon.internal",
        "verification_status": "Verified",
        "owner": "DevOps / Reliability Team",
        "notes": "Confirmed zero high-severity downtime in past 180 days."
    },
    {
        "id": "CLM-803",
        "claim_text": "SOC 2 Type II and ISO 27001 Certified Security Infrastructure",
        "product_or_campaign": "General Brand",
        "category": "Safety & Compliance",
        "evidence_description": "Independent auditor examination report confirming trust services criteria.",
        "evidence_source": "Schellman Compliance Audit Certificate #SC-2024-8891",
        "verification_status": "Verified",
        "owner": "Marcus Vance (Chief Security Officer)",
        "notes": "Valid through January 2026."
    },
    {
        "id": "CLM-804",
        "claim_text": "Guarantees 100% risk-free return on marketing spend",
        "product_or_campaign": "Q4 Growth Campaign",
        "category": "Financial & ROI",
        "evidence_description": "None provided. Flagged by Legal as an unenforceable and high-risk warranty.",
        "evidence_source": "Pending legal review",
        "verification_status": "Unsupported",
        "owner": "Growth Marketing Squad",
        "notes": "Must be removed from all upcoming social and email collateral."
    },
    {
        "id": "CLM-805",
        "claim_text": "Delivers 10x faster review cycles than legacy manual processes",
        "product_or_campaign": "Apex Review Center",
        "category": "Comparative / Superiority",
        "evidence_description": "Beta pilot data from 12 early adopters. Requires larger sample size for external claims.",
        "evidence_source": "Q2 Beta Telemetry Analysis, Apex Product Ops",
        "verification_status": "Pending Verification",
        "owner": "Elena Rostova (Product Marketing)",
        "notes": "Waiting for expanded cohort data before approving public marketing release."
    }
]

def load_demo_data(force_reload: bool = False) -> bool:
    """
    Safely seeds demo data into the database.
    If data already exists and force_reload is False, skips to prevent duplication.
    """
    init_db()
    conn = get_connection()

    existing_rules = conn.execute("SELECT COUNT(*) as count FROM brand_rules").fetchone()["count"]
    if existing_rules > 0 and not force_reload:
        conn.close()
        return False  # Already seeded

    if force_reload:
        # Clear existing tables safely
        tables = ["detected_issues", "analysis_results", "review_records",
                  "claim_audit_logs", "claims", "content_submissions", "brand_rules", "activity_logs"]
        for t in tables:
            conn.execute(f"DELETE FROM {t}")
        conn.commit()

    conn.close()

    # 1. Seed Brand Profile
    update_brand_profile(DEMO_BRAND_PROFILE)

    # 2. Seed Rules
    for rule in DEMO_RULES:
        add_brand_rule(rule)

    # 3. Seed Claims
    for claim in DEMO_CLAIMS:
        add_claim(claim)

    # 4. Seed Submissions & Analyses
    # Sample 1: A submission with flagged issues (Needs Attention)
    sub1_id = create_content_submission({
        "id": "SUB-DEMO-01",
        "title": "Apex Horizon Q4 Enterprise Launch Copy",
        "content_type": "Email Campaign",
        "campaign_name": "Q4 Enterprise Launch",
        "content_text": (
            "Experience revolutionary breakthrough with the Apex Horizon Platform! "
            "Our revolutionary AI engine guarantees 100% risk-free return on marketing spend and is unmatched by anyone. "
            "Customers experience a 64% reduction in brand compliance audit time with zero risk. "
            "Upgrade your Legacy Cloud today."
        ),
        "description": "Email draft targeting VP of Marketing persona for Q4 promotion.",
        "policy_applied": "Apex Standard Global Policy",
        "risk_assessment": "High-Risk Content",
        "review_status": "Changes Requested",
        "assigned_reviewer": "Sarah Lin (Brand Director)",
        "author": "David Chen (Copywriter)"
    })

    issues1 = [
        {
            "id": "ISS-DEMO-101",
            "rule_id": "RULE-101",
            "title": "Absolute Risk-Free Claim Detected",
            "category": "Prohibited Phrase",
            "severity": "High",
            "excerpt": "guarantees 100% risk-free",
            "reason": "Absolute statements regarding risk-free financial returns violate governance policies.",
            "applicable_rule": "RULE-101: Absolute Risk-Free Claims",
            "suggested_correction": "Replace with 'backed by our enterprise SLA and satisfaction commitment'",
            "evidence_status": "Unsupported"
        },
        {
            "id": "ISS-DEMO-102",
            "rule_id": "RULE-102",
            "title": "Performance Claim Match Found",
            "category": "Evidence Required",
            "severity": "Medium",
            "excerpt": "64% reduction in brand compliance audit time",
            "reason": "Metric claim found in content. Matches Claim Passport CLM-801.",
            "applicable_rule": "RULE-102: Numerical Performance & ROI Claims",
            "suggested_correction": "Cite source: '(Source: Forrester TEI Benchmark Report, 2024)'",
            "evidence_status": "Verified (CLM-801)"
        },
        {
            "id": "ISS-DEMO-103",
            "rule_id": "RULE-103",
            "title": "Unsubstantiated Superlative",
            "category": "Prohibited Phrase",
            "severity": "Medium",
            "excerpt": "unmatched by anyone",
            "reason": "Superlative lacks audited third-party comparative study.",
            "applicable_rule": "RULE-103: Unsubstantiated Superlatives",
            "suggested_correction": "Replace with 'recognized by industry analysts for advanced governance'",
            "evidence_status": "Unsupported"
        },
        {
            "id": "ISS-DEMO-104",
            "rule_id": "RULE-104",
            "title": "Deprecated Nomenclature Used",
            "category": "Brand Terminology",
            "severity": "Medium",
            "excerpt": "Legacy Cloud",
            "reason": "Deprecated product name. Brand guidelines specify Apex Horizon Platform.",
            "applicable_rule": "RULE-104: Deprecated Product Naming",
            "suggested_correction": "Replace with 'Apex Horizon Platform'",
            "evidence_status": "Not Required"
        }
    ]

    save_analysis_result({
        "id": "ANL-DEMO-01",
        "submission_id": sub1_id,
        "total_issues": len(issues1),
        "high_severity_count": 1,
        "medium_severity_count": 3,
        "low_severity_count": 0,
        "evidence_needed_count": 2,
        "compliance_score": 62.5,
        "executive_summary": "High-risk draft containing absolute risk claims ('100% risk-free') and deprecated terminology ('Legacy Cloud'). Verified metric 64% reduction requires citation.",
        "suggested_content": (
            "Experience advanced workflow intelligence with the Apex Horizon Platform! "
            "Our platform is recognized by industry analysts for precision brand governance. "
            "Enterprise customers achieve up to a 64% reduction in brand compliance audit time (Source: Forrester TEI Report, 2024). "
            "Upgrade your Apex Horizon Platform today."
        ),
        "risk_assessment": "High-Risk Content"
    }, issues1)

    update_submission_review_status(
        sub1_id,
        "Changes Requested",
        "Sarah Lin (Brand Director)",
        "Please remove the '100% risk-free' phrase and add the Forrester citation for the 64% claim before sending to prospects."
    )

    # Sample 2: An Approved compliant submission
    sub2_id = create_content_submission({
        "id": "SUB-DEMO-02",
        "title": "Enterprise Trust & Security Overview",
        "content_type": "Website Copy",
        "campaign_name": "Trust Center 2024",
        "content_text": (
            "Apex Horizon provides enterprise-grade brand governance powered by audited infrastructure. "
            "Backed by SOC 2 Type II and ISO 27001 certifications, our platform ensures rigorous data privacy "
            "and operational integrity across global marketing workflows."
        ),
        "description": "Copy for security landing page.",
        "policy_applied": "Apex Standard Global Policy",
        "risk_assessment": "Ready for Review",
        "review_status": "Approved",
        "assigned_reviewer": "Marcus Vance (CSO)",
        "author": "Elena Rostova (Product Marketing)"
    })

    save_analysis_result({
        "id": "ANL-DEMO-02",
        "submission_id": sub2_id,
        "total_issues": 0,
        "high_severity_count": 0,
        "medium_severity_count": 0,
        "low_severity_count": 0,
        "evidence_needed_count": 0,
        "compliance_score": 98.0,
        "executive_summary": "Clean, compliant copy. All certifications align with verified Claim Passport records (CLM-803). No prohibited phrases detected.",
        "suggested_content": "No corrections required. Ready for production publication.",
        "risk_assessment": "Ready for Review"
    }, [])

    update_submission_review_status(
        sub2_id,
        "Approved",
        "Marcus Vance (CSO)",
        "Security claims verified against active audit certificates. Approved for website deployment."
    )

    log_activity("SYSTEM", "Workspace", "DEMO", "Sample demo workspace initialized successfully", "System Seeder")
    return True

if __name__ == "__main__":
    load_demo_data(force_reload=True)
    print("Demo data seeded successfully.")
