"""
Tests for the strict determinism surface (DigestCalculator).

Phase 0.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.determinism.digest_calculator import DigestCalculator

_ZERO = "0" * 64


class TestDigestCalculator:
    def test_returns_64_char_hex(self) -> None:
        digest = DigestCalculator.compute(
            policy_hash=_ZERO,
            registry_hash=_ZERO,
            config_surface_hash=_ZERO,
            transcript_hash=_ZERO,
            dependency_lock_hash=_ZERO,
        )
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_deterministic(self) -> None:
        kwargs = {
            "policy_hash": _ZERO,
            "registry_hash": _ZERO,
            "config_surface_hash": _ZERO,
            "transcript_hash": _ZERO,
            "dependency_lock_hash": _ZERO,
        }
        assert DigestCalculator.compute(**kwargs) == DigestCalculator.compute(**kwargs)

    def test_changes_with_policy_hash(self) -> None:
        different = "a" * 64
        d1 = DigestCalculator.compute(
            policy_hash=_ZERO,
            registry_hash=_ZERO,
            config_surface_hash=_ZERO,
            transcript_hash=_ZERO,
            dependency_lock_hash=_ZERO,
        )
        d2 = DigestCalculator.compute(
            policy_hash=different,
            registry_hash=_ZERO,
            config_surface_hash=_ZERO,
            transcript_hash=_ZERO,
            dependency_lock_hash=_ZERO,
        )
        assert d1 != d2

    def test_changes_with_dependency_lock_hash(self) -> None:
        different = "b" * 64
        d1 = DigestCalculator.compute(
            policy_hash=_ZERO,
            registry_hash=_ZERO,
            config_surface_hash=_ZERO,
            transcript_hash=_ZERO,
            dependency_lock_hash=_ZERO,
        )
        d2 = DigestCalculator.compute(
            policy_hash=_ZERO,
            registry_hash=_ZERO,
            config_surface_hash=_ZERO,
            transcript_hash=_ZERO,
            dependency_lock_hash=different,
        )
        assert d1 != d2

    def test_rejects_non_64_char_hash(self) -> None:
        with pytest.raises(ValueError, match="policy_hash"):
            DigestCalculator.compute(
                policy_hash="short",
                registry_hash=_ZERO,
                config_surface_hash=_ZERO,
                transcript_hash=_ZERO,
                dependency_lock_hash=_ZERO,
            )

    def test_zero_hash_helper(self) -> None:
        zh = DigestCalculator.zero_hash()
        assert len(zh) == 64
        assert zh == _ZERO
