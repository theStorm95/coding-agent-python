import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from anthropic.types import ToolParam

DEFINITIONS: list[ToolParam] = []
_handlers: dict[str, Callable[..., str]] = {}

FuncT = Callable[..., str]


def tool(description: str, input_schema: dict[str, Any]) -> Callable[[FuncT], FuncT]:
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        DEFINITIONS.append(
            {
                "name": func.__name__,
                "description": description,
                "input_schema": input_schema,
            }
        )
        _handlers[func.__name__] = func
        return func

    return decorator


@tool(
    description=(
        "Read the contents of a file, with every line prefixed by its line number. "
        "Use `start_line` and `end_line` to read a specific range instead of the whole file — "
        "prefer this for large files or when you already know the relevant section "
        "from grep results. "
        "Line numbers in the output can be passed back to `start_line`/`end_line` "
        "in follow-up calls."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file to read."},
            "start_line": {
                "type": "integer",
                "description": "First line to read, 1-indexed. Defaults to the start of the file.",
            },
            "end_line": {
                "type": "integer",
                "description": "Last line to read, inclusive. Defaults to the end of the file.",
            },
        },
        "required": ["path"],
    },
)
def read_file(path: str, start_line: int | None = None, end_line: int | None = None) -> str:
    lines = Path(path).read_text().splitlines()

    start = (start_line - 1) if start_line is not None else 0
    end = end_line if end_line is not None else len(lines)

    selected = lines[start:end]
    return "\n".join(f"{start + i + 1}: {line}" for i, line in enumerate(selected))


@tool(
    description=(
        "Write content to a file. Without `start_line`/`end_line`, creates or overwrites the "
        "whole file. With a line range, replaces only those lines and preserves the rest — "
        "use this to make targeted edits after reading line numbers from `read_file`. "
        "`start_line` and `end_line` are 1-indexed and inclusive."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file to write."},
            "content": {
                "type": "string",
                "description": "Content to write (or replacement for the given line range).",
            },
            "start_line": {
                "type": "integer",
                "description": "First line to replace, 1-indexed.",
            },
            "end_line": {
                "type": "integer",
                "description": "Last line to replace, inclusive.",
            },
        },
        "required": ["path", "content"],
    },
)
def write_file(
    path: str, content: str, start_line: int | None = None, end_line: int | None = None
) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if start_line is None and end_line is None:
        p.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"

    lines = p.read_text().splitlines(keepends=True)
    start = (start_line - 1) if start_line is not None else 0
    end = end_line if end_line is not None else len(lines)

    replacement = content if content.endswith("\n") else content + "\n"
    lines[start:end] = [replacement]

    p.write_text("".join(lines))

    return f"Replaced lines {start + 1}-{end} in {path}"


@tool(
    description="List files and directories at the given path.",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to list. Defaults to current directory.",
                "default": ".",
            },
        },
        "required": [],
    },
)
def list_directory(path: str = ".") -> str:
    entries = sorted(Path(path).iterdir(), key=lambda e: (e.is_file(), e.name))
    return "\n".join(e.name + ("/" if e.is_dir() else "") for e in entries)


@tool(
    description="Execute a bash command and return its output.",
    input_schema={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The bash command to run."},
        },
        "required": ["command"],
    },
)
def execute_bash(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout
    if result.stderr:
        output += f"\nstderr:\n{result.stderr}"
    return output or "(no output)"


@tool(
    description=(
        "Search for a pattern in files and return matching lines with file paths and line numbers. "
        "Use this to locate where a function, class, variable, or string is defined or referenced. "
        "Prefer this over execute_bash for any search task — it returns structured, "
        "line-numbered results and handles recursive search automatically. "
        "`pattern` is an extended regular expression (supports `+`, `?`, `|`, `()`). "
        "Narrow results with `include` (e.g. '*.py') when you know the file type."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Regular expression to search for.",
            },
            "path": {
                "type": "string",
                "description": "File or directory to search. Defaults to current directory.",
                "default": ".",
            },
            "include": {
                "type": "string",
                "description": "Glob pattern to restrict which files are searched (e.g. '*.py').",
            },
        },
        "required": ["pattern"],
    },
)
def grep(pattern: str, path: str = ".", include: str | None = None) -> str:
    cmd = ["grep", "-Ern", "--color=never", pattern, path]
    if include:
        cmd += ["--include", include]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() or "(no matches)"


def handle(name: str, inputs: dict[str, Any]) -> str:
    handler = _handlers.get(name)
    if handler is None:
        return f"Unknown tool: {name}"
    try:
        return handler(**inputs)
    except Exception as e:
        return f"Error: {e}"
