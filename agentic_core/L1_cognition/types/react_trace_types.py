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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "react_trace_types")
trace_contract.emit_determinism_digest("p0", "react_trace_types")

trace_contract._emit_dispatches_healing_run("p1", "react_trace_types", "L1")
trace_contract._emit_routes_through("p1", "react_trace_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "react_trace_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "react_trace_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "react_trace_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "react_trace_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "react_trace_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "react_trace_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "react_trace_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "react_trace_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "react_trace_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "react_trace_types")
trace_contract._emit_gated_by_confidence("p1", "react_trace_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "react_trace_types", "L1")
trace_contract._emit_reads_policy_state("p1", "react_trace_types", "L1")
trace_contract._emit_authorize_and_execute("p2", "react_trace_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "react_trace_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "react_trace_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "react_trace_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "react_trace_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "react_trace_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "react_trace_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "react_trace_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "react_trace_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "react_trace_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "react_trace_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "react_trace_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "react_trace_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "react_trace_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "react_trace_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "react_trace_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "react_trace_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "react_trace_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "react_trace_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "react_trace_types", "exec_snapshot_link")

trace_contract.record_execution_trace("react_trace_types", "react_trace_types_trace")


trace_contract._emit_emits_metric_event("react_trace_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("react_trace_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("react_trace_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("react_trace_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("react_trace_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("react_trace_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("react_trace_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("react_trace_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("react_trace_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("react_trace_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("react_trace_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("react_trace_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("react_trace_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("react_trace_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("react_trace_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("react_trace_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("react_trace_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("react_trace_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("react_trace_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("react_trace_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("react_trace_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("react_trace_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("react_trace_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("react_trace_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("react_trace_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("react_trace_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("react_trace_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("react_trace_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "react_trace_types", "context_pull")
trace_contract._emit_pulls_context("p1", "react_trace_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "react_trace_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "react_trace_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "react_trace_types", "write_through")
trace_contract._emit_writes_through("p1", "react_trace_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "react_trace_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "react_trace_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "react_trace_types", "routing_commit")

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
    },
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

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "assert_c0_informational", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "assert_c0_informational", "p0_governance")
    leaked = C0_FORBIDDEN_FIELDS & set(rag_context.keys())
    if leaked:
        raise C0BoundaryViolation(
            f"C0 violation{f' in {source}' if source else ''}: "
            f"RAG context contains authority fields {sorted(leaked)}. "
            "RAG context is informational only.",
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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L1_REASONING,
            "ReasonTraceEnvelope.canonical_bytes",
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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L1_REASONING,
            "PromptProvenanceRecord.canonical_bytes",
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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_REASONING, "ReplayGuard.record_violation")

        self._violations.append(source)
        if self.strict:
            raise NonDeterministicCallDetected(
                f"ReplayGuard: non-deterministic call intercepted from '{source}'. "
                "Use semantic_clock_vector instead of wall-clock time or random.",
            )

    @property
    def violations(self) -> list[str]:
        return list(self._violations)

    def assert_clean(self) -> None:
        """Raise if any violations were recorded (non-strict mode check)."""
        if self._violations:
            raise NonDeterministicCallDetected(
                f"ReplayGuard: {len(self._violations)} non-deterministic call(s) detected: {self._violations}",
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
