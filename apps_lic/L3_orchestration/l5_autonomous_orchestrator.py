"""
L5+ Autonomous Orchestrator for Outreach Engine.

Implements full Canon Validator autonomy patterns:
- Convergence loop with max cycles
- Signal-based blackboard communication
- Human-in-the-loop intervention
- Reflection and self-critique
- Blast radius analysis
- Rollback on regression
- Few-shot injection

This orchestrator achieves parity with canon_validator_agentic.py autonomy level.
"""

import logging

logger = logging.getLogger(__name__)

# Re-export from new modular structure
from apps_lic.L3_orchestration.l5_orchestrator.orchestrator import (
    L5OutreachOrchestrator,
)

# Factory function for backward compatibility
def create_l5_outreach_orchestrator(
    campaign_id: str,
    archetype: str = "RECRUITER",
    max_cycles: int = 5,
    quality_threshold: float = 0.75,
    enable_intervention: bool = True,
) -> L5OutreachOrchestrator:
    """Factory function to create L5+ outreach orchestrator."""
    return L5OutreachOrchestrator(
        campaign_id=campaign_id,
        archetype=archetype,
        max_cycles=max_cycles,
        quality_threshold=quality_threshold,
        enable_intervention=enable_intervention,
    )
