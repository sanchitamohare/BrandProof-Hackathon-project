"""
BrandProof Configuration & System Constants (Config package wrapper)
"""
try:
    from settings import *
except (ImportError, ModuleNotFoundError):
    import os
    from pathlib import Path

    if Path(__file__).resolve().parent.name == "config":
        BASE_DIR = Path(__file__).resolve().parent.parent
    else:
        BASE_DIR = Path(__file__).resolve().parent

    DB_PATH = os.environ.get("BRANDPROOF_DB_PATH", str(BASE_DIR / "brandproof.db"))

    APP_NAME = "BrandProof"
    APP_TAGLINE = "Trust Every Brand Claim."
    DEFAULT_WORKSPACE = "Apex Enterprise Brand Governance"
    VERSION = "1.0.0"

    THEME_COLORS = {
        "primary": "#0F172A",
        "brand": "#1E3A8A",
        "brand_light": "#3B82F6",
        "brand_pale": "#EFF6FF",
        "bg_main": "#F8FAFC",
        "bg_card": "#FFFFFF",
        "text_main": "#0F172A",
        "text_muted": "#64748B",
        "border": "#E2E8F0",
        "border_light": "#F1F5F9",
        "success": "#059669",
        "success_bg": "#ECFDF5",
        "warning": "#D97706",
        "warning_bg": "#FFFBEB",
        "danger": "#DC2626",
        "danger_bg": "#FEF2F2",
        "info": "#2563EB",
        "info_bg": "#EFF6FF"
    }

    CONTENT_TYPES = [
        "Advertisement",
        "Social Media Post",
        "Email Campaign",
        "Website Copy",
        "Product Description",
        "Press Release",
        "Whitepaper / Article",
        "Other"
    ]

    CLAIM_STATUSES = [
        "Verified",
        "Pending Verification",
        "Needs Reverification",
        "Unsupported"
    ]

    REVIEW_STATUSES = [
        "Draft",
        "Submitted for Review",
        "Changes Requested",
        "Approved",
        "Rejected"
    ]

    RISK_LEVELS = [
        "Ready for Review",
        "Needs Attention",
        "High-Risk Content"
    ]

    SEVERITY_LEVELS = [
        "Low",
        "Medium",
        "High"
    ]

    RULE_CATEGORIES = [
        "Prohibited Phrase",
        "Evidence Required",
        "Brand Terminology",
        "Required Disclaimer",
        "Tone & Superlative",
        "Regulatory Caution"
    ]
