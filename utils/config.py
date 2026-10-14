"""Application configuration with safe defaults and environment overrides.

All settings are derived from environment variables or Streamlit secrets.
No secret values are stored here beyond boolean flags.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
WORKSPACE_ROOT = DATA_DIR / "workspaces"
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DB_PATH = DATA_DIR / "checkpoints.db"
HISTORY_DB_PATH = DATA_DIR / "history.db"


def _env_bool(name, default=False):
    raw = os.getenv(name)
    try:
        # Streamlit secrets are handled by callers when needed; environment
        # variables are sufficient for non-interactive configuration.
        if raw is None:
            return default
        return str(raw).strip().lower() in {"1", "true", "yes", "on"}
    except Exception:
        return default


SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "python:3.11-slim")
SANDBOX_TIMEOUT_SECONDS = int(os.getenv("SANDBOX_TIMEOUT_SECONDS", "60"))
SANDBOX_CPU_LIMIT = os.getenv("SANDBOX_CPU_LIMIT", "1")
SANDBOX_MEMORY_LIMIT = os.getenv("SANDBOX_MEMORY_LIMIT", "512m")
SANDBOX_PIDS_LIMIT = int(os.getenv("SANDBOX_PIDS_LIMIT", "64"))

MAX_DEVELOPER_ATTEMPTS = int(os.getenv("MAX_DEVELOPER_ATTEMPTS", "3"))
MAX_REVIEW_CYCLES = int(os.getenv("MAX_REVIEW_CYCLES", "2"))

REQUIRES_TEST_APPROVAL = _env_bool("REQUIRES_TEST_APPROVAL", False)
REQUIRES_OVERWRITE_APPROVAL = _env_bool("REQUIRES_OVERWRITE_APPROVAL", True)

DOCKER_REQUIRED = _env_bool("DOCKER_REQUIRED", False)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
