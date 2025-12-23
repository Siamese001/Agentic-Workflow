"""
apps_rg/L3_orchestration package initialization.
Provides orchestration components for the Resume Engine including:
- L5+ Autonomous Orchestrator with Canon Validator patterns
- Hardened Workflow Orchestrator with checkpointing
- Recursive Planner Agent for complex goal decomposition
Generated: 2025-12-07T13:29:00.527590
Updated: 2025-12-17 - Added L5+ autonomy components
"""
import logging
logger = logging.getLogger(__name__)
# Import sovereign ExecutionPhase from core
from agentic_core.L3_orchestration.P1_core.orchestration_types import ExecutionPhase, ExecutionPhaseSignal
# L5+ Autonomous Orchestrator (Canon Validator parity)
from apps_rg.L3_orchestration.l5_autonomous_orchestrator import (
    CycleState,
    L5AutonomousOrchestrator,
    WorkflowSnapshot,
    create_l5_orchestrator,
)
__all__ = ['# L5+ Autonomous Orchestrator', 'L5AutonomousOrchestrator', 'create_l5_orchestrator', 'ExecutionPhase', 'CycleState', 'WorkflowSnapshot', '# Legacy exports (if available)', 'RGWorkflowOrchestrator']
