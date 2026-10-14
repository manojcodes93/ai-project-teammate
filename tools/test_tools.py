"""Test execution tools backed by the configured sandbox."""

from sandbox.executor import DockerSandbox, DockerUnavailableError


ALLOWED_RUNNERS = {"unittest", "pytest", "compileall"}


def _validate_command(command):
    if isinstance(command, str):
        tokens = command.split()
    else:
        tokens = list(command)

    if len(tokens) < 3 or tokens[0] != "python" or tokens[1] != "-m":
        return None, "Only 'python -m <runner> ...' commands are allowed."
    if tokens[2] not in ALLOWED_RUNNERS:
        return None, f"Runner '{tokens[2]}' is not allowed."
    # Block obvious shell metacharacters in all tokens.
    for token in tokens:
        if any(char in token for char in (";", "&", "|", "$", "`", ">", "<")):
            return None, "Shell metacharacters are not allowed."
    return tokens, None


def run_project_tests(workspace, command=None, files=None, sandbox=None):
    """Run an approved test command inside the sandbox."""
    if command is None:
        command = ["python", "-m", "unittest", "discover", "-s", "."]

    tokens, error = _validate_command(command)
    if error:
        return {"ok": False, "error": error, "status": "rejected"}

    if sandbox is None:
        sandbox = DockerSandbox()

    if files is None:
        # Caller is responsible for providing files; fall back to empty to
        # avoid host filesystem access.
        files = {}

    try:
        result = sandbox.execute(files=files, command=tokens)
    except DockerUnavailableError as exc:
        return {"ok": False, "error": str(exc), "status": "unavailable"}
    except Exception as exc:  # pragma: no cover - defensive
        return {"ok": False, "error": str(exc), "status": "error"}

    result["ok"] = result.get("status") == "passed"
    return result


def summarize_test_result(result):
    status = result.get("status", "unknown")
    if status == "passed":
        return "Tests passed."
    if status == "timeout":
        return "Tests timed out."
    if status == "unavailable":
        return "Sandbox unavailable; tests were not run."
    stderr = result.get("stderr") or result.get("error") or ""
    stdout = result.get("stdout") or ""
    return f"Tests failed.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}".strip()
