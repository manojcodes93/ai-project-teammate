"""Execution helpers around the compiled LangGraph workflow."""

import threading
from uuid import uuid4

from langgraph.types import Command

from persistence.checkpoints import CheckpointManager
from graph.workflow import compile_workflow
from utils.config import REQUIRES_TEST_APPROVAL


class WorkflowEngine:
    def __init__(self, checkpointer_manager=None):
        if checkpointer_manager is None:
            self.manager = CheckpointManager()
        else:
            self.manager = checkpointer_manager
        self.graph = compile_workflow(checkpointer=self.manager.saver)

    def close(self):
        self.manager.close()

    def _initial_state(self, request, thread_id, requires_test_approval, max_developer_attempts=None):
        approval = REQUIRES_TEST_APPROVAL if requires_test_approval is None else bool(requires_test_approval)
        attempts = 3 if max_developer_attempts is None else int(max_developer_attempts)
        return {
            "request": request,
            "thread_id": thread_id,
            "files": {},
            "tests_passed": False,
            "review_passed": False,
            "developer_attempts": 0,
            "review_cycles": 0,
            "max_developer_attempts": attempts,
            "max_review_cycles": 2,
            "requires_test_approval": approval,
            "events": [],
            "status": "running",
        }

    def start(self, request, thread_id=None, requires_test_approval=None, max_developer_attempts=None):
        if not thread_id:
            thread_id = f"run-{uuid4().hex[:12]}"
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = self._initial_state(request, thread_id, requires_test_approval, max_developer_attempts)
        result = self.graph.invoke(initial_state, config=config)
        return thread_id, result, config

    def stream(self, request, thread_id=None, requires_test_approval=None, max_developer_attempts=None):
        if not thread_id:
            thread_id = f"run-{uuid4().hex[:12]}"
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = self._initial_state(request, thread_id, requires_test_approval, max_developer_attempts)
        generator = self.graph.stream(initial_state, config=config, stream_mode="updates")
        return thread_id, generator

    def resume(self, thread_id, decision):
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(Command(resume=decision), config=config)
        return result, config

    def resume_stream(self, thread_id, decision):
        config = {"configurable": {"thread_id": thread_id}}
        generator = self.graph.stream(Command(resume=decision), config=config, stream_mode="updates")
        return generator

    def cancel(self, thread_id):
        config = {"configurable": {"thread_id": thread_id}}
        try:
            self.graph.update_state(config, {"status": "cancelled"}, as_node="finalize")
        except Exception:
            pass

    def get_state(self, thread_id):
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.get_state(config)

    def is_interrupted(self, thread_id):
        snapshot = self.get_state(thread_id)
        return bool(getattr(snapshot, "interrupts", None))


def thread_config(thread_id):
    return {"configurable": {"thread_id": thread_id}}
