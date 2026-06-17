"""
Lab 3 — Repository Pattern
"""
import json
import os
import sqlite3
import uuid
from abc import ABC, abstractmethod


class TaskRepository(ABC):
    """Abstract base for all task storage backends."""

    @abstractmethod
    def save(self, task: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, task_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, task_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, task: dict) -> None:
        raise NotImplementedError


class JSONTaskRepository(TaskRepository):
    """Persists tasks as a JSON array in a flat file."""

    def __init__(self, file_path: str = "tasks_repo.json") -> None:
        self._path = file_path
        if not os.path.exists(self._path):
            with open(self._path, "w") as f:
                json.dump([], f)

    def _read(self) -> list[dict]:
        with open(self._path, "r") as f:
            return json.load(f)

    def _write(self, tasks: list[dict]) -> None:
        with open(self._path, "w") as f:
            json.dump(tasks, f, indent=2)

    def save(self, task: dict) -> None:
        tasks = self._read()
        tasks = [t for t in tasks if t["id"] != task["id"]]
        tasks.append(task)
        self._write(tasks)

    def find_by_id(self, task_id: str) -> dict:
        for task in self._read():
            if task["id"] == task_id:
                return task
        raise KeyError(f"Task '{task_id}' not found.")

    def find_all(self) -> list[dict]:
        return self._read()

    def delete(self, task_id: str) -> None:
        tasks = self._read()
        remaining = [t for t in tasks if t["id"] != task_id]
        if len(remaining) == len(tasks):
            raise KeyError(f"Task '{task_id}' not found.")
        self._write(remaining)

    def update(self, task: dict) -> None:
        tasks = self._read()
        for i, t in enumerate(tasks):
            if t["id"] == task["id"]:
                tasks[i] = task
                self._write(tasks)
                return
        raise KeyError(f"Task '{task['id']}' not found.")


class SQLiteTaskRepository(TaskRepository):
    """Persists tasks in an SQLite database."""

    _CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS tasks (
            id       TEXT PRIMARY KEY,
            title    TEXT NOT NULL,
            priority TEXT NOT NULL,
            due_date TEXT,
            status   TEXT NOT NULL DEFAULT 'PENDING'
        )
    """

    def __init__(self, db_path: str = "tasks_repo.db") -> None:
        self._db = db_path
        with sqlite3.connect(self._db) as conn:
            conn.execute(self._CREATE_TABLE)
            conn.commit()

    def _row_to_dict(self, row: tuple) -> dict:
        return {
            "id": row[0],
            "title": row[1],
            "priority": row[2],
            "due_date": row[3],
            "status": row[4],
        }

    def save(self, task: dict) -> None:
        with sqlite3.connect(self._db) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tasks (id, title, priority, due_date, status) "
                "VALUES (:id, :title, :priority, :due_date, :status)",
                task,
            )
            conn.commit()

    def find_by_id(self, task_id: str) -> dict:
        with sqlite3.connect(self._db) as conn:
            row = conn.execute(
                "SELECT id, title, priority, due_date, status FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Task '{task_id}' not found.")
        return self._row_to_dict(row)

    def find_all(self) -> list[dict]:
        with sqlite3.connect(self._db) as conn:
            rows = conn.execute(
                "SELECT id, title, priority, due_date, status FROM tasks"
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def delete(self, task_id: str) -> None:
        with sqlite3.connect(self._db) as conn:
            cursor = conn.execute(
                "DELETE FROM tasks WHERE id = ?", (task_id,)
            )
            conn.commit()
        if cursor.rowcount == 0:
            raise KeyError(f"Task '{task_id}' not found.")

    def update(self, task: dict) -> None:
        with sqlite3.connect(self._db) as conn:
            cursor = conn.execute(
                "UPDATE tasks SET title=:title, priority=:priority, "
                "due_date=:due_date, status=:status WHERE id=:id",
                task,
            )
            conn.commit()
        if cursor.rowcount == 0:
            raise KeyError(f"Task '{task['id']}' not found.")


class TaskService:
    """Business logic for task management."""

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    def add_task(self, title: str, priority: str = "MEDIUM",
                 due_date: str | None = None) -> dict:
        """Create a new task and persist it. Returns the created task."""
        task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "priority": priority,
            "due_date": due_date,
            "status": "PENDING",
        }
        self._repo.save(task)
        return task

    def complete_task(self, task_id: str) -> dict:
        """Mark a task as COMPLETED. Returns the updated task."""
        task = self._repo.find_by_id(task_id)
        task["status"] = "COMPLETED"
        self._repo.update(task)
        return task

    def delete_task(self, task_id: str) -> None:
        """Permanently remove a task by id."""
        self._repo.delete(task_id)

    def list_all_tasks(self) -> list[dict]:
        """Return all tasks in the repository."""
        return self._repo.find_all()
