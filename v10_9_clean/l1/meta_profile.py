"""
Meta Profile — v10_9 (L1 Cognition Layer)

Defines META_PROFILE, a deterministic configuration object
that influences how L1 planners behave.

Controls:
  • planning bias (conservative vs. expansive)
  • verbosity / explanation level
  • reasoning knobs (self-consistency depth, chain-of-thought length)
  • any debugging or experimental flags

This module MUST remain L1-only with no cross-layer imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


# ======================================================================
# META PROFILE OBJECT
# ======================================================================

@dataclass
class MetaProfile:
    """
    Declarative set of meta-level controls for L1 planning.

    Fields:
      planning_bias:
        - conservative: reduces output scope (e.g., fewer deliverables, fewer steps)
        - expansive: increases breadth (not applied by default)

      verbosity:
        Controls how much rationale/explanation L1 includes in steps.

      reasoning:
        Core meta-reasoning controls used across reasoners.
    """

    planning_bias: Dict[str, Any] = field(
        default_factory=lambda: {
            "conservative": False,        # If True → fewer steps, fewer deliverables
        }
    )

    verbosity: Dict[str, Any] = field(
        default_factory=lambda: {
            "explanations_enabled": True,  # Whether reasoners include rationale
            "detail_level": 1,             # 0 = minimal, 1 = normal, 2 = verbose
        }
    )

    reasoning: Dict[str, Any] = field(
        default_factory=lambda: {
            "self_consistency": True,      # Enable L1 consistency heuristics
            "anticipate_failure": True,    # Enable proactive failure reasoning
            "synthetic_error_check": True, # Simulate reasoning to detect weak plans
        }
    )

    debug: Dict[str, Any] = field(
        default_factory=lambda: {
            "trace_enabled": False,        # For development / internal tracing only
        }
    )


# ======================================================================
# GLOBAL META PROFILE INSTANCE
# ======================================================================

META_PROFILE = MetaProfile()
