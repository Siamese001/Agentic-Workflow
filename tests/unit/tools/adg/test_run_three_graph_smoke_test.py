"""Tests for tools/adg/run_three_graph_smoke_test.py.

Covers W1.future of plan three-bucket-gap-remediation-069806 — the
unified three-graph test runner that exercises all three buckets,
classifies the gap distribution, and asserts threshold checks.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.run_three_graph_smoke_test import (  # noqa: E402
    GapDistribution,
    GraphCounts,
    probe_counts,
    probe_gap_distribution,
    run,
    run_checks,
    write_report_json,
)


# ---------------------------------------------------------------------------
# Fixture — synthetic snapshot with all three buckets populated
# ---------------------------------------------------------------------------


def _build_synthetic_snapshot(
    path: Path,
    *,
    add_runtime_view: bool = True,
    add_triplet: bool = True,
    add_shadow: bool = False,
    add_config_bloat: bool = False,
) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT,
            authority TEXT NOT NULL,
            bucket TEXT NOT NULL,
            resolution_status TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            evidence_refs TEXT
        );
        """
    )
    # 5 nodes
    for adg_name in ("ADG::A", "ADG::B", "ADG::C", "ADG::D", "ADG::E"):
        con.execute("INSERT INTO nodes (adg_name) VALUES (?)", (adg_name,))

    # Triplet pair: (1->2 imports) in both static AND registry, plus runtime
    if add_triplet:
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, authority, "
            "bucket, resolution_status, authority_status) "
            "VALUES (1, 2, 'imports', 'static_canonical', 'static', 'V', 'A')"
        )
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, authority, "
            "bucket, resolution_status, authority_status) "
            "VALUES (1, 2, 'imports', 'registry_declared', 'registry', 'S', 'AR')"
        )

    # REGISTRY_DRIFT: static + runtime, no registry — (3->4 calls)
    con.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, authority, "
        "bucket, resolution_status, authority_status) "
        "VALUES (3, 4, 'calls', 'verified', 'static', 'V', 'A')"
    )

    # CONFIG_BLOAT: registry only — (5->1 declared)
    if add_config_bloat:
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, authority, "
            "bucket, resolution_status, authority_status) "
            "VALUES (5, 1, 'declared', 'registry_declared', 'registry', 'S', 'AR')"
        )

    if add_runtime_view:
        con.execute(
            """
            CREATE TABLE v_runtime_proof (
                static_edge_id INTEGER,
                src_name TEXT,
                dst_name TEXT,
                relation_type TEXT,
                attesting_trace_count INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        if add_triplet:
            # Find the static (1->2 imports) edge id
            row = con.execute(
                "SELECT id FROM edges WHERE bucket='static' AND src_id=1 AND dst_id=2"
            ).fetchone()
            if row:
                con.execute(
                    "INSERT INTO v_runtime_proof (static_edge_id, src_name, "
                    "dst_name, relation_type, attesting_trace_count) "
                    "VALUES (?, 'ADG::A', 'ADG::B', 'imports', 5)",
                    (row[0],),
                )
        # Drift runtime row
        row = con.execute(
            "SELECT id FROM edges WHERE bucket='static' AND src_id=3 AND dst_id=4"
        ).fetchone()
        if row:
            con.execute(
                "INSERT INTO v_runtime_proof (static_edge_id, src_name, "
                "dst_name, relation_type, attesting_trace_count) "
                "VALUES (?, 'ADG::C', 'ADG::D', 'calls', 2)",
                (row[0],),
            )
        if add_shadow:
            # SHADOW_CHANNEL: runtime-only edge — present in `edges` with
            # bucket='runtime' (so in_static=0, in_registry=0 for that
            # tuple group), and a matching v_runtime_proof row pointing
            # at it. Mirrors how a real runtime-only edge would land in
            # the static snapshot during runtime ingest.
            con.execute(
                "INSERT INTO edges (src_id, dst_id, relation_type, authority, "
                "bucket, resolution_status, authority_status) "
                "VALUES (4, 5, 'monkey_patch', 'runtime_observed', 'runtime', "
                "'VERIFIED_RUNTIME', 'AUTHORITATIVE_RUNTIME')"
            )
            row = con.execute(
                "SELECT id FROM edges WHERE bucket='runtime' AND src_id=4 "
                "AND dst_id=5 AND relation_type='monkey_patch'"
            ).fetchone()
            con.execute(
                "INSERT INTO v_runtime_proof (static_edge_id, src_name, "
                "dst_name, relation_type, attesting_trace_count) "
                "VALUES (?, 'ADG::D', 'ADG::E', 'monkey_patch', 3)",
                (row[0],),
            )

    con.commit()
    con.close()


@pytest.fixture
def healthy_snapshot(tmp_path: Path) -> Path:
    snap = tmp_path / "snap.sqlite"
    _build_synthetic_snapshot(snap)
    return snap


@pytest.fixture
def shadow_snapshot(tmp_path: Path) -> Path:
    snap = tmp_path / "snap_shadow.sqlite"
    _build_synthetic_snapshot(snap, add_shadow=True)
    return snap


# ---------------------------------------------------------------------------
# Probe phases
# ---------------------------------------------------------------------------


class TestProbeCounts:
    def test_counts_static_registry_runtime(self, healthy_snapshot: Path):
        con = sqlite3.connect(healthy_snapshot)
        try:
            counts = probe_counts(con)
        finally:
            con.close()
        assert counts.static_edges == 2  # (1->2 imports), (3->4 calls)
        assert counts.registry_edges == 1  # (1->2 imports)
        assert counts.runtime_attested_rows == 2  # triplet + drift

    def test_runtime_zero_when_view_missing(self, tmp_path: Path):
        snap = tmp_path / "no_view.sqlite"
        _build_synthetic_snapshot(snap, add_runtime_view=False)
        con = sqlite3.connect(snap)
        try:
            counts = probe_counts(con)
        finally:
            con.close()
        assert counts.runtime_attested_rows == 0


class TestProbeGapDistribution:
    def test_classifies_triplet_and_drift(self, healthy_snapshot: Path):
        con = sqlite3.connect(healthy_snapshot)
        try:
            gap = probe_gap_distribution(con)
        finally:
            con.close()
        assert gap.triplet_attested == 1  # (1->2 imports)
        assert gap.registry_drift == 1  # (3->4 calls)
        assert gap.shadow_channel == 0
        assert gap.dead_path == 0

    def test_detects_shadow_channel(self, shadow_snapshot: Path):
        con = sqlite3.connect(shadow_snapshot)
        try:
            gap = probe_gap_distribution(con)
        finally:
            con.close()
        assert gap.shadow_channel >= 1


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------


class TestRunChecks:
    def test_all_pass_on_healthy(self):
        counts = GraphCounts(static_edges=100, registry_edges=10, runtime_attested_rows=50)
        gap = GapDistribution(
            triplet_attested=20, registry_drift=5, dead_path=0,
            unobserved_code=70, dynamic_dispatch=0, shadow_channel=0,
            config_bloat=1, total=96,
        )
        results = run_checks(
            counts, gap,
            triplet_floor=10, drift_pct_ceiling=10.0, bloat_pct_ceiling=2.0,
        )
        assert all(c.passed for c in results)

    def test_fails_when_shadow_channel_present(self):
        counts = GraphCounts(static_edges=100, registry_edges=10, runtime_attested_rows=50)
        gap = GapDistribution(
            triplet_attested=20, registry_drift=5, shadow_channel=1, total=100,
        )
        results = run_checks(
            counts, gap,
            triplet_floor=10, drift_pct_ceiling=10.0, bloat_pct_ceiling=2.0,
        )
        shadow = [c for c in results if c.name == "shadow_channel_zero"][0]
        assert not shadow.passed

    def test_fails_when_triplet_below_floor(self):
        counts = GraphCounts(static_edges=100, registry_edges=10, runtime_attested_rows=50)
        gap = GapDistribution(triplet_attested=5, total=100)
        results = run_checks(
            counts, gap,
            triplet_floor=10, drift_pct_ceiling=10.0, bloat_pct_ceiling=2.0,
        )
        triplet = [c for c in results if c.name == "triplet_floor"][0]
        assert not triplet.passed

    def test_fails_when_drift_pct_above_ceiling(self):
        counts = GraphCounts(static_edges=100, registry_edges=10, runtime_attested_rows=50)
        gap = GapDistribution(
            triplet_attested=10, registry_drift=20, total=100,
        )
        results = run_checks(
            counts, gap,
            triplet_floor=1, drift_pct_ceiling=10.0, bloat_pct_ceiling=2.0,
        )
        drift = [c for c in results if c.name == "registry_drift_pct_ceiling"][0]
        assert not drift.passed

    def test_fails_when_each_graph_empty(self):
        counts = GraphCounts(static_edges=0, registry_edges=0, runtime_attested_rows=0)
        gap = GapDistribution(total=0)
        results = run_checks(
            counts, gap,
            triplet_floor=1, drift_pct_ceiling=10.0, bloat_pct_ceiling=2.0,
        )
        non_empty = {c.name: c.passed for c in results}
        assert not non_empty["static_graph_non_empty"]
        assert not non_empty["registry_graph_non_empty"]
        assert not non_empty["runtime_graph_non_empty"]


# ---------------------------------------------------------------------------
# End-to-end run() with custom snapshot
# ---------------------------------------------------------------------------


class TestRunEndToEnd:
    def test_returns_passing_report_on_healthy_snapshot(
        self, healthy_snapshot: Path, tmp_path: Path
    ):
        report_out = tmp_path / "report.json"
        report = run(
            snapshot=healthy_snapshot,
            triplet_floor=1,
            drift_pct_ceiling=50.0,  # only 1 drift edge in 3-edge fixture
            bloat_pct_ceiling=50.0,
            report_path=report_out,
        )
        assert report.all_passed()
        assert report.gap.triplet_attested == 1
        assert report.snapshot == healthy_snapshot.name
        assert report_out.exists()
        data = json.loads(report_out.read_text(encoding="utf-8"))
        assert data["overall_passed"] is True

    def test_returns_failing_report_when_shadow_channel(
        self, shadow_snapshot: Path
    ):
        report = run(
            snapshot=shadow_snapshot,
            triplet_floor=1,
            drift_pct_ceiling=99.0,
            bloat_pct_ceiling=99.0,
        )
        assert not report.all_passed()
        # The specific failing check should be shadow_channel_zero
        failing = [c.name for c in report.checks if not c.passed]
        assert "shadow_channel_zero" in failing

    def test_returns_failing_report_when_no_snapshot(self, tmp_path: Path):
        nonexistent = tmp_path / "missing.sqlite"
        report = run(snapshot=nonexistent)
        assert not report.all_passed()
        assert any(c.name == "snapshot_exists" for c in report.checks)


# ---------------------------------------------------------------------------
# JSON report writer
# ---------------------------------------------------------------------------


class TestWriteReportJson:
    def test_writes_valid_json_with_required_keys(
        self, healthy_snapshot: Path, tmp_path: Path
    ):
        from tools.adg.run_three_graph_smoke_test import SmokeTestReport, CheckResult

        report = SmokeTestReport(
            snapshot="test.sqlite",
            counts=GraphCounts(static_edges=10, registry_edges=2, runtime_attested_rows=5),
            gap=GapDistribution(triplet_attested=2, total=10),
            checks=[CheckResult(name="x", passed=True, detail="ok")],
            timestamp_utc="2026-04-29T22:00:00+00:00",
        )
        path = tmp_path / "subdir" / "report.json"
        write_report_json(report, path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "snapshot" in data
        assert "counts" in data
        assert "gap_distribution" in data
        assert "checks" in data
        assert data["overall_passed"] is True
