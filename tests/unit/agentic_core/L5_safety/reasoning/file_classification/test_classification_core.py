"""Snapshot tests for file_classification core functions.

These tests use representative real repo files to validate that extracted
functions maintain behavioral equivalence with the original implementation.
"""

import ast
import pytest
from pathlib import Path

from agentic_core.L5_safety.reasoning.file_classification.classification_core import (
    _detect_filename_tag_conflicts,
    _detect_script_patterns,
    _detect_test_patterns,
    _detect_type_patterns,
)


class TestDetectTestPatterns:
    """Tests for _detect_test_patterns function."""

    def test_detect_unittest_test_file(self):
        """Test detection of unittest-based test file."""
        code = """
import unittest

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertTrue(True)
"""
        tree = ast.parse(code)
        result = _detect_test_patterns(tree, Path("test_example.py"))
        assert result["is_test"] is True

    def test_detect_pytest_test_file(self):
        """Test detection of pytest-based test file."""
        code = """
import pytest

def test_something():
    assert True
"""
        tree = ast.parse(code)
        result = _detect_test_patterns(tree, Path("test_example.py"))
        assert result["is_test"] is True

    def test_non_test_file(self):
        """Test that non-test files are not detected as tests."""
        code = """
def regular_function():
    return 42
"""
        tree = ast.parse(code)
        result = _detect_test_patterns(tree, Path("regular.py"))
        assert result["is_test"] is False


class TestDetectScriptPatterns:
    """Tests for _detect_script_patterns function."""

    def test_detect_main_guard_script(self):
        """Test detection of script with __main__ guard."""
        code = """
def main():
    print("Hello")

if __name__ == "__main__":
    main()
"""
        tree = ast.parse(code)
        result = _detect_script_patterns(tree, Path("script.py"))
        assert result["is_script"] is True

    def test_detect_argparse_script(self):
        """Test detection of script using argparse."""
        code = """
import argparse

def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
"""
        tree = ast.parse(code)
        result = _detect_script_patterns(tree, Path("script.py"))
        assert result["is_script"] is True

    def test_non_script_file(self):
        """Test that non-script files are not detected as scripts."""
        code = """
class MyClass:
    def method(self):
        pass
"""
        tree = ast.parse(code)
        result = _detect_script_patterns(tree, Path("module.py"))
        assert result["is_script"] is False


class TestDetectTypePatterns:
    """Tests for _detect_type_patterns function."""

    def test_detect_enum_collection(self):
        """Test detection of multiple enum classes."""
        code = """
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Priority(Enum):
    HIGH = "high"
    LOW = "low"
"""
        tree = ast.parse(code)
        result = _detect_type_patterns(tree, Path("types.py"))
        assert result["is_types"] is True

    def test_detect_protocol_collection(self):
        """Test detection of protocol definitions."""
        code = """
from typing import Protocol

class MyProtocol(Protocol):
    def method(self) -> int: ...
"""
        tree = ast.parse(code)
        result = _detect_type_patterns(tree, Path("types.py"))
        assert result["is_types"] is True

    def test_non_type_file(self):
        """Test that non-type files are not detected as types."""
        code = """
class MyClass:
    def method(self):
        return 42
"""
        tree = ast.parse(code)
        result = _detect_type_patterns(tree, Path("regular.py"))
        assert result["is_types"] is False


class TestDetectFilenameTagConflicts:
    """Tests for _detect_filename_tag_conflicts function."""

    def test_detect_agent_types_conflict(self):
        """Test detection of _agent_types compound suffix."""
        path = Path("my_agent_types.py")
        result = _detect_filename_tag_conflicts(path)
        # Should detect conflict between AGENT and TYPES
        assert len(result) > 0
        assert "AGENT" in result
        assert "TYPES" in result

    def test_detect_agent_config_conflict(self):
        """Test detection of _agent_config compound suffix."""
        path = Path("security_level_agent_config.py")
        result = _detect_filename_tag_conflicts(path)
        # Should detect conflict between AGENT and CONFIG
        assert len(result) > 0

    def test_no_conflict_clean_filename(self):
        """Test that clean filenames have no conflicts."""
        path = Path("my_agent.py")
        result = _detect_filename_tag_conflicts(path)
        assert len(result) == 0

    def test_no_conflict_domain_words(self):
        """Test that domain words don't trigger false positives."""
        path = Path("find_misnamed_agents_util.py")
        result = _detect_filename_tag_conflicts(path)
        # "agents" is a domain word, not a classification tag
        assert len(result) == 0
