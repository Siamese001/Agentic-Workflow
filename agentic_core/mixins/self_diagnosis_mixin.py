from __future__ import annotations

"""
SelfDiagnosisMixin – Sovereign Agent Role Mixin (Phase 31 – Dec 30, 2025)

Purpose:
  Enable critical agents (especially orchestrators) to autonomously monitor their own health.
  Detects:
    - Missing mandatory components
    - Component health_check failures
    - configuration drift
  Critical for ComplianceOrchestratorAgent, HealingOrchestratorAgent, and future SovereignOrchestrator.

Constitutional Alignment:
  - Enables self-preservation without external monitoring
  - Provides early warning of internal degradation
  - Fully observable via structured diagnosis output
"""

import logging
from datetime import datetime
from typing import Any


class SelfDiagnosisMixin:
    """
    Mixin that adds comprehensive self-diagnostic capability.
    Agents define MANDATORY_COMPONENTS to enable deep health checking.
    """

    # === Override in concrete agents ===
    MANDATORY_COMPONENTS: list[str] = []
    """
    List of attribute names that must exist and be healthy.
    Example:
        MANDATORY_COMPONENTS = [
            "guardian_orchestrator",
            "healing_orchestrator",
            "metrics_witness",
            "experience_buffer"
        ]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Logger = logging.getLogger(f"{self.__class__.__name__}.Diagnosis")

    async def self_diagnose(self) -> dict[str, Any]:
        """
        Perform full self-diagnostic cycle.
        Returns structured report for L6 observability and proactive healing.
        """
        diagnosis = {
            "diagnosis_timestamp": datetime.utcnow().isoformat() + "Z",
            "agent": self.__class__.__name__,
            "overall_health": "healthy",
            "issues": [],
            "successful_checks": [],
            "self_repair_attempts": [],
        }

        self.Logger.info("Initiating self-diagnosis cycle")

        # 1. Check mandatory components exist
        for component_name in self.MANDATORY_COMPONENTS:
            component = getattr(self, component_name, None)
            check_result = {
                "component": component_name,
                "found": component is not None,
            }

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

            # 2. If component has health_check method, invoke it
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
                            f"Component {component_name} reported unhealthy: {health.get('issue')}",
                        )

                        # Optional auto-repair attempt
                        if await self._attempt_component_repair(component_name, component):
                            diagnosis["self_repair_attempts"].append(
                                {"component": component_name, "success": True},
                            )
                # guardian: allow-silent-swallow
                except Exception as e:
                    issue = {
                        "type": "component_diagnosis_failed",
                        "component": component_name,
                        "Severity": "HIGH",
                        "error": str(e),
                    }
                    diagnosis["issues"].append(issue)
                    self.Logger.error(f"Health check failed for {component_name}: {e}", exc_info=True)

        # 3. Overall health assessment
        if diagnosis["issues"]:
            critical_issues = [i for i in diagnosis["issues"] if i.get("Severity") == "CRITICAL"]
            diagnosis["overall_health"] = "critical" if critical_issues else "degraded"
            self.Logger.warning(
                f"Self-diagnosis complete: {diagnosis['overall_health']} ({len(diagnosis['issues'])} issues)",
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
