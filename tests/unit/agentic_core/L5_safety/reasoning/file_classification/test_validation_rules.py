"""Tests for validation_rules module."""

import ast
import pytest
from pathlib import Path

from agentic_core.L5_safety.reasoning.file_classification.validation_rules import (
    check_domain_root_purity,
    check_fake_config,
)


class TestCheckFakeConfig:
    """Tests for check_fake_config function."""

    def test_fake_config_with_active_methods(self):
        """Test detection of config file with active methods."""
        content = """
class MyConfig:
    def __init__(self):
        self.value = 42
    
    def process_data(self):
        return self.value * 2
"""
        path = Path("my_config.py")
        result = check_fake_config(path, content)
        assert result is not None
        assert result.type == "MISNAMED_UTILITY"
        assert "process_data" in result.message

    def test_real_config_dataclass(self):
        """Test that dataclass config files are not flagged."""
        content = """
from dataclasses import dataclass

@dataclass
class MyConfig:
    value: int
    name: str
"""
        path = Path("my_config.py")
        result = check_fake_config(path, content)
        assert result is None

    def test_real_config_constants(self):
        """Test that constant-only config files are not flagged."""
        content = """
VALUE = 42
NAME = "test"
CONFIG = {"key": "value"}
"""
        path = Path("my_config.py")
        result = check_fake_config(path, content)
        assert result is None

    def test_non_config_file(self):
        """Test that non-config files are not checked."""
        content = """
def my_function():
    return 42
"""
        path = Path("my_module.py")
        result = check_fake_config(path, content)
        assert result is None


class TestCheckDomainRootPurity:
    """Tests for check_domain_root_purity function."""

    def test_leaf_node_violation_knowledge(self):
        """Test detection of file in knowledge root."""
        path = Path("agentic_core/knowledge/my_file.py")
        result = check_domain_root_purity(path)
        assert result is not None
        assert result.type == "LEAF_NODE_VIOLATION"

    def test_leaf_node_violation_semantic_memory(self):
        """Test detection of file in semantic_memory root."""
        path = Path("agentic_core/semantic_memory/my_file.py")
        result = check_domain_root_purity(path)
        assert result is not None
        assert result.type == "LEAF_NODE_VIOLATION"

    def test_knowledge_pascal_case_violation(self):
        """Test detection of PascalCase in knowledge domain."""
        path = Path("agentic_core/knowledge/engine/MyModule.py")
        result = check_domain_root_purity(path)
        assert result is not None
        assert result.type == "KNOWLEDGE_PASCAL_CASE"

    def test_knowledge_snake_case_ok(self):
        """Test that snake_case in knowledge is OK."""
        path = Path("agentic_core/knowledge/engine/my_module.py")
        result = check_domain_root_purity(path)
        assert result is None

    def test_init_allowed_in_root(self):
        """Test that __init__.py is allowed in domain root."""
        path = Path("agentic_core/knowledge/__init__.py")
        result = check_domain_root_purity(path)
        assert result is None

    def test_subdirectory_allowed(self):
        """Test that files in subdirectories are OK."""
        path = Path("agentic_core/knowledge/engine/my_module.py")
        result = check_domain_root_purity(path)
        assert result is None
