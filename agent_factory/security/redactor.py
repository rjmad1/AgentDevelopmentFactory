"""
Active Secret Redaction Engine for Logs, Traces, and Data Streams.
"""

import re
from typing import Any, Dict, List, Union


class SecretRedactor:
    """Detects and scrubs credentials, API tokens, and authorization headers from strings and structures."""

    PATTERNS = [
        (re.compile(r"sk-[a-zA-Z0-9\-_]{20,}", re.IGNORECASE), "[REDACTED_API_KEY]"),
        (re.compile(r"Bearer\s+[a-zA-Z0-9\._\-]{20,}", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
        (re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE), "[REDACTED_AWS_KEY]"),
        (re.compile(r"ghp_[a-zA-Z0-9]{36}", re.IGNORECASE), "[REDACTED_GITHUB_TOKEN]"),
        (re.compile(r"-----BEGIN[ A-Z0-9_-]+PRIVATE KEY-----[\s\S]*?-----END[ A-Z0-9_-]+PRIVATE KEY-----"), "[REDACTED_PRIVATE_KEY]"),
        (re.compile(r"(password|secret|token|api_key)\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE), r"\1: '[REDACTED]'"),
    ]

    @classmethod
    def redact_text(cls, text: str) -> str:
        if not text or not isinstance(text, str):
            return text
        redacted = text
        for pattern, replacement in cls.PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted

    @classmethod
    def redact_data(cls, data: Any) -> Any:
        if isinstance(data, str):
            return cls.redact_text(data)
        elif isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                if any(sec_term in k.lower() for sec_term in ["password", "secret", "token", "api_key", "auth"]):
                    new_dict[k] = "[REDACTED]"
                else:
                    new_dict[k] = cls.redact_data(v)
            return new_dict
        elif isinstance(data, list):
            return [cls.redact_data(item) for item in data]
        return data
