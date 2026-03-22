"""ReAct determinism and provenance types — L1_cognition canonical types.

Defines immutable, hashable artifacts required for:
  - Deterministic reasoning trace capture (ReasonTraceEnvelope)
  - Prompt provenance recording (PromptProvenanceRecord)
  - C0 boundary enforcement (C0BoundaryViolation)
  - Replay guard contract (ReplayGuard)

C0 RULE: All RAG context is informational only. These types enforce that
RAG data cannot mutate routing decisions, safety policy, execution tier,
or tool budget.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    record_execution_trace,
)

emit_replay_key("p0", "react_trace_types")
emit_determinism_digest("p0", "react_trace_types")

_emit_dispatches_healing_run("p1", "react_trace_types", "L1")
_emit_routes_through("p1", "react_trace_types", "L1")
_emit_checks_agent_registry("p1", "react_trace_types", "agent_registry")
_emit_validates_agent_capability("p1", "react_trace_types", "capability")
_emit_dispatches_execution_plan("p1", "react_trace_types", "exec_plan")
_emit_agent_executes_agent("p1", "react_trace_types", "sub_agent")
_emit_routes_to_agent("p1", "react_trace_types", "target_agent")
_emit_verifies_policy("p1", "react_trace_types", "policy_check")
_emit_observes_runtime_state("p1", "react_trace_types", "runtime_state")
_emit_verifies_boundary("p1", "react_trace_types", "boundary_check")
_emit_transcripts_response("p1", "react_trace_types", "transcript")
_emit_hard_fails_untranscripted("p1", "react_trace_types")
_emit_gated_by_confidence("p1", "react_trace_types", "confidence_gate")
_emit_escalates_to_human("p1", "react_trace_types", "L1")
_emit_reads_policy_state("p1", "react_trace_types", "L1")
_emit_authorize_and_execute("p2", "react_trace_types", "execution_auth")
_emit_validates_capability("p2", "react_trace_types", "capability_check")
_emit_routes_to_capability("p2", "react_trace_types", "capability_route")
_emit_writes_via_uwg("p2", "react_trace_types", "uwg_write")
_emit_blocks_direct_write("p2", "react_trace_types", "direct_write_block")
_emit_records_tool_invocation("p2", "react_trace_types", "tool_invocation")
_emit_captures_execution_output("p2", "react_trace_types", "exec_output")
_emit_dispatches_agent("p3", "react_trace_types", "agent_dispatch")
_emit_coordinates_agents("p3", "react_trace_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "react_trace_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "react_trace_types", "healing_outcome")
_emit_escalates_failure("p3", "react_trace_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "react_trace_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "react_trace_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "react_trace_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "react_trace_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "react_trace_types", "eval_metric")
_emit_stores_embedding("p4", "react_trace_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "react_trace_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "react_trace_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

record_execution_trace("react_trace_types", "react_trace_types_trace")


_emit_emits_metric_event("react_trace_types", "p4obs", "metric_1")
_emit_emits_metric_event("react_trace_types", "p4obs", "metric_2")
_emit_emits_metric_event("react_trace_types", "p4obs", "metric_3")
_emit_emits_metric_event("react_trace_types", "p4obs", "metric_4")
_emit_emits_metric_event("react_trace_types", "p4obs", "metric_5")
_emit_emits_metric_event("react_trace_types", "p4obs", "metric_6")
_emit_records_incident_event("react_trace_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("react_trace_types", "p4obs", "anomaly")
_emit_writes_observability_log("react_trace_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("react_trace_types", "p4obs", "mon_state")
_emit_triggers_alert("react_trace_types", "p4obs", "alert")
_emit_links_incident_trace("react_trace_types", "p4obs", "trace_link")
_emit_captures_pattern("react_trace_types", "p3lm", "pattern")
_emit_records_learning_event("react_trace_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("react_trace_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("react_trace_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("react_trace_types", "p3lm", "routing")
_emit_improves_agent_policy("react_trace_types", "p3lm", "policy")
_emit_stores_learning_state("react_trace_types", "p3lm", "state")
_emit_records_execution_trace("react_trace_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("react_trace_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("react_trace_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("react_trace_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("react_trace_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("react_trace_types", "env_read", "p2_env_1")
_emit_reads_environ("react_trace_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("react_trace_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("react_trace_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "react_trace_types", "context_pull")
_emit_pulls_context("p1", "react_trace_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "react_trace_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "react_trace_types", "uwg_term_2")
_emit_writes_through("p1", "react_trace_types", "write_through")
_emit_writes_through("p1", "react_trace_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "react_trace_types", "safety_validation")
_emit_invokes_eval("p1", "react_trace_types", "eval_call")
_emit_proposal_commits_routing("p1", "react_trace_types", "routing_commit")

# ---------------------------------------------------------------------------
# C0 Forbidden mutation fields — RAG context must not carry these
# ---------------------------------------------------------------------------

C0_FORBIDDEN_FIELDS: frozenset[str] = frozenset(
    {
        "route_mode",
        "execution_tier",
        "safety_threshold",
        "allowed_tools",
        "auth_token",
        "tool_budget",
        "policy_override",
        "safety_policy",
    }
)


class C0BoundaryViolation(RuntimeError):
    """Raised when RAG context attempts to mutate a protected field."""


def assert_c0_informational(rag_context: dict[str, Any], source: str = "") -> None:
    """Enforce C0 boundary: RAG context must contain no authority fields.

    Args:
        rag_context: The RAG context dict to inspect.
        source: Optional label for error messages.

    Raises:
        C0BoundaryViolation: If any forbidden field is present.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_c0_informational", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_c0_informational", "p0_governance")
    leaked = C0_FORBIDDEN_FIELDS & set(rag_context.keys())
    if leaked:
        raise C0BoundaryViolation(
            f"C0 violation{f' in {source}' if source else ''}: "
            f"RAG context contains authority fields {sorted(leaked)}. "
            "RAG context is informational only."
        )


# ---------------------------------------------------------------------------
# ReasonTraceEnvelope — deterministic reasoning trace artifact
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReasonTraceEnvelope:
    """Immutable envelope capturing a complete ReAct reasoning trace.

    All fields are required. The envelope hash is computed from canonical
    JSON of all fields except envelope_hash itself.
    """

    trace_id: str
    plan_hash: str
    reason_steps: tuple[str, ...]
    action_steps: tuple[str, ...]
    tool_invocations: tuple[str, ...]
    policy_hash: str
    semantic_clock_vector: tuple[int, ...]
    envelope_hash: str = ""

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "ReasonTraceEnvelope.canonical_bytes"
        )

        d = {
            "trace_id": self.trace_id,
            "plan_hash": self.plan_hash,
            "reason_steps": list(self.reason_steps),
            "action_steps": list(self.action_steps),
            "tool_invocations": list(self.tool_invocations),
            "policy_hash": self.policy_hash,
            "semantic_clock_vector": list(self.semantic_clock_vector),
        }
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def compute_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def verify(self) -> bool:
        """Return True if envelope_hash matches recomputed hash."""
        return not self.envelope_hash or self.envelope_hash == self.compute_hash()

    @classmethod
    def build(
        cls,
        trace_id: str,
        plan_hash: str,
        reason_steps: tuple[str, ...],
        action_steps: tuple[str, ...],
        tool_invocations: tuple[str, ...],
        policy_hash: str,
        semantic_clock_vector: tuple[int, ...],
    ) -> ReasonTraceEnvelope:
        obj = cls(
            trace_id=trace_id,
            plan_hash=plan_hash,
            reason_steps=reason_steps,
            action_steps=action_steps,
            tool_invocations=tool_invocations,
            policy_hash=policy_hash,
            semantic_clock_vector=semantic_clock_vector,
            envelope_hash="",
        )
        h = obj.compute_hash()
        return cls(
            trace_id=trace_id,
            plan_hash=plan_hash,
            reason_steps=reason_steps,
            action_steps=action_steps,
            tool_invocations=tool_invocations,
            policy_hash=policy_hash,
            semantic_clock_vector=semantic_clock_vector,
            envelope_hash=h,
        )


# ---------------------------------------------------------------------------
# PromptProvenanceRecord — prompt lineage artifact
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromptProvenanceRecord:
    """Immutable record of prompt construction provenance.

    Captures all inputs that contributed to a prompt so that replay
    can reconstruct the identical prompt hash.
    """

    prompt_hash: str
    prompt_template_id: str
    rag_context_ids: tuple[str, ...]
    policy_hash: str
    model_id: str

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "PromptProvenanceRecord.canonical_bytes"
        )

        d = {
            "prompt_hash": self.prompt_hash,
            "prompt_template_id": self.prompt_template_id,
            "rag_context_ids": list(self.rag_context_ids),
            "policy_hash": self.policy_hash,
            "model_id": self.model_id,
        }
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def record_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @classmethod
    def build(
        cls,
        prompt_text: str,
        prompt_template_id: str,
        rag_context_ids: tuple[str, ...],
        policy_hash: str,
        model_id: str,
    ) -> PromptProvenanceRecord:
        prompt_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
        return cls(
            prompt_hash=prompt_hash,
            prompt_template_id=prompt_template_id,
            rag_context_ids=rag_context_ids,
            policy_hash=policy_hash,
            model_id=model_id,
        )


# ---------------------------------------------------------------------------
# ReplayGuard — intercepts non-deterministic clock/random sources
# ---------------------------------------------------------------------------


class NonDeterministicCallDetected(RuntimeError):
    """Raised when a forbidden non-deterministic call is detected."""


@dataclass
class ReplayGuard:
    """Guards a reasoning execution against non-deterministic sources.

    In replay mode, any call to wall-clock time or random is intercepted
    and replaced with the deterministic semantic_clock_vector tick.

    Usage::

        guard = ReplayGuard(semantic_clock_vector=(1000, 0))
        with guard:
            result = run_react(...)
    """

    semantic_clock_vector: tuple[int, ...]
    strict: bool = True
    _violations: list[str] = field(default_factory=list)

    @property
    def current_tick(self) -> int:
        return self.semantic_clock_vector[0] if self.semantic_clock_vector else 0

    def record_violation(self, source: str) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ReplayGuard.record_violation")

        self._violations.append(source)
        if self.strict:
            raise NonDeterministicCallDetected(
                f"ReplayGuard: non-deterministic call intercepted from '{source}'. "
                "Use semantic_clock_vector instead of wall-clock time or random."
            )

    @property
    def violations(self) -> list[str]:
        return list(self._violations)

    def assert_clean(self) -> None:
        """Raise if any violations were recorded (non-strict mode check)."""
        if self._violations:
            raise NonDeterministicCallDetected(
                f"ReplayGuard: {len(self._violations)} non-deterministic call(s) detected: {self._violations}"
            )


__all__ = [
    "C0_FORBIDDEN_FIELDS",
    "C0BoundaryViolation",
    "assert_c0_informational",
    "ReasonTraceEnvelope",
    "PromptProvenanceRecord",
    "NonDeterministicCallDetected",
    "ReplayGuard",
]
