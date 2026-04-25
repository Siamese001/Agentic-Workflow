"""Tests for the signing adapter in tools/eval/_gateway_factories.py (F4.2)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import pytest

from tools.eval._gateway_factories import (
    _SovereignAdapter,
    _build_signed_artifact,
    _compute_artifact_signature,
    sovereign_default,
)


@dataclass
class _StubResponse:
    text: str = "stub-response"


class _StubGateway:
    """Minimal stub that verifies the artifact signature before responding."""

    def __init__(self, secret_key: bytes) -> None:
        self.secret_key = secret_key
        self.calls = 0

    def generate(self, artifact: Any) -> _StubResponse:
        if not artifact.verify_signature(self.secret_key):
            raise AssertionError("artifact signature failed verification")
        self.calls += 1
        return _StubResponse(text=f"ok:{artifact.trace_id}")


def test_build_signed_artifact_produces_valid_signature():
    secret = b"test-secret"
    artifact = _build_signed_artifact(
        system_prompt="be helpful",
        user_prompt="hi",
        seed=42,
        max_tokens=128,
        temperature=0.0,
        secret_key=secret,
    )
    assert artifact.signature != ""
    assert artifact.verify_signature(secret) is True


def test_signature_matches_artifact_internal_contract():
    secret = b"another-secret"
    artifact = _build_signed_artifact(
        system_prompt="system",
        user_prompt="user",
        seed=1,
        max_tokens=64,
        temperature=0.2,
        secret_key=secret,
    )
    # The factory's helper and the artifact's internal computation must
    # produce the same digest byte-for-byte.
    assert _compute_artifact_signature(artifact, secret) == artifact.signature


def test_signature_fails_with_wrong_key():
    artifact = _build_signed_artifact(
        system_prompt="sys",
        user_prompt="usr",
        seed=3,
        max_tokens=32,
        temperature=0.0,
        secret_key=b"right",
    )
    assert artifact.verify_signature(b"wrong") is False


def test_adapter_round_trip_through_stub_gateway():
    secret = b"adapter-secret"
    gateway = _StubGateway(secret_key=secret)
    adapter = _SovereignAdapter(gateway=gateway, secret_key=secret)
    out = adapter.generate("system", "user", seed=7)
    assert out.startswith("ok:eval-synth-7")
    assert gateway.calls == 1


def test_sovereign_default_fails_closed_without_secret(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("SOVEREIGN_GATEWAY_HMAC", raising=False)
    with pytest.raises(RuntimeError, match="SOVEREIGN_GATEWAY_HMAC"):
        sovereign_default()
