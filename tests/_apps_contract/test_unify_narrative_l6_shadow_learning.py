"""L6 shadow learning for unify_narrative — post-X3 inert observation only."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

BASE = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "unify_narrative",
    "--target-company",
    "Synthetic Enterprise Corp.",
    "--target-role",
    "SVP Engineering, Agentic AI Platforms",
    "--provider",
    "mock",
    "--mock-judges",
    "--allow-test-mock-judges",
    "--allow-non-allow-exit-zero",
]


def _latest() -> Path:
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_mock_run_dir

    rd = resolve_latest_mock_run_dir(REPO, "unify_narrative")
    assert rd is not None
    return rd


def test_canonical_run_emits_l6_shadow_learning_after_x3():
    r = subprocess.run(BASE, cwd=REPO, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr
    rd = _latest()
    assert (rd / "x3_disposition.json").is_file()
    assert (rd / "l6_shadow_learning.json").is_file()
    x3 = json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8"))
    learn = json.loads((rd / "l6_shadow_learning.json").read_text(encoding="utf-8"))
    assert learn.get("runtime_boundary_observed") is True
    assert learn.get("consumed_x3_code") == x3.get("x3_code")
    assert learn.get("section_id") == "unify_narrative"
    assert learn.get("current_run_mutation_assertion") is False
    assert learn.get("current_run_rescue_assertion") is False
    assert learn.get("durable_write_assertion") is False


def test_l6_learning_recommendations_are_future_run_only():
    subprocess.run(BASE, cwd=REPO, capture_output=True, text=True, timeout=180, check=True)
    learn = json.loads((_latest() / "l6_shadow_learning.json").read_text(encoding="utf-8"))
    for rec in learn.get("recommendation_records") or []:
        assert rec.get("applies_to") == "future_run_only"


def test_build_l6_shadow_learning_is_read_only_for_x3(tmp_path: Path):
    from apps_rg.runtime.shadow.l6_shadow_learning import build_l6_shadow_learning_record

    ad = tmp_path / "run"
    ad.mkdir()
    x3 = {
        "x3_code": "X3_BLOCK",
        "authorization_scope": "PLUMBING_ONLY",
        "proceed_to_runtime": False,
        "pass": False,
    }
    (ad / "x3_disposition.json").write_text(json.dumps(x3), encoding="utf-8")
    (ad / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_json_parse_valid", "pass": True}], "failed_gates": []}),
        encoding="utf-8",
    )
    (ad / "x1d_llm_judge_outputs.json").write_text(json.dumps({"judges": []}), encoding="utf-8")
    (ad / "parsed_output.json").write_text(json.dumps({"parse_status": "OK"}), encoding="utf-8")
    (ad / "text_claim_coverage.json").write_text(json.dumps({"overall_pass": True}), encoding="utf-8")
    (ad / "canonical_claim_ledger_v2.json").write_text(json.dumps({"parse_status": "OK"}), encoding="utf-8")

    before = (ad / "x3_disposition.json").read_bytes()
    rec = build_l6_shadow_learning_record(
        artifact_dir=ad,
        repo_root=tmp_path,
        section_id="unify_narrative",
        lane_key="unify_narrative",
    )
    after = (ad / "x3_disposition.json").read_bytes()
    assert before == after
    assert rec["consumed_x3_code"] == "X3_BLOCK"
    assert rec["current_run_mutation_assertion"] is False
    assert rec["current_run_rescue_assertion"] is False
    assert rec["durable_write_assertion"] is False


def test_l6_learning_does_not_rewrite_x3_to_allow():
    """Builder must snapshot X3_BLOCK — never imply an ALLOW rescue for the current run."""
    from apps_rg.runtime.shadow.l6_shadow_learning import build_l6_shadow_learning_record

    ad = Path(pytest.importorskip("tempfile").mkdtemp())
    try:
        x3 = {
            "x3_code": "X3_BLOCK",
            "decisive_reason": "X2",
            "review_reason": "",
            "authorization_scope": "PLUMBING_ONLY",
            "proceed_to_runtime": False,
            "pass": False,
        }
        (ad / "x3_disposition.json").write_text(json.dumps(x3), encoding="utf-8")
        (ad / "x2_gate_outputs.json").write_text(
            json.dumps(
                {
                    "gates": [{"gate_id": "x2_unify_narrative_exactly_one_sentence", "pass": False}],
                    "failed_gates": ["x2_unify_narrative_exactly_one_sentence"],
                }
            ),
            encoding="utf-8",
        )
        (ad / "x1d_llm_judge_outputs.json").write_text(json.dumps({"judges": []}), encoding="utf-8")
        (ad / "parsed_output.json").write_text(json.dumps({"parse_status": "OK"}), encoding="utf-8")
        (ad / "text_claim_coverage.json").write_text(json.dumps({"overall_pass": True}), encoding="utf-8")
        (ad / "canonical_claim_ledger_v2.json").write_text(json.dumps({"parse_status": "OK"}), encoding="utf-8")

        rec = build_l6_shadow_learning_record(
            artifact_dir=ad,
            repo_root=ad,
            section_id="unify_narrative",
            lane_key="unify_narrative",
        )
        assert rec["consumed_x3_code"] == "X3_BLOCK"
        assert rec["consumed_x3_code"] != "X3_ALLOW"
    finally:
        shutil.rmtree(ad, ignore_errors=True)


def test_l6_learning_does_not_downgrade_allow_to_block_in_snapshot():
    from apps_rg.runtime.shadow.l6_shadow_learning import build_l6_shadow_learning_record

    ad = Path(pytest.importorskip("tempfile").mkdtemp())
    try:
        x3 = {
            "x3_code": "X3_ALLOW",
            "authorization_scope": "FULL",
            "proceed_to_runtime": True,
            "pass": True,
        }
        (ad / "x3_disposition.json").write_text(json.dumps(x3), encoding="utf-8")
        (ad / "x2_gate_outputs.json").write_text(
            json.dumps({"gates": [], "failed_gates": []}), encoding="utf-8"
        )
        (ad / "x1d_llm_judge_outputs.json").write_text(json.dumps({"judges": []}), encoding="utf-8")
        (ad / "parsed_output.json").write_text(json.dumps({"parse_status": "OK"}), encoding="utf-8")
        (ad / "text_claim_coverage.json").write_text(json.dumps({"overall_pass": True}), encoding="utf-8")
        (ad / "canonical_claim_ledger_v2.json").write_text(json.dumps({"parse_status": "OK"}), encoding="utf-8")

        rec = build_l6_shadow_learning_record(
            artifact_dir=ad,
            repo_root=ad,
            section_id="unify_narrative",
            lane_key="unify_narrative",
        )
        assert rec["consumed_x3_code"] == "X3_ALLOW"
    finally:
        shutil.rmtree(ad, ignore_errors=True)


def test_l6_inert_when_x3_missing(tmp_path: Path):
    from apps_rg.runtime.shadow.l6_shadow_learning import build_l6_shadow_learning_record

    ad = tmp_path / "empty"
    ad.mkdir()
    rec = build_l6_shadow_learning_record(
        artifact_dir=ad,
        repo_root=tmp_path,
        section_id="unify_narrative",
        lane_key="unify_narrative",
    )
    assert rec["runtime_boundary_observed"] is False
    assert rec["shadow_status"] == "inert_blocked_missing_upstream"
    assert rec["current_run_mutation_assertion"] is False
