# Coding Agent Python

A Python-based AI coding agent that leverages Claude to help with development tasks. The agent can read files, write files, list directories, and execute bash commands to assist with coding workflows.

## Features

- **Interactive CLI** - Chat with Claude directly from your terminal
- **Tool Integration** - Automatically handles file operations and command execution
- **Multi-turn Conversations** - Maintain context across multiple interactions
- **Rich Output** - Formatted responses with markdown support

## Prerequisites

- Python 3.13 or higher
- An Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd coding-agent-python
```

### 2. Set Up Your Environment

#### Option A: Using `uv` (Recommended)

If you don't have `uv` installed, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then set up the project:

```bash
uv sync
```

### 3. Configure Your API Key

Create a `.env` file in the project root with your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

Or set it as an environment variable:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### 4. Run the Agent

```bash
uv run app
```

Or if using venv:

```bash
python -m coding_agent_python.main
```

## Usage

Once the agent is running, you'll see a prompt:

```bash
Claude CLI - type 'quit' or 'exit' to stop

You:
```

Simply type your requests and the agent will help you with:

- Reading and writing files
- Listing directories
- Running bash commands
- General coding assistance

Example interactions:

```bash
You: Can you check what files are in the current directory?
You: Update the README with setup instructions
You: Run the tests
You: quit
```

## Development

### Project Structure

```python
coding-agent-python/
├── src/coding_agent_python/
│   ├── main.py           # CLI entry point
│   ├── agent_loop.py     # Agent logic
│   ├── tools.py          # Tool definitions
│   └── __init__.py
├── tests/
│   ├── unit/             # Unit tests (mocked Anthropic client)
│   └── integration/      # Integration tests (real tools, mocked client)
├── noxfile.py            # Nox session definitions
├── pyproject.toml        # Project configuration
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

### Available Tools

The agent has access to the following tools:

- **read_file** - Read file contents
- **write_file** - Create or overwrite files
- **list_directory** - List files and directories
- **execute_bash** - Run bash commands

## Requirements

See `pyproject.toml` for full dependencies:

- `anthropic>=0.97.0` - Anthropic API client
- `python-dotenv>=1.2.2` - Environment variable management
- `rich>=15.0.0` - Rich terminal formatting

## License

[Add your license here]

## Checks

Install dev dependencies first:

```bash
uv sync --group dev
```

Run all checks (lint, formatting, type checking, and tests) with:

```bash
uv run nox
```

Run a single session:

```bash
uv run nox -s lint        # ruff linting
uv run nox -s fmt         # ruff formatting
uv run nox -s typecheck   # mypy strict
uv run nox -s unit        # unit tests
uv run nox -s integration # integration tests
```

## Contributing

1. Make your changes.
2. Run `uv run nox` — all five sessions must pass before submitting a pull request.
3. Add or update tests for any new behaviour under `tests/unit/` or `tests/integration/` as appropriate.
