# app/services/priority_service.py
import json
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.email import Email
from app.services.ai_provider_service import AIProviderService

logger = logging.getLogger(__name__)

PRIORITY_PROMPT_TEMPLATE = """
You are an assistant that evaluates email urgency and assigns a priority label.
Return a JSON object like:
{{"priority":"High","confidence":0.92}}

Priority levels: High, Medium, Low

Consider sender importance, keywords, deadlines, urgency wording, sentiment, and business impact.

Email content:
---BEGIN---
{content}
---END---
"""

def _call_selected_provider(db: Session, prompt: str) -> Optional[str]:
    provider_service = AIProviderService(db)
    provider = provider_service.get_primary_or_highest_priority()
    if not provider:
        raise RuntimeError("No AI provider configured")
    provider_type = provider.provider_type.lower()
    api_key = provider_service.get_decrypted_api_key(provider)
    try:
        if provider_type == "openai" or provider_type == "openai_compatible":
            import openai
            client = openai.OpenAI(api_key=api_key, base_url=provider.base_url)
            resp = client.chat.completions.create(
                model=provider.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            # try to extract content
            try:
                return resp.choices[0].message.content
            except Exception:
                try:
                    return resp.choices[0].text
                except Exception:
                    return None
        elif provider_type == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(provider.model)
            resp = model.generate_content(prompt)
            return getattr(resp, "text", None)
        elif provider_type == "claude":
            import anthropic
            client = anthropic.Client(api_key=api_key)
            resp = client.messages.create(model=provider.model, messages=[{"role":"user","content":prompt}])
            try:
                return resp.content[0].text
            except Exception:
                return None
        elif provider_type == "ollama":
            import requests
            base_url = provider.base_url or "http://localhost:11434"
            r = requests.post(f"{base_url}/api/generate", json={"model": provider.model, "prompt": prompt}, timeout=30)
            if r.status_code == 200:
                return r.text
            else:
                raise RuntimeError(f"Ollama returned {r.status_code}: {r.text}")
        else:
            raise RuntimeError(f"Unsupported AI provider type: {provider_type}")
    except Exception:
        logger.exception("AI provider call failed for priority classification")
        raise

def _safe_parse_priority(text: Optional[str]) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    txt = text.strip()
    # handle code-fence wrapping
    if txt.startswith("```"):
        parts = txt.split("```")
        if len(parts) >= 2:
            txt = parts[1].strip()
    try:
        parsed = json.loads(txt)
        if isinstance(parsed, dict) and parsed.get("priority"):
            return parsed
    except Exception:
        # try to find JSON object in text
        start = txt.find("{")
        end = txt.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(txt[start:end+1])
                if isinstance(parsed, dict) and parsed.get("priority"):
                    return parsed
            except Exception:
                pass
    return None

def _heuristic_priority(text: str, sender_email: Optional[str] = None) -> Dict[str, Any]:
    """Fallback heuristic to decide priority using keywords and crude sender checks."""
    text_low = (text or "").lower()
    # urgent keywords
    high_kw = ["urgent", "asap", "immediately", "critical", "right away", "do this now", "deadline", "due by"]
    medium_kw = ["please", "request", "follow up", "when you have time", "reminder"]
    low_kw = ["for your information", "fyi", "newsletter", "no action required", "update"]

    score_high = 0
    score_medium = 0
    score_low = 0

    for k in high_kw:
        if k in text_low:
            score_high += 2
    for k in medium_kw:
        if k in text_low:
            score_medium += 1
    for k in low_kw:
        if k in text_low:
            score_low += 1

    # Sender importance heuristic: treat common executive-role local-parts as
    # higher importance. This is a coarse signal — for real accuracy this
    # should eventually read from a configurable VIP sender/domain list
    # instead of hardcoded keywords.
    VIP_SENDER_MARKERS = ["ceo", "founder", "cto", "cfo", "coo", "vp", "president", "director"]
    if sender_email:
        local_part = sender_email.lower().split("@")[0]
        if any(marker in local_part for marker in VIP_SENDER_MARKERS):
            score_high += 2

    # decide
    if score_high >= 2:
        return {"priority": "High", "confidence": min(0.95, 0.6 + score_high * 0.1)}
    if score_medium >= 1:
        return {"priority": "Medium", "confidence": min(0.85, 0.5 + score_medium * 0.1)}
    if score_low >= 1:
        return {"priority": "Low", "confidence": 0.6}
    # default
    return {"priority": "Medium", "confidence": 0.45}

def classify_text_priority(text: str, db: Optional[Session] = None, sender_email: Optional[str] = None) -> Dict[str, Any]:
    """Return predicted priority and confidence for an arbitrary text (no persistence)."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        prompt = PRIORITY_PROMPT_TEMPLATE.format(content=text)
        try:
            raw = _call_selected_provider(db, prompt)
            parsed = _safe_parse_priority(raw)
            if parsed:
                # normalize values
                pr = parsed.get("priority", "Medium").title()
                conf = float(parsed.get("confidence", 0.0))
                return {"priority": pr, "confidence": conf}
        except Exception:
            logger.exception("AI priority classification failed, falling back to heuristics")
        # fallback heuristic — sender_email must be threaded through so the
        # VIP-sender boost actually has a chance to fire.
        return _heuristic_priority(text, sender_email=sender_email)
    finally:
        if close_db:
            db.close()

def classify_email_priority(email_id: str, db: Optional[Session] = None, persist: bool = True) -> Dict[str, Any]:
    """Classify an email by id, persist priority to emails table if persist=True."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        email = db.query(Email).filter(Email.id == email_id).one_or_none()
        if not email:
            raise ValueError("Email not found")
        parts = []
        if email.subject:
            parts.append(email.subject)
        if email.body_text:
            parts.append(email.body_text)
        if email.snippet:
            parts.append(email.snippet)
        content = "\n\n".join(parts)
        result = classify_text_priority(content, db=db, sender_email=email.sender_email)
        # Persist if requested
        if persist:
            # update fields
            email.priority = result.get("priority", "Medium")
            email.priority_confidence = float(result.get("confidence", 0.0))
            db.add(email)
            db.commit()
            db.refresh(email)
        return {"priority": email.priority if persist else result.get("priority"), "confidence": float(result.get("confidence", 0.0))}
    except Exception:
        db.rollback()
        raise
    finally:
        if close_db:
            db.close()