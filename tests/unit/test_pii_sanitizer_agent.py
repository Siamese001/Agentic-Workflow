# New file: tests/unit/test_pii_sanitizer_agent.py
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.guardrails.PIISanitizerAgent import PIISanitizerAgent


@pytest.fixture
def mock_context():
    """Mock context for agent instantiation."""
    context = Mock()
    return context


@pytest.fixture
def pii_sanitizer_agent(mock_context):
    """Fixture for fresh PIISanitizerAgent instance."""
    return PIISanitizerAgent(mock_context)


def test_instantiation(pii_sanitizer_agent):
    """Smoke test: agent instantiates without error."""
    assert pii_sanitizer_agent is not None
    assert hasattr(pii_sanitizer_agent, "run")
    assert hasattr(pii_sanitizer_agent, "PII_PATTERNS")
    assert hasattr(pii_sanitizer_agent, "_sanitize_text")


def test_pii_patterns_configured(pii_sanitizer_agent):
    """Test that PII patterns are properly configured."""
    patterns = pii_sanitizer_agent.PII_PATTERNS
    assert "EMAIL" in patterns
    assert "PHONE" in patterns
    assert "NAME" in patterns
    
    # Test pattern objects are regex compiled
    import re
    for pattern_name, pattern in patterns.items():
        assert isinstance(pattern, re.Pattern)


def test_sanitize_text_email(pii_sanitizer_agent):
    """Test email sanitization."""
    text_with_email = "Contact me at john.doe@example.com for more info."
    sanitized = pii_sanitizer_agent._sanitize_text(text_with_email)
    
    assert "[EMAIL_REDACTED]" in sanitized
    assert "john.doe@example.com" not in sanitized


def test_sanitize_text_phone(pii_sanitizer_agent):
    """Test phone number sanitization."""
    text_with_phone = "Call me at 555-123-4567 or (555) 987-6543."
    sanitized = pii_sanitizer_agent._sanitize_text(text_with_phone)
    
    assert "[PHONE_REDACTED]" in sanitized
    assert "555-123-4567" not in sanitized
    assert "(555) 987-6543" not in sanitized


def test_sanitize_text_name(pii_sanitizer_agent):
    """Test name sanitization."""
    text_with_name = "John Smith is a great developer. Mary Johnson agrees."
    sanitized = pii_sanitizer_agent._sanitize_text(text_with_name)
    
    assert "[NAME_REDACTED]" in sanitized
    assert "John Smith" not in sanitized


def test_sanitize_text_multiple_pii(pii_sanitizer_agent):
    """Test sanitization of multiple PII types."""
    text_with_multiple = "John Smith can be reached at john@example.com or 555-123-4567."
    sanitized = pii_sanitizer_agent._sanitize_text(text_with_multiple)
    
    assert "[NAME_REDACTED]" in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "[PHONE_REDACTED]" in sanitized
    assert "John Smith" not in sanitized
    assert "john@example.com" not in sanitized
    assert "555-123-4567" not in sanitized


def test_sanitize_text_no_pii(pii_sanitizer_agent):
    """Test text without PII remains unchanged."""
    clean_text = "This is a clean text without any personal information."
    sanitized = pii_sanitizer_agent._sanitize_text(clean_text)
    
    assert sanitized == clean_text
    assert "[EMAIL_REDACTED]" not in sanitized
    assert "[PHONE_REDACTED]" not in sanitized
    assert "[NAME_REDACTED]" not in sanitized


def test_run_simple_resume(pii_sanitizer_agent):
    """Test run method with simple resume data."""
    resume_data = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "555-123-4567",
        "skills": ["Python", "JavaScript"],
        "experience": "5 years at Tech Corp"
    }
    
    sanitized = pii_sanitizer_agent.run(resume_data)
    
    assert isinstance(sanitized, dict)
    # Check that structure is preserved
    assert "name" in sanitized
    assert "email" in sanitized
    assert "phone" in sanitized
    assert "skills" in sanitized
    assert isinstance(sanitized["skills"], list)


def test_run_nested_resume(pii_sanitizer_agent):
    """Test run method with nested resume data."""
    resume_data = {
        "personal": {
            "name": "John Smith",
            "contact": {
                "email": "john@example.com",
                "phone": "555-123-4567"
            }
        },
        "experience": [
            {
                "company": "Tech Corp",
                "description": "Worked with Jane Doe on multiple projects"
            }
        ]
    }
    
    sanitized = pii_sanitizer_agent.run(resume_data)
    
    assert isinstance(sanitized, dict)
    assert isinstance(sanitized["personal"], dict)
    assert isinstance(sanitized["personal"]["contact"], dict)
    assert isinstance(sanitized["experience"], list)
    assert isinstance(sanitized["experience"][0], dict)


def test_run_with_non_string_values(pii_sanitizer_agent):
    """Test run method with mixed data types."""
    resume_data = {
        "name": "John Smith",
        "age": 30,
        "salary": 75000.50,
        "active": True,
        "skills": ["Python", "JavaScript"],
        "metadata": None
    }
    
    sanitized = pii_sanitizer_agent.run(resume_data)
    
    assert isinstance(sanitized, dict)
    assert sanitized["age"] == 30
    assert sanitized["salary"] == 75000.50
    assert sanitized["active"] is True
    assert sanitized["metadata"] is None
    assert isinstance(sanitized["skills"], list)


def test_run_empty_resume(pii_sanitizer_agent):
    """Test run method with empty resume."""
    empty_resume = {}
    sanitized = pii_sanitizer_agent.run(empty_resume)
    
    assert isinstance(sanitized, dict)
    assert len(sanitized) == 0


@pytest.mark.autonomy
def test_heal_repository_smoke(pii_sanitizer_agent):
    """Autonomy heal smoke test — ensure no crash."""
    result = pii_sanitizer_agent.heal_repository()
    
    # PIISanitizerAgent is operational guardrail - should skip healing
    assert isinstance(result, dict)
    assert result.get("skipped") == 1


def test_heal_repository_parameters(pii_sanitizer_agent):
    """Test heal_repository accepts expected parameters."""
    result = pii_sanitizer_agent.heal_repository(
        dry_run=False,
        execute=True,
        depth=1,
        max_depth=2
    )
    
    assert isinstance(result, dict)
    assert result.get("skipped") == 1


def test_timeout_decorator_applied(pii_sanitizer_agent):
    """Test that heal_repository has timeout decorator applied."""
    # The method should have timeout applied - we verify it exists
    assert hasattr(pii_sanitizer_agent.heal_repository, '__wrapped__')


def test_json_serialization_safety(pii_sanitizer_agent):
    """Test that the agent handles JSON serialization edge cases."""
    # This tests the json.loads(json.dumps(resume)) pattern in run()
    complex_resume = {
        "name": "John Smith",
        "nested": {
            "deep": {
                "email": "test@example.com"
            }
        },
        "list_with_dict": [
            {"contact": "jane@example.com"},
            "plain string with phone 555-1234"
        ]
    }
    
    sanitized = pii_sanitizer_agent.run(complex_resume)
    assert isinstance(sanitized, dict)
    # Should handle complex nesting without errors
