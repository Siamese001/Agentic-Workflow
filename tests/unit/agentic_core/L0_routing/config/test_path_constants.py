"""Runtime-hardened tests for L0 routing path constants."""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit

PATH_CONSTANTS_MODULE = "agentic_core.L0_routing.config.path_constants"
CONFIG_MODULE = "agentic_core.L0_routing.config"
EXPECTED_VALUES = {
    "HEALING_CONFIDENCE_X": 0.80,
    "HEALING_CONFIDENCE_Y": 0.50,
    "SSOT_SCORE_THRESHOLD_DET": 13,
    "SSOT_SCORE_THRESHOLD_QWEN": 26,
    "QWEN_14B_MODEL_ID": "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4",
}


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
    assert path_constants.HEALING_CONFIDENCE_X > path_constants.HEALING_CONFIDENCE_Y
    assert 0.0 < path_constants.HEALING_CONFIDENCE_Y < 1.0
    assert 0.0 < path_constants.HEALING_CONFIDENCE_X < 1.0


def test_config_helpers_exist_and_are_callable(config_pkg):
    for name in ["get_validated_project_root", "get_apps_directories"]:
        value = getattr(config_pkg, name, None)
        assert callable(value), f"{name} must be callable on {CONFIG_MODULE}"
