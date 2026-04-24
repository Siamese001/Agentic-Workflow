"""Gap 1: canonical runs MUST have a real adg_indexed_*.sqlite file.

Regression test for the 2026-04-23 incident where a JSON-only timestamp
outranked a real SQLite-backed run and got it archived.
"""

from __future__ import annotations

from pathlib import Path

from tools.archive.archive_old_adg import _has_sqlite, identify_runs_to_archive


def _mk(ts: str, *names: str) -> list[Path]:
    return [Path(f"artifacts/adg/{n.format(ts=ts)}") for n in names]


class TestHasSqlite:
    def test_returns_true_only_for_indexed_sqlite(self) -> None:
        assert _has_sqlite(_mk("01012026", "adg_indexed_{ts}.sqlite")) is True

    def test_returns_false_for_json_only(self) -> None:
        assert _has_sqlite(_mk("01012026", "adg_snapshot_{ts}.json")) is False

    def test_returns_false_for_repair_only(self) -> None:
        assert _has_sqlite(_mk("01012026", "adg_repair_{ts}_0951.json")) is False

    def test_returns_false_for_non_indexed_sqlite(self) -> None:
        """A random .sqlite file that isn't `adg_indexed_*` must not count."""
        assert _has_sqlite([Path("artifacts/adg/some_other.sqlite")]) is False


class TestIdentifyRunsToArchive:
    def test_stranded_run_always_archived_regardless_of_recency(self) -> None:
        """A JSON-only 'run' from today must still get archived."""
        runs = {
            "04232026": _mk("04232026", "adg_snapshot_{ts}.json"),  # stranded
            "04222026": _mk("04222026", "adg_indexed_{ts}.sqlite"),  # canonical
            "04212026": _mk("04212026", "adg_indexed_{ts}.sqlite"),  # canonical
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=5)
        assert "04232026" in to_archive, (
            "stranded JSON-only run MUST be archived even though keep_runs=5 and only 2 canonical exist"
        )
        # The canonical ones MUST NOT be archived (within keep quota).
        assert "04222026" not in to_archive
        assert "04212026" not in to_archive

    def test_canonical_runs_respect_keep_n(self) -> None:
        runs = {
            f"{i:02d}012026": _mk(f"{i:02d}012026", "adg_indexed_{ts}.sqlite")
            for i in range(1, 8)  # 7 canonical runs, months 01..07
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=3)
        # Keep the 3 newest, archive the other 4.
        assert len(to_archive) == 4

    def test_stranded_runs_not_counted_toward_keep_quota(self) -> None:
        """Regression: the bug was that stranded runs ate keep-N slots."""
        runs = {
            "04232026": _mk("04232026", "adg_snapshot_{ts}.json"),  # stranded
            "04222026": _mk("04222026", "adg_snapshot_{ts}.json"),  # stranded
            "04212026": _mk("04212026", "adg_indexed_{ts}.sqlite"),  # canonical
            "04202026": _mk("04202026", "adg_indexed_{ts}.sqlite"),  # canonical
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=2)
        # Both canonical runs fit in keep_runs=2 — they must survive.
        assert "04212026" not in to_archive
        assert "04202026" not in to_archive
        # Both stranded runs must be archived.
        assert "04232026" in to_archive
        assert "04222026" in to_archive

    def test_regression_2026_04_23_incident(self) -> None:
        """Exact reproduction of the bug that motivated Gap 1.

        Before fix: stranded newer JSON timestamp outranked a real sqlite
        run that was the only surviving canonical backup, and got it
        archived.
        """
        runs = {
            # Newer stranded run (e.g. from a crashed generator)
            "04232026": _mk("04232026", "adg_snapshot_{ts}.json"),
            # The only real, usable adg snapshot
            "04222026_1133": _mk("04222026_1133", "adg_indexed_{ts}.sqlite"),
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=1)
        # The sqlite-backed run MUST survive.
        assert "04222026_1133" not in to_archive
        # The stranded run MUST be archived.
        assert "04232026" in to_archive
