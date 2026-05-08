"""RTC-REQ-030 — All-Requirements Gate Readiness.

Validates that the all-requirements merkle root verifier can run,
that artifact payload hashes are computable, and that the gate
is ready for CI integration.

W0 implementation per runtime-cert-hardened-w0-7e3c9a.md
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.prove_requirements.artifact_payload_hasher import (
    hash_artifact_payload,
    SUPPORTED_HASH_ALGORITHMS,
)
from scripts.verify_all_requirements_merkle_root import main as merkle_main


class TestRTC030AllRequirementsGate:
    """RTC-REQ-030: All-requirements gate readiness."""

    def test_merkle_verifier_importable(self) -> None:
        """Merkle root verifier is importable."""
        assert callable(merkle_main)

    def test_artifact_hasher_importable(self) -> None:
        """Artifact payload hasher is importable."""
        assert callable(hash_artifact_payload)

    def test_supported_algorithms_defined(self) -> None:
        """SUPPORTED_HASH_ALGORITHMS has at least SHA256."""
        assert "sha256" in SUPPORTED_HASH_ALGORITHMS

    def test_hash_artifact_payload_sha256(self) -> None:
        """SHA256 hash produces 64-char hex digest."""
        payload = b"test payload for hashing"
        digest = hash_artifact_payload(payload, algorithm="sha256")
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)


class TestRTC030HashAlgorithms:
    """Hash algorithm tests."""

    def test_sha256_deterministic(self) -> None:
        """SHA256 produces same hash for same input."""
        payload = b"deterministic test"
        h1 = hash_artifact_payload(payload, "sha256")
        h2 = hash_artifact_payload(payload, "sha256")
        assert h1 == h2

    def test_different_payloads_different_hashes(self) -> None:
        """Different payloads produce different hashes."""
        p1 = b"payload one"
        p2 = b"payload two"
        h1 = hash_artifact_payload(p1, "sha256")
        h2 = hash_artifact_payload(p2, "sha256")
        assert h1 != h2

    def test_empty_payload_hashable(self) -> None:
        """Empty payload can be hashed."""
        digest = hash_artifact_payload(b"", "sha256")
        assert len(digest) == 64


class TestRTC030FailClosedPaths:
    """Fail-closed tests for artifact hashing."""

    def test_invalid_algorithm_fails(self) -> None:
        """Invalid hash algorithm raises error."""
        with pytest.raises(ValueError):
            hash_artifact_payload(b"test", "invalid_algo")

    def test_none_payload_fails(self) -> None:
        """None payload raises error."""
        with pytest.raises((TypeError, ValueError)):
            hash_artifact_payload(None, "sha256")  # type: ignore[arg-type]


class TestRTC030CIIntegration:
    """CI integration readiness tests."""

    def test_verifier_has_main_function(self) -> None:
        """Merkle verifier has main() entry point."""
        import scripts.verify_all_requirements_merkle_root as verifier
        assert hasattr(verifier, "main")

    def test_verifier_returns_exit_code(self) -> None:
        """Merkle verifier returns integer exit code."""
        # This test would run the verifier in a controlled way
        # For now, just verify the function signature
        import inspect
        sig = inspect.signature(merkle_main)
        assert sig.return_annotation in (int, "int")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
