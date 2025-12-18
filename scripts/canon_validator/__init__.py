"""
Canon Validator v2.0 - Subatomic Package
All 50 keys are now covered by Agent classes with zero legacy functions.

This package provides the complete Canon Validator infrastructure:
- ValidationContext: Shared memory (Blackboard) for all agents
- SubAtomicAgent: Base class for all validation agents
- SwarmScheduler: Orchestrator for agent execution
- Individual agents for each validation domain
"""

from .config import (
    EXCLUDED_DIRS,
    EXCLUDED_FILES,
    ALLOWED_ROOT_FOLDERS,
    ALLOWED_ROOT_FILES,
    MIN_DEPTH,
    MAX_DEPTH,
    MAX_LINES,
    MIN_LINES,
    get_python_files,
    is_excluded,
)
from .types import (
    ValidationContext,
    DependencyGraph,
    BudgetManager,
)
from .base import (
    SubAtomicAgent,
    ImportPatcher,
)
from .prompts import (
    POSITIVE_INSTRUCTIONAL_CONTEXT,
    FEW_SHOT_GLOBAL_REFACTOR,
    FEW_SHOT_PROMPTS,
)

# All agents
from .agents import (
    Historian,
    ArchitectureGovernor,
    HygieneGuardian,
    CodeStyleGuardian,
    DependencySentinel,
    SafetyInspector,
    ConcurrencyGuardian,
    TestPilot,
    StructuralEngineer,
    PatternEnforcer,
    SecurityEnforcer,
    PerformanceEnforcer,
    MemoryLeakDetector,
    DeadlockDetector,
    Sherlock,
    StrategicPlanner,
    ReflectionAgent,
    GitAgent,
    BenchmarkingAgent,
    ToolsmithAgent,
    TheStrategist,
    NamingEnforcer,
    DocEnforcer,
    TypeEnforcer,
    TheCartographer,
    TheOmniContext,
)

# Orchestrator
from .orchestrator import SwarmScheduler, IntelligentOrchestrator

__all__ = [
    # Config
    "EXCLUDED_DIRS",
    "EXCLUDED_FILES",
    "ALLOWED_ROOT_FOLDERS",
    "ALLOWED_ROOT_FILES",
    "MIN_DEPTH",
    "MAX_DEPTH",
    "MAX_LINES",
    "MIN_LINES",
    "get_python_files",
    "is_excluded",
    # Types
    "ValidationContext",
    "DependencyGraph",
    "BudgetManager",
    # Base
    "SubAtomicAgent",
    "ImportPatcher",
    # Prompts
    "POSITIVE_INSTRUCTIONAL_CONTEXT",
    "FEW_SHOT_GLOBAL_REFACTOR",
    "FEW_SHOT_PROMPTS",
    # Core Agents
    "Historian",
    "ArchitectureGovernor",
    "HygieneGuardian",
    "CodeStyleGuardian",
    "DependencySentinel",
    # Safety and Testing Agents
    "SafetyInspector",
    "ConcurrencyGuardian",
    "TestPilot",
    "StructuralEngineer",
    "PatternEnforcer",
    # Security and Performance Agents
    "SecurityEnforcer",
    "PerformanceEnforcer",
    "MemoryLeakDetector",
    "DeadlockDetector",
    "Sherlock",
    # Strategic and Operational Agents
    "StrategicPlanner",
    "ReflectionAgent",
    "GitAgent",
    "BenchmarkingAgent",
    "ToolsmithAgent",
    # Refinement and Optimization Agents
    "TheStrategist",
    "NamingEnforcer",
    "DocEnforcer",
    "TypeEnforcer",
    "TheCartographer",
    "TheOmniContext",
    # Orchestrator
    "SwarmScheduler",
    "IntelligentOrchestrator",
]
