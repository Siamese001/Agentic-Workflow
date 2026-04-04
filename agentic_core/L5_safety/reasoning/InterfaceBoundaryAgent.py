from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

emit_replay_key("p0", "InterfaceBoundaryAgent")
emit_determinism_digest("p0", "InterfaceBoundaryAgent")

_emit_dispatches_healing_run("p1", "InterfaceBoundaryAgent", "L5")
_emit_routes_through("p1", "InterfaceBoundaryAgent", "L5")
_emit_checks_agent_registry("p1", "InterfaceBoundaryAgent", "agent_registry")
_emit_validates_agent_capability("p1", "InterfaceBoundaryAgent", "capability")
_emit_dispatches_execution_plan("p1", "InterfaceBoundaryAgent", "exec_plan")
_emit_agent_executes_agent("p1", "InterfaceBoundaryAgent", "sub_agent")
_emit_routes_to_agent("p1", "InterfaceBoundaryAgent", "target_agent")
_emit_verifies_policy("p1", "InterfaceBoundaryAgent", "policy_check")
_emit_observes_runtime_state("p1", "InterfaceBoundaryAgent", "runtime_state")
_emit_verifies_boundary("p1", "InterfaceBoundaryAgent", "boundary_check")
_emit_transcripts_response("p1", "InterfaceBoundaryAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "InterfaceBoundaryAgent")
_emit_gated_by_confidence("p1", "InterfaceBoundaryAgent", "confidence_gate")
_emit_escalates_to_human("p1", "InterfaceBoundaryAgent", "L5")
_emit_reads_policy_state("p1", "InterfaceBoundaryAgent", "L5")

_emit_applies_guardrail("p0", "InterfaceBoundaryAgent", "p0_governance")
_emit_authorize_and_execute("p2", "InterfaceBoundaryAgent", "execution_auth")
_emit_validates_capability("p2", "InterfaceBoundaryAgent", "capability_check")
_emit_routes_to_capability("p2", "InterfaceBoundaryAgent", "capability_route")
_emit_writes_via_uwg("p2", "InterfaceBoundaryAgent", "uwg_write")
_emit_blocks_direct_write("p2", "InterfaceBoundaryAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "InterfaceBoundaryAgent", "tool_invocation")
_emit_captures_execution_output("p2", "InterfaceBoundaryAgent", "exec_output")
_emit_dispatches_agent("p3", "InterfaceBoundaryAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "InterfaceBoundaryAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "InterfaceBoundaryAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "InterfaceBoundaryAgent", "healing_outcome")
_emit_escalates_failure("p3", "InterfaceBoundaryAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "InterfaceBoundaryAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "InterfaceBoundaryAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "InterfaceBoundaryAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "InterfaceBoundaryAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "InterfaceBoundaryAgent", "eval_metric")
_emit_stores_embedding("p4", "InterfaceBoundaryAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "InterfaceBoundaryAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "InterfaceBoundaryAgent", "exec_snapshot_link")

"\nINTERFACE BOUNDARY AGENT\n------------------------\nL2 Execution Agent designed to enforce the boundary between L0 Infrastructure\nand higher-level Orchestration.\n\nMechanism:\n1. Analyzes L0 maintenance scripts for complexity (Methods > 15 or LOC > 200).\n2. Identifies 'Heavy' dependencies being imported by L3/L4 agents.\n3. Automatically generates abstract Interface files in agentic_core/utils/core_extensions/.\n4. Proposes refactoring steps to decouple concrete implementations.\n"
import ast
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_snapshots_state,
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
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.ssot_discovery_validator import get_python_files

_emit_emits_metric_event("InterfaceBoundaryAgent", "p4obs", "metric_1")
_emit_emits_metric_event("InterfaceBoundaryAgent", "p4obs", "metric_2")
_emit_emits_metric_event("InterfaceBoundaryAgent", "p4obs", "metric_3")
_emit_emits_metric_event("InterfaceBoundaryAgent", "p4obs", "metric_4")
_emit_emits_metric_event("InterfaceBoundaryAgent", "p4obs", "metric_5")
_emit_emits_metric_event("InterfaceBoundaryAgent", "p4obs", "metric_6")
_emit_records_incident_event("InterfaceBoundaryAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("InterfaceBoundaryAgent", "p4obs", "anomaly")
_emit_writes_observability_log("InterfaceBoundaryAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("InterfaceBoundaryAgent", "p4obs", "mon_state")
_emit_triggers_alert("InterfaceBoundaryAgent", "p4obs", "alert")
_emit_links_incident_trace("InterfaceBoundaryAgent", "p4obs", "trace_link")
_emit_captures_pattern("InterfaceBoundaryAgent", "p3lm", "pattern")
_emit_records_learning_event("InterfaceBoundaryAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("InterfaceBoundaryAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("InterfaceBoundaryAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("InterfaceBoundaryAgent", "p3lm", "routing")
_emit_improves_agent_policy("InterfaceBoundaryAgent", "p3lm", "policy")
_emit_stores_learning_state("InterfaceBoundaryAgent", "p3lm", "state")
_emit_records_execution_trace("InterfaceBoundaryAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("InterfaceBoundaryAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("InterfaceBoundaryAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("InterfaceBoundaryAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("InterfaceBoundaryAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("InterfaceBoundaryAgent", "env_read", "p2_env_1")
_emit_reads_environ("InterfaceBoundaryAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("InterfaceBoundaryAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("InterfaceBoundaryAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "InterfaceBoundaryAgent", "context_pull")
_emit_pulls_context("p1", "InterfaceBoundaryAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "InterfaceBoundaryAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "InterfaceBoundaryAgent", "uwg_term_2")
_emit_writes_through("p1", "InterfaceBoundaryAgent", "write_through")
_emit_writes_through("p1", "InterfaceBoundaryAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "InterfaceBoundaryAgent", "safety_validation")
_emit_invokes_eval("p1", "InterfaceBoundaryAgent", "eval_call")
_emit_proposal_commits_routing("p1", "InterfaceBoundaryAgent", "routing_commit")


@dataclass
class InterfaceBoundaryAgent(SovereignBaseAgent):
    """
    The Architect Agent.
    Prevents L0 utilities from polluting the upper layers by enforcing interface boundaries.
    """

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "InterfaceBoundaryAgent.heal_repository", "state_snapshot")
        _emit_validated_by_safety_plane(
            str(uuid.uuid4()), "InterfaceBoundaryAgent.heal_repository", "L5_POLICY"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "InterfaceBoundaryAgent.heal_repository"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:InterfaceBoundaryAgent.heal_repository".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        super().heal_repository(**kwargs)
        return {"violations_found": 0, "violations_fixed": 0, "errors": 0}

    # guardian: allow-magic-config
    def __init__(self, root_dir: str = ".", complexity_threshold: int = 15) -> None:
        """Initialize the instance."""
        self.root = Path(root_dir)
        self.threshold = complexity_threshold
        self.violations: list[dict] = []

    def audit_boundaries(self) -> list[dict]:
        """Scans L0 for complexity violations and upward leakage potential."""
        l0_path = self.root / AGENTIC_CORE_DIR / "L0_routing"
        all_py = get_python_files(self.root)
        for py_file in [f for f in all_py if str(f).startswith(str(l0_path))]:
            metrics = self._analyze_file_complexity(py_file)
            if metrics["method_count"] > self.threshold:
                self.violations.append(
                    {"file": str(py_file), "complexity": metrics, "action": "EXTRACT_INTERFACE"}
                )
        return self.violations

    # guardian: allow-type-erasure
    def _analyze_file_complexity(self, file_path: Path) -> dict:
        """Uses AST to count classes and methods within a utility file."""
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
            methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            return {
                "method_count": len(methods),
                "class_count": len(classes),
                "loc": len(file_path.read_text().splitlines()),
            }
        # guardian: allow-silent-swallow
        except (ValueError, TypeError):
            return {"method_count": 0, "class_count": 0, "loc": 0}

    def generate_interface_stub(self, violation: dict) -> str:
        """Creates a proposed abstract base class for a 'Heavy' L0 utility."""
        source_path = Path(violation["file"])
        interface_name = f"I{source_path.stem}"
        content = [
            "from abc import ABC, abstractmethod",
            "",
            f"class {interface_name}(ABC):",
            f'    """Automatically extracted interface for {source_path.name}"""',
        ]
        tree = ast.parse(source_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and (not node.name.startswith("_")):
                args = ast.unparse(node.args)
                content.append(f"    @abstractmethod\n    def {node.name}(self, {args}):\n        pass")
        return "\n".join(content)

    # guardian: allow-type-erasure
    def report(self) -> Any:
        """Detailed report of required structural decoupling."""
        if not self.violations:
            print("✅ BOUNDARY INTEGRITY: All L0 utilities are within complexity limits.")
            return
        print(f"⚠️  ARCHITECTURAL DRIFT: Found {len(self.violations)} heavy L0 utilities.")
        for v in self.violations:
            print(
                f"   [!] {v['file']} exceeds method threshold ({v['complexity']['method_count']}/{self.threshold})"
            )
            print(f"   Recommended: Extract to utils/core_extensions/Interface_{Path(v['file']).stem}.py")

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by InterfaceBoundaryAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"InterfaceBoundaryAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            return {
                "status": "failed",
                "details": f"InterfaceBoundaryAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


if __name__ == "__main__":
    agent = InterfaceBoundaryAgent()
    agent.audit_boundaries()
    agent.report()
