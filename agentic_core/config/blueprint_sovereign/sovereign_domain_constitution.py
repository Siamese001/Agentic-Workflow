from __future__ import annotations
"""
Sovereign Domain Constitution – DDD Alignment (Dec 26, 2025)
Defines Bounded Contexts, Aggregates, and Ubiquitous Language.
L0-L6 Sovereign Stack Hierarchy established.
"""
from typing import Any, Dict, List

# 1. Bounded Contexts (Strict Boundaries)
# Sovereign Layer Hierarchy (L0=Governance, L6=Observability)
# Higher ranks (smaller numbers) define Policy and Intent.
# Lower ranks (larger numbers) provide Data and Infrastructure.
BOUNDED_CONTEXTS: Dict[str, Dict[str, Any]] = {
    "L0_Governance": {
        "path": "agentic_core/L0_maintenance",
        "rank": 0,
        "role": "Metacognition: The Law, Auditors, and Healers"
    },
    "L1_Cognition": {
        "path": "agentic_core/L1_cognition",
        "rank": 1,
        "role": "Strategic Reasoning: Planning and Consensus"
    },
    "L2_Execution": {
        "path": "agentic_core/L2_execution",
        "rank": 2,
        "role": "Action: Tool Implementation and Agent Realization"
    },
    "L3_Orchestration": {
        "path": "agentic_core/L3_orchestration",
        "rank": 3,
        "role": "Workflow: Task Fission and Fusion"
    },
    "L4_State": {
        "path": "agentic_core/L4_state",
        "rank": 4,
        "role": "Memory: Persistence and Semantic Caching"
    },
    "L5_Safety": {
        "path": "agentic_core/L5_safety",
        "rank": 5,
        "role": "Membrane: Input/Output Sanitization"
    },
    "L6_Observability": {
        "path": "agentic_core/L6_observability",
        "rank": 6,
        "role": "Truth: Telemetry, Logging, and Audit Trails"
    },
    "SharedContracts": {
        "path": "apps_shared/base_agents",
        "rank": -1,  # Neutral layer, no rank in hierarchy
        "role": "Neutral Interfaces: Cross-context contracts"
    }
}

# 2. Domain Aggregates (Root Entity Protection)
DOMAIN_AGGREGATES: Dict[str, Dict] = {
    "Mission": {
        "root": "MissionPlan",
        "entities": ["MissionPhase", "ThoughtChain"],
        "invariants": ["Phases must be unique", "No cycles in dependency graph"]
    },
    "Thought": {
        "root": "ThoughtChain",
        "entities": ["ThinkingStep", "Hypothesis", "Revision"],
        "invariants": ["Steps must be sequential", "Conclusion is mandatory"]
    }
}

# 3. Ubiquitous Language (Required Terminology)
UBIQUITOUS_LANGUAGE: Dict[str, str] = {
    "Territory": "Canonical folder with defined depth and canon key",
    "Sovereignty": "State of zero-drift SSOT compliance",
    "Fission": "Atomic decomposition of large logic files",
    "Membrane": "Zero-trust input sanitization layer",
    "Hop": "Atomic unit of agentic execution",
}
