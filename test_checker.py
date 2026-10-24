"""
Automated Unit and Integration Tests for BrandProof
Tests checking engine, database CRUD, workflow transitions, and reports.
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_connection
from database.seed_data import load_demo_data
from database.models import (
    get_brand_rules, get_claims, add_claim, update_claim,
    create_content_submission, get_submission_by_id,
    update_submission_review_status, get_dashboard_metrics
)
from modules.checker_engine import run_content_analysis
from modules.export_utils import export_to_csv, generate_html_compliance_report

class TestBrandProofCore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        load_demo_data(force_reload=True)

    def test_database_initialization(self):
        conn = get_connection()
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()
        expected = ["brand_profiles", "brand_rules", "claims", "content_submissions", "analysis_results", "detected_issues", "review_records", "activity_logs"]
        for t in expected:
            self.assertIn(t, tables, f"Expected table {t} missing from database")

    def test_idempotent_seeding(self):
        # Calling load_demo_data without force should return False and not create duplicates
        res = load_demo_data(force_reload=False)
        self.assertFalse(res, "Second load_demo_data call without force must not re-insert duplicate records")

    def test_rule_detection_high_risk(self):
        copy = "Our engine guarantees 100% risk-free return on investment and is unmatched by anyone."
        rules = get_brand_rules()
        claims = get_claims()
        result = run_content_analysis(copy, rules=rules, claims=claims)

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["risk_assessment"], "High-Risk Content")
        self.assertGreater(result["high_severity_count"], 0)
        self.assertIn("100% risk-free", [i["excerpt"].lower() for i in result["issues"]])

    def test_clean_content_validation(self):
        clean_copy = "We provide enterprise data workflows designed to support transparent brand management."
        rules = get_brand_rules()
        claims = get_claims()
        result = run_content_analysis(clean_copy, rules=rules, claims=claims)

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["risk_assessment"], "Ready for Review")
        self.assertEqual(result["high_severity_count"], 0)

    def test_claim_passport_matching(self):
        # Copy includes verified claim phrase '64% reduction in brand compliance audit time'
        copy = "Our platform achieves a 64% reduction in brand compliance audit time across enterprise cohorts."
        rules = get_brand_rules()
        claims = get_claims()
        result = run_content_analysis(copy, rules=rules, claims=claims)

        # Check if matched claim was identified
        evidence_statuses = [i.get("evidence_status", "") for i in result["issues"]]
        has_clm_match = any("CLM-801" in s for s in evidence_statuses)
        self.assertTrue(has_clm_match, "Should match registered Claim CLM-801")

    def test_review_workflow_transition(self):
        sub_id = create_content_submission({
            "title": "Automated Test Asset",
            "content_type": "Social Media Post",
            "content_text": "Sample test post text for workflow verification.",
            "review_status": "Draft"
        })
        # Advance to Submitted
        update_submission_review_status(sub_id, "Submitted for Review", "Author Marketer", "Ready for review")
        sub = get_submission_by_id(sub_id)
        self.assertEqual(sub["review_status"], "Submitted for Review")

        # Approve
        update_submission_review_status(sub_id, "Approved", "Sarah Lin (Brand Director)", "Looks solid")
        sub_after = get_submission_by_id(sub_id)
        self.assertEqual(sub_after["review_status"], "Approved")

    def test_csv_and_html_export(self):
        claims = get_claims()
        csv_bytes = export_to_csv(claims)
        self.assertGreater(len(csv_bytes), 50, "CSV bytes should contain serialized claim records")

        html_report = generate_html_compliance_report(
            {"title": "Test Report Asset", "content_type": "Advertisement", "campaign_name": "Test"},
            {"created_at": "2024-10-25", "compliance_score": 95, "executive_summary": "Passed all tests", "issues": []}
        )
        self.assertIn("Test Report Asset", html_report)
        self.assertIn("OFFICIAL COMPLIANCE REPORT", html_report)

    def test_dashboard_metrics(self):
        metrics = get_dashboard_metrics()
        self.assertIn("total_checks", metrics)
        self.assertIn("flagged_claims", metrics)
        self.assertIn("pending_reviews", metrics)
        self.assertIn("approved_content", metrics)
        self.assertGreaterEqual(metrics["total_checks"], 1)

    def test_ui_components_and_imports(self):
        from modules.ui_components import (
            get_risk_badge_html, get_severity_badge_html, get_status_badge_html
        )
        # Verify badges generate expected HTML without NameErrors
        for r in ["Ready for Review", "Needs Attention", "High-Risk Content"]:
            self.assertTrue(len(get_risk_badge_html(r)) > 0)
        for s in ["High", "Medium", "Low"]:
            self.assertTrue(len(get_severity_badge_html(s)) > 0)
        for st_val in ["Verified", "Pending Verification", "Unsupported", "Approved", "Rejected"]:
            self.assertTrue(len(get_status_badge_html(st_val)) > 0)

    def test_all_page_modules_load(self):
        # Ensure all 7 page modules and app.py import cleanly
        import modules.pages.overview as p_overview
        import modules.pages.content_checker as p_checker
        import modules.pages.claim_passport as p_passport
        import modules.pages.review_center as p_review
        import modules.pages.analytics as p_analytics
        import modules.pages.settings_page as p_settings
        import modules.pages.help_guide as p_help
        import app as bp_app
        self.assertTrue(hasattr(p_overview, "render_overview"))
        self.assertTrue(hasattr(p_checker, "render_content_checker"))
        self.assertTrue(hasattr(p_passport, "render_claim_passport"))
        self.assertTrue(hasattr(p_review, "render_review_center"))
        self.assertTrue(hasattr(p_analytics, "render_analytics"))
        self.assertTrue(hasattr(p_settings, "render_settings"))
        self.assertTrue(hasattr(p_help, "render_help_guide"))
        self.assertTrue(hasattr(bp_app, "main"))

if __name__ == "__main__":
    unittest.main()
