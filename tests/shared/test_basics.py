"""Basic tests for apps_shared utilities."""

import pytest
from apps_shared.utils.text_processing import clean_llm_code
from apps_shared.domain.constants import EXCLUDED_DIRS


def test_clean_llm_code_strips_markdown():
    """Test that clean_llm_code correctly strips markdown code blocks."""
    # Test with python markdown
    input_text = "```python\nprint('hello world')\n```"
    expected = "print('hello world')"
    assert clean_llm_code(input_text) == expected
    
    # Test with no language specifier
    input_text = "```\ndef test():\n    return True\n```"
    expected = "def test():\n    return True"
    assert clean_llm_code(input_text) == expected
    
    # Test with plain text (no markdown)
    input_text = "print('no markdown')"
    expected = "print('no markdown')"
    assert clean_llm_code(input_text) == expected


def test_excluded_dirs_constants():
    """Test that EXCLUDED_DIRS contains expected values."""
    assert '.git' in EXCLUDED_DIRS
    assert '__pycache__' in EXCLUDED_DIRS
    assert '.pytest_cache' in EXCLUDED_DIRS
    assert 'node_modules' in EXCLUDED_DIRS
