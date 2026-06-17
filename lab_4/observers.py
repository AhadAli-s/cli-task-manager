"""
Lab 4 — Observer Pattern
"""

from abc import ABC, abstractmethod
from datetime import datetime


class TaskObserver(ABC):
    """Contract every observer must honour."""

    @abstractmethod
    def on_task_event(self, event_type: str, task: dict) -> None:
        """React to a task lifecycle event."""
        raise NotImplementedError


class ConsoleLogger(TaskObserver):
    """Prints every task event to the terminal."""

    def on_task_event(self, event_type: str, task: dict) -> None:
        print(f"[EVENT] {event_type}: {task['title']}")


class FileAuditLog(TaskObserver):
    """Appends a timestamped entry for every task event to audit.log."""

    def __init__(self, log_path: str = "audit.log") -> None:
        self._log_path = log_path

    def on_task_event(self, event_type: str, task: dict) -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")
        line = f"[{timestamp}] {event_type}: id={task['id']} title={task['title']!r}\n"
        with open(self._log_path, "a") as f:
            f.write(line)


class HighPriorityAlert(TaskObserver):
    """Prints an alert only when a HIGH-priority task is created."""

    def on_task_event(self, event_type: str, task: dict) -> None:
        if event_type == "task_created" and task.get("priority") == "HIGH":
            print(f"[ALERT] High priority task added: {task['title']}")
