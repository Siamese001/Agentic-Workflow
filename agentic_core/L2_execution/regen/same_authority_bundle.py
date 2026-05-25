"""Frozen authority bundle carried across same-authority regen."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SameAuthorityBundle:
    """Immutable authority snapshot for one regen heal evaluation."""

    frozen_compile_ref: str
    system_prefix_hash: str
    policy_hash: str
    blueprint_hash: str
    registry_digest_set: tuple[str, ...]
    replay_key: str
    provider_lane: str
    model_lane: str
    capability_token: str = ""
    sandbox_envelope: str = ""
    prompt_hash: str = ""

    def __post_init__(self) -> None:
        if not self.frozen_compile_ref:
            raise ValueError("frozen_compile_ref must be non-empty")
        if not self.system_prefix_hash:
            raise ValueError("system_prefix_hash must be non-empty")
        if not self.replay_key:
            raise ValueError("replay_key must be non-empty")
