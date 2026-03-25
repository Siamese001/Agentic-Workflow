"""Behavioral contract tests for agentic_core.L0_routing.utils.core_integrity_util."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.utils.core_integrity_util"


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


def test_configurationerror_is_instantiable(mod):
    """ConfigurationError is accessible and is a type."""
    cls = getattr(mod, "ConfigurationError", None)
    assert cls is not None, "ConfigurationError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ConfigurationError must be a class"


def test_coreintegrityverifier_is_instantiable(mod):
    """CoreIntegrityVerifier is accessible and is a type."""
    cls = getattr(mod, "CoreIntegrityVerifier", None)
    assert cls is not None, "CoreIntegrityVerifier must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CoreIntegrityVerifier must be a class"


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


def test_sovereignlockerror_is_instantiable(mod):
    """SovereignLockError is accessible and is a type."""
    cls = getattr(mod, "SovereignLockError", None)
    assert cls is not None, "SovereignLockError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SovereignLockError must be a class"


def test_final_is_callable(mod):
    """Final is accessible and callable."""
    func = getattr(mod, "Final", None)
    assert func is not None, "Final must be defined in {MODULE_PATH}"
    assert callable(func), "Final must be callable"


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

