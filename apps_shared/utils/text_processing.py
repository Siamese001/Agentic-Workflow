"""Text processing utilities."""

import re


def sanitize_json(text: str) -> str:
    """Removes Markdown formatting from LLM JSON responses."""
    return re.sub(r'```json|```', '', text).strip()


def clean_llm_code(raw_code: str) -> str:
    """Cleans LLM-generated code by removing markdown artifacts."""
    # Remove markdown code block markers
    cleaned = re.sub(r'```[a-z]*\n', '', raw_code)
    cleaned = cleaned.replace('```', '')
    return cleaned.strip()
