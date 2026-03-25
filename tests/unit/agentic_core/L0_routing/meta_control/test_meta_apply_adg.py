"""Behavioral contract tests for agentic_core.L0_routing.meta_control.meta_apply."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.meta_control.meta_apply"


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


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_semanticclocksnapshot_is_instantiable(mod):
    """SemanticClockSnapshot is accessible and is a type."""
    cls = getattr(mod, "SemanticClockSnapshot", None)
    assert cls is not None, "SemanticClockSnapshot must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SemanticClockSnapshot must be a class"


def test_literal_is_callable(mod):
    """Literal is accessible and callable."""
    func = getattr(mod, "Literal", None)
    assert func is not None, "Literal must be defined in {MODULE_PATH}"
    assert callable(func), "Literal must be callable"


def test_apply_meta_learning_rollout_is_callable(mod):
    """apply_meta_learning_rollout is accessible and callable."""
    func = getattr(mod, "apply_meta_learning_rollout", None)
    assert func is not None, "apply_meta_learning_rollout must be defined in {MODULE_PATH}"
    assert callable(func), "apply_meta_learning_rollout must be callable"


def test_assert_no_persistent_write_is_callable(mod):
    """assert_no_persistent_write is accessible and callable."""
    func = getattr(mod, "assert_no_persistent_write", None)
    assert func is not None, "assert_no_persistent_write must be defined in {MODULE_PATH}"
    assert callable(func), "assert_no_persistent_write must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_validate_semantic_clock_is_callable(mod):
    """validate_semantic_clock is accessible and callable."""
    func = getattr(mod, "validate_semantic_clock", None)
    assert func is not None, "validate_semantic_clock must be defined in {MODULE_PATH}"
    assert callable(func), "validate_semantic_clock must be callable"

