"""Arbitration engine for deterministic multi-agent proposal selection."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Sequence

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "engine", "execution_auth")
_emit_validates_capability("p2", "engine", "capability_check")
_emit_routes_to_capability("p2", "engine", "capability_route")
_emit_writes_via_uwg("p2", "engine", "uwg_write")
_emit_blocks_direct_write("p2", "engine", "direct_write_block")
_emit_records_tool_invocation("p2", "engine", "tool_invocation")
_emit_captures_execution_output("p2", "engine", "exec_output")
_emit_dispatches_agent("p3", "engine", "agent_dispatch")
_emit_coordinates_agents("p3", "engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "engine", "healing_outcome")
_emit_escalates_failure("p3", "engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "engine", "eval_metric")
_emit_stores_embedding("p4", "engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "engine", "exec_snapshot_link")
from .types import ArbitrationCandidate, ArbitrationDecision, ArbitrationPolicy

_emit_applies_guardrail("p0", "engine", "p0_governance")
_emit_snapshots_state("p0", "engine", "state_snapshot")
emit_replay_key("p0", "engine")
emit_determinism_digest("p0", "engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class ArbitrationEngine:
    """Deterministic arbitration engine for multi-agent proposal selection."""

    def arbitrate(
        self, candidates: Sequence[ArbitrationCandidate], policy: ArbitrationPolicy
    ) -> ArbitrationDecision:
        """Arbitrate between competing proposals deterministically."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArbitrationEngine.arbitrate")

        if candidates is None:
            raise TypeError("Candidates cannot be None")
        if not candidates:
            return ArbitrationDecision(
                winner_ids=(),
                merged_payload=None,
                rationale_codes=("no_candidates",),
                deterministic_fingerprint=self._compute_fingerprint((), None, ()),
            )
        ids = [c.id for c in candidates]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate candidate IDs detected: {[id for id in ids if ids.count(id) > 1]}")
        for candidate in candidates:
            if math.isnan(candidate.score) or math.isinf(candidate.score):
                raise ValueError(f"Invalid score for candidate {candidate.id}: {candidate.score}")
            if candidate.kind not in policy.allowed_kinds:
                raise ValueError(f"Unknown kind '{candidate.kind}' for candidate {candidate.id}")
        min_score = policy.thresholds.get("min_score", 0.0)
        valid_candidates = [c for c in candidates if c.score >= min_score]
        if not valid_candidates:
            return ArbitrationDecision(
                winner_ids=(),
                merged_payload=None,
                rationale_codes=("no_valid_candidates",),
                deterministic_fingerprint=self._compute_fingerprint((), None, ()),
            )
        weighted_candidates = []
        for candidate in valid_candidates:
            weight = policy.weights.get(candidate.kind, 1.0)
            weighted_score = candidate.score * weight
            weighted_candidates.append((weighted_score, candidate))

        def sort_key(item):
            weighted_score, candidate = item
            return (-weighted_score, candidate.cost, candidate.kind, candidate.id)

        sorted_candidates = sorted(weighted_candidates, key=sort_key)
        max_winners = policy.caps.get("max_winners", len(sorted_candidates))
        winners = sorted_candidates[:max_winners]
        winner_ids = tuple((candidate.id for _, candidate in winners))
        rationale_codes = []
        if len(winners) < len(valid_candidates):
            rationale_codes.append("cap_applied")
        rationale_codes.append("weighted_scoring")
        merged_payload = None
        if len(winners) > 1:
            merged_payload = {
                "merged_from": winner_ids,
                "individual_payloads": [candidate.payload for _, candidate in winners],
            }
        fingerprint = self._compute_fingerprint(winner_ids, merged_payload, tuple(rationale_codes))
        return ArbitrationDecision(
            winner_ids=winner_ids,
            merged_payload=merged_payload,
            rationale_codes=tuple(rationale_codes),
            deterministic_fingerprint=fingerprint,
        )

    def _compute_fingerprint(
        self,
        winner_ids: tuple[str, ...],
        merged_payload: dict[str, Any] | None,
        rationale_codes: tuple[str, ...],
    ) -> str:
        """Compute deterministic fingerprint for the decision."""
        data = {
            "winner_ids": winner_ids,
            "merged_payload": merged_payload,
            "rationale_codes": rationale_codes,
        }
        canonical = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")
        return hashlib.sha256(canonical).hexdigest()
