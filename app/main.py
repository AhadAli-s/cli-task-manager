"""
CLI Task Manager — Entry Point
GrowUrk Software Development Internship — Week 2

Usage:
  python main.py add-task "Fix login bug" --priority HIGH --due-date 2026-05-01
  python main.py add-task "Write tests" --priority MEDIUM --tags bug auth
  python main.py list-tasks
  python main.py list-tasks --sort-by due-date
  python main.py list-tasks --sort-by title
  python main.py complete-task <id>
  python main.py delete-task <id>
  python main.py list-tasks --storage sqlite
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from task_builder import TaskBuilder
from taskmodel import TaskModel
from repository import JSONTaskRepository, SQLiteTaskRepository
from observers import ConsoleLogger, FileAuditLog, HighPriorityAlert
from strategies import SortByPriority, SortByDueDate, SortByTitle

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

cfg = ConfigManager()

SORT_STRATEGIES = {
    "priority": SortByPriority(),
    "due-date": SortByDueDate(),
    "title":    SortByTitle(),
}

PRIORITY_ICONS = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
STATUS_ICONS   = {"PENDING": "⏳", "IN_PROGRESS": "🔄", "COMPLETED": "✅"}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def build_model(storage: str) -> TaskModel:
    if storage == "sqlite":
        repo = SQLiteTaskRepository(db_path="tasks.db")
    else:
        repo = JSONTaskRepository(file_path="tasks.json")

    model = TaskModel(repo)
    model.subscribe(ConsoleLogger())
    model.subscribe(FileAuditLog(log_path="audit.log"))
    model.subscribe(HighPriorityAlert())
    return model


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(args: argparse.Namespace) -> None:
    task = (
        TaskBuilder()
        .set_title(args.title)
        .set_priority(args.priority or "MEDIUM")
        .set_due_date(args.due_date or "")
        .set_tags(args.tags or [])
        .build()
    )

    model = build_model(args.storage)
    saved = model.add_task(
        title    = task.title,
        priority = task.priority,
        due_date = task.due_date or None,
        tags     = task.tags,
    )

    print(f"\nTask created successfully!")
    print(f"  ID       : {saved['id']}")
    print(f"  Title    : {saved['title']}")
    print(f"  Priority : {PRIORITY_ICONS.get(saved['priority'], '')} {saved['priority']}")
    print(f"  Due date : {saved['due_date'] or 'not set'}")
    print(f"  Tags     : {', '.join(saved['tags']) if saved['tags'] else 'none'}")


def cmd_list(args: argparse.Namespace) -> None:
    model = build_model(args.storage)
    model.set_sort_strategy(SORT_STRATEGIES.get(args.sort_by, SortByPriority()))
    tasks = model.list_tasks()

    if not tasks:
        print('\nNo tasks yet. Add one with:  python main.py add-task "Your task title"')
        return

    width = 70
    print(f"\n{'─' * width}")
    print(f"  {'TITLE':<28} {'PRIORITY':<10} {'STATUS':<13} DUE DATE")
    print(f"{'─' * width}")
    for t in tasks:
        p_icon = PRIORITY_ICONS.get(t['priority'], '')
        s_icon = STATUS_ICONS.get(t['status'], '')
        due    = t.get('due_date') or 'not set'
        tags   = ', '.join(t.get('tags') or []) or 'none'
        print(f"  {t['title']:<28} {p_icon} {t['priority']:<8} {s_icon} {t['status']:<11} {due}")
        print(f"  ID: {t['id']}   Tags: {tags}")
        print(f"{'─' * width}")


def cmd_complete(args: argparse.Namespace) -> None:
    model = build_model(args.storage)
    try:
        task = model.complete_task(args.id)
        print(f"\n✅ Marked as COMPLETED: '{task['title']}'")
    except KeyError:
        print(f"\n❌ No task found with ID: {args.id}")
        print("   Run  python main.py list-tasks  to see all IDs.")
        sys.exit(1)


def cmd_delete(args: argparse.Namespace) -> None:
    model = build_model(args.storage)
    try:
        task = model.get_task(args.id)
        model.delete_task(args.id)
        print(f"\n🗑️  Deleted: '{task['title']}'")
    except KeyError:
        print(f"\n❌ No task found with ID: {args.id}")
        print("   Run  python main.py list-tasks  to see all IDs.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task-manager",
        description="CLI Task Manager — GrowUrk Week 2 Project",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    storage_kwargs = dict(default="json", choices=["json", "sqlite"],
                          help="Storage backend (default: json)")

    # add-task
    p = sub.add_parser("add-task", help="Add a new task")
    p.add_argument("title",                             help="Task title")
    p.add_argument("--priority", "-p",
                   choices=["LOW", "MEDIUM", "HIGH"],
                   default="MEDIUM",                    help="Priority (default: MEDIUM)")
    p.add_argument("--due-date", "-d",                  help="Due date YYYY-MM-DD")
    p.add_argument("--tags",     "-t", nargs="*",       help="Tags e.g. --tags bug auth")
    p.add_argument("--storage",  **storage_kwargs)

    # list-tasks
    p = sub.add_parser("list-tasks", help="List all tasks")
    p.add_argument("--sort-by", "-s",
                   choices=["priority", "due-date", "title"],
                   default="priority",                  help="Sort order (default: priority)")
    p.add_argument("--storage", **storage_kwargs)

    # complete-task
    p = sub.add_parser("complete-task", help="Mark a task as completed")
    p.add_argument("id",                                help="Task ID")
    p.add_argument("--storage", **storage_kwargs)

    # delete-task
    p = sub.add_parser("delete-task", help="Delete a task")
    p.add_argument("id",                                help="Task ID")
    p.add_argument("--storage", **storage_kwargs)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    {
        "add-task":      cmd_add,
        "list-tasks":    cmd_list,
        "complete-task": cmd_complete,
        "delete-task":   cmd_delete,
    }[args.command](args)


if __name__ == "__main__":
    main()
