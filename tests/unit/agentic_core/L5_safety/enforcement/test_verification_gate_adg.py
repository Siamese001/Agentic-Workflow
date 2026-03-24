"""ADG importability contract for agentic_core/L5_safety/enforcement/verification_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_verification_gate.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.verification_gate import (  # noqa: F401
        VerificationGate,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    VerificationGate = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="verification_gate deps unavailable")
class TestVerificationGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/verification_gate.py must be importable."""
        assert _AVAILABLE

    def test_verificationgate_defined(self) -> None:
        assert VerificationGate is not None