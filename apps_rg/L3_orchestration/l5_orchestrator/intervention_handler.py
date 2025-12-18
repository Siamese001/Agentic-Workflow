"""
L5 Autonomous Orchestrator - Intervention Handler
"""

import logging
from typing import Any, Dict, List

from apps_shared.signal_bus import SignalType
from apps_shared.intervention_server import InterventionContext, check_intervention_required
from apps_rg.L3_orchestration.l5_orchestrator.types import CycleState

logger = logging.getLogger(__name__)


async def check_intervention_required(orchestrator, cycle_state: CycleState) -> bool:
    """Check if human intervention is required and handle it."""
    
    if not orchestrator.enable_intervention or not orchestrator.intervention_server:
        return False
    
    if not orchestrator.signal_bus:
        return False
    
    # Check intervention conditions
    intervention_needed, risk_factors = check_intervention_required(
        cycle=orchestrator.current_cycle,
        modified_count=len(cycle_state.modified_items),
        signals=[s.value for s in orchestrator.signal_bus.signals],
        quality_score=get_average_quality(orchestrator, cycle_state),
        high_risk_threshold=orchestrator.DEFAULT_HIGH_RISK_MODIFIED_THRESHOLD,
    )
    
    if not intervention_needed:
        return False
    
    logger.warning(f"🚨 INTERVENTION REQUIRED: {risk_factors}")
    
    # Create intervention context
    intervention_ctx = InterventionContext(
        workflow_id=orchestrator.workflow_id,
        cycle=orchestrator.current_cycle,
        reason="High-risk state detected",
        risk_factors=risk_factors,
        modified_items=list(cycle_state.modified_items),
        signals=[s.value for s in orchestrator.signal_bus.signals],
        quality_score=get_average_quality(orchestrator, cycle_state),
        recommendations=generate_recommendations(orchestrator, cycle_state),
    )
    
    # Request intervention
    approved = await orchestrator.intervention_server.request_intervention(
        intervention_ctx,
        timeout=300,  # 5 minute timeout
    )
    
    if not approved:
        await orchestrator.signal_bus.emit(
            SignalType.VETOED,
            "Human vetoed continuation",
            source="InterventionServer"
        )
    
    return True


def get_average_quality(orchestrator, cycle_state: CycleState) -> float:
    """Get average quality score from cycle."""
    if not cycle_state.quality_scores:
        return 1.0
    scores = list(cycle_state.quality_scores.values())
    return sum(scores) / len(scores)


def generate_recommendations(orchestrator, cycle_state: CycleState) -> List[str]:
    """Generate recommendations based on current state."""
    recommendations = []
    
    avg_quality = get_average_quality(orchestrator, cycle_state)
    if avg_quality < orchestrator.quality_threshold:
        recommendations.append(
            f"Quality score ({avg_quality:.2f}) below threshold ({orchestrator.quality_threshold})"
        )
    
    if len(cycle_state.modified_items) > orchestrator.DEFAULT_HIGH_RISK_MODIFIED_THRESHOLD:
        recommendations.append(
            f"Many modifications ({len(cycle_state.modified_items)}) - review carefully"
        )
    
    # Check for failed agents
    failed_agents = [
        e["agent"] for e in cycle_state.execution_log
        if not e.get("success", True)
    ]
    if failed_agents:
        recommendations.append(f"Failed agents: {', '.join(failed_agents)}")
    
    return recommendations
