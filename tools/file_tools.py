"""File operations scoped to a designated workspace."""

from tools.paths import resolve_workspace, safe_relative_path


def list_project_files(workspace):
    root = resolve_workspace(workspace)
    files = []
    for path in root.rglob("*"):
        if path.is_file():
            files.append(path.relative_to(root).as_posix())
    files.sort()
    return {"ok": True, "files": files}


def read_project_file(workspace, relative_path):
    root = resolve_workspace(workspace)
    try:
        target = safe_relative_path(root, relative_path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    if not target.exists() or not target.is_file():
        return {"ok": False, "error": "File not found."}
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"ok": False, "error": "File is not readable as UTF-8 text."}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "path": relative_path, "content": content}


def write_project_file(workspace, relative_path, content, overwrite=False):
    root = resolve_workspace(workspace)
    try:
        target = safe_relative_path(root, relative_path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "requires_approval": False}

    requires_approval = target.exists() and not overwrite
    if requires_approval:
        return {
            "ok": False,
            "error": "Approval required to overwrite an existing file.",
            "requires_approval": True,
            "path": relative_path,
        }

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content), encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "error": str(exc), "requires_approval": False}

    return {
        "ok": True,
        "path": relative_path,
        "bytes_written": len(str(content).encode("utf-8")),
        "overwritten": target.exists() and overwrite,
    }


def tool_read_file(workspace, path):
    return read_project_file(workspace, path)


def tool_write_file(workspace, path, content, overwrite=False):
    return write_project_file(workspace, path, content, overwrite=overwrite)
