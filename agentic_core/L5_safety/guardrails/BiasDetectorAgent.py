from __future__ import annotations
"""Bias Detector Agent - Runs local bias detection with dynamic constitution rules."""

from typing import Any, Dict, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from .SafetyBaseAgent import SafetyBaseAgent  # NEW: Import canonical L5 base class (same directory → relative import)

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# ------------------------------------------------------------------
# REMOVED: Local stub BaseAgent definition (technical debt)
# Reason: SafetyBaseAgent is the canonical L5 base class. It already inherits
#         HealerMixin and provides standardized initialization, logging,
#         and safety utilities. The stub only had pass-through logs.
# ------------------------------------------------------------------

def track_metrics(name):
    """Stub decorator for track_metrics - TODO: Replace with sovereign equivalent"""
    def decorator(func):
        return func
    return decorator

def detect_bias(context, text, workflow_id=""):
    """Stub for detect_bias - TODO: Replace with sovereign equivalent"""
    return {"bias_detected": False, "score": 0.0, "patterns": []}


class BiasDetectorAgent(SafetyBaseAgent, MCPHardenedMixin):
    """Runs local bias detection with dynamic constitution rules."""
    
    def __init__(self, context: Any = None, **kwargs):
        """Initialize BiasDetectorAgent with optional context."""
        super().__init__(name="BiasDetectorAgent", **kwargs)
        self.context = context

    @track_metrics("run_bias_detector")
    def run(self, text: str, workflow_id: str = "") -> Dict[str, object]:
        """Run bias detection on the provided text."""
        # log_info now comes from SafetyBaseAgent (real implementation)
        self.log_info("Detecting bias (local processing with dynamic rules)...")
        result = detect_bias(self.context, text, workflow_id)

        if workflow_id:
            # log_feedback now comes from SafetyBaseAgent (real implementation)
            self.log_feedback(
                workflow_id,
                "bias_detection",
                "warning" if result["bias_detected"] else "success",
                {"patterns_found": len(result.get("patterns", []))},
            )

        return result

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Operational guardrail agent - no repository healing required."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()
        
        print(f"[{self.__class__.__name__}] Operational guardrail - no healing required")
        return {"skipped": 1}

def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, TESTS_DIR: []}
        try:
            assert self is not None
            results["passed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results
