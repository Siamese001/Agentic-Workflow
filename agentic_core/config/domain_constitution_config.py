from __future__ import annotations

# Configuration constants

"""
Sovereign Domain Constitution – DDD Alignment (Dec 26, 2025)
Defines Bounded Contexts, Aggregates, and Ubiquitous Language.
L0-L6 Sovereign Stack Hierarchy established.
"""
from typing import Any
from agentic_core.config.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD


def _get_layer_dirs():
    from agentic_core.L5_safety.config.structure_blueprint import (
        L0_MAINTENANCE_DIR,
        L1_COGNITION_DIR,
        L2_EXECUTION_DIR,
        L3_ORCHESTRATION_DIR,
        L4_STATE_DIR,
        L5_SAFETY_DIR,
        L6_OBSERVABILITY_DIR,
    )

    return (
        L0_MAINTENANCE_DIR,
        L1_COGNITION_DIR,
        L2_EXECUTION_DIR,
        L3_ORCHESTRATION_DIR,
        L4_STATE_DIR,
        L5_SAFETY_DIR,
        L6_OBSERVABILITY_DIR,
    )


try:
    (L0_MAINTENANCE_DIR, L1_COGNITION_DIR, L2_EXECUTION_DIR,
     L3_ORCHESTRATION_DIR, L4_STATE_DIR, L5_SAFETY_DIR, L6_OBSERVABILITY_DIR) = _get_layer_dirs()
except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallow
    L0_MAINTENANCE_DIR = "agentic_core/L0_routing/maintenance"
    L1_COGNITION_DIR = "agentic_core/L1_cognition"
    L2_EXECUTION_DIR = "agentic_core/L2_execution"
    L3_ORCHESTRATION_DIR = "agentic_core/L3_orchestration"
    L4_STATE_DIR = "agentic_core/L4_state"
    L5_SAFETY_DIR = "agentic_core/L5_safety"
    L6_OBSERVABILITY_DIR = "agentic_core/L6_observability"

# 1. Bounded Contexts (Strict Boundaries)
# Sovereign Layer Hierarchy (L0=Governance, L6=observability)
# Higher ranks (smaller numbers) define Policy and Intent.
# Lower ranks (larger numbers) provide Data and Infrastructure.
BOUNDED_CONTEXTS: dict[str, dict[str, Any]] = {
    "L0_Governance": {
        "path": L0_MAINTENANCE_DIR,
        "rank": 0,
        "role": "Metacognition: The Law, Auditors, and Healers",
    },
    "L1_Cognition": {
        "path": L1_COGNITION_DIR,
        "rank": 1,
        "role": "Strategic Reasoning: Planning and Consensus",
    },
    "L2_Execution": {
        "path": L2_EXECUTION_DIR,
        "rank": 2,
        "role": "Action: Tool Implementation and Agent Realization",
    },
    "L3_Orchestration": {
        "path": L3_ORCHESTRATION_DIR,
        "rank": 3,
        "role": "Workflow: Task Fission and Fusion",
    },
    "L4_State": {
        "path": L4_STATE_DIR,
        "rank": 4,
        "role": "Memory: Persistence and Semantic Caching",
    },
    "L5_Safety": {"path": L5_SAFETY_DIR, "rank": 5, "role": "Membrane: Input/Output Sanitization"},
    "L6_Observability": {
        "path": L6_OBSERVABILITY_DIR,
        "rank": 6,
        "role": "Truth: Telemetry, Logging, and Audit Trails",
    },
    "SharedContracts": {
        "path": "apps_shared/base_agents",
        "rank": -1,  # Neutral layer, no rank in hierarchy
        "role": "Neutral Interfaces: Cross-context contracts",
    },
}

# 2. Domain Aggregates (Root Entity Protection)
DOMAIN_AGGREGATES: dict[str, dict] = {
    "Mission": {
        "root": "MissionPlan",
        "entities": ["MissionPhase", "ThoughtChain"],
        "invariants": ["Phases must be unique", "No cycles in dependency graph"],
    },
    "Thought": {
        "root": "ThoughtChain",
        "entities": ["ThinkingStep", "Hypothesis", "Revision"],
        "invariants": ["Steps must be sequential", "Conclusion is mandatory"],
    },
}

# 3. Ubiquitous Language (Required Terminology)
UBIQUITOUS_LANGUAGE: dict[str, str] = {
    "Territory": "Canonical folder with defined depth and canon key",
    "Sovereignty": "State of zero-drift SSOT compliance",
    "Fission": "Atomic decomposition of large logic files",
    "Membrane": "Zero-trust input sanitization layer",
    "Hop": "Atomic unit of agentic execution",
}
