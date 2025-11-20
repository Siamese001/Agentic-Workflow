# FILE: meta_profile.py
"""
Unified Meta Profile (v10_10) — ADAPTIVE BIAS ENGINE

This module implements Pillar 5 (Capability Maturity).
It acts as the "Subconscious" of the agent, holding long-term biases regarding
performance, safety, and planning depth.

Responsibilities:
    1. Bias Storage: Persist preferences (Fast vs. Deep, Strict vs. Loose).
    2. Adaptive Feedback: Update biases based on runtime telemetry (spans/errors).
    3. Snapshotting: Provide a frozen view of biases for the L1 Planner.

Refactor Highlights (v10_10):
    • Strict Pydantic: Extends `models.MetaProfile`.
    • Active Logic: `update_from_spans` calculates heuristics dynamically.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from models import (
    MetaProfile, 
    TraceSpan,
    AgenticBaseModel
)

# =============================================================================
# THE BIAS ENGINE
# =============================================================================

class MetaProfileEngine:
    """
    Manages the adaptive state of the agent.
    """
    
    def __init__(self):
        # The active state (Pydantic Model)
        self._profile = MetaProfile()

    @property
    def profile(self) -> MetaProfile:
        """Read-only view."""
        return self._profile.model_copy()

    # -------------------------------------------------------------------------
    # ADAPTIVE LOGIC (The "Learning" Loop)
    # -------------------------------------------------------------------------

    def update_from_spans(self, spans: List[TraceSpan]) -> None:
        """
        Heuristic: Latency Analysis.
        If 'Planning' takes 2x longer than 'Execution', we are over-thinking.
        Action: Enable Fast Routing Bias.
        """
        planning_ms = 0.0
        execution_ms = 0.0

        for s in spans:
            if s.name == "l1_planning": # Name from L1
                planning_ms += s.duration_ms()
            elif s.name == "l3_execution": # Name from L3
                execution_ms += s.duration_ms()

        # Threshold Check
        if planning_ms > 0 and execution_ms > 0:
            if planning_ms > (execution_ms * 2.0):
                self._set_bias("bias_routing_fast", True, "Planning latency detected.")
            else:
                # Cool down / Reset if healthy
                if self._profile.bias_routing_fast:
                    self._set_bias("bias_routing_fast", False, "Latency normalized.")

    def update_from_issues(self, issues: Dict[str, List[str]]) -> None:
        """
        Heuristic: Failure Analysis.
        If Safety or QA are blocking, we need to be more careful.
        Action: Enable Conservative Planning Bias.
        """
        # 1. Safety Blocks -> Strict Mode
        if issues.get("safety"):
            if not self._profile.bias_safety_strict:
                self._set_bias("bias_safety_strict", True, "Safety violations detected.")
        
        # 2. QA Failures -> Conservative Planning
        if issues.get("qa"):
            if not self._profile.bias_planning_conservative:
                self._set_bias("bias_planning_conservative", True, "QA failures detected.")

    # -------------------------------------------------------------------------
    # INTERNAL HELPERS
    # -------------------------------------------------------------------------

    def _set_bias(self, key: str, value: bool, reason: str) -> None:
        """Atomic update with history logging."""
        # Update current state
        setattr(self._profile, key, value)
        
        # Record history (Pillar 10: Observability)
        entry = {
            "timestamp": "iso-placeholder", # In prod use datetime.utcnow()
            "change": f"{key} -> {value}",
            "reason": reason
        }
        # Keep history trim (last 50 events)
        history = self._profile.history
        history.append(entry)
        if len(history) > 50:
            history.pop(0)
        self._profile.history = history

# Global Singleton
# This instance is imported by L1/L2 to read biases
META_PROFILE = MetaProfileEngine()

# Helper accessors for cleaner imports in other files
def get_planning_bias() -> Dict[str, bool]:
    p = META_PROFILE.profile
    return {
        "conservative": p.bias_planning_conservative,
        # Derived bias: if we are conservative, we are usually not exploratory
        "exploratory": not p.bias_planning_conservative 
    }

def get_routing_bias() -> Dict[str, bool]:
    p = META_PROFILE.profile
    return {
        "prefer_fast": p.bias_routing_fast,
        "prefer_robust_retrieval": p.bias_planning_conservative # Correlated
    }

def get_safety_bias() -> Dict[str, bool]:
    p = META_PROFILE.profile
    return {
        "heightened_caution": p.bias_safety_strict
    }

def get_meta_profile_snapshot() -> Dict[str, Any]:
    return META_PROFILE.profile.model_dump()
