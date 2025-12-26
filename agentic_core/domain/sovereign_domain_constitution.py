"""
Sovereign Domain Constitution – DDD Alignment (Dec 26, 2025)
Defines Bounded Contexts, Aggregates, and Ubiquitous Language.
"""
from typing import List, Dict

# 1. Bounded Contexts (Strict Boundaries)
BOUNDED_CONTEXTS: Dict[str, List[str]] = {
    "Cognition": ["agentic_core/L1_cognition"],
    "Execution": ["agentic_core/L2_execution"],
    "Orchestration": ["agentic_core/L3_orchestration"],
    "State": ["agentic_core/L4_state"],
    "Safety": ["agentic_core/L5_safety"],
    "SemanticMemory": ["agentic_core/semantic_memory"],
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
