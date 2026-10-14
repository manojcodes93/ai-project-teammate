import pytest
from pathlib import Path

from tools.paths import safe_relative_path
from tools.file_tools import write_project_file, read_project_file, list_project_files
from tools.test_tools import check_python_syntax


def test_path_traversal_rejected(tmp_path):
    root = tmp_path
    with pytest.raises(ValueError):
        safe_relative_path(root, "../secret.txt")
    with pytest.raises(ValueError):
        safe_relative_path(root, "sub/../../x")
    with pytest.raises(ValueError):
        safe_relative_path(root, "/etc/passwd")


def test_unauthorized_file_access_rejected(tmp_path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    root = tmp_path / "ws"
    root.mkdir()
    with pytest.raises(ValueError):
        safe_relative_path(root, str(outside))


def test_write_requires_approval_for_existing(tmp_path, monkeypatch):
    import utils.config as config

    config.WORKSPACE_ROOT = tmp_path / "root"
    config.WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    from tools.workspace import create_workspace

    ws = create_workspace("ws")
    write_project_file(ws, "a.txt", "hello", overwrite=False)
    result = write_project_file(ws, "a.txt", "changed", overwrite=False)
    assert result["ok"] is False
    assert result["requires_approval"] is True

    # Approved overwrite (explicit) succeeds.
    result2 = write_project_file(ws, "a.txt", "changed", overwrite=True)
    assert result2["ok"] is True
    assert read_project_file(ws, "a.txt")["content"] == "changed"


def test_valid_invalid_tool_arguments(tmp_path, monkeypatch):
    import utils.config as config

    config.WORKSPACE_ROOT = tmp_path / "root"
    config.WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    from tools.workspace import create_workspace

    ws = create_workspace("ws")
    assert write_project_file(ws, "", "x")["ok"] is False
    assert write_project_file(ws, "a.txt", "x")["ok"] is True
    assert list_project_files(ws)["files"] == ["a.txt"]

    # Syntax check reports failures for bad Python.
    bad = check_python_syntax({"bad.py": "def broken(:\n    pass"})
    assert bad["ok"] is False
    assert "bad.py" in bad["stderr"]

    # Syntax check passes for valid Python.
    good = check_python_syntax({"good.py": "def ok():\n    return 1\n"})
    assert good["ok"] is True


def test_workspace_path_validation(tmp_path):
    from tools.paths import resolve_workspace
    import utils.config as config

    # Redirect root for the test by monkeypatching config
    config.WORKSPACE_ROOT = tmp_path / "root"
    config.WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    ws = config.WORKSPACE_ROOT / "project"
    ws.mkdir()
    assert resolve_workspace(ws) == ws.resolve()
