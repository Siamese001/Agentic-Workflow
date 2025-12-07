"""
Minimal Production Agent Example
Version: 1.0
Compatible with: openai>=1.0.0

A complete, production-ready agent implementation with tool calling,
error handling, and observability.
"""

import json
import logging
from typing import Callable
from openai import OpenAI
from openai import APIError, RateLimitError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MinimalAgent:
    """Production-ready agent with tool execution."""

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "gpt-4o",
        max_iterations: int = 10,
    ):
        self.client = client or OpenAI()
        self.model = model
        self.max_iterations = max_iterations
        self.tools: dict[str, Callable] = {}
        self.tool_schemas: list[dict] = []

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: dict,
    ) -> None:
        """Register a tool for the agent to use."""
        self.tools[name] = func
        self.tool_schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        })

    def run(self, query: str, system_prompt: str | None = None) -> str:
        """Execute agent loop until completion or max iterations."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": query})

        for iteration in range(self.max_iterations):
            logger.info(f"Agent iteration {iteration + 1}/{self.max_iterations}")

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tool_schemas if self.tool_schemas else None,
                )
            except RateLimitError:
                logger.warning("Rate limited, waiting...")
                import time
                time.sleep(5)
                continue
            except APIError as e:
                logger.error(f"API error: {e}")
                raise

            message = response.choices[0].message

            # No tool calls = final answer
            if not message.tool_calls:
                logger.info("Agent completed with final answer")
                return message.content or ""

            # Execute tool calls
            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.info(f"Executing tool: {tool_name}({tool_args})")

                try:
                    result = self.tools[tool_name](**tool_args)
                except Exception as e:
                    result = f"Error: {e}"
                    logger.error(f"Tool execution failed: {e}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })

        logger.warning("Max iterations reached")
        return "I was unable to complete the task within the allowed iterations."


# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = MinimalAgent(model="gpt-4o-mini")

    # Register tools
    agent.register_tool(
        name="get_weather",
        func=lambda location: f"Weather in {location}: 22°C, sunny",
        description="Get current weather for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name",
                },
            },
            "required": ["location"],
        },
    )

    agent.register_tool(
        name="calculate",
        func=lambda expression: eval(expression),  # Note: Use safe eval in production
        description="Evaluate a mathematical expression",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate",
                },
            },
            "required": ["expression"],
        },
    )

    # Run agent
    result = agent.run(
        query="What's the weather in Tokyo and what's 15% of 250?",
        system_prompt="You are a helpful assistant. Use tools when needed.",
    )

    print(f"\nFinal Answer: {result}")
