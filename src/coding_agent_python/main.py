from anthropic.types import MessageParam
from rich.console import Console
from rich.markdown import Markdown

from coding_agent_python.core import agent_loop

console = Console()


def main() -> None:
    messages: list[MessageParam] = []

    console.print("Claude CLI - type 'quit' or 'exit' to stop\n", style="dim")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break

        messages.append({"role": "user", "content": user_input})

        response_text = agent_loop.run(messages)

        console.print("Claude:", style="bold cyan")
        console.print(Markdown(response_text))
        messages.append({"role": "assistant", "content": response_text})


if __name__ == "__main__":
    main()
