"""
L5 Autonomous Orchestrator - Reflection Handler (Outreach Engine)
"""
from typing import Any, Optional, Protocol, Dict, List


import logging
from typing import Any, Optional

from apps_lic.L3_orchestration.l5_orchestrator.types import OutreachCycleState

logger = logging.getLogger(__name__)


async def perform_reflection(orchestrator, cycle_state: OutreachCycleState) -> Optional[Any]:
    """Perform self-critique reflection."""

    if not orchestrator.reflection_agent:
        return None

    signals_summary = {}
    if orchestrator.signal_bus:
        signals_summary = orchestrator.signal_bus.get_summary()

    return await orchestrator.reflection_agent.reflect_on_execution(
        execution_log=cycle_state.execution_log,
        signals_summary=signals_summary,
        cycle=orchestrator.current_cycle,
        quality_scores=cycle_state.quality_scores,
    )


def check_quality_acceptable(orchestrator, cycle_state: OutreachCycleState) -> bool:
    """Check if quality scores meet threshold."""
    if not cycle_state.quality_scores:
        return True

    avg_quality = get_average_quality(orchestrator, cycle_state)
    return avg_quality >= orchestrator.quality_threshold


def get_average_quality(orchestrator, cycle_state: OutreachCycleState) -> float:
    """Get average quality score from cycle."""
    if not cycle_state.quality_scores:
        return 1.0
    scores = list(cycle_state.quality_scores.values())
    return sum(scores) / len(scores)
