"""
Lab 2 — Part C: Builder — TaskBuilder
"""

from __future__ import annotations
from dataclasses import dataclass, field

VALID_PRIORITIES: frozenset[str] = frozenset({"LOW", "MEDIUM", "HIGH"})
VALID_STATUSES:   frozenset[str] = frozenset({"PENDING", "IN_PROGRESS", "COMPLETED"})


@dataclass
class Task:
    """Represents a single task in the CLI Task Manager."""

    title:    str
    priority: str        = "MEDIUM"
    due_date: str | None = None
    tags:     list[str]  = field(default_factory=list)
    status:   str        = "PENDING"

    def __repr__(self) -> str:
        return (
            f"Task("
            f"title={self.title!r}, "
            f"priority={self.priority!r}, "
            f"due_date={self.due_date!r}, "
            f"tags={self.tags!r}, "
            f"status={self.status!r}"
            f")"
        )


class TaskBuilder:
    """Fluent builder for Task objects.

    All setter methods return self to enable method chaining.
    Call build() at the end to validate inputs and get a Task instance.

    Example:
        task = (
            TaskBuilder()
            .set_title("Fix login bug")
            .set_priority("HIGH")
            .set_due_date("2026-04-15")
            .set_tags(["bug", "auth"])
            .set_status("IN_PROGRESS")
            .build()
        )
    """

    def __init__(self) -> None:
        self._title:    str        = ""
        self._priority: str        = "MEDIUM"
        self._due_date: str | None = None
        self._tags:     list[str]  = []
        self._status:   str        = "PENDING"

    def set_title(self, title: str) -> TaskBuilder:
        self._title = title
        return self

    def set_priority(self, priority: str) -> TaskBuilder:
        self._priority = priority
        return self

    def set_due_date(self, due_date: str) -> TaskBuilder:
        self._due_date = due_date
        return self

    def set_tags(self, tags: list[str]) -> TaskBuilder:
        self._tags = list(tags)
        return self

    def set_status(self, status: str) -> TaskBuilder:
        self._status = status
        return self

    def build(self) -> Task:
        """Validate all fields and return a Task instance."""
        if not self._title or not self._title.strip():
            raise ValueError("Task title must not be empty.")
        if self._priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority '{self._priority}'. "
                f"Must be one of: {', '.join(sorted(VALID_PRIORITIES))}."
            )
        if self._status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{self._status}'. "
                f"Must be one of: {', '.join(sorted(VALID_STATUSES))}."
            )
        return Task(
            title    = self._title.strip(),
            priority = self._priority,
            due_date = self._due_date,
            tags     = self._tags,
            status   = self._status,
        )


if __name__ == "__main__":
    print("=== Builder Demonstration ===\n")

    task = (
        TaskBuilder()
        .set_title("Fix login bug")
        .set_priority("HIGH")
        .set_due_date("2026-04-15")
        .set_tags(["bug", "auth"])
        .set_status("IN_PROGRESS")
        .build()
    )
    print(f"Full task:\n  {task}\n")

    minimal = TaskBuilder().set_title("Quick note").build()
    print(f"Minimal task (defaults only):\n  {minimal}\n")

    validation_cases = [
        ("Empty title",      lambda: TaskBuilder().set_title("").build()),
        ("Invalid priority", lambda: TaskBuilder().set_title("X").set_priority("URGENT").build()),
        ("Invalid status",   lambda: TaskBuilder().set_title("X").set_status("DONE").build()),
    ]

    print("Validation errors (all should raise ValueError):")
    for label, fn in validation_cases:
        try:
            fn()
            print(f"  ✗ {label}: no error raised — FAIL")
        except ValueError as exc:
            print(f"  ✓ {label}: {exc}")
