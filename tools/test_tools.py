"""Local syntax checks for generated project files.

This module intentionally does not execute generated code. It only compiles
Python source to catch syntax errors, keeping the host environment safe.
"""


def check_python_syntax(files):
    """Compile each Python file without executing it.

    Returns a structured result compatible with the old test tool output.
    """
    failures = []
    checked = 0

    for path, content in (files or {}).items():
        if not str(path).lower().endswith(".py"):
            continue
        checked += 1
        try:
            compile(str(content), path, "exec")
        except SyntaxError as exc:
            failures.append(f"{path}:{exc.lineno or 0}: {exc.msg}")
        except Exception as exc:  # pragma: no cover - defensive
            failures.append(f"{path}: {exc}")

    if failures:
        return {
            "ok": False,
            "status": "failed",
            "mode": "syntax-check-only",
            "checked_files": checked,
            "exit_code": 1,
            "stdout": "",
            "stderr": "\n".join(failures),
            "error": "\n".join(failures),
        }

    return {
        "ok": True,
        "status": "passed",
        "mode": "syntax-check-only",
        "checked_files": checked,
        "exit_code": 0,
        "stdout": f"Compiled {checked} Python file(s) successfully.",
        "stderr": "",
    }


def run_project_tests(workspace=None, command=None, files=None, sandbox=None):
    """Backwards-compatible entry point for the workflow and callers.

    ``workspace`` is accepted for compatibility but is not read from disk.
    Callers should pass ``files`` directly so that no host filesystem access is
    required.
    """
    if files is None:
        files = {}
    return check_python_syntax(files)


def summarize_test_result(result):
    if result.get("status") == "passed":
        return "Syntax checks passed."
    return "Syntax checks failed.\n" + (result.get("stderr") or result.get("error") or "")
