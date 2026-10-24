"""
BrandProof Configuration & System Constants
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("BRANDPROOF_DB_PATH", str(BASE_DIR / "brandproof.db"))

# Brand Identity
APP_NAME = "BrandProof"
APP_TAGLINE = "Trust Every Brand Claim."
DEFAULT_WORKSPACE = "Apex Enterprise Brand Governance"
VERSION = "1.0.0"

# Color Palette (Subtle, calm, SaaS-focused)
THEME_COLORS = {
    "primary": "#0F172A",       # Deep navy/slate
    "brand": "#1E3A8A",         # Deep royal indigo
    "brand_light": "#3B82F6",   # Soft blue
    "brand_pale": "#EFF6FF",    # Very light blue accent
    "bg_main": "#F8FAFC",       # Warm off-white / light slate
    "bg_card": "#FFFFFF",       # Pure white card
    "text_main": "#0F172A",     # Charcoal text
    "text_muted": "#64748B",    # Muted slate grey
    "border": "#E2E8F0",        # Subtle border
    "border_light": "#F1F5F9",  # Ultra light border
    "success": "#059669",       # Muted emerald green
    "success_bg": "#ECFDF5",    # Green light background
    "warning": "#D97706",       # Warm amber
    "warning_bg": "#FFFBEB",    # Amber light background
    "danger": "#DC2626",        # Restrained crimson
    "danger_bg": "#FEF2F2",     # Crimson light background
    "info": "#2563EB",          # Crisp blue
    "info_bg": "#EFF6FF"        # Crisp blue light background
}

# Content Types
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

# Claim Verification Statuses
CLAIM_STATUSES = [
    "Verified",
    "Pending Verification",
    "Needs Reverification",
    "Unsupported"
]

# Review Workflow Statuses
REVIEW_STATUSES = [
    "Draft",
    "Submitted for Review",
    "Changes Requested",
    "Approved",
    "Rejected"
]

# Risk Classifications
RISK_LEVELS = [
    "Ready for Review",
    "Needs Attention",
    "High-Risk Content"
]

# Severity Levels
SEVERITY_LEVELS = [
    "Low",
    "Medium",
    "High"
]

# Rule Categories
RULE_CATEGORIES = [
    "Prohibited Phrase",
    "Evidence Required",
    "Brand Terminology",
    "Required Disclaimer",
    "Tone & Superlative",
    "Regulatory Caution"
]
