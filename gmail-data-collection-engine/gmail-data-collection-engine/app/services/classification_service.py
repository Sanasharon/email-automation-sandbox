# app/services/classification_service.py
import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.email import Email
from app.models.category import Category
from app.models.email_category import EmailCategory
from app.services.ai_provider_service import AIProviderService

logger = logging.getLogger(__name__)

# Prompt template - you can refine these prompts in prompt_templates table later
CLASSIFICATION_PROMPT_TEMPLATE = """
You are an assistant that classifies email text into business categories.
Return a JSON array (no extra text) of objects like:
[{{"category":"Support","confidence":0.92}}, ...]

Categories to consider: Sales, Support, Billing, HR, General

Email content:
---BEGIN---
{content}
---END---
"""

def _extract_text_from_openai_response(resp):
    # openai-like responses: response.choices[0].message.content
    try:
        return resp.choices[0].message.content
    except Exception:
        # older SDKs may use resp.choices[0].text
        try:
            return resp.choices[0].text
        except Exception:
            return None

def _extract_text_from_gemini(resp):
    try:
        return getattr(resp, "text", None) or resp.text
    except Exception:
        return None

def _extract_text_from_claude(resp):
    try:
        # anthopic/claude response shape
        return resp.content[0].text
    except Exception:
        # fallback
        return None

def _extract_text_from_ollama(resp):
    try:
        # Ollama typically returns JSON or plain text in resp.text
        return resp.text
    except Exception:
        return None

def _safe_parse_json(text: str) -> Optional[List[Dict[str, Any]]]:
    if not text:
        return None
    # Trim and attempt to extract JSON substring
    txt = text.strip()
    # If contains backticks or code fences, strip them
    if txt.startswith("```"):
        # remove possible code fence wrappers
        parts = txt.split("```")
        if len(parts) >= 2:
            txt = parts[1].strip()
    # Try json.loads
    try:
        parsed = json.loads(txt)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        # try to find first '[' .. ']' substring
        start = txt.find("[")
        end = txt.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(txt[start:end+1])
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
    return None

def _fallback_keyword_classify(text: str) -> List[Dict[str, Any]]:
    """Simple keyword fallback classifier in case AI fails to return JSON."""
    text_low = (text or "").lower()
    scores = []
    # simple heuristics
    if any(k in text_low for k in ["invoice", "payment", "bill", "amount due"]):
        scores.append({"category": "Billing", "confidence": 0.9})
    if any(k in text_low for k in ["support", "help", "issue", "ticket", "error"]):
        scores.append({"category": "Support", "confidence": 0.85})
    if any(k in text_low for k in ["pricing", "quote", "purchase", "order"]):
        scores.append({"category": "Sales", "confidence": 0.8})
    if any(k in text_low for k in ["resume", "interview", "hr", "hiring", "candidate"]):
        scores.append({"category": "HR", "confidence": 0.8})
    # fallback general
    if not scores:
        scores.append({"category": "General", "confidence": 0.6})
    return scores

def _call_selected_provider(db: Session, prompt: str) -> Optional[str]:
    """
    Pick an AI provider from DB and call it. Returns raw text output.
    """
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
                max_tokens=400
            )
            return _extract_text_from_openai_response(resp)
        elif provider_type == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(provider.model)
            resp = model.generate_content(prompt)
            return _extract_text_from_gemini(resp)
        elif provider_type == "claude":
            import anthropic
            client = anthropic.Client(api_key=api_key)
            # Using messages.create pattern or similar depending on anthropic SDK version
            resp = client.messages.create(model=provider.model, messages=[{"role":"user","content":prompt}])
            return _extract_text_from_claude(resp)
        elif provider_type == "ollama":
            import requests
            base_url = provider.base_url or "http://localhost:11434"
            # Ollama may expect a JSON payload; adapt if your Ollama endpoint different
            r = requests.post(f"{base_url}/api/generate", json={"model": provider.model, "prompt": prompt}, timeout=30)
            if r.status_code == 200:
                return r.text
            else:
                raise RuntimeError(f"Ollama returned {r.status_code}: {r.text}")
        else:
            raise RuntimeError(f"Unsupported AI provider type: {provider_type}")
    except Exception as exc:
        logger.exception("AI provider call failed: %s", exc)
        raise

def classify_text(text: str, db: Optional[Session] = None, top_k: int = 3) -> List[Dict[str, Any]]:
    """Return list of {category, confidence} predictions without persisting."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(content=text)
        try:
            raw = _call_selected_provider(db, prompt)
            parsed = _safe_parse_json(raw)
            if parsed:
                # normalize confidences to float
                out = []
                for item in parsed[:top_k]:
                    cat = item.get("category") or item.get("label") or item.get("name")
                    conf = float(item.get("confidence") or item.get("score") or 0.0)
                    out.append({"category": cat, "confidence": conf})
                if out:
                    return out
        except Exception:
            logger.exception("AI classification failed, falling back to keyword classifier")

        # Fallback keyword classifier
        return _fallback_keyword_classify(text)[:top_k]
    finally:
        if close_db:
            db.close()

def classify_email(email_id: str, db: Optional[Session] = None, assigned_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """Classify an email by id, persist email_categories, and return persisted results."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        email = db.query(Email).filter(Email.id == email_id).one_or_none()
        if not email:
            raise ValueError("Email not found")

        text_parts = []
        if email.subject:
            text_parts.append(email.subject)
        if email.body_text:
            text_parts.append(email.body_text)
        if email.snippet:
            text_parts.append(email.snippet)
        content = "\n\n".join(text_parts)

        predictions = classify_text(content, db=db, top_k=3)

        persisted = []
        for p in predictions:
            category_name = (p.get("category") or "").strip()
            if not category_name:
                continue
            confidence = float(p.get("confidence", 0.0))
            # find or create category
            cat = db.query(Category).filter(Category.name.ilike(category_name)).one_or_none()
            if not cat:
                # create normalized category name (capitalize)
                cat = Category(name=category_name.title(), description=None)
                db.add(cat)
                db.flush()  # ensure id populated
            # upsert email_category association
            assoc = (
                db.query(EmailCategory)
                .filter(EmailCategory.email_id == email.id, EmailCategory.category_id == cat.id)
                .one_or_none()
            )
            if not assoc:
                assoc = EmailCategory(email_id=email.id, category_id=cat.id, confidence=confidence, assigned_by=assigned_by)
                db.add(assoc)
            else:
                assoc.confidence = confidence
                if assigned_by:
                    assoc.assigned_by = assigned_by
            persisted.append({
                "category": cat.name,
                "category_id": str(cat.id),
                "confidence": confidence
            })
        db.commit()
        return persisted
    except Exception:
        db.rollback()
        raise
    finally:
        if close_db:
            db.close()