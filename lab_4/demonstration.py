"""
Lab 4 — Demonstration Script
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from taskmodel import TaskModel
from observers import ConsoleLogger, FileAuditLog, HighPriorityAlert
from strategies import SortByPriority, SortByDueDate, SortByTitle

AUDIT_LOG = "audit_demo.log"


def run_observer_demo() -> None:
    print("=" * 54)
    print("  PART 1 — Observer Pattern")
    print("=" * 54)

    model = TaskModel()

    console_logger    = ConsoleLogger()
    file_audit        = FileAuditLog(log_path=AUDIT_LOG)
    high_prio_alert   = HighPriorityAlert()

    model.subscribe(console_logger)
    model.subscribe(file_audit)
    model.subscribe(high_prio_alert)

    print("\n--- Adding a HIGH priority task ---")
    t1 = model.add_task("Fix login bug",    priority="HIGH",   due_date="2026-04-30")
    # Expected: ConsoleLogger prints EVENT, FileAuditLog writes to file,
    #           HighPriorityAlert fires because priority == HIGH

    print("\n--- Adding a MEDIUM priority task ---")
    t2 = model.add_task("Update README",    priority="MEDIUM", due_date="2026-06-01")
    # Expected: ConsoleLogger + FileAuditLog fire; HighPriorityAlert stays silent

    print("\n--- Adding a LOW priority task ---")
    t3 = model.add_task("Write changelog",  priority="LOW",    due_date=None)

    print("\n--- Completing the HIGH priority task ---")
    model.complete_task(t1["id"])
    # Expected: ConsoleLogger + FileAuditLog fire; HighPriorityAlert stays silent
    #           (event is 'task_completed', not 'task_created')

    print("\n--- Deleting the LOW priority task ---")
    model.delete_task(t3["id"])

    print(f"\n--- Audit log contents ({AUDIT_LOG}) ---")
    with open(AUDIT_LOG) as f:
        print(f.read().strip())

    print("\n--- Unsubscribing ConsoleLogger, adding another task ---")
    model.unsubscribe(console_logger)
    model.add_task("Secret task", priority="HIGH", due_date="2026-07-01")
    print("  (ConsoleLogger removed — no [EVENT] line above, but [ALERT] still fires)")


def run_strategy_demo() -> None:
    print("\n" + "=" * 54)
    print("  PART 2 — Strategy Pattern")
    print("=" * 54)

    model = TaskModel()
    # suppress observer noise for this demo
    model.add_task("Zebra task",       priority="LOW",    due_date="2026-08-01")
    model.add_task("Alpha task",       priority="HIGH",   due_date="2026-05-15")
    model.add_task("Medium task",      priority="MEDIUM", due_date="2026-04-01")
    model.add_task("Another high",     priority="HIGH",   due_date="2026-06-30")
    model.add_task("No date task",     priority="LOW",    due_date=None)

    strategies = [
        ("SortByPriority",              SortByPriority()),
        ("SortByDueDate",               SortByDueDate()),
        ("SortByTitle",                 SortByTitle()),
    ]

    for label, strategy in strategies:
        model.set_sort_strategy(strategy)
        print(f"\n  [{label}]")
        for t in model.list_tasks():
            due = t["due_date"] or "no date"
            print(f"    [{t['priority']:6}] {t['title']:<22}  due: {due}")


if __name__ == "__main__":
    if os.path.exists(AUDIT_LOG):
        os.remove(AUDIT_LOG)

    run_observer_demo()
    run_strategy_demo()

    print("\n✓ All demonstrations completed successfully.")
