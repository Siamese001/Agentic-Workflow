"""Test coverage for `agentic_core.L0_routing.config.__init__`.

Wave 1 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md`.

Module rationale: this `__init__.py` re-exports 50+ canonical path constants
and structure-blueprint data used by 120 downstream prod modules. Highest
fan-in untested module in the repo. These tests assert the public surface
remains stable so downstream callers do not silently break.
"""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit

CONFIG_PKG = "agentic_core.L0_routing.config"


@pytest.fixture(scope="module")
def config_pkg():
    return pytest.importorskip(CONFIG_PKG)


def test_module_imports_cleanly():
    """Module must import without side-effects raising."""
    mod = importlib.import_module(CONFIG_PKG)
    assert mod is not None


def test_all_export_list_is_non_empty(config_pkg):
    exported = getattr(config_pkg, "__all__", None)
    assert exported is not None, "__all__ must be defined"
    assert isinstance(exported, list)
    assert len(exported) >= 40, "expected at least 40 re-exports"


def test_all_exports_are_resolvable(config_pkg):
    """Every name in __all__ must resolve to an attribute on the module."""
    missing = [name for name in config_pkg.__all__ if not hasattr(config_pkg, name)]
    assert not missing, f"__all__ names not bound on module: {missing}"


@pytest.mark.parametrize(
    "constant_name",
    [
        "AGENTIC_CORE_DIR",
        "L0_ROUTING_DIR",
        "L1_COGNITION_DIR",
        "L2_EXECUTION_DIR",
        "L3_ORCHESTRATION_DIR",
        "L4_STATE_DIR",
        "L5_SAFETY_DIR",
        "L6_OBSERVABILITY_DIR",
        "TESTS_DIR",
        "OPS_SCRIPTS_DIR",
    ],
)
def test_layer_dir_constants_present(config_pkg, constant_name):
    """Layer-root path constants must be exposed for downstream importers."""
    assert hasattr(config_pkg, constant_name)
    value = getattr(config_pkg, constant_name)
    assert value is not None


@pytest.mark.parametrize(
    "helper_name",
    ["get_validated_project_root", "get_apps_directories", "get_all_apps_paths"],
)
def test_path_helpers_are_callable(config_pkg, helper_name):
    helper = getattr(config_pkg, helper_name, None)
    assert callable(helper), f"{helper_name} must be callable"


@pytest.mark.parametrize(
    "blueprint_name",
    [
        "APP_DOMAIN_PREFIXES",
        "AST_PLACEMENT_SIGNALS",
        "CANONICAL_LOCATION_PRIORITY",
        "FILETYPE_TO_FOLDER",
        "FOLDER_PURITY_RULES",
        "L4_APPROVED_FOLDERS",
        "LAYER_KEYWORD_AFFINITY",
        "LAYER_PREFIX_PATTERN",
        "LAYER_ROOTS",
    ],
)
def test_structure_blueprint_data_present(config_pkg, blueprint_name):
    """Structure-blueprint constants must be re-exported from this package."""
    assert hasattr(config_pkg, blueprint_name)
    assert getattr(config_pkg, blueprint_name) is not None


def test_get_validated_project_root_returns_path(config_pkg):
    root = config_pkg.get_validated_project_root()
    assert root is not None
    # Should be either a str or pathlib.Path
    assert hasattr(root, "__fspath__") or isinstance(root, str)


def test_no_unexpected_private_re_exports(config_pkg):
    """__all__ should not advertise underscored names."""
    private = [n for n in config_pkg.__all__ if n.startswith("_")]
    assert not private, f"__all__ leaks private names: {private}"
