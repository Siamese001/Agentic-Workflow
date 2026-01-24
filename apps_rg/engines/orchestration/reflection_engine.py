"""
Reflection Engine - Post-execution learning and scoring
Refactored from RgReflectionAgent.py
"""

from __future__ import annotations
from typing import Any, Dict, List
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class ReflectionEngine(BaseRGEngine):
    """
    Reflection - Post-cycle learning and scoring.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="ORCHESTRATION.REFLECTION")

    async def execute(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze workflow results and extract learnings.
        """
        self._mcp_audit("reflection_start")
        
        reflection = {
            "overall_score": 0.0,
            "strengths": [],
            "weaknesses": [],
            "learnings": [],
            "recommendations": []
        }
        
        # Analyze results
        passed_engines = [k for k, v in workflow_results.items() if v.get("passed", False)]
        failed_engines = [k for k, v in workflow_results.items() if not v.get("passed", True)]
        
        reflection["overall_score"] = len(passed_engines) / max(len(workflow_results), 1)
        
        if reflection["overall_score"] >= 0.9:
            reflection["strengths"].append("High success rate across engines")
        
        if failed_engines:
            reflection["weaknesses"].append(f"Failures in: {', '.join(failed_engines)}")
            reflection["recommendations"].append("Review failed engine configurations")
        
        # Extract learnings
        for engine_name, result in workflow_results.items():
            if result.get("signal"):
                reflection["learnings"].append(f"{engine_name} signaled: {result['signal']}")
        
        self.record_pass("Reflection complete", data=reflection)
        return reflection
