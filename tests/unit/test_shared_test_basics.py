"""Basic tests for apps_shared utilities."""
from apps_shared.domain.constants import EXCLUDED_DIRS
from apps_shared.utils.text_processing import clean_llm_code
from typing import Any

def test_clean_llm_code_strips_markdown() -> Any:
    """Test that clean_llm_code correctly strips markdown code blocks."""
    input_text: Any = "```python\nprint('hello world')\n```"
    expected: Any = "print('hello world')"
    assert clean_llm_code(input_text) == expected
    input_text: Any = '```\ndef test():\n    return True\n```'
    expected: Any = 'def test():\n    return True'
    assert clean_llm_code(input_text) == expected
    input_text: Any = "print('no markdown')"
    expected: Any = "print('no markdown')"
    assert clean_llm_code(input_text) == expected

def test_excluded_dirs_constants() -> Any:
    """Test that EXCLUDED_DIRS contains expected values."""
    assert '.git' in EXCLUDED_DIRS
    assert '__pycache__' in EXCLUDED_DIRS
    assert '.pytest_cache' in EXCLUDED_DIRS
    assert 'node_modules' in EXCLUDED_DIRS
