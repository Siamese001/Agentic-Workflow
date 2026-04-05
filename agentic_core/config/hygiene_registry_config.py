from __future__ import annotations
from agentic_core.config.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

# Configuration constants

"""
Core Hygiene Agents Registry - Mandatory agents for repo health.

These agents form the "gravity anchor" for repository hygiene and must
run before any other validation work.

Territory: agentic_core/config/
"""


# Core hygiene agents organized by tier
CORE_HYGIENE_AGENTS: dict[str, list[str]] = {
    "tier_0_preflight": [
        "CodeValidatorAgent",
    ],
    "tier_1_structural": [
        "ImportAgent",
        "LocationAgent",
        "NamingAgent",
        "HierarchyAgent",
        "CodeDeduplicationAgent",
        "HygieneGuardianAgent",  # Now includes FileCleanupAgent logic (consolidated 2026-01-21)
    ],
    "tier_2_architectural": [
        "StructureEnforcerAgent",
        "FilesystemSSOTReconcilerAgent",
        "DDDAlignmentAgent",
        "GitHygieneAgent",
        # FileCleanupAgent - ARCHIVED: Consolidated into HygieneGuardianAgent (2026-01-21)
    ],
    "tier_3_autonomy": [
        "AutonomyGuardianAgent",
        # CodeJanitorAgent - ARCHIVED: Redundant with CodeValidatorAgent (2026-01-21)
    ],
}

# Agents that MUST pass before any healing proceeds
MANDATORY_PREFLIGHT: list[str] = [
    "CodeValidatorAgent",  # Syntax must be valid
    "ImportAgent",  # Imports must be valid
    "LocationAgent",  # Files must be in valid locations
]

# Agent descriptions for documentation
AGENT_DESCRIPTIONS: dict[str, str] = {
    "CodeValidatorAgent": "Syntax validation, AST parsing, canon compliance",
    "ImportAgent": "Import ordering, gravity waterfall, unused import detection",
    "LocationAgent": "Root folder whitelist, depth enforcement, forbidden patterns",
    "NamingAgent": "Naming conventions, *Agent suffix enforcement",
    "HierarchyAgent": "L2/L3 structure creation, depth enforcement, orphan purging",
    "CodeDeduplicationAgent": "Filename uniqueness, whole-file duplicate detection",
    "HygieneGuardianAgent": "Empty files, orphaned __init__.py, backup/temp cleanup, repeated filenames, copy patterns (consolidated)",
    "StructureEnforcerAgent": "Gravity/layer import enforcement, hierarchy validation",
    "FilesystemSSOTReconcilerAgent": "Blueprint → Filesystem alignment, drift detection",
    "DDDAlignmentAgent": "DDD bounded context enforcement, cross-context import detection",
    "GitHygieneAgent": "Stale branches, large files, uncommitted changes",
    "AutonomyGuardianAgent": "Agent autonomy enforcement, heal_repository() requirement",
    # ARCHIVED AGENTS (kept for reference):
    # "FileCleanupAgent": "ARCHIVED - Consolidated into HygieneGuardianAgent (2026-01-21)",
    # "CodeJanitorAgent": "ARCHIVED - Redundant with CodeValidatorAgent (2026-01-21)",
}


def get_all_hygiene_agents() -> list[str]:
    """Get flat list of all hygiene agents."""
    all_agents = []
    for tier_agents in CORE_HYGIENE_AGENTS.values():
        all_agents.extend(tier_agents)
    return all_agents


def get_tier_agents(tier: int) -> list[str]:
    """
    Get agents for a specific tier.

    Args:
        tier: Tier number (0-3)

    Returns:
        List of agent names for that tier
    """
    tier_map = {
        0: "tier_0_preflight",
        1: "tier_1_structural",
        2: "tier_2_architectural",
        3: "tier_3_autonomy",
    }

    tier_key = tier_map.get(tier)
    if tier_key:
        return CORE_HYGIENE_AGENTS.get(tier_key, [])
    return []


def is_mandatory_agent(agent_name: str) -> bool:
    """Check if agent is in mandatory preflight list."""
    return agent_name in MANDATORY_PREFLIGHT
