"""Professional Competencies section lane — **canonical** path: ``python -m apps_rg --section competencies``.

Delegates to :func:`apps_rg.runtime.dispatch.competencies_dispatch.run_competencies_execution` with
``trace_runtime_path`` set to this module. The dispatch package holds shared compile/runtime helpers;
it is not an alternate CLI entrypoint (legacy ``-m ...competencies_dispatch`` is deprecated).
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from apps_rg.runtime.dispatch.competencies_dispatch import (
    BRIEFING_DEFAULT,
    COMPETENCIES_TEMP_DEFAULT,
    JD_TEXT_DEFAULT,
    PROMPT_ID,
    TARGET_COMPANY_DEFAULT,
    TARGET_TITLE_DEFAULT,
    run_competencies_execution,
)

LANE_KEY = "competencies"

__all__ = [
    "BRIEFING_DEFAULT",
    "COMPETENCIES_TEMP_DEFAULT",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "PROMPT_ID",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "build_competencies_lane_args",
    "run_competencies_lane_execution",
]


def build_competencies_lane_args(
    *,
    provider: str,
    temperature: float,
    x1d_judges: str,
    mock_judges: bool,
    allow_test_mock_judges: bool = False,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    target_role: str | None = None,
    selected_role_fact_set: str = "",
) -> SimpleNamespace:
    """Namespace compatible with :func:`run_competencies_execution`."""
    ns = SimpleNamespace(
        provider=str(provider).strip() or "qwen_vllm",
        temperature=float(temperature),
        x1d_judges=str(x1d_judges),
        mock_judges=bool(mock_judges),
        allow_test_mock_judges=bool(allow_test_mock_judges),
        target_title=str(target_title).strip() or TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or TARGET_COMPANY_DEFAULT,
        jd_text=str(jd_text).strip() or JD_TEXT_DEFAULT,
        briefing=str(briefing).strip() or BRIEFING_DEFAULT,
        target_role=(str(target_role).strip() if target_role else None),
        selected_role_fact_set=str(selected_role_fact_set or ""),
    )
    return ns


def run_competencies_lane_execution(
    args: SimpleNamespace,
    *,
    artifact_dir_override: Path | None = None,
) -> dict[str, Any]:
    """PA → provider → deterministic repairs → X2 → X1D → X3 → L6 under runtime_proofs layout."""
    return run_competencies_execution(
        args,
        artifact_dir_override=artifact_dir_override,
        trace_runtime_path="apps_rg.runtime.sections.competencies_lane",
        print_output=False,
    )
