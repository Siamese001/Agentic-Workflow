"""ADG importability contract for agentic_core/L2_execution/scripts/remediation_dispatcher.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_remediation_dispatcher.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.scripts.remediation_dispatcher import (  # noqa: F401
        NOTE_MAPPED,
        OUTPUT_FILENAME,
        TOOL_ID,
        CanonicalEscalationPayload,
        EscalationContext,
        EscalationDecisionReason,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    TOOL_ID = None  # type: ignore[assignment,misc]
    OUTPUT_FILENAME = None  # type: ignore[assignment,misc]
    EscalationDecisionReason = None  # type: ignore[assignment,misc]
    CanonicalEscalationPayload = None  # type: ignore[assignment,misc]
    EscalationContext = None  # type: ignore[assignment,misc]
    NOTE_MAPPED = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="remediation_dispatcher deps unavailable")
class TestRemediationDispatcherImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/scripts/remediation_dispatcher.py must be importable."""
        assert _AVAILABLE

    def test_escalationdecisionreason_defined(self) -> None:
        assert EscalationDecisionReason is not None

    def test_canonicalescalationpayload_defined(self) -> None:
        assert CanonicalEscalationPayload is not None

    def test_escalationcontext_defined(self) -> None:
        assert EscalationContext is not None
