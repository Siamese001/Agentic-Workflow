"""
Structured Output Examples with JSON Mode
Version: 1.0
Compatible with: openai>=1.0.0

Demonstrates reliable JSON output generation using OpenAI's JSON mode
and structured outputs feature.
"""

import json
from openai import OpenAI
from pydantic import BaseModel


# Method 1: JSON Mode (simple)
def json_mode_example(client: OpenAI, query: str) -> dict:
    """
    Use JSON mode for simple structured outputs.
    Requires explicit JSON instruction in the prompt.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Always respond in valid JSON format.",
            },
            {
                "role": "user",
                "content": f"Analyze this and return JSON with 'sentiment', 'confidence', and 'keywords' fields: {query}",
            },
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


# Method 2: Structured Outputs with Pydantic (recommended)
class SentimentAnalysis(BaseModel):
    """Structured output schema for sentiment analysis."""
    sentiment: str
    confidence: float
    keywords: list[str]
    reasoning: str


def structured_output_example(client: OpenAI, query: str) -> SentimentAnalysis:
    """
    Use structured outputs with Pydantic for type-safe responses.
    This is the recommended approach for production.
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Analyze the sentiment of the provided text.",
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        response_format=SentimentAnalysis,
    )

    return response.choices[0].message.parsed


# Method 3: Function calling for structured extraction
def function_calling_example(client: OpenAI, query: str) -> dict:
    """
    Use function calling to extract structured data.
    Useful when you need to extract specific entities.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "record_analysis",
                "description": "Record the sentiment analysis results",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sentiment": {
                            "type": "string",
                            "enum": ["positive", "negative", "neutral"],
                            "description": "Overall sentiment",
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Confidence score",
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key terms from the text",
                        },
                    },
                    "required": ["sentiment", "confidence", "keywords"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Analyze the sentiment and call the record_analysis function.",
            },
            {"role": "user", "content": query},
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "record_analysis"}},
    )

    tool_call = response.choices[0].message.tool_calls[0]
    return json.loads(tool_call.function.arguments)


# Example usage
if __name__ == "__main__":
    client = OpenAI()
    test_text = "I absolutely love this product! It exceeded all my expectations."

    print("=== JSON Mode ===")
    result1 = json_mode_example(client, test_text)
    print(json.dumps(result1, indent=2))

    print("\n=== Structured Outputs ===")
    result2 = structured_output_example(client, test_text)
    print(result2.model_dump_json(indent=2))

    print("\n=== Function Calling ===")
    result3 = function_calling_example(client, test_text)
    print(json.dumps(result3, indent=2))
