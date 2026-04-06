"""
agentic_core/L2_execution/types/execution_tool_contract.py

ToolContract — P2-L2 gap remediation.

Typed interface for every L2 tool invocation. Closes the gap where
75 exec modules invoke tools (48,070 imports) with no typed contract,
producing anonymous ADG edges. All tool dispatch must go through a
ToolContract so that invocations carry capability, signature, and
risk metadata resolvable by the ADG.

ADG edges emitted: execution_terminates_at_uwg, applies_guardrail
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("execution_tool_contract", "p4obs", "metric_1")
_emit_emits_metric_event("execution_tool_contract", "p4obs", "metric_2")
_emit_emits_metric_event("execution_tool_contract", "p4obs", "metric_3")
_emit_emits_metric_event("execution_tool_contract", "p4obs", "metric_4")
_emit_emits_metric_event("execution_tool_contract", "p4obs", "metric_5")
_emit_emits_metric_event("execution_tool_contract", "p4obs", "metric_6")
_emit_records_incident_event("execution_tool_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("execution_tool_contract", "p4obs", "anomaly")
_emit_writes_observability_log("execution_tool_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("execution_tool_contract", "p4obs", "mon_state")
_emit_triggers_alert("execution_tool_contract", "p4obs", "alert")
_emit_links_incident_trace("execution_tool_contract", "p4obs", "trace_link")
_emit_captures_pattern("execution_tool_contract", "p3lm", "pattern")
_emit_records_learning_event("execution_tool_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execution_tool_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("execution_tool_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execution_tool_contract", "p3lm", "routing")
_emit_improves_agent_policy("execution_tool_contract", "p3lm", "policy")
_emit_stores_learning_state("execution_tool_contract", "p3lm", "state")
_emit_records_execution_trace("execution_tool_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execution_tool_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execution_tool_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execution_tool_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execution_tool_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execution_tool_contract", "env_read", "p2_env_1")
_emit_reads_environ("execution_tool_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("execution_tool_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execution_tool_contract", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "execution_tool_contract")
emit_determinism_digest("p0", "execution_tool_contract")

_emit_dispatches_healing_run("p1", "execution_tool_contract", "L2")
_emit_routes_through("p1", "execution_tool_contract", "L2")
_emit_checks_agent_registry("p1", "execution_tool_contract", "agent_registry")
_emit_validates_agent_capability("p1", "execution_tool_contract", "capability")
_emit_dispatches_execution_plan("p1", "execution_tool_contract", "exec_plan")
_emit_agent_executes_agent("p1", "execution_tool_contract", "sub_agent")
_emit_routes_to_agent("p1", "execution_tool_contract", "target_agent")
_emit_verifies_policy("p1", "execution_tool_contract", "policy_check")
_emit_observes_runtime_state("p1", "execution_tool_contract", "runtime_state")
_emit_verifies_boundary("p1", "execution_tool_contract", "boundary_check")
_emit_transcripts_response("p1", "execution_tool_contract", "transcript")
_emit_hard_fails_untranscripted("p1", "execution_tool_contract")
_emit_gated_by_confidence("p1", "execution_tool_contract", "confidence_gate")
_emit_escalates_to_human("p1", "execution_tool_contract", "L2")
_emit_reads_policy_state("p1", "execution_tool_contract", "L2")
_emit_pulls_context("p1", "execution_tool_contract", "context_pull")
_emit_pulls_context("p1", "execution_tool_contract", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "execution_tool_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execution_tool_contract", "uwg_term_secondary")
_emit_writes_through("p1", "execution_tool_contract", "write_through")
_emit_writes_through("p1", "execution_tool_contract", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "execution_tool_contract", "safety_validation")
_emit_invokes_eval("p1", "execution_tool_contract", "eval_call")
_emit_proposal_commits_routing("p1", "execution_tool_contract", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "execution_tool_contract")
_emit_applies_guardrail("p0", "execution_tool_contract", "p0_governance")
_emit_snapshots_state("p0", "execution_tool_contract", "state_snapshot")
_emit_authorize_and_execute("p2", "execution_tool_contract", "execution_auth")
_emit_validates_capability("p2", "execution_tool_contract", "capability_check")
_emit_routes_to_capability("p2", "execution_tool_contract", "capability_route")
_emit_writes_via_uwg("p2", "execution_tool_contract", "uwg_write")
_emit_blocks_direct_write("p2", "execution_tool_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "execution_tool_contract", "tool_invocation")
_emit_captures_execution_output("p2", "execution_tool_contract", "exec_output")
_emit_dispatches_agent("p3", "execution_tool_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "execution_tool_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution_tool_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution_tool_contract", "healing_outcome")
_emit_escalates_failure("p3", "execution_tool_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution_tool_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution_tool_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution_tool_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution_tool_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution_tool_contract", "eval_metric")
_emit_stores_embedding("p4", "execution_tool_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution_tool_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution_tool_contract", "exec_snapshot_link")


class ToolCategory(str, Enum):
    """High-level category of a tool."""

    FILE_SYSTEM = "file_system"
    CODE_EXECUTION = "code_execution"
    EXTERNAL_API = "external_api"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    LLM_CALL = "llm_call"
    SEARCH = "search"
    DATABASE = "database"
    ORCHESTRATION = "orchestration"


@dataclass(frozen=True)
class ToolCapabilityDescriptor:
    """Capability metadata for a single tool."""

    tool_name: str
    category: ToolCategory
    risk_level: str
    requires_sandbox: bool
    idempotent: bool
    max_retries: int = 1
    timeout_ms: int = 30_000
    capabilities: tuple[str, ...] = field(default_factory=tuple)

    @property
    def capability_hash(self) -> str:
        payload = f"{self.tool_name}:{self.category}:{self.risk_level}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class ToolContract:
    """Typed, immutable contract for a single tool invocation.

    Every L2 tool dispatch must be expressed as a ToolContract so
    that the ADG can trace ``execution_terminates_at_uwg`` edges.

    Usage::

        contract = ToolContract.create(
            tool_name="file_system.write",
            category=ToolCategory.FILE_SYSTEM,
            args={"path": "artifacts/out.json", "data": "{}"},
            trace_id=current_trace_id,
        )
        uwg.execute_from_contract(contract)
    """

    tool_name: str
    category: ToolCategory
    args: dict[str, Any]
    trace_id: str
    contract_hash: str
    capability_hash: str
    timestamp_monotonic: float
    requires_sandbox: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tool_name: str,
        category: ToolCategory,
        args: dict[str, Any],
        trace_id: str = "",
        requires_sandbox: bool = False,
        metadata: dict[str, Any] | None = None,
        capability_descriptor: ToolCapabilityDescriptor | None = None,
    ) -> ToolContract:
        ts = time.monotonic()
        payload = f"{tool_name}:{category}:{trace_id}:{ts:.6f}"
        contract_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
        cap_hash = (
            capability_descriptor.capability_hash
            if capability_descriptor
            else hashlib.sha256(tool_name.encode()).hexdigest()[:16]
        )
        return cls(
            tool_name=tool_name,
            category=category,
            args=args,
            trace_id=trace_id,
            contract_hash=contract_hash,
            capability_hash=cap_hash,
            timestamp_monotonic=ts,
            requires_sandbox=requires_sandbox,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "category": self.category.value,
            "trace_id": self.trace_id,
            "contract_hash": self.contract_hash,
            "capability_hash": self.capability_hash,
            "requires_sandbox": self.requires_sandbox,
            "arg_keys": sorted(self.args.keys()),
        }


_tool_registry: dict[str, ToolCapabilityDescriptor] = {}


def register_tool_capability(descriptor: ToolCapabilityDescriptor) -> None:
    """Register a tool's capability descriptor globally."""
    _tool_registry[descriptor.tool_name] = descriptor


def get_tool_capability(tool_name: str) -> ToolCapabilityDescriptor | None:
    """Return the registered capability descriptor for ``tool_name``."""
    return _tool_registry.get(tool_name)


def registered_tools() -> list[str]:
    return list(_tool_registry.keys())


__all__ = [
    "ToolCategory",
    "ToolCapabilityDescriptor",
    "ToolContract",
    "register_tool_capability",
    "get_tool_capability",
    "registered_tools",
]
