"""
Lab 3 — Demonstration Script
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from repository import (
    TaskRepository,
    JSONTaskRepository,
    SQLiteTaskRepository,
    TaskService,
)
from decorators import (
    timing_decorator,
    logging_decorator,
    retry_decorator,
    make_cache,
)


# ---------------------------------------------------------------------------
# Decorated repository — decorators applied in lab-specified order:
#   retry (outermost) → logging (middle) → timing (innermost)
# ---------------------------------------------------------------------------

_cache_read, _cache_invalidate = make_cache()


class DecoratedSQLiteRepo(SQLiteTaskRepository):
    """SQLiteTaskRepository with all three decorators on save(), plus caching."""

    @retry_decorator(max_retries=3)
    @logging_decorator
    @timing_decorator
    def save(self, task: dict) -> None:  # type: ignore[override]
        super().save(task)

    @_cache_read
    def find_by_id(self, task_id: str) -> dict:
        return super().find_by_id(task_id)

    @_cache_invalidate
    def delete(self, task_id: str) -> None:
        super().delete(task_id)

    @_cache_invalidate
    def save_invalidating(self, task: dict) -> None:
        """Used only to demo cache invalidation via save; not part of normal flow."""
        super().save(task)


# ---------------------------------------------------------------------------
# Part 1 — repository swap
# ---------------------------------------------------------------------------

def run_service_demo(label: str, repo: TaskRepository) -> None:
    print(f"\n{'─' * 52}")
    print(f"  Backend: {label}")
    print(f"{'─' * 52}")

    svc = TaskService(repo)

    t1 = svc.add_task("Write unit tests",  priority="HIGH",   due_date="2026-05-01")
    t2 = svc.add_task("Update README",     priority="LOW",    due_date="2026-06-01")
    t3 = svc.add_task("Fix login bug",     priority="MEDIUM", due_date="2026-04-30")

    print("\nAll tasks after adding three:")
    for t in svc.list_all_tasks():
        print(f"  [{t['status']:10}] [{t['priority']:6}] {t['title']}")

    svc.complete_task(t1["id"])
    print(f"\nCompleted : '{t1['title']}'")

    svc.delete_task(t3["id"])
    print(f"Deleted   : '{t3['title']}'")

    print("\nFinal task list:")
    for t in svc.list_all_tasks():
        print(f"  [{t['status']:10}] [{t['priority']:6}] {t['title']}")


# ---------------------------------------------------------------------------
# Part 2 — decorated save()
# ---------------------------------------------------------------------------

def run_decorator_demo() -> None:
    # --- normal decorated save ---
    print(f"\n{'=' * 52}")
    print("  Decorator Demo — normal save()")
    print(f"{'=' * 52}\n")

    repo = DecoratedSQLiteRepo(db_path="demo_decorated.db")
    task = {
        "id":       "demo-001",
        "title":    "Decorator test task",
        "priority": "HIGH",
        "due_date": "2026-12-31",
        "status":   "PENDING",
    }
    repo.save(task)

    # --- flaky save: fail twice, succeed on third attempt ---
    print(f"\n{'=' * 52}")
    print("  Decorator Demo — save() fails twice then succeeds")
    print(f"{'=' * 52}\n")

    attempt_count = {"n": 0}
    _original_super_save = SQLiteTaskRepository.save

    def flaky_save(self, task):  # type: ignore
        attempt_count["n"] += 1
        if attempt_count["n"] < 3:
            raise IOError(f"Simulated I/O failure on attempt {attempt_count['n']}")
        _original_super_save(self, task)

    SQLiteTaskRepository.save = flaky_save  # type: ignore[method-assign]

    flaky_task = {
        "id":       "demo-002",
        "title":    "Flaky task — succeeds on attempt 3",
        "priority": "MEDIUM",
        "due_date": "2026-12-31",
        "status":   "PENDING",
    }
    DecoratedSQLiteRepo(db_path="demo_decorated.db").save(flaky_task)

    SQLiteTaskRepository.save = _original_super_save  # type: ignore[method-assign]


# ---------------------------------------------------------------------------
# Part 3 — caching demo
# ---------------------------------------------------------------------------

def run_cache_demo() -> None:
    print(f"\n{'=' * 52}")
    print("  Caching Demo — find_by_id cache hit & invalidation")
    print(f"{'=' * 52}")

    repo = DecoratedSQLiteRepo(db_path="demo_decorated.db")
    task_id = "demo-001"

    print("\n1st call  (cache MISS — queries database):")
    repo.find_by_id(task_id)

    print("\n2nd call  (cache HIT — no database query):")
    repo.find_by_id(task_id)

    print("\nCalling delete() — cache must be invalidated:")
    try:
        repo.delete(task_id)
    except KeyError:
        pass  # may already be absent; invalidation is what matters

    print("\n3rd call  (cache MISS — invalidated by delete):")
    try:
        repo.find_by_id(task_id)
    except KeyError:
        print(f"  KeyError: task '{task_id}' was deleted — correct behaviour.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for f in ("tasks_repo.json", "tasks_repo.db", "demo_decorated.db"):
        if os.path.exists(f):
            os.remove(f)

    print("=" * 52)
    print("  PART 1 — Repository Swap")
    print("=" * 52)
    run_service_demo("JSONTaskRepository",   JSONTaskRepository())
    run_service_demo("SQLiteTaskRepository", SQLiteTaskRepository())

    run_decorator_demo()
    run_cache_demo()

    print("\n✓ All demonstrations completed successfully.")
