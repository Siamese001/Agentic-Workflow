"""Product-release assembly must execute aggregate full-resume judge, not x2_no_judge_calls pass."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.assembly.final_resume_x2 import run_final_resume_x2_gates


def _minimal_final_resume(*, judge_calls_made: bool) -> dict:
    return {
        "final_resume_hash": "abc",
        "calls": {
            "provider_calls_made": False,
            "qwen_calls_made": False,
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


def test_product_mode_fails_without_aggregate_judge_artifacts(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("APPS_RG_ASSEMBLY_STRUCTURAL_ONLY", raising=False)
    out = tmp_path / "assembly"
    out.mkdir()
    repo = tmp_path
    from apps_rg.runtime.assembly.final_resume_manifest import FinalResumePaths

    paths = FinalResumePaths(
        repo_root=repo,
        rollup_json=repo / "rollup.json",
        locked_manifest=repo / "locked.json",
        locked_x2=repo / "locked_x2.json",
        base_resume=repo / "base.json",
        output_dir=out,
    )
    (repo / "rollup.json").write_text("{}", encoding="utf-8")
    (repo / "locked.json").write_text("{}", encoding="utf-8")
    (repo / "locked_x2.json").write_text("{}", encoding="utf-8")
    (repo / "base.json").write_text("{}", encoding="utf-8")

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
    out = tmp_path / "assembly"
    out.mkdir()
    review = {
        "full_resume_coherence_pass": True,
        "decisive_reason": "quorum_pass_no_blockers",
        "blockers": [],
    }
    (out / "full_resume_llm_coherence_review.json").write_text(json.dumps(review), encoding="utf-8")
    (out / "x1d_full_resume_judge_outputs.json").write_text('{"judges":[]}', encoding="utf-8")

    repo = tmp_path
    from apps_rg.runtime.assembly.final_resume_manifest import FinalResumePaths

    paths = FinalResumePaths(
        repo_root=repo,
        rollup_json=repo / "rollup.json",
        locked_manifest=repo / "locked.json",
        locked_x2=repo / "locked_x2.json",
        base_resume=repo / "base.json",
        output_dir=out,
    )
    for name in ("rollup.json", "locked.json", "locked_x2.json", "base.json"):
        (repo / name).write_text("{}", encoding="utf-8")

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
