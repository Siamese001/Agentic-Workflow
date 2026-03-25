"""Behavioral contract tests for agentic_core.L0_routing.enforcement.crypto_trust_contracts."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.enforcement.crypto_trust_contracts"


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


def test_escalationrequirederror_is_instantiable(mod):
    """EscalationRequiredError is accessible and is a type."""
    cls = getattr(mod, "EscalationRequiredError", None)
    assert cls is not None, "EscalationRequiredError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EscalationRequiredError must be a class"


def test_hashmismatchtracker_is_instantiable(mod):
    """HashMismatchTracker is accessible and is a type."""
    cls = getattr(mod, "HashMismatchTracker", None)
    assert cls is not None, "HashMismatchTracker must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HashMismatchTracker must be a class"


def test_keystatus_is_instantiable(mod):
    """KeyStatus is accessible and is a type."""
    cls = getattr(mod, "KeyStatus", None)
    assert cls is not None, "KeyStatus must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "KeyStatus must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_replaydetectederror_is_instantiable(mod):
    """ReplayDetectedError is accessible and is a type."""
    cls = getattr(mod, "ReplayDetectedError", None)
    assert cls is not None, "ReplayDetectedError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ReplayDetectedError must be a class"


def test_replayguardrecord_is_instantiable(mod):
    """ReplayGuardRecord is accessible and is a type."""
    cls = getattr(mod, "ReplayGuardRecord", None)
    assert cls is not None, "ReplayGuardRecord must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ReplayGuardRecord must be a class"


def test_replayguardstore_is_instantiable(mod):
    """ReplayGuardStore is accessible and is a type."""
    cls = getattr(mod, "ReplayGuardStore", None)
    assert cls is not None, "ReplayGuardStore must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ReplayGuardStore must be a class"


def test_signatureenclave_is_instantiable(mod):
    """SignatureEnclave is accessible and is a type."""
    cls = getattr(mod, "SignatureEnclave", None)
    assert cls is not None, "SignatureEnclave must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SignatureEnclave must be a class"


def test_build_signed_guardian_artifact_is_callable(mod):
    """build_signed_guardian_artifact is accessible and callable."""
    func = getattr(mod, "build_signed_guardian_artifact", None)
    assert func is not None, "build_signed_guardian_artifact must be defined in {MODULE_PATH}"
    assert callable(func), "build_signed_guardian_artifact must be callable"


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


def test_hash_artifact_canonical_is_callable(mod):
    """hash_artifact_canonical is accessible and callable."""
    func = getattr(mod, "hash_artifact_canonical", None)
    assert func is not None, "hash_artifact_canonical must be defined in {MODULE_PATH}"
    assert callable(func), "hash_artifact_canonical must be callable"


def test_record_and_block_replay_is_callable(mod):
    """record_and_block_replay is accessible and callable."""
    func = getattr(mod, "record_and_block_replay", None)
    assert func is not None, "record_and_block_replay must be defined in {MODULE_PATH}"
    assert callable(func), "record_and_block_replay must be callable"


def test_record_hash_mismatch_is_callable(mod):
    """record_hash_mismatch is accessible and callable."""
    func = getattr(mod, "record_hash_mismatch", None)
    assert func is not None, "record_hash_mismatch must be defined in {MODULE_PATH}"
    assert callable(func), "record_hash_mismatch must be callable"


def test_sign_artifact_is_callable(mod):
    """sign_artifact is accessible and callable."""
    func = getattr(mod, "sign_artifact", None)
    assert func is not None, "sign_artifact must be defined in {MODULE_PATH}"
    assert callable(func), "sign_artifact must be callable"


def test_verify_signature_is_callable(mod):
    """verify_signature is accessible and callable."""
    func = getattr(mod, "verify_signature", None)
    assert func is not None, "verify_signature must be defined in {MODULE_PATH}"
    assert callable(func), "verify_signature must be callable"

