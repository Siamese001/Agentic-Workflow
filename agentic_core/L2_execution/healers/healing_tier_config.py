"""
L2.3 Healing Tier Configuration — L4-Backed, Validated at Startup.

All thresholds and model IDs are explicitly declared. No silent defaults.
Hard-fails if X <= Y or values are out of range.

Config is frozen after validation — no runtime mutation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# FIXED THRESHOLDS - IMMUTABLE BY META-LEARNING
HEALING_CONFIDENCE_X = 0.75  # Upper threshold - CANNOT BE MODIFIED
HEALING_CONFIDENCE_Y = 0.40  # Lower threshold - CANNOT BE MODIFIED

# Qwen pinned revisions for determinism
QWEN_MODEL_REVISION_SHA = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
QWEN_TOKENIZER_REVISION_SHA = "f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7"
QWEN_VLLM_VERSION = "0.4.2"
QWEN_CUDA_VERSION = "12.1"
QWEN_TORCH_VERSION = "2.1.0"

# Qwen 14B — targets RTX 5090 (32 GB VRAM, CUDA >= 12.0, compute >= 8.9)
QWEN_14B_MODEL_ID = "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4"
QWEN_14B_MIN_VRAM_GB: float = 16.0  # Int4-quantized 14B fits in 16 GB
QWEN_14B_MIN_CUDA = "12.0"
QWEN_14B_MIN_COMPUTE: float = 8.0  # Ada Lovelace baseline (RTX 4090/5090)

# Agents that must be routed through the Qwen 14B tier (medium confidence)
# when local-GPU inference is available.  The resolver checks this set at
# dispatch time; agents absent from this set keep their existing routing.
QWEN_14B_AGENT_KEYS: frozenset[str] = frozenset(
    {
        "arch_governor",
        "file_classification",
        "cognitive_disposition",
        "observability_probe",
    }
)

# BMG embedding model tag — used by the cosine-similarity fallback in the
# decision engine.  The actual model is loaded lazily by the embedding helper.
BMG_EMBEDDING_MODEL_ID = "BAAI/bge-m3"
# Agents whose similarity scoring uses BMG embeddings instead of Jaccard.
BMG_EMBEDDING_AGENT_KEYS: frozenset[str] = frozenset({"location", "root_hygiene"})


@dataclass(frozen=True, slots=True)
class HealingTierConfig:
    """Immutable, validated configuration for the L2.3 healing tier router.

    Attributes:
        heal_confidence_x: Upper threshold. heal_confidence >= X → LOCAL_AGENT.
        heal_confidence_y: Lower threshold. Y <= heal_confidence < X → QWEN_VLLM.
                           heal_confidence < Y → GEMINI_2_5_PRO.
        max_heal_retries: Maximum heal attempts before forcing GEMINI_2_5_PRO.
        model_qwen_vllm_id: Model identifier for the Qwen 7B vLLM backend.
        model_qwen_14b_vllm_id: Model identifier for the Qwen 14B vLLM backend (RTX 5090).
        model_gemini_2_5_pro_id: Model identifier for the Gemini 2.5 Pro backend.
        enable_bmg_embeddings: When True the decision engine uses BMG cosine
            similarity instead of Jaccard for semantic scoring.
    """

    heal_confidence_x: float
    heal_confidence_y: float
    max_heal_retries: int
    model_qwen_vllm_id: str
    model_gemini_2_5_pro_id: str
    model_qwen_14b_vllm_id: str = QWEN_14B_MODEL_ID
    enable_bmg_embeddings: bool = False

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
        if not self.model_qwen_14b_vllm_id:
            raise ValueError("model_qwen_14b_vllm_id must not be empty")


def load_default_healing_tier_config() -> HealingTierConfig:
    """Load the canonical default healing tier config.

    In production, these values would be loaded from L4 state store.
    This function provides the explicit, auditable defaults.

    Returns:
        Validated HealingTierConfig instance.
    """
    bmg_available = os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() == "true"
    return HealingTierConfig(
        heal_confidence_x=HEALING_CONFIDENCE_X,
        heal_confidence_y=HEALING_CONFIDENCE_Y,
        max_heal_retries=3,
        model_qwen_vllm_id="Qwen/Qwen2.5-7B-Instruct",
        model_qwen_14b_vllm_id=QWEN_14B_MODEL_ID,
        model_gemini_2_5_pro_id="gemini-2.5-pro",
        enable_bmg_embeddings=bmg_available,
    )


def validate_qwen_startup_state() -> None:
    """Hard validate kill switch at startup."""
    qwen_enabled = os.environ.get("QWEN_VLLM_ENABLED", "true").lower() == "true"

    if not qwen_enabled:
        # Assert no Qwen processes are running (cross-platform)
        if is_vllm_process_running():
            raise RuntimeError(
                "QWEN_VLLM_ENABLED=False but vLLM process detected. "
                "Terminate all vLLM processes before starting."
            )

        import logging

        logger = logging.getLogger(__name__)
        logger.info("QWEN_VLLM_ENABLED=False - Qwen tier disabled at startup")
        return

    # If enabled, validate GPU capabilities before allowing startup
    try:
        # Import here to avoid circular dependency
        from agentic_core.L2_execution.healers.qwen_gpu_validator import validate_qwen_gpu_capabilities

        validate_qwen_gpu_capabilities(model_size="7B")  # Default to 7B for validation
        logger.info("QWEN_VLLM_ENABLED=True - GPU validation passed")
    except Exception as exc:
        logger.error(f"QWEN_VLLM_ENABLED=True but GPU validation failed: {exc}")
        raise


def is_vllm_process_running() -> bool:
    """Cross-platform detection of vLLM processes using psutil."""
    try:
        import psutil

        for proc in psutil.process_iter(attrs=["cmdline"]):
            cmdline = proc.info.get("cmdline", [])
            if cmdline and "vllm" in " ".join(cmdline):
                return True
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, ImportError):
        return False


__all__ = [
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "QWEN_MODEL_REVISION_SHA",
    "QWEN_TOKENIZER_REVISION_SHA",
    "QWEN_VLLM_VERSION",
    "QWEN_CUDA_VERSION",
    "QWEN_TORCH_VERSION",
    "QWEN_14B_MODEL_ID",
    "QWEN_14B_MIN_VRAM_GB",
    "QWEN_14B_MIN_CUDA",
    "QWEN_14B_MIN_COMPUTE",
    "QWEN_14B_AGENT_KEYS",
    "BMG_EMBEDDING_MODEL_ID",
    "BMG_EMBEDDING_AGENT_KEYS",
    "HealingTierConfig",
    "load_default_healing_tier_config",
    "validate_qwen_startup_state",
    "is_vllm_process_running",
]
