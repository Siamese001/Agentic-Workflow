"""
Test scripts purity policy.

Validates:
- scripts/ allowed only under L0_maintenance
- PascalCase filenames forbidden in scripts/
- test_*.py forbidden in scripts/
- SCRIPTS_FORBIDDEN_PATTERNS enforced
"""

import re

import pytest

from agentic_core.L5_safety.config.structure_blueprint_config import (
    CORE_SUBFOLDER_MAP,
    SCRIPTS_FORBIDDEN_PATTERNS,
)


class TestScriptsForbiddenPatterns:
    """Tests for SCRIPTS_FORBIDDEN_PATTERNS constant."""

    def test_patterns_exist(self):
        """SCRIPTS_FORBIDDEN_PATTERNS must be defined."""
        assert SCRIPTS_FORBIDDEN_PATTERNS is not None
        assert len(SCRIPTS_FORBIDDEN_PATTERNS) >= 2

    def test_pascalcase_pattern_exists(self):
        """Pattern for PascalCase filenames must exist."""
        patterns = [re.compile(p) for p in SCRIPTS_FORBIDDEN_PATTERNS]
        # Test that PascalCase is matched
        test_names = ["AgentAuditResult.py", "BatchEmbeddingService.py", "SovereignReport.py"]
        for name in test_names:
            matched = any(p.match(name) for p in patterns)
            assert matched, f"PascalCase filename '{name}' should be forbidden"

    def test_test_prefix_pattern_exists(self):
        """Pattern for test_*.py filenames must exist."""
        patterns = [re.compile(p) for p in SCRIPTS_FORBIDDEN_PATTERNS]
        test_names = ["test_something.py", "test_lifecycle_audit.py", "test_verify.py"]
        for name in test_names:
            matched = any(p.match(name) for p in patterns)
            assert matched, f"test_ filename '{name}' should be forbidden"

    @pytest.mark.parametrize(
        "valid_script",
        [
            "run_healing.py",
            "colors.py",
            "full_agent_discovery.py",
            "check_syntax_util.py",
            "__init__.py",
        ],
    )
    def test_valid_scripts_not_matched(self, valid_script: str):
        """Valid script names should not be matched by forbidden patterns."""
        patterns = [re.compile(p) for p in SCRIPTS_FORBIDDEN_PATTERNS]
        matched = any(p.match(valid_script) for p in patterns)
        assert not matched, f"Valid script '{valid_script}' should not be forbidden"


class TestScriptsLocationPolicy:
    """Tests for scripts/ folder location policy."""

    def test_scripts_only_in_l0_maintenance(self):
        """scripts/ subfolder should only exist in L0_maintenance."""
        for layer, subfolders in CORE_SUBFOLDER_MAP.items():
            if layer == "L0_maintenance":
                assert "scripts" in subfolders, "L0_maintenance must have scripts/"
            elif layer.startswith("L") and "_" in layer:
                # Other L* layers should not have scripts/
                assert "scripts" not in subfolders, f"{layer} should not have scripts/"

    def test_l0_maintenance_has_scripts(self):
        """L0_maintenance must have scripts/ subfolder."""
        l0_subfolders = CORE_SUBFOLDER_MAP.get("L0_maintenance", [])
        assert "scripts" in l0_subfolders


class TestScriptsPurityValidation:
    """Tests for scripts purity validation logic."""

    @pytest.mark.parametrize(
        "forbidden_name",
        [
            "AgentAuditResult.py",
            "BatchEmbeddingService.py",
            "GitKrakenHealingStrategy.py",
            "InMemoryVectorCache.py",
            "SovereignHealingEngine.py",
            "SovereignReport.py",
            "StrategistBioWriter.py",
            "VectorHealingStrategy.py",
        ],
    )
    def test_pascalcase_class_modules_forbidden(self, forbidden_name: str):
        """PascalCase class module names are forbidden in scripts/."""
        patterns = [re.compile(p) for p in SCRIPTS_FORBIDDEN_PATTERNS]
        matched = any(p.match(forbidden_name) for p in patterns)
        assert matched, f"'{forbidden_name}' should be forbidden in scripts/"

    @pytest.mark.parametrize(
        "forbidden_name",
        [
            "test_boundary_stress_test.py",
            "test_lifecycle_audit.py",
            "test_runtime_verify_installation.py",
            "test_verify_meta_learning_integration.py",
            "test_verify_self_healing.py",
            "test_generator.py",
        ],
    )
    def test_test_files_forbidden(self, forbidden_name: str):
        """test_*.py files are forbidden in scripts/."""
        patterns = [re.compile(p) for p in SCRIPTS_FORBIDDEN_PATTERNS]
        matched = any(p.match(forbidden_name) for p in patterns)
        assert matched, f"'{forbidden_name}' should be forbidden in scripts/"
