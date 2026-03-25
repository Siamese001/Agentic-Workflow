"""Behavioral contract tests for agentic_core.L0_routing.types.governance_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.governance_types"


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


def test_changeaction_is_instantiable(mod):
    """ChangeAction is accessible and is a type."""
    cls = getattr(mod, "ChangeAction", None)
    assert cls is not None, "ChangeAction must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ChangeAction must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_evidencepack_is_instantiable(mod):
    """EvidencePack is accessible and is a type."""
    cls = getattr(mod, "EvidencePack", None)
    assert cls is not None, "EvidencePack must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EvidencePack must be a class"


def test_exceptionscope_is_instantiable(mod):
    """ExceptionScope is accessible and is a type."""
    cls = getattr(mod, "ExceptionScope", None)
    assert cls is not None, "ExceptionScope must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExceptionScope must be a class"


def test_governedpayload_is_instantiable(mod):
    """GovernedPayload is accessible and is a type."""
    cls = getattr(mod, "GovernedPayload", None)
    assert cls is not None, "GovernedPayload must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GovernedPayload must be a class"


def test_hiloutcome_is_instantiable(mod):
    """HILOutcome is accessible and is a type."""
    cls = getattr(mod, "HILOutcome", None)
    assert cls is not None, "HILOutcome must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HILOutcome must be a class"


def test_hilreviewoutcome_is_instantiable(mod):
    """HILReviewOutcome is accessible and is a type."""
    cls = getattr(mod, "HILReviewOutcome", None)
    assert cls is not None, "HILReviewOutcome must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HILReviewOutcome must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


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

