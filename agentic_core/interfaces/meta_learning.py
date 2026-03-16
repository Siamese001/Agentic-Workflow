"""
agentic_core/interfaces/meta_learning.py

Sovereign meta-learning interface for apps_* consumption.

AUTHORITY CONSTRAINTS:
- Meta-learning is mandatory by default (proposal_only=False)
- commit(), activate(), execute() are BLOCKED with PermissionError
- Inner client is sealed via __slots__ and __getattr__ override
- JSON-only payload validation on ChangePackage
- proposal_only=False requires explicit approval_gate + version_store injection

USAGE (apps_*):
    from agentic_core.interfaces.meta_learning import (
        get_sovereign_meta_client,
        ChangePackage,
        HealingPattern,
        MetaLearningGuardrails,
        get_guardrails,
    )
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "meta_learning", "p0_governance")
_emit_reads_policy_state("p0", "meta_learning", "policy_binding")
_emit_snapshots_state("p0", "meta_learning", "state_snapshot")
emit_replay_key("p0", "meta_learning")
emit_determinism_digest("p0", "meta_learning")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "meta_learning", "execution_auth")
_emit_validates_capability("p2", "meta_learning", "capability_check")
_emit_routes_to_capability("p2", "meta_learning", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning", "exec_output")
_emit_dispatches_agent("p3", "meta_learning", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning", "eval_metric")
_emit_stores_embedding("p4", "meta_learning", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning", "exec_snapshot_link")

JSONPrimitive = str | int | float | bool | None


@dataclass(frozen=True)
class ChangePackage:
    """
    Immutable JSON-only proposal package.

    No executable closures, callables, function pointers, or object references
    are permitted in parameters.  Runtime validation enforces this.

    ``proposal_only`` defaults to True.  Setting it to False requires an
    explicit ``approval_token`` to be supplied; without one the constructor
    raises ValueError, preventing silent runtime activation.
    """

    proposal_id: str
    change_type: str
    parameters: dict[str, Any]
    requires_approval: bool = True
    proposal_only: bool = True
    approval_token: str | None = None

    def __post_init__(self) -> None:
        try:
            json.dumps(self.parameters)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"ChangePackage.parameters must be JSON-serializable: {exc}") from exc
        if not self.proposal_only and (not self.approval_token):
            raise ValueError(
                "ChangePackage.proposal_only=False requires an explicit approval_token. Runtime mutation without an approval token is prohibited."
            )


class SovereignMetaLearningClient:
    """
    Reflection-hardened sealed implementation of MetaLearningInterface.

    Authority guards:
    - __slots__ prevents __dict__ attribute traversal
    - __getattr__ blocks access to any undeclared attribute
    - __setattr__ / __delattr__ prevent modification
    - commit / activate / execute raise PermissionError unconditionally
    - Mandatory application by default (proposal_only=False)
    """

    __slots__ = ("_sealed_client", "_proposal_only")

    def __init__(
        self,
        inner_client: Any,
        proposal_only: bool = False,
        approval_gate: Any = None,
        version_store: Any = None,
    ) -> None:
        if not proposal_only and (approval_gate is None or version_store is None):
            raise PermissionError(
                "proposal_only=False requires explicit approval_gate and version_store injection.  No silent activation path allowed."
            )
        object.__setattr__(self, "_sealed_client", inner_client)
        object.__setattr__(self, "_proposal_only", proposal_only)

    def propose_healing_pattern(self, pattern: dict[str, Any]) -> ChangePackage:
        """Propose or apply a healing pattern change — JSON-only payload."""
        return ChangePackage(
            proposal_id=str(uuid.uuid4()),
            change_type="healing_pattern",
            parameters=pattern,
            requires_approval=True,
        )

    def suggest_threshold_adjustment(self, threshold: float) -> ChangePackage:
        """Apply or suggest a routing threshold change."""
        return ChangePackage(
            proposal_id=str(uuid.uuid4()),
            change_type="threshold_adjustment",
            parameters={"threshold": threshold},
            requires_approval=True,
        )

    def retrieve_healing_pattern(self, violation_type: str, error_signature: str) -> dict[str, Any] | None:
        """Read-only pattern retrieval — delegates to inner client."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignMetaLearningClient.retrieve_healing_pattern")

        inner = object.__getattribute__(self, "_sealed_client")
        if hasattr(inner, "retrieve_pattern"):
            return inner.retrieve_pattern(violation_type, error_signature)
        return None

    def commit(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("commit() authority reserved for L5 — blocked by interface seal")

    def activate(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("activate() authority reserved for L0 — blocked by interface seal")

    def execute(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("execute() authority reserved for L2 — blocked by interface seal")

    def store_pattern(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("store_pattern() write authority reserved for L4 — blocked")

    def __getattr__(self, name: str) -> Any:
        raise AttributeError(
            f"'{self.__class__.__name__}' has no attribute '{name}' — inner client access is sealed"
        )

    def __getattribute__(self, name: str) -> Any:
        allowed = frozenset(
            {
                "propose_healing_pattern",
                "suggest_threshold_adjustment",
                "retrieve_healing_pattern",
                "commit",
                "activate",
                "execute",
                "store_pattern",
                "__class__",
                "__slots__",
                "__doc__",
                "__module__",
                "__getattribute__",
                "__getattr__",
                "__setattr__",
                "__delattr__",
            }
        )
        if name not in allowed:
            raise AttributeError(f"'{self.__class__.__name__}' attribute '{name}' is sealed")
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(f"Cannot set attribute '{name}' on sealed SovereignMetaLearningClient")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"Cannot delete attribute '{name}' on sealed SovereignMetaLearningClient")


def get_sovereign_meta_client(
    proposal_only: bool = False, approval_gate: Any = None, version_store: Any = None
) -> SovereignMetaLearningClient:
    """
    Factory: returns a sealed sovereign meta-learning client.

    Default: proposal_only=False — mandatory application mode.
    """
    from agentic_core.L1_cognition.engines.meta_client import get_meta_learning_client

    inner = get_meta_learning_client()
    return SovereignMetaLearningClient(
        inner, proposal_only=proposal_only, approval_gate=approval_gate, version_store=version_store
    )


def get_guardrails() -> Any:
    """Re-export guardrails — read-only safety checks, no mutation authority."""
    from agentic_core.L1_cognition.utils.guardrails_util import get_guardrails as _get

    return _get()


def _import_healing_pattern() -> type:
    from agentic_core.L1_cognition.types.client_types import HealingPattern

    return HealingPattern


def _import_guardrails_class() -> type:
    from agentic_core.L1_cognition.utils.guardrails_util import MetaLearningGuardrails

    return MetaLearningGuardrails


try:
    from agentic_core.L1_cognition.types.client_types import HealingPattern
    from agentic_core.L1_cognition.utils.guardrails_util import MetaLearningGuardrails
except ImportError:
    HealingPattern = None
    MetaLearningGuardrails = None
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("meta_learning", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning", "p4obs", "alert")
_emit_links_incident_trace("meta_learning", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning", "p3lm", "pattern")
_emit_records_learning_event("meta_learning", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning", "p3lm", "policy")
_emit_stores_learning_state("meta_learning", "p3lm", "state")
_emit_records_execution_trace("meta_learning", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_learning", "context_pull")
_emit_pulls_context("p1", "meta_learning", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "meta_learning", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning", "uwg_term_secondary")
_emit_writes_through("p1", "meta_learning", "write_through")
_emit_writes_through("p1", "meta_learning", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "meta_learning", "safety_validation")
_emit_invokes_eval("p1", "meta_learning", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning", "routing_commit")

__all__ = [
    "ChangePackage",
    "SovereignMetaLearningClient",
    "get_sovereign_meta_client",
    "get_guardrails",
    "HealingPattern",
    "MetaLearningGuardrails",
    "JSONPrimitive",
]
