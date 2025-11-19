# FILE: meta_profile.py
"""
Meta Profile & Adaptive Biases (v10_9) — META LAYER ONLY (RESTORED/ENHANCED)

This module defines the global meta-profile for the v10_9 agentic
architecture. It captures *soft preferences* and *adaptive learned
biases* that are NOT part of the core L1–L5 logic, but are used by:

    • L1 Strategy / RAG planners:
        – adjust reasoning strategy (CoT → ToT with critique)
        – adjust depth/complexity thresholds
        – adjust domain emphasis based on prior failures

    • L2 Execution (drafting, QA, RAG):
        – adjust model preferences (fast vs high-precision)
        – adjust evidence weighting thresholds
        – modify QA tolerance for re-checks

    • L3 Orchestration:
        – adjust retry vs replan vs escalate tendencies
        – adjust concurrency hints (parallel nodes vs sequential safety path)

    • L4 State / Memory:
        – meta-signals for memory pruning severity
        – storing meta-traces for future runs

    • L5 Safety / Policy:
        – adjust strictness mode (STRICT/BALANCED/PERMISSIVE)
        – intensify or relax constitutional constraints

Agentic Guardrails:
    • NO planning (L1)
    • NO execution (L2)
    • NO orchestration (L3)
    • NO state mutation (L4)
    • NO safety decisions (L5)
    • deterministic + pure-data only

The META PROFILE provides:
    • persistent meta-biases
    • adaptive biasing surfaces (learned from self-correction)
    • routing biases
    • safety biases
    • cost / latency biases
    • reasoning mode biases
    • cross-run tendencies (retry vs replan vs escalate)
    • observability-driven bias adjustments

This fully restores the v10_8 “Meta Profile + Cross-Run Bias Learning”
that was lost in the v10_9 simplification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


# ============================================================================
# 1. META-BIAS CATEGORY STRUCTURES
# ============================================================================


@dataclass
class RoutingBias:
    """
    Routing-level preferences.
    These are *hints only* for L2/L3/L5 routing models and providers.

    Fields:
        prefer_fast:     opt for cheaper/faster models when safe
        prefer_strict:   opt for safer/more accurate models
        prefer_long_ctx: prefer long context windows
        prefer_high_precision: prefer higher-capability models on complex tasks
    """
    prefer_fast: bool = False
    prefer_strict: bool = False
    prefer_long_ctx: bool = False
    prefer_high_precision: bool = False


@dataclass
class ReasoningBias:
    """
    L1 reasoning preferences.

    Fields:
        use_cot:           prefer Chain-of-Thought
        use_tot:           prefer Tree-of-Thought
        enable_critique:   prefer reflective critique phase
        depth:             "shallow" / "standard" / "deep"
        conservative_mode: prefer safer, narrower planning when risky
    """
    use_cot: bool = True
    use_tot: bool = False
    enable_critique: bool = False
    depth: str = "standard"
    conservative_mode: bool = False


@dataclass
class SafetyBias:
    """
    Soft safety preferences (mapped into L5 SafetyMode + SafetyConfig).

    Fields:
        heightened_caution:  intense safety scanning
        reduce_false_pos:    relax heuristics to avoid unnecessary blocks
        enforce_constitutional: always apply constitutional layer
        escalate_on_uncertainty: recommend escalation when ambiguous
    """
    heightened_caution: bool = False
    reduce_false_pos: bool = False
    enforce_constitutional: bool = True
    escalate_on_uncertainty: bool = False


@dataclass
class CostLatencyBias:
    """
    Cost/latency preferences.

    Fields:
        cost_sensitivity:  "low" | "medium" | "high"
        latency_target_ms: numerical latency target for L2 routing
        prefer_cached:      preference for cached retrieval (predictive caching)
    """
    cost_sensitivity: str = "medium"
    latency_target_ms: int = 2000
    prefer_cached: bool = True


@dataclass
class CorrectionBias:
    """
    Cross-run self-correction tendencies.

    Fields:
        retry_preference:  prefer retrying L2 execution
        replan_preference: prefer regenerating plan from L1
        escalate_preference: prefer escalate→HIL path
        avoid_redundant_steps: bias toward eliminating redundant nodes
    """
    retry_preference: float = 0.4
    replan_preference: float = 0.3
    escalate_preference: float = 0.1
    avoid_redundant_steps: bool = True


@dataclass
class ObservabilityBias:
    """
    Observability-based meta preferences.

    Fields:
        enable_span_tracing: whether to activate detailed span events
        enable_cost_tracing: track tokens & cost precisely
        enable_failure_patterns: detect recurring patterns across runs
    """
    enable_span_tracing: bool = True
    enable_cost_tracing: bool = True
    enable_failure_patterns: bool = True


@dataclass
class ToneBias:
    """
    High-level tone preferences used by L1/L2.

    Fields:
        tone:        "professional" | "executive" | "technical" | "casual"
        intensity:   1–10 (how assertive content feels)
        avoid_jargon: avoid domain-heavy language
    """
    tone: str = "professional"
    intensity: int = 5
    avoid_jargon: bool = False


# ============================================================================
# 2. META PROFILE (FULL STATE)
# ============================================================================


@dataclass
class MetaProfile:
    """
    Full META profile capturing all adaptive biases.

    This is stored in a singleton and only read by higher layers.
    """

    routing_bias: RoutingBias = field(default_factory=RoutingBias)
    reasoning_bias: ReasoningBias = field(default_factory=ReasoningBias)
    safety_bias: SafetyBias = field(default_factory=SafetyBias)
    cost_latency_bias: CostLatencyBias = field(default_factory=CostLatencyBias)
    correction_bias: CorrectionBias = field(default_factory=CorrectionBias)
    observability_bias: ObservabilityBias = field(default_factory=ObservabilityBias)
    tone_bias: ToneBias = field(default_factory=ToneBias)

    # Historical signals (learned across runs)
    history_signals: List[Dict[str, Any]] = field(default_factory=list)

    def snapshot(self) -> Dict[str, Any]:
        """Return a deep pure-data snapshot."""
        return {
            "routing_bias": self.routing_bias.__dict__,
            "reasoning_bias": self.reasoning_bias.__dict__,
            "safety_bias": self.safety_bias.__dict__,
            "cost_latency_bias": self.cost_latency_bias.__dict__,
            "correction_bias": self.correction_bias.__dict__,
            "observability_bias": self.observability_bias.__dict__,
            "tone_bias": self.tone_bias.__dict__,
            "history": [dict(h) for h in self.history_signals],
        }

    def record_signal(self, signal: Dict[str, Any]) -> None:
        """
        Used by L4/L5/meta-learning to store new signals.

        Example:
            META_PROFILE.record_signal({"type": "qa_failure", "count": 3})
        """
        self.history_signals.append(dict(signal))

        # Adaptive auto-adjustments (subset of v10_8 behavior)
        if signal.get("type") == "qa_failure":
            self.reasoning_bias.enable_critique = True
            self.reasoning_bias.use_tot = True
            self.safety_bias.heightened_caution = True

        if signal.get("type") == "safety_block":
            self.safety_bias.escalate_on_uncertainty = True
            self.reasoning_bias.conservative_mode = True


# Global singleton
META_PROFILE = MetaProfile()


# ============================================================================
# 3. PUBLIC READ-ONLY ACCESSORS
# ============================================================================

def get_routing_bias() -> Dict[str, Any]:
    """Return routing-level meta-biases."""
    return dict(META_PROFILE.routing_bias.__dict__)


def get_reasoning_bias() -> Dict[str, Any]:
    """Return reasoning-level meta-biases."""
    return dict(META_PROFILE.reasoning_bias.__dict__)


def get_safety_bias() -> Dict[str, Any]:
    """Return safety-level meta-biases."""
    return dict(META_PROFILE.safety_bias.__dict__)


def get_cost_latency_bias() -> Dict[str, Any]:
    """Return cost/latency routing biases."""
    return dict(META_PROFILE.cost_latency_bias.__dict__)


def get_correction_bias() -> Dict[str, Any]:
    """Return adaptive retry/replan tendencies."""
    return dict(META_PROFILE.correction_bias.__dict__)


def get_observability_bias() -> Dict[str, Any]:
    """Return observability-level adaptive biases."""
    return dict(META_PROFILE.observability_bias.__dict__)


def get_tone_bias() -> Dict[str, Any]:
    """Return tone/jargon preferences."""
    return dict(META_PROFILE.tone_bias.__dict__)


def get_meta_profile_snapshot() -> Dict[str, Any]:
    """Return full snapshot of the meta profile for debugging."""
    return META_PROFILE.snapshot()
