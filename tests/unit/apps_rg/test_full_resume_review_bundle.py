"""Full-resume layout: flat lanes + review zip."""
from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path

from apps_rg.runtime.full_resume_review_bundle import (
    REVIEW_BUNDLE_FILENAME,
    REVIEW_INDEX_FILENAME,
    emit_full_resume_review_bundle,
)
from apps_rg.runtime.runtime_proof_layout import (
    FULL_RESUME_DIR_PREFIX,
    MODULAR_R4_SECTIONS_ROOT_ENV,
    allocate_full_resume_artifact_dir,
    prepare_runtime_proof_run_dir,
)
from apps_rg.runtime.sections_root_manifest import emit_sections_root_manifest


def test_allocate_full_resume_dir_prefix(tmp_path: Path) -> None:
    ad = allocate_full_resume_artifact_dir(tmp_path)
    assert ad.name.startswith(FULL_RESUME_DIR_PREFIX)


def test_whole_run_flat_lane_dir(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path
    ad = allocate_full_resume_artifact_dir(repo)
    lanes = ad / "lanes"
    monkeypatch.setenv("APPS_RG_MODULAR_R4_SECTIONS_ROOT", str(lanes))
    monkeypatch.setenv("APPS_RG_WHOLE_RUN_ENVELOPE", "1")
    emit_sections_root_manifest(
        repo_root=repo,
        sections_root_abs=lanes,
        source_env_literal=MODULAR_R4_SECTIONS_ROOT_ENV,
        correlation_id=ad.name,
    )
    rd = prepare_runtime_proof_run_dir(repo, "headline", "retired_provider_profile", "headline_20260520_120000")
    assert rd == ad / "lanes" / "headline"
    assert not (ad / "lanes" / "headline" / "real").exists()


def test_emit_review_bundle(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_abc123"
    run.mkdir()
    (run / "r4_run_manifest.json").write_text("{}", encoding="utf-8")
    lane = run / "lanes" / "headline"
    lane.mkdir(parents=True)
    (lane / "l2_output.json").write_text(json.dumps({"text": "ok"}), encoding="utf-8")
    zpath = emit_full_resume_review_bundle(run)
    assert zpath.is_file()
    assert (run / REVIEW_INDEX_FILENAME).is_file()
    with zipfile.ZipFile(zpath) as zf:
        names = set(zf.namelist())
    assert REVIEW_INDEX_FILENAME in names
    assert "lanes/headline/l2_output.json" in names
    assert REVIEW_BUNDLE_FILENAME not in names
