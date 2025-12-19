"""Tests for extracted utilities from the monolith."""

from apps_shared.utils.text_processing import clean_llm_code


def test_clean_llm_code():
    """Test that clean_llm_code removes markdown artifacts."""
    # Test input with markdown code block
    input_text = "```python\nprint('hello')\n```"
    expected_output = "print('hello')"
    
    result = clean_llm_code(input_text)
    
    assert result == expected_output, f"Expected '{expected_output}', got '{result}'"


def test_clean_llm_code_with_language_specifier():
    """Test clean_llm_code with different language specifiers."""
    input_text = "```python\n\ndef test():\n    return True\n```"
    expected_output = "def test():\n    return True"
    
    result = clean_llm_code(input_text)
    
    assert result == expected_output, f"Expected '{expected_output}', got '{result}'"


def test_clean_llm_code_without_markdown():
    """Test clean_llm_code with plain text (no markdown)."""
    input_text = "print('no markdown here')"
    expected_output = "print('no markdown here')"
    
    result = clean_llm_code(input_text)
    
    assert result == expected_output, f"Expected '{expected_output}', got '{result}'"
