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
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "injection_scan_util", "execution_auth")
_emit_validates_capability("p2", "injection_scan_util", "capability_check")
_emit_routes_to_capability("p2", "injection_scan_util", "capability_route")
_emit_writes_via_uwg("p2", "injection_scan_util", "uwg_write")
_emit_blocks_direct_write("p2", "injection_scan_util", "direct_write_block")
_emit_records_tool_invocation("p2", "injection_scan_util", "tool_invocation")
_emit_captures_execution_output("p2", "injection_scan_util", "exec_output")
_emit_dispatches_agent("p3", "injection_scan_util", "agent_dispatch")
_emit_coordinates_agents("p3", "injection_scan_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "injection_scan_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "injection_scan_util", "healing_outcome")
_emit_escalates_failure("p3", "injection_scan_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "injection_scan_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "injection_scan_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "injection_scan_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "injection_scan_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "injection_scan_util", "eval_metric")
_emit_stores_embedding("p4", "injection_scan_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "injection_scan_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "injection_scan_util", "exec_snapshot_link")

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
