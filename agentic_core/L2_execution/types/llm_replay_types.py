"""
H3: Provider-pinned LLM replay enforcement types.

Defines the replay bundle, strategy, and mode policy for
deterministic LLM replay.  Production replay MUST use
RECORDED_OUTPUT mode.  DETERMINISTIC_INFERENCE is demoted to
dev/test only and labeled NON_AUTHORITATIVE.

Lives in L2 (execution types) per gravity rules.
"""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)
from agentic_core.utils.canonical_serializer_util import (
    canonical_bytes,
)


class ReplayMode(enum.Enum):
    """LLM replay mode policy.

    RECORDED_OUTPUT: Default for production. Uses stored raw
        response bytes verbatim.
    DETERMINISTIC_INFERENCE: Dev/test only. Re-invokes the LLM
        with temperature=0 + seed. Labeled NON_AUTHORITATIVE.
    """

    RECORDED_OUTPUT = "RECORDED_OUTPUT"
    DETERMINISTIC_INFERENCE = "DETERMINISTIC_INFERENCE"


# Modes allowed per environment
PRODUCTION_ALLOWED_MODES = frozenset({ReplayMode.RECORDED_OUTPUT})
DEV_TEST_ALLOWED_MODES = frozenset({ReplayMode.RECORDED_OUTPUT, ReplayMode.DETERMINISTIC_INFERENCE})


def is_authoritative(mode: ReplayMode) -> bool:
    """Only RECORDED_OUTPUT is authoritative for governance."""
    return mode is ReplayMode.RECORDED_OUTPUT


def mode_label(mode: ReplayMode) -> str:
    """Return the governance label for a replay mode."""
    if mode is ReplayMode.DETERMINISTIC_INFERENCE:
        return "NON_AUTHORITATIVE"
    return "AUTHORITATIVE"


@dataclass(frozen=True)
class ReplayBundle:
    """Immutable bundle of LLM interaction artifacts for replay.

    All fields are pinned at capture time and frozen.
    """

    model_version: str
    tokenizer_version: str
    raw_prompt_bytes: bytes
    raw_response_bytes: bytes
    provider_checksum: str
    replay_hash: str
    integrity_verified: bool

    @staticmethod
    def create(
        *,
        model_version: str,
        tokenizer_version: str,
        raw_prompt_bytes: bytes,
        raw_response_bytes: bytes,
    ) -> ReplayBundle:
        """Construct a bundle with computed checksums."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ReplayBundle.create")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReplayBundle.create".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        checksum_input = f"{model_version}+{tokenizer_version}"
        provider_checksum = hashlib.sha256(checksum_input.encode("utf-8")).hexdigest()
        bundle_obj = {
            "model_version": model_version,
            "tokenizer_version": tokenizer_version,
            "raw_prompt_bytes": raw_prompt_bytes.hex(),
            "raw_response_bytes": raw_response_bytes.hex(),
            "provider_checksum": provider_checksum,
        }
        replay_hash = hashlib.sha256(canonical_bytes(bundle_obj)).hexdigest()
        return ReplayBundle(
            model_version=model_version,
            tokenizer_version=tokenizer_version,
            raw_prompt_bytes=raw_prompt_bytes,
            raw_response_bytes=raw_response_bytes,
            provider_checksum=provider_checksum,
            replay_hash=replay_hash,
            integrity_verified=True,
        )

    def verify_checksum(self) -> bool:
        """Re-derive provider checksum and compare."""
        expected = hashlib.sha256(f"{self.model_version}+{self.tokenizer_version}".encode()).hexdigest()
        return expected == self.provider_checksum


@dataclass(frozen=True)
class LLMReplayStrategy:
    """Strategy for replaying an LLM interaction.

    Combines the replay bundle with the mode policy.
    """

    bundle: ReplayBundle
    mode: ReplayMode

    def replay(self) -> bytes:
        """Execute the replay strategy.

        RECORDED_OUTPUT: return stored raw_response_bytes.
        DETERMINISTIC_INFERENCE: raise (not implemented in
            production — requires explicit dev/test wiring).
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "LLMReplayStrategy.replay")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:LLMReplayStrategy.replay".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.mode is ReplayMode.RECORDED_OUTPUT:
            return self.bundle.raw_response_bytes
        raise NotImplementedError(
            "DETERMINISTIC_INFERENCE replay requires explicit "
            "dev/test wiring. This mode is NON_AUTHORITATIVE "
            "and must not be used in production."
        )

    @property
    def is_authoritative(self) -> bool:
        return is_authoritative(self.mode)

    @property
    def governance_label(self) -> str:
        return mode_label(self.mode)


def verify_replay_integrity(bundle: ReplayBundle) -> bool:
    """Re-derive replay_hash and verify bundle integrity.

    Returns True only if the re-derived hash matches the
    stored replay_hash.
    """
    bundle_obj = {
        "model_version": bundle.model_version,
        "tokenizer_version": bundle.tokenizer_version,
        "raw_prompt_bytes": bundle.raw_prompt_bytes.hex(),
        "raw_response_bytes": bundle.raw_response_bytes.hex(),
        "provider_checksum": bundle.provider_checksum,
    }
    expected = hashlib.sha256(canonical_bytes(bundle_obj)).hexdigest()
    return expected == bundle.replay_hash


def validate_production_mode(mode: ReplayMode) -> None:
    """Raise if mode is not allowed in production."""
    if mode not in PRODUCTION_ALLOWED_MODES:
        raise ValueError(
            f"ReplayMode.{mode.name} is not allowed in "
            f"production. Only {PRODUCTION_ALLOWED_MODES} "
            f"are permitted."
        )
