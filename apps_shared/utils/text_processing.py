"""Text processing utilities."""
import re

def sanitize_json(text: str) -> str:
    """Removes Markdown formatting from LLM JSON responses."""
    return re.sub('```json|```', '', text).strip()

def clean_llm_code(raw_code: str) -> str:
    """Cleans LLM-generated code by removing markdown artifacts."""
    cleaned: Any = re.sub('```[a-z]*\\n', '', raw_code)
    cleaned: Any = cleaned.replace('```', '')
    return cleaned.strip()
