"""Archive-aware artifact verification regression tests.

Plan: NEXT_STEP `adg-pipeline-artifact-packaging`. ``_verify_artifacts``
runs AFTER ``_archive_old_artifacts`` in the pipeline, so by the time
verification fires the freshly-built zip may already have been moved
into ``artifacts/adg/_archive/<YYYY-MM>/`` and gzipped from
``adg_run_<ts>.zip`` to ``adg_run_<ts>.zip.gz``.

The fix added ``_artifact_locations`` / ``_artifact_present`` helpers
that check root, the timestamped archive month-dir, and ``.gz``
variants. These tests pin that contract.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from tools.generate.core.helpers import (
    _artifact_locations,
    _artifact_present,
    _verify_artifacts,
)


TS = "04282026_0933"
ARCHIVE_MONTH_DIR = "_archive/2026-04"


class TestArtifactLocations:
    def test_returns_root_plus_archive_plus_gz_variants(self, tmp_path: Path) -> None:
        locs = _artifact_locations(tmp_path, TS, f"adg_run_{TS}.zip")
        rel = [str(p.relative_to(tmp_path)).replace("\\", "/") for p in locs]
        assert f"adg_run_{TS}.zip" in rel
        assert f"adg_run_{TS}.zip.gz" in rel
        assert f"{ARCHIVE_MONTH_DIR}/adg_run_{TS}.zip" in rel
        assert f"{ARCHIVE_MONTH_DIR}/adg_run_{TS}.zip.gz" in rel

    def test_degraded_timestamp_returns_root_only(self, tmp_path: Path) -> None:
        locs = _artifact_locations(tmp_path, "garbage_ts", "anything.zip")
        # Only root candidates when the timestamp can't be parsed
        assert all(
            "_archive" not in str(p.relative_to(tmp_path))
            for p in locs
        )


class TestArtifactPresent:
    def test_finds_at_root(self, tmp_path: Path) -> None:
        target = tmp_path / f"adg_run_{TS}.zip"
        target.write_bytes(b"PK\x03\x04stub")
        found = _artifact_present(tmp_path, TS, f"adg_run_{TS}.zip")
        assert found == target

    def test_finds_in_archive_month_dir(self, tmp_path: Path) -> None:
        archive_dir = tmp_path / ARCHIVE_MONTH_DIR
        archive_dir.mkdir(parents=True)
        target = archive_dir / f"adg_run_{TS}.zip"
        target.write_bytes(b"PK\x03\x04stub")
        found = _artifact_present(tmp_path, TS, f"adg_run_{TS}.zip")
        assert found == target

    def test_finds_gzipped_in_archive(self, tmp_path: Path) -> None:
        archive_dir = tmp_path / ARCHIVE_MONTH_DIR
        archive_dir.mkdir(parents=True)
        target_gz = archive_dir / f"adg_run_{TS}.zip.gz"
        with gzip.open(target_gz, "wb") as fh:
            fh.write(b"PK\x03\x04stub")
        found = _artifact_present(tmp_path, TS, f"adg_run_{TS}.zip")
        assert found == target_gz

    def test_returns_none_when_truly_missing(self, tmp_path: Path) -> None:
        found = _artifact_present(tmp_path, TS, f"adg_run_{TS}.zip")
        assert found is None


class TestVerifyArtifactsArchiveAware:
    """``_verify_artifacts`` should not record a deferred failure when the
    artifacts only exist in the archive month-dir.
    """

    def _build_full_archive_layout(self, root: Path) -> None:
        """Place all 5 expected artifacts (zip + 4 reports) in the archive
        month-dir as the post-archive pipeline state would.
        """
        archive_dir = root / ARCHIVE_MONTH_DIR
        archive_dir.mkdir(parents=True)
        # Gzipped zip (matches real archive_zip_files behaviour)
        with gzip.open(archive_dir / f"adg_run_{TS}.zip.gz", "wb") as fh:
            fh.write(b"PK\x03\x04stub")
        # Plain JSON reports
        for rname in (
            "layer_coverage_report",
            "edge_density_report",
            "provenance_report",
            "closure_validation_report",
        ):
            (archive_dir / f"{rname}_{TS}.json").write_text(
                json.dumps({"stub": True}), encoding="utf-8"
            )

    def test_no_deferred_failure_when_all_artifacts_archived(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        self._build_full_archive_layout(tmp_path)

        # Reset the deferred registry so this test sees a clean slate.
        from tools.generate.integration import deferred_failures as df_mod

        monkeypatch.setenv("ADG_CONTINUE_ON_GATE_FAILURE", "1")
        df_mod.reset_for_tests()

        _verify_artifacts(tmp_path, TS, no_zip=False, no_reports=False)
        out = capsys.readouterr().out

        assert "missing" not in out.lower(), out
        names = {row["gate_name"] for row in df_mod.deferred_failure_summary()}
        assert "verify_artifacts.zip" not in names
        assert "verify_artifacts.reports" not in names
        # Verifier should announce it found archived artifacts
        assert ".zip.gz" in out or "_archive/2026-04" in out

    def test_records_deferred_failure_when_truly_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Empty tmp_path — no zip, no reports anywhere
        from tools.generate.integration import deferred_failures as df_mod

        monkeypatch.setenv("ADG_CONTINUE_ON_GATE_FAILURE", "1")
        df_mod.reset_for_tests()

        _verify_artifacts(tmp_path, TS, no_zip=False, no_reports=False)
        out = capsys.readouterr().out

        names = {row["gate_name"] for row in df_mod.deferred_failure_summary()}
        assert "verify_artifacts.zip" in names
        assert "verify_artifacts.reports" in names
        assert "Zip archive not found" in out
