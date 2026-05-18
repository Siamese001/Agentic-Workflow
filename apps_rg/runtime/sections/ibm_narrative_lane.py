"""Canonical IBM narrative lane — ``python -m apps_rg --section ibm_narrative``.

``ibm_narrative_dispatch`` holds shared ``run_ibm_narrative_execution`` (compile / provider / gates / L6);
its ``python -m`` entry is retired—use the selected-section CLI only.
"""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.dispatch.ibm_narrative_dispatch import (
    BRIEFING_DEFAULT,
    JD_TEXT_DEFAULT,
    PROMPT_ID,
    REPO_ROOT,
    TARGET_COMPANY_DEFAULT,
    TARGET_TITLE_DEFAULT,
    NARRATIVE_TEMP_DEFAULT as IBM_NARRATIVE_TEMP_DEFAULT,
    run_ibm_narrative_execution,
)

LANE_KEY = "ibm_narrative"

# Matches ``ibm_position_narrative_v1.yaml`` temperature_profile (STOP 14 sweep band).
IBM_NARRATIVE_TEMP_RANGE = (0.30, 0.45)


def run_ibm_narrative_lane_execution(
    args,
    *,
    artifact_dir_override: Path | None = None,
):
    """Invoke shared IBM narrative execution with canonical lane provenance in prompt_selection_trace."""
    return run_ibm_narrative_execution(
        args,
        artifact_dir_override=artifact_dir_override,
        trace_runtime_path="apps_rg.runtime.sections.ibm_narrative_lane",
        print_output=False,
    )


__all__ = [
    "BRIEFING_DEFAULT",
    "IBM_NARRATIVE_TEMP_DEFAULT",
    "IBM_NARRATIVE_TEMP_RANGE",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "PROMPT_ID",
    "REPO_ROOT",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "run_ibm_narrative_lane_execution",
]
