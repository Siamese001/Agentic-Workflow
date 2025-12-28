"""
Mission Plan Stub - Legacy Compatibility Bridge

PURPOSE:
    Legacy compatibility bridge for mission_plan imports.
    Re-exports MissionPlan and Missing from agentic_core.

STATUS: Active - Required for backward compatibility
"""
from agentic_core.L0_maintenance.P1_core.core import MissionPlan, Missing
__all__ = ["MissionPlan", "Missing"]
