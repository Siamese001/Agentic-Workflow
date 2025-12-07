# ReAct Pattern – Production Implementation Guide

## Overview

ReAct (Reasoning + Acting) is a prompting paradigm that interleaves reasoning traces
with action execution, enabling more robust and interpretable agent behavior.

## Core Loop

```
Thought → Action → Observation → Thought → ... → Final Answer
```

## Implementation

```python
from openai import OpenAI
from typing import Callable

class ReActAgent:
    """Production ReAct agent with tool execution."""

    def __init__(
        self,
        client: OpenAI,
        tools: dict[str, Callable],
        max_iterations: int = 10,
    ):
        self.client = client
        self.tools = tools
        self.max_iterations = max_iterations

    def run(self, query: str) -> str:
        """Execute ReAct loop until final answer or max iterations."""
        messages = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": query},
        ]

        for i in range(self.max_iterations):
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=self._format_tools(),
            )

            message = response.choices[0].message

            # Check for final answer
            if not message.tool_calls:
                return message.content

            # Execute tool calls
            messages.append(message)
            for tool_call in message.tool_calls:
                result = self._execute_tool(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        return "Max iterations reached without final answer"

    def _system_prompt(self) -> str:
        return """You are a ReAct agent. For each step:
1. Thought: Analyze what you know and what you need
2. Action: Call a tool if needed
3. Observation: Process the tool result
4. Repeat until you can provide a Final Answer

Always explain your reasoning before taking actions."""

    def _execute_tool(self, tool_call) -> str:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        return str(self.tools[name](**args))
```

## Best Practices

1. **Explicit Reasoning**: Require the model to explain its thought process
2. **Tool Descriptions**: Provide clear, detailed tool descriptions
3. **Error Handling**: Gracefully handle tool execution failures
4. **Iteration Limits**: Always set maximum iteration bounds
5. **Observation Formatting**: Structure tool outputs for easy parsing

## Example Trace

```
User: What's the weather in Tokyo and should I bring an umbrella?

Thought: I need to check the current weather in Tokyo to answer this question.
Action: get_weather(location="Tokyo")
Observation: {"temp": 22, "condition": "light rain", "humidity": 85}

Thought: The weather shows light rain in Tokyo. I should recommend an umbrella.
Final Answer: The weather in Tokyo is 22°C with light rain and 85% humidity.
Yes, you should definitely bring an umbrella!
```

## References

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
