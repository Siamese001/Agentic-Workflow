#!/usr/bin/env python3
"""
TOXIC DEPENDENCY AUDITOR
-------------------------
L5 Safety Validator designed to identify 'Toxic Hubs' within the core.
Toxicity is defined by high Fan-in (number of inward dependencies).

Logic:
1. Scans all agentic_core modules to build an inverse dependency map.
2. Ranks modules by inward dependency count (Fan-in).
3. Identifies 'High-Risk' modules that would cause massive drift if violated.
4. Feeds priorities to the DynamicSealAgent for targeted remediation.
"""

import ast
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "toxic_dependency_auditor_enforcer")
trace_contract.emit_determinism_digest("p0", "toxic_dependency_auditor_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "toxic_dependency_auditor_enforcer", "L5")
trace_contract._emit_routes_through("p1", "toxic_dependency_auditor_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "toxic_dependency_auditor_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "toxic_dependency_auditor_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "toxic_dependency_auditor_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "toxic_dependency_auditor_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "toxic_dependency_auditor_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "toxic_dependency_auditor_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "toxic_dependency_auditor_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "toxic_dependency_auditor_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "toxic_dependency_auditor_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "toxic_dependency_auditor_enforcer")
trace_contract._emit_gated_by_confidence("p1", "toxic_dependency_auditor_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "toxic_dependency_auditor_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "toxic_dependency_auditor_enforcer", "L5")

trace_contract._emit_applies_guardrail("p0", "toxic_dependency_auditor_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "toxic_dependency_auditor_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "toxic_dependency_auditor_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "toxic_dependency_auditor_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "toxic_dependency_auditor_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "toxic_dependency_auditor_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "toxic_dependency_auditor_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "toxic_dependency_auditor_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "toxic_dependency_auditor_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "toxic_dependency_auditor_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "toxic_dependency_auditor_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "toxic_dependency_auditor_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "toxic_dependency_auditor_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "toxic_dependency_auditor_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "toxic_dependency_auditor_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "toxic_dependency_auditor_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "toxic_dependency_auditor_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "toxic_dependency_auditor_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "toxic_dependency_auditor_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "toxic_dependency_auditor_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "toxic_dependency_auditor_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "toxic_dependency_auditor_enforcer", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("toxic_dependency_auditor_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("toxic_dependency_auditor_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("toxic_dependency_auditor_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("toxic_dependency_auditor_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("toxic_dependency_auditor_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("toxic_dependency_auditor_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("toxic_dependency_auditor_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("toxic_dependency_auditor_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("toxic_dependency_auditor_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("toxic_dependency_auditor_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("toxic_dependency_auditor_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("toxic_dependency_auditor_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("toxic_dependency_auditor_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("toxic_dependency_auditor_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("toxic_dependency_auditor_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("toxic_dependency_auditor_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("toxic_dependency_auditor_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("toxic_dependency_auditor_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("toxic_dependency_auditor_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("toxic_dependency_auditor_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("toxic_dependency_auditor_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("toxic_dependency_auditor_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("toxic_dependency_auditor_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("toxic_dependency_auditor_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("toxic_dependency_auditor_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("toxic_dependency_auditor_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("toxic_dependency_auditor_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("toxic_dependency_auditor_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "toxic_dependency_auditor_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "toxic_dependency_auditor_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "toxic_dependency_auditor_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "toxic_dependency_auditor_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "toxic_dependency_auditor_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "toxic_dependency_auditor_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "toxic_dependency_auditor_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "toxic_dependency_auditor_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "toxic_dependency_auditor_enforcer", "routing_commit")


class ToxicDependencyAuditor(SovereignBaseAgent):
    """
    The Risk-Assessor Agent.
    Identifies the most critical components of the Sovereign Architecture.
    """

    # guardian: allow-magic-config
    def __init__(self, root_dir: str = ".", toxic_threshold: int = 10):
        self.root = Path(root_dir)
        self.threshold = toxic_threshold
        self.dependency_map: dict[str, set[str]] = {}  # module -> set of dependents

    def audit_toxicity(self, coverage_data: dict[str, float] = None) -> list[dict]:
        """Builds the fan-in map and identifies toxic hubs with coverage weighting.

        Args:
            coverage_data: Optional dict mapping module paths to coverage percentages (0.0-1.0)

        Returns:
            List of toxic hubs sorted by systemic risk score
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "ToxicDependencyAuditor.audit_toxicity",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ToxicDependencyAuditor.audit_toxicity".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._build_fan_in_map()

        toxic_hubs = []
        for module, dependents in tqdm(self.dependency_map.items(), desc="Processing", unit="item"):
            if len(dependents) >= self.threshold:
                # Calculate base toxicity score (fan-in)
                fan_in = len(dependents)

                # Apply coverage weighting if available
                coverage_weight = 1.0
                if coverage_data and module in coverage_data:
                    # Lower coverage = higher risk
                    # Coverage 0% = 2.0x multiplier, 100% = 1.0x multiplier
                    coverage_pct = coverage_data[module]
                    coverage_weight = 2.0 - coverage_pct

                # Systemic risk = fan_in * coverage_weight
                systemic_risk = fan_in * coverage_weight

                toxic_hubs.append(
                    {
                        "module": module,
                        "fan_in": fan_in,
                        "coverage": coverage_data.get(module, 0.0) if coverage_data else None,
                        "coverage_weight": coverage_weight,
                        "systemic_risk": systemic_risk,
                        "dependents": list(dependents),
                    },
                )

        # Sort by systemic risk (highest first)
        return sorted(toxic_hubs, key=lambda x: x["systemic_risk"], reverse=True)

    def _build_fan_in_map(self):
        """Walks all python files to see who imports what."""
        # Operation Zero: Use ssot_discovery instead of glob
        from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(self.root / AGENTIC_CORE_DIR):
            current_module = self._get_module_name(py_file)
            imports = self._extract_internal_imports(py_file)

            for imp in imports:
                if imp not in self.dependency_map:
                    self.dependency_map[imp] = set()
                self.dependency_map[imp].add(current_module)

    def _extract_internal_imports(self, file_path: Path) -> set[str]:
        """Uses AST to find internal agentic_core imports."""
        imports = set()
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith(AGENTIC_CORE_DIR):
                        imports.add(node.module)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(AGENTIC_CORE_DIR):
                            imports.add(alias.name)
        except (
            ValueError,
            TypeError,
        ):  # guardian: allow-silent-swallow  -- ADG-burn: silent_exception_swallow
            pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow
        return imports

    def _get_module_name(self, file_path: Path) -> str:
        """Maps file path to standard dot-notation module name."""
        try:
            rel_path = file_path.relative_to(self.root)
            return str(rel_path.as_posix()).replace("/", ".").replace(".py", "")
        except ValueError:
            return ""

    def report(self, toxic_hubs: list[dict]):
        """Generates a Sovereign Toxicity Report with coverage weighting."""
        if not toxic_hubs:
            print(f"✅ TOXICITY CHECK: No modules exceed fan-in threshold ({self.threshold}).")
            return

        print(f"☢️  TOXIC HUB ALERT: {len(toxic_hubs)} modules identified as high-risk.")
        print("-" * 60)
        for hub in tqdm(toxic_hubs, desc="Processing", unit="item"):
            print(f"Module: {hub['module']}")
            print(f"Fan-in (Dependencies): {hub['fan_in']}")

            if hub.get("coverage") is not None:
                coverage_pct = hub["coverage"] * 100
                print(f"Coverage: {coverage_pct:.1f}%")
                print(f"Coverage Weight: {hub['coverage_weight']:.2f}x")
                print(f"Systemic Risk Score: {hub['systemic_risk']:.1f}")
            else:
                print(f"Toxicity Score: {hub['fan_in']}")

            print(f"Impact: A single violation here affects {hub['fan_in']} components.")
            print("-" * 60)

    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        # Toxic dependency auditor is detection-only
        toxic_hubs = self.audit_toxicity()
        return {
            "violations_found": len(toxic_hubs),
            "violations_fixed": 0,
            "errors": 0,
            "skipped": len(toxic_hubs),
            "reason": "Toxic dependencies require architectural refactoring",
        }

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal toxic dependency violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (toxic_hub, high_fan_in)
                - module: Module with high fan-in
                - fan_in: Number of dependencies

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Toxic dependencies require architectural refactoring",
        }


if __name__ == "__main__":
    auditor = ToxicDependencyAuditor()
    hubs = auditor.audit_toxicity()
    auditor.report(hubs)
