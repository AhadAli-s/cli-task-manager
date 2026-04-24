"""
Lab 4 — Strategy Pattern
"""

from abc import ABC, abstractmethod

PRIORITY_ORDER: dict[str, int] = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


class SortStrategy(ABC):
    """Contract every sorting strategy must honour."""

    @abstractmethod
    def sort(self, tasks: list[dict]) -> list[dict]:
        """Return a new sorted list; do not modify the original."""
        raise NotImplementedError


class SortByPriority(SortStrategy):
    """Sorts tasks HIGH → MEDIUM → LOW."""

    def sort(self, tasks: list[dict]) -> list[dict]:
        return sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t.get("priority", "LOW"), 99))


class SortByDueDate(SortStrategy):
    """Sorts tasks by due_date ascending; tasks with no due date go last."""

    def sort(self, tasks: list[dict]) -> list[dict]:
        return sorted(
            tasks,
            key=lambda t: (t.get("due_date") is None, t.get("due_date") or ""),
        )


class SortByTitle(SortStrategy):
    """Sorts tasks alphabetically by title, case-insensitive."""

    def sort(self, tasks: list[dict]) -> list[dict]:
        return sorted(tasks, key=lambda t: t.get("title", "").lower())
