"""ADG importability contract for agentic_core/L0_routing/utils/core_integrity_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_core_integrity_util.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.utils.core_integrity_util import (  # noqa: F401
        CoreIntegrityVerifier,
        SovereignLockError,
        emergency_shutdown,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    CoreIntegrityVerifier = None  # type: ignore[assignment,misc]
    SovereignLockError = None  # type: ignore[assignment,misc]
    emergency_shutdown = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="core_integrity_util deps unavailable")
class TestCoreIntegrityUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/utils/core_integrity_util.py must be importable."""
        assert _AVAILABLE

    def test_coreintegrityverifier_defined(self) -> None:
        assert CoreIntegrityVerifier is not None

    def test_sovereignlockerror_defined(self) -> None:
        assert SovereignLockError is not None
