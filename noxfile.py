import nox

nox.options.default_venv_backend = "uv"
nox.options.sessions = ["lint", "fmt", "typecheck", "unit", "integration"]

PYTHON = "3.13"


@nox.session(python=PYTHON)
def lint(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", "check", ".")


@nox.session(python=PYTHON)
def fmt(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", "format", "--check", ".")


@nox.session(python=PYTHON)
def typecheck(session: nox.Session) -> None:
    session.install("-e", ".", "mypy")
    session.run("mypy", "src")


@nox.session(python=PYTHON)
def unit(session: nox.Session) -> None:
    session.install("-e", ".", "pytest")
    session.run("pytest", "tests/unit", "-v", *session.posargs)


@nox.session(python=PYTHON)
def integration(session: nox.Session) -> None:
    session.install("-e", ".", "pytest")
    session.run("pytest", "tests/integration", "-v", *session.posargs)
