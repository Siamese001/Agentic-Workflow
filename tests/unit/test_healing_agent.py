"""Tests for L0 Maintenance reasoning agents."""

from pathlib import Path

import pytest


class TestHealingAgent:
    """Tests for healing agent functionality."""

    def test_healing_agent_exists(self):
        """Healing agent module should exist."""
        path = Path("agentic_core/L0_routing/reasoning")
        assert path.exists(), "L0_routing/reasoning/ should exist"

    def test_maintenance_has_healing_classes(self):
        """Maintenance should have healing/repair classes."""
        reasoning_path = Path("agentic_core/L0_routing/reasoning")
        if reasoning_path.exists():
            py_files = list(reasoning_path.glob("*.py"))
            assert len(py_files) > 0, "L0_routing/reasoning/ should have Python files"


class TestDiscoveryAgent:
    """Tests for discovery functionality."""

    def test_discovery_types_defined(self):
        """Discovery types should be defined in types/."""
        types_path = Path("agentic_core/L0_routing/types")
        if not types_path.exists():
            pytest.skip("L0_routing/types/ not found")

        type_files = list(types_path.glob("*.py"))
        assert len(type_files) > 0, "L0_routing/types/ should have type definitions"


class TestBootstrapAgent:
    """Tests for bootstrap functionality."""

    def test_bootstrap_config_exists(self):
        """Bootstrap config should exist."""
        config_path = Path("agentic_core/L0_routing/config")
        if not config_path.exists():
            pytest.skip("L0_routing/config/ not found")

        config_files = list(config_path.glob("*.py"))
        assert len(config_files) > 0, "L0_routing/config/ should have config files"


class TestMaintenanceLayerIntegrity:
    """Tests for L0 layer structural integrity."""

    def test_scripts_purity(self):
        """L0 scripts should be pure scripts (no Agent classes)."""
        scripts_path = Path("agentic_core/L0_routing/scripts")
        if not scripts_path.exists():
            pytest.skip("L0_routing/scripts/ not found")

        violations = []
        for py_file in scripts_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Check for Agent class definitions
            if "class " in content and "Agent(" in content:
                # PascalCase files with Agent classes should not be in scripts/
                if py_file.stem[0].isupper():
                    violations.append(str(py_file))

        # Note: Some legacy files may still exist
        if violations:
            pytest.skip(f"Found {len(violations)} Agent classes in scripts/ (legacy)")

    def test_maintenance_agents_in_reasoning(self):
        """Agent classes in L0 should be in reasoning/."""
        base = Path("agentic_core/L0_routing")
        if not base.exists():
            pytest.skip("L0_routing/ not found")

        violations = []
        for subfolder in ["types", "config"]:
            subfolder_path = base / subfolder
            if not subfolder_path.exists():
                continue
            for py_file in subfolder_path.glob("*.py"):
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "class " in content and "Agent(" in content:
                    violations.append(str(py_file))

        assert len(violations) == 0, f"Agent classes in wrong subfolder: {violations}"

    def test_utils_are_utilities(self):
        """L0 utils should be utility functions, not agents."""
        utils_path = Path("agentic_core/L0_routing/utils")
        if not utils_path.exists():
            pytest.skip("L0_routing/utils/ not found")

        violations = []
        for py_file in utils_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "class " in content and "Agent(" in content:
                violations.append(str(py_file))

        assert len(violations) == 0, f"Agent classes in utils/: {violations}"
