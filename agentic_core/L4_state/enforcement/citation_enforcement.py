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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

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
