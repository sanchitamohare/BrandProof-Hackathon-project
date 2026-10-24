"""
Database connection and schema initialization for BrandProof
"""
import sqlite3
import os
from pathlib import Path
from settings import DB_PATH

def get_connection():
    """Get a connection to the SQLite database with Row factory."""
    db_file = Path(DB_PATH)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Create all database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Brand Profile
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brand_profiles (
        id INTEGER PRIMARY KEY,
        brand_name TEXT NOT NULL,
        tagline TEXT,
        voice_and_tone TEXT,
        industry TEXT,
        primary_disclaimer TEXT,
        updated_at TEXT
    );
    """)

    # 2. Brand Governance Rules
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brand_rules (
        id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        pattern_or_phrase TEXT NOT NULL,
        is_regex INTEGER DEFAULT 0,
        severity TEXT NOT NULL,
        explanation TEXT NOT NULL,
        suggested_fix TEXT,
        required_evidence_type TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );
    """)

    # 3. Claims (Claim Passport)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id TEXT PRIMARY KEY,
        claim_text TEXT NOT NULL,
        product_or_campaign TEXT NOT NULL,
        category TEXT NOT NULL,
        evidence_description TEXT,
        evidence_source TEXT,
        verification_status TEXT NOT NULL,
        owner TEXT NOT NULL,
        verified_date TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 4. Claim Audit History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claim_audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_id TEXT NOT NULL,
        action TEXT NOT NULL,
        changed_by TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE
    );
    """)

    # 5. Content Submissions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_submissions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content_type TEXT NOT NULL,
        campaign_name TEXT,
        content_text TEXT NOT NULL,
        description TEXT,
        policy_applied TEXT DEFAULT 'Standard Global Policy',
        risk_assessment TEXT DEFAULT 'Pending Analysis',
        review_status TEXT DEFAULT 'Draft',
        assigned_reviewer TEXT,
        author TEXT DEFAULT 'Demo Marketing Lead',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 6. Analysis Results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_results (
        id TEXT PRIMARY KEY,
        submission_id TEXT NOT NULL,
        total_issues INTEGER DEFAULT 0,
        high_severity_count INTEGER DEFAULT 0,
        medium_severity_count INTEGER DEFAULT 0,
        low_severity_count INTEGER DEFAULT 0,
        evidence_needed_count INTEGER DEFAULT 0,
        compliance_score REAL DEFAULT 100.0,
        executive_summary TEXT,
        suggested_content TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (submission_id) REFERENCES content_submissions(id) ON DELETE CASCADE
    );
    """)

    # 7. Detected Issues
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detected_issues (
        id TEXT PRIMARY KEY,
        analysis_id TEXT NOT NULL,
        rule_id TEXT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        excerpt TEXT NOT NULL,
        reason TEXT NOT NULL,
        applicable_rule TEXT,
        suggested_correction TEXT,
        evidence_status TEXT,
        position_start INTEGER DEFAULT 0,
        position_end INTEGER DEFAULT 0,
        FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE
    );
    """)

    # 8. Human Review Records & Approval Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS review_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id TEXT NOT NULL,
        action TEXT NOT NULL,
        reviewer_name TEXT NOT NULL,
        comments TEXT,
        previous_status TEXT,
        new_status TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (submission_id) REFERENCES content_submissions(id) ON DELETE CASCADE
    );
    """)

    # 9. Global Workspace Activity Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        description TEXT NOT NULL,
        user_name TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
