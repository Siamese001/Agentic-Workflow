"""Module-level CLI defaults for the competencies lane (neutral SSOT)."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes

PROMPT_ID = "competencies_dispatch_v1"
COMPETENCIES_TEMP_DEFAULT = 0.38
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text
COMPETENCIES_MAX_OUTPUT_TOKENS = 6000
DEFAULT_COMPETENCIES_SC_OUTPUT_TOKENS = 4096
LANE_KEY = "competencies"


def competencies_self_consistency_output_tokens() -> int:
    """Per-path live SC budget; full-lane/repair ceiling remains 6000."""
    import os

    raw = os.environ.get("APPS_RG_COMPETENCIES_SC_OUTPUT_TOKENS", "").strip()
    try:
        requested = int(raw) if raw else DEFAULT_COMPETENCIES_SC_OUTPUT_TOKENS
    except ValueError:
        requested = DEFAULT_COMPETENCIES_SC_OUTPUT_TOKENS
    return max(1500, min(requested, COMPETENCIES_MAX_OUTPUT_TOKENS))


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
