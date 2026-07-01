from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tools.generate.archiving.archiver import (
    _archive_old_artifacts,
    _extract_timestamp,
    _parse_timestamp,
)


def test_extract_timestamp_supports_graphdb_workdir_name() -> None:
    assert _extract_timestamp("graphdb_04202026_1510") == "04202026_1510"


def test_extract_timestamp_mmddyyyy_hhmm_main_generator() -> None:
    """Main generator format: MMDDYYYY_HHMM (8+4 digits, month-leading)."""
    assert _extract_timestamp("adg_indexed_04232026_1418.sqlite") == "04232026_1418"
    assert _extract_timestamp("adg_snapshot_04232026_1418.json") == "04232026_1418"
    assert _extract_timestamp("adg_graphdb_index_04222026_1218.json") == "04222026_1218"


def test_extract_timestamp_yyyymmdd_hhmmss_sub_builders() -> None:
    """Sub-builder format: YYYYMMDD_HHMMSS (8+6 digits, year-leading).

    Regression guard: this format was unrecognized prior to the fix,
    causing watchlist/anomaly/gate artifacts to accumulate forever.
    """
    assert _extract_timestamp("adg_anomaly_watchlist_20260418_155948.json") == "20260418_155948"
    assert _extract_timestamp("adg_graph_watchlist_20260423_155151.json") == "20260423_155151"
    assert _extract_timestamp("adg_gate_results_20260423_152323.json") == "20260423_152323"


def test_parse_timestamp_yyyymmdd_hhmmss() -> None:
    """Parse year-leading 8+6 timestamp to a correct datetime."""
    assert _parse_timestamp("20260423_155151") == datetime(2026, 4, 23, 15, 51, 51)


def test_parse_timestamp_mmddyyyy_hhmm_still_works() -> None:
    """Main-generator format continues to parse after the new branch lands."""
    assert _parse_timestamp("04232026_1418") == datetime(2026, 4, 23, 14, 18, 0)


def test_archive_old_artifacts_removes_yyyymmdd_hhmmss_files(tmp_path: Path, monkeypatch) -> None:
    """YYYYMMDD_HHMMSS artifacts are purged along with other old runs (regression)."""
    adg_dir = tmp_path / "adg"
    adg_dir.mkdir(parents=True)

    current_ts = "04232026_1800"
    old_ts_iso = "20260418_155948"

    (adg_dir / f"adg_indexed_{current_ts}.sqlite").write_text("current", encoding="utf-8")
    old_anomaly = adg_dir / f"adg_anomaly_watchlist_{old_ts_iso}.json"
    old_anomaly.write_text("{}", encoding="utf-8")
    old_graph = adg_dir / f"adg_graph_watchlist_{old_ts_iso}.json"
    old_graph.write_text("{}", encoding="utf-8")
    old_gate = adg_dir / f"adg_gate_results_{old_ts_iso}.json"
    old_gate.write_text("{}", encoding="utf-8")

    from tools.generate.reporting import analysis as reporting_analysis

    monkeypatch.setattr(reporting_analysis, "_cleanup_validation_files", lambda *_a, **_k: None)

    _archive_old_artifacts(adg_dir=adg_dir, current_ts=current_ts, keep_runs=1)

    archive_dir = adg_dir / "_archive" / "2026-04"
    assert not old_anomaly.exists(), "old anomaly watchlist should leave artifacts/adg root"
    assert not old_graph.exists(), "old graph watchlist should leave artifacts/adg root"
    assert not old_gate.exists(), "old gate results should leave artifacts/adg root"
    assert (archive_dir / f"{old_gate.name}.gz").is_file(), "gate results archived under _archive"
    assert (adg_dir / f"adg_indexed_{current_ts}.sqlite").exists(), "current run must survive"


def test_archive_orphan_run_without_zip_moves_to_archive(tmp_path: Path, monkeypatch) -> None:
    """Runs without adg_run_<ts>.zip gzip loose files under _archive (not delete)."""
    adg_dir = tmp_path / "adg"
    adg_dir.mkdir(parents=True)
    current_ts = "04202026_1530"
    old_ts = "04202026_1510"
    (adg_dir / f"adg_indexed_{current_ts}.sqlite").write_text("current", encoding="utf-8")
    old_sqlite = adg_dir / f"adg_indexed_{old_ts}.sqlite"
    old_sqlite.write_text("old", encoding="utf-8")

    from tools.generate.reporting import analysis as reporting_analysis

    monkeypatch.setattr(reporting_analysis, "_cleanup_validation_files", lambda *_a, **_k: None)

    _archive_old_artifacts(adg_dir=adg_dir, current_ts=current_ts, keep_runs=1)

    archive_dir = adg_dir / "_archive" / "2026-04"
    assert not old_sqlite.exists()
    assert (archive_dir / f"{old_sqlite.name}.gz").is_file()


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

    archive_dir = adg_dir / "_archive" / "2026-04"
    assert not old_workdir.exists(), "old graphdb workdir should leave artifacts/adg root"
    assert (archive_dir / old_workdir.name).is_dir(), "graphdb workdir moved under _archive"
    assert current_workdir.exists()


def test_archive_old_artifacts_archives_markdown_yaml_and_intoto_sidecars(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Non-JSON ADG sidecars must not accumulate in artifacts/adg root."""
    adg_dir = tmp_path / "adg"
    adg_dir.mkdir(parents=True)
    current_ts = "07012026_0354"
    old_ts = "06292026_0701"

    (adg_dir / f"adg_indexed_{current_ts}.sqlite").write_text("current", encoding="utf-8")
    old_md = adg_dir / f"adg_bcg_executive_summary_{old_ts}.md"
    old_yaml = adg_dir / f"adg_bcg_executive_summary_{old_ts}.yaml"
    old_intoto = adg_dir / f"adg_indexed_{old_ts}.sqlite.intoto.jsonl"
    for path in (old_md, old_yaml, old_intoto):
        path.write_text("old", encoding="utf-8")

    from tools.generate.reporting import analysis as reporting_analysis

    monkeypatch.setattr(reporting_analysis, "_cleanup_validation_files", lambda *_a, **_k: None)

    _archive_old_artifacts(adg_dir=adg_dir, current_ts=current_ts, keep_runs=1)

    archive_dir = adg_dir / "_archive" / "2026-06"
    for path in (old_md, old_yaml, old_intoto):
        assert not path.exists()
        assert (archive_dir / f"{path.name}.gz").is_file()
    assert (adg_dir / f"adg_indexed_{current_ts}.sqlite").exists()


def test_archive_old_artifacts_groups_current_utc_helpers_by_sqlite_metadata(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Multiple UTC helper buckets for the current run must stay protected."""
    adg_dir = tmp_path / "adg"
    adg_dir.mkdir(parents=True)
    current_ts = "07012026_0354"
    old_ts = "06292026_0701"

    current_sqlite = adg_dir / f"adg_indexed_{current_ts}.sqlite"
    current_sqlite.write_text("current", encoding="utf-8")
    (adg_dir / f"adg_indexed_{old_ts}.sqlite").write_text("old", encoding="utf-8")
    helper_one = adg_dir / "adg_gate_results_20260701_080018.json"
    helper_one.write_text(
        f'{{"snapshot_path": "{current_sqlite.as_posix()}"}}',
        encoding="utf-8",
    )
    helper_two = adg_dir / "adg_graph_watchlist_20260701_040041.json"
    helper_two.write_text(
        f'{{"sqlite_source": "adg_indexed_{current_ts}.sqlite"}}',
        encoding="utf-8",
    )

    from tools.generate.reporting import analysis as reporting_analysis

    monkeypatch.setattr(reporting_analysis, "_cleanup_validation_files", lambda *_a, **_k: None)

    _archive_old_artifacts(adg_dir=adg_dir, current_ts=current_ts, keep_runs=1)

    assert helper_one.exists()
    assert helper_two.exists()
    assert current_sqlite.exists()
    assert not (adg_dir / f"adg_indexed_{old_ts}.sqlite").exists()
