"""
injection_scan_util.py - Canonical injection scan helper.

Thin wrapper around InjectionDetector.scan() to standardize scanning calls
across all prompt joinpoints. Logs source context for audit trail without
logging raw text.
"""

from __future__ import annotations

import logging

from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "injection_scan_util")
_emit_applies_guardrail("p0", "injection_scan_util", "p0_governance")
_emit_reads_policy_state("p0", "injection_scan_util", "policy_binding")
_emit_snapshots_state("p0", "injection_scan_util", "state_snapshot")
emit_replay_key("p0", "injection_scan_util")
emit_determinism_digest("p0", "injection_scan_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)
_detector = InjectionDetector()


def scan_untrusted_text(text: str, *, source: str) -> None:
    """Scan *text* for injection signatures using the canonical detector.

    Args:
        text: The untrusted text to scan.
        source: Audit label describing the origin (e.g. "tool_output",
                "user_input", "full_prompt"). Never logged with raw text.

    Raises:
        SecurityViolationError: If an injection signature is detected.
    """
    if not text:
        return
    Logger.debug("Injection scan invoked: source=%s, length=%d", source, len(text))
    _detector.scan(text)
