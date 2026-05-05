import pytest

import coding_agent_python.tools.todo_tools as todo_tools_module
from coding_agent_python.tools import todo_read, todo_update, todo_write


@pytest.fixture(autouse=False)
def reset_todos() -> None:
    todo_tools_module._todos.clear()


class TestTodoWrite:
    def test_creates_todo_list(self, reset_todos: None) -> None:
        result = todo_write(["task one", "task two"])
        assert "task one" in result
        assert "task two" in result

    def test_all_tasks_start_pending(self, reset_todos: None) -> None:
        result = todo_write(["a", "b"])
        assert result.count("[ ]") == 2

    def test_tasks_are_numbered_from_one(self, reset_todos: None) -> None:
        result = todo_write(["first", "second"])
        assert "1. first" in result
        assert "2. second" in result

    def test_replaces_existing_list(self, reset_todos: None) -> None:
        todo_write(["old task"])
        result = todo_write(["new task"])
        assert "old task" not in result
        assert "new task" in result

    def test_empty_list(self, reset_todos: None) -> None:
        result = todo_write([])
        assert result == "(no todos)"


class TestTodoUpdate:
    def test_marks_task_complete(self, reset_todos: None) -> None:
        todo_write(["do something"])
        result = todo_update(1, "complete")
        assert "[x]" in result

    def test_marks_task_in_progress(self, reset_todos: None) -> None:
        todo_write(["step one", "step two"])
        result = todo_update(2, "in_progress")
        assert "[~]" in result

    def test_marks_task_pending(self, reset_todos: None) -> None:
        todo_write(["a"])
        todo_update(1, "complete")
        result = todo_update(1, "pending")
        assert "[ ]" in result

    def test_returns_full_list(self, reset_todos: None) -> None:
        todo_write(["a", "b", "c"])
        result = todo_update(2, "complete")
        assert "a" in result
        assert "b" in result
        assert "c" in result

    def test_out_of_range_index_returns_error(self, reset_todos: None) -> None:
        todo_write(["only one"])
        result = todo_update(5, "complete")
        assert result.startswith("Error:")

    def test_zero_index_returns_error(self, reset_todos: None) -> None:
        todo_write(["task"])
        result = todo_update(0, "complete")
        assert result.startswith("Error:")

    def test_no_todos_returns_error(self, reset_todos: None) -> None:
        result = todo_update(1, "complete")
        assert result.startswith("Error:")


class TestTodoRead:
    def test_returns_placeholder_when_empty(self, reset_todos: None) -> None:
        assert todo_read() == "(no todos)"

    def test_returns_current_list(self, reset_todos: None) -> None:
        todo_write(["alpha", "beta"])
        result = todo_read()
        assert "alpha" in result
        assert "beta" in result

    def test_does_not_modify_list(self, reset_todos: None) -> None:
        todo_write(["x"])
        todo_read()
        result = todo_read()
        assert "x" in result
