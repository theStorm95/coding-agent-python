"""
Integration tests for the full agent loop.

The Anthropic client is mocked to control the conversation flow, but all tool
implementations (read_file, write_file, etc.) run for real against tmp_path.
This validates that tool outputs are correctly passed back into the message
history and ultimately influence the agent's final response.
"""

from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, patch

from anthropic.types import MessageParam

from coding_agent_python.core import agent_loop


def _text_block(text: str) -> MagicMock:
    b = MagicMock()
    b.type = "text"
    b.text = text
    return b


def _tool_block(name: str, inputs: dict, tool_id: str) -> MagicMock:
    b = MagicMock()
    b.type = "tool_use"
    b.name = name
    b.input = inputs
    b.id = tool_id
    return b


def _response(content: list, stop_reason: str) -> MagicMock:
    r = MagicMock()
    r.content = content
    r.stop_reason = stop_reason
    return r


class TestAgentWithFileTools:
    def test_agent_reads_file_and_returns_response(self, tmp_path: Path) -> None:
        target = tmp_path / "hello.txt"
        target.write_text("world content")

        responses = [
            _response([_tool_block("read_file", {"path": str(target)}, "t1")], "tool_use"),
            _response([_text_block("The file says: world content")], "end_turn"),
        ]

        with patch("coding_agent_python.core.agent_loop.client") as mock_client:
            mock_client.messages.create.side_effect = responses
            messages: list[MessageParam] = [{"role": "user", "content": "read hello.txt"}]
            result = agent_loop.run(messages)

        assert result == "The file says: world content"
        # The real file content should have been passed back to the model
        tool_result_content = cast(list[dict[str, Any]],messages[2]["content"])[0]["content"]
        assert "world content" in tool_result_content

    def test_agent_writes_then_reads_file(self, tmp_path: Path) -> None:
        write_path = str(tmp_path / "new.txt")

        responses = [
            _response(
                [_tool_block("write_file", {"path": write_path, "content": "written!"}, "t1")],
                "tool_use",
            ),
            _response([_tool_block("read_file", {"path": write_path}, "t2")], "tool_use"),
            _response([_text_block("All done")], "end_turn"),
        ]

        with patch("coding_agent_python.core.agent_loop.client") as mock_client:
            mock_client.messages.create.side_effect = responses
            messages: list[MessageParam] = [{"role": "user", "content": "write then read"}]
            result = agent_loop.run(messages)

        assert result == "All done"
        assert Path(write_path).read_text() == "written!"
        assert mock_client.messages.create.call_count == 3
        # Second tool result should contain the written content
        read_result = cast(list[dict[str, Any]],messages[4]["content"])[0]["content"]
        assert "written!" in read_result

    def test_agent_lists_directory_contents(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("")
        (tmp_path / "b.py").write_text("")

        responses = [
            _response([_tool_block("list_directory", {"path": str(tmp_path)}, "t1")], "tool_use"),
            _response([_text_block("Listed the files")], "end_turn"),
        ]

        with patch("coding_agent_python.core.agent_loop.client") as mock_client:
            mock_client.messages.create.side_effect = responses
            messages: list[MessageParam] = [{"role": "user", "content": "list files"}]
            result = agent_loop.run(messages)

        assert result == "Listed the files"
        listing = cast(list[dict[str, Any]],messages[2]["content"])[0]["content"]
        assert "a.py" in listing
        assert "b.py" in listing

    def test_agent_executes_bash_command(self) -> None:
        responses = [
            _response(
                [_tool_block("execute_bash", {"command": "echo integration_test"}, "t1")],
                "tool_use",
            ),
            _response([_text_block("Command ran successfully")], "end_turn"),
        ]

        with patch("coding_agent_python.core.agent_loop.client") as mock_client:
            mock_client.messages.create.side_effect = responses
            messages: list[MessageParam] = [{"role": "user", "content": "run a command"}]
            result = agent_loop.run(messages)

        assert result == "Command ran successfully"
        bash_result = cast(list[dict[str, Any]],messages[2]["content"])[0]["content"]
        assert "integration_test" in bash_result

    def test_message_history_grows_correctly_across_turns(self, tmp_path: Path) -> None:
        f = tmp_path / "data.txt"
        f.write_text("42")

        responses = [
            _response([_tool_block("read_file", {"path": str(f)}, "t1")], "tool_use"),
            _response([_text_block("The answer is 42")], "end_turn"),
        ]

        with patch("coding_agent_python.core.agent_loop.client") as mock_client:
            mock_client.messages.create.side_effect = responses
            messages: list[MessageParam] = [{"role": "user", "content": "what is in data.txt?"}]
            agent_loop.run(messages)

        # [user, assistant(tool_use), user(tool_result), assistant(end_turn)]
        assert len(messages) == 4
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"
        assert messages[3]["role"] == "assistant"
