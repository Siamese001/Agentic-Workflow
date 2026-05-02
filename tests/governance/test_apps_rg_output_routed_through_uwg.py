"""Test 5 — Generated resume must be written through UWG, not directly.

Fails today: ``apps_rg/scripts/generate_resume.py:264`` writes
``generated_resume.json`` directly to ``artifacts/apps_rg/runs/...`` with no
CommitRequest, no UWGValidationReceipt, no UWGCommitReceipt sibling.

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 6 P6.1-6.2.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: generated_resume.json written directly, bypassing UWG. "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 6 P6.1-6.2.",
    strict=True,
)
def test_resume_output_has_uwg_commit_receipt(latest_apps_rg_run_dir: Path) -> None:
    resume = latest_apps_rg_run_dir / "generated_resume.json"
    assert resume.exists(), f"missing app output at {resume}"

    uwg_dir = latest_apps_rg_run_dir / "uwg"
    commit_receipt = uwg_dir / "uwg_commit_receipt.json"
    commit_request = uwg_dir / "commit_request.json"
    validation_receipt = uwg_dir / "uwg_validation_receipt.json"

    assert commit_request.exists(), f"missing CommitRequest at {commit_request}"
    assert validation_receipt.exists(), f"missing UWGValidationReceipt at {validation_receipt}"
    assert commit_receipt.exists(), f"missing UWGCommitReceipt at {commit_receipt}"

    receipt_doc = json.loads(commit_receipt.read_text(encoding="utf-8"))
    for field in ("request_id", "run_id", "trace_root", "output_path", "output_hash"):
        assert field in receipt_doc, f"UWGCommitReceipt missing required field: {field}"

    # The committed path must point at the actual on-disk artifact and the
    # hash must match (i.e., the receipt is bound to real bytes, not synthetic).
    import hashlib

    actual = hashlib.sha256(resume.read_bytes()).hexdigest()
    assert receipt_doc["output_hash"] == actual, (
        f"UWGCommitReceipt.output_hash {receipt_doc['output_hash']!r} does not match "
        f"sha256 of generated_resume.json ({actual!r})"
    )
