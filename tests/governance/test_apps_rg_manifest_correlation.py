"""Test 9 — Per-run manifest must join all receipts by shared IDs and hashes.

Fails today: no ``manifest.json`` is written under
``artifacts/apps_rg/runs/<ts>/``. Cross-receipt correlation is impossible.

Remediation: plan ``apps-rg-governed-runtime-b8d4f1.md`` Wave 6 P6.3.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


REQUIRED_MANIFEST_FIELDS = {
    "command",
    "cwd",
    "git_branch",
    "git_commit",
    "mission",
    "scenario_id",
    "request_id",
    "run_id",
    "trace_root",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "artifacts",
}

REQUIRED_ARTIFACT_ENTRIES = {
    "l1_plan_contract",
    "route_contract",
    "final_evidence_contract",
    "compiled_prompt_artifact",
    "sealed_l2_artifact",
    "exit_review_packet",
    "x1_bundle",
    "x3_disposition_receipt",
    "uwg_commit_receipt",
    "replay_comparison_receipt",
    "no_bypass_assertion_receipt",
    "runtime_adg_snapshot",
    "final_output",
}


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.governance
@pytest.mark.xfail(
    reason="Governance gap: per-run manifest.json not produced. "
    "Remediation: plan apps-rg-governed-runtime-b8d4f1.md Wave 6 P6.3.",
    strict=True,
)
def test_manifest_correlates_all_receipts(latest_apps_rg_run_dir: Path) -> None:
    manifest_path = latest_apps_rg_run_dir / "manifest.json"
    assert manifest_path.exists(), f"missing manifest at {manifest_path}"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    missing = REQUIRED_MANIFEST_FIELDS - set(manifest.keys())
    assert not missing, f"manifest missing required fields: {sorted(missing)}"

    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, dict)
    missing_artifacts = REQUIRED_ARTIFACT_ENTRIES - set(artifacts.keys())
    assert not missing_artifacts, f"manifest.artifacts missing entries: {sorted(missing_artifacts)}"

    # Each artifact entry must list a path AND a sha256, AND the file must exist
    # AND the recorded sha256 must match the actual bytes.
    for name, entry in artifacts.items():
        assert "path" in entry and "sha256" in entry, (
            f"manifest.artifacts.{name} missing path or sha256"
        )
        ap = Path(entry["path"])
        if not ap.is_absolute():
            ap = latest_apps_rg_run_dir.parent.parent.parent / ap
        assert ap.exists(), f"manifest.artifacts.{name}.path does not exist on disk: {ap}"
        actual = _sha256_of(ap)
        assert entry["sha256"] == actual, (
            f"manifest.artifacts.{name}.sha256 mismatch — declared {entry['sha256']}, actual {actual}"
        )

    # Cross-receipt ID join: every receipt that has request_id/run_id/trace_root
    # must agree with the manifest.
    for name in ("l1_plan_contract", "route_contract", "exit_review_packet", "x3_disposition_receipt"):
        ap = Path(artifacts[name]["path"])
        if not ap.is_absolute():
            ap = latest_apps_rg_run_dir.parent.parent.parent / ap
        if ap.suffix == ".json":
            doc = json.loads(ap.read_text(encoding="utf-8"))
            for field in ("request_id", "run_id", "trace_root"):
                assert doc.get(field) == manifest[field], (
                    f"{name}.{field}={doc.get(field)!r} does not match manifest.{field}={manifest[field]!r}"
                )
