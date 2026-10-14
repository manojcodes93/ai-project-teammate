"""LangGraph SQLite checkpoint helpers."""

import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

from utils.config import CHECKPOINT_DB_PATH


class CheckpointManager:
    """Owns a SQLite connection and its LangGraph saver."""

    def __init__(self, path=None):
        self.path = Path(path or CHECKPOINT_DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path), check_same_thread=False)
        self.saver = SqliteSaver(self.connection)

    def close(self):
        try:
            self.connection.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def create_checkpointer(path=None):
    manager = CheckpointManager(path=path)
    return manager.saver, manager


def open_checkpointer(path=None):
    """Return (saver, manager). Caller owns cleanup of manager."""
    return create_checkpointer(path)
