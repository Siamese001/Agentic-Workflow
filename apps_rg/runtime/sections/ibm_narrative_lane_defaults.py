"""Module-level CLI defaults for the IBM narrative lane (neutral SSOT)."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes

PROMPT_ID = "ibm_position_narrative_dispatch_v1"
NARRATIVE_TEMP_DEFAULT = 0.45
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text
# 1200 truncated live attempt-1 responses at max_tokens (postRungs_20260610_2246:
# stop_reason=max_tokens, output_tokens=1200) and left parse-retry / metric-budget
# regen paths with the same cap. Same defect class as headline 900→4000 (PR #285).
NARRATIVE_MAX_OUTPUT_TOKENS = 4000
LANE_KEY = "ibm_narrative"


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
