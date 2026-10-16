"""Structured logging configuration.

The logger never emits secret values. Callers must avoid passing entire
environment dictionaries or API keys to log calls.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone

from utils.config import LOG_LEVEL


_SENSITIVE_KEYS = {"api_key", "password", "secret", "token", "authorization"}


def configure_logging():
    root = logging.getLogger("buildwithcrew")
    if root.handlers:
        return root

    level = getattr(logging, str(LOG_LEVEL).upper(), logging.INFO)
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            if record.__dict__.get("event_data"):
                payload["data"] = _redact(record.event_data)
            if record.exc_info:
                payload["exception"] = self.formatException(record.exc_info)
            return json.dumps(payload, default=str)

    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.propagate = False
    return root


def _redact(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, val in value.items():
            if str(key).lower() in _SENSITIVE_KEYS or "key" in str(key).lower():
                cleaned[key] = "***redacted***"
            else:
                cleaned[key] = _redact(val)
        return cleaned
    if isinstance(value, (list, tuple)):
        return [_redact(v) for v in value]
    return value


def get_logger(name):
    configure_logging()
    return logging.getLogger(f"buildwithcrew.{name}")


class SensitiveFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        # Best-effort guard; real protection is never calling with secrets.
        for secret_name in ("GROQ_API_KEY",):
            value = os.getenv(secret_name)
            if value and value in message:
                record.msg = message.replace(value, "***redacted***")
        return True