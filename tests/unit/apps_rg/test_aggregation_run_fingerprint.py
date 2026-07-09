"""Unit tests for aggregation run fingerprint and preflight."""
# apps-test-model: APP CONTRACT

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.assembly.final_resume_x2 import GENERATED_LANE_IDS
from apps_rg.runtime.aggregation.preflight import assert_preflight_pass, run_aggregation_preflight
from apps_rg.runtime.aggregation.run_fingerprint import build_orchestration_fingerprint
from apps_rg.runtime.aggregation.section_sealed_index import build_section_sealed_index
from apps_rg.runtime.spine.section_x3_finalize import FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT


def _write_final_materialized_contract(
    run_dir: Path,
    lane: str,
    *,
    pass_: bool = True,
    binding_pass: bool | None = True,
) -> None:
    doc = {
        "schema_version": "apps_rg.final_materialized_acceptance_contract.v1",
        "section_id": lane,
        "gate_id": "x3_final_materialized_acceptance_contract",
        "pass": pass_,
    }
    if binding_pass is not None:
        doc["x2_final_materialized_binding_pass"] = binding_pass
    (run_dir / FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT).write_text(
        json.dumps(doc),
        encoding="utf-8",
    )


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
    _write_final_materialized_contract(run_dir, "headline")
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


def test_preflight_records_provenance_mismatch_without_blocking(tmp_path: Path) -> None:
    lanes = {}
    pointers = []
    for lane in GENERATED_LANE_IDS:
        rel = f"lane/{lane}"
        run_dir = tmp_path / rel
        run_dir.mkdir(parents=True)
        for name in (
            "l2_output.json",
            "x2_gate_outputs.json",
            "x3_disposition.json",
            "section_input_usage_ledger.json",
            "x2_source_fact_pool_receipt.json",
        ):
            (run_dir / name).write_text("{}", encoding="utf-8")
        _write_final_materialized_contract(run_dir, lane)
        lanes[lane] = {
            "latest_successful_real_artifact_path": rel,
            "x2_failed": 0,
            "x3_code": "X3_ALLOW",
        }
        pointers.append(
            {
                "lane": lane,
                "x3_code": "X3_ALLOW",
                "product_quality_status": "PASS",
                "pool_receipt_status": "PASS",
            }
        )

    fingerprint = {
        "same_date_prefix_coherent": False,
        "lane_run_ids": {lane: f"{lane}_mixed" for lane in GENERATED_LANE_IDS},
        "jd_digest_coherent": "MISMATCH",
        "briefing_digest_coherent": "MISMATCH",
    }
    results = run_aggregation_preflight(
        repo=tmp_path,
        rollup_blob={"lanes": lanes},
        fingerprint=fingerprint,
        sealed_index={"pointers": pointers},
    )

    assert next(r for r in results if r.gate_id == "x2_preflight_jd_digest_coherence").pass_
    briefing = next(r for r in results if r.gate_id == "x2_preflight_briefing_digest_coherence")
    assert briefing.pass_
    assert briefing.observed["advisory_only"] is True
    assert_preflight_pass(results)


def test_preflight_blocks_failed_final_materialized_contract(tmp_path: Path) -> None:
    lanes = {}
    pointers = []
    for lane in GENERATED_LANE_IDS:
        rel = f"lane/{lane}"
        run_dir = tmp_path / rel
        run_dir.mkdir(parents=True)
        for name in (
            "l2_output.json",
            "x2_gate_outputs.json",
            "x3_disposition.json",
            "section_input_usage_ledger.json",
            "x2_source_fact_pool_receipt.json",
        ):
            (run_dir / name).write_text("{}", encoding="utf-8")
        _write_final_materialized_contract(run_dir, lane, pass_=lane != "ey_bullets")
        lanes[lane] = {
            "latest_successful_real_artifact_path": rel,
            "x2_failed": 0,
            "x3_code": "X3_ALLOW",
        }
        pointers.append(
            {
                "lane": lane,
                "x3_code": "X3_ALLOW",
                "product_quality_status": "PASS",
                "pool_receipt_status": "PASS",
            }
        )

    results = run_aggregation_preflight(
        repo=tmp_path,
        rollup_blob={"lanes": lanes},
        fingerprint={
            "same_date_prefix_coherent": True,
            "lane_run_ids": {lane: f"{lane}_run" for lane in GENERATED_LANE_IDS},
            "jd_digest_coherent": "OK",
            "briefing_digest_coherent": "OK",
        },
        sealed_index={"pointers": pointers},
    )

    gate = next(
        r for r in results if r.gate_id == "x2_preflight_final_materialized_acceptance_contracts_pass"
    )
    assert gate.pass_ is False
    assert gate.observed == ["ey_bullets:final_materialized_acceptance_contract_failed"]


def test_preflight_blocks_pass_true_contract_without_x2_binding_proof(tmp_path: Path) -> None:
    lanes = {}
    pointers = []
    for lane in GENERATED_LANE_IDS:
        rel = f"lane/{lane}"
        run_dir = tmp_path / rel
        run_dir.mkdir(parents=True)
        for name in (
            "l2_output.json",
            "x2_gate_outputs.json",
            "x3_disposition.json",
            "section_input_usage_ledger.json",
            "x2_source_fact_pool_receipt.json",
        ):
            (run_dir / name).write_text("{}", encoding="utf-8")
        _write_final_materialized_contract(
            run_dir,
            lane,
            binding_pass=None if lane == "headline" else True,
        )
        lanes[lane] = {
            "latest_successful_real_artifact_path": rel,
            "x2_failed": 0,
            "x3_code": "X3_ALLOW",
        }
        pointers.append(
            {
                "lane": lane,
                "x3_code": "X3_ALLOW",
                "product_quality_status": "PASS",
                "pool_receipt_status": "PASS",
            }
        )

    results = run_aggregation_preflight(
        repo=tmp_path,
        rollup_blob={"lanes": lanes},
        fingerprint={
            "same_date_prefix_coherent": True,
            "lane_run_ids": {lane: f"{lane}_run" for lane in GENERATED_LANE_IDS},
            "jd_digest_coherent": "OK",
            "briefing_digest_coherent": "OK",
        },
        sealed_index={"pointers": pointers},
    )

    gate = next(
        r for r in results if r.gate_id == "x2_preflight_final_materialized_acceptance_contracts_pass"
    )
    assert gate.pass_ is False
    assert gate.observed == ["headline:final_materialized_x2_binding_not_proven"]
