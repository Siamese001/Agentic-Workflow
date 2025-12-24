"""Sovereign Layer: L3_orchestration"""

from agentic_core.L3_orchestration.framework.dag_executor import DAGNode, DAGExecutionResult, DAGExecutor
from agentic_core.L3_orchestration.P1_core.fission_executor import apply_fission_blueprint
from agentic_core.L3_orchestration.health.autonomic_monitor_impl import AutonomicMonitor
from agentic_core.L3_orchestration.health.autonomic_monitor_types import HealthStatus, AlertSeverity, HealthMetrics, HealthAlert
from agentic_core.L3_orchestration.health.benchmarking_agent import BenchmarkResult, BenchmarkSuite, BenchmarkingAgent, BenchmarkContext
from agentic_core.L3_orchestration.health.deadlock_detector import TaskMonitor, DeadlockDetector
from agentic_core.L3_orchestration.health.memory_leak_detector import MemorySnapshot, MemoryLeakDetector
from agentic_core.L3_orchestration.S3_vitality.context import ThermalProfile, MemoryConfig, GeminiConfig, UniversalContext
from agentic_core.L3_orchestration.S3_vitality.fission_manager import FissionResult, FissionManager
from agentic_core.L3_orchestration.S3_vitality.git_safety_handler import GitSafetyHandler
from agentic_core.L3_orchestration.S3_vitality.mcp_router import MCPRouter
from agentic_core.L3_orchestration.S3_vitality.safety_guardrail import SafetyResult, SafetyGuardrail
# TEMPORARY: Disabled due to cascading type import errors
# from agentic_core.security.agent_permissions_impl import AgentPermissionManager
# from agentic_core.security.agent_permissions_types import PermissionScope, PermissionAction, Permission, PermissionCheck
# from agentic_core.training.agent_gym_impl import AgentGym
# from agentic_core.training.agent_gym_types import ScenarioType, PerformanceLevel, TrainingScenario, BenchmarkResult, TrainingSession

__all__ = ['DAGNode', 'DAGExecutionResult', 'DAGExecutor', 'apply_fission_blueprint', 'AutonomicMonitor', 'HealthStatus', 'AlertSeverity', 'HealthMetrics', 'HealthAlert', 'BenchmarkResult', 'BenchmarkSuite', 'BenchmarkingAgent', 'BenchmarkContext', 'TaskMonitor', 'DeadlockDetector', 'MemorySnapshot', 'MemoryLeakDetector', 'ThermalProfile', 'MemoryConfig', 'GeminiConfig', 'UniversalContext', 'FissionResult', 'FissionManager', 'GitSafetyHandler', 'MCPRouter', 'SafetyResult', 'SafetyGuardrail']
