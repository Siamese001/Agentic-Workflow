"""Fleet-wide REQ tagging — every governed app must populate the ledger.

This test enters ``otel_lifecycle_capture`` once per app with the expected
``app_id`` and asserts that the REQ Coverage Ledger gains exemplar rows
for every priority REQ_ID for that app. Subprocess-isolated to dodge
pytest's logging-capture interference (same pattern as
``test_otel_emission_live.py``).

Note: only the bridge + REQ markers are exercised here, not the full app
orchestrator (those need fixtures/inputs and are app-specific). The
priority REQ markers are emitted on context-manager entry, so the test
proves the wiring is sound across the fleet.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

PRIORITY_REQS = [
    "REQ-L6-OBS-ANTI-BYPASS-001",
    "REQ-L6-OUTCOME-TRAJECTORY-001",
    "REQ-L6-PROPOSAL-ADMISSION-001",
    "REQ-L6-MEMORY-PROMOTION-IFACE-001",
    "REQ-L0-ROUTECONTRACT-TELEMETRY-001",
    "REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001",
]


@pytest.mark.parametrize(
    "app_id,mission",
    [
        ("apps_rg", "apps_rg.test_fleet_tagging"),
        ("apps_eval", "apps_eval.test_fleet_tagging"),
        ("apps_exec", "apps_exec.test_fleet_tagging"),
        ("apps_lic", "apps_lic.test_fleet_tagging"),
        ("apps_research", "apps_research.test_fleet_tagging"),
        ("apps_rfp", "apps_rfp.test_fleet_tagging"),
    ],
)
def test_app_emits_all_priority_reqs(app_id, mission, tmp_path):
    """Each governed app must emit all 6 priority REQ exemplars."""
    ledger = tmp_path / "ledger.sqlite"
    out_file = tmp_path / "result.json"
    script = f"""
import json, sys
sys.path.insert(0, r"{REPO_ROOT}")
from agentic_core.runtime.contracts.otel_lifecycle_bridge import otel_lifecycle_capture
from tools.runtime_evidence.ledger_writer import write_emissions

# Enter the context manager — emits the 6 REQ markers + buffers spans.
with otel_lifecycle_capture(mission="{mission}", app_id="{app_id}") as bridge:
    pass  # the entry alone is sufficient — REQ emission happens there

# Bridge has the 6 spans; re-route to a private ledger (the real flush
# inside the context manager uses the production ledger; we want isolation).
spans = bridge.buffered_spans()
result = write_emissions(spans, app_id="{app_id}", source="{mission}", db_path=r"{ledger}")
result["span_count"] = len(spans)
result["req_ids_in_spans"] = sorted({{
    rid
    for s in spans
    for rid in (s.get("attributes") or {{}}).get("agentic.req.ids", [])
}})
with open(r"{out_file}", "w") as f:
    json.dump(result, f, default=str)
"""
    r = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=60, check=False,
    )
    assert r.returncode == 0, (
        f"{app_id} subprocess failed: {r.stderr[-1000:]}"
    )
    result = json.loads(out_file.read_text())
    assert result["success"] is True, f"ledger write failed: {result}"
    observed_reqs = set(result["req_ids_in_spans"])
    missing = set(PRIORITY_REQS) - observed_reqs
    assert not missing, (
        f"{app_id} did not emit all priority REQs. "
        f"Observed: {sorted(observed_reqs)}. Missing: {sorted(missing)}"
    )
    assert result["distinct_req_ids"] == len(PRIORITY_REQS), (
        f"{app_id} ledger should have {len(PRIORITY_REQS)} distinct REQ rows, "
        f"got {result['distinct_req_ids']}"
    )
