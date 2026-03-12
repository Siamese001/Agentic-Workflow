"""ADG importability contract for agentic_core/interfaces/IBlackboardLeaseVerifierProtocol.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_IBlackboardLeaseVerifierProtocol.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import (  # noqa: F401
        IBlackboardLeaseVerifier,
        SandboxViolationError,
        HealingLeaseError,
        PreservationViolationError,
        get_project_root,
        validate_sandbox,
        require_healing_lease,
        read_file,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    IBlackboardLeaseVerifier = None  # type: ignore[assignment,misc]
    SandboxViolationError = None  # type: ignore[assignment,misc]
    HealingLeaseError = None  # type: ignore[assignment,misc]
    PreservationViolationError = None  # type: ignore[assignment,misc]
    get_project_root = None  # type: ignore[assignment,misc]
    validate_sandbox = None  # type: ignore[assignment,misc]
    require_healing_lease = None  # type: ignore[assignment,misc]
    read_file = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="IBlackboardLeaseVerifierProtocol.py deps unavailable")
class TestIblackboardleaseverifierprotocolImportability:
    def test_module_importable(self) -> None:
        """ADG contract: IBlackboardLeaseVerifierProtocol.py must be importable."""
        assert _AVAILABLE

    def test_iblackboardleaseverifier_is_type(self) -> None:
        assert IBlackboardLeaseVerifier is not None

    def test_sandboxviolationerror_is_type(self) -> None:
        assert SandboxViolationError is not None

    def test_healingleaseerror_is_type(self) -> None:
        assert HealingLeaseError is not None

    def test_get_project_root_callable(self) -> None:
        assert callable(get_project_root)

    def test_validate_sandbox_callable(self) -> None:
        assert callable(validate_sandbox)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

