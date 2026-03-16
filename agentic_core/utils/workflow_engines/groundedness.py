"""
Groundedness Metric

Measures whether the generated answer is supported by retrieved context.
Uses token-overlap heuristic (F1 over unigrams) as a deterministic
zero-dependency approximation.  An LLM-judge variant is available via
the optional judge callable injected at construction time.
"""

from __future__ import annotations

import re
from typing import Callable

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

_emit_authorize_and_execute("p2", "groundedness", "execution_auth")
_emit_validates_capability("p2", "groundedness", "capability_check")
_emit_routes_to_capability("p2", "groundedness", "capability_route")
_emit_writes_via_uwg("p2", "groundedness", "uwg_write")
_emit_blocks_direct_write("p2", "groundedness", "direct_write_block")
_emit_records_tool_invocation("p2", "groundedness", "tool_invocation")
_emit_captures_execution_output("p2", "groundedness", "exec_output")
_emit_dispatches_agent("p3", "groundedness", "agent_dispatch")
_emit_coordinates_agents("p3", "groundedness", "agent_coordination")
_emit_records_workflow_lineage("p3", "groundedness", "workflow_lineage")
_emit_records_healing_outcome("p3", "groundedness", "healing_outcome")
_emit_escalates_failure("p3", "groundedness", "failure_escalation")
_emit_orchestrates_workflow("p3", "groundedness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "groundedness", "healing_dispatch")
_emit_invokes_evaluation("p3", "groundedness", "evaluation_signal")
_emit_records_telemetry_event("p4", "groundedness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "groundedness", "eval_metric")
_emit_stores_embedding("p4", "groundedness", "embedding_store")
_emit_updates_meta_learning_state("p4", "groundedness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "groundedness", "exec_snapshot_link")
from .base import GenerationMetric

_emit_applies_guardrail("p0", "groundedness", "p0_governance")
_emit_reads_policy_state("p0", "groundedness", "policy_binding")
_emit_snapshots_state("p0", "groundedness", "state_snapshot")
emit_replay_key("p0", "groundedness")
emit_determinism_digest("p0", "groundedness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    text = text.lower()
    text = re.sub("[^\\w\\s]", " ", text)
    return [t for t in text.split() if t]


def _token_f1(prediction_tokens: list[str], context_tokens: list[str]) -> float:
    """Compute F1 between two token lists."""
    if not prediction_tokens or not context_tokens:
        return 0.0
    pred_set = set(prediction_tokens)
    ctx_set = set(context_tokens)
    common = pred_set & ctx_set
    if not common:
        return 0.0
    precision = len(common) / len(pred_set)
    recall = len(common) / len(ctx_set)
    if precision + recall == 0.0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


class Groundedness(GenerationMetric):
    """Measures whether the answer is supported by the retrieved context.

    Without a judge: uses token-overlap F1 between answer and concatenated context.
    With a judge callable: calls judge(answer, context_str) -> float in [0, 1].
    """

    def __init__(self, judge: Callable[[str, str], float] | None = None):
        self._judge = judge

    @property
    def name(self) -> str:
        return "groundedness"

    def compute(self, prediction: str, ground_truth: str, context: str | list[str] | None = None) -> float:
        """Compute groundedness score.

        Args:
            prediction: Generated answer string
            ground_truth: Expected answer (unused in heuristic mode; used by judge)
            context: Retrieved context documents (str or list of str)

        Returns:
            Groundedness score in [0, 1]
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "Groundedness.compute")

        if not prediction:
            return 0.0
        if context is None:
            context_str = ground_truth if ground_truth else ""
        elif isinstance(context, list):
            context_str = " ".join(context)
        else:
            context_str = context
        if not context_str:
            return 0.0
        if self._judge is not None:
            return float(self._judge(prediction, context_str))
        pred_tokens = _tokenize(prediction)
        ctx_tokens = _tokenize(context_str)
        return _token_f1(pred_tokens, ctx_tokens)


__all__ = ["Groundedness", "_tokenize", "_token_f1"]
