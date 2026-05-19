"""Run apps_lic outreach workflow for Charles Morris (Truist) with Truist briefing context."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_MISSION_PATH = Path(__file__).resolve().parent / "charles_truist_mission.json"
_OUTPUT_DIR = _REPO / "artifacts" / "apps_lic" / "runs" / "charles_truist_outreach"


async def _run() -> dict:
    from apps_lic.reasoning.enterprise_campaign_orchestrator import EnterpriseLicOrchestrator
    from apps_lic.types.lic_models_types import OutreachMission

    with _MISSION_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)

    mission = OutreachMission(
        mission_id=str(uuid4()),
        sender_profile=data["sender_profile"],
        recipient_profile=data["recipient_profile"],
        job_description=data["job_description"],
        connection_status=data["recipient_profile"].get("connection_status", "not_connected"),
        prior_message_count=int(data["recipient_profile"].get("prior_message_count", 0) or 0),
    )

    orchestrator = EnterpriseLicOrchestrator()
    return await orchestrator.execute_workflow(mission)


def main() -> int:
    result = asyncio.run(_run())
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _OUTPUT_DIR / "outreach_result.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))
    print(f"\nSaved: {out_path}")
    if result.get("status") == "success" and result.get("production_ready"):
        return 0
    return 1 if result.get("status") != "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
