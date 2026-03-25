"""Behavioral contract tests for agentic_core.interfaces.meta_control."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.interfaces.meta_control"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_capabilitytokenartifact_is_instantiable(mod):
    """CapabilityTokenArtifact is accessible and is a type."""
    cls = getattr(mod, "CapabilityTokenArtifact", None)
    assert cls is not None, "CapabilityTokenArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CapabilityTokenArtifact must be a class"


def test_configdeltaartifact_is_instantiable(mod):
    """ConfigDeltaArtifact is accessible and is a type."""
    cls = getattr(mod, "ConfigDeltaArtifact", None)
    assert cls is not None, "ConfigDeltaArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ConfigDeltaArtifact must be a class"


def test_semanticclocksnapshot_is_instantiable(mod):
    """SemanticClockSnapshot is accessible and is a type."""
    cls = getattr(mod, "SemanticClockSnapshot", None)
    assert cls is not None, "SemanticClockSnapshot must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SemanticClockSnapshot must be a class"


def test_apply_change_package_readonly_is_callable(mod):
    """apply_change_package_readonly is accessible and callable."""
    func = getattr(mod, "apply_change_package_readonly", None)
    assert func is not None, "apply_change_package_readonly must be defined in {MODULE_PATH}"
    assert callable(func), "apply_change_package_readonly must be callable"


def test_apply_meta_learning_rollout_is_callable(mod):
    """apply_meta_learning_rollout is accessible and callable."""
    func = getattr(mod, "apply_meta_learning_rollout", None)
    assert func is not None, "apply_meta_learning_rollout must be defined in {MODULE_PATH}"
    assert callable(func), "apply_meta_learning_rollout must be callable"


def test_apply_with_invariants_is_callable(mod):
    """apply_with_invariants is accessible and callable."""
    func = getattr(mod, "apply_with_invariants", None)
    assert func is not None, "apply_with_invariants must be defined in {MODULE_PATH}"
    assert callable(func), "apply_with_invariants must be callable"


def test_canonical_json_is_callable(mod):
    """canonical_json is accessible and callable."""
    func = getattr(mod, "canonical_json", None)
    assert func is not None, "canonical_json must be defined in {MODULE_PATH}"
    assert callable(func), "canonical_json must be callable"


def test_load_current_is_callable(mod):
    """load_current is accessible and callable."""
    func = getattr(mod, "load_current", None)
    assert func is not None, "load_current must be defined in {MODULE_PATH}"
    assert callable(func), "load_current must be callable"


def test_validate_component_allowed_is_callable(mod):
    """validate_component_allowed is accessible and callable."""
    func = getattr(mod, "validate_component_allowed", None)
    assert func is not None, "validate_component_allowed must be defined in {MODULE_PATH}"
    assert callable(func), "validate_component_allowed must be callable"

