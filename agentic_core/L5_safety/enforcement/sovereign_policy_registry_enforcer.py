from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "sovereign_policy_registry_enforcer")
emit_determinism_digest("p0", "sovereign_policy_registry_enforcer")

_emit_dispatches_healing_run("p1", "sovereign_policy_registry_enforcer", "L5")
_emit_routes_through("p1", "sovereign_policy_registry_enforcer", "L5")
_emit_escalates_to_human("p1", "sovereign_policy_registry_enforcer", "L5")
_emit_reads_policy_state("p1", "sovereign_policy_registry_enforcer", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "sovereign_policy_registry_enforcer")
_emit_applies_guardrail("p0", "sovereign_policy_registry_enforcer", "p0_governance")
_emit_snapshots_state("p0", "sovereign_policy_registry_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "sovereign_policy_registry_enforcer", "execution_auth")
_emit_validates_capability("p2", "sovereign_policy_registry_enforcer", "capability_check")
_emit_routes_to_capability("p2", "sovereign_policy_registry_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_policy_registry_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_policy_registry_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_policy_registry_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_policy_registry_enforcer", "exec_output")
_emit_dispatches_agent("p3", "sovereign_policy_registry_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_policy_registry_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_policy_registry_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_policy_registry_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_policy_registry_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_policy_registry_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_policy_registry_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_policy_registry_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_policy_registry_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_policy_registry_enforcer", "eval_metric")
_emit_stores_embedding("p4", "sovereign_policy_registry_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_policy_registry_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_policy_registry_enforcer", "exec_snapshot_link")


class PolicySeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SovereignPolicy:
    id: str
    description: str
    severity: PolicySeverity
    enabled: bool = True


class SovereignPolicyRegistry:
    """
    The Immutable Constitution of the Agentic Core.
    Defines what IS allowed, independent of HOW it is checked.
    """

    DATA_LOCALITY = SovereignPolicy(
        id="GOV-001",
        description="L4 State must not leave local execution environment without explicit encryption.",
        severity=PolicySeverity.CRITICAL,
    )
    MAX_TOKENS_PER_TURN = SovereignPolicy(
        id="GOV-002", description="Single LLM turn must not exceed 32k tokens.", severity=PolicySeverity.HIGH
    )
    NO_PLAINTEXT_SECRETS = SovereignPolicy(
        id="GOV-003",
        description="No high-entropy strings (API keys) in logs or stdout.",
        severity=PolicySeverity.CRITICAL,
    )

    @classmethod
    def get_all(cls):
        return [v for k, v in cls.__dict__.items() if isinstance(v, SovereignPolicy)]
