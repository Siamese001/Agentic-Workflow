"""Every artifact under contracts/ MUST contain run_id and trace_id.

A handwritten "pretty" proof file with no trace links cannot pass this
test — that is the user-spec anti-cheat invariant for static fake proof.
"""

from __future__ import annotations

import json
from pathlib import Path


def test_every_contract_carries_run_and_trace_ids(
    proof_dir: Path, run_manifest: dict
) -> None:
    run_id = run_manifest["run_id"]
    trace_id = run_manifest["trace_id"]
    contracts_dir = proof_dir / "contracts"
    files = sorted(contracts_dir.glob("*.json"))
    assert files, f"no contracts under {contracts_dir}"
    for jp in files:
        body_str = jp.read_text(encoding="utf-8")
        # Substring check is sufficient — both IDs are non-trivial uuids.
        assert run_id in body_str, (
            f"{jp.name} missing run_id={run_id} (handwritten/static proof?)"
        )
        assert trace_id in body_str, (
            f"{jp.name} missing trace_id={trace_id} (handwritten/static proof?)"
        )


def test_proof_verdict_was_recomputed(proof_verdict: dict) -> None:
    """proof_verdict must include verifier_version and recomputed hashes."""
    assert proof_verdict.get("verifier_version"), "verifier_version missing"
    assert proof_verdict.get("recomputed_hashes"), "recomputed_hashes empty"
    assert proof_verdict["final_status"] == "PASS", (
        f"verdict not PASS: {proof_verdict.get('failed_checks')}"
    )
