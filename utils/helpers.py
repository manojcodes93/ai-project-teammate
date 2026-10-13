import os
import sqlite3
import time
from contextlib import closing
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    Groq,
    RateLimitError,
)

load_dotenv()

# Resolve the project root regardless of the current working directory so the
# database always lives in the same place.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "history.db")

DEFAULT_MODEL = "openai/gpt-oss-120b"
REQUEST_TIMEOUT = 60.0
MAX_TOKENS = 8192
TEMPERATURE = 0.7
REASONING_EFFORT = "low"
MAX_RETRIES = 3
RETRY_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


def _secret(key):
    """Read a Streamlit secret, tolerating a missing secrets file."""
    try:
        return st.secrets.get(key)
    except Exception:
        return None


def _resolve_model():
    return _secret("GROQ_MODEL") or os.getenv("GROQ_MODEL") or DEFAULT_MODEL


def _resolve_int(name, default):
    raw = _secret(name) or os.getenv(name)
    try:
        return int(raw) if raw is not None else default
    except (TypeError, ValueError):
        return default


def _resolve_float(name, default):
    raw = _secret(name) or os.getenv(name)
    try:
        return float(raw) if raw is not None else default
    except (TypeError, ValueError):
        return default


def _resolve_reasoning_effort():
    """Return the reasoning effort to send, or None to omit the parameter."""
    raw = _secret("GROQ_REASONING_EFFORT")
    if raw is None:
        raw = os.getenv("GROQ_REASONING_EFFORT")
    if raw is None:
        raw = REASONING_EFFORT
    raw = str(raw).strip()
    if raw.lower() in {"", "off", "false"}:
        return None
    return raw


def get_client():
    """Create a Groq client, raising a clear error when the key is missing."""
    api_key = _secret("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Add it to your environment (.env) or "
            "Streamlit secrets."
        )

    return Groq(api_key=api_key, timeout=REQUEST_TIMEOUT)


def _create_completion(client, **kwargs):
    """Create a chat completion, retrying transient/rate-limit failures."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            return client.chat.completions.create(**kwargs)
        except (RateLimitError, APIConnectionError, APITimeoutError) as exc:
            last_error = exc
        except APIStatusError as exc:
            if getattr(exc, "status_code", None) not in RETRY_STATUS_CODES:
                raise
            last_error = exc

        if attempt < MAX_RETRIES - 1:
            time.sleep(2 ** attempt)

    raise last_error


def get_ai_response(system_prompt, user_input, model=None):
    """Call the LLM. Raises on failure so callers can surface a real error."""
    client = get_client()

    params = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        "model": model or _resolve_model(),
        "max_completion_tokens": _resolve_int("GROQ_MAX_TOKENS", MAX_TOKENS),
        "temperature": _resolve_float("GROQ_TEMPERATURE", TEMPERATURE),
    }

    reasoning_effort = _resolve_reasoning_effort()
    if reasoning_effort is not None:
        params["reasoning_effort"] = reasoning_effort

    completion = _create_completion(client, **params)

    choice = completion.choices[0]
    content = choice.message.content or ""

    if choice.finish_reason == "length":
        if not content.strip():
            raise RuntimeError(
                "The model used its entire token budget before producing a "
                "response. Increase GROQ_MAX_TOKENS and try again."
            )
        content += (
            "\n\n---\n"
            "**This response was truncated** because it reached the "
            "`GROQ_MAX_TOKENS` limit. Increase `GROQ_MAX_TOKENS` for a "
            "complete answer."
        )
    return content


# -- Database --------------------------------------------------------------

def _connect():
    return sqlite3.connect(DB_PATH, timeout=10)


def init_db():
    with closing(_connect()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_idea TEXT NOT NULL,
                teammate TEXT NOT NULL,
                output TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_to_history(project_idea, teammate, output):
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with closing(_connect()) as conn:
        conn.execute("""
            INSERT INTO history (project_idea, teammate, output, created_at)
            VALUES (?, ?, ?, ?)
        """, (project_idea, teammate, output, local_time))
        conn.commit()


def get_history():
    with closing(_connect()) as conn:
        cursor = conn.execute("""
            SELECT id, project_idea, teammate, output, created_at
            FROM history
            ORDER BY datetime(created_at) DESC, id DESC
        """)
        return cursor.fetchall()


def delete_history_item(item_id):
    with closing(_connect()) as conn:
        conn.execute("DELETE FROM history WHERE id = ?", (item_id,))
        conn.commit()


def clear_all_history():
    with closing(_connect()) as conn:
        conn.execute("DELETE FROM history")
        conn.commit()
