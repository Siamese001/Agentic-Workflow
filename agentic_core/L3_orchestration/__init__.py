"""Sovereign Layer: L3_orchestration"""

from agentic_core.L3_orchestration.workflow_engines.autonomic_monitor_impl import (
    AutonomicMonitor,
)
from agentic_core.L3_orchestration.workflow_engines.autonomic_monitor_types import (
    AlertSeverity,
    HealthAlert,
    HealthMetrics,
    HealthStatus,
)
from agentic_core.L3_orchestration.workflow_engines.benchmarking_agent import (
    BenchmarkContext,
    BenchmarkingAgent,
    BenchmarkResult,
    BenchmarkSuite,
)
from agentic_core.L3_orchestration.workflow_engines.dag_executor import (
    DAGExecutionResult,
    DAGExecutor,
    DAGNode,
)
from agentic_core.L3_orchestration.workflow_engines.deadlock_detector import (
    DeadlockDetector,
    TaskMonitor,
)
from agentic_core.L3_orchestration.workflow_engines.fission_executor import (
    apply_fission_blueprint,
)
from agentic_core.L3_orchestration.workflow_engines.fission_manager import (
    FissionManager,
    FissionResult,
)
from agentic_core.L3_orchestration.workflow_engines.git_safety_handler import (
    GitSafetyHandler,
)
try:
    from agentic_core.L3_orchestration.workflow_engines.mcp_router import MCPRouter
except ImportError:
    # [L6 HARDENING] Graceful degradation when MCP router missing
    # Rationale: Log repeatedly shows "No module named 'agentic_core.L3_orchestration.workflow_engines'"
    # → MCPRouter import fails → Sovereign MCP Router falls back → direct writes disabled
    # → TerritoryHealerAgent cannot move files safely → healing restricted
    class MCPRouter:
        def __init__(self, *args, **kwargs):
            print("   [!] MCPRouter unavailable — using direct filesystem fallback")
        def route(self, *args, **kwargs):
            return {"status": "fallback", "action": "direct"}
    print("   [WARNING] MCPRouter stub loaded (missing mcp/ package)")
from agentic_core.L3_orchestration.workflow_engines.memory_leak_detector import (
    MemoryLeakDetector,
    MemorySnapshot,
)
from agentic_core.L3_orchestration.workflow_engines.safety_guardrail import (
    SafetyGuardrail,
    SafetyResult,
)
from agentic_core.schemas.P1_core.context_passport import ThermalProfile

__all__ = ['DAGNode', 'DAGExecutionResult', 'DAGExecutor', 'apply_fission_blueprint', 'AutonomicMonitor', 'HealthStatus', 'AlertSeverity', 'HealthMetrics', 'HealthAlert', 'BenchmarkResult', 'BenchmarkSuite', 'BenchmarkingAgent', 'BenchmarkContext', 'TaskMonitor', 'DeadlockDetector', 'MemorySnapshot', 'MemoryLeakDetector', 'ThermalProfile', 'FissionResult', 'FissionManager', 'GitSafetyHandler', 'MCPRouter', 'SafetyResult', 'SafetyGuardrail']
