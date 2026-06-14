"""Unit tests for agentic_core.L5_safety.contracts.verify.

W2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 L5 safety chokepoint (x2.0).
``verify`` (fan_in=15) supplies ``verify_certification_ref`` — the fail-closed guard
every emit contract's __post_init__ calls. Structural validity only (non-empty str).
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.contracts.verify import verify_certification_ref


class TestVerifyCertificationRef:
    @pytest.mark.parametrize("ref", ["cert-1", "x", "  padded-ok  ", "sha256:abc"])
    def test_non_empty_string_is_valid(self, ref: str) -> None:
        assert verify_certification_ref(ref) is True

    @pytest.mark.parametrize("ref", ["", "   ", "\t", "\n"])
    def test_blank_is_invalid(self, ref: str) -> None:
        assert verify_certification_ref(ref) is False

    @pytest.mark.parametrize("ref", [None, 0, 123, [], {}, object()])
    def test_non_string_is_invalid(self, ref: object) -> None:
        assert verify_certification_ref(ref) is False  # type: ignore[arg-type]
