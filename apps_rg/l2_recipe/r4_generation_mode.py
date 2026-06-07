"""Runtime generation mode for ``GenerateResumeStep`` (env-flagged).

Canonical **proven** generation style for integrated R4 is documented in
``apps_rg.l2_recipe.r4_generation_route`` (``modular_section_lanes``). **Default** when
unset is ``modular_section_lanes``.

``APPS_RG_R4_GENERATION_MODE`` must be unset or ``modular_section_lanes`` only.
``legacy_full_resume`` is retired (no monolithic envelope rollback).

For modular mode, section dispatch ``--provider`` defaults to ``external_claude``.
``qwen_vllm`` remains explicitly selectable for local comparison runs.

Invalid values fail closed with ``RuntimeError``.
"""

from __future__ import annotations

import os
from typing import Final, Literal

ENV_APPS_RG_R4_GENERATION_MODE: Final[str] = "APPS_RG_R4_GENERATION_MODE"
ENV_APPS_RG_MODULAR_LANE_PROVIDER: Final[str] = "APPS_RG_MODULAR_LANE_PROVIDER"
MODE_MODULAR_SECTION_LANES: Final[str] = "modular_section_lanes"
RETIRED_MODE_LEGACY_FULL_RESUME: Final[str] = "legacy_full_resume"

_MODULAR_LANE_PROVIDER_ALLOWED: Final[frozenset[str]] = frozenset(
    {"qwen_vllm", "external_claude"}
)

AppsRgR4GenerationMode = Literal["modular_section_lanes"]


def resolve_apps_rg_r4_generation_mode() -> AppsRgR4GenerationMode:
    """Return generation mode from ``APPS_RG_R4_GENERATION_MODE``.

    Default when unset is ``modular_section_lanes``. ``legacy_full_resume`` raises.
    """
    raw = os.environ.get(ENV_APPS_RG_R4_GENERATION_MODE, "").strip().lower()
    if not raw:
        return MODE_MODULAR_SECTION_LANES
    if raw == RETIRED_MODE_LEGACY_FULL_RESUME:
        msg = (
            f"RETIRED_APPS_RG_R4_GENERATION_MODE: {RETIRED_MODE_LEGACY_FULL_RESUME!r} is no longer supported; "
            f"use {MODE_MODULAR_SECTION_LANES!r} (unset env for default)."
        )
        raise RuntimeError(msg)
    if raw == MODE_MODULAR_SECTION_LANES:
        return MODE_MODULAR_SECTION_LANES
    msg = (
        f"INVALID_APPS_RG_R4_GENERATION_MODE: {raw!r} "
        f"(expected unset or {MODE_MODULAR_SECTION_LANES!r})"
    )
    raise RuntimeError(msg)


def resolve_apps_rg_modular_lane_provider() -> str:
    """Section-lane provider for R4 modular Phase 1 dispatch argv (``--provider``)."""
    raw = os.environ.get(ENV_APPS_RG_MODULAR_LANE_PROVIDER, "").strip().lower()
    if not raw:
        return "external_claude"
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
    "MODE_MODULAR_SECTION_LANES",
    "RETIRED_MODE_LEGACY_FULL_RESUME",
    "resolve_apps_rg_modular_lane_provider",
    "resolve_apps_rg_r4_generation_mode",
]
