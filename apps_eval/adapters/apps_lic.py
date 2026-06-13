"""Narrow live adapter for apps_lic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_eval.contracts import AppOutputSnapshot


def run_apps_lic_live(scenario_id: str, payload: dict[str, Any], artifact_dir: Path) -> AppOutputSnapshot:
    from apps_lic.runtime.dispatch.canonical_dispatch import (
        build_cli_ingress_raw,
        run_canonical_apps_lic_spine,
    )

    raw_ingress = build_cli_ingress_raw(
        recipient_class=str(payload.get("recipient_class", "recruiter")),
        channel=str(payload.get("channel", "linkedin")),
        outreach_mode=str(payload.get("outreach_mode", "cold")),
        manual_brief=str(payload.get("manual_brief", "")),
        lead_profile=payload.get("lead_profile") or {},
        campaign_objective=payload.get("campaign_objective"),
    )
    result = run_canonical_apps_lic_spine(raw_ingress, artifact_dir=artifact_dir)
    if hasattr(result, "to_dict"):
        data = result.to_dict()
    elif isinstance(result, dict):
        data = result
    else:
        data = {"result": str(result)}
    return AppOutputSnapshot(
        app_id="apps_lic",
        scenario_id=scenario_id,
        x3_disposition=str(data.get("x3_code") or data.get("exit_status") or "UNKNOWN"),
        output={"result": data},
        artifacts=[],
        provenance={
            "entrypoints": [
                "apps_lic.runtime.dispatch.canonical_dispatch:build_cli_ingress_raw",
                "apps_lic.runtime.dispatch.canonical_dispatch:run_canonical_apps_lic_spine",
            ]
        },
        side_effects={"product_state_mutated": False, "writes": []},
    )
