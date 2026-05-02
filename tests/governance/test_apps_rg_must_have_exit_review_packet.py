"""Test 3 — Latest apps_rg run must produce an ExitReviewPacket.

Fails today: ``ExitEvalPipeline.run`` is wired only into the R1B safe-reuse
path (``integrated_safe_reuse_run.py``), not the R3 grounded-read path that
apps_rg uses.

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 3 P3.1.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: Exit V6 pipeline not invoked for R3 path. "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 3 P3.1.",
    strict=True,
)
def test_exit_review_packet_emitted(latest_apps_rg_run_dir: Path) -> None:
    exit_dir = latest_apps_rg_run_dir / "exit"
    packet = exit_dir / "exit_review_packet.json"
    assert packet.exists(), (
        f"missing ExitReviewPacket at {packet} — Exit V6 pipeline must run for R3"
    )

    doc = json.loads(packet.read_text(encoding="utf-8"))
    for field in ("request_id", "run_id", "trace_root", "review_target", "policy_hash"):
        assert field in doc, f"ExitReviewPacket missing required field: {field}"
