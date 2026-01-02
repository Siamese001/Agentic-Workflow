from __future__ import annotations
"""
Canon Validator Agents Package.
All validation agents are exported from this module.
Note: Most imports are now stubs due to restructured module paths.
"""

# Stub imports - actual agents are discovered dynamically by ComplianceOrchestrator
ArchitectureGovernor = None
BenchmarkingAgent = None
CodeStyleGuardian = None
ConcurrencyGuardian = None
DeadlockDetector = None
DependencySentinel = None
DocEnforcer = None
GitAgent = None
Historian = None
HygieneGuardian = None
MemoryLeakDetector = None
NamingEnforcer = None
PatternEnforcer = None
PerformanceEnforcer = None
ReflectionAgent = None
SafetyInspector = None
SecurityEnforcer = None
Sherlock = None
StrategicPlanner = None
StructuralEngineer = None
TestPilot = None
TheCartographer = None
TheOmniContext = None
TheStrategist = None
ToolsmithAgent = None
TypeEnforcer = None

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
