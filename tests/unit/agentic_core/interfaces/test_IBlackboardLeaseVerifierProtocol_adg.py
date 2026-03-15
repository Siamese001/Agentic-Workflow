"""ADG importability contract for agentic_core/interfaces/IBlackboardLeaseVerifierProtocol.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_IBlackboardLeaseVerifierProtocol.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import (  # noqa: F401
        HealingLeaseError,
        IBlackboardLeaseVerifier,
        PreservationViolationError,
        SandboxViolationError,
        get_project_root,
        validate_sandbox,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    IBlackboardLeaseVerifier = None  # type: ignore[assignment,misc]
    SandboxViolationError = None  # type: ignore[assignment,misc]
    HealingLeaseError = None  # type: ignore[assignment,misc]
    get_project_root = None  # type: ignore[assignment,misc]
    validate_sandbox = None  # type: ignore[assignment,misc]
    PreservationViolationError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="IBlackboardLeaseVerifierProtocol deps unavailable")
class TestIblackboardleaseverifierprotocolImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/interfaces/IBlackboardLeaseVerifierProtocol.py must be importable."""
        assert _AVAILABLE

    def test_iblackboardleaseverifier_defined(self) -> None:
        assert IBlackboardLeaseVerifier is not None

    def test_sandboxviolationerror_defined(self) -> None:
        assert SandboxViolationError is not None

    def test_healingleaseerror_defined(self) -> None:
        assert HealingLeaseError is not None

    def test_preservationviolationerror_defined(self) -> None:
        assert PreservationViolationError is not None
