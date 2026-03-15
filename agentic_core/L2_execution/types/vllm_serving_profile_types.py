"""
WAVE 1 — Authoritative vLLM Serving Profiles for 32GB GPU.

Defines pinned serving profiles for LOCAL_FAST_7B and LOCAL_STRONG_14B,
config validation guards, and the co-change invariant enforcement.

No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

GPU_MEMORY_UTILIZATION: float = 0.85
GPU_VRAM_GB: int = 32
LOCAL_FAST_7B_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
LOCAL_FAST_7B_MAX_MODEL_LEN: int = 8192
LOCAL_FAST_7B_MAX_NUM_SEQS: int = 4
LOCAL_FAST_7B_GPU_MEMORY_UTILIZATION: float = GPU_MEMORY_UTILIZATION
LOCAL_STRONG_14B_MODEL: str = "Qwen/Qwen2.5-14B-Instruct"
LOCAL_STRONG_14B_MAX_MODEL_LEN: int = 4096
LOCAL_STRONG_14B_MAX_NUM_SEQS: int = 2
LOCAL_STRONG_14B_GPU_MEMORY_UTILIZATION: float = GPU_MEMORY_UTILIZATION
LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING: int = 8192


@dataclass(frozen=True)
class VLLMServingProfile:
    """Immutable serving profile for a vLLM tier.

    Validated at construction time. Startup fails on invalid config.
    """

    profile_name: str
    model: str
    max_model_len: int
    max_num_seqs: int
    gpu_memory_utilization: float

    def __post_init__(self) -> None:
        if self.max_model_len <= 0:
            raise VLLMServingProfileInvalid(
                profile=self.profile_name, reason=f"max_model_len={self.max_model_len} must be > 0"
            )
        if self.max_num_seqs <= 0:
            raise VLLMServingProfileInvalid(
                profile=self.profile_name, reason=f"max_num_seqs={self.max_num_seqs} must be > 0"
            )
        if not 0.0 < self.gpu_memory_utilization <= 1.0:
            raise VLLMServingProfileInvalid(
                profile=self.profile_name,
                reason=f"gpu_memory_utilization={self.gpu_memory_utilization} must be in (0.0, 1.0]",
            )
        if "14B" in self.profile_name and self.max_model_len > LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING:
            raise VLLMServingProfileInvalid(
                profile=self.profile_name,
                reason=f"max_model_len={self.max_model_len} exceeds LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING={LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING} — hard fail at startup",
            )


class VLLMServingProfileInvalid(Exception):
    """Raised when a serving profile fails validation.

    Triggers hard fail at startup — never silently ignored.
    """

    def __init__(self, profile: str, reason: str) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "VLLMServingProfileInvalid.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "VLLMServingProfileInvalid.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "VLLMServingProfileInvalid.__init__"
        )
        self.profile = profile
        self.reason = reason
        super().__init__(f"VLLMServingProfileInvalid: profile={profile!r}, reason={reason}")


PROFILE_LOCAL_FAST_7B: VLLMServingProfile = VLLMServingProfile(
    profile_name="LOCAL_FAST_7B",
    model=LOCAL_FAST_7B_MODEL,
    max_model_len=LOCAL_FAST_7B_MAX_MODEL_LEN,
    max_num_seqs=LOCAL_FAST_7B_MAX_NUM_SEQS,
    gpu_memory_utilization=LOCAL_FAST_7B_GPU_MEMORY_UTILIZATION,
)
PROFILE_LOCAL_STRONG_14B: VLLMServingProfile = VLLMServingProfile(
    profile_name="LOCAL_STRONG_14B",
    model=LOCAL_STRONG_14B_MODEL,
    max_model_len=LOCAL_STRONG_14B_MAX_MODEL_LEN,
    max_num_seqs=LOCAL_STRONG_14B_MAX_NUM_SEQS,
    gpu_memory_utilization=LOCAL_STRONG_14B_GPU_MEMORY_UTILIZATION,
)
SERVING_PROFILE_REGISTRY: dict[str, VLLMServingProfile] = {
    "local_fast": PROFILE_LOCAL_FAST_7B,
    "local_strong": PROFILE_LOCAL_STRONG_14B,
}


def assert_no_simultaneous_increase(
    old_max_model_len: int,
    new_max_model_len: int,
    old_max_num_seqs: int,
    new_max_num_seqs: int,
    profile_name: str,
) -> None:
    """Enforce: max_model_len and max_num_seqs cannot both increase in same commit.

    Args:
        old_max_model_len: Previous max_model_len value.
        new_max_model_len: Proposed new max_model_len value.
        old_max_num_seqs: Previous max_num_seqs value.
        new_max_num_seqs: Proposed new max_num_seqs value.
        profile_name: Profile name for error reporting.

    Raises:
        VLLMCoChangeViolation: If both values increase simultaneously.
    """
    model_len_increased = new_max_model_len > old_max_model_len
    num_seqs_increased = new_max_num_seqs > old_max_num_seqs
    if model_len_increased and num_seqs_increased:
        raise VLLMCoChangeViolation(
            profile=profile_name,
            old_max_model_len=old_max_model_len,
            new_max_model_len=new_max_model_len,
            old_max_num_seqs=old_max_num_seqs,
            new_max_num_seqs=new_max_num_seqs,
        )


class VLLMCoChangeViolation(Exception):
    """Raised when max_model_len and max_num_seqs both increase simultaneously.

    This invariant prevents KV-cache OOM on 32GB GPU.
    """

    def __init__(
        self,
        profile: str,
        old_max_model_len: int,
        new_max_model_len: int,
        old_max_num_seqs: int,
        new_max_num_seqs: int,
    ) -> None:
        self.profile = profile
        self.old_max_model_len = old_max_model_len
        self.new_max_model_len = new_max_model_len
        self.old_max_num_seqs = old_max_num_seqs
        self.new_max_num_seqs = new_max_num_seqs
        super().__init__(
            f"VLLMCoChangeViolation: profile={profile!r} — max_model_len {old_max_model_len}->{new_max_model_len} AND max_num_seqs {old_max_num_seqs}->{new_max_num_seqs} both increased simultaneously. Only one may increase per commit."
        )


def get_profile(tier: str) -> VLLMServingProfile:
    """Retrieve serving profile by tier name.

    Args:
        tier: Tier name ("local_fast" or "local_strong").

    Returns:
        VLLMServingProfile for the requested tier.

    Raises:
        KeyError: If tier is not in SERVING_PROFILE_REGISTRY.
    """
    if tier not in SERVING_PROFILE_REGISTRY:
        msg = f"Unknown tier {tier!r}. Valid tiers: {sorted(SERVING_PROFILE_REGISTRY)}"
        raise KeyError(msg)
    return SERVING_PROFILE_REGISTRY[tier]


__all__ = [
    "GPU_MEMORY_UTILIZATION",
    "GPU_VRAM_GB",
    "LOCAL_FAST_7B_GPU_MEMORY_UTILIZATION",
    "LOCAL_FAST_7B_MAX_MODEL_LEN",
    "LOCAL_FAST_7B_MAX_NUM_SEQS",
    "LOCAL_FAST_7B_MODEL",
    "LOCAL_STRONG_14B_GPU_MEMORY_UTILIZATION",
    "LOCAL_STRONG_14B_MAX_MODEL_LEN",
    "LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING",
    "LOCAL_STRONG_14B_MAX_NUM_SEQS",
    "LOCAL_STRONG_14B_MODEL",
    "PROFILE_LOCAL_FAST_7B",
    "PROFILE_LOCAL_STRONG_14B",
    "SERVING_PROFILE_REGISTRY",
    "VLLMCoChangeViolation",
    "VLLMServingProfile",
    "VLLMServingProfileInvalid",
    "assert_no_simultaneous_increase",
    "get_profile",
]
