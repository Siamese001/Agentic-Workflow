"""Test 7 — Latest apps_rg run must produce a replay comparison receipt.

Fails today: production replay-receipt writer does not exist. Replay
receipts are produced only by the e2e test harness
(``tests/e2e/proof/runner.py``) and the requirements-proof scaffolding
(``artifacts/runtime/requirements_proof/replay/``).

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 5 P5.1.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: no production replay-receipt writer exists. "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 5 P5.1.",
    strict=True,
)
def test_replay_comparison_receipt_emitted(latest_apps_rg_run_dir: Path) -> None:
    replay_dir = latest_apps_rg_run_dir / "replay"
    receipt = replay_dir / "replay_comparison_receipt.json"
    assert receipt.exists(), (
        f"missing replay receipt at {receipt} — production replay writer required"
    )

    doc = json.loads(receipt.read_text(encoding="utf-8"))
    for field in ("request_id", "run_id", "trace_root", "replay_key", "replay_match", "comparison_method"):
        assert field in doc, f"replay receipt missing required field: {field}"

    assert isinstance(doc["replay_match"], bool), "replay_match must be a boolean"
    assert doc.get("replay_key"), "replay_key must be a non-empty value (no _noop shim)"
