# mission_controller.py
# Shim module - re-exports MissionController from mission_controller_engine.py
# This provides backward compatibility for imports expecting mission_controller.MissionController

from agentic_core.L3_orchestration.workflow_engines.mission_controller_engine import MissionController

__all__ = ["MissionController"]
