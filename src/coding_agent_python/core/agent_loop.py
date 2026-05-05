import os

import anthropic
from anthropic.types import MessageParam, ToolResultBlockParam
from dotenv import load_dotenv
from rich.console import Console

from coding_agent_python import tools

load_dotenv()

client = anthropic.Anthropic()
console = Console()

SYSTEM_PROMPT = (
    f"You are a coding agent at {os.getcwd()}. "
    "Before working on any multi-step task, ALWAYS call todo_write first "
    "to write your complete plan. Execute each step in order. "
    "Call todo_update after completing each step."
)


def run(messages: list[MessageParam]) -> str:
    while True:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=8096,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=tools.DEFINITIONS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return ""

        tool_results: list[ToolResultBlockParam] = []
        for block in response.content:
            if block.type == "tool_use":
                console.print(f"  tool: {block.name}", style="bold yellow")
                console.print(f"  input: {block.input}", style="dim")
                result = tools.handle(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        messages.append({"role": "user", "content": tool_results})
