"""
Reasoning Configuration Toggles for RG Sovereign Architecture — DEFAULTS ONLY.

These are static fallback defaults used when no L0-stamped
ReasoningIntensityProfile is available (e.g. unit tests, offline mode).

GOVERNANCE: Runtime reasoning intensity is governed by the
ReasoningIntensityProfile stamped by L0 ReasoningPolicyEngine and
injected via SignedExecutionEnvelope. Do NOT add environment-based
overrides or a get_toggles() factory here.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "reasoning_toggles_config", "p0_governance")
_emit_reads_policy_state("p0", "reasoning_toggles_config", "policy_binding")
_emit_snapshots_state("p0", "reasoning_toggles_config", "state_snapshot")
emit_replay_key("p0", "reasoning_toggles_config")
emit_determinism_digest("p0", "reasoning_toggles_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class ReasoningToggles(BaseModel):
    """
    Static fallback defaults for enabling/disabling advanced reasoning features.
    Enforces strict safety bounds to prevent infinite loops or token exhaustion.

    NOTE: At runtime these values are OVERRIDDEN by the L0-stamped
    ReasoningIntensityProfile.  This class is defaults-only.
    """

    # Core Toggles
    use_cot: bool = Field(default=True, description="Enable Chain-of-Thought reasoning.")
    use_reflexion: bool = Field(default=False, description="Enable self-correction loops.")
    strict_mode: bool = Field(default=True, description="Fail on minor validation errors.")
    use_persistent_tracing: bool = Field(default=True, description="Enable persistent trace storage.")
    use_cyclic_validation: bool = Field(default=True, description="Enable cyclic retry validation.")

    # Tree of Thought Parameters
    tot_branches: int = Field(default=2, description="Number of alternative reasoning paths.")
    min_tot_depth: int = Field(default=1, description="Minimum depth for tree exploration.")

    # Sampling Parameters
    temperature_cap: float = Field(default=0.5, description="Maximum temperature.")

    @field_validator("tot_branches")
    @classmethod
    def validate_branches(cls, v: int) -> int:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReasoningToggles.validate_branches")

        if not 1 <= v <= 5:
            raise ValueError(f"tot_branches must be between 1 and 5. Got {v}.")
        return v


DEFAULT_TOGGLES = ReasoningToggles()
