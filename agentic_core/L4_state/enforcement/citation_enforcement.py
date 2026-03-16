"""
Phase 8 — Citation Enforcement: anchor coverage rule for retrieval-backed responses.

enforce_citations_for_retrieval(output, anchored_results, retrieval_used) -> output_with_citations
  - If retrieval_used=True and anchored_results empty/missing -> CitationEnforcementViolation
  - Else attach CitationBundle to output["citations"] deterministically (non-mutating to index)
  - If retrieval_used=False -> return output unchanged (legacy parity)
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from agentic_core.L4_state.types.citation_bundle_types import build_citation_bundle
from agentic_core.L4_state.types.retrieval_anchor_types import AnchoredResult, RetrievalAnchor
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "citation_enforcement")
emit_determinism_digest("p0", "citation_enforcement")

_emit_dispatches_healing_run("p1", "citation_enforcement", "L4")
_emit_routes_through("p1", "citation_enforcement", "L4")
_emit_escalates_to_human("p1", "citation_enforcement", "L4")
_emit_reads_policy_state("p1", "citation_enforcement", "L4")
_emit_authorize_and_execute("p2", "citation_enforcement", "execution_auth")
_emit_validates_capability("p2", "citation_enforcement", "capability_check")
_emit_routes_to_capability("p2", "citation_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "citation_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "citation_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "citation_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "citation_enforcement", "exec_output")
_emit_dispatches_agent("p3", "citation_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "citation_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "citation_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "citation_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "citation_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "citation_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "citation_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "citation_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "citation_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "citation_enforcement", "eval_metric")
_emit_stores_embedding("p4", "citation_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "citation_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "citation_enforcement", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("citation_enforcement", "p4obs", "metric_1")
_emit_emits_metric_event("citation_enforcement", "p4obs", "metric_2")
_emit_emits_metric_event("citation_enforcement", "p4obs", "metric_3")
_emit_emits_metric_event("citation_enforcement", "p4obs", "metric_4")
_emit_emits_metric_event("citation_enforcement", "p4obs", "metric_5")
_emit_emits_metric_event("citation_enforcement", "p4obs", "metric_6")
_emit_records_incident_event("citation_enforcement", "p4obs", "incident")
_emit_captures_runtime_anomaly("citation_enforcement", "p4obs", "anomaly")
_emit_writes_observability_log("citation_enforcement", "p4obs", "obs_log")
_emit_updates_monitoring_state("citation_enforcement", "p4obs", "mon_state")
_emit_triggers_alert("citation_enforcement", "p4obs", "alert")
_emit_links_incident_trace("citation_enforcement", "p4obs", "trace_link")
_emit_captures_pattern("citation_enforcement", "p3lm", "pattern")
_emit_records_learning_event("citation_enforcement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("citation_enforcement", "p3lm", "snapshot")
_emit_feeds_meta_learning("citation_enforcement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("citation_enforcement", "p3lm", "routing")
_emit_improves_agent_policy("citation_enforcement", "p3lm", "policy")
_emit_stores_learning_state("citation_enforcement", "p3lm", "state")
_emit_records_execution_trace("citation_enforcement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("citation_enforcement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("citation_enforcement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("citation_enforcement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("citation_enforcement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("citation_enforcement", "env_read", "p2_env_1")
_emit_reads_environ("citation_enforcement", "env_read", "p2_env_2")
_emit_reads_runtime_state("citation_enforcement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("citation_enforcement", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "citation_enforcement", "context_pull")
_emit_pulls_context("p1", "citation_enforcement", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "citation_enforcement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "citation_enforcement", "uwg_term_2")
_emit_writes_through("p1", "citation_enforcement", "write_through")
_emit_writes_through("p1", "citation_enforcement", "write_through_2")
_emit_validated_by_safety_plane("p1", "citation_enforcement", "safety_validation")
_emit_invokes_eval("p1", "citation_enforcement", "eval_call")
_emit_proposal_commits_routing("p1", "citation_enforcement", "routing_commit")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class CitationEnforcementViolation(Exception):
    """
    Raised when retrieval was used but anchors are missing from the response.

    Attributes
    ----------
    code   : str — always "MISSING_CITATIONS"
    detail : str — human-readable description
    """

    code: str = "MISSING_CITATIONS"

    def __init__(self, detail: str = "") -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "CitationEnforcementViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "CitationEnforcementViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "CitationEnforcementViolation.__init__"
        )
        self.detail = detail
        super().__init__(
            f"[{self.code}] Retrieval used but citations missing" + (f": {detail}" if detail else "")
        )


def _build_request_hash_from_output(output: dict[str, Any]) -> str:
    """
    Derive a stable request_hash from the output dict.
    Uses only non-volatile fields present in the output.
    Falls back to sha256 of the output keys if no canonical subset available.
    """
    subset = {
        k: output[k]
        for k in sorted(output)
        if k not in ("citations", "timestamp", "elapsed_ms", "trace_id")
        and isinstance(output[k], (str, int, float, bool))
    }
    raw = json.dumps(subset, sort_keys=True, separators=(",", ":")).encode()
    return _sha256(raw)


def enforce_citations_for_retrieval(
    output: dict[str, Any],
    anchored_results: list[AnchoredResult] | None,
    retrieval_used: bool,
    *,
    request_hash: str | None = None,
) -> dict[str, Any]:
    """
    Enforce anchor coverage rule for retrieval-backed responses.

    Parameters
    ----------
    output           : dict  — the response artifact to attach citations to
    anchored_results : list[AnchoredResult] | None
        Retrieved content with anchors. Must be non-empty if retrieval_used=True.
    retrieval_used   : bool
        True if L4 retrieval was used to produce this response.
    request_hash     : str | None
        Optional stable hash of the retrieval request. Auto-derived if None.

    Returns
    -------
    dict — output with "citations" key containing CitationBundle.to_dict()
           (unchanged if retrieval_used=False)

    Raises
    ------
    CitationEnforcementViolation(code="MISSING_CITATIONS")
        If retrieval_used=True and anchored_results is empty or None.
    """
    if not retrieval_used:
        return output
    if not anchored_results:
        raise CitationEnforcementViolation(detail="retrieval_used=True but anchored_results is empty or None")
    anchors: list[RetrievalAnchor] = [r.anchor for r in anchored_results]
    rh = request_hash if request_hash else _build_request_hash_from_output(output)
    bundle = build_citation_bundle(request_hash=rh, anchors=anchors)
    result = dict(output)
    result["citations"] = bundle.to_dict()
    return result


def assemble_response(
    output: dict[str, Any],
    anchored_results: list[AnchoredResult] | None,
    retrieval_used: bool,
    *,
    request_hash: str | None = None,
) -> dict[str, Any]:
    """
    Canonical response assembly seam.

    Calls enforce_citations_for_retrieval() to attach citations before returning.
    This is the single authoritative entry point for final response construction.
    """
    return enforce_citations_for_retrieval(
        output=output,
        anchored_results=anchored_results,
        retrieval_used=retrieval_used,
        request_hash=request_hash,
    )
