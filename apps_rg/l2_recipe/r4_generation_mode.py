"""Runtime generation mode for ``GenerateResumeStep`` (env-flagged).

Canonical **proven** generation style for integrated R4 is documented in
``apps_rg.l2_recipe.r4_generation_route`` (``modular_section_lanes``). **Default** when
unset remains ``legacy_full_resume`` for explicit rollback and deterministic defaults.

``APPS_RG_R4_GENERATION_MODE`` selects how the recipe obtains structured résumé JSON:

- unset / empty → ``legacy_full_resume`` (monolithic ``run_apps_rg_l2_envelope``)
- ``modular_section_lanes`` → ``run_modular_resume_generation`` (no envelope)

For modular mode, section dispatch ``--provider`` defaults to ``mock``. Set
``APPS_RG_MODULAR_LANE_PROVIDER=qwen_vllm`` for real vLLM generation (with
``VLLM_BASE_URL`` / ``QWEN_VLLM_MODEL`` per ``qwen_vllm_provider``).

Invalid values fail closed with ``RuntimeError`` (no silent downgrade to legacy).
"""

from __future__ import annotations

import os
from typing import Final, Literal

ENV_APPS_RG_R4_GENERATION_MODE: Final[str] = "APPS_RG_R4_GENERATION_MODE"
ENV_APPS_RG_MODULAR_LANE_PROVIDER: Final[str] = "APPS_RG_MODULAR_LANE_PROVIDER"
MODE_MODULAR_SECTION_LANES: Final[str] = "modular_section_lanes"
MODE_LEGACY_FULL_RESUME: Final[str] = "legacy_full_resume"

_MODULAR_LANE_PROVIDER_ALLOWED: Final[frozenset[str]] = frozenset({"mock", "qwen_vllm"})

AppsRgR4GenerationMode = Literal["legacy_full_resume", "modular_section_lanes"]


def resolve_apps_rg_r4_generation_mode() -> AppsRgR4GenerationMode:
    """Return generation mode from ``APPS_RG_R4_GENERATION_MODE``.

    Default when unset is ``legacy_full_resume`` (preserves historic behavior).
    """
    raw = os.environ.get(ENV_APPS_RG_R4_GENERATION_MODE, "").strip().lower()
    if not raw:
        return MODE_LEGACY_FULL_RESUME
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

    Default ``mock`` preserves deterministic plumbing runs. Set
    ``APPS_RG_MODULAR_LANE_PROVIDER=qwen_vllm`` for local OpenAI-compatible vLLM
    (see ``VLLM_BASE_URL``, ``QWEN_VLLM_MODEL`` in ``qwen_vllm_provider``).
    """
    raw = os.environ.get(ENV_APPS_RG_MODULAR_LANE_PROVIDER, "").strip().lower()
    if not raw:
        return "mock"
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
