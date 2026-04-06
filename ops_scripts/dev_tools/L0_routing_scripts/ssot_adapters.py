"""
SSOT Pipeline Adapters — Pure mapping layer for execute_ssot run_pipeline.

Each adapter class wraps one existing agent and maps its bespoke call surface
onto the four-method L2AgentProtocol (pre_commit / validate / execute / heal).

Rules enforced here:
- Adapters are PURE MAPPING only — no logic added, no agent internals touched.
- All agent imports are deferred (inside __init__) to avoid circular imports.
- pre_commit and validate MUST NOT receive ctx.heal=True; the orchestrator
  enforces this structurally via scan_ctx before calling the adapter.
- ArchGovAdapter stores _plan between execute and heal subphases; it is reset
  to None after heal completes to prevent state leakage across pipeline runs.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

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
    _emit_reads_through,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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
)

if TYPE_CHECKING:
    from agentic_core.L2_execution.protocol import SubphaseResult
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    emit_determinism_digest,
    emit_replay_key,
)

def _to_result(raw: Any, *, fixed: list[dict] | None = None) -> SubphaseResult:
    """Normalise an agent return dict into SubphaseResult.

    Agents return a variety of dict shapes. We extract violations where
    possible; anything else maps to an empty-violations clean result.
    """
    from agentic_core.L2_execution.protocol import SubphaseResult

    if isinstance(raw, SubphaseResult):
        return raw
    violations: list[dict] = []
    mutations: list[dict] = []
    if isinstance(raw, dict):
        for key in ("violations", "violations_found", "issues", "errors"):
            val = raw.get(key)
            if isinstance(val, list):
                violations = [v if isinstance(v, dict) else {"raw": v} for v in val]
                break
        for key in ("fixed", "actions_taken", "healed", "changes"):
            val = raw.get(key)
            if isinstance(val, list):
                mutations = [v if isinstance(v, dict) else {"raw": v} for v in val]
                break
    if fixed is not None:
        mutations = fixed
    return SubphaseResult(violations=violations, fixed=mutations)


def _noop() -> SubphaseResult:
    """Return a clean no-op result (for agents that don't support a subphase)."""
    from agentic_core.L2_execution.protocol import SubphaseResult

    return SubphaseResult()


class ReconcilerAdapter:
    """Adapter for FilesystemSSOTReconcilerAgent (roster key: 'reconciler')."""

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    def pre_commit(self, territory: str, ctx: Any) -> SubphaseResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ReconcilerAdapter.pre_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        raw = self._agent.detect_root_drift()
        return _to_result(raw)

    def validate(self, territory: str, ctx: Any) -> SubphaseResult:
        ok, raw = self._agent.run_ci_verification_sync()
        result = _to_result(raw)
        if not ok and (not result.violations):
            result.violations = [{"type": "ci_verification_failed", "detail": str(raw)}]
        return result

    def execute(self, territory: str, ctx: Any) -> SubphaseResult:
        dry_run = not getattr(ctx, "heal", False)
        raw = self._agent.heal_repository(dry_run=dry_run)
        return _to_result(raw)

    def heal(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.heal_repository(dry_run=False, execute=True)
        return _to_result(raw)


class LocationAdapter:
    """Adapter for LocationAgent (roster key: 'location')."""

    def __init__(self, agent: Any) -> None:
        self._agent = agent
        self._scan_violations: list[dict] = []

    def pre_commit(self, territory: str, ctx: Any) -> SubphaseResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "LocationAdapter.pre_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        raw = self._agent.run(files=None)
        result = _to_result(raw)
        self._scan_violations = result.violations
        return result

    def validate(self, territory: str, ctx: Any) -> SubphaseResult:
        from agentic_core.L2_execution.protocol import SubphaseResult

        return SubphaseResult(violations=list(self._scan_violations))

    def execute(self, territory: str, ctx: Any) -> SubphaseResult:
        auto_approve = getattr(ctx, "auto_approve", True)
        raw = self._agent.heal_violations(self._scan_violations, auto_approve=auto_approve)
        return _to_result(raw)

    def heal(self, territory: str, ctx: Any) -> SubphaseResult:
        auto_approve = getattr(ctx, "auto_approve", True)
        raw = self._agent.heal_violations(self._scan_violations, auto_approve=auto_approve)
        return _to_result(raw)


class FileClassAdapter:
    """Adapter for FileClassificationAgent (roster key: 'file_classification')."""

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    def pre_commit(self, territory: str, ctx: Any) -> SubphaseResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "FileClassAdapter.pre_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        raw = self._agent.run()
        return _to_result(raw)

    def validate(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.run()
        return _to_result(raw)

    def execute(self, territory: str, ctx: Any) -> SubphaseResult:
        dry_run = not getattr(ctx, "heal", False)
        raw = self._agent.heal_repository(dry_run=dry_run)
        return _to_result(raw)

    def heal(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.heal_repository(dry_run=False, execute=True)
        return _to_result(raw)


class HierarchyAdapter:
    """Adapter for HierarchyAgent (roster key: 'hierarchy')."""

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    def pre_commit(self, territory: str, ctx: Any) -> SubphaseResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "HierarchyAdapter.pre_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        raw = self._agent.scan_root_violations(target_territory=territory)
        return _to_result(raw)

    def validate(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.scan_root_violations(target_territory=territory)
        return _to_result(raw)

    def execute(self, territory: str, ctx: Any) -> SubphaseResult:
        dry_run = not getattr(ctx, "heal", False)
        raw = self._agent.heal_hierarchy(dry_run=dry_run, target_territory=territory)
        return _to_result(raw)

    def heal(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.heal_hierarchy(dry_run=False, target_territory=territory)
        return _to_result(raw)


class ArchGovAdapter:
    """Adapter for ArchitectureGovernorAgent (roster key: 'arch_governor').

    Intermediate state: _plan is set by execute(), consumed by heal(), then
    reset to None. This is deterministic because execute always precedes heal
    in the PIPELINE_SUBPHASES ordering enforced by run_pipeline.
    """

    def __init__(self, agent: Any) -> None:
        self._agent = agent
        self._audit_report: dict | None = None
        self._plan: dict | None = None

    def pre_commit(self, territory: str, ctx: Any) -> SubphaseResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ArchGovAdapter.pre_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        raw = self._agent.run_audit(target_territories=[territory])
        self._audit_report = raw if isinstance(raw, dict) else {}
        return _to_result(raw)

    def validate(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.comprehensive_territory_audit(
            target_territories=[territory], check_layer_boundaries=True
        )
        self._audit_report = raw if isinstance(raw, dict) else {}
        return _to_result(raw)

    def execute(self, territory: str, ctx: Any) -> SubphaseResult:
        report = self._audit_report or {}
        self._plan = self._agent.generate_healing_plan(report)
        dry_run = not getattr(ctx, "heal", False)
        raw = self._agent.heal_repository(dry_run=dry_run)
        return _to_result(raw)

    def heal(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.heal_repository(dry_run=False, execute=True)
        self._plan = None
        return _to_result(raw)


class GravityAdapter:
    """Adapter for GravityLeakRepairAgent (roster key: 'gravity_repair')."""

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    def pre_commit(self, territory: str, ctx: Any) -> SubphaseResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "GravityAdapter.pre_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        raw = self._agent.heal_repository(dry_run=True)
        return _to_result(raw)

    def validate(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.heal_repository(dry_run=True)
        return _to_result(raw)

    def execute(self, territory: str, ctx: Any) -> SubphaseResult:
        dry_run = not getattr(ctx, "heal", False)
        raw = self._agent.heal_repository(dry_run=dry_run)
        return _to_result(raw)

    def heal(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.heal_repository(dry_run=False, execute=True)
        return _to_result(raw)


class SysArchAdapter:
    """Adapter for SystemArchitectAgent (roster key: 'system_architect').

    SystemArchitectAgent explicitly returns manual_required for mutations.
    execute and heal are no-ops by design.
    """

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    def pre_commit(self, territory: str, ctx: Any) -> SubphaseResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "SysArchAdapter.pre_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        raw = self._agent.validate_core_architecture(f"agentic_core/{territory}")
        return _to_result(raw)

    def validate(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.validate_core_architecture(f"agentic_core/{territory}")
        return _to_result(raw)

    def execute(self, territory: str, ctx: Any) -> SubphaseResult:
        return _noop()

    def heal(self, territory: str, ctx: Any) -> SubphaseResult:
        return _noop()


class ObsProbeAdapter:
    """Adapter for ObservabilityProbeExecutorAgent (roster key: 'observability_probe').

    Observability is read-only; execute and heal are no-ops.
    """

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    def pre_commit(self, territory: str, ctx: Any) -> SubphaseResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ObsProbeAdapter.pre_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        raw = self._agent.scan_violations(target_territory=territory)
        return _to_result(raw)

    def validate(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.scan_violations(target_territory=territory)
        return _to_result(raw)

    def execute(self, territory: str, ctx: Any) -> SubphaseResult:
        return _noop()

    def heal(self, territory: str, ctx: Any) -> SubphaseResult:
        return _noop()


class RootHygieneAdapter:
    """Adapter for RootHygieneAgent (roster key: 'root_hygiene').

    Previously dead code — violations were read from state that was never
    written. Now invoked directly via this adapter.
    """

    def __init__(self, agent: Any) -> None:
        self._agent = agent

    def pre_commit(self, territory: str, ctx: Any) -> SubphaseResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "RootHygieneAdapter.pre_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        raw = self._agent.scan_root_violations()
        return _to_result(raw)

    def validate(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.run()
        return _to_result(raw)

    def execute(self, territory: str, ctx: Any) -> SubphaseResult:
        dry_run = not getattr(ctx, "heal", False)
        raw = self._agent.heal_repository(dry_run=dry_run)
        return _to_result(raw)

    def heal(self, territory: str, ctx: Any) -> SubphaseResult:
        raw = self._agent.heal_repository(dry_run=False, execute=True)
        return _to_result(raw)


ADAPTER_REGISTRY: dict[str, type] = {
    "reconciler": ReconcilerAdapter,
    "location": LocationAdapter,
    "file_classification": FileClassAdapter,
    "hierarchy": HierarchyAdapter,
    "arch_governor": ArchGovAdapter,
    "gravity_repair": GravityAdapter,
    "system_architect": SysArchAdapter,
    "observability_probe": ObsProbeAdapter,
    "root_hygiene": RootHygieneAdapter,
}


def build_adapters(agents: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """Instantiate agents and wrap each in the appropriate adapter.

    Args:
        agents:       Dict mapping roster key -> agent class (as in _legacy_main).
        project_root: Passed to agent constructors.

    Returns:
        Dict mapping roster key -> adapter instance implementing L2AgentProtocol.
    """
    adapters: dict[str, Any] = {}
    for key, adapter_cls in ADAPTER_REGISTRY.items():
        agent_cls = agents.get(key) or agents.get(
            "conversational_repair" if key == "observability_probe" else key
        )
        if agent_cls is None:
            continue
        try:
            agent_instance = agent_cls(project_root=project_root)
        except TypeError:
            try:
                agent_instance = agent_cls()
            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                continue
        adapters[key] = adapter_cls(agent_instance)
    return adapters
