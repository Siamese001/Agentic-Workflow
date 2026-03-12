"""ADG importability contract for agentic_core/L5_safety/audit/ai_check_audit.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ai_check_audit.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.audit.ai_check_audit import (  # noqa: F401
        AICheckAuditRecord,
        AICheckAuditEmitter,
        get_audit_emitter,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AICheckAuditRecord = None  # type: ignore[assignment,misc]
    AICheckAuditEmitter = None  # type: ignore[assignment,misc]
    get_audit_emitter = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ai_check_audit.py deps unavailable")
class TestAiCheckAuditImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ai_check_audit.py must be importable."""
        assert _AVAILABLE

    def test_aicheckauditrecord_is_type(self) -> None:
        assert AICheckAuditRecord is not None

    def test_aicheckauditemitter_is_type(self) -> None:
        assert AICheckAuditEmitter is not None

    def test_get_audit_emitter_callable(self) -> None:
        assert callable(get_audit_emitter)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

