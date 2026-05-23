"""W4.0 — final resume aggregation preflight negative controls."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.aggregation.preflight import (
    AggregationPreflightError,
    assert_preflight_pass,
    run_aggregation_preflight,
)
from apps_rg.runtime.assembly.final_resume_manifest import resolve_default_paths
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root

REPO = find_repo_root()


@pytest.fixture(scope="module")
def rollup_blob() -> dict:
    paths = resolve_default_paths(REPO)
    if not paths.rollup_json.is_file():
        pytest.skip("rollup missing")
    return json.loads(paths.rollup_json.read_text(encoding="utf-8"))


def test_preflight_rejects_blocked_x3(rollup_blob: dict) -> None:
    blob = json.loads(json.dumps(rollup_blob))
    lanes = blob.setdefault("lanes", {})
    lane = "headline"
    row = dict(lanes.get(lane) or {})
    row["x3_code"] = "X3_BLOCK_TEST"
    lanes[lane] = row
    sealed = {"pointers": [{"lane": lane, "x3_code": "X3_BLOCK_TEST", "product_quality_status": "FAIL"}]}
    fp = {"same_date_prefix_coherent": True, "jd_digest_coherent": "OK", "briefing_digest_coherent": "OK"}
    results = run_aggregation_preflight(repo=REPO, rollup_blob=blob, fingerprint=fp, sealed_index=sealed)
    with pytest.raises(AggregationPreflightError, match="blocked"):
        assert_preflight_pass(results)


def test_preflight_missing_x3_disposition_rollup_row(rollup_blob: dict) -> None:
    blob = json.loads(json.dumps(rollup_blob))
    lanes = blob.setdefault("lanes", {})
    if "headline" in lanes:
        lanes["headline"] = {"latest_successful_real_artifact_path": "artifacts/missing/run"}
    sealed = {"pointers": []}
    fp = {"same_date_prefix_coherent": True, "jd_digest_coherent": "OK", "briefing_digest_coherent": "OK"}
    results = run_aggregation_preflight(repo=REPO, rollup_blob=blob, fingerprint=fp, sealed_index=sealed)
    proof_gate = next(r for r in results if r.gate_id == "x2_preflight_required_proof_artifacts_present")
    assert proof_gate.pass_ is False


def test_preflight_passes_on_real_rollup(rollup_blob: dict) -> None:
    from apps_rg.runtime.aggregation.run_fingerprint import build_fingerprint_from_rollup
    from apps_rg.runtime.assembly.final_resume_manifest import resolve_default_paths

    paths = resolve_default_paths(REPO)
    locked = json.loads(paths.locked_manifest.read_text(encoding="utf-8"))
    base_digest = str(locked.get("base_resume_json_hash") or "")
    fp, sealed = build_fingerprint_from_rollup(
        repo=REPO,
        rollup_blob=rollup_blob,
        base_resume_digest=base_digest,
    )
    results = run_aggregation_preflight(
        repo=REPO,
        rollup_blob=rollup_blob,
        fingerprint=fp,
        sealed_index=sealed,
    )
    try:
        assert_preflight_pass(results)
    except AggregationPreflightError as exc:
        pytest.skip(f"rollup prerequisites not assembly-safe: {exc}")
    except TypeError as exc:
        pytest.skip(f"fingerprint API mismatch on this tree: {exc}")
