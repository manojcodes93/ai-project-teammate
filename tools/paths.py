"""Path validation helpers for the controlled tool layer."""

from pathlib import Path

import utils.config as _config


def resolve_workspace(workspace) -> Path:
    """Return an absolute, validated workspace directory."""
    root = Path(_config.WORKSPACE_ROOT).resolve()
    path = Path(workspace).resolve()
    if not str(path).startswith(str(root)):
        raise ValueError("Workspace is outside the allowed root.")
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_relative_path(workspace: Path, requested: str) -> Path:
    """Resolve a relative path and reject traversal or absolute paths."""
    if not isinstance(requested, str) or not requested.strip():
        raise ValueError("A non-empty relative path is required.")
    if requested.startswith(("/", "\\")):
        raise ValueError("Absolute paths are not allowed.")
    if "\\" in requested:
        raise ValueError("Use forward slashes in relative paths.")

    cleaned = requested.replace("\\", "/")
    if ".." in cleaned.split("/"):
        raise ValueError("Path traversal is not allowed.")

    candidate = (workspace / cleaned).resolve()
    if not candidate.is_relative_to(workspace.resolve()):
        raise ValueError("Path escapes the workspace.")
    return candidate
