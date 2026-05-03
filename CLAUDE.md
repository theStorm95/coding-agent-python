# Coding Agent Python

## Guidelines

- Follow Python best practices: PEP 8 style, idiomatic patterns, and clean structure.
- Use type annotations throughout — all function signatures, return types, and variables where the type is not immediately obvious.
- Always write tests for new code. Place tests in a `tests/` directory using `pytest`.

## Development

This project uses [nox](https://nox.thea.codes/) for task automation with `uv` as the venv backend.

Run all checks (lint, fmt, typecheck, unit, integration):

```bash
nox
```

Run a specific session:

```bash
nox -s lint
nox -s fmt
nox -s typecheck
nox -s unit
nox -s integration
```

Sessions:

- `lint` — runs `ruff check`
- `fmt` — runs `ruff format --check`
- `typecheck` — runs `mypy` on `src/`
- `unit` — runs `pytest tests/unit`
- `integration` — runs `pytest tests/integration`
