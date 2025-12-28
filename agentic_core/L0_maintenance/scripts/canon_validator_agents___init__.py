"""
Canon Validator Agents Package.
All validation agents are exported from this module.
"""

from agentic_core.architecture_governor import ArchitectureGovernor
from agentic_core.benchmarking_agent import BenchmarkingAgent
from agentic_core.code_style_guardian import CodeStyleGuardian
from agentic_core.concurrency_guardian import ConcurrencyGuardian
from agentic_core.deadlock_detector import DeadlockDetector
from agentic_core.dependency_sentinel import DependencySentinel
from agentic_core.doc_enforcer import DocEnforcer
from agentic_core.git_agent import GitAgent
from agentic_core.historian import Historian
from agentic_core.hygiene_guardian import HygieneGuardian
from agentic_core.memory_leak_detector import MemoryLeakDetector
from agentic_core.naming_enforcer import NamingEnforcer
from agentic_core.pattern_enforcer import PatternEnforcer
from agentic_core.performance_enforcer import PerformanceEnforcer
from agentic_core.reflection_agent import ReflectionAgent
from agentic_core.safety_inspector import SafetyInspector
from agentic_core.security_enforcer import SecurityEnforcer
from agentic_core.sherlock import Sherlock
from agentic_core.strategic_planner import StrategicPlanner
from agentic_core.structural_engineer import StructuralEngineer
from agentic_core.test_pilot import TestPilot
from agentic_core.the_cartographer import TheCartographer, TheOmniContext
from agentic_core.the_strategist import TheStrategist
from agentic_core.toolsmith_agent import ToolsmithAgent
from agentic_core.type_enforcer import TypeEnforcer

__all__ = [
    # Core agents
    "Historian",
    "ArchitectureGovernor",
    "HygieneGuardian",
    "CodeStyleGuardian",
    "DependencySentinel",
    # Safety and testing
    "SafetyInspector",
    "ConcurrencyGuardian",
    "TestPilot",
    "StructuralEngineer",
    "PatternEnforcer",
    # Security and performance
    "SecurityEnforcer",
    "PerformanceEnforcer",
    "MemoryLeakDetector",
    "DeadlockDetector",
    "Sherlock",
    # Strategic and operational
    "StrategicPlanner",
    "ReflectionAgent",
    "GitAgent",
    "BenchmarkingAgent",
    "ToolsmithAgent",
    # Refinement and optimization
    "TheStrategist",
    "NamingEnforcer",
    "DocEnforcer",
    "TypeEnforcer",
    "TheCartographer",
    "TheOmniContext",
]
