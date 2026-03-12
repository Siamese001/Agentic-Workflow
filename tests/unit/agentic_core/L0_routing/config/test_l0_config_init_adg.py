"""ADG-driven tests for agentic_core/L0_routing/config/__init__.py — fan_in=139.

This is the highest-risk uncovered module: 139 callers depend on symbols
re-exported through this package. Tests verify the public API surface is
stable and all advertised symbols are importable.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestL0ConfigPackageImports:
    """All __all__ symbols must be importable from the package root."""

    def test_path_constants_re_exported(self):
        from agentic_core.L0_routing.config import (
            AGENTIC_CORE_DIR,
            APPS_LIC_DIR,
            APPS_RG_DIR,
            APPS_SHARED_DIR,
            ARCHIVES_DIR,
            GLOBAL_EXCLUDED_DIRS,
            L0_ROUTING_DIR,
            L1_COGNITION_DIR,
            L2_EXECUTION_DIR,
            L3_ORCHESTRATION_DIR,
            L4_STATE_DIR,
            L5_SAFETY_DIR,
            L6_OBSERVABILITY_DIR,
            LAYER_ROOTS,
            OPS_SCRIPTS_DIR,
            TESTS_DIR,
        )
        assert isinstance(AGENTIC_CORE_DIR, str)
        assert isinstance(TESTS_DIR, str)
        assert isinstance(LAYER_ROOTS, (list, tuple, frozenset, set))

    def test_structure_blueprint_data_re_exported(self):
        from agentic_core.L0_routing.config import (
            APP_DOMAIN_PREFIXES,
            FILETYPE_TO_FOLDER,
            FOLDER_PURITY_RULES,
            LAYER_KEYWORD_AFFINITY,
            SUFFIX_TO_FOLDER,
        )
        assert isinstance(FILETYPE_TO_FOLDER, dict)
        assert isinstance(SUFFIX_TO_FOLDER, dict)

    def test_get_validated_project_root_callable(self):
        from agentic_core.L0_routing.config import get_validated_project_root
        assert callable(get_validated_project_root)

    def test_get_validated_project_root_returns_path(self, tmp_path):
        from pathlib import Path
        from agentic_core.L0_routing.config import get_validated_project_root
        root = get_validated_project_root()
        assert isinstance(root, Path)
        assert root.is_dir()

    def test_all_path_constants_are_strings(self):
        from agentic_core.L0_routing.config import (
            AGENTIC_CORE_DIR,
            APPS_LIC_DIR,
            APPS_RG_DIR,
            APPS_SHARED_DIR,
            L0_ROUTING_DIR,
            OPS_SCRIPTS_DIR,
            SCRIPTS_DIR,
            TESTS_DIR,
        )
        for const in (
            AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR,
            L0_ROUTING_DIR, OPS_SCRIPTS_DIR, SCRIPTS_DIR, TESTS_DIR,
        ):
            assert isinstance(const, str), f"Expected str, got {type(const)} for {const!r}"
            assert len(const) > 0

    def test_layer_roots_covers_all_layers(self):
        from agentic_core.L0_routing.config import LAYER_ROOTS
        layers = list(LAYER_ROOTS)
        assert len(layers) >= 6

    def test_forbidden_ephemeral_patterns_is_sequence(self):
        from agentic_core.L0_routing.config import FORBIDDEN_EPHEMERAL_PATTERNS
        assert hasattr(FORBIDDEN_EPHEMERAL_PATTERNS, '__iter__')

    def test_root_whitelist_is_sequence(self):
        from agentic_core.L0_routing.config import ROOT_WHITELIST
        assert hasattr(ROOT_WHITELIST, '__iter__')

    def test_agent_discovery_json_is_string(self):
        from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON
        assert isinstance(AGENT_DISCOVERY_JSON, str)
        assert AGENT_DISCOVERY_JSON.endswith(".json")


class TestL0ConfigStability:
    """Key constants must have stable, expected values."""

    def test_agentic_core_dir_value(self):
        from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
        assert AGENTIC_CORE_DIR == "agentic_core"

    def test_tests_dir_value(self):
        from agentic_core.L0_routing.config import TESTS_DIR
        assert TESTS_DIR == "tests"

    def test_ops_scripts_dir_value(self):
        from agentic_core.L0_routing.config import OPS_SCRIPTS_DIR
        assert OPS_SCRIPTS_DIR == "ops_scripts"
