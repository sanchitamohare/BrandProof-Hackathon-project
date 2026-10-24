"""
BrandProof Governance Checking Engine
Provides explainable rule-based checks, claim passport cross-referencing,
risk scoring, and actionable correction suggestions.
"""
import re
from typing import List, Dict, Any, Tuple
try:
    from database.models import get_brand_rules, get_claims, generate_id
except (ImportError, ModuleNotFoundError):
    from models import get_brand_rules, get_claims, generate_id

def run_content_analysis(
    text: str,
    rules: List[Dict[str, Any]] = None,
    claims: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyzes marketing copy against active brand rules and cross-references Claim Passport.
    Returns structured analysis results, issue list, score, and revised copy suggestion.
    """
    if not text or not text.strip():
        return {
            "is_valid": False,
            "error": "Content is empty. Please enter marketing text to analyze."
        }

    if rules is None:
        rules = get_brand_rules(active_only=True)
    if claims is None:
        claims = get_claims()

    issues: List[Dict[str, Any]] = []
    text_lower = text.lower()
    revised_text = text

    # Step 1: Evaluate configured brand rules
    for rule in rules:
        pattern = rule.get("pattern_or_phrase", "")
        if not pattern:
            continue

        is_regex = bool(rule.get("is_regex", 0))
        matches = []

        try:
            if is_regex:
                for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                    matches.append((match.group(0), match.start(), match.end()))
            else:
                # Substring case-insensitive match
                sub_pattern = re.escape(pattern)
                for match in re.finditer(sub_pattern, text, flags=re.IGNORECASE):
                    matches.append((match.group(0), match.start(), match.end()))
        except re.error:
            # Fallback for invalid regex pattern in user-entered custom rule
            if pattern.lower() in text_lower:
                idx = text_lower.find(pattern.lower())
                matches.append((text[idx:idx+len(pattern)], idx, idx+len(pattern)))

        for matched_str, start_pos, end_pos in matches:
            # Cross-reference with Claim Passport if rule is Evidence Required
            evidence_status = "Not Required"
            reason = rule.get("explanation", "Matches flagged governance rule.")
            suggested_fix = rule.get("suggested_fix", "Review phrasing.")

            # Find surrounding sentence context for better Claim Passport matching
            sentence_start = max(0, text.rfind('.', 0, start_pos) + 1)
            sentence_end = text.find('.', end_pos)
            if sentence_end == -1:
                sentence_end = len(text)
            sentence_context = text[sentence_start:sentence_end].lower()

            # Search if any known claim relates to this excerpt or surrounding sentence
            matched_claim = None
            # Extract numbers/percentages from matched string
            numbers_in_match = set(re.findall(r"\b\d+[%xX]?\b", matched_str.lower()))

            for claim in claims:
                claim_text_lower = claim.get("claim_text", "").lower()
                numbers_in_claim = set(re.findall(r"\b\d+[%xX]?\b", claim_text_lower))
                
                # Check 1: Metric overlap (e.g. both contain 64% or 10x) and domain words in sentence
                if numbers_in_match and numbers_in_claim and (numbers_in_match & numbers_in_claim):
                    matched_claim = claim
                    break
                
                # Check 2: Excerpt directly contained in claim or vice versa
                if matched_str.lower() in claim_text_lower or claim_text_lower in sentence_context:
                    matched_claim = claim
                    break

                # Check 3: Significant shared words between claim and surrounding sentence
                claim_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", claim_text_lower))
                context_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", sentence_context))
                if len(claim_words & context_words) >= 2:
                    matched_claim = claim
                    break

            if matched_claim:
                status = matched_claim.get("verification_status", "Pending")
                evidence_status = f"{status} ({matched_claim.get('id')})"
                if status == "Verified":
                    reason = f"Numerical/factual claim aligns with Claim Passport {matched_claim.get('id')}, but requires proper attribution."
                    suggested_fix = f"Append citation: '(Source: {matched_claim.get('evidence_source', 'Verified Internal Study')})'"
                elif status == "Unsupported":
                    reason = f"Claim corresponds to known unsupported claim {matched_claim.get('id')}. Notes: {matched_claim.get('notes', 'No supporting data')}"
                    suggested_fix = "Remove or replace with non-absolute positioning."
                else:
                    reason = f"Claim corresponds to {matched_claim.get('id')} which is currently '{status}'. Legal substantiation pending."
                    suggested_fix = "Soften to general statement until verification completes."
            elif rule.get("category") == "Evidence Required":
                evidence_status = "Missing Passport Entry"
                reason = "Quantitative or comparative claim detected without a matching verified Claim Passport record."
                suggested_fix = "Register this claim in Claim Passport or add verified benchmark citation."

            issue = {
                "id": generate_id("ISS"),
                "rule_id": rule.get("id"),
                "title": rule.get("title", "Governance Notice"),
                "category": rule.get("category", "General"),
                "severity": rule.get("severity", "Medium"),
                "excerpt": matched_str,
                "reason": reason,
                "applicable_rule": f"{rule.get('id')}: {rule.get('title')}",
                "suggested_correction": suggested_fix,
                "evidence_status": evidence_status,
                "position_start": start_pos,
                "position_end": end_pos
            }
            issues.append(issue)

    # Deduplicate issues overlapping on exact same excerpt and rule
    unique_issues = []
    seen = set()
    for iss in issues:
        key = (iss["rule_id"], iss["excerpt"].lower())
        if key not in seen:
            seen.add(key)
            unique_issues.append(iss)

    # Calculate metrics
    high_count = sum(1 for i in unique_issues if i["severity"] == "High")
    med_count = sum(1 for i in unique_issues if i["severity"] == "Medium")
    low_count = sum(1 for i in unique_issues if i["severity"] == "Low")
    evidence_needed_count = sum(1 for i in unique_issues if "Missing" in i["evidence_status"] or "Unsupported" in i["evidence_status"] or "Pending" in i["evidence_status"])

    # Determine risk assessment
    if high_count > 0:
        risk_assessment = "High-Risk Content"
    elif med_count > 1:
        risk_assessment = "Needs Attention"
    elif med_count == 1 or low_count > 0:
        risk_assessment = "Needs Attention"
    else:
        risk_assessment = "Ready for Review"

    # Compute compliance score (0 - 100)
    score_deduction = (high_count * 25) + (med_count * 12) + (low_count * 5)
    compliance_score = max(0.0, min(100.0, 100.0 - score_deduction))

    # Generate smart revised content draft
    suggested_content = text
    # Apply standard fixes for known patterns
    for iss in unique_issues:
        excerpt = iss["excerpt"]
        correction = iss["suggested_correction"]
        # If correction specifies replacement phrase
        repl_match = re.search(r"Replace with ['\"]([^'\"]+)['\"]", correction, re.IGNORECASE)
        append_match = re.search(r"Append citation: ['\"]([^'\"]+)['\"]", correction, re.IGNORECASE)

        if repl_match:
            replacement = repl_match.group(1)
            suggested_content = re.sub(re.escape(excerpt), replacement, suggested_content, flags=re.IGNORECASE)
        elif append_match:
            citation = append_match.group(1)
            if citation not in suggested_content:
                suggested_content = re.sub(re.escape(excerpt), f"{excerpt} {citation}", suggested_content, flags=re.IGNORECASE)

    # Executive narrative summary
    if len(unique_issues) == 0:
        exec_summary = "Content conforms to all active brand rules and terminology guidelines. No unsupported or absolute claims detected."
    elif risk_assessment == "High-Risk Content":
        exec_summary = f"Identified {len(unique_issues)} governance findings ({high_count} High, {med_count} Medium). Critical risks include prohibited absolute claims or unverified financial guarantees. Human review required before publishing."
    else:
        exec_summary = f"Identified {len(unique_issues)} governance recommendations ({med_count} Medium, {low_count} Low). Includes wording optimizations and required claim citations."

    return {
        "is_valid": True,
        "risk_assessment": risk_assessment,
        "compliance_score": round(compliance_score, 1),
        "total_issues": len(unique_issues),
        "high_severity_count": high_count,
        "medium_severity_count": med_count,
        "low_severity_count": low_count,
        "evidence_needed_count": evidence_needed_count,
        "executive_summary": exec_summary,
        "suggested_content": suggested_content,
        "issues": unique_issues
    }
