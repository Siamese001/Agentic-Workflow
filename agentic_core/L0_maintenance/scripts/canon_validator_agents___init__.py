from __future__ import annotations
"""
Canon Validator Agents Package.
All validation agents are exported from this module.
Note: Most imports are now stubs due to restructured module paths.
"""

# Stub imports - actual agents are discovered dynamically by ComplianceOrchestratorAgent
ArchitectureGovernor = None
BenchmarkingAgent = None
CodeStyleGuardian = None
ConcurrencyGuardianAgent = None
DeadlockDetectorAgent = None
DependencySentinelAgent = None
DocEnforcer = None
GitAgent = None
Historian = None
HygieneGuardian = None
MemoryLeakDetectorAgent = None
NamingEnforcer = None
PatternEnforcerAgent = None
PerformanceEnforcer = None
RgReflectionAgent = None
SafetyInspectorAgent = None
SecurityEnforcer = None
Sherlock = None
RgStrategicPlannerAgent = None
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
    "DependencySentinelAgent",
    # Safety and testing
    "SafetyInspectorAgent",
    "ConcurrencyGuardianAgent",
    "TestPilot",
    "StructuralEngineer",
    "PatternEnforcerAgent",
    # Security and performance
    "SecurityEnforcer",
    "PerformanceEnforcer",
    "MemoryLeakDetectorAgent",
    "DeadlockDetectorAgent",
    "Sherlock",
    # Strategic and operational
    "StrategicPlannerAgent",
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
