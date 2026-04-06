"""Prompt artifact types for ADG-backed prompt provenance and learning.

Defines the immutable data types that represent prompt lifecycle artifacts:

  CompiledPromptArtifact  — the fully-assembled, deterministic prompt sent
                            to a model; a primary ADG node.
  PromptSlotManifest      — breakdown of token counts and hashes per slot
                            (S0, D0, I0, C0, U0).
  PromptSafetyDecision    — result of L5 policy/guardrail/budget evaluation.
  PromptExecutionRecord   — runtime execution data (route, model, latency,
                            tokens, trace linkage).
  PromptOutcomeRecord     — per-execution outcome + slot failure annotation;
                            feeds the meta-learning bus.
  PreferenceRecord        — HITL Path-D feedback for DPO dataset generation.
  PromptDriftSignal       — inter-version drift observation produced by the
                            PromptDriftDetector.

Design invariants
-----------------
1. All types are frozen dataclasses — immutable after construction.
2. No wall-clock reads; ``timestamp_utc`` always caller-supplied.
3. stable_hash() = SHA-256(deterministic_json(to_dict())) for every type.
4. influence_class is always ``"C0_INFORMATIONAL"``; these types MUST NOT
   directly alter routing, safety tier, or config.
5. All tuple fields with set-like semantics are stored sorted to guarantee
   canonical serialization.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
)

_emit_authorize_and_execute("p2", "prompt_artifact_types", "execution_auth")
_emit_validates_capability("p2", "prompt_artifact_types", "capability_check")
_emit_routes_to_capability("p2", "prompt_artifact_types", "capability_route")
_emit_writes_via_uwg("p2", "prompt_artifact_types", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_artifact_types", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_artifact_types", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_artifact_types", "exec_output")
_emit_dispatches_agent("p3", "prompt_artifact_types", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_artifact_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_artifact_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_artifact_types", "healing_outcome")
_emit_escalates_failure("p3", "prompt_artifact_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_artifact_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_artifact_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_artifact_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_artifact_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_artifact_types", "eval_metric")
_emit_stores_embedding("p4", "prompt_artifact_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_artifact_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_artifact_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
from system_learning.enforcement.determinism import deterministic_json

_emit_emits_metric_event("prompt_artifact_types", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_artifact_types", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_artifact_types", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_artifact_types", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_artifact_types", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_artifact_types", "p4obs", "metric_6")
_emit_records_incident_event("prompt_artifact_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_artifact_types", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_artifact_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_artifact_types", "p4obs", "mon_state")
_emit_triggers_alert("prompt_artifact_types", "p4obs", "alert")
_emit_links_incident_trace("prompt_artifact_types", "p4obs", "trace_link")
_emit_captures_pattern("prompt_artifact_types", "p3lm", "pattern")
_emit_records_learning_event("prompt_artifact_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_artifact_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_artifact_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_artifact_types", "p3lm", "routing")
_emit_improves_agent_policy("prompt_artifact_types", "p3lm", "policy")
_emit_stores_learning_state("prompt_artifact_types", "p3lm", "state")
_emit_records_execution_trace("prompt_artifact_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_artifact_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_artifact_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_artifact_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_artifact_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_artifact_types", "env_read", "p2_env_1")
_emit_reads_environ("prompt_artifact_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_artifact_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_artifact_types", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "prompt_artifact_types")
_emit_applies_guardrail("p0", "prompt_artifact_types", "p0_governance")
_emit_snapshots_state("p0", "prompt_artifact_types", "state_snapshot")
_emit_pulls_context("p1", "prompt_artifact_types", "context_pull")
_emit_pulls_context("p1", "prompt_artifact_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "prompt_artifact_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_artifact_types", "uwg_term_secondary")
_emit_writes_through("p1", "prompt_artifact_types", "write_through")
_emit_writes_through("p1", "prompt_artifact_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "prompt_artifact_types", "safety_validation")
_emit_invokes_eval("p1", "prompt_artifact_types", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_artifact_types", "routing_commit")
_emit_escalates_to_human("p1", "prompt_artifact_types", "human_escalation")
_emit_routes_through("p1", "prompt_artifact_types", "route_through")
_emit_checks_agent_registry("p1", "prompt_artifact_types", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_artifact_types", "capability")
_emit_dispatches_execution_plan("p1", "prompt_artifact_types", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_artifact_types", "sub_agent")
_emit_routes_to_agent("p1", "prompt_artifact_types", "target_agent")
_emit_verifies_policy("p1", "prompt_artifact_types", "policy_check")
_emit_observes_runtime_state("p1", "prompt_artifact_types", "runtime_state")
_emit_verifies_boundary("p1", "prompt_artifact_types", "boundary_check")
_emit_transcripts_response("p1", "prompt_artifact_types", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_artifact_types")
_emit_gated_by_confidence("p1", "prompt_artifact_types", "confidence_gate")
emit_replay_key("p0", "prompt_artifact_types")
emit_determinism_digest("p0", "prompt_artifact_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Outcome class literals (shared with trace_feature_types)
# ---------------------------------------------------------------------------

_VALID_OUTCOME_CLASSES: frozenset[str] = frozenset(
    {
        "SUCCESS",
        "SAFE_FAILURE",
        "HEALED_SUCCESS",
        "ESCALATED",
        "REPLAY_FAILURE",
        "UNKNOWN",
    }
)

# ---------------------------------------------------------------------------
# Slot identifiers
# ---------------------------------------------------------------------------

_VALID_SLOTS: frozenset[str] = frozenset({"S0", "D0", "I0", "C0", "U0"})

# ---------------------------------------------------------------------------
# Budget class literals
# ---------------------------------------------------------------------------

_VALID_BUDGET_CLASSES: frozenset[str] = frozenset(
    {"COMPACT", "STANDARD", "EXTENDED", "OVERFLOW"}
)

# ---------------------------------------------------------------------------
# Slot failure categories (section 12 of the addendum)
# ---------------------------------------------------------------------------

_VALID_FAILURE_SLOTS: frozenset[str] = frozenset(
    {
        "S0",   # policy violation
        "D0",   # policy violation / context overflow
        "I0",   # misinterpreted task / style drift
        "C0",   # hallucination / context overflow
        "U0",   # misinterpreted task
        "NONE", # no slot failure identified
    }
)

# ---------------------------------------------------------------------------
# Preference decision literals
# ---------------------------------------------------------------------------

_VALID_PREFERENCE_DECISIONS: frozenset[str] = frozenset(
    {"ACCEPTED", "REJECTED", "MODIFIED", "DEFERRED"}
)

# ---------------------------------------------------------------------------
# Drift signal types
# ---------------------------------------------------------------------------

_VALID_DRIFT_TYPES: frozenset[str] = frozenset(
    {
        "ESCALATION_RATE_INCREASE",
        "GROUNDEDNESS_DROP",
        "REPLAY_INSTABILITY",
        "GUARDRAIL_VIOLATION_INCREASE",
        "IMPROVEMENT_DETECTED",
        "REGRESSION_DETECTED",
    }
)


# ===========================================================================
# PromptSlotManifest
# ===========================================================================


@dataclass(frozen=True)
class PromptSlotManifest:
    """Token-count and hash breakdown for each slot in a compiled prompt.

    Attributes
    ----------
    s0_hash : str
        SHA-256 of the S0 (system/role) slot content.
    d0_hash : str
        SHA-256 of the D0 (defensive fence) slot content.
    i0_hash : str
        SHA-256 of the I0 (instruction) slot content.
    c0_hash : str
        SHA-256 of the C0 (context/RAG) slot content.
    u0_hash : str
        SHA-256 of the U0 (user input) slot content.
    s0_tokens : int
        Token count for S0 slot.
    d0_tokens : int
        Token count for D0 slot.
    i0_tokens : int
        Token count for I0 slot.
    c0_tokens : int
        Token count for C0 slot.
    u0_tokens : int
        Token count for U0 slot.
    total_tokens : int
        Sum of all slot token counts.
    budget_class : str
        One of COMPACT / STANDARD / EXTENDED / OVERFLOW.
    """

    s0_hash: str
    d0_hash: str
    i0_hash: str
    c0_hash: str
    u0_hash: str
    s0_tokens: int
    d0_tokens: int
    i0_tokens: int
    c0_tokens: int
    u0_tokens: int
    total_tokens: int
    budget_class: str

    def __post_init__(self) -> None:
        if self.budget_class not in _VALID_BUDGET_CLASSES:
            raise ValueError(
                f"budget_class must be one of {sorted(_VALID_BUDGET_CLASSES)}, "
                f"got {self.budget_class!r}"
            )
        for slot, tok in (
            ("s0_tokens", self.s0_tokens),
            ("d0_tokens", self.d0_tokens),
            ("i0_tokens", self.i0_tokens),
            ("c0_tokens", self.c0_tokens),
            ("u0_tokens", self.u0_tokens),
            ("total_tokens", self.total_tokens),
        ):
            if tok < 0:
                raise ValueError(f"{slot} must be >= 0, got {tok}")

    def to_dict(self) -> dict:
        return {
            "budget_class": self.budget_class,
            "c0_hash": self.c0_hash,
            "c0_tokens": self.c0_tokens,
            "d0_hash": self.d0_hash,
            "d0_tokens": self.d0_tokens,
            "i0_hash": self.i0_hash,
            "i0_tokens": self.i0_tokens,
            "s0_hash": self.s0_hash,
            "s0_tokens": self.s0_tokens,
            "total_tokens": self.total_tokens,
            "u0_hash": self.u0_hash,
            "u0_tokens": self.u0_tokens,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(
            deterministic_json(self.to_dict()).encode("utf-8")
        ).hexdigest()


# ===========================================================================
# CompiledPromptArtifact
# ===========================================================================


@dataclass(frozen=True)
class CompiledPromptArtifact:
    """A fully assembled, immutable compiled prompt artifact.

    This is a **primary ADG node** of type ``CompiledPromptArtifact``.
    Every prompt sent to a model must be representable as one of these.

    Attributes
    ----------
    prompt_hash : str
        SHA-256 of the canonical serialized prompt payload.
    slot_manifest : PromptSlotManifest
        Per-slot token counts and hashes.
    template_ids : tuple[str, ...]
        Sorted template IDs used to assemble the prompt.
    fewshot_ids : tuple[str, ...]
        Sorted few-shot example IDs injected.
    injection_ids : tuple[str, ...]
        Sorted I0-injection IDs (instructions/style policies).
    c0_sources : tuple[str, ...]
        Sorted C0 context source hashes (RAG chunk IDs / citation hashes).
    model_target : str
        Identifier of the model this prompt was compiled for.
    policy_hash : str | None
        Hash of the active policy at compilation time.
    adg_entity_name : str
        ADG entity name for this artifact (``ADG::CompiledPrompt::{prefix}``).
    influence_class : str
        Always ``"C0_INFORMATIONAL"``.
    timestamp_utc : int
        Caller-supplied compilation timestamp.
    """

    prompt_hash: str
    slot_manifest: PromptSlotManifest
    template_ids: tuple[str, ...]
    fewshot_ids: tuple[str, ...]
    injection_ids: tuple[str, ...]
    c0_sources: tuple[str, ...]
    model_target: str
    policy_hash: str | None
    adg_entity_name: str
    influence_class: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.influence_class != "C0_INFORMATIONAL":
            raise ValueError(
                "CompiledPromptArtifact.influence_class must be 'C0_INFORMATIONAL', "
                f"got {self.influence_class!r}"
            )
        if not self.prompt_hash:
            raise ValueError("prompt_hash must not be empty")
        if not self.adg_entity_name.startswith("ADG::"):
            raise ValueError(
                f"adg_entity_name must start with 'ADG::', got {self.adg_entity_name!r}"
            )
        if not self.model_target:
            raise ValueError("model_target must not be empty")

    def to_dict(self) -> dict:
        return {
            "adg_entity_name": self.adg_entity_name,
            "c0_sources": sorted(self.c0_sources),
            "fewshot_ids": sorted(self.fewshot_ids),
            "influence_class": self.influence_class,
            "injection_ids": sorted(self.injection_ids),
            "model_target": self.model_target,
            "policy_hash": self.policy_hash,
            "prompt_hash": self.prompt_hash,
            "slot_manifest": self.slot_manifest.to_dict(),
            "template_ids": sorted(self.template_ids),
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


# ===========================================================================
# PromptSafetyDecision
# ===========================================================================


@dataclass(frozen=True)
class PromptSafetyDecision:
    """Result of L5 policy, guardrail, and budget validation on a compiled prompt.

    Attributes
    ----------
    decision_id : str
        Content-addressed SHA-256 of this decision.
    prompt_hash : str
        The prompt artifact being validated.
    allowed : bool
        True iff all safety checks passed.
    policy_hash : str | None
        Active policy hash at validation time.
    guardrail_set : tuple[str, ...]
        Sorted guardrail IDs evaluated.
    budget_class : str
        Budget class from the slot manifest.
    denial_reasons : tuple[str, ...]
        Empty when allowed=True; populated when allowed=False.
    adg_relation : str
        ``compiled_prompt_allowed`` or ``compiled_prompt_blocked``.
    timestamp_utc : int
        Caller-supplied validation timestamp.
    """

    decision_id: str
    prompt_hash: str
    allowed: bool
    policy_hash: str | None
    guardrail_set: tuple[str, ...]
    budget_class: str
    denial_reasons: tuple[str, ...]
    adg_relation: str
    timestamp_utc: int

    _VALID_ADG_RELATIONS: frozenset[str] = frozenset(
        {"compiled_prompt_allowed", "compiled_prompt_blocked"}
    )

    def __post_init__(self) -> None:
        if self.adg_relation not in self._VALID_ADG_RELATIONS:
            raise ValueError(
                f"adg_relation must be one of {sorted(self._VALID_ADG_RELATIONS)}, "
                f"got {self.adg_relation!r}"
            )
        if self.allowed and self.denial_reasons:
            raise ValueError(
                "denial_reasons must be empty when allowed=True"
            )
        if not self.allowed and not self.denial_reasons:
            raise ValueError(
                "denial_reasons must not be empty when allowed=False"
            )
        if self.budget_class not in _VALID_BUDGET_CLASSES:
            raise ValueError(
                f"budget_class must be one of {sorted(_VALID_BUDGET_CLASSES)}"
            )

    def to_dict(self) -> dict:
        return {
            "adg_relation": self.adg_relation,
            "allowed": self.allowed,
            "budget_class": self.budget_class,
            "decision_id": self.decision_id,
            "denial_reasons": sorted(self.denial_reasons),
            "guardrail_set": sorted(self.guardrail_set),
            "policy_hash": self.policy_hash,
            "prompt_hash": self.prompt_hash,
            "timestamp_utc": self.timestamp_utc,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(
            deterministic_json(self.to_dict()).encode("utf-8")
        ).hexdigest()


# ===========================================================================
# PromptExecutionRecord
# ===========================================================================


@dataclass(frozen=True)
class PromptExecutionRecord:
    """Runtime execution data for a compiled prompt.

    Attributes
    ----------
    execution_id : str
        Content-addressed SHA-256 of this record.
    prompt_hash : str
        The prompt artifact that was executed.
    trace_id : str
        ADG trace ID linking to the execution trace.
    route_selected : str
        Routing path (e.g. PATH_A, PATH_B).
    model_id : str
        Model identifier used for inference.
    latency_ms : int
        Observed inference latency in milliseconds.
    input_tokens : int
        Token count of the prompt as sent.
    output_tokens : int
        Token count of the model response.
    adg_entity_name : str
        ADG entity name for this execution.
    timestamp_utc : int
        Caller-supplied execution timestamp.
    """

    execution_id: str
    prompt_hash: str
    trace_id: str
    route_selected: str
    model_id: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    adg_entity_name: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if not self.prompt_hash:
            raise ValueError("prompt_hash must not be empty")
        if self.latency_ms < 0:
            raise ValueError(f"latency_ms must be >= 0, got {self.latency_ms}")
        if self.input_tokens < 0:
            raise ValueError(f"input_tokens must be >= 0, got {self.input_tokens}")
        if self.output_tokens < 0:
            raise ValueError(f"output_tokens must be >= 0, got {self.output_tokens}")

    def to_dict(self) -> dict:
        return {
            "adg_entity_name": self.adg_entity_name,
            "execution_id": self.execution_id,
            "input_tokens": self.input_tokens,
            "latency_ms": self.latency_ms,
            "model_id": self.model_id,
            "output_tokens": self.output_tokens,
            "prompt_hash": self.prompt_hash,
            "route_selected": self.route_selected,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(
            deterministic_json(self.to_dict()).encode("utf-8")
        ).hexdigest()


# ===========================================================================
# PromptOutcomeRecord
# ===========================================================================


@dataclass(frozen=True)
class PromptOutcomeRecord:
    """Per-execution outcome record for a compiled prompt.

    This is the primary feed object for the meta-learning bus.
    Slot failure annotations connect outcome to the specific slot
    responsible, enabling targeted prompt tuning.

    Attributes
    ----------
    outcome_id : str
        Content-addressed SHA-256 of this record.
    prompt_hash : str
        The prompt artifact whose execution produced this outcome.
    trace_id : str
        ADG trace ID of the execution.
    route : str
        Routing path selected.
    model : str
        Model used.
    groundedness_score : float
        Retrieval groundedness score in [0.0, 1.0].
    guardrail_hits : tuple[str, ...]
        Sorted guardrail IDs that fired during this execution.
    healer_invoked : bool
        Whether a healer was activated.
    healer_id : str | None
        Healer agent ID if healer_invoked is True.
    hitl_escalation : bool
        Whether the execution was escalated to a human.
    replay_status : str
        ``PASSED``, ``FAILED``, or ``NOT_TESTED``.
    final_outcome : str
        One of SUCCESS / SAFE_FAILURE / HEALED_SUCCESS / ESCALATED / REPLAY_FAILURE / UNKNOWN.
    failure_slot : str
        The slot most responsible for the failure (S0/D0/I0/C0/U0/NONE).
    support_score : float
        Citation support score in [0.0, 1.0].
    completeness_score : float
        Answer completeness score in [0.0, 1.0].
    citation_count : int
        Number of citations / RAG chunks used.
    adg_entity_name : str
        ADG entity name for this outcome record.
    timestamp_utc : int
        Caller-supplied outcome timestamp.
    """

    outcome_id: str
    prompt_hash: str
    trace_id: str
    route: str
    model: str
    groundedness_score: float
    guardrail_hits: tuple[str, ...]
    healer_invoked: bool
    healer_id: str | None
    hitl_escalation: bool
    replay_status: str
    final_outcome: str
    failure_slot: str
    support_score: float
    completeness_score: float
    citation_count: int
    adg_entity_name: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.final_outcome not in _VALID_OUTCOME_CLASSES:
            raise ValueError(
                f"final_outcome must be one of {sorted(_VALID_OUTCOME_CLASSES)}, "
                f"got {self.final_outcome!r}"
            )
        if self.failure_slot not in _VALID_FAILURE_SLOTS:
            raise ValueError(
                f"failure_slot must be one of {sorted(_VALID_FAILURE_SLOTS)}, "
                f"got {self.failure_slot!r}"
            )
        for attr, val in (
            ("groundedness_score", self.groundedness_score),
            ("support_score", self.support_score),
            ("completeness_score", self.completeness_score),
        ):
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{attr} must be in [0.0, 1.0], got {val}")
        if self.citation_count < 0:
            raise ValueError(f"citation_count must be >= 0, got {self.citation_count}")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.replay_status not in ("PASSED", "FAILED", "NOT_TESTED"):
            raise ValueError(
                f"replay_status must be PASSED/FAILED/NOT_TESTED, got {self.replay_status!r}"
            )

    def to_dict(self) -> dict:
        return {
            "adg_entity_name": self.adg_entity_name,
            "citation_count": self.citation_count,
            "completeness_score": round(self.completeness_score, 6),
            "failure_slot": self.failure_slot,
            "final_outcome": self.final_outcome,
            "groundedness_score": round(self.groundedness_score, 6),
            "guardrail_hits": sorted(self.guardrail_hits),
            "healer_id": self.healer_id,
            "healer_invoked": self.healer_invoked,
            "hitl_escalation": self.hitl_escalation,
            "model": self.model,
            "outcome_id": self.outcome_id,
            "prompt_hash": self.prompt_hash,
            "replay_status": self.replay_status,
            "route": self.route,
            "support_score": round(self.support_score, 6),
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


# ===========================================================================
# PreferenceRecord
# ===========================================================================


@dataclass(frozen=True)
class PreferenceRecord:
    """HITL Path-D feedback record for DPO dataset generation.

    Created when a human reviewer patches, accepts, or rejects the model
    output for a specific compiled prompt.

    Attributes
    ----------
    preference_id : str
        Content-addressed SHA-256 of this record.
    prompt_hash : str
        The compiled prompt that triggered the escalation.
    trace_id : str
        Execution trace that produced the escalation.
    proposal_summary : str
        Summary of what the model proposed (original output).
    human_patch : str | None
        The human-supplied correction, or None if accepted/deferred.
    decision : str
        One of ACCEPTED / REJECTED / MODIFIED / DEFERRED.
    outcome : str
        Post-patch outcome class.
    adg_entity_name : str
        ADG entity name for this preference record.
    timestamp_utc : int
        Caller-supplied HITL decision timestamp.
    """

    preference_id: str
    prompt_hash: str
    trace_id: str
    proposal_summary: str
    human_patch: str | None
    decision: str
    outcome: str
    adg_entity_name: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.decision not in _VALID_PREFERENCE_DECISIONS:
            raise ValueError(
                f"decision must be one of {sorted(_VALID_PREFERENCE_DECISIONS)}, "
                f"got {self.decision!r}"
            )
        if self.outcome not in _VALID_OUTCOME_CLASSES:
            raise ValueError(
                f"outcome must be one of {sorted(_VALID_OUTCOME_CLASSES)}, "
                f"got {self.outcome!r}"
            )
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if not self.prompt_hash:
            raise ValueError("prompt_hash must not be empty")
        if self.decision == "MODIFIED" and self.human_patch is None:
            raise ValueError(
                "human_patch must not be None when decision is MODIFIED"
            )

    def to_dict(self) -> dict:
        return {
            "adg_entity_name": self.adg_entity_name,
            "decision": self.decision,
            "human_patch": self.human_patch,
            "outcome": self.outcome,
            "preference_id": self.preference_id,
            "prompt_hash": self.prompt_hash,
            "proposal_summary": self.proposal_summary,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


# ===========================================================================
# PromptDriftSignal
# ===========================================================================


@dataclass(frozen=True)
class PromptDriftSignal:
    """Inter-version drift observation for a prompt template or artifact.

    Produced by the PromptDriftDetector when comparing two windows of
    PromptOutcomeRecords for the same prompt_hash or template_id.

    Attributes
    ----------
    signal_id : str
        Content-addressed SHA-256 of this signal.
    prompt_hash_before : str
        Prompt hash of the earlier version (or empty for first observation).
    prompt_hash_after : str
        Prompt hash of the later version being observed.
    drift_type : str
        One of the VALID_DRIFT_TYPES.
    magnitude : float
        Signed magnitude of the change (positive = worsening for regressions,
        positive = improving for IMPROVEMENT_DETECTED).
    affected_slot : str | None
        The slot most associated with the drift, or None if cross-slot.
    baseline_window_size : int
        Number of outcome records in the before window.
    current_window_size : int
        Number of outcome records in the after window.
    adg_relation : str
        The ADG relation emitted (e.g. ``prompt_prompt_regression_detected``).
    timestamp_utc : int
        Caller-supplied detection timestamp.
    """

    signal_id: str
    prompt_hash_before: str
    prompt_hash_after: str
    drift_type: str
    magnitude: float
    affected_slot: str | None
    baseline_window_size: int
    current_window_size: int
    adg_relation: str
    timestamp_utc: int

    _VALID_ADG_RELATIONS: frozenset[str] = frozenset(
        {
            "prompt_version_replaced_by",
            "prompt_template_superseded",
            "prompt_prompt_regression_detected",
            "prompt_prompt_improvement_detected",
        }
    )

    def __post_init__(self) -> None:
        if self.drift_type not in _VALID_DRIFT_TYPES:
            raise ValueError(
                f"drift_type must be one of {sorted(_VALID_DRIFT_TYPES)}, "
                f"got {self.drift_type!r}"
            )
        if self.adg_relation not in self._VALID_ADG_RELATIONS:
            raise ValueError(
                f"adg_relation must be one of {sorted(self._VALID_ADG_RELATIONS)}, "
                f"got {self.adg_relation!r}"
            )
        if self.baseline_window_size < 0:
            raise ValueError("baseline_window_size must be >= 0")
        if self.current_window_size < 1:
            raise ValueError("current_window_size must be >= 1")
        if self.affected_slot is not None and self.affected_slot not in _VALID_FAILURE_SLOTS:
            raise ValueError(
                f"affected_slot must be one of {sorted(_VALID_FAILURE_SLOTS)} or None"
            )

    def to_dict(self) -> dict:
        return {
            "adg_relation": self.adg_relation,
            "affected_slot": self.affected_slot,
            "baseline_window_size": self.baseline_window_size,
            "current_window_size": self.current_window_size,
            "drift_type": self.drift_type,
            "magnitude": round(self.magnitude, 6),
            "prompt_hash_after": self.prompt_hash_after,
            "prompt_hash_before": self.prompt_hash_before,
            "signal_id": self.signal_id,
            "timestamp_utc": self.timestamp_utc,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(
            deterministic_json(self.to_dict()).encode("utf-8")
        ).hexdigest()


# ===========================================================================
# Exports
# ===========================================================================

__all__ = [
    "CompiledPromptArtifact",
    "PreferenceRecord",
    "PromptDriftSignal",
    "PromptExecutionRecord",
    "PromptOutcomeRecord",
    "PromptSafetyDecision",
    "PromptSlotManifest",
]
