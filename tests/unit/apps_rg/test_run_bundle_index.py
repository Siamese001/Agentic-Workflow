"""Tests for RUN_BUNDLE_INDEX.json emission (apps_rg/run_bundle_index.py)."""
from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from apps_rg.runtime.run_bundle_index import (
    RUN_BUNDLE_INDEX_FILENAME,
    assert_run_bundle_index_document_shape,
    build_integrated_run_bundle_document,
    build_lane_runtime_proof_bundle_document,
    emit_integrated_run_bundle_index,
    load_apps_rg_pipeline_namespaces,
)
from apps_rg.runtime.run_correlation_links import RUN_LINKS_FILENAME
from apps_rg.runtime import run_bundle_index as run_bundle_index_mod


def _assert_repo_safe_posix(rel: str) -> None:
    assert rel
    assert not rel.startswith(("/", "\\"))
    assert ".." not in rel.split("/")
    if len(rel) > 1 and rel[1] == ":":
        raise AssertionError(f"drive path not allowed: {rel!r}")


def test_load_pipeline_namespaces_returns_tuple(tmp_path: Path) -> None:
    repo = tmp_path
    art, logn = load_apps_rg_pipeline_namespaces(repo)
    assert "artifacts" in art
    assert isinstance(logn, str)


def test_schema_integrated_and_lane(tmp_path: Path) -> None:
    repo = tmp_path
    int_dir = tmp_path / "artifacts" / "apps_rg" / "runs" / "cli_x"
    int_dir.mkdir(parents=True)
    (int_dir / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    idoc = build_integrated_run_bundle_document(repo, int_dir, run_id="a", correlation_id="a")
    assert_run_bundle_index_document_shape(idoc)
    assert idoc["bundle_kind"] == "integrated_run"
    for e in idoc["entries"]:
        for ek in ("role", "relative_path", "content_type", "required", "exists", "producer"):
            assert ek in e

    lane_dir = tmp_path / "artifacts" / "apps_rg" / "runtime_proofs" / "h" / "mock" / "z"
    lane_dir.mkdir(parents=True)
    (lane_dir / "run_manifest.json").write_text("{}", encoding="utf-8")
    (lane_dir / "l2_output.json").write_text("{}", encoding="utf-8")
    ldoc = build_lane_runtime_proof_bundle_document(repo, lane_dir, lane="headline", run_id="z")
    assert_run_bundle_index_document_shape(ldoc)
    assert ldoc["lane"] == "headline"


def test_path_safety_root_and_entries_no_absolute_no_dup(tmp_path: Path) -> None:
    repo = tmp_path
    run_dir = tmp_path / "artifacts" / "apps_rg" / "runs" / "cli_safe"
    run_dir.mkdir(parents=True)
    (run_dir / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    (run_dir / "extra_sidecar.txt").write_text("x", encoding="utf-8")
    out = run_dir / "outputs"
    out.mkdir()
    (out / "extra_out.json").write_text("{}", encoding="utf-8")
    doc = build_integrated_run_bundle_document(repo, run_dir, run_id="s", correlation_id=None)
    _assert_repo_safe_posix(str(doc["root_path"]))
    rels: list[str] = []
    for e in doc["entries"]:
        rp = str(e["relative_path"])
        _assert_repo_safe_posix(rp)
        rels.append(rp)
    assert len(rels) == len(set(rels))

    lane = tmp_path / "artifacts" / "apps_rg" / "runtime_proofs" / "es" / "mock" / "r1"
    lane.mkdir(parents=True)
    (lane / "run_manifest.json").write_text("{}", encoding="utf-8")
    (lane / "l2_output.json").write_text("{}", encoding="utf-8")
    ldoc = build_lane_runtime_proof_bundle_document(repo, lane, lane="executive_summary", run_id="r1")
    _assert_repo_safe_posix(str(ldoc["root_path"]))
    lr = [str(e["relative_path"]) for e in ldoc["entries"]]
    assert len(lr) == len(set(lr))
    for rp in lr:
        _assert_repo_safe_posix(rp)


def test_integrated_coverage_roles_when_files_present(tmp_path: Path) -> None:
    repo = tmp_path
    d = tmp_path / "artifacts" / "apps_rg" / "runs" / "full_i"
    d.mkdir(parents=True)
    files = {
        "terminal_ret_packet.json": "{}",
        "run_report.json": "{}",
        "runtime_identity_envelope.json": "{}",
        "r4_run_manifest.json": "{}",
        "agentic_core_l7_route_family_coverage.json": '{"summary":{}}',
        "agentic_core_how_trace.json": "{}",
        "runtime_exhaust_bundle.json": "{}",
        "exit_review_packet.json": "{}",
        "generated_resume.json": "[]",
        "Amit_Ayer_Resume.docx": "x",
    }
    for name, body in files.items():
        (d / name).write_text(body, encoding="utf-8")
    outp = d / "outputs"
    outp.mkdir()
    (outp / "generated_resume.json").write_text("[]", encoding="utf-8")
    (outp / "resume.docx").write_text("x", encoding="utf-8")
    doc = build_integrated_run_bundle_document(repo, d, run_id="full_i", correlation_id="full_i")
    by_role = {e["role"]: e for e in doc["entries"]}
    assert by_role["spine_terminal_ret_packet"]["exists"] is True
    assert by_role["narrative_run_report"]["exists"] is True
    assert by_role["spine_runtime_identity_envelope"]["exists"] is True
    assert by_role["spine_r4_run_manifest"]["exists"] is True
    assert by_role["audit_l7_route_family_coverage"]["exists"] is True
    assert by_role["audit_how_trace"]["exists"] is True
    assert by_role["spine_runtime_exhaust"]["exists"] is True
    assert by_role["spine_exit_review_packet"]["exists"] is True
    assert by_role["product_resume_json_flat"]["exists"] is True
    assert by_role["product_resume_json_outputs"]["exists"] is True


def test_lane_coverage_roles_when_files_present(tmp_path: Path) -> None:
    repo = tmp_path
    d = tmp_path / "artifacts" / "apps_rg" / "runtime_proofs" / "executive_summary" / "real" / "lr1"
    d.mkdir(parents=True)
    names = (
        "run_manifest.json",
        "l2_output.json",
        "x1d_llm_judge_outputs.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
        "l6_shadow_eval_package.json",
        "fact_check_result.json",
        "repair_receipt.json",
    )
    for n in names:
        (d / n).write_text("{}", encoding="utf-8")
    doc = build_lane_runtime_proof_bundle_document(repo, d, lane="executive_summary", run_id="lr1")
    br = {e["role"]: e for e in doc["entries"]}
    assert br["lane_run_manifest"]["exists"] is True
    assert br["lane_l2_output"]["exists"] is True
    assert br["judge_x1d_outputs"]["exists"] is True
    assert br["gate_x2_outputs"]["exists"] is True
    assert br["disposition_x3"]["exists"] is True
    assert br["l6_shadow_eval_package"]["exists"] is True
    assert br["fact_check_result"]["exists"] is True
    assert br["repair_receipt"]["exists"] is True


def test_extras_indexed_once_under_root_and_outputs(tmp_path: Path) -> None:
    repo = tmp_path
    d = tmp_path / "artifacts" / "apps_rg" / "runs" / "ex"
    d.mkdir(parents=True)
    (d / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    (d / "zing.txt").write_text("z", encoding="utf-8")
    od = d / "outputs"
    od.mkdir()
    (od / "other.json").write_text("{}", encoding="utf-8")
    doc = build_integrated_run_bundle_document(repo, d, run_id="ex", correlation_id=None)
    paths = [e["relative_path"] for e in doc["entries"] if e["role"].startswith("integrated_emitted_")]
    assert len(paths) == len(set(paths))
    assert any(p.endswith("/zing.txt") or p.endswith("zing.txt") for p in paths)
    assert any("outputs/other.json" in p for p in paths)


def test_required_missing_shows_exists_false(tmp_path: Path) -> None:
    repo = tmp_path
    d = tmp_path / "artifacts" / "apps_rg" / "runs" / "empty_req"
    d.mkdir(parents=True)
    doc = build_integrated_run_bundle_document(repo, d, run_id="empty_req", correlation_id=None)
    by_role = {e["role"]: e for e in doc["entries"]}
    for role in (
        "spine_terminal_ret_packet",
        "spine_runtime_identity_envelope",
        "spine_r4_run_manifest",
        "audit_l7_route_family_coverage",
        "audit_how_trace",
    ):
        assert role in by_role, f"missing required role row {role}"
        assert by_role[role]["required"] is True
        assert by_role[role]["exists"] is False
    lane = tmp_path / "lane_min"
    lane.mkdir(parents=True)
    ldoc = build_lane_runtime_proof_bundle_document(repo, lane, lane="headline", run_id="x")
    br = {e["role"]: e for e in ldoc["entries"]}
    assert br["lane_run_manifest"]["required"] is True and br["lane_run_manifest"]["exists"] is False
    assert br["lane_l2_output"]["required"] is True and br["lane_l2_output"]["exists"] is False


def test_headline_proof_strict_marks_core_bundle_paths_required(tmp_path: Path) -> None:
    from apps_rg.runtime.run_bundle_index import (
        _CANONICAL_HEADLINE_PRODUCER,
        _HEADLINE_PROOF_STRICT_SUFFIXES,
    )

    repo = tmp_path
    lane = tmp_path / "artifacts" / "apps_rg" / "runtime_proofs" / "headline" / "real" / "r_strict"
    lane.mkdir(parents=True)
    (lane / "run_manifest.json").write_text("{}", encoding="utf-8")
    (lane / "l2_output.json").write_text("{}", encoding="utf-8")
    doc_loose = build_lane_runtime_proof_bundle_document(repo, lane, lane="headline", run_id="r_strict")
    doc_strict = build_lane_runtime_proof_bundle_document(
        repo, lane, lane="headline", run_id="r_strict", proof_contract_strict=True
    )

    def _by_basename(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for e in entries:
            rp = str(e["relative_path"]).replace("\\", "/")
            base = rp.rsplit("/", 1)[-1]
            out[base] = e
        return out

    by_base_loose = _by_basename(doc_loose["entries"])
    by_base_strict = _by_basename(doc_strict["entries"])
    assert by_base_loose["claim_ledger.json"]["required"] is False
    for suf in _HEADLINE_PROOF_STRICT_SUFFIXES:
        assert suf in by_base_strict
        row = by_base_strict[suf]
        assert row["required"] is True
        assert row["producer"] == _CANONICAL_HEADLINE_PRODUCER


def test_emit_integrated_logs_on_write_oserror(caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    caplog.set_level(logging.WARNING, logger="apps_rg.runtime.run_bundle_index")

    def boom(*_a: object, **_k: object) -> None:
        raise OSError("simulated disk failure")

    monkeypatch.setattr(run_bundle_index_mod, "write_run_bundle_index", boom)
    rd = tmp_path / "artifacts" / "apps_rg" / "runs" / "logt"
    rd.mkdir(parents=True)
    (rd / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    emit_integrated_run_bundle_index(tmp_path, rd, run_id="logt", correlation_id=None)
    assert "RUN_BUNDLE_INDEX write failed" in caplog.text


def test_finalize_runtime_proof_emits_index(tmp_path: Path) -> None:
    from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run

    repo = tmp_path
    lane = "headline"
    lane_root = repo / "artifacts" / "apps_rg" / "runtime_proofs" / lane
    ad = lane_root / "mock" / "t_final"
    ad.mkdir(parents=True)
    (ad / "l2_output.json").write_text('{"runtime_generation_status":"MOCKED"}', encoding="utf-8")

    (ad / "l6_shadow_eval_package.json").write_text("{}", encoding="utf-8")
    finalize_runtime_proof_run(
        repo,
        lane,
        "mock",
        ad,
        run_id="t_final",
        section_id="headline",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
    )
    mf = json.loads((ad / "run_manifest.json").read_text(encoding="utf-8"))
    assert mf["run_dir_repo_relative"].endswith("/runtime_proofs/headline/mock/t_final")
    assert "l2_output.json" in mf["artifact_links"]
    assert "l6_shadow_eval_package.json" in mf["artifact_links"]
    assert mf["l2_output_repo_relative"].endswith("/mock/t_final/l2_output.json")
    assert mf["l6_shadow_eval_package_repo_relative"].endswith("/mock/t_final/l6_shadow_eval_package.json")
    ptr_path = repo / "artifacts" / "apps_rg" / "runtime_proofs" / lane / "latest_mock_run.json"
    ptr = json.loads(ptr_path.read_text(encoding="utf-8"))
    assert ptr["l6_shadow_eval_package_repo_relative"] == mf["l6_shadow_eval_package_repo_relative"]

    idx = ad / RUN_BUNDLE_INDEX_FILENAME
    assert idx.is_file()
    data = json.loads(idx.read_text(encoding="utf-8"))
    assert data["bundle_kind"] == "lane_runtime_proof"
    assert data["run_id"] == "t_final"


def test_finalize_does_not_fail_when_index_write_oserror(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """OSError on index write is logged; run_manifest and pointers still finalize."""
    from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run

    caplog.set_level(logging.WARNING, logger="apps_rg.runtime.run_bundle_index")

    def boom(*_a: object, **_k: object) -> None:
        raise OSError("no write")

    monkeypatch.setattr(run_bundle_index_mod, "write_run_bundle_index", boom)

    repo = tmp_path
    lane = "headline"
    ad = repo / "artifacts" / "apps_rg" / "runtime_proofs" / lane / "mock" / "t_bo"
    ad.mkdir(parents=True)
    (ad / "l2_output.json").write_text('{"runtime_generation_status":"MOCKED"}', encoding="utf-8")

    finalize_runtime_proof_run(
        repo,
        lane,
        "mock",
        ad,
        run_id="t_bo",
        section_id="headline",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
    )
    assert (ad / "run_manifest.json").is_file()
    assert "RUN_BUNDLE_INDEX write failed" in caplog.text
    assert not (ad / RUN_BUNDLE_INDEX_FILENAME).is_file()


def test_emit_integrated_writes_file(tmp_path: Path) -> None:
    repo = tmp_path
    rd = tmp_path / "artifacts" / "apps_rg" / "runs" / "z9"
    rd.mkdir(parents=True)
    (rd / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    p = emit_integrated_run_bundle_index(repo, rd, run_id="z9", correlation_id="z9")
    assert p.name == RUN_BUNDLE_INDEX_FILENAME
    assert p.is_file()
    links = rd / RUN_LINKS_FILENAME
    assert links.is_file(), "RUN_LINKS.json must be emitted after RUN_BUNDLE_INDEX"


def test_render_run_summary_succeeds_on_fixture_dir(tmp_path: Path) -> None:
    run_dir = tmp_path / "fixture_run"
    run_dir.mkdir()
    (run_dir / "terminal_ret_packet.json").write_text('{"payload":{}}', encoding="utf-8")
    (run_dir / "run_report.json").write_text("{}", encoding="utf-8")
    (run_dir / "r4_run_manifest.json").write_text("{}", encoding="utf-8")
    (run_dir / "runtime_identity_envelope.json").write_text("{}", encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[3]
    script = repo_root / "tools" / "apps_rg" / "render_run_summary.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(run_dir)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "apps_rg Run Summary" in proc.stdout


def test_unsafe_relative_suffix_rejected(tmp_path: Path) -> None:
    repo = tmp_path
    d = tmp_path / "w"
    d.mkdir()
    from apps_rg.runtime.run_bundle_index import _file_entry

    with pytest.raises(ValueError, match="unsafe relative_suffix"):
        _file_entry(
            repo,
            d,
            role="bad",
            relative_suffix="../escape.txt",
            content_type="text/plain",
            required=False,
            producer="test",
        )
