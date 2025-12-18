"""
Autonomous Outreach Engine - Full Autonomy Implementation

This module provides the autonomous agent architecture for outreach campaigns,
bringing it to Level 4+ autonomy with multi-agent coordination, self-diagnosis,
and self-healing capabilities.

Ported from Resume Engine autonomous module with outreach-specific adaptations.
"""

from .context import OutreachEngineContext, OutreachBudgetManager
from .base_agent import OutreachAgent
from .agents import (
    LeadQualityAgent,
    ContactValidatorAgent,
    MessageComplianceAgent,
    TemplateOptimizer,
    CampaignBalanceAgent,
    DeliverabilityAgent,
    OutreachTestPilot,
    CampaignPlanner,
    OutreachReflectionAgent,
)
from .healing import (
    OutreachHealingStrategy,
    OutreachCycleResult,
    OutreachHealingResult,
    OutreachSignalRouter,
    OutreachAgentFactory,
    OutreachHealingCycle,
    OutreachHealingOrchestrator,
    run_outreach_healing_mission,
)
from .learning import (
    OutreachLearningLoop,
    OutreachConfidenceScorer,
    OutreachMemoryPersistence,
    OutreachLearningAgent,
)
from .observability import (
    OutreachExecutionTracer,
    OutreachMetricsCollector,
    OutreachAuditReporter,
    OutreachPhase5Orchestrator,
)
from .proactive import (
    OutreachTaskPriority,
    OutreachHandoffReason,
    OutreachProactiveTask,
    OutreachHandoffRequest,
    OutreachCapabilityProfile,
    OutreachProactiveScheduler,
    OutreachPredictiveHandoff,
    OutreachCapabilityMonitor,
    OutreachProactiveAgent,
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
