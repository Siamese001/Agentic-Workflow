from __future__ import annotations
"""
Autonomous Outreach Engine - Full Autonomy Implementation

This module provides the autonomous agent architecture for outreach campaigns,
bringing it to Level 4+ autonomy with multi-agent coordination, self-diagnosis,
and self-healing capabilities.

Ported from Resume Engine autonomous module with outreach-specific adaptations.
"""

from .agents import (
    CampaignBalanceAgent,
    CampaignPlanner,
    ContactValidatorAgent,
    DeliverabilityAgent,
    LeadQualityAgent,
    MessageComplianceAgent,
    OutreachReflectionAgent,
    OutreachTestPilot,
    TemplateOptimizer,
)
from .outreach_base import OutreachAgent
from .context import OutreachBudgetManager, OutreachEngineContext
from .healing import (
    OutreachAgentFactory,
    OutreachCycleResult,
    OutreachHealingCycle,
    OutreachHealingOrchestrator,
    OutreachHealingResult,
    OutreachHealingStrategy,
    OutreachSignalRouter,
    run_outreach_healing_mission,
)
from .learning import (
    OutreachConfidenceScorer,
    OutreachLearningAgent,
    OutreachLearningLoop,
    OutreachMemoryPersistence,
)
from .observability import (
    OutreachAuditReporter,
    OutreachExecutionTracer,
    OutreachMetricsCollector,
    OutreachPhase5Orchestrator,
)
from .proactive import (
    OutreachCapabilityMonitor,
    OutreachCapabilityProfile,
    OutreachHandoffReason,
    OutreachHandoffRequest,
    OutreachPredictiveHandoff,
    OutreachProactiveAgent,
    OutreachProactiveScheduler,
    OutreachProactiveTask,
    OutreachTaskPriority,
)

__all__ = [
    # Context
    "OutreachEngineContext",
    "OutreachBudgetManager",
    # Base
    "OutreachAgent",
    # Agents
    "LeadQualityAgent",
    "ContactValidatorAgent",
    "MessageComplianceAgent",
    "TemplateOptimizer",
    "CampaignBalanceAgent",
    "DeliverabilityAgent",
    "OutreachTestPilot",
    "CampaignPlanner",
    "OutreachReflectionAgent",
    # Healing
    "OutreachHealingStrategy",
    "OutreachCycleResult",
    "OutreachHealingResult",
    "OutreachSignalRouter",
    "OutreachAgentFactory",
    "OutreachHealingCycle",
    "OutreachHealingOrchestrator",
    "run_outreach_healing_mission",
    # Learning
    "OutreachLearningLoop",
    "OutreachConfidenceScorer",
    "OutreachMemoryPersistence",
    "OutreachLearningAgent",
    # Observability
    "OutreachExecutionTracer",
    "OutreachMetricsCollector",
    "OutreachAuditReporter",
    "OutreachPhase5Orchestrator",
    # Proactive & Predictive (L4.5 Enhancements)
    "OutreachTaskPriority",
    "OutreachHandoffReason",
    "OutreachProactiveTask",
    "OutreachHandoffRequest",
    "OutreachCapabilityProfile",
    "OutreachProactiveScheduler",
    "OutreachPredictiveHandoff",
    "OutreachCapabilityMonitor",
    "OutreachProactiveAgent",
]
