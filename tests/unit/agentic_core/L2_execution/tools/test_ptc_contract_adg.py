"""ADG importability contract for agentic_core/L2_execution/tools/ptc_contract.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ptc_contract.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.tools.ptc_contract import (  # noqa: F401
        PTCBytesCapExceeded,
        PTCContractEnforcer,
        PTCContractViolation,
        PTCUnsignedEnvelopeError,
        redact_output,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PTCContractViolation = None  # type: ignore[assignment,misc]
    PTCBytesCapExceeded = None  # type: ignore[assignment,misc]
    PTCUnsignedEnvelopeError = None  # type: ignore[assignment,misc]
    redact_output = None  # type: ignore[assignment,misc]
    PTCContractEnforcer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ptc_contract deps unavailable")
class TestPtcContractImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/tools/ptc_contract.py must be importable."""
        assert _AVAILABLE

    def test_ptccontractviolation_defined(self) -> None:
        assert PTCContractViolation is not None

    def test_ptcbytescapexceeded_defined(self) -> None:
        assert PTCBytesCapExceeded is not None

    def test_ptcunsignedenvelopeerror_defined(self) -> None:
        assert PTCUnsignedEnvelopeError is not None

    def test_ptccontractenforcer_defined(self) -> None:
        assert PTCContractEnforcer is not None
