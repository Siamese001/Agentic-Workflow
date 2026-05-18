"""Runtime generation mode for ``GenerateResumeStep`` (env-flagged).

Canonical **proven** generation style for integrated R4 is documented in
``apps_rg.l2_recipe.r4_generation_route`` (``modular_section_lanes``). **Default** when
unset is ``modular_section_lanes``. Set ``APPS_RG_R4_GENERATION_MODE=legacy_full_resume``
for explicit monolithic envelope rollback.

``APPS_RG_R4_GENERATION_MODE`` selects how the recipe obtains structured résumé JSON:

- unset / empty → ``modular_section_lanes`` (``run_modular_resume_generation``; no envelope)
- ``legacy_full_resume`` → monolithic ``run_apps_rg_l2_envelope``
- ``modular_section_lanes`` → same modular path as default

For modular mode, section dispatch ``--provider`` defaults to ``qwen_vllm``
(``VLLM_BASE_URL`` / ``QWEN_VLLM_MODEL`` per ``qwen_vllm_provider``). Contract
tests may set ``APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1`` for deterministic output
without a live server.

Invalid values fail closed with ``RuntimeError`` (no silent coercion to ``legacy_full_resume``).
"""

from __future__ import annotations

import os
from typing import Final, Literal

ENV_APPS_RG_R4_GENERATION_MODE: Final[str] = "APPS_RG_R4_GENERATION_MODE"
ENV_APPS_RG_MODULAR_LANE_PROVIDER: Final[str] = "APPS_RG_MODULAR_LANE_PROVIDER"
MODE_MODULAR_SECTION_LANES: Final[str] = "modular_section_lanes"
MODE_LEGACY_FULL_RESUME: Final[str] = "legacy_full_resume"

_MODULAR_LANE_PROVIDER_ALLOWED: Final[frozenset[str]] = frozenset({"qwen_vllm"})

AppsRgR4GenerationMode = Literal["legacy_full_resume", "modular_section_lanes"]


def resolve_apps_rg_r4_generation_mode() -> AppsRgR4GenerationMode:
    """Return generation mode from ``APPS_RG_R4_GENERATION_MODE``.

    Default when unset is ``modular_section_lanes``. Use ``legacy_full_resume`` only as
    explicit rollback (monolithic envelope).
    """
    raw = os.environ.get(ENV_APPS_RG_R4_GENERATION_MODE, "").strip().lower()
    if not raw:
        return MODE_MODULAR_SECTION_LANES
    if raw == MODE_LEGACY_FULL_RESUME:
        return MODE_LEGACY_FULL_RESUME
    if raw == MODE_MODULAR_SECTION_LANES:
        return MODE_MODULAR_SECTION_LANES
    msg = (
        f"INVALID_APPS_RG_R4_GENERATION_MODE: {raw!r} "
        f"(expected {MODE_MODULAR_SECTION_LANES!r} or {MODE_LEGACY_FULL_RESUME!r})"
    )
    raise RuntimeError(msg)


def resolve_apps_rg_modular_lane_provider() -> str:
    """Section-lane provider for R4 modular Phase 1 dispatch argv (``--provider``).

    Default ``qwen_vllm`` targets local OpenAI-compatible vLLM (see
    ``VLLM_BASE_URL``, ``QWEN_VLLM_MODEL``). Tests may use
    ``APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1`` instead of a live server.
    """
    raw = os.environ.get(ENV_APPS_RG_MODULAR_LANE_PROVIDER, "").strip().lower()
    if not raw:
        return "qwen_vllm"
    if raw not in _MODULAR_LANE_PROVIDER_ALLOWED:
        msg = (
            f"INVALID_APPS_RG_MODULAR_LANE_PROVIDER: {raw!r} "
            f"(expected {sorted(_MODULAR_LANE_PROVIDER_ALLOWED)!r})"
        )
        raise RuntimeError(msg)
    return raw


__all__ = [
    "AppsRgR4GenerationMode",
    "ENV_APPS_RG_MODULAR_LANE_PROVIDER",
    "ENV_APPS_RG_R4_GENERATION_MODE",
    "MODE_LEGACY_FULL_RESUME",
    "MODE_MODULAR_SECTION_LANES",
    "resolve_apps_rg_modular_lane_provider",
    "resolve_apps_rg_r4_generation_mode",
]
