"""Tests for P1/P2 of RCA 2026-04-28 — session scratch cleanup, stale
unparseable timestamp purge, and zip-fail breadcrumb integration.

Covers:
    - _cleanup_session_scratch: age-gated deletion of ad-hoc logs/TSVs/etc.
    - _purge_unparseable_buckets: age-gated deletion of sentinels like
      ``adg_indexed_99999999_9999.sqlite``.
    - Public _archive_old_artifacts wires both purges in.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from tools.generate.archiving.archiver import (
    _archive_old_artifacts,
    _cleanup_session_scratch,
    _purge_unparseable_buckets,
)


def _set_mtime_days_ago(path: Path, days: float) -> None:
    """Backdate a file's mtime by ``days`` days."""
    cutoff = time.time() - (days * 86400)
    os.utime(path, (cutoff, cutoff))


@pytest.fixture
def adg_dir(tmp_path: Path, monkeypatch) -> Path:
    """ADG dir with the validation-cleanup hook neutered."""
    d = tmp_path / "adg"
    d.mkdir(parents=True)
    from tools.generate.reporting import analysis as reporting_analysis

    monkeypatch.setattr(reporting_analysis, "_cleanup_validation_files", lambda *_a, **_k: None)
    return d


# ---------------------------------------------------------------------------
# _cleanup_session_scratch — pattern coverage and age gating
# ---------------------------------------------------------------------------


class TestCleanupSessionScratch:
    def test_deletes_ad_hoc_redirect_logs_when_stale(self, adg_dir: Path) -> None:
        stale = adg_dir / "_w1_regen.log"
        stale.write_text("x" * 100, encoding="utf-8")
        _set_mtime_days_ago(stale, days=5)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert not stale.exists()

    def test_deletes_burn_log_pattern(self, adg_dir: Path) -> None:
        stale = adg_dir / "_burn_001.log"
        stale.write_text("burn", encoding="utf-8")
        _set_mtime_days_ago(stale, days=10)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert not stale.exists()

    def test_deletes_wave_queue_tsv(self, adg_dir: Path) -> None:
        stale = adg_dir / "wave_queue_200.tsv"
        stale.write_text("a\tb", encoding="utf-8")
        _set_mtime_days_ago(stale, days=4)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert not stale.exists()

    def test_deletes_tech_debt_review(self, adg_dir: Path) -> None:
        stale = adg_dir / "tech_debt_review_04232026.txt"
        stale.write_text("debt", encoding="utf-8")
        _set_mtime_days_ago(stale, days=10)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert not stale.exists()

    def test_deletes_dead_scan(self, adg_dir: Path) -> None:
        stale = adg_dir / "dead_dup_scan_04232026.txt"
        stale.write_text("scan", encoding="utf-8")
        _set_mtime_days_ago(stale, days=10)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert not stale.exists()

    def test_deletes_stub_archive_candidates(self, adg_dir: Path) -> None:
        stale = adg_dir / "stub_archive_candidates.json"
        stale.write_text("[]", encoding="utf-8")
        _set_mtime_days_ago(stale, days=5)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert not stale.exists()

    def test_deletes_bare_sha256_json_fingerprint(self, adg_dir: Path) -> None:
        sha = "63872ff7dd8423cd99c660d4246398580106b6ad04f398f6ae238fa4fb21b4f0"
        stale = adg_dir / f"{sha}.json"
        stale.write_text("{}", encoding="utf-8")
        _set_mtime_days_ago(stale, days=5)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert not stale.exists()

    def test_keeps_fresh_files(self, adg_dir: Path) -> None:
        """Files within the age window must be preserved (in-flight work)."""
        fresh = adg_dir / "_w1_regen.log"
        fresh.write_text("fresh", encoding="utf-8")
        # mtime is now (just-written) — within 3-day window

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert fresh.exists()

    def test_does_not_touch_generator_outputs(self, adg_dir: Path) -> None:
        """Generator-produced files (adg_*.sqlite, adg_*.json) are out of scope."""
        stale = adg_dir / "adg_indexed_04282026_1722.sqlite"
        stale.write_bytes(b"sqlite")
        _set_mtime_days_ago(stale, days=30)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert stale.exists(), "scratch cleanup must not delete generator outputs"

    def test_does_not_touch_arbitrary_json(self, adg_dir: Path) -> None:
        """A plain non-SHA256 .json file must be left alone (e.g. p1_ratchet.json)."""
        keep = adg_dir / "p1_ratchet.json"
        keep.write_text("{}", encoding="utf-8")
        _set_mtime_days_ago(keep, days=30)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert keep.exists()

    def test_skips_archive_subdir(self, adg_dir: Path) -> None:
        """Files inside artifacts/adg/_archive/ must never be touched."""
        archive = adg_dir / "_archive"
        archive.mkdir()
        nested = archive / "_old.log"
        nested.write_text("old", encoding="utf-8")
        _set_mtime_days_ago(nested, days=30)

        _cleanup_session_scratch(adg_dir, max_age_days=3)

        assert nested.exists()

    def test_handles_missing_dir(self, tmp_path: Path) -> None:
        """No-op when the ADG dir does not exist (idempotent)."""
        _cleanup_session_scratch(tmp_path / "nonexistent", max_age_days=3)

    def test_two_tier_fast_one_hour_default(self, adg_dir: Path) -> None:
        """RCA 2026-04-28 (round 2): default fast tier is 1 HOUR, not days.

        A redirect log produced 2 hours ago by `python ... > _foo.log` is
        clearly stale once the producing command exits — the old 3-day
        default left them accumulating throughout a workday.
        """
        log_2h = adg_dir / "_burn_recent.log"
        log_2h.write_text("x", encoding="utf-8")
        # Backdate to 2 hours ago
        old_time = time.time() - (2 * 3600)
        os.utime(log_2h, (old_time, old_time))

        # Wave queue from same 2h ago — should SURVIVE (slow tier 24h floor)
        wave = adg_dir / "wave_queue_recent.tsv"
        wave.write_text("a\tb", encoding="utf-8")
        os.utime(wave, (old_time, old_time))

        _cleanup_session_scratch(adg_dir)  # use new defaults

        assert not log_2h.exists(), "fast-tier log >1h must be cleaned"
        assert wave.exists(), "slow-tier wave queue <24h must survive"

    def test_two_tier_slow_24h_default(self, adg_dir: Path) -> None:
        """Slow tier (wave queues, triage TXTs) keeps a 24-hour floor."""
        wave_old = adg_dir / "wave_queue_yesterday.tsv"
        wave_old.write_text("a\tb", encoding="utf-8")
        # 25 hours ago — past 24h slow floor
        old_time = time.time() - (25 * 3600)
        os.utime(wave_old, (old_time, old_time))

        _cleanup_session_scratch(adg_dir)

        assert not wave_old.exists(), "slow-tier file >24h must be cleaned"

    def test_err_extension_pattern(self, adg_dir: Path) -> None:
        """`_*.err` (stderr redirect targets) are now in the fast tier."""
        err = adg_dir / "_run.log.err"
        err.write_text("err", encoding="utf-8")
        _set_mtime_days_ago(err, days=1)

        _cleanup_session_scratch(adg_dir)

        assert not err.exists()


# ---------------------------------------------------------------------------
# _purge_unparseable_buckets — sentinel cleanup
# ---------------------------------------------------------------------------


class TestPurgeUnparseableBuckets:
    def test_deletes_stale_sentinel_sqlite(self, adg_dir: Path) -> None:
        sentinel = adg_dir / "adg_indexed_99999999_9999.sqlite"
        sentinel.write_bytes(b"sentinel")
        _set_mtime_days_ago(sentinel, days=30)

        runs = {"99999999_9999": [sentinel]}
        _purge_unparseable_buckets(runs, ["99999999_9999"], max_age_days=7)

        assert not sentinel.exists()

    def test_keeps_fresh_unparseable(self, adg_dir: Path) -> None:
        """A freshly-written file with a bogus timestamp is kept (operator may
        be debugging right now)."""
        sentinel = adg_dir / "adg_indexed_99999999_9999.sqlite"
        sentinel.write_bytes(b"sentinel")
        # mtime = now

        runs = {"99999999_9999": [sentinel]}
        _purge_unparseable_buckets(runs, ["99999999_9999"], max_age_days=7)

        assert sentinel.exists()

    def test_no_op_when_no_unparseable(self, adg_dir: Path) -> None:
        sentinel = adg_dir / "adg_indexed_04282026_1722.sqlite"
        sentinel.write_bytes(b"valid")

        runs = {"04282026_1722": [sentinel]}
        _purge_unparseable_buckets(runs, [], max_age_days=7)

        assert sentinel.exists()


# ---------------------------------------------------------------------------
# _archive_old_artifacts — end-to-end wiring
# ---------------------------------------------------------------------------


class TestArchiveOldArtifactsIntegration:
    def test_session_scratch_cleaned_during_archive(self, adg_dir: Path) -> None:
        """Stale scratch files are deleted as part of _archive_old_artifacts."""
        # Two recognized runs so retention triggers (>keep_runs)
        (adg_dir / "adg_indexed_04282026_1722.sqlite").write_bytes(b"current")
        old_run = adg_dir / "adg_indexed_04272026_1500.sqlite"
        old_run.write_bytes(b"old")
        # zip for old run, so the run appears as zipped (avoids orphan path)
        (adg_dir / "adg_run_04272026_1500.zip").write_bytes(b"zip")

        # Stale scratch
        stale_log = adg_dir / "_w1_regen.log"
        stale_log.write_text("x", encoding="utf-8")
        _set_mtime_days_ago(stale_log, days=10)

        # Fresh scratch (must survive)
        fresh_log = adg_dir / "_burn_now.log"
        fresh_log.write_text("y", encoding="utf-8")

        _archive_old_artifacts(adg_dir=adg_dir, current_ts="04282026_1722", keep_runs=1)

        assert not stale_log.exists(), "stale scratch must be cleaned"
        assert fresh_log.exists(), "fresh scratch must survive"

    def test_stale_sentinel_purged_during_archive(self, adg_dir: Path) -> None:
        """Sentinel adg_indexed_99999999_9999.sqlite is purged when stale."""
        (adg_dir / "adg_indexed_04282026_1722.sqlite").write_bytes(b"current")
        sentinel = adg_dir / "adg_indexed_99999999_9999.sqlite"
        sentinel.write_bytes(b"sentinel")
        _set_mtime_days_ago(sentinel, days=30)

        _archive_old_artifacts(adg_dir=adg_dir, current_ts="04282026_1722", keep_runs=1)

        assert not sentinel.exists()

    def test_current_run_protected_from_tz_skew(self, adg_dir: Path) -> None:
        """RCA 2026-04-28: current run must never be archived even when a
        sub-builder UTC timestamp ranks numerically higher than the main
        run's local timestamp.

        Scenario: main run is 04282026_1801 (local 18:01). A sub-builder
        gate-results file uses YYYYMMDD_HHMMSS in UTC (21:53:38 = local
        17:53:38). Naive comparison would put 215338 > 180100, archiving
        the current run by mistake.
        """
        current_ts = "04282026_1801"
        # current run's primary artifact + zip
        current_sqlite = adg_dir / f"adg_indexed_{current_ts}.sqlite"
        current_sqlite.write_bytes(b"current_sqlite")
        current_zip = adg_dir / f"adg_run_{current_ts}.zip"
        current_zip.write_bytes(b"current_zip")
        current_snap = adg_dir / f"adg_snapshot_{current_ts}.json"
        current_snap.write_text("{}", encoding="utf-8")

        # sub-builder gate_results in UTC, naive-ranks higher than main_local
        sub_builder = adg_dir / "adg_gate_results_20260428_215338.json"
        sub_builder.write_text("{}", encoding="utf-8")

        # genuinely older run that SHOULD be archived
        older_run = adg_dir / "adg_indexed_04272026_1500.sqlite"
        older_run.write_bytes(b"older")
        older_zip = adg_dir / "adg_run_04272026_1500.zip"
        older_zip.write_bytes(b"older_zip")

        _archive_old_artifacts(adg_dir=adg_dir, current_ts=current_ts, keep_runs=1)

        assert current_sqlite.exists(), "current run sqlite must NOT be archived"
        assert current_zip.exists(), "current run zip must NOT be archived"
        assert current_snap.exists(), "current run snapshot must NOT be archived"
        # older run should be gone (archived/deleted)
        assert not older_run.exists(), "older run sqlite must be archived/removed"
        assert not older_zip.exists(), "older run zip must be archived/removed"

    def test_archive_skipped_breadcrumb_pattern_recognized(self, adg_dir: Path) -> None:
        """archive_skipped_<ts>.txt is in the whitelist so it gets archived
        with the rest of an old run rather than accumulating."""
        # Two runs — old one will be archived
        (adg_dir / "adg_indexed_04282026_1722.sqlite").write_bytes(b"current")
        old_breadcrumb = adg_dir / "archive_skipped_04272026_1500.txt"
        old_breadcrumb.write_text("breadcrumb", encoding="utf-8")
        (adg_dir / "adg_run_04272026_1500.zip").write_bytes(b"zip")

        _archive_old_artifacts(adg_dir=adg_dir, current_ts="04282026_1722", keep_runs=1)

        # Old breadcrumb should be gone (consumed during retention)
        assert not old_breadcrumb.exists()
