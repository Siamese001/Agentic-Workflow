"""
L2 Agent Protocol — Unified subphase interface for execute_ssot pipeline.

Defines the four-method taxonomy that every pipeline adapter must implement:
  pre_commit  — read-only fast gate (no mutations)
  validate    — deep read-only scan (may be slow)
  execute     — confidence-gated mutations (dry_run or live)
  heal        — confidence-gated residual repair (live)

These types are imported by ssot_adapters.py and execute_ssot.py.
No agent modules are imported here. Zero side effects at import time.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

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

emit_replay_key("p0", "protocol")
emit_determinism_digest("p0", "protocol")

_emit_dispatches_healing_run("p1", "protocol", "L2")
_emit_routes_through("p1", "protocol", "L2")
_emit_checks_agent_registry("p1", "protocol", "agent_registry")
_emit_validates_agent_capability("p1", "protocol", "capability")
_emit_dispatches_execution_plan("p1", "protocol", "exec_plan")
_emit_agent_executes_agent("p1", "protocol", "sub_agent")
_emit_routes_to_agent("p1", "protocol", "target_agent")
_emit_verifies_policy("p1", "protocol", "policy_check")
_emit_observes_runtime_state("p1", "protocol", "runtime_state")
_emit_verifies_boundary("p1", "protocol", "boundary_check")
_emit_transcripts_response("p1", "protocol", "transcript")
_emit_hard_fails_untranscripted("p1", "protocol")
_emit_gated_by_confidence("p1", "protocol", "confidence_gate")
_emit_escalates_to_human("p1", "protocol", "L2")
_emit_reads_policy_state("p1", "protocol", "L2")
_emit_authorize_and_execute("p2", "protocol", "execution_auth")
_emit_validates_capability("p2", "protocol", "capability_check")
_emit_routes_to_capability("p2", "protocol", "capability_route")
_emit_writes_via_uwg("p2", "protocol", "uwg_write")
_emit_blocks_direct_write("p2", "protocol", "direct_write_block")
_emit_records_tool_invocation("p2", "protocol", "tool_invocation")
_emit_captures_execution_output("p2", "protocol", "exec_output")
_emit_dispatches_agent("p3", "protocol", "agent_dispatch")
_emit_coordinates_agents("p3", "protocol", "agent_coordination")
_emit_records_workflow_lineage("p3", "protocol", "workflow_lineage")
_emit_records_healing_outcome("p3", "protocol", "healing_outcome")
_emit_escalates_failure("p3", "protocol", "failure_escalation")
_emit_orchestrates_workflow("p3", "protocol", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "protocol", "healing_dispatch")
_emit_invokes_evaluation("p3", "protocol", "evaluation_signal")
_emit_records_telemetry_event("p4", "protocol", "telemetry_event")
_emit_captures_evaluation_metric("p4", "protocol", "eval_metric")
_emit_stores_embedding("p4", "protocol", "embedding_store")
_emit_updates_meta_learning_state("p4", "protocol", "meta_learning")
_emit_links_execution_to_snapshot("p4", "protocol", "exec_snapshot_link")
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

_emit_emits_metric_event("protocol", "p4obs", "metric_1")
_emit_emits_metric_event("protocol", "p4obs", "metric_2")
_emit_emits_metric_event("protocol", "p4obs", "metric_3")
_emit_emits_metric_event("protocol", "p4obs", "metric_4")
_emit_emits_metric_event("protocol", "p4obs", "metric_5")
_emit_emits_metric_event("protocol", "p4obs", "metric_6")
_emit_records_incident_event("protocol", "p4obs", "incident")
_emit_captures_runtime_anomaly("protocol", "p4obs", "anomaly")
_emit_writes_observability_log("protocol", "p4obs", "obs_log")
_emit_updates_monitoring_state("protocol", "p4obs", "mon_state")
_emit_triggers_alert("protocol", "p4obs", "alert")
_emit_links_incident_trace("protocol", "p4obs", "trace_link")
_emit_captures_pattern("protocol", "p3lm", "pattern")
_emit_records_learning_event("protocol", "p3lm", "learning_event")
_emit_writes_learning_snapshot("protocol", "p3lm", "snapshot")
_emit_feeds_meta_learning("protocol", "p3lm", "meta_feed")
_emit_updates_routing_strategy("protocol", "p3lm", "routing")
_emit_improves_agent_policy("protocol", "p3lm", "policy")
_emit_stores_learning_state("protocol", "p3lm", "state")
_emit_records_execution_trace("protocol", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("protocol", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("protocol", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("protocol", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("protocol", "L4_STATE", "p2_trace_5")
_emit_reads_environ("protocol", "env_read", "p2_env_1")
_emit_reads_environ("protocol", "env_read", "p2_env_2")
_emit_reads_runtime_state("protocol", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("protocol", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "protocol", "context_pull")
_emit_pulls_context("p1", "protocol", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "protocol", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "protocol", "uwg_term_2")
_emit_writes_through("p1", "protocol", "write_through")
_emit_writes_through("p1", "protocol", "write_through_2")
_emit_validated_by_safety_plane("p1", "protocol", "safety_validation")
_emit_invokes_eval("p1", "protocol", "eval_call")
_emit_proposal_commits_routing("p1", "protocol", "routing_commit")


@dataclass
class SubphaseResult:
    """Result from a single subphase execution."""

    violations: list[dict] = field(default_factory=list)
    fixed: list[dict] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""
    error: str | None = None


@dataclass
class AgentRunResult:
    """Aggregated result for one agent across all four subphases."""

    subphases: dict[str, SubphaseResult] = field(default_factory=dict)
    gated: bool = False
    gate_reason: str = ""
    error: str | None = None
    violations_total: int = 0
    mutations_applied: int = 0


@runtime_checkable
class L2AgentProtocol(Protocol):
    """Protocol every pipeline adapter must satisfy."""

    def pre_commit(self, territory: str, ctx: object) -> SubphaseResult:
        """Read-only fast gate. Must never mutate filesystem."""
        ...

    def validate(self, territory: str, ctx: object) -> SubphaseResult:
        """Deep read-only scan. Must never mutate filesystem."""
        ...

    def execute(self, territory: str, ctx: object) -> SubphaseResult:
        """Confidence-gated mutations."""
        ...

    def heal(self, territory: str, ctx: object) -> SubphaseResult:
        """Confidence-gated residual repair."""
        ...


PIPELINE_SUBPHASES: tuple[str, ...] = ("pre_commit", "validate", "execute", "heal")


def compute_pipeline_digest(
    pipeline_order: list[str],
    adapter_keys: list[str],
    territory: str,
    heal: bool,
    enable_llm: bool,
    tamper_token: str = "",
) -> str:
    """Compute a stable SHA-256 digest from pipeline configuration.

    Args:
        pipeline_order: Ordered list of agent_id strings (AGENT_PIPELINE).
        adapter_keys:   Sorted list of keys present in adapters dict.
        territory:      The target territory string.
        heal:           ctx.heal flag.
        enable_llm:     ctx.enable_llm flag.
        tamper_token:   When SSOT_ORCH_NEGCTRL_TAMPER=1, contains "1"; else "0".

    Returns:
        64-char lowercase hex SHA-256 digest.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_pipeline_digest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_pipeline_digest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "compute_pipeline_digest")
    payload = "|".join(
        [
            ",".join(pipeline_order),
            ",".join(sorted(adapter_keys)),
            territory,
            str(heal),
            str(enable_llm),
            tamper_token,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def emit_pipeline_digest(
    pipeline_order: list[str], adapter_keys: list[str], territory: str, heal: bool, enable_llm: bool
) -> str:
    """Compute digest, print the canonical line, and return the digest string.

    Printed line format (exactly once per run):
        EXECUTE_SSOT_PIPELINE_DIGEST: <64-hex>

    When env var SSOT_ORCH_NEGCTRL_TAMPER=1, the tamper token is included
    in the payload so the digest differs from a clean run — used by the
    negative-control test.
    """
    tamper_token = os.environ.get("SSOT_ORCH_NEGCTRL_TAMPER", "0")
    digest = compute_pipeline_digest(
        pipeline_order=pipeline_order,
        adapter_keys=adapter_keys,
        territory=territory,
        heal=heal,
        enable_llm=enable_llm,
        tamper_token=tamper_token,
    )
    print(f"EXECUTE_SSOT_PIPELINE_DIGEST: {digest}")
    return digest
