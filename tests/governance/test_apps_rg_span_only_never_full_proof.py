"""Test 10 — A RuntimeADGSnapshot alone must NEVER satisfy FULLY_PROVEN.

This is a meta-test that protects the entire ``tests/governance/`` suite from
regressing into "telemetry == proof" thinking. It scans the run directory and
asserts that if a RuntimeADGSnapshot exists but ANY of the canonical
governance artifacts are missing, the run cannot be FULLY_PROVEN.

Stays GREEN once the other 9 tests pass — by then every required artifact
exists, and this test's condition (snapshot present AND all receipts present)
is satisfied. Stays FAILING (xfail) until then.

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 7 P7.3.
"""
from __future__ import annotations

from pathlib import Path

import pytest


# Receipts that must coexist with the RuntimeADGSnapshot for FULLY_PROVEN.
REQUIRED_RECEIPT_FILES = (
    "manifest.json",
    "contracts/l1_plan_contract.json",
    "contracts/route_contract.json",
    "exit/exit_review_packet.json",
    "uwg/uwg_commit_receipt.json",
    "replay/replay_comparison_receipt.json",
    "no_bypass/no_bypass_assertion_receipt.json",
)


def _runtime_adg_snapshot_for_run(run_dir: Path) -> Path | None:
    """Find the runtime ADG snapshot whose mission tag references this run.

    Permissive: returns the most recent runtime_adg/*/<hash>.json under
    ``agentic_core/L4_state/memory/runtime_adg/`` — the per-run binding is
    enforced by the manifest test (test 9), not here.
    """
    repo = run_dir.parent.parent.parent.parent  # artifacts/apps_rg/runs/<ts>/ -> repo
    adg_root = repo / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
    if not adg_root.exists():
        return None
    snaps = sorted(
        (p for p in adg_root.rglob("*.json") if p.parent != adg_root),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return snaps[0] if snaps else None


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: required receipts coexisting with RuntimeADGSnapshot are missing. "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 7 P7.3.",
    strict=True,
)
def test_span_only_evidence_does_not_satisfy_full_proof(latest_apps_rg_run_dir: Path) -> None:
    snapshot = _runtime_adg_snapshot_for_run(latest_apps_rg_run_dir)
    assert snapshot is not None and snapshot.exists(), (
        "no RuntimeADGSnapshot found — cannot apply meta-rule"
    )

    missing: list[str] = []
    for rel in REQUIRED_RECEIPT_FILES:
        if not (latest_apps_rg_run_dir / rel).exists():
            missing.append(rel)

    assert not missing, (
        f"RuntimeADGSnapshot exists at {snapshot} but the run is missing {len(missing)} "
        f"required governance receipt(s): {missing}. Span-only evidence does not satisfy "
        "FULLY_PROVEN per the audit standard."
    )
