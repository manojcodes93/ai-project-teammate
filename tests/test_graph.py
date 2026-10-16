"""Tests for the LangGraph workflow."""

import pytest


from graph.workflow import compile_workflow
from persistence.checkpoints import CheckpointManager
from utils.config import MAX_DEVELOPER_ATTEMPTS


@pytest.fixture
def llm_mocks(monkeypatch):
    monkeypatch.setattr("graph.nodes.run_product_manager", lambda request, context=None: "requirements")
    monkeypatch.setattr(
        "graph.nodes.run_developer",
        lambda prompt, feedback=None, existing_code=None: "```python\nprint('ok')\n```",
    )
    monkeypatch.setattr("graph.nodes.run_tester", lambda request, code=None: "test strategy")
    monkeypatch.setattr(
        "graph.nodes.run_reviewer",
        lambda code: "BUGS:\n- No bugs found\n\nOPTIMIZATIONS:\nNONE\n\nBEST PRACTICES:\nok\n\nCORRECTED CODE:\n```python\nprint('ok')\n```",
    )
    monkeypatch.setattr("graph.nodes.run_documentation", lambda request, files=None: "docs")
    monkeypatch.setattr(
        "graph.nodes.run_project_tests",
        lambda workspace, command=None, files=None, sandbox=None: {
            "ok": True,
            "status": "passed",
            "exit_code": 0,
        },
    )


def test_successful_execution_through_all_agents(llm_mocks, tmp_path):
    manager = CheckpointManager(path=tmp_path / "cp.db")
    try:
        graph = compile_workflow(checkpointer=manager.saver)
        config = {"configurable": {"thread_id": "success"}}
        result = graph.invoke(
            {
                "request": "build a thing",
                "thread_id": "success",
                "files": {},
                "tests_passed": False,
                "review_passed": False,
                "developer_attempts": 0,
                "review_cycles": 0,
                "max_developer_attempts": MAX_DEVELOPER_ATTEMPTS,
                "max_review_cycles": 2,
                "status": "running",
            },
            config=config,
        )
        assert result["status"] == "success"
        assert "main.py" in result["files"]
        assert result["developer_attempts"] == 1
    finally:
        manager.close()


def test_failed_tests_trigger_developer_retry(llm_mocks, monkeypatch, tmp_path):
    calls = {"dev": 0}

    def flaky_developer(prompt, feedback=None, existing_code=None):
        calls["dev"] += 1
        if calls["dev"] == 1:
            return "```python\nprint('first')\n```"
        return "```python\nprint('fixed')\n```"

    monkeypatch.setattr("graph.nodes.run_developer", flaky_developer)

    # Force the sandbox/tester to fail on first attempt, pass on second.
    from tools import test_tools

    original = test_tools.run_project_tests
    attempts = {"n": 0}

    def fake_tests(workspace, command=None, files=None, sandbox=None):
        attempts["n"] += 1
        if attempts["n"] == 1:
            return {"ok": False, "status": "failed", "stdout": "", "stderr": "boom", "exit_code": 1}
        return {"ok": True, "status": "passed", "stdout": "ok", "stderr": "", "exit_code": 0}

    monkeypatch.setattr("graph.nodes.run_project_tests", fake_tests)

    manager = CheckpointManager(path=tmp_path / "cp.db")
    try:
        graph = compile_workflow(checkpointer=manager.saver)
        config = {"configurable": {"thread_id": "retry"}}
        result = graph.invoke(
            {
                "request": "build a thing",
                "thread_id": "retry",
                "files": {},
                "tests_passed": False,
                "review_passed": False,
                "developer_attempts": 0,
                "review_cycles": 0,
                "max_developer_attempts": MAX_DEVELOPER_ATTEMPTS,
                "max_review_cycles": 2,
                "status": "running",
            },
            config=config,
        )
        assert result["status"] == "success"
        assert calls["dev"] == 2
        assert result["developer_attempts"] == 2
    finally:
        manager.close()


def test_retry_exhaustion_terminates_failed(llm_mocks, monkeypatch, tmp_path):
    # Tests always fail.
    monkeypatch.setattr(
        "graph.nodes.run_project_tests",
        lambda workspace, command=None, files=None, sandbox=None: {
            "ok": False,
            "status": "failed",
            "stdout": "",
            "stderr": "nope",
            "exit_code": 1,
        },
    )

    manager = CheckpointManager(path=tmp_path / "cp.db")
    try:
        graph = compile_workflow(checkpointer=manager.saver)
        config = {"configurable": {"thread_id": "exhaust"}}
        result = graph.invoke(
            {
                "request": "build a thing",
                "thread_id": "exhaust",
                "files": {},
                "tests_passed": False,
                "review_passed": False,
                "developer_attempts": 0,
                "review_cycles": 0,
                "max_developer_attempts": MAX_DEVELOPER_ATTEMPTS,
                "max_review_cycles": 2,
                "status": "running",
            },
            config=config,
        )
        assert result["status"] != "success"
        assert result["developer_attempts"] == MAX_DEVELOPER_ATTEMPTS
    finally:
        manager.close()


def test_review_failure_routes_to_developer(llm_mocks, monkeypatch, tmp_path):
    reviews = {"n": 0}

    def flaky_review(code):
        reviews["n"] += 1
        if reviews["n"] == 1:
            return "BUGS:\n- bug\n\nOPTIMIZATIONS:\nNONE\n\nBEST PRACTICES:\nNONE\n\nCORRECTED CODE:\n```python\nprint('fixed')\n```"
        return "BUGS:\n- No bugs found\n\nOPTIMIZATIONS:\nNONE\n\nBEST PRACTICES:\nNONE\n\nCORRECTED CODE:\n```python\nprint('fixed')\n```"

    monkeypatch.setattr("graph.nodes.run_reviewer", flaky_review)

    manager = CheckpointManager(path=tmp_path / "cp.db")
    try:
        graph = compile_workflow(checkpointer=manager.saver)
        config = {"configurable": {"thread_id": "review"}}
        result = graph.invoke(
            {
                "request": "build a thing",
                "thread_id": "review",
                "files": {},
                "tests_passed": False,
                "review_passed": False,
                "developer_attempts": 0,
                "review_cycles": 0,
                "max_developer_attempts": MAX_DEVELOPER_ATTEMPTS,
                "max_review_cycles": 2,
                "status": "running",
            },
            config=config,
        )
        assert result["status"] == "success"
        assert reviews["n"] == 2
    finally:
        manager.close()


def test_final_success_not_reported_when_failures_remain(llm_mocks, monkeypatch, tmp_path):
    monkeypatch.setattr(
        "graph.nodes.run_project_tests",
        lambda *a, **k: {"ok": False, "status": "failed", "stderr": "x", "exit_code": 1},
    )
    manager = CheckpointManager(path=tmp_path / "cp.db")
    try:
        graph = compile_workflow(checkpointer=manager.saver)
        config = {"configurable": {"thread_id": "no-success"}}
        result = graph.invoke(
            {
                "request": "build a thing",
                "thread_id": "no-success",
                "files": {},
                "tests_passed": False,
                "review_passed": False,
                "developer_attempts": 0,
                "review_cycles": 0,
                "max_developer_attempts": 1,
                "max_review_cycles": 2,
                "status": "running",
            },
            config=config,
        )
        assert result["status"] != "success"
        assert (result.get("final_result") or {}).get("status") != "success"
    finally:
        manager.close()
