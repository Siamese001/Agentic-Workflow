"""Minimal Anthropic Reference Client
Production-ready minimal client for quick integration with prompt caching.
"""

import os

from anthropic import Anthropic


def simple_message(prompt: str, model: str = "claude-3-5-sonnet-20241022") -> str:
    """Simple message completion with Anthropic.

    Args:
        prompt: Input prompt text
        model: Anthropic model to use

    Returns:
        Generated response text
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # guardian: allow-magic-config
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )

    return response.content[0].text


def cached_message(prompt: str, system_prompt: str = None) -> str:
    """Message with prompt caching for cost optimization.

    Args:
        prompt: Input prompt text
        system_prompt: Optional system prompt to cache

    Returns:
        Generated response text
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Build system prompt with caching
    system_content = []
    if system_prompt:
        system_content.append({"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}})

    # guardian: allow-magic-config
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        system=system_content if system_content else None,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )

    return response.content[0].text


def tool_use_message(prompt: str, tools: list) -> dict:
    """Message with tool use capabilities.

    Args:
        prompt: Input prompt text
        tools: List of tool specifications

    Returns:
        Response with content and tool calls
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # guardian: allow-magic-config
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        tools=tools,
    )

    content = ""
    tool_calls = []

    for content_block in response.content:
        if content_block.type == "text":
            content += content_block.text
        elif content_block.type == "tool_use":
            tool_calls.append(
                {"id": content_block.id, "name": content_block.name, "input": content_block.input},
            )

    return {"content": content, "tool_calls": tool_calls}


if __name__ == "__main__":
    # Test simple message
    # print(simple_message("Hello, Claude!")) # Example call

    # Test cached message
    cached_message("Summarize quantum computing", system_prompt="You are an expert physics educator.")

    # Test tool use
    tools = [
        {
            "name": "get_weather",
            "description": "Get weather information",
            "input_schema": {"type": "object", "properties": {"location": {"type": "string"}}},
        },
    ]
    # print(tool_use_message("What's the weather like in San Francisco?", tools)) # Example call
