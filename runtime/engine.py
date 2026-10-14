"""Execution helpers around the compiled LangGraph workflow."""

from uuid import uuid4

from persistence.checkpoints import CheckpointManager
from graph.workflow import compile_workflow
from langgraph.types import Command


class WorkflowEngine:
    def __init__(self, checkpointer_manager=None):
        if checkpointer_manager is None:
            self.manager = CheckpointManager()
        else:
            self.manager = checkpointer_manager
        self.graph = compile_workflow(checkpointer=self.manager.saver)

    def close(self):
        self.manager.close()

    def start(self, request, thread_id=None):
        if not thread_id:
            thread_id = f"run-{uuid4().hex[:12]}"
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "request": request,
            "thread_id": thread_id,
            "files": {},
            "tests_passed": False,
            "review_passed": False,
            "developer_attempts": 0,
            "review_cycles": 0,
            "max_developer_attempts": 3,
            "max_review_cycles": 2,
            "status": "running",
        }
        result = self.graph.invoke(initial_state, config=config)
        return thread_id, result, config

    def resume(self, thread_id, decision):
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(Command(resume=decision), config=config)
        return result, config

    def get_state(self, thread_id):
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = self.graph.get_state(config)
        return snapshot

    def is_interrupted(self, thread_id):
        snapshot = self.get_state(thread_id)
        return bool(getattr(snapshot, "interrupts", None))


def thread_config(thread_id):
    return {"configurable": {"thread_id": thread_id}}