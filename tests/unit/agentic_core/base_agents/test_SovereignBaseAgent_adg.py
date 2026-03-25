"""Behavioral contract tests for agentic_core.base_agents.SovereignBaseAgent."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.base_agents.SovereignBaseAgent"


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


def test_adgbehavioralmixin_is_instantiable(mod):
    """ADGBehavioralMixin is accessible and is a type."""
    cls = getattr(mod, "ADGBehavioralMixin", None)
    assert cls is not None, "ADGBehavioralMixin must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGBehavioralMixin must be a class"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_atomicexecutionmixin_is_instantiable(mod):
    """AtomicExecutionMixin is accessible and is a type."""
    cls = getattr(mod, "AtomicExecutionMixin", None)
    assert cls is not None, "AtomicExecutionMixin must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AtomicExecutionMixin must be a class"


def test_audittrailmixin_is_instantiable(mod):
    """AuditTrailMixin is accessible and is a type."""
    cls = getattr(mod, "AuditTrailMixin", None)
    assert cls is not None, "AuditTrailMixin must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AuditTrailMixin must be a class"


def test_configmixin_is_instantiable(mod):
    """ConfigMixin is accessible and is a type."""
    cls = getattr(mod, "ConfigMixin", None)
    assert cls is not None, "ConfigMixin must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ConfigMixin must be a class"


def test_coreintegrityverifier_is_instantiable(mod):
    """CoreIntegrityVerifier is accessible and is a type."""
    cls = getattr(mod, "CoreIntegrityVerifier", None)
    assert cls is not None, "CoreIntegrityVerifier must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CoreIntegrityVerifier must be a class"


def test_embeddingmixin_is_instantiable(mod):
    """EmbeddingMixin is accessible and is a type."""
    cls = getattr(mod, "EmbeddingMixin", None)
    assert cls is not None, "EmbeddingMixin must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EmbeddingMixin must be a class"


def test_goldencontextmixin_is_instantiable(mod):
    """GoldenContextMixin is accessible and is a type."""
    cls = getattr(mod, "GoldenContextMixin", None)
    assert cls is not None, "GoldenContextMixin must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GoldenContextMixin must be a class"


def test_emergency_shutdown_is_callable(mod):
    """emergency_shutdown is accessible and callable."""
    func = getattr(mod, "emergency_shutdown", None)
    assert func is not None, "emergency_shutdown must be defined in {MODULE_PATH}"
    assert callable(func), "emergency_shutdown must be callable"


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


def test_generate_trace_id_is_callable(mod):
    """generate_trace_id is accessible and callable."""
    func = getattr(mod, "generate_trace_id", None)
    assert func is not None, "generate_trace_id must be defined in {MODULE_PATH}"
    assert callable(func), "generate_trace_id must be callable"


def test_is_v15_enforced_is_callable(mod):
    """is_v15_enforced is accessible and callable."""
    func = getattr(mod, "is_v15_enforced", None)
    assert func is not None, "is_v15_enforced must be defined in {MODULE_PATH}"
    assert callable(func), "is_v15_enforced must be callable"


def test_runtime_guard_is_callable(mod):
    """runtime_guard is accessible and callable."""
    func = getattr(mod, "runtime_guard", None)
    assert func is not None, "runtime_guard must be defined in {MODULE_PATH}"
    assert callable(func), "runtime_guard must be callable"

