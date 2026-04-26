"""Unit tests for PA.7 signature + canonical manifest."""

from __future__ import annotations

from agentic_core.prompt_governance.prompt_assembly.pa7_signature import (
    SIGNATURE_VERSION,
    canonicalize_manifest,
    compute_manifest_hash,
    compute_replay_key,
    sign_manifest,
    verify_signature,
)


def test_canonicalize_is_deterministic_under_key_reorder():
    a = canonicalize_manifest({"b": 1, "a": 2, "c": [3, 4]})
    b = canonicalize_manifest({"a": 2, "c": [3, 4], "b": 1})
    assert a == b


def test_canonicalize_strips_whitespace():
    out = canonicalize_manifest({"a": 1, "b": 2})
    # No whitespace per separators=(",", ":")
    assert b" " not in out


def test_manifest_hash_is_64_hex():
    cb = canonicalize_manifest({"x": 1})
    h = compute_manifest_hash(cb)
    assert len(h) == 64
    int(h, 16)  # must parse as hex


def test_replay_key_includes_nonce():
    cb = canonicalize_manifest({"x": 1})
    h = compute_manifest_hash(cb)
    rk1 = compute_replay_key(h, "nonce-A")
    rk2 = compute_replay_key(h, "nonce-B")
    assert rk1 != rk2


def test_sign_and_verify_round_trip():
    key = b"secret-key-123"
    signed = sign_manifest({"a": 1, "b": [1, 2]}, secret_key=key, idempotency_nonce="n-1")
    assert signed.signature_version == SIGNATURE_VERSION
    assert verify_signature(signed.canonical_bytes, signed.signature, secret_key=key) is True


def test_verify_fails_with_wrong_key():
    signed = sign_manifest({"a": 1}, secret_key=b"key-A")
    assert verify_signature(signed.canonical_bytes, signed.signature, secret_key=b"key-B") is False


def test_verify_fails_on_tampered_bytes():
    signed = sign_manifest({"a": 1}, secret_key=b"k")
    tampered = signed.canonical_bytes + b"x"
    assert verify_signature(tampered, signed.signature, secret_key=b"k") is False


def test_signed_manifest_carries_signing_key_reference():
    signed = sign_manifest({"a": 1}, secret_key=b"k", signing_key_reference="kms:key-1")
    assert signed.signing_key_reference == "kms:key-1"
