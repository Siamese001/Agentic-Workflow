"""
Function Calling Patterns
Version: 1.0
Compatible with: openai>=1.0.0

Comprehensive examples of OpenAI function calling patterns
for production applications.
"""

import json
from typing import Any
from openai import OpenAI


# Pattern 1: Basic Function Calling
def basic_function_calling(client: OpenAI, query: str) -> dict:
    """
    Basic function calling with a single tool.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name, e.g., 'Tokyo'",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature unit",
                        },
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
        tools=tools,
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        return {
            "function": tool_call.function.name,
            "arguments": json.loads(tool_call.function.arguments),
        }

    return {"response": message.content}


# Pattern 2: Parallel Function Calling
def parallel_function_calling(client: OpenAI, query: str) -> list[dict]:
    """
    Handle multiple function calls in a single response.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "Get current time for a timezone",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {"type": "string"},
                    },
                    "required": ["timezone"],
                },
            },
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
        tools=tools,
        parallel_tool_calls=True,
    )

    message = response.choices[0].message
    results = []

    if message.tool_calls:
        for tool_call in message.tool_calls:
            results.append({
                "id": tool_call.id,
                "function": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments),
            })

    return results


# Pattern 3: Forced Function Calling
def forced_function_calling(client: OpenAI, text: str) -> dict:
    """
    Force the model to call a specific function.
    Useful for structured data extraction.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "extract_entities",
                "description": "Extract named entities from text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "people": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Names of people mentioned",
                        },
                        "organizations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Organization names",
                        },
                        "locations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Location names",
                        },
                    },
                    "required": ["people", "organizations", "locations"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract entities from the text."},
            {"role": "user", "content": text},
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "extract_entities"}},
    )

    tool_call = response.choices[0].message.tool_calls[0]
    return json.loads(tool_call.function.arguments)


# Pattern 4: Function Calling with Execution Loop
def function_calling_loop(
    client: OpenAI,
    query: str,
    tools: list[dict],
    tool_implementations: dict[str, callable],
    max_iterations: int = 5,
) -> str:
    """
    Complete function calling loop with tool execution.
    """
    messages = [{"role": "user", "content": query}]

    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message

        # No tool calls = final answer
        if not message.tool_calls:
            return message.content or ""

        # Execute tools and add results
        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            # Execute the tool
            if func_name in tool_implementations:
                result = tool_implementations[func_name](**func_args)
            else:
                result = f"Error: Unknown function {func_name}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    return "Max iterations reached"


# Example usage
if __name__ == "__main__":
    client = OpenAI()

    print("=== Basic Function Calling ===")
    result = basic_function_calling(client, "What's the weather in Paris?")
    print(json.dumps(result, indent=2))

    print("\n=== Parallel Function Calling ===")
    results = parallel_function_calling(
        client, "What's the weather and time in Tokyo and New York?"
    )
    print(json.dumps(results, indent=2))

    print("\n=== Forced Function Calling ===")
    entities = forced_function_calling(
        client,
        "Elon Musk announced that Tesla will open a new factory in Berlin, Germany.",
    )
    print(json.dumps(entities, indent=2))
