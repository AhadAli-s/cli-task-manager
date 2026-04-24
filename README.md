## What I Built

A fully working command-line task manager built across 5 labs, each focused on a different software design concept. The final project assembles all labs into one cohesive application.

---

## Labs Completed

### Lab 1 — SOLID Principles
Identified and fixed violations of all five SOLID principles in real broken Python code. Refactored a bloated `ReportManager` into focused classes, fixed a Liskov violation in an exporter hierarchy, and rewired a `TaskManager` to depend on abstractions instead of a hardcoded SQLite class.

### Lab 2 — Creational Patterns
Implemented three patterns in the context of the task manager:
- **Singleton** — `ConfigManager` with thread-safe double-checked locking
- **Factory Method** — `TaskStorageFactory` that returns JSON, SQLite, or in-memory storage from a string key
- **Builder** — `TaskBuilder` with fluent method chaining and validation on `build()`

### Lab 3 — Repository & Decorator Patterns
- **Repository** — abstract `TaskRepository` interface with `JSONTaskRepository` and `SQLiteTaskRepository` implementations. `TaskService` never references a concrete backend directly.
- **Decorators** — `timing_decorator`, `logging_decorator`, `retry_decorator`, and a bonus `caching_decorator` with shared cache invalidation across `save()`, `delete()`, and `find_by_id()`.

### Lab 4 — Observer & Strategy Patterns
- **Observer** — `TaskModel` notifies `ConsoleLogger`, `FileAuditLog`, and `HighPriorityAlert` on every task event. Observers are fully decoupled; adding a new one requires zero changes to `TaskModel`.
- **Strategy** — interchangeable sorting via `SortByPriority`, `SortByDueDate`, and `SortByTitle`.

### Lab 5 — UML Diagrams
Three architecture diagrams written in PlantUML (versioned as `.puml` source files):
- **Class diagram** — all 14 classes with inheritance, composition, and dependency relationships
- **Sequence diagram** — full flow of `add-task --priority HIGH` through every layer
- **Component diagram** — high-level system boundaries and data flow

---

## Project Structure

```
cli-task-manager/
├── lab1/               # SOLID principles refactoring
├── lab2/               # Singleton, Factory, Builder
├── lab3/               # Repository pattern + Decorators
├── lab4/               # Observer + Strategy patterns
├── lab5/               # PlantUML source files
├── docs/diagrams/      # Exported PNG diagrams
└── app/                # Final assembled CLI application
    ├── main.py         # Entry point (argparse CLI)
    ├── task_model.py   # Observable subject — coordinates everything
    ├── repository.py   # Data access layer
    ├── observers.py    # Event listeners
    ├── strategies.py   # Sorting algorithms
    ├── task_builder.py # Fluent task construction
    └── config.py       # Singleton configuration
```

---

## How to Run

```bash
# Install dependencies (none beyond Python 3.10+ stdlib)
cd app/

# Add a task
python main.py add-task "Fix login bug" --priority HIGH --due-date 2026-05-01

# List tasks (sorted by priority by default)
python main.py list-tasks
python main.py list-tasks --sort-by due-date
python main.py list-tasks --sort-by title

# Complete or delete a task (use the ID printed when adding)
python main.py complete-task <task-id>
python main.py delete-task <task-id>

# Use SQLite instead of JSON
python main.py add-task "Another task" --storage sqlite
python main.py list-tasks --storage sqlite
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `TaskModel` accepts a `TaskRepository` via constructor | Dependency Inversion — business logic never depends on a concrete backend |
| Observers notified after every mutation | Open/Closed — new reactions (email, Slack) require only a new observer class |
| `SortStrategy` uses `sorted()` not `.sort()` | Returns a new list; never mutates the original task list |
| `retry_decorator` always re-raises after exhaustion | Failing silently and returning `None` would be worse than crashing loudly |
| PlantUML for diagrams | Diagrams are text files — they can be version-controlled and reviewed in PRs |

---

## Pylint Score: 8.68/ 10

---

