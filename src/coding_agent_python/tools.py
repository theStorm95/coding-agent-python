import subprocess
from pathlib import Path

from anthropic.types import ToolParam


DEFINITIONS: list[ToolParam] = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to read."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file, creating it or overwriting it if it exists.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to write."},
                "content": {"type": "string", "description": "Content to write."},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and directories at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path to list. Defaults to current directory.", "default": "."},
            },
            "required": [],
        },
    },
    {
        "name": "execute_bash",
        "description": "Execute a bash command and return its output.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The bash command to run."},
            },
            "required": ["command"],
        },
    },
]


def read_file(path: str) -> str:
    return Path(path).read_text()


def write_file(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} bytes to {path}"


def list_directory(path: str = ".") -> str:
    entries = sorted(Path(path).iterdir(), key=lambda e: (e.is_file(), e.name))
    return "\n".join(e.name + ("/" if e.is_dir() else "") for e in entries)


def execute_bash(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout
    if result.stderr:
        output += f"\nstderr:\n{result.stderr}"
    return output or "(no output)"


def handle(name: str, inputs: dict) -> str:
    try:
        match name:
            case "read_file":
                return read_file(**inputs)
            case "write_file":
                return write_file(**inputs)
            case "list_directory":
                return list_directory(**inputs)
            case "execute_bash":
                return execute_bash(**inputs)
            case _:
                return f"Unknown tool: {name}"
    except Exception as e:
        return f"Error: {e}"
