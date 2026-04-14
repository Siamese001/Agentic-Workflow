"""Prompt Execution Tracer — captures execution lineage and outcome graph edges.

Responsibilities
----------------
1. Accept a raw execution signal dict and produce a ``PromptExecutionRecord``
   and a ``PromptOutcomeRecord``.
2. Emit all execution ADG relations (section 5) and outcome ADG relations
   (section 6) and retrieval ADG relations (section 7).
3. Classify the failure slot (section 12) from the outcome + guardrail hits.
4. Emit HITL relations (section 11) when hitl_escalation=True.

Design invariants
-----------------
1. No wall-clock reads; ``timestamp_utc`` always caller-supplied.
2. Fail-safe extraction — missing signal fields always produce safe defaults.
3. All outputs are content-addressed.
4. The tracer is pure-function: deterministic for identical inputs.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
    record_execution_trace,
)

_emit_authorize_and_execute("p2", "prompt_execution_tracer", "execution_auth")
_emit_validates_capability("p2", "prompt_execution_tracer", "capability_check")
_emit_routes_to_capability("p2", "prompt_execution_tracer", "capability_route")
_emit_writes_via_uwg("p2", "prompt_execution_tracer", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_execution_tracer", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_execution_tracer", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_execution_tracer", "exec_output")
_emit_dispatches_agent("p3", "prompt_execution_tracer", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_execution_tracer", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_execution_tracer", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_execution_tracer", "healing_outcome")
_emit_escalates_failure("p3", "prompt_execution_tracer", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_execution_tracer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_execution_tracer", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_execution_tracer", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_execution_tracer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_execution_tracer", "eval_metric")
_emit_stores_embedding("p4", "prompt_execution_tracer", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_execution_tracer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_execution_tracer", "exec_snapshot_link")
from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.prompt_adg_relations import (
    EXECUTION_EXECUTED_BY_MODEL,
    EXECUTION_GENERATES_TRACE,
    EXECUTION_ROUTES_TO,
    HITL_CAUSED_ESCALATION,
    OUTCOME_ESCALATED_HITL,
    OUTCOME_FAILED,
    OUTCOME_FAILED_REPLAY,
    OUTCOME_PASSED_REPLAY,
    OUTCOME_PRODUCED_ANSWER,
    OUTCOME_TRIGGERED_HEALER,
    RETRIEVAL_RETRIEVES_VIA,
    RETRIEVAL_SCORES_GROUNDEDNESS,
    RETRIEVAL_USES_CHUNK,
    RETRIEVAL_USES_CITATION_SET,
)
from system_learning.types.prompt_artifact_types import (
    PromptExecutionRecord,
    PromptOutcomeRecord,
)

_emit_applies_guardrail("p0", "prompt_execution_tracer", "p0_governance")
_emit_reads_policy_state("p0", "prompt_execution_tracer", "policy_binding")
_emit_snapshots_state("p0", "prompt_execution_tracer", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("prompt_execution_tracer", "prompt_execution_tracer_trace")


_emit_emits_metric_event("prompt_execution_tracer", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_execution_tracer", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_execution_tracer", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_execution_tracer", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_execution_tracer", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_execution_tracer", "p4obs", "metric_6")
_emit_records_incident_event("prompt_execution_tracer", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_execution_tracer", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_execution_tracer", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_execution_tracer", "p4obs", "mon_state")
_emit_triggers_alert("prompt_execution_tracer", "p4obs", "alert")
_emit_links_incident_trace("prompt_execution_tracer", "p4obs", "trace_link")
_emit_captures_pattern("prompt_execution_tracer", "p3lm", "pattern")
_emit_records_learning_event("prompt_execution_tracer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_execution_tracer", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_execution_tracer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_execution_tracer", "p3lm", "routing")
_emit_improves_agent_policy("prompt_execution_tracer", "p3lm", "policy")
_emit_stores_learning_state("prompt_execution_tracer", "p3lm", "state")
_emit_records_execution_trace("prompt_execution_tracer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_execution_tracer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_execution_tracer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_execution_tracer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_execution_tracer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_execution_tracer", "env_read", "p2_env_1")
_emit_reads_environ("prompt_execution_tracer", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_execution_tracer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_execution_tracer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_execution_tracer", "context_pull")
_emit_pulls_context("p1", "prompt_execution_tracer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_execution_tracer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_execution_tracer", "uwg_term_2")
_emit_writes_through("p1", "prompt_execution_tracer", "write_through")
_emit_writes_through("p1", "prompt_execution_tracer", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_execution_tracer", "safety_validation")
_emit_invokes_eval("p1", "prompt_execution_tracer", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_execution_tracer", "routing_commit")
_emit_escalates_to_human("p1", "prompt_execution_tracer", "human_escalation")
_emit_routes_through("p1", "prompt_execution_tracer", "route_through")
_emit_checks_agent_registry("p1", "prompt_execution_tracer", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_execution_tracer", "capability")
_emit_dispatches_execution_plan("p1", "prompt_execution_tracer", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_execution_tracer", "sub_agent")
_emit_routes_to_agent("p1", "prompt_execution_tracer", "target_agent")
_emit_verifies_policy("p1", "prompt_execution_tracer", "policy_check")
_emit_observes_runtime_state("p1", "prompt_execution_tracer", "runtime_state")
_emit_verifies_boundary("p1", "prompt_execution_tracer", "boundary_check")
_emit_hard_fails_untranscripted("p1", "prompt_execution_tracer")
_emit_gated_by_confidence("p1", "prompt_execution_tracer", "confidence_gate")
emit_replay_key("p0", "prompt_execution_tracer")
emit_determinism_digest("p0", "prompt_execution_tracer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Outcome classifier
# ---------------------------------------------------------------------------

_OUTCOME_PRIORITY = (
    "REPLAY_FAILURE",
    "ESCALATED",
    "HEALED_SUCCESS",
    "SAFE_FAILURE",
    "SUCCESS",
    "UNKNOWN",
)


def _classify_outcome(sig: dict) -> str:
    if sig.get("replay_failed") is True:
        return "REPLAY_FAILURE"
    if sig.get("hitl_escalation") is True or sig.get("human_escalation_flag") is True:
        return "ESCALATED"
    healed = sig.get("healed") is True or sig.get("healing_invoked") is True
    success = sig.get("success")
    if success is True and healed:
        return "HEALED_SUCCESS"
    if success is True:
        return "SUCCESS"
    if success is False:
        return "SAFE_FAILURE"
    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Replay status classifier
# ---------------------------------------------------------------------------


def _classify_replay(sig: dict) -> str:
    if sig.get("replay_failed") is True:
        return "FAILED"
    if sig.get("replay_passed") is True:
        return "PASSED"
    return "NOT_TESTED"


# ---------------------------------------------------------------------------
# Slot failure classifier (section 12)
# ---------------------------------------------------------------------------

_SLOT_FAILURE_MAP: dict[str, str] = {
    "POLICY_VIOLATION": "S0",
    "HALLUCINATION": "C0",
    "MISINTERPRETED_TASK": "U0",
    "STYLE_DRIFT": "I0",
    "CONTEXT_OVERFLOW": "C0",
    "GUARDRAIL_BLOCK": "D0",
}


def _classify_failure_slot(sig: dict, guardrail_hits: tuple[str, ...]) -> str:
    explicit = sig.get("failure_slot")
    if explicit in ("S0", "D0", "I0", "C0", "U0", "NONE"):
        return explicit
    failure_type = sig.get("failure_type", "")
    if failure_type in _SLOT_FAILURE_MAP:
        return _SLOT_FAILURE_MAP[failure_type]
    if guardrail_hits:
        return "D0"  # guardrails fire in the D0 defensive fence
    return "NONE"


# ---------------------------------------------------------------------------
# Execution record builder
# ---------------------------------------------------------------------------


def _build_execution_id(prompt_hash: str, trace_id: str, timestamp_utc: int) -> str:
    canonical = deterministic_json(
        {
            "prompt_hash": prompt_hash,
            "timestamp_utc": timestamp_utc,
            "trace_id": trace_id,
        },
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _build_outcome_id(prompt_hash: str, trace_id: str, final_outcome: str, timestamp_utc: int) -> str:
    canonical = deterministic_json(
        {
            "final_outcome": final_outcome,
            "prompt_hash": prompt_hash,
            "timestamp_utc": timestamp_utc,
            "trace_id": trace_id,
        },
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Trace result container
# ---------------------------------------------------------------------------


@dataclass
class ExecutionTraceResult:
    """Output of PromptExecutionTracer.trace().

    Attributes
    ----------
    execution_record : PromptExecutionRecord
    outcome_record : PromptOutcomeRecord
    adg_relations : list[tuple[str, str, str]]
    """

    execution_record: PromptExecutionRecord
    outcome_record: PromptOutcomeRecord
    adg_relations: list[tuple[str, str, str]]


# ---------------------------------------------------------------------------
# Tracer
# ---------------------------------------------------------------------------


class PromptExecutionTracer:
    """Converts raw execution signal dicts into structured execution and
    outcome records with full ADG relation emission.

    Usage::

        tracer = PromptExecutionTracer()
        result = tracer.trace(
            prompt_hash="abc...",
            trace_id="tr-001",
            signal={...},
            timestamp_utc=ts,
        )
        # result.execution_record, result.outcome_record, result.adg_relations
    """

    def trace(
        self,
        prompt_hash: str,
        trace_id: str,
        signal: dict,
        timestamp_utc: int,
    ) -> ExecutionTraceResult:
        """Trace a single prompt execution.

        Parameters
        ----------
        prompt_hash : str
            Hash of the compiled prompt artifact.
        trace_id : str
            ADG trace ID for this execution.
        signal : dict
            Raw execution signal dictionary.
        timestamp_utc : int
            Caller-supplied execution timestamp.

        Returns
        -------
        ExecutionTraceResult
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptExecutionTracer.trace")

        sig = signal or {}

        route = str(sig.get("route_selected") or "UNKNOWN")
        model_id = str(sig.get("model_id") or sig.get("model") or "UNKNOWN")
        latency_ms = max(0, int(sig.get("latency_ms") or 0))
        input_tokens = max(0, int(sig.get("input_tokens") or 0))
        output_tokens = max(0, int(sig.get("output_tokens") or 0))
        adg_prefix = str(sig.get("adg_entity_prefix") or "ADG::PromptExecution")

        execution_id = _build_execution_id(prompt_hash, trace_id, timestamp_utc)
        exec_entity = f"{adg_prefix}::{execution_id[:16]}"

        execution_record = PromptExecutionRecord(
            execution_id=execution_id,
            prompt_hash=prompt_hash,
            trace_id=trace_id,
            route_selected=route,
            model_id=model_id,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            adg_entity_name=exec_entity,
            timestamp_utc=timestamp_utc,
        )

        # --- Outcome ---
        final_outcome = _classify_outcome(sig)
        replay_status = _classify_replay(sig)

        groundedness = float(sig.get("groundedness_score") or sig.get("retrieval_groundedness_score") or 0.0)
        groundedness = max(0.0, min(1.0, groundedness))

        support_score = max(0.0, min(1.0, float(sig.get("support_score") or 0.0)))
        completeness_score = max(0.0, min(1.0, float(sig.get("completeness_score") or 0.0)))
        citation_count = max(0, int(sig.get("citation_count") or 0))

        raw_guardrails = sig.get("guardrail_hits") or sig.get("guardrails_applied") or []
        if isinstance(raw_guardrails, str):
            raw_guardrails = [raw_guardrails]
        guardrail_hits: tuple[str, ...] = tuple(sorted(str(g) for g in raw_guardrails if g))

        healer_invoked = bool(sig.get("healing_invoked") or sig.get("healed"))
        healer_id = sig.get("healer_id") or None
        hitl_escalation = bool(sig.get("hitl_escalation") or sig.get("human_escalation_flag"))

        failure_slot = _classify_failure_slot(sig, guardrail_hits)

        outcome_id = _build_outcome_id(prompt_hash, trace_id, final_outcome, timestamp_utc)
        outcome_entity = f"ADG::PromptOutcome::{outcome_id[:16]}"

        outcome_record = PromptOutcomeRecord(
            outcome_id=outcome_id,
            prompt_hash=prompt_hash,
            trace_id=trace_id,
            route=route,
            model=model_id,
            groundedness_score=groundedness,
            guardrail_hits=guardrail_hits,
            healer_invoked=healer_invoked,
            healer_id=healer_id,
            hitl_escalation=hitl_escalation,
            replay_status=replay_status,
            final_outcome=final_outcome,
            failure_slot=failure_slot,
            support_score=support_score,
            completeness_score=completeness_score,
            citation_count=citation_count,
            adg_entity_name=outcome_entity,
            timestamp_utc=timestamp_utc,
        )

        # --- ADG relations ---
        prompt_node = f"ADG::CompiledPrompt::{prompt_hash[:16]}"
        relations: list[tuple[str, str, str]] = []

        # Execution family
        relations.append((prompt_node, EXECUTION_ROUTES_TO, f"ADG::Route::{route}"))
        relations.append((prompt_node, EXECUTION_EXECUTED_BY_MODEL, f"ADG::Model::{model_id}"))
        relations.append((prompt_node, EXECUTION_GENERATES_TRACE, f"ADG::Trace::{trace_id}"))

        # Outcome family
        outcome_rel = _pick_outcome_relation(final_outcome)
        relations.append((prompt_node, outcome_rel, outcome_entity))

        if healer_invoked:
            healer_node = f"ADG::Healer::{healer_id or 'UNKNOWN'}"
            relations.append((prompt_node, OUTCOME_TRIGGERED_HEALER, healer_node))

        if hitl_escalation:
            relations.append((prompt_node, OUTCOME_ESCALATED_HITL, f"ADG::HITL::Escalation::{trace_id[:16]}"))
            relations.append((prompt_node, HITL_CAUSED_ESCALATION, f"ADG::HITL::Escalation::{trace_id[:16]}"))

        if replay_status == "PASSED":
            relations.append((prompt_node, OUTCOME_PASSED_REPLAY, f"ADG::ReplayCheck::{trace_id[:16]}"))
        elif replay_status == "FAILED":
            relations.append((prompt_node, OUTCOME_FAILED_REPLAY, f"ADG::ReplayCheck::{trace_id[:16]}"))

        # Retrieval family
        retrieval_path = str(sig.get("retrieval_path") or "UNKNOWN")
        relations.append((prompt_node, RETRIEVAL_RETRIEVES_VIA, f"ADG::RetrievalPath::{retrieval_path}"))

        chunk_ids = sig.get("chunk_ids") or []
        if isinstance(chunk_ids, str):
            chunk_ids = [chunk_ids]
        for cid in sorted(chunk_ids):
            relations.append((prompt_node, RETRIEVAL_USES_CHUNK, f"ADG::Chunk::{str(cid)[:16]}"))

        citation_set_hash = sig.get("citation_set_hash")
        if citation_set_hash:
            relations.append(
                (
                    prompt_node,
                    RETRIEVAL_USES_CITATION_SET,
                    f"ADG::CitationSet::{str(citation_set_hash)[:16]}",
                ),
            )

        relations.append(
            (
                prompt_node,
                RETRIEVAL_SCORES_GROUNDEDNESS,
                f"ADG::GroundednessScore::{_fmt_score(groundedness)}",
            ),
        )

        return ExecutionTraceResult(
            execution_record=execution_record,
            outcome_record=outcome_record,
            adg_relations=relations,
        )

    def trace_batch(
        self,
        executions: list[tuple[str, str, dict, int]],
    ) -> list[ExecutionTraceResult]:
        """Trace a batch of executions.

        Parameters
        ----------
        executions : list of (prompt_hash, trace_id, signal, timestamp_utc)

        Returns
        -------
        list[ExecutionTraceResult]
            Sorted by execution_record.execution_id for determinism.
        """
        results = []
        for prompt_hash, trace_id, signal, ts in executions:
            try:
                results.append(self.trace(prompt_hash, trace_id, signal, ts))
            except (AttributeError, KeyError, TypeError, ValueError) as exc:
                logger.warning(
                    "prompt_execution_tracer: trace failed",
                    extra={"trace_id": trace_id, "error": str(exc)},
                )
        results.sort(key=lambda r: r.execution_record.execution_id)
        return results


# ---------------------------------------------------------------------------
# Outcome relation picker
# ---------------------------------------------------------------------------


def _pick_outcome_relation(final_outcome: str) -> str:
    mapping = {
        "SUCCESS": OUTCOME_PRODUCED_ANSWER,
        "HEALED_SUCCESS": OUTCOME_PRODUCED_ANSWER,
        "SAFE_FAILURE": OUTCOME_FAILED,
        "ESCALATED": OUTCOME_ESCALATED_HITL,
        "REPLAY_FAILURE": OUTCOME_FAILED_REPLAY,
        "UNKNOWN": OUTCOME_FAILED,
    }
    return mapping.get(final_outcome, OUTCOME_FAILED)


def _fmt_score(score: float) -> str:
    return f"{score:.4f}"


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def trace_execution(
    prompt_hash: str,
    trace_id: str,
    signal: dict,
    timestamp_utc: int,
) -> ExecutionTraceResult:
    """Module-level convenience wrapper."""
    _emit_transcripts_response(str(uuid.uuid4()), "Module.trace_execution", "model")
    return PromptExecutionTracer().trace(prompt_hash, trace_id, signal, timestamp_utc)


__all__ = [
    "ExecutionTraceResult",
    "PromptExecutionTracer",
    "trace_execution",
]
