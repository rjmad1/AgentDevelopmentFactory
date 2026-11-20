"""
OmniRoute Gateway Model Adapter (OpenAI-compatible HTTP Interface).
"""

import json
from typing import Dict, Any, Optional
import urllib.request
import urllib.error

from agent_factory.adapters.base import ModelAdapter


class OmniRouteModelAdapter(ModelAdapter):
    """Adapter connecting to local OmniRoute gateway on port 20128."""

    def __init__(self, endpoint: str = "http://127.0.0.1:20128/v1", api_key: str = "local_omniroute_token", model: str = "hermes-reasoning"):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model

    def check_health(self) -> bool:
        try:
            req = urllib.request.Request(
                f"{self.endpoint}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return resp.status in (200, 201)
        except Exception:
            # Health check probe failed or unauthorized
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": (options or {}).get("model", self.model),
            "messages": messages,
            "temperature": (options or {}).get("temperature", 0.2),
            "max_tokens": (options or {}).get("max_tokens", 2048),
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.endpoint}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"OmniRoute HTTP {e.code}: {e.read().decode('utf-8', 'ignore')}")
        except Exception as e:
            raise RuntimeError(f"OmniRoute Gateway connection failed: {e}")
