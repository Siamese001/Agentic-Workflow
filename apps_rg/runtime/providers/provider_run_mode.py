"""Classify apps_rg L2 provider run intent for authenticity / stub gating (app-local)."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.providers.provider_types import ProviderKind, ProviderProfile

from apps_rg.l2_recipe.resume_generation_contract import (
    MODE_DIAGNOSTIC,
    MODE_STUB_RECEIPT,
    normalize_resume_artifact_contract_mode,
)


class ProviderRunMode(str, Enum):
    """How strict provider authenticity is for this process / request."""

    LIVE_REQUIRED = "live_required"
    EXPLICIT_STUB = "explicit_stub"
    TEST_STUB = "test_stub"
    UNKNOWN = "unknown"


class AppsRgEnvelopeProviderResolutionError(RuntimeError):
    """No non-stub profile can be resolved for the CPA (live context)."""


def _pytest_active() -> bool:
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    return "pytest" in sys.modules


def classify_provider_run_mode(
    *,
    resume_artifact_contract_mode: Any = None,
    cli_explicit_stub: bool = False,
) -> ProviderRunMode:
    """Return coarse provider-authenticity mode for the current context.

    - Normal full résumé CLI / production-like run → LIVE_REQUIRED.
    - Stub / diagnostic contract mode or explicit CLI stub → EXPLICIT_STUB.
    - Pytest / CI harness (``PYTEST_CURRENT_TEST``) → TEST_STUB.
    """
    if _pytest_active():
        return ProviderRunMode.TEST_STUB

    if cli_explicit_stub:
        return ProviderRunMode.EXPLICIT_STUB

    norm = normalize_resume_artifact_contract_mode(resume_artifact_contract_mode)
    if norm in (MODE_STUB_RECEIPT, MODE_DIAGNOSTIC):
        return ProviderRunMode.EXPLICIT_STUB

    raw = (os.environ.get("APPS_RG_L2_PROVIDER_MODE") or "").strip().lower()
    if raw in ("stub_only", "stub", "off", "0", "false", "no"):
        return ProviderRunMode.EXPLICIT_STUB

    return ProviderRunMode.LIVE_REQUIRED


_STUB_CLASS_NAME_HINTS: frozenset[str] = frozenset(
    {
        "stubprovider",
        "stubllm",
        "mockprovider",
    }
)


@dataclass(frozen=True, slots=True)
class ProviderAuthenticityViolation:
    generation_status: str
    decisive_reason: str
    decisive_reason_code: str
    full_resume_generated: bool = False


def assert_provider_authentic_for_full_resume(
    *,
    run_mode: ProviderRunMode,
    profile: ProviderProfile,
    invoker_class_name: str | None = None,
) -> ProviderAuthenticityViolation | None:
    """If LIVE_REQUIRED, forbid stub profile / stub invoker / contradictory FORCE_STUB."""
    if run_mode != ProviderRunMode.LIVE_REQUIRED:
        return None

    if os.environ.get("APPS_RG_L2_FORCE_STUB", "").strip() == "1":
        from apps_rg.l2_recipe.resume_output_shape import BLOCKED_STUB_PROVIDER

        return ProviderAuthenticityViolation(
            generation_status=BLOCKED_STUB_PROVIDER,
            decisive_reason=(
                "APPS_RG_L2_FORCE_STUB=1 is forbidden for LIVE_REQUIRED full résumé runs "
                "(use explicit stub contract mode or test harness)."
            ),
            decisive_reason_code="E3_BLOCKED_STUB_PROVIDER",
        )

    pid = str(profile.profile_id or "").lower()
    if profile.provider_kind == ProviderKind.STUB or "stub" in pid:
        from apps_rg.l2_recipe.resume_output_shape import BLOCKED_STUB_PROVIDER

        return ProviderAuthenticityViolation(
            generation_status=BLOCKED_STUB_PROVIDER,
            decisive_reason=(
                "Stub provider profile is forbidden for LIVE_REQUIRED full résumé generation."
            ),
            decisive_reason_code="E3_BLOCKED_STUB_PROVIDER",
        )

    if invoker_class_name:
        compact = invoker_class_name.replace("_", "").lower()
        for hint in _STUB_CLASS_NAME_HINTS:
            if hint in compact:
                from apps_rg.l2_recipe.resume_output_shape import BLOCKED_STUB_PROVIDER

                return ProviderAuthenticityViolation(
                    generation_status=BLOCKED_STUB_PROVIDER,
                    decisive_reason=(
                        f"Invoker {invoker_class_name!r} is classified as a stub gateway for "
                        "LIVE_REQUIRED runs."
                    ),
                    decisive_reason_code="E3_BLOCKED_STUB_PROVIDER",
                )

    return None


__all__ = [
    "AppsRgEnvelopeProviderResolutionError",
    "ProviderAuthenticityViolation",
    "ProviderRunMode",
    "assert_provider_authentic_for_full_resume",
    "classify_provider_run_mode",
]
