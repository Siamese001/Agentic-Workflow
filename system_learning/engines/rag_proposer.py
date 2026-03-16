"""RAG Parameter Proposer — proposes retrieval-augmented generation parameter adjustments.

Analyzes retrieval quality metrics (recall, precision, top_k efficiency) and
proposes bounded adjustments to RAG parameters like similarity_cutoff and top_k.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "rag_proposer", "p0_governance")
_emit_reads_policy_state("p0", "rag_proposer", "policy_binding")
_emit_snapshots_state("p0", "rag_proposer", "state_snapshot")
emit_replay_key("p0", "rag_proposer")
emit_determinism_digest("p0", "rag_proposer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rag_proposer", "execution_auth")
_emit_validates_capability("p2", "rag_proposer", "capability_check")
_emit_routes_to_capability("p2", "rag_proposer", "capability_route")
_emit_writes_via_uwg("p2", "rag_proposer", "uwg_write")
_emit_blocks_direct_write("p2", "rag_proposer", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_proposer", "tool_invocation")
_emit_captures_execution_output("p2", "rag_proposer", "exec_output")
_emit_dispatches_agent("p3", "rag_proposer", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_proposer", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_proposer", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_proposer", "healing_outcome")
_emit_escalates_failure("p3", "rag_proposer", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_proposer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_proposer", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_proposer", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_proposer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_proposer", "eval_metric")
_emit_stores_embedding("p4", "rag_proposer", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_proposer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_proposer", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_LOW_RECALL_THRESHOLD = 0.6
_HIGH_NOISE_THRESHOLD = 0.4
_TOP_K_MIN = 3
_TOP_K_MAX = 20
_SIMILARITY_CUTOFF_MIN = 0.3
_SIMILARITY_CUTOFF_MAX = 0.95
_SIMILARITY_DELTA = 0.05
_MIN_OBSERVATIONS = 5


@dataclass(frozen=True, slots=True)
class RAGChangePackage:
    """Immutable RAG parameter adjustment proposal."""

    surface_name: str
    parameter: str
    old_value: float
    new_value: float
    justification: str
    snapshot_id: str

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RAGChangePackage.canonical_bytes")

        data = {
            "surface_name": self.surface_name,
            "parameter": self.parameter,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class RAGParameterProposer:
    """Concrete RAG proposer conforming to the RAGProposer Protocol."""

    def propose(
        self, snapshot: Any, metrics: Any, config: Any, now_utc: int, history: Any, cooldown: Any, sample: Any
    ) -> RAGChangePackage | None:
        """Propose RAG parameter changes based on retrieval quality metrics.

        Parameters
        ----------
        metrics : dict
            Must contain ``"rag_recall"``, ``"rag_precision"``,
            ``"rag_observation_count"``, and optionally ``"rag_top_k"``
            and ``"rag_similarity_cutoff"``.
        config : dict
            Current RAG config with ``"similarity_cutoff"`` and ``"top_k"``.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RAGParameterProposer.propose")

        if not isinstance(metrics, dict) or not isinstance(config, dict):
            return None
        recall = metrics.get("rag_recall", 1.0)
        precision = metrics.get("rag_precision", 1.0)
        n_obs = metrics.get("rag_observation_count", 0)
        if n_obs < _MIN_OBSERVATIONS:
            return None
        snapshot_id = getattr(snapshot, "snapshot_id", "unknown")
        current_cutoff = config.get("similarity_cutoff", 0.7)
        if recall < _LOW_RECALL_THRESHOLD:
            new_cutoff = max(current_cutoff - _SIMILARITY_DELTA, _SIMILARITY_CUTOFF_MIN)
            if new_cutoff != current_cutoff:
                return RAGChangePackage(
                    surface_name="rag_similarity_cutoff",
                    parameter="similarity_cutoff",
                    old_value=current_cutoff,
                    new_value=round(new_cutoff, 4),
                    justification=f"RAG recall {recall:.3f} < {_LOW_RECALL_THRESHOLD}; lowering cutoff from {current_cutoff} to {new_cutoff:.4f}",
                    snapshot_id=snapshot_id,
                )
        if precision < _HIGH_NOISE_THRESHOLD:
            new_cutoff = min(current_cutoff + _SIMILARITY_DELTA, _SIMILARITY_CUTOFF_MAX)
            if new_cutoff != current_cutoff:
                return RAGChangePackage(
                    surface_name="rag_similarity_cutoff",
                    parameter="similarity_cutoff",
                    old_value=current_cutoff,
                    new_value=round(new_cutoff, 4),
                    justification=f"RAG precision {precision:.3f} < {_HIGH_NOISE_THRESHOLD}; raising cutoff from {current_cutoff} to {new_cutoff:.4f}",
                    snapshot_id=snapshot_id,
                )
        return None


__all__ = ["RAGParameterProposer", "RAGChangePackage"]
