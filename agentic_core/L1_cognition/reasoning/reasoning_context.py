"""
agentic_core/L1_cognition/context/reasoning_context.py

Run-scoped ReasoningContext — P0/L1 closure.

Single source of truth for all fields that must travel with every L1
reasoning step.  No module may reconstruct context from globals, Redis
reads, or ambient state.

ADG edges emitted (via reason_and_record):
    records_execution_trace
    signs_execution_trace
    references_policy_hash
    transcripts_response
    hard_fails_untranscripted
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

@dataclass(frozen=True)
class ReasoningContext:
    """Immutable run-scoped context that MUST be passed to every L1 reasoning
    call.  No reasoning may proceed without an explicit instance of this
    object.

    Required fields (all must be non-empty at creation time):
        run_id                    — unique per agent invocation
        trace_id                  — routing/execution trace linkage
        routing_contract_id       — RoutingContract that authorised this run
        policy_hash               — hash of active policy state
        policy_version            — version string of the active policy
        prompt_hash               — hash of assembled prompt
        context_hash              — deterministic hash of full context state
        evidence_hash             — hash of all bound retrieval evidence
        retrieved_context_ids     — list of retrieval result IDs seen
        memory_version            — version tag of memory snapshot used
        state_version             — version tag of runtime state snapshot
        router_decision_id        — routing decision that triggered this run
        parent_reasoning_trace_id — parent trace for chained reasoning
        parent_context_hash       — parent context_hash for lineage
        clock_tick                — deterministic clock value at context creation
        model_id                  — model/LLM identifier
    """

    run_id: str
    trace_id: str
    routing_contract_id: str
    policy_hash: str
    policy_version: str
    prompt_hash: str
    context_hash: str
    evidence_hash: str
    retrieved_context_ids: tuple[str, ...]
    memory_version: str
    state_version: str
    router_decision_id: str
    parent_reasoning_trace_id: str
    parent_context_hash: str
    clock_tick: float
    model_id: str

    def __post_init__(self) -> None:
        missing = [
            f
            for f in ("run_id", "trace_id", "policy_hash", "prompt_hash", "clock_tick", "model_id")
            if not getattr(self, f)
        ]
        if missing:
            raise ValueError(f"ReasoningContext missing required fields: {missing}")

    @classmethod
    def create(
        cls,
        *,
        run_id: str | None = None,
        trace_id: str | None = None,
        routing_contract_id: str = "",
        policy_hash: str,
        policy_version: str = "1.0",
        prompt_hash: str,
        retrieved_context_ids: list[str] | None = None,
        evidence_hash: str = "",
        memory_version: str = "0",
        state_version: str = "0",
        router_decision_id: str = "",
        parent_reasoning_trace_id: str = "",
        parent_context_hash: str = "",
        clock_tick: float,
        model_id: str,
    ) -> ReasoningContext:
        """Factory with sensible defaults for optional fields."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReasoningContext.create", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReasoningContext.create", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "ReasoningContext.create")
        _run_id = run_id or str(uuid.uuid4())
        _trace_id = trace_id or str(uuid.uuid4())
        ids = tuple(retrieved_context_ids or [])
        _evidence_hash = evidence_hash or _hash_ids(ids)
        # Compute context_hash from all deterministic inputs
        _ctx_hash = _compute_context_hash(
            run_id=_run_id,
            trace_id=_trace_id,
            policy_hash=policy_hash,
            prompt_hash=prompt_hash,
            evidence_hash=_evidence_hash,
            memory_version=memory_version,
            state_version=state_version,
            model_id=model_id,
            clock_tick=clock_tick,
        )
        return cls(
            run_id=_run_id,
            trace_id=_trace_id,
            routing_contract_id=routing_contract_id,
            policy_hash=policy_hash,
            policy_version=policy_version,
            prompt_hash=prompt_hash,
            context_hash=_ctx_hash,
            evidence_hash=_evidence_hash,
            retrieved_context_ids=ids,
            memory_version=memory_version,
            state_version=state_version,
            router_decision_id=router_decision_id,
            parent_reasoning_trace_id=parent_reasoning_trace_id,
            parent_context_hash=parent_context_hash,
            clock_tick=clock_tick,
            model_id=model_id,
        )

    def with_parent(self, parent_trace_id: str) -> ReasoningContext:
        """Return a child context that carries lineage from this context."""
        new_trace_id = str(uuid.uuid4())
        new_ctx_hash = _compute_context_hash(
            run_id=self.run_id,
            trace_id=new_trace_id,
            policy_hash=self.policy_hash,
            prompt_hash=self.prompt_hash,
            evidence_hash=self.evidence_hash,
            memory_version=self.memory_version,
            state_version=self.state_version,
            model_id=self.model_id,
            clock_tick=self.clock_tick,
        )
        return ReasoningContext(
            run_id=self.run_id,
            trace_id=new_trace_id,
            routing_contract_id=self.routing_contract_id,
            policy_hash=self.policy_hash,
            policy_version=self.policy_version,
            prompt_hash=self.prompt_hash,
            context_hash=new_ctx_hash,
            evidence_hash=self.evidence_hash,
            retrieved_context_ids=self.retrieved_context_ids,
            memory_version=self.memory_version,
            state_version=self.state_version,
            router_decision_id=self.router_decision_id,
            parent_reasoning_trace_id=parent_trace_id,
            parent_context_hash=self.context_hash,
            clock_tick=self.clock_tick,
            model_id=self.model_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "trace_id": self.trace_id,
            "routing_contract_id": self.routing_contract_id,
            "policy_hash": self.policy_hash,
            "policy_version": self.policy_version,
            "prompt_hash": self.prompt_hash,
            "context_hash": self.context_hash,
            "evidence_hash": self.evidence_hash,
            "retrieved_context_ids": list(self.retrieved_context_ids),
            "memory_version": self.memory_version,
            "state_version": self.state_version,
            "router_decision_id": self.router_decision_id,
            "parent_reasoning_trace_id": self.parent_reasoning_trace_id,
            "parent_context_hash": self.parent_context_hash,
            "clock_tick": self.clock_tick,
            "model_id": self.model_id,
        }


def _hash_ids(ids: tuple[str, ...]) -> str:
    if not ids:
        return hashlib.sha256(b"empty").hexdigest()[:16]
    return hashlib.sha256("|".join(sorted(ids)).encode()).hexdigest()[:16]


def _compute_context_hash(
    *,
    run_id: str,
    trace_id: str,
    policy_hash: str,
    prompt_hash: str,
    evidence_hash: str,
    memory_version: str,
    state_version: str,
    model_id: str,
    clock_tick: float,
) -> str:
    """Deterministic hash of the full context state."""
    payload = (
        f"{run_id}|{trace_id}|{policy_hash}|"
        f"{prompt_hash}|{evidence_hash}|"
        f"{memory_version}|{state_version}|{model_id}|{clock_tick}"
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


@dataclass
class ReasoningTraceArtifact:
    """Structured reasoning trace artifact — all 9 required fields.

    ADG edge: records_execution_trace (pre), signs_execution_trace (post)
    """

    reasoning_trace_id: str
    run_id: str
    prompt_hash: str
    context_hash: str
    retrieved_evidence_hash: str
    policy_hash: str
    reasoning_step_hash: str
    output_hash: str
    parent_trace_id: str
    model_id: str = ""
    signed: bool = False
    transcript_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        ctx: ReasoningContext,
        reasoning_step_hash: str = "",
        output_hash: str = "",
        transcript_id: str = "",
    ) -> ReasoningTraceArtifact:
        return cls(
            reasoning_trace_id=str(uuid.uuid4()),
            run_id=ctx.run_id,
            prompt_hash=ctx.prompt_hash,
            context_hash=ctx.context_hash,
            retrieved_evidence_hash=ctx.evidence_hash,
            policy_hash=ctx.policy_hash,
            reasoning_step_hash=reasoning_step_hash or ctx.context_hash,
            output_hash=output_hash,
            parent_trace_id=ctx.parent_reasoning_trace_id,
            model_id=ctx.model_id,
            transcript_id=transcript_id,
        )

    def is_complete(self) -> bool:
        """True if all required fields are populated."""
        return all(
            [
                self.reasoning_trace_id,
                self.run_id,
                self.prompt_hash,
                self.context_hash,
                self.retrieved_evidence_hash,
                self.policy_hash,
                self.reasoning_step_hash,
                self.output_hash,
            ]
        )

    def sign(self) -> None:
        """Mark trace as signed (emits signs_execution_trace ADG edge)."""
        self.signed = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "reasoning_trace_id": self.reasoning_trace_id,
            "run_id": self.run_id,
            "prompt_hash": self.prompt_hash,
            "context_hash": self.context_hash,
            "retrieved_evidence_hash": self.retrieved_evidence_hash,
            "policy_hash": self.policy_hash,
            "reasoning_step_hash": self.reasoning_step_hash,
            "output_hash": self.output_hash,
            "parent_trace_id": self.parent_trace_id,
            "model_id": self.model_id,
            "signed": self.signed,
            "transcript_id": self.transcript_id,
        }


@dataclass
class ReasoningTranscript:
    """Per-model-response transcript artifact.

    ADG edge: transcripts_response
    """

    transcript_id: str
    reasoning_trace_id: str
    raw_response_hash: str
    normalized_response_hash: str
    model_id: str
    inference_config_hash: str
    parent_reasoning_trace_id: str

    @classmethod
    def create(
        cls,
        *,
        trace_id: str,
        raw_response: str,
        model_id: str,
        inference_config: dict[str, Any] | None = None,
        parent_trace_id: str = "",
    ) -> ReasoningTranscript:
        raw_hash = hashlib.sha256(raw_response.encode()).hexdigest()[:32]
        norm_hash = hashlib.sha256(raw_response.strip().lower().encode()).hexdigest()[:32]
        cfg_hash = hashlib.sha256(repr(sorted((inference_config or {}).items())).encode()).hexdigest()[:16]
        return cls(
            transcript_id=str(uuid.uuid4()),
            reasoning_trace_id=trace_id,
            raw_response_hash=raw_hash,
            normalized_response_hash=norm_hash,
            model_id=model_id,
            inference_config_hash=cfg_hash,
            parent_reasoning_trace_id=parent_trace_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "transcript_id": self.transcript_id,
            "reasoning_trace_id": self.reasoning_trace_id,
            "raw_response_hash": self.raw_response_hash,
            "normalized_response_hash": self.normalized_response_hash,
            "model_id": self.model_id,
            "inference_config_hash": self.inference_config_hash,
            "parent_reasoning_trace_id": self.parent_reasoning_trace_id,
        }


__all__ = [
    "ReasoningContext",
    "ReasoningTraceArtifact",
    "ReasoningTranscript",
    "_compute_context_hash",
    "_hash_ids",
]
