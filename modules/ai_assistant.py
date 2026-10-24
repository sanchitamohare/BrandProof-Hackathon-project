"""
Optional AI Assistant Integration for BrandProof
Supports external LLM rewriting and advanced reasoning when configured.
Transparently falls back to deterministic rule engine when unconfigured.
"""
import os
import json
from typing import Dict, Any, Optional

def get_ai_status() -> Dict[str, Any]:
    """Check whether an external AI provider is configured."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    provider = os.environ.get("AI_PROVIDER", "none").strip()

    if api_key:
        return {
            "configured": True,
            "provider": "OpenAI / Compatible API",
            "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            "status_text": "Connected (AI Deep Reasoning Enabled)"
        }
    return {
        "configured": False,
        "provider": "None",
        "model": "Deterministic Rule Engine",
        "status_text": "Not Configured — Using 100% Deterministic Rule Engine"
    }

def request_ai_enhancement(
    text: str,
    issues: list,
    brand_tone: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Requests optional AI enhancement if key is provided.
    Never fabricates fake results.
    """
    key = api_key or os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return {
            "success": False,
            "mode": "rule_based_fallback",
            "message": "No external AI API key configured. Utilizing local BrandProof deterministic rule engine.",
            "enhanced_text": None,
            "ai_insights": None
        }

    # Attempt OpenAI API call if `requests` or `openai` is available
    try:
        import urllib.request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        prompt = (
            f"You are BrandProof Governance Assistant. Revise the following marketing copy to strictly resolve "
            f"these detected governance violations:\n"
            f"{json.dumps([{'rule': i.get('applicable_rule'), 'excerpt': i.get('excerpt'), 'suggestion': i.get('suggested_correction')} for i in issues])}\n\n"
            f"Brand tone requirement: {brand_tone}\n\n"
            f"Original Copy:\n\"{text}\"\n\n"
            f"Provide a JSON response with keys 'revised_copy' (string) and 'explanation' (string)."
        )
        payload = json.dumps({
            "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": "You are a brand compliance editor. Respond strictly in JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }).encode("utf-8")

        req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            content = res_data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return {
                "success": True,
                "mode": "ai_enhanced",
                "message": "AI analysis and rewriting completed via configured API.",
                "enhanced_text": parsed.get("revised_copy", text),
                "ai_insights": parsed.get("explanation", "Rewritten for compliance.")
            }
    except Exception as e:
        return {
            "success": False,
            "mode": "api_error",
            "message": f"External AI request could not be completed ({str(e)}). Falling back to rule-based engine.",
            "enhanced_text": None,
            "ai_insights": None
        }
