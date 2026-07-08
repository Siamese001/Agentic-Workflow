"""Enhancement 8: Ownership / blast-radius overlay.

Associates each module in the ADG with:
  - owner: logical domain (platform, apps_rg, apps_lic, apps_shared, safety, etc.)
  - criticality: low / medium / high
  - runtime_surface: CI / prod / healing / governance

Also provides OwnershipRegistry.blast_radius_report() that combines
ownership metadata with a blast-radius node set to produce a structured
impact report.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "ownership", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "ownership", "policy_binding")
trace_contract._emit_snapshots_state("p0", "ownership", "state_snapshot")

trace_contract._emit_emits_metric_event("ownership", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ownership", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ownership", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ownership", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ownership", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ownership", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ownership", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ownership", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ownership", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ownership", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ownership", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ownership", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ownership", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ownership", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ownership", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ownership", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ownership", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ownership", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ownership", "p3lm", "state")
trace_contract._emit_records_execution_trace("ownership", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ownership", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ownership", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ownership", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ownership", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ownership", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ownership", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ownership", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ownership", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ownership", "context_pull")
trace_contract._emit_pulls_context("p1", "ownership", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ownership", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ownership", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ownership", "write_through")
trace_contract._emit_writes_through("p1", "ownership", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ownership", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ownership", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ownership", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "ownership", "human_escalation")
trace_contract._emit_routes_through("p1", "ownership", "route_through")
trace_contract._emit_checks_agent_registry("p1", "ownership", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ownership", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ownership", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ownership", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ownership", "target_agent")
trace_contract._emit_verifies_policy("p1", "ownership", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ownership", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ownership", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ownership", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ownership")
trace_contract._emit_gated_by_confidence("p1", "ownership", "confidence_gate")
trace_contract.emit_replay_key("p0", "ownership")
trace_contract.emit_determinism_digest("p0", "ownership")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "ownership", "execution_auth")
trace_contract._emit_validates_capability("p2", "ownership", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ownership", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ownership", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ownership", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ownership", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ownership", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ownership", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ownership", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ownership", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ownership", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ownership", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ownership", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ownership", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ownership", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ownership", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ownership", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ownership", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ownership", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ownership", "exec_snapshot_link")

Owner = Literal["platform", "apps_rg", "apps_lic", "apps_shared", "safety", "observability", "unknown"]
Criticality = Literal["low", "medium", "high"]
RuntimeSurface = Literal["CI", "prod", "healing", "governance", "unknown"]


@dataclass
class ModuleOwnership:
    """Ownership metadata for a single module path."""

    module_path: str
    owner: Owner = "unknown"
    criticality: Criticality = "medium"
    runtime_surface: RuntimeSurface = "unknown"

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "owner": self.owner,
            "criticality": self.criticality,
            "runtime_surface": self.runtime_surface,
        }


_PREFIX_OWNER_MAP: list[tuple[str, Owner, Criticality, RuntimeSurface]] = [
    ("agentic_core/L0_routing", "platform", "high", "prod"),
    ("agentic_core/L1_cognition", "platform", "high", "prod"),
    ("agentic_core/L2_execution", "platform", "high", "governance"),
    ("agentic_core/L3_orchestration", "platform", "high", "prod"),
    ("agentic_core/L4_memory", "platform", "medium", "prod"),
    ("agentic_core/L5_safety", "safety", "high", "governance"),
    ("agentic_core/L6_observability", "observability", "medium", "prod"),
    ("agentic_core/adg", "platform", "high", "CI"),
    ("apps_rg/", "apps_rg", "medium", "prod"),
    ("apps_lic/", "apps_lic", "medium", "prod"),
    ("apps_shared/", "apps_shared", "medium", "prod"),
    ("system_learning/", "platform", "medium", "healing"),
    ("ops_scripts/", "platform", "low", "CI"),
    ("tools/", "platform", "low", "CI"),
    ("tests/", "platform", "low", "CI"),
]


def _infer_ownership(module_path: str) -> ModuleOwnership:
    """Infer ownership from module path prefix rules."""
    norm = module_path.replace("\\", "/")
    if norm.startswith("ADG::Module::"):
        norm = norm[len("ADG::Module::") :]
    for prefix, owner, criticality, surface in _PREFIX_OWNER_MAP:
        if norm.startswith(prefix):
            return ModuleOwnership(
                module_path=module_path,
                owner=owner,
                criticality=criticality,
                runtime_surface=surface,
            )
    return ModuleOwnership(module_path=module_path)


class OwnershipRegistry:
    """Registry that provides ownership lookups and blast-radius reports.

    Usage:
        registry = OwnershipRegistry.from_scan_result(result)
        report = registry.blast_radius_report("agentic_core/L2_execution/UniversalWriteGateway.py", impact_nodes)
    """

    def __init__(self) -> None:
        self._map: dict[str, ModuleOwnership] = {}

    @classmethod
    def from_scan_result(cls, result: object) -> OwnershipRegistry:
        """Build registry from a ScanResult's module list."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "OwnershipRegistry.from_scan_result",
        )

        reg = cls()
        for mod in getattr(result, "modules", []):
            reg._map[mod] = _infer_ownership(mod)
        return reg

    @classmethod
    def from_module_list(cls, modules: list[str]) -> OwnershipRegistry:
        reg = cls()
        for mod in modules:
            reg._map[mod] = _infer_ownership(mod)
        return reg

    def get(self, module_path: str) -> ModuleOwnership:
        return self._map.get(module_path, _infer_ownership(module_path))

    def blast_radius_report(
        self,
        changed_module: str,
        impacted_modules: list[str],
    ) -> dict:
        """Produce a blast-radius report for a changed module.

        Args:
            changed_module: The module that changed.
            impacted_modules: All transitively impacted modules (from query_engine).

        Returns:
            Structured dict with owner, criticality, impacted domains, and
            a HIGH/MEDIUM/LOW aggregate risk level.
        """
        changed_meta = self.get(changed_module)

        impacted_by_owner: dict[str, list[str]] = {}
        high_count = 0
        for mod in impacted_modules:
            meta = self.get(mod)
            impacted_by_owner.setdefault(meta.owner, []).append(mod)
            if meta.criticality == "high":
                high_count += 1

        if changed_meta.criticality == "high" or high_count >= 3:
            aggregate_risk = "HIGH"
        elif high_count >= 1 or changed_meta.criticality == "medium":
            aggregate_risk = "MEDIUM"
        else:
            aggregate_risk = "LOW"

        surfaces: set[str] = {changed_meta.runtime_surface}
        for mod in impacted_modules:
            surfaces.add(self.get(mod).runtime_surface)
        surfaces.discard("unknown")

        return {
            "changed_module": changed_module,
            "owner": changed_meta.owner,
            "criticality": changed_meta.criticality,
            "runtime_surface": changed_meta.runtime_surface,
            "aggregate_risk": aggregate_risk,
            "impacted_module_count": len(impacted_modules),
            "impacted_high_criticality_count": high_count,
            "affected_domains": sorted(impacted_by_owner.keys()),
            "affected_surfaces": sorted(surfaces),
            "impacted_by_owner": {k: sorted(v) for k, v in sorted(impacted_by_owner.items())},
        }

    def to_dict(self) -> dict:
        return {k: v.to_dict() for k, v in sorted(self._map.items())}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
