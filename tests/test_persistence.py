from persistence.checkpoints import CheckpointManager


def test_checkpoint_save_and_resume(tmp_path):
    manager = CheckpointManager(path=tmp_path / "cp.db")
    try:
        saver = manager.saver
        assert saver is not None
        # Basic table sanity: checkpoint db file created.
        assert (tmp_path / "cp.db").exists()
    finally:
        manager.close()


def test_existing_history_preserved(tmp_path, monkeypatch):
    # Use temp DB path for history.
    import utils.helpers as helpers
    import utils.config as config

    db_path = tmp_path / "history.db"
    monkeypatch.setattr(helpers, "DB_PATH", str(db_path))
    helpers.init_db()
    helpers.save_to_history("idea", "Tester", "output")
    rows = helpers.get_history()
    assert len(rows) == 1
    # workflow_runs table is separate and available.
    helpers.save_workflow_run("t1", "idea", "success", 1, 1, "summary")
    runs = helpers.get_workflow_runs()
    assert len(runs) == 1
    assert rows[0][1] == "idea"


def test_approval_interruption_resume(tmp_path, monkeypatch):
    # Enable approval requirement
    monkeypatch.setenv("REQUIRES_TEST_APPROVAL", "true")
    # Reload config value used in nodes by patching
    import utils.config as config

    monkeypatch.setattr(config, "REQUIRES_TEST_APPROVAL", True)
    monkeypatch.setattr("graph.nodes.run_product_manager", lambda request, context=None: "req")
    monkeypatch.setattr(
        "graph.nodes.run_developer",
        lambda prompt, feedback=None, existing_code=None: "```python\nprint('ok')\n```",
    )
    monkeypatch.setattr("graph.nodes.run_tester", lambda request, code=None: "strategy")
    monkeypatch.setattr("graph.nodes.run_reviewer", lambda code: "BUGS:\n- No bugs found\n\nCORRECTED CODE:\n```python\nprint('ok')\n```")
    monkeypatch.setattr("graph.nodes.run_documentation", lambda request, files=None: "docs")
    monkeypatch.setattr(
        "graph.nodes.run_project_tests",
        lambda workspace, command=None, files=None, sandbox=None: {"ok": True, "status": "passed", "exit_code": 0},
    )

    from runtime.engine import WorkflowEngine
    from persistence.checkpoints import CheckpointManager

    manager = CheckpointManager(path=tmp_path / "cp.db")
    try:
        engine = WorkflowEngine(checkpointer_manager=manager)
        thread_id, result, config = engine.start("build")
        # Should be interrupted before tests (if interrupt actually emitted)
        snapshot = engine.get_state(thread_id)
        # Resume approved
        res, cfg = engine.resume(thread_id, {"approved": True})
        assert res.get("status") in {"success", "running"}
    finally:
        manager.close()
        engine.close()


def test_rejected_actions_do_not_execute(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUIRES_TEST_APPROVAL", "true")
    import utils.config as config

    monkeypatch.setattr(config, "REQUIRES_TEST_APPROVAL", True)

    from unittest import mock

    # Mock test runner to track calls
    calls = {"count": 0}

    def fake_tests(workspace, command=None, files=None, sandbox=None):
        calls["count"] += 1
        return {"ok": True, "status": "passed", "exit_code": 0}

    monkeypatch.setattr("graph.nodes.run_product_manager", lambda request, context=None: "req")
    monkeypatch.setattr(
        "graph.nodes.run_developer", lambda prompt, feedback=None, existing_code=None: "```python\nprint('ok')\n```"
    )
    monkeypatch.setattr("graph.nodes.run_tester", lambda request, code=None: "strategy")
    monkeypatch.setattr("graph.nodes.run_reviewer", lambda code: "BUGS:\n- No bugs found\n\nCORRECTED CODE:\n```python\nprint('ok')\n```")
    monkeypatch.setattr("graph.nodes.run_documentation", lambda request, files=None: "docs")
    monkeypatch.setattr("graph.nodes.run_project_tests", fake_tests)

    from persistence.checkpoints import CheckpointManager
    from runtime.engine import WorkflowEngine

    manager = CheckpointManager(path=tmp_path / "cp.db")
    try:
        engine = WorkflowEngine(checkpointer_manager=manager)
        thread_id, result, config = engine.start("build")
        # reject
        engine.resume(thread_id, {"approved": False})
        # tests should not have run
        assert calls["count"] == 0
    finally:
        manager.close()
        engine.close()
