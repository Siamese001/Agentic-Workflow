"""
Tests for classification kernel governance hardening.

Phase 4 Wave 4.2: Validates CONFIG_WITH_LOGIC detection and DUAL_TAG conflict tracking.
"""

from pathlib import Path

import pytest

from agentic_core.core.classification_kernel import (
    classify_file_standalone,
    clear_classification_cache,
    clear_classification_conflicts,
    get_classification_conflicts,
)

pytestmark = pytest.mark.governance


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear caches before and after each test."""
    clear_classification_cache()
    clear_classification_conflicts()
    yield
    clear_classification_cache()
    clear_classification_conflicts()


class TestConfigWithLogicDetection:
    """Tests for CONFIG_WITH_LOGIC violation detection."""

    def test_pure_config_file_classified_as_config(self, tmp_path: Path):
        """A CONFIG file with only schema definitions should be CONFIG."""
        config_file = tmp_path / "environment_config.py"
        config_file.write_text('''
"""Environment configuration schema."""
from pydantic import BaseModel

class EnvironmentConfig(BaseModel):
    """Pure schema - no executable methods."""
    api_key: str
    timeout: int = 30
''')
        result = classify_file_standalone(config_file)
        assert result == "CONFIG", f"Expected CONFIG, got {result}"

        conflicts = get_classification_conflicts()
        config_conflicts = [c for c in conflicts if c["conflict_type"] == "CONFIG_WITH_LOGIC"]
        assert len(config_conflicts) == 0, "Pure CONFIG should not have CONFIG_WITH_LOGIC conflict"

    def test_config_with_logic_detected(self, tmp_path: Path):
        """A CONFIG file with executable methods should be CONFIG_WITH_LOGIC."""
        config_file = tmp_path / "bad_config.py"
        config_file.write_text('''
"""Config file with logic - violation."""
from pydantic import BaseModel

class BadConfig(BaseModel):
    """Config with executable methods."""
    api_key: str

    def validate_key(self) -> bool:
        """This is executable logic - violation!"""
        return len(self.api_key) > 10

    def process_data(self, data: dict) -> dict:
        """More executable logic - violation!"""
        return {"processed": data}
''')
        result = classify_file_standalone(config_file)
        assert result == "CONFIG_WITH_LOGIC", f"Expected CONFIG_WITH_LOGIC, got {result}"

        conflicts = get_classification_conflicts()
        config_conflicts = [c for c in conflicts if c["conflict_type"] == "CONFIG_WITH_LOGIC"]
        assert len(config_conflicts) == 1, "Should detect CONFIG_WITH_LOGIC conflict"

    def test_config_with_dunder_methods_is_valid(self, tmp_path: Path):
        """CONFIG files with only dunder methods should be valid CONFIG."""
        config_file = tmp_path / "valid_config.py"
        config_file.write_text('''
"""Config with dunder methods only."""
from pydantic import BaseModel

class ValidConfig(BaseModel):
    """Config with only dunder methods."""
    api_key: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"Config(api_key=***)"
''')
        result = classify_file_standalone(config_file)
        assert result == "CONFIG", f"Expected CONFIG, got {result}"

    def test_config_with_property_is_valid(self, tmp_path: Path):
        """CONFIG files with property decorators should be valid CONFIG."""
        config_file = tmp_path / "property_config.py"
        config_file.write_text('''
"""Config with property decorators."""
from pydantic import BaseModel

class PropertyConfig(BaseModel):
    """Config with properties only."""
    _api_key: str

    @property
    def api_key(self) -> str:
        return self._api_key
''')
        result = classify_file_standalone(config_file)
        assert result == "CONFIG", f"Expected CONFIG, got {result}"


class TestDualTagConflictDetection:
    """Tests for DUAL_TAG conflict detection."""

    def test_single_signal_no_conflict(self, tmp_path: Path):
        """A file with single top-tier signal should have no conflicts."""
        agent_file = tmp_path / "simple_agent.py"
        agent_file.write_text('''
"""Simple agent with single signal."""

class SimpleAgent:
    """Just an agent."""
    def run(self):
        pass
''')
        classify_file_standalone(agent_file)

        conflicts = get_classification_conflicts()
        dual_conflicts = [c for c in conflicts if c["conflict_type"] == "DUAL_TAG"]
        assert len(dual_conflicts) == 0, "Single signal should have no DUAL_TAG conflict"

    def test_orchestrator_mixin_dual_tag_detected(self, tmp_path: Path):
        """A file with both Orchestrator and Mixin signals should be flagged."""
        dual_file = tmp_path / "orchestrator_mixin.py"
        dual_file.write_text('''
"""File with dual signals - Orchestrator and Mixin."""

class OrchestratorMixin:
    """This has both Orchestrator and Mixin in the name."""
    def run(self):
        pass
''')
        classify_file_standalone(dual_file)

        conflicts = get_classification_conflicts()
        dual_conflicts = [c for c in conflicts if c["conflict_type"] == "DUAL_TAG"]
        assert len(dual_conflicts) == 1, "Should detect DUAL_TAG conflict"
        assert "ORCHESTRATOR" in dual_conflicts[0]["signals"]
        assert "MIXIN" in dual_conflicts[0]["signals"]

    def test_orchestrator_agent_dual_tag_detected(self, tmp_path: Path):
        """A file with both Orchestrator and Agent signals should be flagged."""
        dual_file = tmp_path / "orchestrator_agent.py"
        dual_file.write_text('''
"""File with dual signals - Orchestrator and Agent."""

class OrchestratorAgent:
    """This has both Orchestrator and Agent in the name."""
    def run(self):
        pass
''')
        classify_file_standalone(dual_file)

        conflicts = get_classification_conflicts()
        dual_conflicts = [c for c in conflicts if c["conflict_type"] == "DUAL_TAG"]
        assert len(dual_conflicts) == 1, "Should detect DUAL_TAG conflict"
        assert "ORCHESTRATOR" in dual_conflicts[0]["signals"]
        assert "AGENT" in dual_conflicts[0]["signals"]


class TestUtilityWithSchemaDetection:
    """Tests for UTILITY files that should not contain Pydantic schemas."""

    def test_utility_file_classified_correctly(self, tmp_path: Path):
        """A UTILITY file should be classified as UTILITY."""
        util_file = tmp_path / "helper_util.py"
        util_file.write_text('''
"""Helper utilities."""

def process_data(data: dict) -> dict:
    """Process data."""
    return {"processed": data}

def validate_input(value: str) -> bool:
    """Validate input."""
    return len(value) > 0
''')
        result = classify_file_standalone(util_file)
        assert result == "UTILITY", f"Expected UTILITY, got {result}"


class TestClassificationDeterminism:
    """Tests for classification determinism."""

    def test_same_file_same_result(self, tmp_path: Path):
        """Same file should always produce same classification."""
        test_file = tmp_path / "determinism_test.py"
        test_file.write_text('''
"""Test file for determinism."""

class TestClass:
    def method(self):
        pass
''')
        results = [classify_file_standalone(test_file) for _ in range(10)]
        assert len(set(results)) == 1, "Classification should be deterministic"

    def test_priority_order_respected(self, tmp_path: Path):
        """Higher priority signals should win over lower priority."""
        # AGENT (priority 10) should win over CLASS (priority 18)
        agent_file = tmp_path / "priority_agent.py"
        agent_file.write_text('''
"""Agent file."""

class PriorityAgent:
    """Agent class."""
    def run(self):
        pass
''')
        result = classify_file_standalone(agent_file)
        assert result == "AGENT", f"AGENT should win over CLASS, got {result}"
