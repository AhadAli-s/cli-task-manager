"""
CLI Task Manager — TaskModel
"""

import uuid
from repository import TaskRepository
from observers import TaskObserver
from strategies import SortStrategy, SortByPriority


class TaskModel:
    """Observable subject that persists tasks via a repository,
    notifies observers on every change, and sorts via a strategy."""

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo
        self._observers: list[TaskObserver] = []
        self._sort_strategy: SortStrategy = SortByPriority()

    def subscribe(self, observer: TaskObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: TaskObserver) -> None:
        self._observers = [o for o in self._observers if o is not observer]

    def _notify(self, event_type: str, task: dict) -> None:
        for observer in list(self._observers):
            observer.on_task_event(event_type, task)

    def set_sort_strategy(self, strategy: SortStrategy) -> None:
        self._sort_strategy = strategy

    def add_task(
        self,
        title: str,
        priority: str = "MEDIUM",
        due_date: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        task = {
            "id":       str(uuid.uuid4()),
            "title":    title,
            "priority": priority,
            "due_date": due_date,
            "tags":     tags or [],
            "status":   "PENDING",
        }
        self._repo.save(task)
        self._notify("task_created", task)
        return task

    def complete_task(self, task_id: str) -> dict:
        task = self._repo.find_by_id(task_id)
        task["status"] = "COMPLETED"
        self._repo.update(task)
        self._notify("task_completed", task)
        return task

    def delete_task(self, task_id: str) -> None:
        task = self._repo.find_by_id(task_id)
        self._repo.delete(task_id)
        self._notify("task_deleted", task)

    def list_tasks(self) -> list[dict]:
        return self._sort_strategy.sort(self._repo.find_all())

    def get_task(self, task_id: str) -> dict:
        return self._repo.find_by_id(task_id)
