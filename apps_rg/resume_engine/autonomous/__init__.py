"""
Autonomous Resume Engine - Phase 1 & 2: Foundation + Self-Healing

This module provides the autonomous agent architecture for resume generation,
bringing it to Level 4+ autonomy with multi-agent coordination, self-diagnosis,
and self-healing capabilities.
"""

from .context import ResumeEngineContext, BudgetManager, SectionDependencyGraph
from .base_agent import ResumeAgent
from .agents import (
    ContentQualityAgent,
    FactCheckAgent,
    BrandComplianceAgent,
    TemplateOptimizer,
    SectionBalanceAgent,
    ATSCompatibilityAgent,
    TestPilot,
    StrategicPlanner,
    ReflectionAgent,
)
from .orchestrator import run_resume_mission, quick_validate
from .healing import (
    HealingStrategy,
    CycleResult,
    HealingResult,
    SignalRouter,
    AgentFactory,
    HealingCycle,
    HealingOrchestrator,
    run_self_healing_mission,
    ConvergenceDetector,
    AutomaticRollback,
)
from .learning import (
    ConfidenceLevel,
    LearningExample,
    ConfidenceResult,
    Instruction,
    MemoryState,
    LearningLoop,
    ConfidenceScorer,
    InstructionInjector,
    MemoryPersistence,
    ResumeLearningAgent,
)

__all__ = [
    # Context
    "ResumeEngineContext",
    "BudgetManager",
    "SectionDependencyGraph",
    # Base
    "ResumeAgent",
    # Agents
    "ContentQualityAgent",
    "FactCheckAgent",
    "BrandComplianceAgent",
    "TemplateOptimizer",
    "SectionBalanceAgent",
    "ATSCompatibilityAgent",
    "TestPilot",
    "StrategicPlanner",
    "ReflectionAgent",
    # Orchestration (Phase 1)
    "run_resume_mission",
    "quick_validate",
    # Self-Healing (Phase 2)
    "HealingStrategy",
    "CycleResult",
    "HealingResult",
    "SignalRouter",
    "AgentFactory",
    "HealingCycle",
    "HealingOrchestrator",
    "run_self_healing_mission",
    "ConvergenceDetector",
    "AutomaticRollback",
    # Learning & Intelligence (Phase 3)
    "ConfidenceLevel",
    "LearningExample",
    "ConfidenceResult",
    "Instruction",
    "MemoryState",
    "LearningLoop",
    "ConfidenceScorer",
    "InstructionInjector",
    "MemoryPersistence",
    "ResumeLearningAgent",
]
