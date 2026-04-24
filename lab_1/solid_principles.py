"""
Lab 1 — SOLID Principles
"""

# =============================================================================
# PART A — SRP & OCP
# =============================================================================

# BEFORE:
# class ReportManager:
#     def __init__(self, tasks):
#         self.tasks = tasks
#     def filter_overdue(self):
#         from datetime import date
#         return [t for t in self.tasks if t['due_date'] < date.today().isoformat()]
#     def format_as_text(self, tasks):
#         lines = []
#         for t in tasks:
#             lines.append(f"[{t['priority']}] {t['title']} — due {t['due_date']}")
#         return "\n".join(lines)
#     def format_as_html(self, tasks):
#         rows = "".join(f"<tr><td>{t['title']}</td><td>{t['due_date']}</td></tr>" for t in tasks)
#         return f"<table>{rows}</table>"
#     def save_to_file(self, content, filename):
#         with open(filename, 'w') as f:
#             f.write(content)
#     def send_email(self, content, recipient):
#         import smtplib
#         pass

# --- SRP Violations in ReportManager ---
# 1. Filtering tasks       — belongs in a dedicated filter/query class.
# 2. Formatting as text    — belongs in a TextFormatter class.
# 3. Formatting as HTML    — belongs in an HtmlFormatter class.
# 4. Saving to file        — belongs in a file I/O / persistence class.
# 5. Sending email         — belongs in a notification / email-gateway class.
# ReportManager has five separate reasons to change — one per responsibility above.

# --- OCP Violation ---
# Adding JSON output requires opening ReportManager and adding format_as_json().
# Every new format forces modification of the existing class — violating OCP.
# Fix: extract formatting behind an abstract Formatter interface so new formats
# are added by writing new classes, not editing existing ones.

# AFTER: -----------------------------------------------------------------------

from abc import ABC, abstractmethod
from datetime import date


# --- Responsibility 1: filtering ---

class TaskFilter:
    """Responsible solely for filtering task collections."""

    @staticmethod
    def overdue(tasks: list[dict]) -> list[dict]:
        return [t for t in tasks if t['due_date'] < date.today().isoformat()]


# --- Responsibility 2: formatting (abstract interface — satisfies OCP) ---

class Formatter(ABC):
    """Abstract base for all output formatters."""

    @abstractmethod
    def format(self, tasks: list[dict]) -> str:
        raise NotImplementedError


class TextFormatter(Formatter):
    """Responsible solely for formatting tasks as plain text."""

    def format(self, tasks: list[dict]) -> str:
        lines = [f"[{t['priority']}] {t['title']} — due {t['due_date']}" for t in tasks]
        return "\n".join(lines)


class HtmlFormatter(Formatter):
    """Responsible solely for formatting tasks as an HTML table."""

    def format(self, tasks: list[dict]) -> str:
        rows = "".join(
            f"<tr><td>{t['title']}</td><td>{t['due_date']}</td></tr>"
            for t in tasks
        )
        return f"<table>{rows}</table>"


class JsonFormatter(Formatter):
    """Responsible solely for formatting tasks as JSON."""

    def format(self, tasks: list[dict]) -> str:
        import json
        return json.dumps(tasks, indent=2)


# --- Responsibility 3: file persistence ---

class FileSaver:
    """Responsible solely for writing content to the filesystem."""

    @staticmethod
    def save(content: str, filename: str) -> None:
        with open(filename, 'w') as f:
            f.write(content)


# --- Responsibility 4: email delivery ---

class EmailSender:
    """Responsible solely for sending content via email."""

    @staticmethod
    def send(content: str, recipient: str) -> None:
        # Real SMTP logic would live here; stub for demonstration.
        print(f"[EMAIL] Sending to {recipient}:\n{content[:80]}...")


# =============================================================================
# PART B — LSP
# =============================================================================

# BEFORE:
# class TaskExporter:
#     def export(self, tasks):
#         raise NotImplementedError
#
# class CSVExporter(TaskExporter):
#     def export(self, tasks):
#         lines = ["title,priority,due_date"]
#         for t in tasks:
#             lines.append(f"{t['title']},{t['priority']},{t['due_date']}")
#         return "\n".join(lines)
#
# class ReadOnlyExporter(TaskExporter):
#     def export(self, tasks):
#         raise PermissionError("This exporter is read-only and cannot export.")
#
# def export_all(exporter: TaskExporter, tasks):
#     result = exporter.export(tasks)
#     print(result)

# --- LSP Violation ---
# ReadOnlyExporter inherits from TaskExporter and promises the same contract:
# "call export() and get a result."  But it breaks that contract by raising
# PermissionError instead.  Any code that accepts a TaskExporter — like
# export_all() — will crash when handed a ReadOnlyExporter, even though the
# type annotation says it is safe.  Substituting the subtype for the parent type
# breaks the program — this is the definition of an LSP violation.

# --- Fix ---
# ReadOnlyExporter has no business extending TaskExporter because it cannot
# honour the export contract.  Remove the inheritance entirely.
# If "read-only" behaviour is meaningful, model it as a separate concept
# (e.g. a ViewableStorage that has a load() method but no export()).

# AFTER: -----------------------------------------------------------------------

class TaskExporter(ABC):
    """Contract: any concrete exporter can export a task list and return a string."""

    @abstractmethod
    def export(self, tasks: list[dict]) -> str:
        raise NotImplementedError


class CSVExporter(TaskExporter):
    """Exports tasks as comma-separated values."""

    def export(self, tasks: list[dict]) -> str:
        lines = ["title,priority,due_date"]
        for t in tasks:
            lines.append(f"{t['title']},{t['priority']},{t['due_date']}")
        return "\n".join(lines)


# ReadOnlyExporter is NOT a TaskExporter — it has a completely different role.
class ReadOnlyViewer:
    """Provides read access to tasks; has no export capability by design."""

    def view(self, tasks: list[dict]) -> None:
        for t in tasks:
            print(f"  {t['title']} [{t['priority']}] due {t['due_date']}")


def export_all(exporter: TaskExporter, tasks: list[dict]) -> None:
    """Safe to call with ANY TaskExporter subclass — LSP guaranteed."""
    result = exporter.export(tasks)
    print(result)


# =============================================================================
# PART C — DIP
# =============================================================================

# BEFORE:
# class SQLiteTaskRepository:
#     def save(self, task):
#         import sqlite3
#         conn = sqlite3.connect('tasks.db')
#         conn.close()
#
# class TaskManager:
#     def __init__(self):
#         self.repo = SQLiteTaskRepository()   # hard dependency on concrete class
#     def add_task(self, task):
#         self.repo.save(task)

# --- DIP Violation ---
# TaskManager (high-level policy) directly instantiates SQLiteTaskRepository
# (low-level detail).  This means:
# • TaskManager cannot be unit-tested without a real SQLite database.
# • Swapping to JSON or PostgreSQL requires editing TaskManager itself.
# Both high-level and low-level modules depend on the concrete class instead of
# on an abstraction — violating DIP.

# AFTER: -----------------------------------------------------------------------

import json
import os


class TaskRepository(ABC):
    """Abstraction that both high-level (TaskManager) and low-level modules depend on."""

    @abstractmethod
    def save(self, task: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_all(self) -> list[dict]:
        raise NotImplementedError


class SQLiteTaskRepository(TaskRepository):
    """Low-level detail: persists tasks in SQLite."""

    def __init__(self, db_path: str = 'tasks.db') -> None:
        import sqlite3
        self._db_path = db_path
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tasks "
            "(id TEXT PRIMARY KEY, title TEXT, priority TEXT, due_date TEXT)"
        )
        conn.commit()
        conn.close()

    def save(self, task: dict) -> None:
        import sqlite3
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            "INSERT OR REPLACE INTO tasks VALUES (:id, :title, :priority, :due_date)",
            task,
        )
        conn.commit()
        conn.close()

    def load_all(self) -> list[dict]:
        import sqlite3
        conn = sqlite3.connect(self._db_path)
        rows = conn.execute("SELECT id, title, priority, due_date FROM tasks").fetchall()
        conn.close()
        return [
            {"id": r[0], "title": r[1], "priority": r[2], "due_date": r[3]}
            for r in rows
        ]


class JSONTaskRepository(TaskRepository):
    """Low-level detail: persists tasks in a JSON file."""

    def __init__(self, file_path: str = 'tasks.json') -> None:
        self._file_path = file_path
        if not os.path.exists(self._file_path):
            with open(self._file_path, 'w') as f:
                json.dump([], f)

    def save(self, task: dict) -> None:
        tasks = self.load_all()
        tasks = [t for t in tasks if t.get('id') != task.get('id')]
        tasks.append(task)
        with open(self._file_path, 'w') as f:
            json.dump(tasks, f, indent=2)

    def load_all(self) -> list[dict]:
        with open(self._file_path, 'r') as f:
            return json.load(f)


class TaskManager:
    """High-level policy: depends only on the TaskRepository abstraction.

    The concrete repository is injected through the constructor — DIP satisfied.
    TaskManager never needs to change regardless of which storage backend is used.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo          # depends on abstraction, not concrete class

    def add_task(self, task: dict) -> None:
        self._repo.save(task)

    def list_tasks(self) -> list[dict]:
        return self._repo.load_all()


# =============================================================================
# DEMONSTRATION — runs when the file is executed directly
# =============================================================================

if __name__ == '__main__':
    import uuid

    SAMPLE_TASKS = [
        {'id': '1', 'title': 'Write tests',    'priority': 'HIGH',   'due_date': '2024-01-01'},
        {'id': '2', 'title': 'Fix login bug',  'priority': 'MEDIUM', 'due_date': '2099-12-31'},
        {'id': '3', 'title': 'Update README',  'priority': 'LOW',    'due_date': '2024-06-01'},
    ]

    print("=" * 60)
    print("PART A — SRP & OCP")
    print("=" * 60)

    overdue = TaskFilter.overdue(SAMPLE_TASKS)
    print(f"Overdue tasks: {[t['title'] for t in overdue]}\n")

    for fmt_class in (TextFormatter, HtmlFormatter, JsonFormatter):
        fmt = fmt_class()
        print(f"--- {fmt_class.__name__} ---")
        print(fmt.format(SAMPLE_TASKS[:2]))
        print()

    print("=" * 60)
    print("PART B — LSP")
    print("=" * 60)

    csv_exporter = CSVExporter()
    export_all(csv_exporter, SAMPLE_TASKS)
    print()

    viewer = ReadOnlyViewer()
    print("ReadOnlyViewer.view() (not an exporter):")
    viewer.view(SAMPLE_TASKS[:1])
    print()

    print("=" * 60)
    print("PART C — DIP")
    print("=" * 60)

    test_task = {
        'id': str(uuid.uuid4()),
        'title': 'Demonstrate DIP',
        'priority': 'HIGH',
        'due_date': '2026-12-31',
    }

    # Same TaskManager, different repositories — zero changes to TaskManager.
    for repo_class, label in (
        (JSONTaskRepository,   'JSONTaskRepository'),
        (SQLiteTaskRepository, 'SQLiteTaskRepository'),
    ):
        repo = repo_class()
        manager = TaskManager(repo)
        manager.add_task(test_task)
        loaded = manager.list_tasks()
        print(f"[{label}] Saved and loaded: {loaded[-1]['title']}")

    print("\nAll demonstrations completed successfully.")
