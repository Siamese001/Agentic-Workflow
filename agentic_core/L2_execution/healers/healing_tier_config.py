"""
L2.3 Healing Tier Configuration — L4-Backed, Validated at Startup.

All thresholds and model IDs are explicitly declared. No silent defaults.
Hard-fails if X <= Y or values are out of range.

Config is frozen after validation — no runtime mutation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HealingTierConfig:
    """Immutable, validated configuration for the L2.3 healing tier router.

    Attributes:
        heal_confidence_x: Upper threshold. heal_confidence >= X → LOCAL_AGENT.
        heal_confidence_y: Lower threshold. Y <= heal_confidence < X → QWEN_VLLM.
                           heal_confidence < Y → GEMINI_2_5_PRO.
        max_heal_retries: Maximum heal attempts before forcing GEMINI_2_5_PRO.
        model_qwen_vllm_id: Model identifier for the Qwen vLLM backend.
        model_gemini_2_5_pro_id: Model identifier for the Gemini 2.5 Pro backend.
    """

    heal_confidence_x: float
    heal_confidence_y: float
    max_heal_retries: int
    model_qwen_vllm_id: str
    model_gemini_2_5_pro_id: str

    def __post_init__(self) -> None:
        if not (0.0 < self.heal_confidence_x <= 1.0):
            raise ValueError(f"heal_confidence_x must be in (0.0, 1.0], got {self.heal_confidence_x}")
        if not (0.0 <= self.heal_confidence_y < 1.0):
            raise ValueError(f"heal_confidence_y must be in [0.0, 1.0), got {self.heal_confidence_y}")
        if self.heal_confidence_x <= self.heal_confidence_y:
            raise ValueError(
                f"heal_confidence_x ({self.heal_confidence_x}) must be > "
                f"heal_confidence_y ({self.heal_confidence_y})"
            )
        if self.max_heal_retries < 1:
            raise ValueError(f"max_heal_retries must be >= 1, got {self.max_heal_retries}")
        if not self.model_qwen_vllm_id:
            raise ValueError("model_qwen_vllm_id must not be empty")
        if not self.model_gemini_2_5_pro_id:
            raise ValueError("model_gemini_2_5_pro_id must not be empty")


def load_default_healing_tier_config() -> HealingTierConfig:
    """Load the canonical default healing tier config.

    In production, these values would be loaded from L4 state store.
    This function provides the explicit, auditable defaults.

    Returns:
        Validated HealingTierConfig instance.
    """
    return HealingTierConfig(
        heal_confidence_x=0.75,
        heal_confidence_y=0.40,
        max_heal_retries=3,
        model_qwen_vllm_id="qwen2.5-coder-32b-instruct",
        model_gemini_2_5_pro_id="gemini-2.5-pro",
    )


__all__ = [
    "HealingTierConfig",
    "load_default_healing_tier_config",
]
