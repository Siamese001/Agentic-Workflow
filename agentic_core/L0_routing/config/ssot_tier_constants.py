"""
agentic_core/L0_routing/config/ssot_tier_constants.py

L0-accessible copies of the SSOT routing/healing tier thresholds.

These constants are copied here from L2_execution/healers/healing_tier_config.py
so that L0 scripts (_ssot_reporting.py, _ssot_routing.py) can read them without
importing across the L0→L2 layer boundary.

Source of truth: agentic_core/L2_execution/healers/healing_tier_config.py
ADG fix: A-06 (violates L0→L2 in _ssot_reporting.py and _ssot_routing.py)
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_reads_policy_state("p1", "ssot_tier_constants", "L0")
_emit_escalates_to_human("p1", "ssot_tier_constants", "L0")
_emit_routes_through("p1", "ssot_tier_constants", "L0")
_emit_dispatches_healing_run("p1", "ssot_tier_constants", "L0")

# FIXED THRESHOLDS - IMMUTABLE BY META-LEARNING
HEALING_CONFIDENCE_X: float = 0.80  # Upper threshold: conf > X  → DETERMINISTIC
HEALING_CONFIDENCE_Y: float = 0.50  # Lower threshold: conf <= Y → GEMINI 2.5 Pro

# SSOT score thresholds for integer-score routing (S = 3C+4B+3A+2N+4F)
SSOT_SCORE_THRESHOLD_DET: int = 13  # S <= 13  → DETERMINISTIC
SSOT_SCORE_THRESHOLD_QWEN: int = 26  # S <= 26  → QWEN; S > 26 → GEMINI

# Qwen 14B model identifier
QWEN_14B_MODEL_ID: str = "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4"

__all__ = [
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "SSOT_SCORE_THRESHOLD_DET",
    "SSOT_SCORE_THRESHOLD_QWEN",
    "QWEN_14B_MODEL_ID",
]
