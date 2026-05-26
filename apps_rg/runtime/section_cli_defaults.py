"""Section CLI defaults and fail-closed input policy for ``python -m apps_rg --section <lane>``.

``executive_summary`` requires explicit ``--target-company``, ``--target-role``, ``--jd``, and
``--manual-brief`` on the CLI path (no résumé-derived company/title, no DEFAULT_SSOT JD/briefing).

Other section lanes may still use SSOT defaults under ``apps_rg/config``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Final, Literal

CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE: Final[str] = "CLI_OVERRIDE"
CLI_PROVIDER_RESOLUTION_ENV_APPS_RG_MODULAR_LANE_PROVIDER: Final[str] = "ENV_APPS_RG_MODULAR_LANE_PROVIDER"
CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM: Final[str] = "DEV_DEFAULT_QWEN_VLLM"
# Legacy alias (same string used before mock provider removal); prefer DEV_DEFAULT_QWEN_VLLM.
CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_MOCK: Final[str] = "DEV_DEFAULT_QWEN_VLLM"
# Explicit label for pytest / harness runs that force a mock resolution trace (never proof_eligible).
CLI_PROVIDER_RESOLUTION_TEST_MOCK: Final[str] = "TEST_MOCK"

ProviderResolutionSource = Literal[
    "CLI_OVERRIDE",
    "ENV_APPS_RG_MODULAR_LANE_PROVIDER",
    "DEV_DEFAULT_QWEN_VLLM",
    "TEST_MOCK",
]

_DEFAULT_BRIEFING = (
    Path(__file__).resolve().parent.parent / "config" / "default_targeting_briefing.txt"
)


class SectionCliConfigError(RuntimeError):
    """Fail-closed configuration for section-only CLI (missing SSOT file, empty resume, etc.)."""


def default_targeting_briefing_text() -> str:
    """UTF-8 text from ``default_targeting_briefing.txt`` (stripped)."""
    p = _DEFAULT_BRIEFING
    if not p.is_file():
        msg = (
            f"MISSING_DEFAULT_BRIEFING: expected default targeting briefing at {p.as_posix()} "
            "(apps_rg SSOT). Restore the file or pass --manual-brief with a path or URL."
        )
        raise SectionCliConfigError(msg)
    raw = p.read_text(encoding="utf-8").strip()
    if not raw:
        msg = (
            f"EMPTY_DEFAULT_BRIEFING: {p.as_posix()} has no content. "
            "Add briefing material or pass --manual-brief."
        )
        raise SectionCliConfigError(msg)
    return raw


def _truthy_env(raw: str | None) -> bool:
    if raw is None:
        return False
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def resolve_allow_non_allow_exit_zero(cli_flag: bool) -> bool:
    """True when CLI flag set or ``APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO`` is truthy.

    Disabled on product fail-closed runs (integrated ``python -m apps_rg`` / whole-run).
    """
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    if product_fail_closed_runtime():
        return False
    if cli_flag:
        return True
    return _truthy_env(os.environ.get("APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO"))


def resolve_phase1_lane_allow_non_allow_exit_zero(cli_flag: bool) -> bool:
    """Phase-1 modular lane dispatch — same SSOT as section CLI (``resolve_allow_non_allow_exit_zero``).

    Used when ``run_canonical_apps_rg_from_cli_primitives`` invokes section runners in-process
    during whole-run ``GenerateResumeStep`` so ``--allow-non-allow-exit-zero`` / env parity
    matches ``python -m apps_rg --section <lane>``.
    """
    return resolve_allow_non_allow_exit_zero(cli_flag)


def resolve_cli_x1d_judges(cli_value: str | None) -> str:
    """Honor ``APPS_RG_E2E_X1D_JUDGES`` when CLI omits ``--x1d-judges``."""
    from apps_rg.runtime.x1d_judge_policy import APPS_RG_E2E_DEFAULT_X1D_JUDGES

    if cli_value is not None and str(cli_value).strip():
        return str(cli_value).strip()
    env_csv = (os.environ.get("APPS_RG_E2E_X1D_JUDGES") or "").strip()
    return env_csv or APPS_RG_E2E_DEFAULT_X1D_JUDGES


def resolve_cli_lane_provider_with_source(cli_value: str | None) -> tuple[str, str]:
    """Resolve lane provider for section CLI and label *how* it was chosen.

    - ``CLI_OVERRIDE`` — non-empty ``--provider``
    - ``ENV_APPS_RG_MODULAR_LANE_PROVIDER`` — CLI omitted, env var set (any allowed value)
    - ``DEV_DEFAULT_QWEN_VLLM`` — CLI omitted, env unset (default ``qwen_vllm``)
    """
    from apps_rg.l2_recipe.r4_generation_mode import (
        ENV_APPS_RG_MODULAR_LANE_PROVIDER,
        resolve_apps_rg_modular_lane_provider,
    )

    if cli_value is not None and str(cli_value).strip():
        v = str(cli_value).strip().lower()
        if v == "mock":
            raise SectionCliConfigError(
                "Invalid --provider 'mock': section lanes require qwen_vllm. "
                "Live qwen_vllm required; APPS_RG_QWEN_OFFLINE_CONTRACT_STUB is disabled on product paths."
            )
        if v != "qwen_vllm":
            raise SectionCliConfigError(
                f"Invalid --provider {cli_value!r} (expected qwen_vllm)."
            )
        return v, CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE

    raw_env = str(os.environ.get(ENV_APPS_RG_MODULAR_LANE_PROVIDER) or "").strip()
    if raw_env:
        resolved = resolve_apps_rg_modular_lane_provider()
        return resolved, CLI_PROVIDER_RESOLUTION_ENV_APPS_RG_MODULAR_LANE_PROVIDER

    resolved = resolve_apps_rg_modular_lane_provider()
    return resolved, CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM


def resolve_cli_lane_provider(cli_value: str | None) -> str:
    """Honor ``APPS_RG_MODULAR_LANE_PROVIDER`` when CLI omits ``--provider``."""
    provider, _src = resolve_cli_lane_provider_with_source(cli_value)
    return provider


def coalesce_lane_provider_resolution_source(
    *,
    explicit: str | None,
    resolved_provider: str,
) -> str:
    """Infer resolution label when executive_summary runs outside minimal CLI (e.g. unit tests)."""
    from apps_rg.l2_recipe.r4_generation_mode import ENV_APPS_RG_MODULAR_LANE_PROVIDER

    if explicit is not None and str(explicit).strip():
        return str(explicit).strip()
    raw_env = str(os.environ.get(ENV_APPS_RG_MODULAR_LANE_PROVIDER) or "").strip()
    if raw_env:
        return CLI_PROVIDER_RESOLUTION_ENV_APPS_RG_MODULAR_LANE_PROVIDER
    if str(resolved_provider).strip().lower() == "qwen_vllm" and not raw_env:
        return CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM
    return CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE


def collect_executive_summary_mandatory_missing(args: Any) -> list[str]:
    """Return CLI flags still empty for an ``executive_summary`` lane run."""
    missing: list[str] = []
    if not str(getattr(args, "target_company", "") or "").strip():
        missing.append("--target-company")
    if not str(getattr(args, "target_role", "") or "").strip():
        missing.append("--target-role")
    if not str(getattr(args, "jd", "") or "").strip():
        missing.append("--jd")
    if not str(getattr(args, "manual_brief", "") or "").strip():
        missing.append("--manual-brief")
    return missing


def validate_executive_summary_mandatory_inputs(args: Any) -> None:
    """Fail closed when company, title, JD, or briefing were not supplied on the CLI."""
    missing = collect_executive_summary_mandatory_missing(args)
    if not missing:
        return
    raise SectionCliConfigError(
        "executive_summary requires explicit targeting inputs: "
        + ", ".join(missing)
        + ". Pass --target-company, --target-role, --jd (file path or inline text), and "
        "--manual-brief (file path, https URL, or inline text). Résumé-derived defaults and "
        "DEFAULT_SSOT JD/briefing files are not applied on this path."
    )


def fill_executive_summary_cli_targets(args: Any) -> None:
    """Deprecated: résumé-derived targeting is not used for ``executive_summary`` CLI runs.

    Kept for callers that still import the symbol; use
    :func:`validate_executive_summary_mandatory_inputs` instead.
    """
    if str(getattr(args, "target_company", "") or "").strip() and str(
        getattr(args, "target_role", "") or ""
    ).strip():
        return
    from apps_rg.runtime.sections import executive_summary_lane as lane

    try:
        base, _path_used, _digest = lane.load_base_resume()
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        raise SectionCliConfigError(
            "Cannot load base résumé for executive_summary defaults: "
            f"{exc} (check --resume, apps_rg/resume/base/active_base_resume_pointer.json, "
            "or canonical base JSON under apps_rg/resume/base/)."
        ) from exc

    facts = base.get("facts", base)
    if not isinstance(facts, dict):
        raise SectionCliConfigError(
            "Base résumé JSON has no usable facts object for executive_summary targeting."
        )
    emps = facts.get("employment", [])
    if not isinstance(emps, list) or not emps:
        raise SectionCliConfigError(
            "Base résumé has no employment entries; cannot derive --target-company / --target-role."
        )

    title, employer = "", ""
    for emp in emps:
        if not isinstance(emp, dict):
            continue
        if emp.get("is_current"):
            title = str(emp.get("title") or "").strip()
            employer = str(emp.get("employer") or "").strip()
            if title and employer:
                break
    if not (title and employer):
        emp0 = emps[0]
        if isinstance(emp0, dict):
            title = str(emp0.get("title") or "").strip()
            employer = str(emp0.get("employer") or "").strip()
    if not title or not employer:
        raise SectionCliConfigError(
            "Cannot derive --target-company / --target-role from base résumé "
            "(missing title or employer on current/first employment row)."
        )
    args.target_company = employer
    args.target_role = title


__all__ = [
    "CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE",
    "CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_MOCK",
    "CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM",
    "CLI_PROVIDER_RESOLUTION_ENV_APPS_RG_MODULAR_LANE_PROVIDER",
    "CLI_PROVIDER_RESOLUTION_TEST_MOCK",
    "ProviderResolutionSource",
    "SectionCliConfigError",
    "coalesce_lane_provider_resolution_source",
    "collect_executive_summary_mandatory_missing",
    "default_targeting_briefing_text",
    "fill_executive_summary_cli_targets",
    "resolve_allow_non_allow_exit_zero",
    "resolve_phase1_lane_allow_non_allow_exit_zero",
    "resolve_cli_lane_provider",
    "resolve_cli_lane_provider_with_source",
    "resolve_cli_x1d_judges",
    "validate_executive_summary_mandatory_inputs",
]
