"""Product-release assembly must execute aggregate full-resume judge, not x2_no_judge_calls pass."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.assembly.final_resume_x2 import GENERATED_LANE_IDS, run_final_resume_x2_gates


def _minimal_final_resume(*, judge_calls_made: bool) -> dict:
    return {
        "final_resume_hash": "abc",
        "calls": {
            "provider_calls_made": False,
            "retired_provider_calls_made": False,
            "judge_calls_made": judge_calls_made,
            "docx_rendered": False,
        },
        "sections": [],
    }


def _gate(results, gate_id: str):
    for g in results:
        if g.gate_id == gate_id:
            return g
    raise AssertionError(gate_id)


def _paths(tmp_path: Path):
    from apps_rg.runtime.assembly.final_resume_manifest import FinalResumePaths

    out = tmp_path / "assembly"
    out.mkdir()
    repo = tmp_path
    for name in ("rollup.json", "locked.json", "locked_x2.json", "base.json"):
        (repo / name).write_text("{}", encoding="utf-8")
    return repo, FinalResumePaths(
        repo_root=repo,
        rollup_json=repo / "rollup.json",
        locked_manifest=repo / "locked.json",
        locked_x2=repo / "locked_x2.json",
        base_resume=repo / "base.json",
        output_dir=out,
    )


def _generated_rollup_row(lane: str, **overrides) -> dict:
    row = {
        "accepted_real_evidence_resolution": "modular_r4_explicit_run_dir",
        "rollup_source_run_dir": f"artifacts/apps_rg/runtime_proofs/{lane}",
        "runtime_generation_status": "REAL_LLM",
        "x2_failed": 0,
        "x2_failed_gate_ids": [],
        "x3_code": "X3_ALLOW",
    }
    row.update(overrides)
    return row


def test_final_resume_x2_accepts_patch_run_explicit_real_x3_allow_dirs(tmp_path: Path):
    repo, paths = _paths(tmp_path)
    rollup = {
        "lanes": {
            lane: _generated_rollup_row(lane)
            for lane in GENERATED_LANE_IDS
        }
    }

    results = run_final_resume_x2_gates(
        repo=repo,
        paths=paths,
        final_resume_blob=_minimal_final_resume(judge_calls_made=False),
        rollup_blob=rollup,
        locked_manifest_blob={},
        coherence_review=None,
        product_release_mode=False,
    )

    assert _gate(results, "x2_generated_sections_from_latest_successful_real").pass_ is True


def test_final_resume_x2_rejects_patch_run_explicit_dir_without_x3_allow(tmp_path: Path):
    repo, paths = _paths(tmp_path)
    rollup = {
        "lanes": {
            lane: _generated_rollup_row(lane)
            for lane in GENERATED_LANE_IDS
        }
    }
    rollup["lanes"]["headline"]["x3_code"] = "X3_BLOCK"

    results = run_final_resume_x2_gates(
        repo=repo,
        paths=paths,
        final_resume_blob=_minimal_final_resume(judge_calls_made=False),
        rollup_blob=rollup,
        locked_manifest_blob={},
        coherence_review=None,
        product_release_mode=False,
    )

    gate = _gate(results, "x2_generated_sections_from_latest_successful_real")
    assert gate.pass_ is False
    assert "headline resolution not accepted" in str(gate.observed_value)


def test_product_mode_fails_without_aggregate_judge_artifacts(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("APPS_RG_ASSEMBLY_STRUCTURAL_ONLY", raising=False)
    repo, paths = _paths(tmp_path)

    results = run_final_resume_x2_gates(
        repo=repo,
        paths=paths,
        final_resume_blob=_minimal_final_resume(judge_calls_made=False),
        rollup_blob={},
        locked_manifest_blob={},
        coherence_review=None,
        product_release_mode=True,
    )
    assert _gate(results, "x2_final_resume_aggregate_judge_executed").pass_ is False
    assert _gate(results, "x2_final_resume_aggregate_judge_artifact_present").pass_ is False
    assert _gate(results, "x2_full_resume_llm_coherence_aggregation").pass_ is False
    ids = {g.gate_id for g in results}
    assert "x2_no_judge_calls" not in ids


def test_product_mode_passes_when_coherence_artifacts_and_review_present(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("APPS_RG_ASSEMBLY_STRUCTURAL_ONLY", raising=False)
    repo, paths = _paths(tmp_path)
    out = paths.output_dir
    review = {
        "full_resume_coherence_pass": True,
        "decisive_reason": "quorum_pass_no_blockers",
        "blockers": [],
    }
    (out / "full_resume_llm_coherence_review.json").write_text(json.dumps(review), encoding="utf-8")
    (out / "x1d_full_resume_judge_outputs.json").write_text('{"judges":[]}', encoding="utf-8")

    results = run_final_resume_x2_gates(
        repo=repo,
        paths=paths,
        final_resume_blob=_minimal_final_resume(judge_calls_made=True),
        rollup_blob={},
        locked_manifest_blob={},
        coherence_review=review,
        product_release_mode=True,
    )
    assert _gate(results, "x2_final_resume_aggregate_judge_executed").pass_ is True
    assert _gate(results, "x2_final_resume_aggregate_judge_artifact_present").pass_ is True
    assert _gate(results, "x2_full_resume_llm_coherence_aggregation").pass_ is True
