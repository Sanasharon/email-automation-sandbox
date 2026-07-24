import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ai_provider import AIProvider
from app.auth.encryption import encrypt_string, decrypt_string

logger = logging.getLogger("ai_provider_service")


class AIProviderService:
    def __init__(self, db: Session):
        self.db = db

    def get_providers(self, user_id: Optional[str] = None) -> List[AIProvider]:
        query = self.db.query(AIProvider).filter(AIProvider.is_enabled == True)
        if user_id:
            query = query.filter(AIProvider.user_id == user_id)
        return query.order_by(AIProvider.priority.desc(), AIProvider.created_at.desc()).all()

    def get_provider(self, provider_id: str) -> Optional[AIProvider]:
        return self.db.query(AIProvider).filter(AIProvider.id == provider_id).first()

    def get_decrypted_api_key(self, provider: AIProvider) -> Optional[str]:
        key = getattr(provider, 'api_key_encrypted', None) or getattr(provider, 'api_key', None)
        if not key:
            return None
        try:
            return decrypt_string(key)
        except Exception:
            return key

    def get_active_provider(self) -> Optional[AIProvider]:
        return self.db.query(AIProvider).filter(
            AIProvider.is_enabled == True,
            AIProvider.is_primary == True
        ).first()

    def get_primary_or_highest_priority(self) -> Optional[AIProvider]:
        primary = self.get_active_provider()
        if primary:
            return primary
        return self.db.query(AIProvider).filter(
            AIProvider.is_enabled == True
        ).order_by(AIProvider.priority.desc()).first()

    def create_provider(self, data: dict) -> AIProvider:
        if data.get("api_key_encrypted"):
            data["api_key_encrypted"] = encrypt_string(data["api_key_encrypted"])
        provider = AIProvider(**data)
        self.db.add(provider)
        if data.get("is_primary"):
            self._clear_other_primaries(provider.id)
        self.db.commit()
        self.db.refresh(provider)
        logger.info(f"Created AI provider: {provider.name} ({provider.provider_type})")
        return provider

    def update_provider(self, provider_id: str, data: dict) -> Optional[AIProvider]:
        provider = self.get_provider(provider_id)
        if not provider:
            return None
        if data.get("api_key_encrypted"):
            data["api_key_encrypted"] = encrypt_string(data["api_key_encrypted"])
        for key, value in data.items():
            if value is not None and hasattr(provider, key):
                setattr(provider, key, value)
        if data.get("is_primary"):
            self._clear_other_primaries(provider_id)
        self.db.commit()
        self.db.refresh(provider)
        logger.info(f"Updated AI provider: {provider.name}")
        return provider

    def delete_provider(self, provider_id: str) -> bool:
        provider = self.get_provider(provider_id)
        if not provider:
            return False
        self.db.delete(provider)
        self.db.commit()
        logger.info(f"Deleted AI provider: {provider.name}")
        return True

    def test_provider(self, provider_id: str) -> dict:
        provider = self.get_provider(provider_id)
        if not provider:
            return {"success": False, "error": "Provider not found"}
        try:
            if provider.provider_type == "openai":
                return self._test_openai(provider)
            elif provider.provider_type == "gemini":
                return self._test_gemini(provider)
            elif provider.provider_type == "claude":
                return self._test_claude(provider)
            elif provider.provider_type == "ollama":
                return self._test_ollama(provider)
            elif provider.provider_type == "openai_compatible":
                return self._test_openai_compatible(provider)
            else:
                return {"success": False, "error": f"Unsupported provider type: {provider.provider_type}"}
        except Exception as e:
            provider.status = "error"
            provider.last_error = str(e)
            self.db.commit()
            return {"success": False, "error": str(e)}

    def _clear_other_primaries(self, keep_id):
        self.db.query(AIProvider).filter(
            AIProvider.id != keep_id,
            AIProvider.is_primary == True
        ).update({"is_primary": False})

    def _test_openai(self, provider: AIProvider) -> dict:
        try:
            import openai
            api_key = self.get_decrypted_api_key(provider)
            client = openai.OpenAI(api_key=api_key, base_url=provider.base_url)
            response = client.chat.completions.create(
                model=provider.model,
                messages=[{"role": "user", "content": "Say 'Connection successful' in exactly 2 words."}],
                max_tokens=10
            )
            provider.status = "active"
            provider.last_error = None
            from datetime import datetime, timezone
            provider.last_tested_at = datetime.now(timezone.utc)
            self.db.commit()
            return {"success": True, "message": "Connection successful", "response": response.choices[0].message.content}
        except Exception as e:
            provider.status = "error"
            provider.last_error = str(e)
            self.db.commit()
            return {"success": False, "error": str(e)}

    def _test_gemini(self, provider: AIProvider) -> dict:
        try:
            import google.generativeai as genai
            api_key = self.get_decrypted_api_key(provider)
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(provider.model)
            response = model.generate_content("Say 'Connection successful'")
            provider.status = "active"
            provider.last_error = None
            from datetime import datetime, timezone
            provider.last_tested_at = datetime.now(timezone.utc)
            self.db.commit()
            return {"success": True, "message": "Connection successful", "response": response.text}
        except Exception as e:
            provider.status = "error"
            provider.last_error = str(e)
            self.db.commit()
            return {"success": False, "error": str(e)}

    def _test_claude(self, provider: AIProvider) -> dict:
        try:
            import anthropic
            api_key = self.get_decrypted_api_key(provider)
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=provider.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'Connection successful'"}]
            )
            provider.status = "active"
            provider.last_error = None
            from datetime import datetime, timezone
            provider.last_tested_at = datetime.now(timezone.utc)
            self.db.commit()
            return {"success": True, "message": "Connection successful", "response": response.content[0].text}
        except Exception as e:
            provider.status = "error"
            provider.last_error = str(e)
            self.db.commit()
            return {"success": False, "error": str(e)}

    def _test_ollama(self, provider: AIProvider) -> dict:
        try:
            import requests
            base_url = provider.base_url or "http://localhost:11434"
            resp = requests.get(f"{base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                provider.status = "active"
                provider.last_error = None
                from datetime import datetime, timezone
                provider.last_tested_at = datetime.now(timezone.utc)
                self.db.commit()
                return {"success": True, "message": "Ollama is running", "models": [m["name"] for m in resp.json().get("models", [])]}
            return {"success": False, "error": f"Ollama returned status {resp.status_code}"}
        except Exception as e:
            provider.status = "error"
            provider.last_error = str(e)
            self.db.commit()
            return {"success": False, "error": str(e)}

    def _test_openai_compatible(self, provider: AIProvider) -> dict:
        try:
            import openai
            api_key = self.get_decrypted_api_key(provider) or "dummy"
            client = openai.OpenAI(api_key=api_key, base_url=provider.base_url)
            response = client.chat.completions.create(
                model=provider.model,
                messages=[{"role": "user", "content": "Say 'Connection successful'"}],
                max_tokens=10
            )
            provider.status = "active"
            provider.last_error = None
            from datetime import datetime, timezone
            provider.last_tested_at = datetime.now(timezone.utc)
            self.db.commit()
            return {"success": True, "message": "Connection successful", "response": response.choices[0].message.content}
        except Exception as e:
            provider.status = "error"
            provider.last_error = str(e)
            self.db.commit()
            return {"success": False, "error": str(e)}
