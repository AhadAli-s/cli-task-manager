from __future__ import annotations
from dataclasses import dataclass, field


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
