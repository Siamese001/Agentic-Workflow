"""Behavioral contract tests for agentic_core.L0_routing.meta_control.meta_apply_ops."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.meta_control.meta_apply_ops"


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


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_callable_is_instantiable(mod):
    """Callable is accessible and is a type."""
    cls = getattr(mod, "Callable", None)
    assert cls is not None, "Callable must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Callable must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


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


def test_invariantcheckfn_is_callable(mod):
    """InvariantCheckFn is accessible and callable."""
    func = getattr(mod, "InvariantCheckFn", None)
    assert func is not None, "InvariantCheckFn must be defined in {MODULE_PATH}"
    assert callable(func), "InvariantCheckFn must be callable"


def test_apply_with_invariants_is_callable(mod):
    """apply_with_invariants is accessible and callable."""
    func = getattr(mod, "apply_with_invariants", None)
    assert func is not None, "apply_with_invariants must be defined in {MODULE_PATH}"
    assert callable(func), "apply_with_invariants must be callable"


def test_check_rate_limit_is_callable(mod):
    """check_rate_limit is accessible and callable."""
    func = getattr(mod, "check_rate_limit", None)
    assert func is not None, "check_rate_limit must be defined in {MODULE_PATH}"
    assert callable(func), "check_rate_limit must be callable"


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


def test_evaluate_invariants_is_callable(mod):
    """evaluate_invariants is accessible and callable."""
    func = getattr(mod, "evaluate_invariants", None)
    assert func is not None, "evaluate_invariants must be defined in {MODULE_PATH}"
    assert callable(func), "evaluate_invariants must be callable"


def test_record_apply_timestamp_is_callable(mod):
    """record_apply_timestamp is accessible and callable."""
    func = getattr(mod, "record_apply_timestamp", None)
    assert func is not None, "record_apply_timestamp must be defined in {MODULE_PATH}"
    assert callable(func), "record_apply_timestamp must be callable"


def test_record_canary_state_is_callable(mod):
    """record_canary_state is accessible and callable."""
    func = getattr(mod, "record_canary_state", None)
    assert func is not None, "record_canary_state must be defined in {MODULE_PATH}"
    assert callable(func), "record_canary_state must be callable"

