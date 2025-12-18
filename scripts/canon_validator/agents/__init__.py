"""
Canon Validator Agents Package.
All validation agents are exported from this module.
"""

# Batch 2: Core agents
from .historian import Historian
from .architecture_governor import ArchitectureGovernor
from .hygiene_guardian import HygieneGuardian
from .code_style_guardian import CodeStyleGuardian
from .dependency_sentinel import DependencySentinel

# Batch 3: Safety and testing agents
from .safety_inspector import SafetyInspector
from .concurrency_guardian import ConcurrencyGuardian
from .test_pilot import TestPilot
from .structural_engineer import StructuralEngineer
from .pattern_enforcer import PatternEnforcer

# Batch 4: Security and performance agents
from .security_enforcer import SecurityEnforcer
from .performance_enforcer import PerformanceEnforcer
from .memory_leak_detector import MemoryLeakDetector
from .deadlock_detector import DeadlockDetector
from .sherlock import Sherlock

# Batch 5: Strategic and operational agents
from .strategic_planner import StrategicPlanner
from .reflection_agent import ReflectionAgent
from .git_agent import GitAgent
from .benchmarking_agent import BenchmarkingAgent
from .toolsmith_agent import ToolsmithAgent

# Batch 6: Refinement and optimization agents
from .the_strategist import TheStrategist
from .naming_enforcer import NamingEnforcer
from .doc_enforcer import DocEnforcer
from .type_enforcer import TypeEnforcer
from .the_cartographer import TheCartographer, TheOmniContext

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
