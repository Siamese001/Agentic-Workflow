"""Agent classes for agentic_core."""

# Base classes
from .base import SubAtomicAgent, ImportPatcher

# Analysis agents
from .analysis import SemanticMapper, TruthKeeper

# Concurrency agents
from .concurrency import (
    MemoryLeakDetector,
    DeadlockAnalyzer,
    DeadlockDetector,
    RaceAnalyzer
)

# Context agents
from .context import OmniContext

# Planning agents
from .planning import StrategicPlanner, ReflectionAgent

# Security agents (SafetyInspector, ConcurrencyGuardian, SecurityEnforcer, RedSentinel)
from .security import SafetyInspector, ConcurrencyGuardian, SecurityEnforcer, RedSentinel

# Specialized agents
from .specialized import (
    TheCartographer,
    TheOmniContext,
    TheStrategist,
    NamingEnforcer,
    DocEnforcer,
    TypeEnforcer
)

# Infrastructure agents
from .infrastructure import Historian, GitAgent, BenchmarkingAgent

# Engineering agents
from .engineering import StructuralEngineer, PatternEnforcer

# Governance agents
from .governance import ArchitectureGovernor, DependencySentinel

# Quality agents (HygieneGuardian, CodeStyleGuardian, PerformanceEnforcer)
from .quality import HygieneGuardian, CodeStyleGuardian, PerformanceEnforcer

# Repair agents
from .repair import TestPilot, ToolsmithAgent, Sherlock

__all__ = [
    # Base
    'SubAtomicAgent',
    'ImportPatcher',
    # Analysis
    'SemanticMapper',
    'TruthKeeper',
    # Concurrency
    'MemoryLeakDetector',
    'DeadlockAnalyzer',
    'DeadlockDetector',
    'RaceAnalyzer',
    # Context
    'OmniContext',
    # Planning
    'StrategicPlanner',
    'ReflectionAgent',
    # Security
    'SafetyInspector',
    'ConcurrencyGuardian',
    'SecurityEnforcer',
    'RedSentinel',
    # Specialized
    'TheCartographer',
    'TheOmniContext',
    'TheStrategist',
    'NamingEnforcer',
    'DocEnforcer',
    'TypeEnforcer',
    # Infrastructure
    'Historian',
    'GitAgent',
    'BenchmarkingAgent',
    # Engineering
    'StructuralEngineer',
    'PatternEnforcer',
    # Governance
    'ArchitectureGovernor',
    'DependencySentinel',
    # Quality
    'HygieneGuardian',
    'CodeStyleGuardian',
    'PerformanceEnforcer',
    # Repair
    'TestPilot',
    'ToolsmithAgent',
    'Sherlock',
]
