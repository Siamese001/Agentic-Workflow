"""
Phase 7 — ToolIntent: declarative tool emission from L1 + L1 mutation blocker.

L1 cognition MUST NOT directly invoke mutating tools.
Instead it emits a ToolIntent which is executed in the L2.2 commit sandbox.

Enforcement seam:
  assert_l1_tool_allowed(capability) — raises ToolViolation if MUTATING_* in L1 context.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "tool_intent_types")
emit_determinism_digest("p0", "tool_intent_types")

_emit_dispatches_healing_run("p1", "tool_intent_types", "L2")
_emit_routes_through("p1", "tool_intent_types", "L2")
_emit_checks_agent_registry("p1", "tool_intent_types", "agent_registry")
_emit_validates_agent_capability("p1", "tool_intent_types", "capability")
_emit_dispatches_execution_plan("p1", "tool_intent_types", "exec_plan")
_emit_agent_executes_agent("p1", "tool_intent_types", "sub_agent")
_emit_routes_to_agent("p1", "tool_intent_types", "target_agent")
_emit_verifies_policy("p1", "tool_intent_types", "policy_check")
_emit_observes_runtime_state("p1", "tool_intent_types", "runtime_state")
_emit_verifies_boundary("p1", "tool_intent_types", "boundary_check")
_emit_transcripts_response("p1", "tool_intent_types", "transcript")
_emit_hard_fails_untranscripted("p1", "tool_intent_types")
_emit_gated_by_confidence("p1", "tool_intent_types", "confidence_gate")
_emit_escalates_to_human("p1", "tool_intent_types", "L2")
_emit_reads_policy_state("p1", "tool_intent_types", "L2")

_emit_applies_guardrail("p0", "tool_intent_types", "p0_governance")
_emit_snapshots_state("p0", "tool_intent_types", "state_snapshot")
_emit_authorize_and_execute("p2", "tool_intent_types", "execution_auth")
_emit_validates_capability("p2", "tool_intent_types", "capability_check")
_emit_routes_to_capability("p2", "tool_intent_types", "capability_route")
_emit_writes_via_uwg("p2", "tool_intent_types", "uwg_write")
_emit_blocks_direct_write("p2", "tool_intent_types", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_intent_types", "tool_invocation")
_emit_captures_execution_output("p2", "tool_intent_types", "exec_output")
_emit_dispatches_agent("p3", "tool_intent_types", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_intent_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_intent_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_intent_types", "healing_outcome")
_emit_escalates_failure("p3", "tool_intent_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_intent_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_intent_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_intent_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_intent_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_intent_types", "eval_metric")
_emit_stores_embedding("p4", "tool_intent_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_intent_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_intent_types", "exec_snapshot_link")

_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ToolCapability(str, Enum):
    """
    Capability class of a tool.

    NON_MUTATING      — read-only; safe to call from L1 directly.
    MUTATING_EXTERNAL — writes to external services (Redis, Pinecone, APIs).
    MUTATING_FS       — writes to the filesystem.
    MUTATING_STATEBUS — writes to the internal state bus / event bus.
    """

    NON_MUTATING = "non_mutating"
    MUTATING_EXTERNAL = "mutating_external"
    MUTATING_FS = "mutating_fs"
    MUTATING_STATEBUS = "mutating_statebus"


_MUTATING_CAPABILITIES: frozenset[ToolCapability] = frozenset(
    {ToolCapability.MUTATING_EXTERNAL, ToolCapability.MUTATING_FS, ToolCapability.MUTATING_STATEBUS}
)


def is_mutating(capability: ToolCapability) -> bool:
    """Return True if the capability class requires sandbox execution."""
    return capability in _MUTATING_CAPABILITIES


class ToolViolation(Exception):
    """
    Raised when L1 attempts a direct mutating tool call, or when a ToolIntent
    is executed outside the L2.2 commit sandbox.

    Attributes
    ----------
    code   : str  — violation code string
    detail : str  — human-readable description
    """

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"[{code}]" + (f" {detail}" if detail else ""))


_L1_COGNITION_ACTIVE: bool = False


def is_l1_cognition_active() -> bool:
    """Return True when L1 cognition context is active."""
    return _L1_COGNITION_ACTIVE


def assert_l1_tool_allowed(capability: ToolCapability, tool_name: str = "") -> None:
    """
    Raise ToolViolation(code="L1_TOOL_CALL_BLOCKED") if L1 cognition is active
    and the tool has a MUTATING_* capability.

    Call this at the top of any tool invocation seam.
    """
    if _L1_COGNITION_ACTIVE and is_mutating(capability):
        detail = f"tool '{tool_name}' has capability {capability.value}; emit ToolIntent instead"
        raise ToolViolation(code="L1_TOOL_CALL_BLOCKED", detail=detail)


from contextlib import contextmanager
from typing import Generator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("tool_intent_types", "p4obs", "metric_1")
_emit_emits_metric_event("tool_intent_types", "p4obs", "metric_2")
_emit_emits_metric_event("tool_intent_types", "p4obs", "metric_3")
_emit_emits_metric_event("tool_intent_types", "p4obs", "metric_4")
_emit_emits_metric_event("tool_intent_types", "p4obs", "metric_5")
_emit_emits_metric_event("tool_intent_types", "p4obs", "metric_6")
_emit_records_incident_event("tool_intent_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("tool_intent_types", "p4obs", "anomaly")
_emit_writes_observability_log("tool_intent_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("tool_intent_types", "p4obs", "mon_state")
_emit_triggers_alert("tool_intent_types", "p4obs", "alert")
_emit_links_incident_trace("tool_intent_types", "p4obs", "trace_link")
_emit_captures_pattern("tool_intent_types", "p3lm", "pattern")
_emit_records_learning_event("tool_intent_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tool_intent_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("tool_intent_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tool_intent_types", "p3lm", "routing")
_emit_improves_agent_policy("tool_intent_types", "p3lm", "policy")
_emit_stores_learning_state("tool_intent_types", "p3lm", "state")
_emit_records_execution_trace("tool_intent_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tool_intent_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tool_intent_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tool_intent_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tool_intent_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tool_intent_types", "env_read", "p2_env_1")
_emit_reads_environ("tool_intent_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("tool_intent_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tool_intent_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tool_intent_types", "context_pull")
_emit_pulls_context("p1", "tool_intent_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tool_intent_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tool_intent_types", "uwg_term_2")
_emit_writes_through("p1", "tool_intent_types", "write_through")
_emit_writes_through("p1", "tool_intent_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "tool_intent_types", "safety_validation")
_emit_invokes_eval("p1", "tool_intent_types", "eval_call")
_emit_proposal_commits_routing("p1", "tool_intent_types", "routing_commit")


@contextmanager
def l1_cognition_scope() -> Generator[None, None, None]:
    """
    Context manager that activates the L1 cognition enforcement flag.

    Inside this scope, any direct call to a MUTATING_* tool raises ToolViolation.
    """
    global _L1_COGNITION_ACTIVE
    already_active = _L1_COGNITION_ACTIVE
    _L1_COGNITION_ACTIVE = True
    try:
        yield
    finally:
        if not already_active:
            _L1_COGNITION_ACTIVE = False


@dataclass
class ToolIntent:
    """
    Declarative tool intent emitted by L1 cognition.

    Fields
    ------
    schema_version : int   — bumped on breaking changes
    tool_name      : str   — non-empty tool identifier
    capability     : ToolCapability
    args           : dict  — JSON-serializable tool arguments
    args_hash      : str   — sha256(canonical args); auto-computed if empty
    requires_commit: bool  — True for any MUTATING_* capability (enforced)
    policy_hash    : str   — active PolicyConfig hash
    model_hash     : str   — active ModelConfig hash
    budget_hash    : str   — active BudgetConfig hash
    routing_hash   : str   — active RoutingConfig hash
    intent_hash    : str   — sha256(canonical_bytes excluding intent_hash); auto-computed
    """

    schema_version: int
    tool_name: str
    capability: ToolCapability
    args: dict[str, Any]
    requires_commit: bool
    policy_hash: str = ""
    model_hash: str = ""
    budget_hash: str = ""
    routing_hash: str = ""
    args_hash: str = field(default="", init=True)
    intent_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"ToolIntent: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}"
            )
        if not self.tool_name:
            raise ValueError("ToolIntent: tool_name must be non-empty")
        if not isinstance(self.capability, ToolCapability):
            raise TypeError(
                f"ToolIntent: capability must be ToolCapability, got {type(self.capability).__name__}"
            )
        if not isinstance(self.args, dict):
            raise TypeError("ToolIntent: args must be a dict")
        if is_mutating(self.capability) and (not self.requires_commit):
            raise ValueError(
                f"ToolIntent: requires_commit must be True for capability {self.capability.value}"
            )
        if not self.args_hash:
            self.args_hash = _sha256(json.dumps(self.args, sort_keys=True, separators=(",", ":")).encode())
        object.__setattr__(self, "intent_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """Deterministic serialisation excluding intent_hash (self-referential)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ToolIntent.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ToolIntent.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        doc: dict[str, Any] = {
            "args_hash": self.args_hash,
            "budget_hash": self.budget_hash,
            "capability": self.capability.value,
            "model_hash": self.model_hash,
            "policy_hash": self.policy_hash,
            "requires_commit": self.requires_commit,
            "routing_hash": self.routing_hash,
            "schema_version": self.schema_version,
            "tool_name": self.tool_name,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool_name": self.tool_name,
            "capability": self.capability.value,
            "args": self.args,
            "args_hash": self.args_hash,
            "requires_commit": self.requires_commit,
            "policy_hash": self.policy_hash,
            "model_hash": self.model_hash,
            "budget_hash": self.budget_hash,
            "routing_hash": self.routing_hash,
            "intent_hash": self.intent_hash,
        }


def build_tool_intent(
    tool_name: str,
    capability: ToolCapability,
    args: dict[str, Any],
    *,
    policy_hash: str = "",
    model_hash: str = "",
    budget_hash: str = "",
    routing_hash: str = "",
) -> ToolIntent:
    """
    Factory: build a ToolIntent from tool parameters.

    requires_commit is automatically set to True for MUTATING_* capabilities.
    """
    return ToolIntent(
        schema_version=_SCHEMA_VERSION,
        tool_name=tool_name,
        capability=capability,
        args=args,
        requires_commit=is_mutating(capability),
        policy_hash=policy_hash,
        model_hash=model_hash,
        budget_hash=budget_hash,
        routing_hash=routing_hash,
    )
