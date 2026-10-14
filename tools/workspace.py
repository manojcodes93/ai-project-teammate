"""Workspace creation and lifecycle helpers."""

import uuid
from pathlib import Path

from tools.paths import resolve_workspace
import utils.config as _config


def create_workspace(label="project") -> Path:
    workspace = Path(_config.WORKSPACE_ROOT) / f"{label}-{uuid.uuid4().hex[:8]}"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def cleanup_workspace(workspace) -> bool:
    import shutil

    path = Path(workspace)
    if not path.exists():
        return True
    if not path.is_relative_to(Path(_config.WORKSPACE_ROOT).resolve()):
        return False
    shutil.rmtree(path, ignore_errors=True)
    return not path.exists()


def write_files(workspace, files):
    """Write a mapping of relative path -> content into a workspace."""
    root = resolve_workspace(workspace)
    written = []
    for relative, content in (files or {}).items():
        target = safe_path_resolve(root, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content), encoding="utf-8")
        written.append(target.relative_to(root).as_posix())
    return written


def safe_path_resolve(root, relative):
    from tools.paths import safe_relative_path

    return safe_relative_path(root, relative)
