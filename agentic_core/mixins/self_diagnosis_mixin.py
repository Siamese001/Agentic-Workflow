from __future__ import annotations

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

_emit_applies_guardrail("p0", "self_diagnosis_mixin", "p0_governance")
_emit_reads_policy_state("p0", "self_diagnosis_mixin", "policy_binding")
_emit_snapshots_state("p0", "self_diagnosis_mixin", "state_snapshot")
emit_replay_key("p0", "self_diagnosis_mixin")
emit_determinism_digest("p0", "self_diagnosis_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "self_diagnosis_mixin", "execution_auth")
_emit_validates_capability("p2", "self_diagnosis_mixin", "capability_check")
_emit_routes_to_capability("p2", "self_diagnosis_mixin", "capability_route")
_emit_writes_via_uwg("p2", "self_diagnosis_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "self_diagnosis_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "self_diagnosis_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "self_diagnosis_mixin", "exec_output")
_emit_dispatches_agent("p3", "self_diagnosis_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "self_diagnosis_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "self_diagnosis_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "self_diagnosis_mixin", "healing_outcome")
_emit_escalates_failure("p3", "self_diagnosis_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "self_diagnosis_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "self_diagnosis_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "self_diagnosis_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "self_diagnosis_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "self_diagnosis_mixin", "eval_metric")
_emit_stores_embedding("p4", "self_diagnosis_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "self_diagnosis_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "self_diagnosis_mixin", "exec_snapshot_link")

"\nSelfDiagnosisMixin – Sovereign Agent Role Mixin (Phase 31 – Dec 30, 2025)\n\nPurpose:\n  Enable critical agents (especially orchestrators) to autonomously monitor their own health.\n  Detects:\n    - Missing mandatory components\n    - Component health_check failures\n    - configuration drift\n  Critical for ComplianceOrchestratorAgent, HealingOrchestratorAgent, and future SovereignOrchestrator.\n\nConstitutional Alignment:\n  - Enables self-preservation without external monitoring\n  - Provides early warning of internal degradation\n  - Fully observable via structured diagnosis output\n"
import logging
from datetime import datetime
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class SelfDiagnosisMixin:
    """
    Mixin that adds comprehensive self-diagnostic capability.
    Agents define MANDATORY_COMPONENTS to enable deep health checking.
    """

    MANDATORY_COMPONENTS: list[str] = []
    '\n    List of attribute names that must exist and be healthy.\n    Example:\n        MANDATORY_COMPONENTS = [\n            "guardian_orchestrator",\n            "healing_orchestrator",\n            "metrics_witness",\n            "experience_buffer"\n        ]\n    '

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Logger = logging.getLogger(f"{self.__class__.__name__}.Diagnosis")

    async def self_diagnose(self) -> dict[str, Any]:
        """
        Perform full self-diagnostic cycle.
        Returns structured report for L6 observability and proactive healing.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SelfDiagnosisMixin.self_diagnose")

        diagnosis = {
            "diagnosis_timestamp": datetime.utcnow().isoformat() + "Z",
            "agent": self.__class__.__name__,
            "overall_health": "healthy",
            "issues": [],
            "successful_checks": [],
            "self_repair_attempts": [],
        }
        self.Logger.info("Initiating self-diagnosis cycle")
        for component_name in self.MANDATORY_COMPONENTS:
            component = getattr(self, component_name, None)
            check_result = {"component": component_name, "found": component is not None}
            if component is None:
                issue = {
                    "type": "missing_component",
                    "component": component_name,
                    "Severity": "CRITICAL",
                    "message": f"Mandatory component '{component_name}' is Missing",
                }
                diagnosis["issues"].append(issue)
                self.Logger.error(issue["message"])
                continue
            diagnosis["successful_checks"].append(check_result)
            if hasattr(component, "health_check"):
                try:
                    health = await component.health_check()
                    if not health.get("healthy", True):
                        issue = {
                            "type": "component_unhealthy",
                            "component": component_name,
                            "Severity": health.get("Severity", "HIGH"),
                            "details": health.get("issue", "Unknown health issue"),
                        }
                        diagnosis["issues"].append(issue)
                        self.Logger.warning(
                            f"Component {component_name} reported unhealthy: {health.get('issue')}"
                        )
                        if await self._attempt_component_repair(component_name, component):
                            diagnosis["self_repair_attempts"].append(
                                {"component": component_name, "success": True}
                            )
                except Exception as e:
                    raise
                    issue = {
                        "type": "component_diagnosis_failed",
                        "component": component_name,
                        "Severity": "HIGH",
                        "error": str(e),
                    }
                    diagnosis["issues"].append(issue)
                    self.Logger.error(f"Health check failed for {component_name}: {e}", exc_info=True)
        try:
            import sys as _sys
            from pathlib import Path as _Path

            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _mod = _sys.modules.get(self.__class__.__module__)
            _self_file = _Path(getattr(_mod, "__file__", "") or "").resolve() if _mod else None
            if _self_file and _self_file.exists():
                _root = _self_file.parents[3]
                _bp = _gbp(_self_file, _root)
                diagnosis["adg_antipatterns"] = sorted(_bp.antipattern_signals)
                diagnosis["adg_behavioral_score"] = _bp.behavioral_score
        # guardian: allow-silent-swallow
        except Exception:
            pass
        if diagnosis["issues"]:
            critical_issues = [i for i in diagnosis["issues"] if i.get("Severity") == "CRITICAL"]
            diagnosis["overall_health"] = "critical" if critical_issues else "degraded"
            self.Logger.warning(
                f"Self-diagnosis complete: {diagnosis['overall_health']} ({len(diagnosis['issues'])} issues)"
            )
        else:
            diagnosis["overall_health"] = "healthy"
            self.Logger.info("Self-diagnosis complete: fully healthy")
        return diagnosis

    async def _attempt_component_repair(self, component_name: str, component: Any) -> bool:
        """
        Optional hook: attempt to repair unhealthy component.
        Default: no repair (conservative).
        Override in agents that support self-repair.
        """
        self.Logger.info(f"No repair logic defined for {component_name} — manual intervention required")
        return False

    async def health_check(self) -> dict[str, Any]:
        """
        Standard health_check interface — called by parent orchestrators or self.
        Uses self_diagnose() for consistency.
        """
        diagnosis = await self.self_diagnose()
        healthy = diagnosis["overall_health"] == "healthy"
        return {
            "healthy": healthy,
            "Severity": "CRITICAL"
            if diagnosis["overall_health"] == "critical"
            else "WARNING"
            if diagnosis["overall_health"] == "degraded"
            else "OK",
            "issue": None if healthy else f"{len(diagnosis['issues'])} component issues detected",
            "full_diagnosis": diagnosis,
        }
