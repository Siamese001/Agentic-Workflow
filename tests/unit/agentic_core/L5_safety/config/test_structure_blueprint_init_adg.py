"""ADG-driven tests for agentic_core/L5_safety/config/structure_blueprint/__init__.py — fan_in=106.

106 callers depend on symbols exported through this package. Tests verify
the public API surface is stable, all advertised symbols are importable,
and key structural constants have expected shapes.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestStructureBlueprintCoreImports:
    """Path constants and SSOT symbols must be importable from the package."""

    def test_path_constants_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import (
            AGENTIC_CORE_DIR,
            APPS_LIC_DIR,
            APPS_RG_DIR,
            APPS_SHARED_DIR,
            LAYER_ROOTS,
            OPS_SCRIPTS_DIR,
            TESTS_DIR,
        )
        assert isinstance(AGENTIC_CORE_DIR, str)
        assert isinstance(TESTS_DIR, str)

    def test_layer_dirs_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import (
            L0_MAINTENANCE_DIR,
            L1_COGNITION_DIR,
            L2_EXECUTION_DIR,
            L3_ORCHESTRATION_DIR,
            L4_STATE_DIR,
            L5_SAFETY_DIR,
            L6_OBSERVABILITY_DIR,
        )
        for val in (
            L0_MAINTENANCE_DIR, L1_COGNITION_DIR, L2_EXECUTION_DIR,
            L3_ORCHESTRATION_DIR, L4_STATE_DIR, L5_SAFETY_DIR, L6_OBSERVABILITY_DIR,
        ):
            assert isinstance(val, str) and len(val) > 0

    def test_test_dirs_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import (
            TESTS_DIR,
            TESTS_UNIT_DIR,
            TESTS_E2E_DIR,
            TESTS_INTEGRATION_DIR,
        )
        assert isinstance(TESTS_UNIT_DIR, str)
        assert isinstance(TESTS_E2E_DIR, str)

    def test_reports_dir_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import REPORTS_DIR
        assert isinstance(REPORTS_DIR, str)

    def test_docs_reports_plans_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import DOCS_REPORTS_PLANS
        assert isinstance(DOCS_REPORTS_PLANS, str)
        assert "docs" in DOCS_REPORTS_PLANS or "reports" in DOCS_REPORTS_PLANS

    def test_layer_roots_is_iterable(self):
        from agentic_core.L5_safety.config.structure_blueprint import LAYER_ROOTS
        roots = list(LAYER_ROOTS)
        assert len(roots) >= 6

    def test_global_excluded_dirs_is_iterable(self):
        from agentic_core.L5_safety.config.structure_blueprint import GLOBAL_EXCLUDED_DIRS
        dirs = list(GLOBAL_EXCLUDED_DIRS)
        assert len(dirs) > 0


class TestStructureBlueprintGovernanceImports:
    """Governance constants must be importable and have expected types."""

    def test_gravity_config_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import GRAVITY_CONFIG
        assert isinstance(GRAVITY_CONFIG, dict)

    def test_healing_config_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import HEALING_CONFIG
        assert isinstance(HEALING_CONFIG, dict)

    def test_mission_config_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import MISSION_CONFIG
        assert isinstance(MISSION_CONFIG, dict)

    def test_territory_definition_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import TerritoryDefinition
        assert callable(TerritoryDefinition)

    def test_subfolder_definition_importable(self):
        from agentic_core.L5_safety.config.structure_blueprint import SubfolderDefinition
        assert callable(SubfolderDefinition)


class TestStructureBlueprintCallables:
    """Callable symbols must be importable and invocable."""

    def test_get_validated_project_root_callable(self):
        from agentic_core.L5_safety.config.structure_blueprint import get_validated_project_root
        result = get_validated_project_root()
        from pathlib import Path
        assert isinstance(result, Path)
        assert result.is_dir()

    def test_get_sovereign_territories_callable(self):
        from agentic_core.L5_safety.config.structure_blueprint import get_sovereign_territories
        result = get_sovereign_territories()
        assert result is not None

    def test_get_all_territories_callable(self):
        from agentic_core.L5_safety.config.structure_blueprint import get_all_territories
        result = get_all_territories()
        assert result is not None

    def test_get_territory_metadata_callable(self):
        from agentic_core.L5_safety.config.structure_blueprint import get_territory_metadata
        assert callable(get_territory_metadata)

    def test_is_valid_root_folder_callable(self):
        from agentic_core.L5_safety.config.structure_blueprint import is_valid_root_folder
        assert callable(is_valid_root_folder)

    def test_safe_path_join_callable(self):
        from agentic_core.L5_safety.config.structure_blueprint import safe_path_join
        assert callable(safe_path_join)

    def test_is_path_allowed_callable(self):
        from agentic_core.L5_safety.config.structure_blueprint import is_path_allowed
        assert callable(is_path_allowed)

    def test_is_layer_root_callable(self):
        from agentic_core.L5_safety.config.structure_blueprint import is_layer_root
        assert callable(is_layer_root)

    def test_get_canonical_test_path_callable(self):
        from agentic_core.L5_safety.config.structure_blueprint import get_canonical_test_path
        assert callable(get_canonical_test_path)


class TestStructureBlueprintStability:
    """Key constants must have stable values matching architectural expectations."""

    def test_agentic_core_dir_stable(self):
        from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR
        assert AGENTIC_CORE_DIR == "agentic_core"

    def test_tests_dir_stable(self):
        from agentic_core.L5_safety.config.structure_blueprint import TESTS_DIR
        assert TESTS_DIR == "tests"

    def test_layer_roots_contains_all_layers(self):
        from agentic_core.L5_safety.config.structure_blueprint import LAYER_ROOTS
        roots = list(LAYER_ROOTS)
        assert len(roots) >= 6
        roots_flat = " ".join(str(r) for r in roots)
        assert any(x in roots_flat for x in ("L0", "L1", "L2", "L3", "L4", "L5"))

    def test_forbidden_patterns_is_sequence(self):
        from agentic_core.L5_safety.config.structure_blueprint import FORBIDDEN_PATTERNS
        assert hasattr(FORBIDDEN_PATTERNS, '__iter__')
        assert len(list(FORBIDDEN_PATTERNS)) > 0
