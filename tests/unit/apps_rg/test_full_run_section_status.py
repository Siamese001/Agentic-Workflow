"""Mandatory per-section status table for integrated full-resume runs."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.full_run_section_status import (
    FINAL_AGGREGATION_LANE,
    FULL_RUN_SECTION_STATUS_MD,
    collect_full_run_section_status,
    persist_full_run_section_status,
    render_full_run_section_status_markdown,
)


def _write_lane(
    root: Path,
    lane: str,
    *,
    txt_name: str,
    txt_body: str,
    x3_code: str = "ALLOW",
    x2_pass: bool = True,
    failed_gate: str | None = None,
) -> None:
    lane_dir = root / "lanes" / lane
    lane_dir.mkdir(parents=True, exist_ok=True)
    (lane_dir / txt_name).write_text(txt_body + "\n", encoding="utf-8")
    (lane_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": x3_code, "product_quality_status": "PASS"}) + "\n",
        encoding="utf-8",
    )
    gates = []
    if failed_gate:
        gates.append({"gate_id": failed_gate, "pass": False})
    else:
        gates.append({"gate_id": "x2_smoke", "pass": x2_pass})
    (lane_dir / "x2_gate_outputs.json").write_text(json.dumps({"gates": gates}) + "\n", encoding="utf-8")
    (lane_dir / "run_manifest.json").write_text(
        json.dumps({"runtime_generation_status": "REAL_LLM"}) + "\n",
        encoding="utf-8",
    )


def _write_final_aggregation(root: Path) -> None:
    asm = root / "modular_r4" / "final_resume_assembly"
    asm.mkdir(parents=True, exist_ok=True)
    (asm / "final_resume.json").write_text('{"sections": []}\n', encoding="utf-8")
    (asm / "aggregation_preflight.json").write_text(
        json.dumps({"all_pass": True}) + "\n",
        encoding="utf-8",
    )
    (asm / "final_resume_x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_full_resume_llm_coherence_aggregation", "pass": True}]})
        + "\n",
        encoding="utf-8",
    )
    (asm / "full_resume_llm_coherence_review.json").write_text(
        json.dumps(
            {
                "criteria_scores": {
                    "mean_normalized_score": 0.94,
                    "model_backed_pass_count": 2,
                    "model_backed_total": 2,
                },
                "full_resume_coherence_pass": True,
                "aggregation_method": "quorum_majority_model_backed",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (asm / "x1d_full_resume_judge_outputs.json").write_text(
        json.dumps(
            {
                "aggregation": {
                    "aggregation_method": "quorum_majority_model_backed",
                    "full_resume_coherence_pass": True,
                    "model_backed_pass_count": 2,
                    "model_backed_total": 2,
                },
                "judges": [
                    {
                        "judge_id": "gemini",
                        "provider_name": "Google Gemini 3.1 Pro Preview",
                        "provider_key": "gemini_pro",
                        "model_name": "gemini-3.1-pro-preview",
                        "score": 5.0,
                        "threshold": 4.0,
                        "pass": True,
                        "provider_status": "MODEL_BACKED_PASS",
                    },
                    {
                        "judge_id": "openai",
                        "provider_name": "OpenAI ChatGPT",
                        "provider_key": "openai_chatgpt",
                        "model_name": "gpt-5.5",
                        "score": 4.4,
                        "threshold": 4.0,
                        "pass": True,
                        "provider_status": "MODEL_BACKED_PASS",
                    },
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_collect_rows_include_display_txt_links(tmp_path: Path):
    run_root = tmp_path / "full_resume_test123"
    _write_lane(run_root, "headline", txt_name="headline_output.txt", txt_body="SVP | AI | Cloud")
    _write_lane(
        run_root,
        "competencies",
        txt_name="competencies_display.txt",
        txt_body="Agentic AI: routing, orchestration",
        x3_code="BLOCK",
        x2_pass=False,
        failed_gate="x2_competencies_keyword_repetition_limit",
    )
    rows = collect_full_run_section_status(run_root, repo_root=tmp_path)
    by_lane = {r.lane: r for r in rows}
    assert by_lane["headline"].display_txt_rel == "lanes/headline/headline_output.txt"
    assert by_lane["competencies"].display_txt_rel == "lanes/competencies/competencies_display.txt"
    assert by_lane["competencies"].x3_code == "BLOCK"
    assert "x2_competencies_keyword_repetition_limit" in by_lane["competencies"].x2_failed_gate_ids

    md = render_full_run_section_status_markdown(rows, run_root=run_root, repo_root=tmp_path)
    assert "lanes/headline/headline_output.txt" in md
    assert "lanes/competencies/competencies_display.txt" in md
    assert "x2_competencies_keyword_repetition_limit" in md


def test_collect_rows_support_modular_r4_sections_layout(tmp_path: Path):
    run_root = tmp_path / "anthropic_custom_run"
    comp_base = run_root / "modular_r4" / "sections" / "competencies"
    comp_run = comp_base / "real" / "competencies_20260702_120000"
    comp_run.mkdir(parents=True, exist_ok=True)
    (comp_run / "competencies_display.txt").write_text(
        "Applied AI Partnerships: partner architecture\n",
        encoding="utf-8",
    )
    (comp_run / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "product_quality_status": "PASS"}) + "\n",
        encoding="utf-8",
    )
    (comp_run / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_smoke", "pass": True}]}) + "\n",
        encoding="utf-8",
    )
    (comp_run / "run_manifest.json").write_text(
        json.dumps({"runtime_generation_status": "REAL_LLM"}) + "\n",
        encoding="utf-8",
    )
    (comp_base / "latest_real_run.json").write_text(
        json.dumps({"run_dir": comp_run.relative_to(tmp_path).as_posix()}) + "\n",
        encoding="utf-8",
    )

    headline_base = run_root / "modular_r4" / "sections" / "headline"
    headline_base.mkdir(parents=True, exist_ok=True)
    (headline_base / "integrated_lane_pre_run_failure.json").write_text(
        json.dumps({"blocker": "PHASE1_NO_RUN_DIR"}) + "\n",
        encoding="utf-8",
    )

    rows = collect_full_run_section_status(run_root, repo_root=tmp_path)
    by_lane = {r.lane: r for r in rows}

    assert by_lane["competencies"].display_txt_rel.endswith(
        "modular_r4/sections/competencies/real/competencies_20260702_120000/competencies_display.txt"
    )
    assert by_lane["competencies"].x3_code == "X3_ALLOW"
    assert by_lane["competencies"].runtime_generation_status == "REAL_LLM"
    assert by_lane["headline"].x3_code == "PRE_RUN:PHASE1_NO_RUN_DIR"


def test_collect_rows_support_flat_lane_pointer_to_sibling_runtime_proof(tmp_path: Path):
    run_root = tmp_path / "full_resume_wrapper"
    lane_base = run_root / "lanes" / "competencies"
    lane_base.mkdir(parents=True, exist_ok=True)
    lane_run = tmp_path / "artifacts" / "apps_rg" / "runtime_proofs" / "competencies_real_123"
    lane_run.mkdir(parents=True, exist_ok=True)
    (lane_run / "competencies_display.txt").write_text(
        "Applied AI Partnerships: partner architecture\n",
        encoding="utf-8",
    )
    (lane_run / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "product_quality_status": "PASS"}) + "\n",
        encoding="utf-8",
    )
    (lane_run / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_smoke", "pass": True}]}) + "\n",
        encoding="utf-8",
    )
    (lane_run / "run_manifest.json").write_text(
        json.dumps({"runtime_generation_status": "REAL_LLM"}) + "\n",
        encoding="utf-8",
    )
    (lane_run / "x1d_llm_judge_outputs.json").write_text(
        json.dumps(
            {
                "judges": [
                    {
                        "provider_name": "Google Gemini 3.1 Pro Preview",
                        "model_name": "gemini-3.1-pro-preview",
                        "score": 5.0,
                        "threshold": 4.0,
                        "pass": True,
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (lane_base / "latest_successful_real_run.json").write_text(
        json.dumps({"run_dir": lane_run.relative_to(tmp_path).as_posix()}) + "\n",
        encoding="utf-8",
    )

    rows = collect_full_run_section_status(run_root, repo_root=tmp_path)
    row = {r.lane: r for r in rows}["competencies"]

    assert row.lane_dir == lane_run.relative_to(tmp_path).as_posix()
    assert row.display_txt_rel == (
        lane_run / "competencies_display.txt"
    ).relative_to(tmp_path).as_posix()
    assert row.x3_code == "X3_ALLOW"
    assert row.x2_pass == "PASS"
    assert row.runtime_generation_status == "REAL_LLM"
    assert "Google Gemini 3.1 Pro Preview" in row.judge_summary


def test_persist_infers_repo_root_for_modular_pointers(tmp_path: Path):
    (tmp_path / "apps_rg" / "resume" / "base").mkdir(parents=True)
    run_root = tmp_path / "artifacts" / "apps_rg" / "runs" / "whole_run"
    lane_base = run_root / "modular_r4" / "sections" / "competencies"
    lane_base.mkdir(parents=True, exist_ok=True)
    lane_run = tmp_path / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_abc123"
    lane_run.mkdir(parents=True, exist_ok=True)
    (lane_run / "competencies_display.txt").write_text(
        "Applied AI Partnerships: partner architecture\n",
        encoding="utf-8",
    )
    (lane_run / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "product_quality_status": "PASS"}) + "\n",
        encoding="utf-8",
    )
    (lane_run / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_smoke", "pass": True}]}) + "\n",
        encoding="utf-8",
    )
    (lane_run / "run_manifest.json").write_text(
        json.dumps({"runtime_generation_status": "REAL_LLM"}) + "\n",
        encoding="utf-8",
    )
    (lane_base / "latest_successful_real_run.json").write_text(
        json.dumps({"run_dir": lane_run.relative_to(tmp_path).as_posix()}) + "\n",
        encoding="utf-8",
    )

    out = persist_full_run_section_status(run_root)
    payload = out["payload"]
    row = next(lane for lane in payload["lanes"] if lane["lane"] == "competencies")

    assert row["lane_dir"] == lane_run.relative_to(tmp_path).as_posix()
    assert row["x3_code"] == "X3_ALLOW"
    assert row["x2_pass"] == "PASS"
    assert row["runtime_generation_status"] == "REAL_LLM"
    assert row["display_txt_relpath"] == (
        lane_run / "competencies_display.txt"
    ).relative_to(tmp_path).as_posix()


def test_collect_rows_prefers_current_generated_rollup_over_stale_pointer(tmp_path: Path):
    run_root = tmp_path / "full_resume_wrapper"
    lane_base = run_root / "lanes" / "executive_summary"
    lane_base.mkdir(parents=True, exist_ok=True)
    stale_run = tmp_path / "artifacts" / "apps_rg" / "runtime_proofs" / "exec_stale"
    stale_run.mkdir(parents=True, exist_ok=True)
    (stale_run / "resume_display_text.txt").write_text("Stale blocked summary.\n", encoding="utf-8")
    (stale_run / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_BLOCK", "product_quality_status": "FAIL"}) + "\n",
        encoding="utf-8",
    )
    (stale_run / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_old", "pass": False}]}) + "\n",
        encoding="utf-8",
    )
    (lane_base / "latest_successful_real_run.json").write_text(
        json.dumps({"run_dir": stale_run.relative_to(tmp_path).as_posix()}) + "\n",
        encoding="utf-8",
    )

    current_run = tmp_path / "artifacts" / "apps_rg" / "runtime_proofs" / "exec_current"
    current_run.mkdir(parents=True, exist_ok=True)
    (current_run / "resume_display_text.txt").write_text("Current authorized summary.\n", encoding="utf-8")
    (current_run / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "product_quality_status": "PASS"}) + "\n",
        encoding="utf-8",
    )
    (current_run / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_smoke", "pass": True}]}) + "\n",
        encoding="utf-8",
    )
    (current_run / "run_manifest.json").write_text(
        json.dumps({"runtime_generation_status": "REAL_LLM"}) + "\n",
        encoding="utf-8",
    )
    rollup_dir = run_root / "modular_r4" / "generated_lane_rollup"
    rollup_dir.mkdir(parents=True, exist_ok=True)
    (rollup_dir / "generated_lane_rollup.json").write_text(
        json.dumps(
            {
                "lanes": {
                    "executive_summary": {
                        "accepted_real_evidence_resolution": "modular_r4_explicit_run_dir",
                        "rollup_source_run_dir": current_run.relative_to(tmp_path).as_posix(),
                    }
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    rows = collect_full_run_section_status(run_root, repo_root=tmp_path)
    row = {r.lane: r for r in rows}["executive_summary"]

    assert row.lane_dir == current_run.relative_to(tmp_path).as_posix()
    assert row.x3_code == "X3_ALLOW"
    assert row.x2_pass == "PASS"
    assert row.display_txt_rel == (
        current_run / "resume_display_text.txt"
    ).relative_to(tmp_path).as_posix()


def test_collect_rows_append_final_aggregation_lane_with_judges(tmp_path: Path):
    run_root = tmp_path / "full_resume_test123"
    _write_lane(run_root, "headline", txt_name="headline_output.txt", txt_body="SVP | AI | Cloud")
    _write_final_aggregation(run_root)

    rows = collect_full_run_section_status(run_root, repo_root=tmp_path)
    final = rows[-1]

    assert final.lane == FINAL_AGGREGATION_LANE
    assert final.executed is True
    assert final.x3_code == "X3_ALLOW"
    assert final.x2_pass == "PASS"
    assert final.product_quality == "PASS"
    assert final.runtime_generation_status == "ASSEMBLED"
    assert final.aggregation_pass == "PASS"
    assert final.mean_normalized_score == "0.94"
    assert final.model_backed_pass_count == "2"
    assert final.model_backed_total == "2"
    assert "Google Gemini 3.1 Pro Preview" in final.judge_summary
    assert "OpenAI ChatGPT" in final.judge_summary
    assert final.display_txt_rel == "modular_r4/final_resume_assembly/final_resume.json"

    md = render_full_run_section_status_markdown(rows, run_root=run_root, repo_root=tmp_path)
    assert FINAL_AGGREGATION_LANE in md
    assert "Google Gemini 3.1 Pro Preview" in md
    assert "gpt-5.5" in md


def test_persist_writes_md_and_json(tmp_path: Path):
    run_root = tmp_path / "full_resume_abc"
    _write_lane(run_root, "unify_bullets", txt_name="unify_bullets_output.txt", txt_body="- bullet one")
    _write_final_aggregation(run_root)
    out = persist_full_run_section_status(run_root, repo_root=tmp_path)
    assert (run_root / FULL_RUN_SECTION_STATUS_MD).is_file()
    assert (run_root / "full_run_section_status.json").is_file()
    payload = json.loads((run_root / "full_run_section_status.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "apps_rg.full_run_section_status.v1"
    assert any(l["lane"] == "unify_bullets" for l in payload["lanes"])
    aggregate = next(l for l in payload["lanes"] if l["lane"] == FINAL_AGGREGATION_LANE)
    assert aggregate["aggregation_method"] == "quorum_majority_model_backed"
    assert len(aggregate["judges"]) == 2
    assert out["markdown_path"].name == FULL_RUN_SECTION_STATUS_MD
