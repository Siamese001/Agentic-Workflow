"""Minimal OpenAI Reference Client
Production-ready minimal client for quick integration and testing.
"""

import json
import os



def simple_completion(prompt: str, model: str = "gpt-4o-2024-08-06") -> str:
    """Simple chat completion with OpenAI.

    Args:
        prompt: Input prompt text
        model: OpenAI model to use

    Returns:
        Generated response text
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )

    return response.choices[0].message.content


def structured_completion(prompt: str, schema: dict) -> dict:
    """Structured completion with JSON schema.

    Args:
        prompt: Input prompt text
        schema: JSON schema for output

    Returns:
        Structured response data
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": schema.get("title", "response"), "schema": schema},
        },
        max_tokens=2000,
        temperature=0.3,
    )

    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    # Test simple completion

    # Test structured completion
    schema = {
        "type": "object",
        "properties": {
            "topic": {"type": "string"},
            "summary": {"type": "string"},
            "key_points": {"type": "array", "items": {"type": "string"}},
        },
    }