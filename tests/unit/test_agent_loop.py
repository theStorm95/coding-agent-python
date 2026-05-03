from typing import cast
from unittest.mock import MagicMock, patch

from anthropic.types import MessageParam, ToolResultBlockParam

from coding_agent_python import agent_loop


def _text_block(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def _tool_block(name: str, inputs: dict, tool_id: str = "tool_1") -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.name = name
    block.input = inputs
    block.id = tool_id
    return block


def _response(content: list, stop_reason: str) -> MagicMock:
    response = MagicMock()
    response.content = content
    response.stop_reason = stop_reason
    return response


class TestRun:
    def test_returns_text_on_end_turn(self) -> None:
        mock_response = _response([_text_block("Hello!")], "end_turn")

        with patch("coding_agent_python.agent_loop.client") as mock_client:
            mock_client.messages.create.return_value = mock_response
            messages: list[MessageParam] = [{"role": "user", "content": "hi"}]
            result = agent_loop.run(messages)

        assert result == "Hello!"

    def test_returns_empty_string_when_no_text_block(self) -> None:
        mock_response = _response([], "end_turn")

        with patch("coding_agent_python.agent_loop.client") as mock_client:
            mock_client.messages.create.return_value = mock_response
            messages: list[MessageParam] = [{"role": "user", "content": "hi"}]
            result = agent_loop.run(messages)

        assert result == ""

    def test_appends_assistant_message_to_history(self) -> None:
        text_block = _text_block("response")
        mock_response = _response([text_block], "end_turn")

        with patch("coding_agent_python.agent_loop.client") as mock_client:
            mock_client.messages.create.return_value = mock_response
            messages: list[MessageParam] = [{"role": "user", "content": "hi"}]
            agent_loop.run(messages)

        assert messages[-1] == {"role": "assistant", "content": [text_block]}

    def test_tool_use_then_end_turn(self) -> None:
        tool_response = _response([_tool_block("execute_bash", {"command": "echo hi"})], "tool_use")
        end_response = _response([_text_block("Done")], "end_turn")

        with patch("coding_agent_python.agent_loop.client") as mock_client:
            mock_client.messages.create.side_effect = [tool_response, end_response]
            messages: list[MessageParam] = [{"role": "user", "content": "run echo"}]
            result = agent_loop.run(messages)

        assert result == "Done"
        assert mock_client.messages.create.call_count == 2

    def test_tool_result_appended_to_messages(self) -> None:
        tool_response = _response(
            [_tool_block("execute_bash", {"command": "echo test"}, "tid_1")], "tool_use"
        )
        end_response = _response([_text_block("done")], "end_turn")

        with patch("coding_agent_python.agent_loop.client") as mock_client:
            mock_client.messages.create.side_effect = [tool_response, end_response]
            messages: list[MessageParam] = [{"role": "user", "content": "run it"}]
            agent_loop.run(messages)

        # messages: [user, assistant(tool_use), user(tool_result), assistant(end)]
        tool_result_msg = messages[2]
        assert tool_result_msg["role"] == "user"
        content = cast(list[ToolResultBlockParam], tool_result_msg["content"])
        assert len(content) == 1
        assert content[0]["type"] == "tool_result"
        assert content[0]["tool_use_id"] == "tid_1"

    def test_multiple_tool_calls_in_one_turn(self) -> None:
        tool_response = _response(
            [
                _tool_block("execute_bash", {"command": "echo a"}, "t1"),
                _tool_block("execute_bash", {"command": "echo b"}, "t2"),
            ],
            "tool_use",
        )
        end_response = _response([_text_block("both done")], "end_turn")

        with patch("coding_agent_python.agent_loop.client") as mock_client:
            mock_client.messages.create.side_effect = [tool_response, end_response]
            messages: list[MessageParam] = [{"role": "user", "content": "run both"}]
            result = agent_loop.run(messages)

        assert result == "both done"
        tool_results = cast(list[ToolResultBlockParam], messages[2]["content"])
        assert len(tool_results) == 2
        assert {r["tool_use_id"] for r in tool_results} == {"t1", "t2"}
