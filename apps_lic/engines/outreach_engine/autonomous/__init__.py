from __future__ import annotations
"""
Autonomous Outreach Engine - Full Autonomy Implementation

This module provides the autonomous agent architecture for outreach campaigns,
bringing it to Level 4+ autonomy with multi-agent coordination, self-diagnosis,
and self-healing capabilities.

Ported from Resume Engine autonomous module with outreach-specific adaptations.
"""

from .agents import (
    LeadQualityAgent,
    OutreachTestPilot,
)
from .context import OutreachBudgetManager, OutreachEngineContext
from .OutreachSignalRouterAgent import (
    OutreachAgentFactory,
    OutreachCycleResult,
    OutreachHealingCycle,
    OutreachHealingResult,
    OutreachHealingStrategy,
    OutreachSignalRouterAgent,
    run_outreach_healing_mission,
    OutreachMetricsCollector,
    OutreachPhase5OrchestratorAgent,
)
from .proactive import (
    OutreachCapabilityMonitorAgent,
    OutreachCapabilityProfile,
    OutreachHandoffReason,
    OutreachHandoffRequest,
    OutreachPredictiveHandoff,
    OutreachProactiveScheduler,
    OutreachProactiveTask,
    OutreachTaskPriority,
)
from .OutreachProactiveAgent import OutreachProactiveAgent

__all__ = [
    "ContactValidatorAgent",
    "MessageComplianceAgent",
    "TemplateOptimizerAgent",
    "CampaignBalanceAgent",
    "DeliverabilityAgent",
    "OutreachTestPilot",
    "CampaignPlannerAgent",
    "OutreachReflectionAgent",
    # Healing
    "OutreachHealingStrategy",
    "OutreachCycleResult",
    "OutreachHealingResult",
    "OutreachSignalRouterAgent",
    "OutreachAgentFactory",
    "OutreachHealingCycle",
    "OutreachHealingOrchestratorAgent",
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
    "OutreachPhase5OrchestratorAgent",
    # Proactive & Predictive (L4.5 Enhancements)
    "OutreachTaskPriority",
    "OutreachHandoffReason",
    "OutreachProactiveTask",
    "OutreachHandoffRequest",
    "OutreachCapabilityProfile",
    "OutreachProactiveScheduler",
    "OutreachPredictiveHandoff",
    "OutreachCapabilityMonitorAgent",
    "OutreachProactiveAgent",
]
