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

    @staticmethod
    def create(
        *,
        model_version: str,
        tokenizer_version: str,
        raw_prompt_bytes: bytes,
        raw_response_bytes: bytes,
    ) -> ReplayBundle:
        """Construct a bundle with computed provider checksum."""
        checksum_input = f"{model_version}+{tokenizer_version}"
        provider_checksum = hashlib.sha256(checksum_input.encode("utf-8")).hexdigest()
        return ReplayBundle(
            model_version=model_version,
            tokenizer_version=tokenizer_version,
            raw_prompt_bytes=raw_prompt_bytes,
            raw_response_bytes=raw_response_bytes,
            provider_checksum=provider_checksum,
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


def validate_production_mode(mode: ReplayMode) -> None:
    """Raise if mode is not allowed in production."""
    if mode not in PRODUCTION_ALLOWED_MODES:
        raise ValueError(
            f"ReplayMode.{mode.name} is not allowed in "
            f"production. Only {PRODUCTION_ALLOWED_MODES} "
            f"are permitted."
        )
