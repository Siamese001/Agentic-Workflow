"""Test 4 — Latest apps_rg run must end in exactly one X3 disposition.

Fails today: no X3 disposition is emitted for R3 (only the R1B path emits
``x3_disposition_receipt.json`` via ``integrated_runtime_emitter``).

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 3 P3.2.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


# Canonical X3 disposition values per agentic_core/L3_orchestration/exit_eval/v6/x3_dispositions.py
X3_CANONICAL_DISPOSITIONS = {
    "ALLOW",
    "ALLOW_WITH_REVISION",
    "DENY",
    "PARTIAL_ALLOW",
    "ESCALATE_HITL",
    "BLOCK_REPAIR",
}


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: no X3 disposition receipt emitted for R3 path. "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 3 P3.2.",
    strict=True,
)
def test_exactly_one_x3_disposition(latest_apps_rg_run_dir: Path) -> None:
    exit_dir = latest_apps_rg_run_dir / "exit"
    receipts = list(exit_dir.glob("x3_*.json")) if exit_dir.exists() else []

    assert len(receipts) == 1, (
        f"Expected exactly one X3 disposition receipt under {exit_dir}; found {len(receipts)}"
    )

    doc = json.loads(receipts[0].read_text(encoding="utf-8"))
    disposition = doc.get("disposition") or doc.get("verdict")
    assert disposition in X3_CANONICAL_DISPOSITIONS, (
        f"X3 disposition {disposition!r} not in canonical set {X3_CANONICAL_DISPOSITIONS}"
    )
    for field in ("request_id", "run_id", "trace_root"):
        assert field in doc, f"X3 receipt missing required ID field: {field}"
