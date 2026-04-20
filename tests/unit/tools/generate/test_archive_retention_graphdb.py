from __future__ import annotations

from pathlib import Path

from tools.generate.archiving.archiver import _archive_old_artifacts, _extract_timestamp


def test_extract_timestamp_supports_graphdb_workdir_name() -> None:
    assert _extract_timestamp("graphdb_04202026_1510") == "04202026_1510"


def test_archive_old_artifacts_removes_old_graphdb_workdir(tmp_path: Path, monkeypatch) -> None:
    adg_dir = tmp_path / "adg"
    adg_dir.mkdir(parents=True)

    current_ts = "04202026_1530"
    old_ts = "04202026_1510"

    old_workdir = adg_dir / f"graphdb_{old_ts}"
    old_workdir.mkdir(parents=True)
    (old_workdir / "index.json").write_text("{}", encoding="utf-8")

    current_workdir = adg_dir / f"graphdb_{current_ts}"
    current_workdir.mkdir(parents=True)
    (current_workdir / "index.json").write_text("{}", encoding="utf-8")

    from tools.generate.reporting import analysis as reporting_analysis

    monkeypatch.setattr(reporting_analysis, "_cleanup_validation_files", lambda *_args, **_kwargs: None)

    _archive_old_artifacts(adg_dir=adg_dir, current_ts=current_ts, keep_runs=1)

    assert not old_workdir.exists()
    assert current_workdir.exists()
