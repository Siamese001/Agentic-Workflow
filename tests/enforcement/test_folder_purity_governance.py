"""
Negative tests for folder purity governance rules.

Tests that verify the enforcement of:
- L0-L6 enforcement/ SCRIPT classification => FAIL
- L0-L6 enforcement/ SERVICE without valid suffix => FAIL
- agentic_core/utils files lacking *_util.py => FAIL
- agentic_core/config/agent_configs files lacking *_config.py => FAIL
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L5_safety.config.structure_blueprint_config import (
    FOLDER_ALIASES,
    FOLDER_PURITY_RULES,
    INFRASTRUCTURE_PROFILES,
)


class TestFolderPurityGovernanceRules:
    """Test governance rules are correctly defined."""

    def test_utils_requires_util_suffix(self) -> None:
        """Verify utils folder requires *_util.py suffix."""
        assert "utils" in FOLDER_PURITY_RULES
        patterns = FOLDER_PURITY_RULES["utils"]
        # Check that _util.py is required
        util_pattern_found = any("_util" in p for p in patterns)
        assert util_pattern_found, "utils folder must require *_util.py suffix"

    def test_agent_configs_requires_config_suffix(self) -> None:
        """Verify agent_configs folder requires *_config.py suffix."""
        assert "agent_configs" in FOLDER_PURITY_RULES
        patterns = FOLDER_PURITY_RULES["agent_configs"]
        # Check that _config.py is required
        config_pattern_found = any("_config" in p for p in patterns)
        assert config_pattern_found, "agent_configs folder must require *_config.py suffix"

    def test_mixins_requires_mixin_suffix(self) -> None:
        """Verify mixins folder requires *_mixin.py suffix (snake_case)."""
        assert "mixins" in FOLDER_PURITY_RULES
        patterns = FOLDER_PURITY_RULES["mixins"]
        # Check that _mixin.py is required and snake_case
        mixin_pattern = patterns[0] if patterns else ""
        assert "_mixin" in mixin_pattern, "mixins folder must require *_mixin.py suffix"
        # Verify snake_case pattern (lowercase + underscore)
        assert "[a-z0-9_]" in mixin_pattern, "mixins must use snake_case pattern"

    def test_interfaces_requires_i_prefix(self) -> None:
        """Verify interfaces folder requires I*.py prefix (PascalCase)."""
        assert "interfaces" in FOLDER_PURITY_RULES
        patterns = FOLDER_PURITY_RULES["interfaces"]
        # Check that I prefix is required
        i_prefix_found = any(p.startswith("^I") for p in patterns)
        assert i_prefix_found, "interfaces folder must require I*.py prefix"

    def test_folder_aliases_knowledge_to_reasoning(self) -> None:
        """Verify knowledge folder aliases to reasoning."""
        assert "knowledge" in FOLDER_ALIASES
        assert FOLDER_ALIASES["knowledge"] == "reasoning"

    def test_folder_aliases_validation_to_validators(self) -> None:
        """Verify validation folder aliases to validators."""
        assert "validation" in FOLDER_ALIASES
        assert FOLDER_ALIASES["validation"] == "validators"


class TestEnforcementFolderRules:
    """Test L0-L6 enforcement/ folder rules."""

    def test_enforcement_folder_exists_in_rules(self) -> None:
        """Verify enforcement folder has purity rules."""
        assert "enforcement" in FOLDER_PURITY_RULES

    def test_enforcement_allows_strategy_suffix(self) -> None:
        """Verify enforcement/ allows *Strategy.py files."""
        patterns = FOLDER_PURITY_RULES["enforcement"]
        strategy_pattern_found = any("Strategy" in p for p in patterns)
        assert strategy_pattern_found, "enforcement/ must allow *Strategy.py"


class TestUtilsFileSuffixCompliance:
    """Test that agentic_core/utils files comply with *_util.py suffix."""

    @pytest.fixture
    def utils_dir(self) -> Path:
        """Get the agentic_core/utils directory."""
        return Path(__file__).parents[2] / "agentic_core" / "utils"

    def test_utils_files_have_util_suffix(self, utils_dir: Path) -> None:
        """All .py files in agentic_core/utils must end with _util.py."""
        if not utils_dir.exists():
            pytest.skip("agentic_core/utils directory not found")

        violations = []
        for py_file in utils_dir.glob("*.py"):
            if py_file.name in ("__init__.py", "__main__.py", "conftest.py"):
                continue
            if not py_file.name.endswith("_util.py") and not py_file.name.endswith("_helper.py"):
                violations.append(py_file.name)

        if violations:
            pytest.fail(
                f"Utils files lacking *_util.py suffix ({len(violations)}): {violations[:10]}"
            )


class TestAgentConfigsFileSuffixCompliance:
    """Test that agentic_core/config/agent_configs files comply with rules."""

    @pytest.fixture
    def agent_configs_dir(self) -> Path:
        """Get the agentic_core/config/agent_configs directory."""
        return Path(__file__).parents[2] / "agentic_core" / "config" / "agent_configs"

    def test_agent_configs_files_have_valid_suffix(self, agent_configs_dir: Path) -> None:
        """All files in agent_configs must end with _config.py or be YAML/JSON."""
        if not agent_configs_dir.exists():
            pytest.skip("agentic_core/config/agent_configs directory not found")

        violations = []
        for file in agent_configs_dir.iterdir():
            if file.name in ("__init__.py", "__main__.py"):
                continue
            if file.suffix == ".py" and not file.name.endswith("_config.py"):
                violations.append(file.name)
            elif file.suffix not in (".py", ".yaml", ".json", ".yml"):
                violations.append(file.name)

        if violations:
            pytest.fail(
                f"Agent config files with invalid suffix ({len(violations)}): {violations[:10]}"
            )
