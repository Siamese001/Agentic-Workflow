"""Provider-neutral section model limits and identity for apps_rg generation.

Relocated from the retired ``qwen_vllm_health`` module (Qwen/vLLM removal). The
context-window budget (``SECTION_MODEL_MAX_MODEL_LEN``) preserves the historical
tuned value used by prompt-truncation budgeting; the model identity defaults to the
apps_rg external Claude generation model so prompt-render manifests and X2 model-name
proofs agree with the provider that actually serves section generation.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Final

# Section input-context budget — Claude era (post-Qwen-removal 2026-06-13; raised 2026-06-15).
# The apps_rg generator is external Claude Sonnet 4.6 (~200k provider context). The old caps
# (24576 Qwen container, then 32768) were Qwen-vLLM leftovers that repeatedly token-BLOCKED
# executive_summary (its prompt + briefing + JD + C0 ~= 20k tokens hit the 95% cap at 24576/32768
# → L2_BLOCK, no generation). Default raised 32768 → 131072 (128k): generous Claude-era headroom
# (~6x exec_summary's need) with safe margin below Sonnet's 200k hard ceiling, so token caps no
# longer block any section AND the briefing/JD are no longer truncated by a tiny budget.
# Raising the CAP does not increase billed input — actual input is fixed by content; the cap only
# stops the legacy budget from rejecting it. The legacy Qwen container --max-model-len (24576) is
# the SSOT for apps_lic + agentic_core healers (VLLM_MAX_MODEL_LEN), NOT this constant.
SECTION_MODEL_MAX_MODEL_LEN: Final[int] = int(os.getenv("APPS_RG_SECTION_MAX_MODEL_LEN", "131072"))

# Fail-soft fallback ONLY. The SSOT for the apps_rg generation model is
# apps_rg/config/provider_profiles.yaml (profiles.external_claude_generator.default_model);
# this literal is used only when that YAML is unreadable so this foundational module
# (imported by ~15 section lanes + the X2 validator) never fails to import. Kept equal
# to the YAML value by tests/unit/apps_rg/test_section_model_limits_ssot.py.
DEFAULT_EXTERNAL_CLAUDE_MODEL: Final[str] = "claude-sonnet-4-6"

# Provider-profile SSOT path (apps_rg/config/provider_profiles.yaml). This module
# lives at apps_rg/runtime/, so parents[1] == apps_rg.
_PROVIDER_PROFILES_PATH: Final[Path] = (
    Path(__file__).resolve().parents[1] / "config" / "provider_profiles.yaml"
)


def _ssot_default_model() -> str | None:
    """Return ``external_claude_generator.default_model`` from the provider-profiles
    SSOT, or ``None`` when unavailable. Fail-soft — never raises."""
    try:
        import yaml  # noqa: PLC0415 — optional dep; absence falls back to literal

        data = yaml.safe_load(_PROVIDER_PROFILES_PATH.read_text(encoding="utf-8"))
        profiles = (data or {}).get("profiles") or {}
        model = (profiles.get("external_claude_generator") or {}).get("default_model")
        if model:
            return str(model).strip() or None
        return None
    except Exception:  # guardian: allow-broad-exception -- SSOT read is fail-soft; foundational module must never fail to import
        return None


def _ssot_model_by_section() -> dict[str, str]:
    """Per-section model overrides from the provider-profiles SSOT
    (``external_claude_generator.model_by_section``). Fail-soft — ``{}`` when unavailable."""
    try:
        import yaml  # noqa: PLC0415 — optional dep; absence yields {} (default model)

        data = yaml.safe_load(_PROVIDER_PROFILES_PATH.read_text(encoding="utf-8"))
        profiles = (data or {}).get("profiles") or {}
        raw = (profiles.get("external_claude_generator") or {}).get("model_by_section") or {}
        if not isinstance(raw, dict):
            return {}
        return {
            str(k).strip().lower(): str(v).strip()
            for k, v in raw.items()
            if str(k).strip() and str(v).strip()
        }
    except Exception:  # guardian: allow-broad-exception -- SSOT read is fail-soft; foundational module must never fail to import
        return {}


def resolve_section_generation_model(
    section_id: str | None,
    environ: Mapping[str, str] | None = None,
) -> str:
    """THE single resolver for the apps_rg per-section generator model (SSOT-backed).

    Every apps_rg generation dispatch MUST route the model through this function so the
    provider request carries the per-section model and no other source (agentic_core
    ``reasoning_types`` default, ``.env``, or a hardcoded literal) can win.

    Precedence:
      1. ``APPS_RG_EXTERNAL_CLAUDE_MODEL`` env pin (operator override — ALL sections)
      2. ``provider_profiles.yaml`` ``external_claude_generator.model_by_section[section]``
      3. ``provider_profiles.yaml`` ``external_claude_generator.default_model``
      4. ``DEFAULT_EXTERNAL_CLAUDE_MODEL`` literal fallback (YAML unreadable)
    """
    env = os.environ if environ is None else environ
    pin = str(env.get("APPS_RG_EXTERNAL_CLAUDE_MODEL") or "").strip()
    if pin:
        return pin
    sid = str(section_id or "").strip().lower()
    if sid:
        by_section = _ssot_model_by_section()
        if sid in by_section:
            return by_section[sid]
    return _ssot_default_model() or DEFAULT_EXTERNAL_CLAUDE_MODEL


def external_claude_generation_model(environ: Mapping[str, str] | None = None) -> str:
    """Section-agnostic default generator model (no per-section override).

    Equivalent to ``resolve_section_generation_model(None)`` — returns the operator pin or
    the SSOT ``default_model``. Callers that know their section MUST prefer
    :func:`resolve_section_generation_model` so the per-section tier applies.
    """
    return resolve_section_generation_model(None, environ)


# Canonical generation model identity for apps_rg sections — resolved from the external
# Claude generation profile (``provider_profiles.yaml`` -> external_claude_generator) so the
# X2 ``x2_model_name_allowed`` proof and prompt-render manifests reference the real provider model.
SECTION_MODEL_ID: Final[str] = external_claude_generation_model()

__all__ = [
    "DEFAULT_EXTERNAL_CLAUDE_MODEL",
    "SECTION_MODEL_ID",
    "SECTION_MODEL_MAX_MODEL_LEN",
    "external_claude_generation_model",
    "resolve_section_generation_model",
]
