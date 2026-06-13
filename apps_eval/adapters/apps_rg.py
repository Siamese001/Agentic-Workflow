"""Narrow live adapter for apps_rg."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_eval.contracts import AppOutputSnapshot


def run_apps_rg_live(scenario_id: str, payload: dict[str, Any], artifact_dir: Path) -> AppOutputSnapshot:
    from agentic_core.runtime.entry.apps_rg_dispatch import dispatch_apps_rg_run

    result = dispatch_apps_rg_run(
        target_company=str(payload.get("target_company", "")),
        target_role=str(payload.get("target_role", "")),
        target_level=str(payload.get("target_level", "")),
        jd=str(payload.get("jd", "")),
        manual_brief=str(payload.get("manual_brief", "")),
        resume_path=str(payload.get("resume_path", "")),
        generation_mode=str(payload.get("generation_mode", "strategic_tailor")),
        artifact_dir=str(artifact_dir),
    )
    return AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id=scenario_id,
        x3_disposition=str(result.get("x3_code") or result.get("exit_status") or "UNKNOWN"),
        output={"result": result},
        artifacts=[],
        provenance={"entrypoint": "agentic_core.runtime.entry.apps_rg_dispatch:dispatch_apps_rg_run"},
        side_effects={"product_state_mutated": False, "writes": []},
    )
