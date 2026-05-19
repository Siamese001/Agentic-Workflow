"""Unit tests for aggregation run fingerprint and preflight."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.aggregation.preflight import run_aggregation_preflight
from apps_rg.runtime.aggregation.run_fingerprint import build_orchestration_fingerprint
from apps_rg.runtime.aggregation.section_sealed_index import build_section_sealed_index


def test_fingerprint_flags_mixed_run_ids() -> None:
    sealed = {
        "pointers": [
            {"lane": "headline", "run_id": "headline_20260518_a", "x3_code": "X3_REVIEW_X", "product_quality_status": "PASS"},
            {"lane": "executive_summary", "run_id": "exec_20260517_b", "x3_code": "X3_ALLOW", "product_quality_status": "PASS"},
        ],
    }
    fp = build_orchestration_fingerprint(
        rollup_blob={"rollup_id": "r1"},
        sealed_index=sealed,
        base_resume_digest="abc",
        rollup_id="r1",
    )
    assert fp["same_date_prefix_coherent"] is False
    assert fp["jd_digest_coherent"] == "UNKNOWN"


def test_preflight_fails_blocked_x3(tmp_path: Path) -> None:
    rollup = {
        "lanes": {
            "headline": {
                "latest_successful_real_artifact_path": "lane/headline",
                "x2_failed": 0,
                "x3_code": "X3_BLOCK_DETERMINISTIC",
            },
        },
    }
    run_dir = tmp_path / "lane" / "headline"
    run_dir.mkdir(parents=True)
    for name in (
        "l2_output.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
        "section_input_usage_ledger.json",
        "x2_source_fact_pool_receipt.json",
    ):
        (run_dir / name).write_text("{}", encoding="utf-8")
    (run_dir / "l2_output.json").write_text(
        json.dumps({"run_id": "h1", "claim_ledger": [], "product_quality_status": "PASS"}),
        encoding="utf-8",
    )
    (run_dir / "x2_source_fact_pool_receipt.json").write_text(
        json.dumps({"x2_source_fact_pool_status": "PASS"}),
        encoding="utf-8",
    )
    sealed = build_section_sealed_index(repo=tmp_path, rollup_blob=rollup, base_resume_digest="d")
    fp = build_orchestration_fingerprint(
        rollup_blob=rollup,
        sealed_index=sealed,
        base_resume_digest="d",
        rollup_id="r",
    )
    results = run_aggregation_preflight(repo=tmp_path, rollup_blob=rollup, fingerprint=fp, sealed_index=sealed)
    blocked = next(r for r in results if r.gate_id == "x2_preflight_no_blocked_x3")
    assert blocked.pass_ is False
