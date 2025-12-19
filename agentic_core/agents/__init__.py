"""Agent classes for agentic_core."""

# Base classes
# Analysis agents
from .analysis import SemanticMapper, TruthKeeper
from .base import ImportPatcher, SubAtomicAgent

# Canon Validator agents (Subatomic Level 5)
from .canon_base_agent import CanonBaseAgent
from .system_architect import SystemArchitect
from .code_janitor import CodeJanitor
from .structural_engineer import StructuralEngineer as CanonStructuralEngineer
from .healer_agent import HealerAgent

# Concurrency agents
from .concurrency import (
    DeadlockAnalyzer,
    DeadlockDetector,
    MemoryLeakDetector,
    RaceAnalyzer,
)

# Context agents
from .context import OmniContext

# Engineering agents
from .engineering import PatternEnforcer, StructuralEngineer

# Governance agents
from .governance import ArchitectureGovernor, DependencySentinel

# Infrastructure agents
from .infrastructure import BenchmarkingAgent, GitAgent, Historian

# Planning agents
from .planning import ReflectionAgent, StrategicPlanner

# Quality agents (HygieneGuardian, CodeStyleGuardian, PerformanceEnforcer)
from .quality import CodeStyleGuardian, HygieneGuardian, PerformanceEnforcer

# Repair agents
from .repair import Sherlock, TestPilot, ToolsmithAgent

# Security agents (SafetyInspector, ConcurrencyGuardian, SecurityEnforcer, RedSentinel)
from .security import (
    ConcurrencyGuardian,
    RedSentinel,
    SafetyInspector,
    SecurityEnforcer,
)

# Memory agents (Level 5 Autonomous Learning)
from .memory_architect import MemoryArchitect, get_memory_architect

# Pattern retrieval agents
from .pattern_retrieval_agent import PatternRetrievalAgent, get_pattern_agent

# Systemic enhancement agents
from .adversarial_red_teamer import AdversarialRedTeamer, get_red_teamer
from .dynamic_model_router import DynamicModelRouter, get_model_router
from .schema_evolver import SchemaEvolver, get_schema_evolver
from .predictive_cost_auditor import PredictiveCostAuditor, get_cost_auditor

# Cognitive assurance agents
from .regression_oracle import RegressionOracle, get_regression_oracle
from .hallucination_hunter import HallucinationHunter, get_hallucination_hunter
from .dependency_diplomat import DependencyDiplomat, get_dependency_diplomat
from .context_curator import ContextCurator, get_context_curator

# Specialized agents
from .specialized import (
    DocEnforcer,
    NamingEnforcer,
    TheCartographer,
    TheOmniContext,
    TheStrategist,
    TypeEnforcer,
)

__all__ = [
    # Base
    'SubAtomicAgent',
    'ImportPatcher',
    # Canon Validator (Subatomic Level 5)
    'CanonBaseAgent',
    'SystemArchitect',
    'CodeJanitor',
    'CanonStructuralEngineer',
    'HealerAgent',
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
