"""Fail-closed checks that CLI targeting inputs were updated beyond DEFAULT_SSOT placeholders."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.selected_role_fact_set import digest_text
from apps_rg.runtime.briefing_resolution import BriefingResolutionError, resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import JdResolutionError, resolve_jd_for_lanes

_ENV_ALLOW_STALE_TARGETING_SSOT = "APPS_RG_ALLOW_STALE_TARGETING_SSOT"


def _truthy_env(name: str) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return False
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def default_targeting_jd_digest() -> str:
    from apps_rg.runtime.jd_resolution import default_jd_targeting_text

    return digest_text(default_jd_targeting_text())


def default_targeting_briefing_digest() -> str:
    from apps_rg.runtime.briefing_ssot import default_targeting_briefing_text

    return digest_text(default_targeting_briefing_text())


def is_stale_default_targeting_jd(jd_description: str) -> bool:
    """True when resolved JD body still matches committed DEFAULT_SSOT placeholder."""
    body = str(jd_description or "").strip()
    if not body:
        return True
    return digest_text(body) == default_targeting_jd_digest()


def is_stale_default_targeting_briefing(briefing_text: str) -> bool:
    """True when resolved briefing still matches committed DEFAULT_SSOT placeholder."""
    body = str(briefing_text or "").strip()
    if not body:
        return True
    return digest_text(body) == default_targeting_briefing_digest()


def resolve_executive_summary_cli_targeting_material(args: Any) -> tuple[str, str]:
    """Load JD description and briefing text using the same rules as executive_summary dispatch."""
    jd_legacy = str(getattr(args, "jd", "") or "").strip()
    jd_ref = ""
    jd_txt = ""
    if jd_legacy:
        p = Path(jd_legacy)
        if p.is_file():
            jd_ref = jd_legacy
        else:
            jd_txt = jd_legacy

    tc = str(getattr(args, "target_company", "") or "").strip()
    tr = str(getattr(args, "target_role", "") or "").strip()
    jd_resolved = resolve_jd_for_lanes(
        job_description_ref=jd_ref or None,
        job_description_text=jd_txt or None,
        target_company=tc,
        target_role=tr,
        require_run_specific=True,
    )
    brief_resolved = resolve_briefing_for_lanes(
        briefing_artifact_ref=str(getattr(args, "manual_brief", "") or "").strip() or None,
        require_run_specific=True,
    )
    return jd_resolved.description, brief_resolved.text


def validate_executive_summary_targeting_inputs_updated(args: Any) -> None:
    """Fail closed when JD or briefing were not updated from DEFAULT_SSOT placeholders."""
    from apps_rg.runtime.section_cli_defaults import SectionCliConfigError

    if _truthy_env(_ENV_ALLOW_STALE_TARGETING_SSOT):
        return

    try:
        jd_text, briefing_text = resolve_executive_summary_cli_targeting_material(args)
    except (JdResolutionError, BriefingResolutionError) as exc:
        raise SectionCliConfigError(str(exc)) from exc

    stale: list[str] = []
    if is_stale_default_targeting_jd(jd_text):
        stale.append(
            "JD still matches apps_rg/config/default_jd_targeting.txt (DEFAULT_SSOT placeholder). "
            "Update the job description material or pass a run-specific --jd path/text."
        )
    if is_stale_default_targeting_briefing(briefing_text):
        stale.append(
            "briefing still matches apps_rg/config/default_targeting_briefing.txt "
            "(DEFAULT_SSOT placeholder). Update briefing material or pass a run-specific "
            "--manual-brief path/URL/text."
        )
    if not stale:
        return

    waiver = (
        f"Test/plumbing override only: set {_ENV_ALLOW_STALE_TARGETING_SSOT}=1 to bypass this gate."
    )
    raise SectionCliConfigError(
        "executive_summary targeting inputs are not updated: " + " ".join(stale) + " " + waiver
    )


__all__ = [
    "default_targeting_briefing_digest",
    "default_targeting_jd_digest",
    "is_stale_default_targeting_briefing",
    "is_stale_default_targeting_jd",
    "resolve_executive_summary_cli_targeting_material",
    "validate_executive_summary_targeting_inputs_updated",
]
