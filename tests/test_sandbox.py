from unittest import mock

from sandbox.executor import DockerSandbox, DockerUnavailableError


def test_docker_unavailable_does_not_execute_host():
    sandbox = DockerSandbox()
    with mock.patch("sandbox.executor.docker_available", return_value=False):
        try:
            sandbox.execute(files={"main.py": "print(1)"}, command=["python", "main.py"])
        except DockerUnavailableError:
            pass
        else:
            raise AssertionError("Expected DockerUnavailableError")


def test_timeout_handled_with_mock():
    sandbox = DockerSandbox(timeout=1)
    fake_proc = mock.Mock()

    def fake_run(*args, **kwargs):
        raise __import__("subprocess").TimeoutExpired(cmd="docker", timeout=1)

    with mock.patch("sandbox.executor.docker_available", return_value=True):
        with mock.patch("sandbox.executor.subprocess.run", side_effect=fake_run):
            result = sandbox.execute(files={}, command=["python", "-m", "unittest"])
    assert result["status"] == "timeout"
    assert result["timed_out"] is True


def test_cleanup_container_on_timeout():
    sandbox = DockerSandbox(timeout=1)
    import subprocess as sp

    calls = []

    def fake_run(*args, **kwargs):
        if args and isinstance(args[0], list) and args[0][:1] == ["docker"] and "kill" in args[0]:
            calls.append("kill")
            return mock.Mock(returncode=0)
        raise sp.TimeoutExpired(cmd="docker", timeout=1)

    with mock.patch("sandbox.executor.docker_available", return_value=True):
        with mock.patch("sandbox.executor.subprocess.run", side_effect=fake_run):
            sandbox.execute(files={}, command=["python", "-m", "unittest"])
    assert "kill" in calls


def test_successful_execution_mock():
    sandbox = DockerSandbox()
    completed = mock.Mock(returncode=0, stdout=b"ok", stderr=b"")
    with mock.patch("sandbox.executor.docker_available", return_value=True):
        with mock.patch("sandbox.executor.subprocess.run", return_value=completed):
            result = sandbox.execute(files={"main.py": "print('ok')"}, command=["python", "main.py"])
    assert result["status"] == "passed"
    assert result["exit_code"] == 0
    assert result["stdout"] == "ok"


def test_temp_workspace_cleanup_tools():
    from tools.workspace import create_workspace, cleanup_workspace

    ws = create_workspace("test")
    assert ws.exists()
    assert cleanup_workspace(ws) is True
    assert not ws.exists()