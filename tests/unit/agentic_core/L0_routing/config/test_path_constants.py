"""Runtime-hardened tests for L0 routing path constants."""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit

PATH_CONSTANTS_MODULE = "agentic_core.L0_routing.config.path_constants"
CONFIG_MODULE = "agentic_core.L0_routing.config"
EXPECTED_VALUES = {
    "SSOT_SCORE_THRESHOLD_DET": 13,
    "SSOT_SCORE_THRESHOLD_QWEN": 26,
}
# Registry-based local model coverage lives in test_model_registry.py.


@pytest.fixture(scope="module")
def path_constants():
    return pytest.importorskip(PATH_CONSTANTS_MODULE)


@pytest.fixture(scope="module")
def config_pkg():
    return pytest.importorskip(CONFIG_MODULE)


def test_expected_constants_exist_with_exact_values(path_constants):
    for name, expected in EXPECTED_VALUES.items():
        assert hasattr(path_constants, name), f"{name} missing from {PATH_CONSTANTS_MODULE}"
        assert getattr(path_constants, name) == expected


def test_expected_constants_are_exported(path_constants):
    exported = set(getattr(path_constants, "__all__", []))
    missing = set(EXPECTED_VALUES) - exported
    assert not missing, f"Expected constants missing from __all__: {sorted(missing)}"


def test_threshold_relationships_are_sane(path_constants):
    assert path_constants.SSOT_SCORE_THRESHOLD_DET < path_constants.SSOT_SCORE_THRESHOLD_QWEN

def test_config_helpers_exist_and_are_callable(config_pkg):
    for name in ["get_validated_project_root", "get_apps_directories"]:
        value = getattr(config_pkg, name, None)
        assert callable(value), f"{name} must be callable on {CONFIG_MODULE}"
