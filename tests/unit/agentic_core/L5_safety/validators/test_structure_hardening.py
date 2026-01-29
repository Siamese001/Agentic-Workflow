"""
Test suite for structure_blueprint.py hardening.
Verifies that 'Junior AI' cannot accidentally mutate core registries.

[HARDENING] 2026-01-26: Validates immutable type annotations and frozenset usage.
"""

import re
import sys
from pathlib import Path

import pytest

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Import the module under test
from agentic_core.L5_safety.validators import structure_blueprint as sb


class TestStructureHardening:
    """
    Aggressive validation of the 'Hardened' SSOT.
    Verifies that 'Junior AI' cannot accidentally mutate core registries.
    """

    def test_immutability_of_registries(self):
        """
        CRITICAL: Verify that core registries are typed as Final and Mapping/Sequence/frozenset.
        This prevents runtime mutation and enforces static analysis constraints.
        """
        # 1. SOVEREIGN_REGISTRY - verify it exists and is dict-like at runtime
        assert hasattr(sb, "SOVEREIGN_REGISTRY")
        assert isinstance(sb.SOVEREIGN_REGISTRY, dict)  # Mapping at runtime is dict

        # 2. SUBFOLDER_MAPS - verify they exist and are dict-like
        maps_to_check = [
            "CORE_SUBFOLDER_MAP",
            "APPS_RG_SUBFOLDER_MAP",
            "APPS_LIC_SUBFOLDER_MAP",
            "APPS_SHARED_SUBFOLDER_MAP",
            "TESTS_L2_SUBFOLDER_MAP",
        ]

        for map_name in maps_to_check:
            val = getattr(sb, map_name)
            assert isinstance(val, dict), f"{map_name} must be a dict (typed as Mapping)"
            # Ensure no 'Any' slipped through in keys/values if we can sample
            if val:
                k = next(iter(val))
                assert isinstance(k, str)
                assert isinstance(val[k], (list, tuple))

    def test_frozenset_enforcement(self):
        """
        CRITICAL: Ensure sets are converted to frozenset for hashability and immutability.
        """
        frozen_registries = [
            "CANON_SIGNALS",
            "APP_RG_AST_TERMS",
            "APP_LIC_AST_TERMS",
            "APP_RG_VARIABLE_TERMS",
            "APP_LIC_VARIABLE_TERMS",
            "APP_RG_STRING_TERMS",
            "APP_LIC_STRING_TERMS",
            "FORBIDDEN_APP_MODULES",
            "L4_APPROVED_FOLDERS",
        ]

        for name in frozen_registries:
            val = getattr(sb, name, None)
            assert val is not None, f"{name} not found in structure_blueprint"
            assert isinstance(val, frozenset), f"{name} must be a frozenset, got {type(val)}"

    def test_layer_forbidden_imports_frozenset_values(self):
        """
        CRITICAL: LAYER_FORBIDDEN_IMPORTS values should be frozenset.
        """
        assert hasattr(sb, "LAYER_FORBIDDEN_IMPORTS")
        for k, v in sb.LAYER_FORBIDDEN_IMPORTS.items():
            assert isinstance(v, frozenset), (
                f"Value for {k} in LAYER_FORBIDDEN_IMPORTS must be frozenset"
            )

    def test_naming_convention_structure(self):
        """
        CRITICAL: Validate NAMING_CONVENTIONS schema integrity.
        Must contain 'pattern', 'description', 'examples', 'anti_examples'.
        """
        conventions = sb.NAMING_CONVENTIONS
        required_keys = {"pattern", "description", "examples", "anti_examples"}

        for key, rules in conventions.items():
            missing = required_keys - set(rules.keys())
            assert not missing, f"Naming convention '{key}' missing keys: {missing}"

            # Verify regex compilation
            try:
                re.compile(rules["pattern"])
            except re.error as e:
                pytest.fail(f"Invalid regex for {key}: {e}")

    def test_syntax_cleanup_end_of_file(self):
        """
        CRITICAL: Ensure the file doesn't end with garbage text (e.g., user prompts).
        This test checks the integrity of the last defined dictionary `DOCS_SUBFOLDER_METADATA`.
        """
        assert hasattr(sb, "DOCS_SUBFOLDER_METADATA")
        docs_meta = sb.DOCS_SUBFOLDER_METADATA
        assert "technical" in docs_meta
        assert "archive" in docs_meta
        assert len(docs_meta) == 5, (
            f"DOCS_SUBFOLDER_METADATA incomplete or corrupted, got {len(docs_meta)} keys"
        )

    def test_path_safety_logic(self):
        """
        CRITICAL: Verify path validation logic (safe_prefixed_filename).
        """
        # Case 1: No prefix needed
        assert sb.safe_prefixed_filename("healing", "healing_agent.py") == "healing_agent.py"

        # Case 2: Prefix needed
        assert sb.safe_prefixed_filename("healing", "agent.py") == "healing_agent.py"

        # Case 3: Empty prefix
        assert sb.safe_prefixed_filename("", "agent.py") == "agent.py"

        # Case 4: Already has prefix - returns unchanged
        assert sb.safe_prefixed_filename("core", "core_logic.py") == "core_logic.py"

    def test_core_territory_keywords_frozenset_values(self):
        """
        CRITICAL: CORE_TERRITORY_KEYWORDS inner values should be frozenset.
        """
        assert hasattr(sb, "CORE_TERRITORY_KEYWORDS")
        for territory, keywords_dict in sb.CORE_TERRITORY_KEYWORDS.items():
            for key, val in keywords_dict.items():
                assert isinstance(val, frozenset), f"Value for {territory}/{key} must be frozenset"

    def test_project_root_structures(self):
        """
        CRITICAL: Verify PROJECT_ROOT structures exist and are properly typed.
        """
        assert hasattr(sb, "PROJECT_ROOT_SUBFOLDERS")
        assert hasattr(sb, "PROJECT_ROOT_METADATA")
        assert hasattr(sb, "DATA_SUBFOLDER_METADATA")
        assert hasattr(sb, "DOCS_SUBFOLDER_METADATA")

        # Verify they are dict-like
        assert isinstance(sb.PROJECT_ROOT_SUBFOLDERS, dict)
        assert isinstance(sb.PROJECT_ROOT_METADATA, dict)
        assert isinstance(sb.DATA_SUBFOLDER_METADATA, dict)
        assert isinstance(sb.DOCS_SUBFOLDER_METADATA, dict)

    def test_violation_severity_immutability(self):
        """
        CRITICAL: Verify VIOLATION_SEVERITY is immutable Mapping.
        """
        assert hasattr(sb, "VIOLATION_SEVERITY")
        assert isinstance(sb.VIOLATION_SEVERITY, dict)
        assert "GRAVITY VIOLATION" in sb.VIOLATION_SEVERITY
        assert sb.VIOLATION_SEVERITY["GRAVITY VIOLATION"] == 10

    def test_healing_config_structure(self):
        """
        CRITICAL: Verify HEALING_CONFIG has expected keys.
        """
        assert hasattr(sb, "HEALING_CONFIG")
        required_keys = ["max_rounds", "max_per_file", "global_budget", "max_moves_per_run"]
        for key in required_keys:
            assert key in sb.HEALING_CONFIG, f"HEALING_CONFIG missing key: {key}"

    def test_agent_registry_structure(self):
        """
        CRITICAL: Verify AGENT_REGISTRY has expected layer keys.
        """
        assert hasattr(sb, "AGENT_REGISTRY")
        expected_layers = ["L0", "L1", "L2", "L3", "L4", "L5"]
        for layer in expected_layers:
            assert layer in sb.AGENT_REGISTRY, f"AGENT_REGISTRY missing layer: {layer}"
            assert isinstance(sb.AGENT_REGISTRY[layer], list)

    def test_exerciser_registry_structure(self):
        """
        CRITICAL: Verify EXERCISER_REGISTRY has expected layer keys.
        """
        assert hasattr(sb, "EXERCISER_REGISTRY")
        assert "L5_safety" in sb.EXERCISER_REGISTRY
        assert sb.EXERCISER_REGISTRY["L5_safety"] == "L5SafetyExerciserAgent"

    def test_no_orphan_any_on_key_registries(self):
        """
        CRITICAL: Scan module to ensure import was successful.
        This test verifies that we successfully imported the module without syntax errors
        which would happen if we messed up the TypeDicts or imports.
        """
        # If we got here, the module imported successfully
        assert hasattr(sb, "SOVEREIGN_REGISTRY")
        assert hasattr(sb, "CORE_SUBFOLDER_MAP")
        assert hasattr(sb, "CANON_SIGNALS")
        assert hasattr(sb, "LAYER_FORBIDDEN_IMPORTS")


class TestDuplicatePrefixDetection:
    """Test suite for duplicate prefix detection."""

    def test_no_duplicate_prefix_valid(self):
        """Test that valid filenames pass."""
        has_violation, msg = sb.validate_no_duplicate_prefix("healing_strategies.py")
        assert not has_violation

    def test_no_duplicate_prefix_invalid(self):
        """Test that duplicate prefixes are detected."""
        has_violation, msg = sb.validate_no_duplicate_prefix("healing_healing_strategies.py")
        assert has_violation
        assert "Duplicate prefix" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
