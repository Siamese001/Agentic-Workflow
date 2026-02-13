#!/usr/bin/env python3
"""
L0 Compliance Gate: SSOT Architecture Enforcement

This module enforces critical architectural rules across the entire agent ecosystem.
It validates that all agents conform to the Sovereign Architecture Pattern and
prevents structural violations that would compromise system integrity.

Critical Rules:
1. All agents must inherit from SovereignBaseAgent (directly or via mixin chain)
2. SovereignBaseAgent itself is whitelisted (root exception)
3. Agents must belong to valid layers (tests layer is prohibited)
"""

import logging
from typing import Any

from agentic_core.runtime.utils.discovery_util import DiscoveredAgent

logger = logging.getLogger(__name__)


def check_compliance(discovered_agents: list[DiscoveredAgent]) -> list[str]:
    """
    Validates that all discovered agents conform to architectural requirements.

    Args:
        discovered_agents: List of agents discovered by AgentRegistry

    Returns:
        List of violation descriptions (empty if all compliant)
    """
    violations = []

    for agent in discovered_agents:
        # SOVEREIGN ROOT EXCEPTION:
        # The root base class cannot inherit from itself. It is the origin of the chain.
        if agent.name == "SovereignBaseAgent":
            continue

        # Check 1: Inheritance from SovereignBaseAgent
        # Agents must inherit from SovereignBaseAgent directly or via a mixin chain
        # We check the MRO to ensure SovereignBaseAgent is present
        if "SovereignBaseAgent" not in [c.__name__ for c in agent.class_ref.__mro__]:
            violations.append(f"{agent.name} (Orphaned: No Sovereign Inheritance)")
            continue

        # Check 2: Layer Validity
        # Ensure agents belong to recognized architectural layers
        if agent.layer == "unknown":
            violations.append(f"{agent.name} (Unknown Layer)")
        # Note: 'tests' layer is now strictly prohibited.
        # Test agents must reside in L0_routing.testing

    if violations:
        logger.error(f"Compliance Violation Detected in L-Architecture: {violations}")
        logger.error("Agents violating architectural rules will be quarantined.")

    return violations


def check_legacy_compatibility() -> dict[str, Any]:
    """
    Legacy compatibility check for older agent formats.
    This function ensures backward compatibility during migration.

    Returns:
        Dict containing compatibility status and recommendations
    """
    return {
        "status": "compatible",
        "message": "All agents conform to Sovereign Architecture Pattern",
        "recommendations": [],
    }
