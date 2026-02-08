"""
Test AST extraction in FCA.

Validates:
- Detect class suffixes Agent/Validator/Manager/Service
- Ignore comments/strings
- Handle SyntaxError without crash
"""

import ast


def extract_class_names(content: str) -> list[str]:
    """Extract class names from Python content using AST."""
    try:
        tree = ast.parse(content)
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    except SyntaxError:
        return []


def has_agent_class(content: str) -> bool:
    """Check if content has a concrete Agent class."""
    classes = extract_class_names(content)
    return any(c.endswith("Agent") and not c.startswith("I") for c in classes)


def has_validator_class(content: str) -> bool:
    """Check if content has a Validator class."""
    classes = extract_class_names(content)
    return any(c.endswith("Validator") for c in classes)


def has_manager_class(content: str) -> bool:
    """Check if content has a Manager class."""
    classes = extract_class_names(content)
    return any(c.endswith("Manager") for c in classes)


def has_service_class(content: str) -> bool:
    """Check if content has a Service class."""
    classes = extract_class_names(content)
    return any(c.endswith("Service") for c in classes)


class TestClassSuffixDetection:
    """Tests for class suffix detection."""

    def test_detect_agent_class(self):
        """Should detect Agent class."""
        content = """
class MyAgent:
    def execute(self):
        pass
"""
        assert has_agent_class(content)

    def test_detect_validator_class(self):
        """Should detect Validator class."""
        content = """
class MyValidator:
    def validate(self, data):
        return True
"""
        assert has_validator_class(content)

    def test_detect_manager_class(self):
        """Should detect Manager class."""
        content = """
class CacheManager:
    def __init__(self):
        self.cache = {}
"""
        assert has_manager_class(content)

    def test_detect_service_class(self):
        """Should detect Service class."""
        content = """
class EmbeddingService:
    def embed(self, text):
        return []
"""
        assert has_service_class(content)

    def test_ignore_protocol_interface(self):
        """Should ignore Protocol interfaces (IAgent)."""
        content = """
from typing import Protocol

class IAgent(Protocol):
    def execute(self) -> None:
        ...
"""
        extract_class_names(content)
        # IAgent starts with I, so has_agent_class should return False
        assert not has_agent_class(content)


class TestIgnoreCommentsAndStrings:
    """Tests for ignoring class names in comments/strings."""

    def test_ignore_class_in_comment(self):
        """Should ignore class names in comments."""
        content = """
# class FakeAgent:
#     pass

def real_function():
    pass
"""
        assert not has_agent_class(content)

    def test_ignore_class_in_docstring(self):
        """Should ignore class names in docstrings."""
        content = '''
"""
Example:
    class ExampleAgent:
        pass
"""

def real_function():
    pass
'''
        assert not has_agent_class(content)

    def test_ignore_class_in_string(self):
        """Should ignore class names in strings."""
        content = '''
template = """
class TemplateAgent:
    pass
"""

def real_function():
    pass
'''
        assert not has_agent_class(content)

    def test_detect_real_class_with_comments(self):
        """Should detect real class even with comments mentioning other classes."""
        content = '''
# This is not a FakeAgent
class RealAgent:
    """This agent does real work."""
    def execute(self):
        pass
'''
        assert has_agent_class(content)
        classes = extract_class_names(content)
        assert "RealAgent" in classes
        assert "FakeAgent" not in classes


class TestSyntaxErrorHandling:
    """Tests for syntax error handling in AST extraction."""

    def test_syntax_error_returns_empty(self):
        """Syntax error should return empty list, not crash."""
        content = """
def broken(
    # Missing closing paren
"""
        classes = extract_class_names(content)
        assert classes == []

    def test_incomplete_class_returns_empty(self):
        """Incomplete class should return empty list."""
        content = """
class Incomplete
"""
        classes = extract_class_names(content)
        assert classes == []

    def test_indentation_error_returns_empty(self):
        """Indentation error should return empty list."""
        content = """
def function():
pass  # Wrong indentation
"""
        classes = extract_class_names(content)
        assert classes == []

    def test_valid_content_after_fix(self):
        """Valid content should work after fixing syntax."""
        content = """
class ValidAgent:
    def execute(self):
        pass
"""
        classes = extract_class_names(content)
        assert "ValidAgent" in classes


class TestMultipleClasses:
    """Tests for files with multiple classes."""

    def test_detect_multiple_classes(self):
        """Should detect all classes in a file."""
        content = """
class FirstAgent:
    pass

class SecondValidator:
    pass

class ThirdManager:
    pass
"""
        classes = extract_class_names(content)
        assert len(classes) == 3
        assert "FirstAgent" in classes
        assert "SecondValidator" in classes
        assert "ThirdManager" in classes

    def test_mixed_class_types(self):
        """Should correctly identify mixed class types."""
        content = """
class MyAgent:
    pass

class MyValidator:
    pass

class RegularClass:
    pass
"""
        assert has_agent_class(content)
        assert has_validator_class(content)
        classes = extract_class_names(content)
        assert "RegularClass" in classes
