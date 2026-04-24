"""
Lab 2 — Part B: Factory Method — TaskStorageFactory
"""

import json
import os
import sqlite3
from abc import ABC, abstractmethod


class TaskStorage(ABC):
    """Contract every storage backend must honour."""

    @abstractmethod
    def save(self, task: dict) -> None:
        """Persist a single task."""
        raise NotImplementedError

    @abstractmethod
    def load(self) -> list[dict]:
        """Return all persisted tasks."""
        raise NotImplementedError



class JSONStorage(TaskStorage):
    """Stores tasks as a JSON array in a flat file."""

    def __init__(self, path: str = "tasks_factory.json") -> None:
        self._path = path
        if not os.path.exists(self._path):
            with open(self._path, "w") as f:
                json.dump([], f)

    def save(self, task: dict) -> None:
        tasks = self.load()
        # replace existing task with same id, or append
        tasks = [t for t in tasks if t.get("id") != task.get("id")]
        tasks.append(task)
        with open(self._path, "w") as f:
            json.dump(tasks, f, indent=2)

    def load(self) -> list[dict]:
        with open(self._path, "r") as f:
            return json.load(f)


class SQLiteStorage(TaskStorage):
    """Stores tasks in an SQLite database table."""

    def __init__(self, db_path: str = "tasks_factory.db") -> None:
        self._db_path = db_path
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id       TEXT PRIMARY KEY,
                    title    TEXT NOT NULL,
                    priority TEXT,
                    due_date TEXT
                )
                """
            )
            conn.commit()

    def save(self, task: dict) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tasks (id, title, priority, due_date) "
                "VALUES (:id, :title, :priority, :due_date)",
                task,
            )
            conn.commit()

    def load(self) -> list[dict]:
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT id, title, priority, due_date FROM tasks"
            ).fetchall()
        return [
            {"id": r[0], "title": r[1], "priority": r[2], "due_date": r[3]}
            for r in rows
        ]


class MemoryStorage(TaskStorage):
    """Stores tasks in memory — useful for tests; no filesystem I/O."""

    def __init__(self) -> None:
        self._store: list[dict] = []

    def save(self, task: dict) -> None:
        self._store = [t for t in self._store if t.get("id") != task.get("id")]
        self._store.append(task)

    def load(self) -> list[dict]:
        return list(self._store)



BACKEND_MAP: dict[str, type[TaskStorage]] = {
    "json":   JSONStorage,
    "sqlite": SQLiteStorage,
    "memory": MemoryStorage,
}


class TaskStorageFactory:
    """Creates the correct TaskStorage backend from a plain string key."""

    @staticmethod
    def create(backend: str) -> TaskStorage:
        key = backend.strip().lower()
        if key not in BACKEND_MAP:
            supported = ", ".join(f"'{k}'" for k in BACKEND_MAP)
            raise ValueError(
                f"Unsupported backend '{backend}'. Supported: {supported}."
            )
        return BACKEND_MAP[key]()


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uuid

    TEST_TASK = {
        "id":       str(uuid.uuid4()),
        "title":    "Factory demo task",
        "priority": "HIGH",
        "due_date": "2026-12-31",
    }

    print("=== Factory Method Demonstration ===\n")

    for backend in ("json", "sqlite", "memory"):
        storage = TaskStorageFactory.create(backend)
        storage.save(TEST_TASK)
        loaded = storage.load()
        match = next((t for t in loaded if t["id"] == TEST_TASK["id"]), None)
        status = "✓" if match else "✗"
        print(f"[{backend:6}]  {status}  saved → loaded: '{match['title'] if match else 'NOT FOUND'}'")

    print()

    # Unsupported backend raises a clear ValueError
    try:
        TaskStorageFactory.create("postgres")
    except ValueError as exc:
        print(f"ValueError caught as expected:\n  {exc}")