"""
Export and Compliance Report Generation Utilities for BrandProof
"""
import io
import pandas as pd
from typing import List, Dict, Any

def export_to_csv(data: List[Dict[str, Any]]) -> bytes:
    """Converts a list of dicts into downloadable CSV bytes."""
    if not data:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

def generate_html_compliance_report(submission: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    """
    Generates a standalone, beautifully styled HTML Compliance Audit Certificate / Report
    suitable for immediate browser viewing and printing to PDF.
    """
    sub_title = submission.get("title", "Marketing Content Analysis")
    sub_type = submission.get("content_type", "General")
    campaign = submission.get("campaign_name", "Global")
    risk = submission.get("risk_assessment", "Pending")
    status = submission.get("review_status", "Draft")
    date = analysis.get("created_at", "N/A")
    score = analysis.get("compliance_score", 100.0)
    summary = analysis.get("executive_summary", "No issues detected.")
    suggested = analysis.get("suggested_content", "")
    original = submission.get("content_text", "")
    issues = analysis.get("issues", [])

    issues_html = ""
    if not issues:
        issues_html = "<p style='color: #059669; font-weight: 600;'>No governance violations detected. Content complies with brand policy.</p>"
    else:
        for idx, iss in enumerate(issues, 1):
            sev_color = "#DC2626" if iss.get("severity") == "High" else ("#D97706" if iss.get("severity") == "Medium" else "#2563EB")
            issues_html += f"""
            <div style="border-left: 4px solid {sev_color}; background-color: #F8FAFC; padding: 12px 16px; margin-bottom: 12px; border-radius: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <strong style="color: #0F172A; font-size: 14px;">#{idx}. {iss.get('title')}</strong>
                    <span style="font-size: 11px; font-weight: 700; color: {sev_color}; background: #FFF; border: 1px solid {sev_color}; padding: 2px 6px; border-radius: 4px;">{iss.get('severity').upper()}</span>
                </div>
                <div style="font-size: 13px; color: #334155; margin-bottom: 4px;"><strong>Flagged Excerpt:</strong> <span style="background: #FEF08A; padding: 2px 4px; border-radius: 3px;">"{iss.get('excerpt')}"</span></div>
                <div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><strong>Governance Reason:</strong> {iss.get('reason')}</div>
                <div style="font-size: 13px; color: #0284C7; margin-bottom: 4px;"><strong>Applicable Policy:</strong> {iss.get('applicable_rule')}</div>
                <div style="font-size: 13px; color: #065F46;"><strong>Recommended Action:</strong> {iss.get('suggested_correction')}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;"><strong>Evidence Status:</strong> {iss.get('evidence_status', 'N/A')}</div>
            </div>
            """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BrandProof Compliance Audit - {sub_title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #0F172A;
            background-color: #FFFFFF;
            margin: 0;
            padding: 40px;
            font-size: 14px;
            line-height: 1.5;
        }}
        .report-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0F172A;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .brand-logo {{
            font-size: 22px;
            font-weight: 800;
            color: #1E3A8A;
            letter-spacing: -0.02em;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            background: #F8FAFC;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #E2E8F0;
            margin-bottom: 24px;
        }}
        .meta-item strong {{
            display: block;
            font-size: 11px;
            text-transform: uppercase;
            color: #64748B;
            margin-bottom: 4px;
        }}
        .meta-item span {{
            font-size: 14px;
            font-weight: 600;
            color: #0F172A;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #0F172A;
            border-bottom: 1px solid #E2E8F0;
            padding-bottom: 6px;
            margin-top: 24px;
            margin-bottom: 12px;
        }}
        .copy-box {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            padding: 14px;
            border-radius: 6px;
            white-space: pre-wrap;
            font-family: inherit;
        }}
        .footer {{
            margin-top: 40px;
            border-top: 1px solid #E2E8F0;
            padding-top: 16px;
            font-size: 11px;
            color: #94A3B8;
            display: flex;
            justify-content: space-between;
        }}
        @media print {{
            body {{ padding: 20px; }}
            button {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <div>
            <div class="brand-logo">BrandProof</div>
            <div style="font-size: 12px; color: #64748B;">AI-Powered Brand Governance & Claim Verification</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 12px; font-weight: 600; color: #475569;">OFFICIAL COMPLIANCE REPORT</div>
            <div style="font-size: 11px; color: #94A3B8;">Generated: {date}</div>
        </div>
    </div>

    <div class="meta-grid">
        <div class="meta-item">
            <strong>Content Asset</strong>
            <span>{sub_title}</span>
        </div>
        <div class="meta-item">
            <strong>Asset Type / Campaign</strong>
            <span>{sub_type} ({campaign})</span>
        </div>
        <div class="meta-item">
            <strong>Risk Assessment</strong>
            <span>{risk}</span>
        </div>
        <div class="meta-item">
            <strong>Compliance Score</strong>
            <span>{score} / 100</span>
        </div>
    </div>

    <div class="section-title">Executive Governance Summary</div>
    <p style="color: #334155; font-size: 14px;">{summary}</p>

    <div class="section-title">Detected Issues & Actionable Corrections ({len(issues)})</div>
    {issues_html}

    <div class="section-title">Original Marketing Copy Submitted</div>
    <div class="copy-box">{original}</div>

    <div class="section-title">Suggested Compliant Revision</div>
    <div class="copy-box" style="border-left: 3px solid #059669;">{suggested if suggested else "No changes required."}</div>

    <div class="footer">
        <span>BrandProof Enterprise Governance Platform • Audit Certificate</span>
        <span>Confidential & Internal Compliance Reference</span>
    </div>
</body>
</html>
"""
    return html
