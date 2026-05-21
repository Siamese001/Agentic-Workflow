"""Mandatory per-section status table for integrated full-resume runs."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.full_run_section_status import (
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


def test_persist_writes_md_and_json(tmp_path: Path):
    run_root = tmp_path / "full_resume_abc"
    _write_lane(run_root, "unify_bullets", txt_name="unify_bullets_output.txt", txt_body="- bullet one")
    out = persist_full_run_section_status(run_root, repo_root=tmp_path)
    assert (run_root / FULL_RUN_SECTION_STATUS_MD).is_file()
    assert (run_root / "full_run_section_status.json").is_file()
    payload = json.loads((run_root / "full_run_section_status.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "apps_rg.full_run_section_status.v1"
    assert any(l["lane"] == "unify_bullets" for l in payload["lanes"])
    assert out["markdown_path"].name == FULL_RUN_SECTION_STATUS_MD
