"""Tests for RUN_LINKS.json (W3.1 correlation manifest)."""
from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.run_bundle_index import (
    RUN_BUNDLE_INDEX_FILENAME,
    build_integrated_run_bundle_document,
    build_log_discovery_metadata,
    emit_integrated_run_bundle_index,
)
from apps_rg.runtime.run_correlation_links import (
    RUN_LINKS_FILENAME,
    assert_run_links_document_shape,
    build_modular_sections_root_attachment,
    build_run_links_document,
    discover_lane_bundle_refs,
    emit_integrated_run_links,
    finalize_lane_bundle_ref_rows,
)
from apps_rg.runtime.runtime_proof_layout import (
    MODULAR_R4_SECTIONS_ROOT_ENV,
    modular_sections_root_from_env,
    prepare_runtime_proof_run_dir,
)
from apps_rg.runtime.sections_root_manifest import emit_sections_root_manifest
from apps_rg.runtime import run_bundle_index as run_bundle_index_mod
from apps_rg.runtime import run_correlation_links as run_correlation_links_mod


def _write_pipeline_defaults(
    repo: Path,
    *,
    log_namespace: str = "apps_rg/pipeline_logs",
    telemetry_prefix: str | None = "apps_rg.r4_integrated",
) -> None:
    cfg_dir = repo / "config" / "profiles" / "apps_rg"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    yaml_text = (
        'schema_version: "1.0"\n'
        "app_id: apps_rg\n"
        "profile_type: pipeline_defaults\n"
        "pipeline_config:\n"
        "  default_timeout_seconds: 900\n"
        "namespace_defaults:\n"
        '  artifact_namespace: "artifacts/apps_rg/runs"\n'
        f'  log_namespace: "{log_namespace}"\n'
    )
    if telemetry_prefix is not None:
        yaml_text += f'  telemetry_prefix: "{telemetry_prefix}"\n'
    (cfg_dir / "pipeline_defaults.yaml").write_text(yaml_text, encoding="utf-8")


def _assert_repo_safe_posix(rel: str) -> None:
    assert rel
    assert not rel.startswith(("/", "\\"))
    assert ".." not in rel.split("/")
    if len(rel) > 1 and rel[1] == ":":
        raise AssertionError(f"drive path not allowed: {rel!r}")


def test_run_links_schema_empty_lane_bundle_refs(tmp_path: Path) -> None:
    repo = tmp_path
    int_dir = tmp_path / "artifacts" / "apps_rg" / "runs" / "clean"
    int_dir.mkdir(parents=True)
    (int_dir / "terminal_ret_packet.json").write_text('{"hints": []}', encoding="utf-8")
    doc = build_run_links_document(
        repo,
        int_dir,
        integrated_run_id="clean",
        correlation_id=None,
    )
    assert_run_links_document_shape(doc)
    assert doc["lane_bundle_refs"] == []
    assert isinstance(doc["aggregate_refs"], list)


def test_run_links_repo_relative_posix_all_paths(tmp_path: Path) -> None:
    repo = tmp_path
    int_dir = tmp_path / "artifacts" / "apps_rg" / "runs" / "p1"
    int_dir.mkdir(parents=True)
    (int_dir / "run_report.json").write_text(
        'trace: artifacts/apps_rg/runtime_proofs/headline/mock/lane_run_1/note.txt\n',
        encoding="utf-8",
    )

    lane = tmp_path / "artifacts" / "apps_rg" / "runtime_proofs" / "headline" / "mock" / "lane_run_1"
    lane.mkdir(parents=True)
    (lane / RUN_BUNDLE_INDEX_FILENAME).write_text(json.dumps({"correlation_id": None}), encoding="utf-8")

    doc = build_run_links_document(repo, int_dir, integrated_run_id="p1", correlation_id="corr-1")

    assert_run_links_document_shape(doc)
    root = Path(__file__).resolve()
    assert root.parts  # quiet unused in some interpreters
    del root
    for key in ("root_path", "integrated_bundle_index_ref"):
        _assert_repo_safe_posix(str(doc[key]))
    for row in doc["lane_bundle_refs"]:
        _assert_repo_safe_posix(row["bundle_index_ref"])
        _assert_repo_safe_posix(row["root_path"])
    for row in doc["aggregate_refs"]:
        _assert_repo_safe_posix(str(row["relative_path"]))


def test_discovered_lane_points_at_bundle_index_when_present(tmp_path: Path) -> None:
    repo = tmp_path
    integrated = repo / "artifacts" / "apps_rg" / "runs" / "ic"
    integrated.mkdir(parents=True)
    (integrated / "r4_run_manifest.json").write_text(
        '{"path":"artifacts/apps_rg/runtime_proofs/exec_summary/mock/r99/"}',
        encoding="utf-8",
    )
    lane = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "exec_summary" / "mock" / "r99"
    lane.mkdir(parents=True)
    idx = lane / RUN_BUNDLE_INDEX_FILENAME
    idx.write_text(json.dumps({"correlation_id": None, "bundle_kind": "lane_runtime_proof"}), encoding="utf-8")

    doc = build_run_links_document(repo, integrated, integrated_run_id="ic", correlation_id=None)
    assert doc["lane_bundle_refs"]
    row = doc["lane_bundle_refs"][0]
    assert row["lane"] == "exec_summary"
    assert row["proof_mode"] == "mock"
    assert row["exists"] is True
    bundle_ref = lane.relative_to(repo).as_posix() + "/" + RUN_BUNDLE_INDEX_FILENAME
    assert row["bundle_index_ref"] == bundle_ref


def test_duplicate_corpus_path_dedupes_lane_rows(tmp_path: Path) -> None:
    corpus = (
        'a artifacts/apps_rg/runtime_proofs/headline/mock/dup_lane/x.json '
        'b artifacts/apps_rg/runtime_proofs/headline/mock/dup_lane/y.json '
    )
    repo = tmp_path
    refs = discover_lane_bundle_refs(repo, corpus, correlation_id=None)
    assert len(refs) == 1
    assert refs[0]["run_id"] == "dup_lane"


def test_finalize_dedupe_same_bundle_index_ref_keeps_lexicographically_smallest_triple() -> None:
    shared = "artifacts/apps_rg/runtime_proofs/x/mock/y/RUN_BUNDLE_INDEX.json"
    row_a = {
        "lane": "headline",
        "proof_mode": "mock",
        "run_id": "a",
        "bundle_index_ref": shared,
        "root_path": "artifacts/apps_rg/runtime_proofs/headline/mock/a",
        "exists": True,
        "producer": "t",
    }
    row_b = {
        "lane": "exec_summary",
        "proof_mode": "mock",
        "run_id": "z",
        "bundle_index_ref": shared,
        "root_path": "artifacts/apps_rg/runtime_proofs/exec_summary/mock/z",
        "exists": True,
        "producer": "t",
    }
    triple_map = {
        ("headline", "mock", "a"): row_a,
        ("exec_summary", "mock", "z"): row_b,
    }
    out = finalize_lane_bundle_ref_rows(triple_map)
    assert len(out) == 1
    assert out[0]["lane"] == "exec_summary"


def test_lane_skipped_when_correlation_mismatch(tmp_path: Path) -> None:
    repo = tmp_path
    corpus = 'x artifacts/apps_rg/runtime_proofs/headline/mock/bad_corr/z.json '
    lane = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "headline" / "mock" / "bad_corr"
    lane.mkdir(parents=True)
    (lane / RUN_BUNDLE_INDEX_FILENAME).write_text(
        json.dumps({"correlation_id": "lane-only"}),
        encoding="utf-8",
    )
    refs = discover_lane_bundle_refs(repo, corpus, correlation_id="integrated-x")
    assert refs == []


def test_emit_integrated_writes_run_links_next_to_bundle_index(tmp_path: Path) -> None:
    repo = tmp_path
    rd = repo / "artifacts" / "apps_rg" / "runs" / "with_links"
    rd.mkdir(parents=True)
    (rd / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    emit_integrated_run_bundle_index(repo, rd, run_id="with_links", correlation_id="c1")
    links = rd / RUN_LINKS_FILENAME
    assert links.is_file()
    payload = json.loads(links.read_text(encoding="utf-8"))
    assert_run_links_document_shape(payload)


def test_log_discovery_unavailable_without_config_when_no_log_dir(tmp_path: Path) -> None:
    """No pipeline_defaults.yaml: no telemetry_prefix; default log dir absent -> unavailable."""
    repo = tmp_path
    ld = build_log_discovery_metadata(repo)
    assert ld["mode"] == "unavailable"
    assert ld["log_root_path"] is None
    assert ld["log_namespace"] == "apps_rg/pipeline_logs"


def test_log_discovery_telemetry_only_when_prefix_configured_but_dir_missing(tmp_path: Path) -> None:
    _write_pipeline_defaults(tmp_path, telemetry_prefix="apps_rg.otlp_test")
    ld = build_log_discovery_metadata(tmp_path)
    assert ld["mode"] == "telemetry_only"
    assert ld["log_root_path"] is None


def test_log_discovery_disk_when_log_namespace_directory_exists(tmp_path: Path) -> None:
    _write_pipeline_defaults(tmp_path)
    log_root = tmp_path / "apps_rg" / "pipeline_logs"
    log_root.mkdir(parents=True)
    ld = build_log_discovery_metadata(tmp_path)
    assert ld["mode"] == "disk"
    assert ld["log_root_path"] == "apps_rg/pipeline_logs"


def test_unsafe_log_namespace_raises_value_error(tmp_path: Path) -> None:
    _write_pipeline_defaults(tmp_path, log_namespace="../escape_logs")
    with pytest.raises(ValueError, match="path escape"):
        build_log_discovery_metadata(tmp_path)


def test_build_run_links_includes_log_discovery_shape(tmp_path: Path) -> None:
    repo = tmp_path
    _write_pipeline_defaults(repo, telemetry_prefix="apps_rg.otlp_test")
    int_dir = tmp_path / "artifacts" / "apps_rg" / "runs" / "lx"
    int_dir.mkdir(parents=True)
    (int_dir / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    doc = build_run_links_document(repo, int_dir, integrated_run_id="lx", correlation_id=None)
    assert_run_links_document_shape(doc)
    assert doc["log_discovery"]["mode"] == "telemetry_only"


def test_integrated_bundle_index_has_log_root_path_only_when_disk(tmp_path: Path) -> None:
    _write_pipeline_defaults(tmp_path)
    run_dir = tmp_path / "artifacts" / "apps_rg" / "runs" / "ix"
    run_dir.mkdir(parents=True)
    (run_dir / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    pl_dir = tmp_path / "apps_rg" / "pipeline_logs"
    pl_dir.mkdir(parents=True)
    doc = build_integrated_run_bundle_document(tmp_path, run_dir, run_id="ix", correlation_id=None)
    assert doc.get("log_root_path") == "apps_rg/pipeline_logs"


def test_integrated_emit_raises_value_error_on_unsafe_log_namespace(tmp_path: Path) -> None:
    rd = tmp_path / "artifacts" / "apps_rg" / "runs" / "bad"
    rd.mkdir(parents=True)
    (rd / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    _write_pipeline_defaults(tmp_path, log_namespace="/abs/logs")
    with pytest.raises(ValueError, match="absolute"):
        emit_integrated_run_bundle_index(tmp_path, rd, run_id="bad")


def test_oserror_bundle_index_write_logs_warning_but_run_links_still_writes(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    caplog.set_level(logging.WARNING, logger="apps_rg.runtime.run_bundle_index")

    def boom_idx(*_a: object, **_k: object) -> None:
        raise OSError("simulated RUN_BUNDLE_INDEX write failure")

    monkeypatch.setattr(run_bundle_index_mod, "write_run_bundle_index", boom_idx)

    rd = tmp_path / "artifacts" / "apps_rg" / "runs" / "dualfail"
    rd.mkdir(parents=True)
    (rd / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    emit_integrated_run_bundle_index(tmp_path, rd, run_id="dualfail", correlation_id=None)
    assert "RUN_BUNDLE_INDEX write failed" in caplog.text
    assert (rd / RUN_LINKS_FILENAME).is_file()


def test_oserror_run_links_write_logs_warning(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    caplog.set_level(logging.WARNING, logger="apps_rg.runtime.run_correlation_links")

    def boom(_d: object, _doc: object) -> None:
        raise OSError("no space")

    monkeypatch.setattr(run_correlation_links_mod, "write_run_links", boom)
    rd = tmp_path / "artifacts" / "apps_rg" / "runs" / "rlfail"
    rd.mkdir(parents=True)
    (rd / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    out = emit_integrated_run_links(tmp_path, rd, integrated_run_id="rlfail", correlation_id=None)
    assert out.name == RUN_LINKS_FILENAME
    assert "RUN_LINKS write failed" in caplog.text


def test_modular_sections_root_default_when_env_unset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(MODULAR_R4_SECTIONS_ROOT_ENV, raising=False)
    att = build_modular_sections_root_attachment(tmp_path)
    assert att["mode"] == "default"
    assert att["manifest_ref"] is None
    assert att["root_path"] is None
    assert att["exists"] is False


def test_modular_env_outside_repo_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "workspace" / "repo"
    repo.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.setenv(MODULAR_R4_SECTIONS_ROOT_ENV, str(outside.resolve()))
    with pytest.raises(ValueError, match="inside repo_root"):
        modular_sections_root_from_env(repo)


def test_modular_env_dotdot_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(MODULAR_R4_SECTIONS_ROOT_ENV, "../escape")
    with pytest.raises(ValueError, match=r"\.\."):
        modular_sections_root_from_env(tmp_path)


def test_prepare_runtime_proof_requires_manifest_when_modular_env_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    sr = tmp_path / "modular_sections_here"
    sr.mkdir()
    monkeypatch.setenv(MODULAR_R4_SECTIONS_ROOT_ENV, str(sr.resolve()))
    with pytest.raises(ValueError, match="sections_root_manifest"):
        prepare_runtime_proof_run_dir(tmp_path, "headline", "mock", "r1")


def test_run_links_modular_env_manifest_required(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sr = tmp_path / "sections_w4"
    sr.mkdir()
    monkeypatch.setenv(MODULAR_R4_SECTIONS_ROOT_ENV, str(sr.resolve()))
    int_dir = tmp_path / "artifacts" / "apps_rg" / "runs" / "lw4"
    int_dir.mkdir(parents=True)
    (int_dir / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="sections_root_manifest"):
        build_run_links_document(tmp_path, int_dir, integrated_run_id="lw4", correlation_id=None)


def test_run_links_records_modular_env_manifest_when_emit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    sr = tmp_path / "sections_linked"
    sr.mkdir()
    emit_sections_root_manifest(
        repo_root=tmp_path,
        sections_root_abs=sr,
        source_env_literal=MODULAR_R4_SECTIONS_ROOT_ENV,
        integrated_run_ref="artifacts/apps_rg/runs/linked_case",
        run_links_ref=None,
        notes=None,
    )
    monkeypatch.setenv(MODULAR_R4_SECTIONS_ROOT_ENV, str(sr.resolve()))
    int_dir = tmp_path / "artifacts" / "apps_rg" / "runs" / "linked_case"
    int_dir.mkdir(parents=True)
    (int_dir / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    doc = build_run_links_document(tmp_path, int_dir, integrated_run_id="linked_case", correlation_id=None)
    assert doc["modular_sections_root"]["mode"] == "env_manifest"
    assert doc["modular_sections_root"]["exists"] is True
    assert doc["modular_sections_root"]["manifest_ref"].endswith("sections_root_manifest.json")


def test_integrated_emit_includes_modular_block(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sr = tmp_path / "sections_int"
    sr.mkdir()
    emit_sections_root_manifest(
        repo_root=tmp_path,
        sections_root_abs=sr,
        source_env_literal=MODULAR_R4_SECTIONS_ROOT_ENV,
        correlation_id=None,
        integrated_run_ref=None,
        run_links_ref=None,
    )
    monkeypatch.setenv(MODULAR_R4_SECTIONS_ROOT_ENV, str(sr.resolve()))
    rd = tmp_path / "artifacts" / "apps_rg" / "runs" / "imod"
    rd.mkdir(parents=True)
    (rd / "terminal_ret_packet.json").write_text("{}", encoding="utf-8")
    emit_integrated_run_bundle_index(tmp_path, rd, run_id="imod")
    monkeypatch.delenv(MODULAR_R4_SECTIONS_ROOT_ENV, raising=False)
    payload = json.loads((rd / RUN_LINKS_FILENAME).read_text(encoding="utf-8"))
    assert payload["modular_sections_root"]["mode"] == "env_manifest"


@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[3] / "artifacts" / "apps_rg" / "runs" / "_proof_smoke_integrated")
    .is_dir(),
    reason="repo smoke integrated dir not present",
)
def test_render_run_summary_exits_zero_on_smoke_integrated() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    run_dir = repo_root / "artifacts" / "apps_rg" / "runs" / "_proof_smoke_integrated"
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
