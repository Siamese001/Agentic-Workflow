"""Tests for classification_core module."""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

_classification_core = pytest.importorskip(
    "agentic_core.L5_safety.reasoning.file_classification.classification_core",
    reason="Requires file classification core from the monorepo checkout.",
)
ClassifiedFile = _classification_core.ClassifiedFile
ClassificationResult = _classification_core.ClassificationResult
FileCategory = _classification_core.FileCategory
FileLocation = _classification_core.FileLocation
ValidationIssue = _classification_core.ValidationIssue
_analyze_class_definition = _classification_core._analyze_class_definition
_analyze_file_content = _classification_core._analyze_file_content
_build_classified_file = _classification_core._build_classified_file
_classify_by_content = _classification_core._classify_by_content
_classify_by_location = _classification_core._classify_by_location
_classify_file_pure = _classification_core.classify_file_pure
_extract_imports = _classification_core._extract_imports
_extract_top_level_functions = _classification_core._extract_top_level_functions
_get_file_stem = _classification_core._get_file_stem
_has_active_logic = _classification_core._has_active_logic
_has_config_indicators = _classification_core._has_config_indicators
_has_orchestrator_indicators = _classification_core._has_orchestrator_indicators
_has_script_indicators = _classification_core._has_script_indicators
_is_agent_class = _classification_core._is_agent_class
_is_orchestrator_class = _classification_core._is_orchestrator_class
_is_service_class = _classification_core._is_service_class
_validate_classification = _classification_core._validate_classification
_validate_content_location_alignment = _classification_core._validate_content_location_alignment
_validate_folder_rules = _classification_core._validate_folder_rules
_validate_naming_rules = _classification_core._validate_naming_rules
validate_folder_suffix_consistency = _classification_core.validate_folder_suffix_consistency


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


class TestComputeContentScores:
    """Tests for _compute_content_scores function."""

    def test_agent_detection(self, tmp_path):
        """Test detection of agent classes."""
        code = """
class MyAgent:
    def execute(self):
        pass
"""
        test_file = tmp_path / "test_agent.py"
        test_file.write_text(code)
        result = _compute_content_scores(test_file)
        assert result["AGENT"] > 0

    def test_dataclass_detection(self, tmp_path):
        """Test detection of dataclass types."""
        code = """
from dataclasses import dataclass

@dataclass
class MyModel:
    name: str
    value: int
"""
        test_file = tmp_path / "test_dataclass.py"
        test_file.write_text(code)
        result = _compute_content_scores(test_file)
        assert result["TYPES"] > 0

    def test_config_detection(self, tmp_path):
        """Test detection of config constants."""
        code = """
MAX_RETRIES = 3
TIMEOUT = 30
API_KEY = "secret"
"""
        test_file = tmp_path / "test_config.py"
        test_file.write_text(code)
        result = _compute_content_scores(test_file)
        assert result["CONFIG"] > 0


class TestDetectEnforcerControlSignal:
    """Tests for _detect_enforcer_control_signal function."""

    def test_raise_in_validate(self):
        """Test detection of raise in validate function."""
        code = """
def validate_input(data):
    if not data:
        raise ValueError("Invalid input")
"""
        tree = ast.parse(code)
        result = _detect_enforcer_control_signal(tree, code)
        assert result is True

    def test_return_false_tuple(self):
        """Test detection of (False, "...") return pattern."""
        code = """
def check_permission(user):
    if not user.is_admin:
        return (False, "Not authorized")
"""
        tree = ast.parse(code)
        result = _detect_enforcer_control_signal(tree, code)
        assert result is True

    def test_no_control_signal(self):
        """Test that functions without control signals return False."""
        code = """
def process_data(data):
    return data.upper()
"""
        tree = ast.parse(code)
        result = _detect_enforcer_control_signal(tree, code)
        assert result is False


class TestDetectConfigPatterns:
    """Tests for _detect_config_patterns function."""

    def test_config_class_name(self):
        """Test detection of Config class suffix."""
        code = """
class AppConfig:
    def __init__(self):
        self.debug = False
"""
        tree = ast.parse(code)
        result = _detect_config_patterns(
            tree,
            Path("app_config.py"),
            code,
            ["config"],
            {"debug", "timeout"},
        )
        assert result is True

    def test_config_attributes(self):
        """Test detection of config-like attributes."""
        code = """
class Settings:
    debug: bool
    timeout: int
    api_key: str
"""
        tree = ast.parse(code)
        result = _detect_config_patterns(
            tree,
            Path("settings.py"),
            code,
            [],
            {"debug", "timeout", "api_key"},
        )
        assert result is True

    def test_non_config_file(self):
        """Test that non-config files return False."""
        code = """
class MyClass:
    def method(self):
        return 42
"""
        tree = ast.parse(code)
        result = _detect_config_patterns(
            tree,
            Path("regular.py"),
            code,
            [],
            {"debug"},
        )
        assert result is False


class TestDetectValidatorPatterns:
    """Tests for _detect_validator_patterns function."""

    def test_validate_method(self):
        """Test detection of validate method."""
        code = """
class MyValidator:
    def validate_input(self, data):
        return True
"""
        tree = ast.parse(code)
        result = _detect_validator_patterns(tree, Path("validator.py"), code, ["validate"])
        assert result is True

    def test_check_function(self):
        """Test detection of check function."""
        code = """
def check_permissions(user):
    return user.is_admin
"""
        tree = ast.parse(code)
        result = _detect_validator_patterns(tree, Path("checks.py"), code, ["check"])
        assert result is True

    def test_assert_usage(self):
        """Test detection of assert statements."""
        code = """
def verify_data(data):
    assert data is not None
    assert len(data) > 0
    assert data.get("id") is not None
"""
        tree = ast.parse(code)
        result = _detect_validator_patterns(tree, Path("verify.py"), code, [])
        assert result is True

    def test_non_validator_file(self):
        """Test that non-validator files return False."""
        code = """
class MyClass:
    def method(self):
        return 42
"""
        tree = ast.parse(code)
        result = _detect_validator_patterns(tree, Path("regular.py"), code, [])
        assert result is False


class TestDetectOrchestratorPatterns:
    """Tests for _detect_orchestrator_patterns function."""

    def test_inheritance_detection(self):
        """Test detection of orchestrator base class inheritance."""
        code = """
from agentic_core.L3_orchestration.base import L3OrchestrationBase

class MyOrchestrator(L3OrchestrationBase):
    def execute(self):
        pass
"""
        tree = ast.parse(code)
        result = _detect_orchestrator_patterns(tree, Path("my_orchestrator.py"), code, "MyOrchestrator")
        assert result is True

    def test_exact_suffix_detection(self):
        """Test detection of exact orchestrator suffix."""
        code = """
class PipelineOrchestrator:
    def run(self):
        pass
"""
        tree = ast.parse(code)
        result = _detect_orchestrator_patterns(
            tree,
            Path("pipeline_orchestrator.py"),
            code,
            "PipelineOrchestrator",
        )
        assert result is True

    def test_non_orchestrator_file(self):
        """Test that non-orchestrator files return False."""
        code = """
class MyClass:
    def method(self):
        return 42
"""
        tree = ast.parse(code)
        result = _detect_orchestrator_patterns(tree, Path("regular.py"), code, "MyClass")
        assert result is False


class TestFuzzyMatchNameOrContent:
    """Tests for _fuzzy_match_name_or_content function."""

    def test_exact_name_match(self):
        """Test exact name matching."""
        result = _fuzzy_match_name_or_content("my_config.py", Path("test.py"), "", ["config"])
        assert result is True

    def test_content_pattern_match(self):
        """Test content pattern matching in function names."""
        code = """
def validate_input(data):
    return True
"""
        result = _fuzzy_match_name_or_content("test.py", Path("test.py"), code, ["validate"])
        assert result is True

    def test_no_match(self):
        """Test that patterns not present return False."""
        code = """
def process_data(data):
    return data.upper()
"""
        result = _fuzzy_match_name_or_content("test.py", Path("test.py"), code, ["validate"])
        assert result is False


class TestIsTrueAgent:
    """Tests for _is_true_agent function."""

    def test_agent_naming_convention(self):
        """Test detection by Agent suffix."""
        code = """
class MyAgent:
    def execute(self):
        pass
"""
        tree = ast.parse(code)
        node = tree.body[0]
        result = _is_true_agent(node, Path("test.py"))
        assert result is True

    def test_non_agent_class(self):
        """Test that non-agent classes return False."""
        code = """
class MyClass:
    def method(self):
        return 42
"""
        tree = ast.parse(code)
        node = tree.body[0]
        result = _is_true_agent(node, Path("test.py"))
        assert result is False


class TestIsServiceClass:
    """Tests for _is_service_class function."""

    def test_service_decorator(self):
        """Test detection by @service decorator."""
        code = """
@service
class MyService:
    def method(self):
        pass
"""
        tree = ast.parse(code)
        node = tree.body[0]
        result = _is_service_class(node, Path("test.py"))
        assert result is True

    def test_service_naming(self):
        """Test detection by Service suffix."""
        code = """
class DataService:
    def method(self):
        pass
"""
        tree = ast.parse(code)
        node = tree.body[0]
        result = _is_service_class(node, Path("test.py"))
        assert result is True

    def test_non_service_class(self):
        """Test that non-service classes return False."""
        code = """
class MyClass:
    def method(self):
        return 42
"""
        tree = ast.parse(code)
        node = tree.body[0]
        result = _is_service_class(node, Path("test.py"))
        assert result is False


class TestIsFactoryClass:
    """Tests for _is_factory_class function."""

    def test_factory_naming(self):
        """Test detection by Factory suffix."""
        code = """
class MyFactory:
    def method(self):
        pass
"""
        tree = ast.parse(code)
        node = tree.body[0]
        result = _is_factory_class(node)
        assert result is True

    def test_factory_methods(self):
        """Test detection by create_* methods."""
        code = """
class Builder:
    def create_instance(self):
        return None
"""
        tree = ast.parse(code)
        node = tree.body[0]
        result = _is_factory_class(node)
        assert result is True

    def test_non_factory_class(self):
        """Test that non-factory classes return False."""
        code = """
class MyClass:
    def method(self):
        return 42
"""
        tree = ast.parse(code)
        node = tree.body[0]
        result = _is_factory_class(node)
        assert result is False


class TestValidateSingleSuffix:
    """Tests for validate_single_suffix function."""

    def test_single_suffix_compliant(self):
        """Test that files with single suffix are compliant."""
        result = validate_single_suffix("model_provider_types.py")
        assert result is None

    def test_multiple_suffixes_violation(self):
        """Test that files with multiple suffixes are violations."""
        result = validate_single_suffix("model_provider_types_config.py")
        assert result is not None
        assert "found_suffixes" in result
        assert "suggested_name" in result

    def test_exempt_files(self):
        """Test that exempt files pass validation."""
        assert validate_single_suffix("__init__.py") is None
        assert validate_single_suffix("__main__.py") is None
        assert validate_single_suffix("conftest.py") is None


class TestValidateFolderSuffixConsistency:
    """Tests for validate_folder_suffix_consistency function."""

    def test_types_folder_compliant(self):
        """Test that types folder with correct suffix is compliant."""
        result = validate_folder_suffix_consistency(Path("config/types/model_types.py"))
        assert result is None

    def test_types_folder_violation(self):
        """Test that types folder with wrong suffix is violation."""
        result = validate_folder_suffix_consistency(Path("config/types/model.py"))
        assert result is not None
        assert result["folder"] == "types"

    def test_utils_folder_compliant(self):
        """Test that utils folder with correct suffix is compliant."""
        result = validate_folder_suffix_consistency(Path("config/utils/helper_util.py"))
        assert result is None

    def test_non_typed_folder(self):
        """Test that non-typed folders are not checked."""
        result = validate_folder_suffix_consistency(Path("config/reasoning/agent.py"))
        assert result is None


class TestClassifyFilePure:
    """Tests for classify_file_pure function."""

    def test_classify_config_file(self):
        """Test classification of a config file."""
        import os
        import tempfile

        code = """
class Config:
    SETTINGS = "value"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix="_config.py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = Path(f.name)

        try:
            result = classify_file_pure(temp_path)
            assert result == "CONFIG"
        finally:
            os.unlink(temp_path)

    def test_classify_test_file(self):
        """Test classification of a test file."""
        import os
        import tempfile

        code = """
import unittest

class MyTest(unittest.TestCase):
    def test_something(self):
        pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = Path(f.name)

        try:
            result = classify_file_pure(temp_path)
            assert result == "TEST"
        finally:
            os.unlink(temp_path)

    def test_classify_nonexistent_file(self):
        """Test classification of nonexistent file."""
        result = classify_file_pure(Path("nonexistent_file.py"))
        assert result == "IGNORE"
