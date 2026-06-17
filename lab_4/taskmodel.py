"""
Lab 4 — TaskModel
"""

import uuid
from observers import TaskObserver
from strategies import SortStrategy, SortByPriority


class TaskModel:
    """Core task store that acts as the observable subject."""

    def __init__(self) -> None:
        self._tasks: dict[str, dict] = {}          # id -> task dict
        self._observers: list[TaskObserver] = []
        self._sort_strategy: SortStrategy = SortByPriority()


    def subscribe(self, observer: TaskObserver) -> None:
        """Register an observer to receive task events."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: TaskObserver) -> None:
        """Remove a previously registered observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, event_type: str, task: dict) -> None:
        """Broadcast an event to every subscribed observer."""
        for observer in list(self._observers):   # copy guards against mid-loop removal
            observer.on_task_event(event_type, task)


    def set_sort_strategy(self, strategy: SortStrategy) -> None:
        """Swap the active sorting strategy at runtime."""
        self._sort_strategy = strategy


    def add_task(self, title: str, priority: str = "MEDIUM", due_date: str | None = None) -> dict:
        """
        Create and store a new task, then notify observers with 'task_created'.

        Returns the newly created task dictionary.
        """
        task: dict = {
            "id":       str(uuid.uuid4()),
            "title":    title,
            "priority": priority.upper(),
            "due_date": due_date,
            "status":   "PENDING",
        }
        self._tasks[task["id"]] = task
        self._notify("task_created", task)
        return task

    def complete_task(self, task_id: str) -> dict:
        """Mark a task as COMPLETED and notify observers with 'task_completed'."""
        task = self._tasks[task_id]
        task["status"] = "COMPLETED"
        self._notify("task_completed", task)
        return task

    def delete_task(self, task_id: str) -> dict:
        """Remove a task from the store and notify observers with 'task_deleted'."""
        task = self._tasks.pop(task_id)
        self._notify("task_deleted", task)
        return task

    def list_tasks(self) -> list[dict]:
        """Return all tasks sorted by the current strategy."""
        return self._sort_strategy.sort(list(self._tasks.values()))