"""Tests for extracted utilities from the monolith."""
from apps_shared.utils.text_processing import clean_llm_code
from typing import Any

def test_clean_llm_code() -> Any:
    """Test that clean_llm_code removes markdown artifacts."""
    input_text: Any = "```python\nprint('hello')\n```"
    expected_output: Any = "print('hello')"
    result: Any = clean_llm_code(input_text)
    assert result == expected_output, f"Expected '{expected_output}', got '{result}'"

def test_clean_llm_code_with_language_specifier() -> Any:
    """Test clean_llm_code with different language specifiers."""
    input_text: Any = '```python\n\ndef test():\n    return True\n```'
    expected_output: Any = 'def test():\n    return True'
    result: Any = clean_llm_code(input_text)
    assert result == expected_output, f"Expected '{expected_output}', got '{result}'"

def test_clean_llm_code_without_markdown() -> Any:
    """Test clean_llm_code with plain text (no markdown)."""
    input_text: Any = "print('no markdown here')"
    expected_output: Any = "print('no markdown here')"
    result: Any = clean_llm_code(input_text)
    assert result == expected_output, f"Expected '{expected_output}', got '{result}'"
