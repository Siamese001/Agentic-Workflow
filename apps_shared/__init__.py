"""
Apps Shared - Common Components for L5+ Autonomous Engines.

This module provides shared autonomy components used by both the
Resume Engine (apps_rg) and Outreach Engine (apps_lic).

Canon Validator L5+ Autonomy Components:
- SignalBus: Blackboard pattern for inter-agent communication
- ReflectionAgent: Self-critique and learning
- InterventionServer: Human-in-the-loop approval
- FewShotLibrary: Prompt enhancement patterns
- ValidationContext: Central blackboard for all agents
"""

from apps_shared.few_shot_library import FewShotExample, FewShotLibrary, get_few_shot
from apps_shared.intervention_server import (
    InterventionContext,
    InterventionServer,
    check_intervention_required,
    get_intervention_server,
    start_intervention_server,
)
from apps_shared.reflection_agent import (
    ExecutionTrace,
    ReflectionAgent,
    ReflectionDecision,
    ReflectionResult,
    create_reflection_agent,
)
from apps_shared.signal_bus import (
    Signal,
    SignalBus,
    SignalHistory,
    SignalType,
    get_signal_bus,
    reset_signal_bus,
)

# Phase 5: Removed import to avoid circular dependency
# ValidationContext should be imported directly from agentic_core.domain.context
# Legacy compatibility maintained through lazy import pattern

def _get_validation_context():
    """Lazy import to avoid circular dependency."""
    from agentic_core.domain.context import ValidationContext
    return ValidationContext

# Legacy compatibility
ModifiedItem = None  # Deprecated - use ValidationContext directly
create_validation_context = _get_validation_context  # Factory function compatibility
ValidationContext = property(lambda self: _get_validation_context())  # Lazy property

__all__ = [
    # Signal Bus
    "SignalBus",
    "SignalType",
    "Signal",
    "SignalHistory",
    "get_signal_bus",
    "reset_signal_bus",
    # Reflection Agent
    "ReflectionAgent",
    "ReflectionDecision",
    "ReflectionResult",
    "ExecutionTrace",
    "create_reflection_agent",
    # Intervention Server
    "InterventionServer",
    "InterventionContext",
    "check_intervention_required",
    "get_intervention_server",
    "start_intervention_server",
    # Few-Shot Library
    "FewShotLibrary",
    "FewShotExample",
    "get_few_shot",
    # Validation Context
    "ValidationContext",
    "ModifiedItem",
    "create_validation_context",
]
