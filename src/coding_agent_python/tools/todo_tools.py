from typing import Literal

from .core_tools import tool

TodoStatus = Literal["pending", "in_progress", "complete"]

_todos: list[dict[str, str]] = []


def _format_todos() -> str:
    if not _todos:
        return "(no todos)"
    icons = {"pending": "[ ]", "in_progress": "[~]", "complete": "[x]"}
    lines = [
        f"{icons.get(t['status'], '[ ]')} {i + 1}. {t['task']}"
        for i, t in enumerate(_todos)
    ]
    return "\n".join(lines)


@tool(
    description=(
        "Create or replace the todo list with a fresh set of tasks. "
        "Call this before starting any multi-step task to lay out your plan. "
        "All tasks start with status 'pending'. Returns the full list."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "todos": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ordered list of tasks to complete.",
            },
        },
        "required": ["todos"],
    },
)
def todo_write(todos: list[str]) -> str:
    global _todos
    _todos = [{"task": t, "status": "pending"} for t in todos]
    return _format_todos()


@tool(
    description=(
        "Update the status of a todo item by its 1-based index. "
        "Valid statuses: 'pending', 'in_progress', 'complete'. "
        "Call this after finishing each step. Returns the full updated list."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "index": {
                "type": "integer",
                "description": "1-based index of the todo item to update.",
            },
            "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "complete"],
                "description": "New status for the item.",
            },
        },
        "required": ["index", "status"],
    },
)
def todo_update(index: int, status: TodoStatus) -> str:
    if not _todos:
        return "Error: no todos exist. Call todo_write first."
    if index < 1 or index > len(_todos):
        return f"Error: index {index} out of range (1-{len(_todos)})."
    _todos[index - 1]["status"] = status
    return _format_todos()


@tool(
    description="Return the current todo list without modifying it.",
    input_schema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
def todo_read() -> str:
    return _format_todos()
