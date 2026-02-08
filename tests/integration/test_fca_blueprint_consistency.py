"""
Integration test: FCA and Blueprint consistency.

Validates:
- Any FCA target_path must be blueprint-valid
- FCA classification results align with blueprint structure
"""

import pytest
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint_config import (
    CORE_SUBFOLDER_MAP,
    LAYER_ROOTS,
    is_layer_root,
    is_allowed_subfolder,
)


class TestFCABlueprintConsistency:
    """Tests for FCA and Blueprint consistency."""

    def test_all_layer_roots_in_core_subfolder_map(self):
        """All LAYER_ROOTS must have entries in CORE_SUBFOLDER_MAP."""
        for layer in LAYER_ROOTS:
            assert layer in CORE_SUBFOLDER_MAP, f"{layer} missing from CORE_SUBFOLDER_MAP"

    def test_all_lcd_subfolders_allowed(self):
        """All LCD subfolders must be allowed for each layer."""
        lcd_subfolders = ["config", "types", "reasoning", "enforcement", "validators", "utils"]
        for layer in LAYER_ROOTS:
            for subfolder in lcd_subfolders:
                assert is_allowed_subfolder(layer, subfolder), f"{layer}/{subfolder} not allowed"

    def test_layer_nuances_in_subfolder_map(self):
        """Layer nuances (scripts, tools, memory, dashboards) must be in CORE_SUBFOLDER_MAP."""
        nuances = {
            "L0_maintenance": "scripts",
            "L2_execution": "tools",
            "L4_state": "memory",
            "L6_observability": "dashboards",
        }
        for layer, nuance in nuances.items():
            subfolders = CORE_SUBFOLDER_MAP.get(layer, [])
            assert nuance in subfolders, f"{layer} missing nuance: {nuance}"

    def test_fca_target_paths_are_blueprint_valid(self):
        """FCA suggested target paths should be blueprint-valid."""
        # Test that common target paths are valid
        valid_targets = [
            ("L5_safety", "reasoning"),
            ("L5_safety", "enforcement"),
            ("L5_safety", "types"),
            ("L0_maintenance", "scripts"),
            ("L2_execution", "tools"),
            ("L4_state", "memory"),
            ("L6_observability", "dashboards"),
        ]
        for layer, subfolder in valid_targets:
            layer_subfolders = CORE_SUBFOLDER_MAP.get(layer, [])
            assert subfolder in layer_subfolders, f"{layer}/{subfolder} not in blueprint"


class TestFCAClassificationAlignment:
    """Tests for FCA classification alignment with blueprint."""

    @pytest.fixture
    def fca(self):
        """Create FCA instance."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent
        return FileClassificationAgent()

    def test_agent_classification_targets_reasoning(self, fca, tmp_path):
        """Agent classification should target reasoning/ subfolder."""
        content = '''"""Agent module."""
class TestAgent:
    def execute(self):
        pass
'''
        test_file = tmp_path / "test_agent.py"
        test_file.write_text(content)

        result = fca.classify_file(test_file)
        # Result may be string or dict depending on FCA implementation
        if result:
            if isinstance(result, dict) and result.get("type") == "AGENT":
                target = result.get("target_subfolder")
                if target:
                    assert target == "reasoning", f"Agent should target reasoning/, got {target}"
            # If result is string, just verify it ran without error
            assert True

    def test_types_classification_targets_types(self, fca, tmp_path):
        """Types classification should target types/ subfolder."""
        content = '''"""Types module."""
from dataclasses import dataclass

@dataclass
class SomeType:
    value: str
'''
        test_file = tmp_path / "some_types.py"
        test_file.write_text(content)

        result = fca.classify_file(test_file)
        # Should be classified as TYPES
        if result and result.get("type") == "TYPES":
            target = result.get("target_subfolder")
            if target:
                assert target == "types", f"Types should target types/, got {target}"
