"""
Injection Profiles — v10_9 (L1 Cognition Layer)

Defines DEFAULT_FRAMING_PROFILE, which provides:
  • global goal framing
  • success criteria
  • task mode
  • scope boundaries
  • cost/latency targets

L1 reasoners attach this framing into PlanObject instances via
injection_framing. This allows L2/L3/L5 processors to reference
end-to-end constraints without performing L1-level cognition.

This module MUST contain no imports from L2/L3/L4/L5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# ======================================================================
# PROFILE DATA STRUCTURES
# ======================================================================

@dataclass
class FramingProfile:
    """
    Declarative profile controlling how L1 planners frame tasks
    before handing them to L2 and L3 layers.

    All fields are purely descriptive:
      • no logic
      • no cross-layer dependencies
      • no model calls
    """

    global_goal: str = "Produce the most accurate, structured, reliable output possible."
    success_criteria: List[str] = field(
        default_factory=lambda: [
            "Factual accuracy",
            "Logical consistency",
            "Structured outputs",
            "No hallucination",
            "Relevance to the user objective",
        ]
    )
    task_mode: str = "deterministic"
    scope_boundaries: Dict[str, str] = field(
        default_factory=lambda: {
            "allowed": "planning, drafting, reasoning",
            "disallowed": "model execution, tool invocation, state mutation",
        }
    )
    cost_latency: Dict[str, int] = field(
        default_factory=lambda: {
            "max_tokens": 2000,
            "max_latency_ms": 3000,
        }
    )


# ======================================================================
# DEFAULT FRAMING PROFILE
# ======================================================================

DEFAULT_FRAMING_PROFILE = FramingProfile()
