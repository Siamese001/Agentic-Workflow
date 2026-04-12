"""Tests for ADG watchlist builder (Prompt 4).

Validates:
1. Watchlist is non-empty when signals exist
2. Ranking is stable
3. Terminal output is bounded
4. SC-1 linked hotspots appear
"""

from pathlib import Path

import pytest

from tools.generate.adg_watchlist_builder import (
    ADGWatchlistBuilder,
    WatchlistItem,
    build_and_emit_watchlist,
)


def get_latest_adg_sqlite() -> Path:
    """Find the latest ADG SQLite snapshot."""
    adg_dir = Path("artifacts/adg")
    sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    if not sqlite_files:
        pytest.skip("No ADG SQLite found")
    return sqlite_files[-1]


class TestWatchlistGeneration:
    """Validate watchlist generation produces high-signal output."""

    def test_watchlist_not_empty(self):
        """Watchlist should have items when hotspots/violations exist."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            watchlist = builder.build_watchlist()

        assert len(watchlist) > 0, "Expected non-empty watchlist with current data"

    def test_top_item_has_high_fan_in_or_violation(self):
        """Top ranked item should have either high fan-in or violations."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            watchlist = builder.build_watchlist()

        if not watchlist:
            pytest.skip("Empty watchlist")

        top = watchlist[0]
        assert top.rank == 1
        # Should have either high fan-in, cone risk, or violations
        assert top.fan_in > 100 or top.cone_risk > 50 or top.sc1_violation or top.sc5_violation, (
            f"Top item should have high signal: {top}"
        )

    def test_sc1_violations_appear_in_watchlist(self):
        """Files with SC-1 violations should appear in watchlist."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            sc1_files = builder._get_sc1_violations()
            watchlist = builder.build_watchlist()

        if not sc1_files:
            pytest.skip("No SC-1 violations in current snapshot")

        # At least some SC-1 files should be in watchlist
        watchlist_files = {item.file for item in watchlist}
        sc1_in_watchlist = sc1_files & watchlist_files

        assert len(sc1_in_watchlist) > 0, "Expected SC-1 violations in watchlist"

    def test_multi_signal_hotspots_ranked_higher(self):
        """Items with multiple signals (fan-in + SC-1) should rank higher."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            watchlist = builder.build_watchlist()

        # Find items with multiple signals
        multi_signal = [item for item in watchlist if item.fan_in > 100 and item.sc1_violation]

        if not multi_signal:
            pytest.skip("No multi-signal items in current data")

        # Multi-signal items should be in top half of watchlist
        multi_signal_ranks = [item.rank for item in multi_signal]
        avg_rank = sum(multi_signal_ranks) / len(multi_signal_ranks)
        median_rank = len(watchlist) / 2

        assert avg_rank <= median_rank, (
            f"Multi-signal items should rank higher (avg {avg_rank} vs median {median_rank})"
        )

    def test_ranks_are_sequential(self):
        """Ranks should be 1, 2, 3, ... without gaps."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            watchlist = builder.build_watchlist()

        if not watchlist:
            pytest.skip("Empty watchlist")

        expected_ranks = list(range(1, len(watchlist) + 1))
        actual_ranks = [item.rank for item in watchlist]

        assert actual_ranks == expected_ranks, "Ranks should be sequential from 1"

    def test_scores_descending(self):
        """Scores should be in descending order."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            watchlist = builder.build_watchlist()

        if len(watchlist) < 2:
            pytest.skip("Need at least 2 items")

        scores = [item.score for item in watchlist]
        assert scores == sorted(scores, reverse=True), "Scores should be descending"


class TestWatchlistArtifact:
    """Validate watchlist artifact emission."""

    def test_artifact_created(self, tmp_path):
        """Watchlist artifact should be created."""
        sqlite_path = get_latest_adg_sqlite()
        output_dir = tmp_path / "test_output"
        output_dir.mkdir()

        artifact_path = build_and_emit_watchlist(sqlite_path, output_dir, print_summary=False)

        assert artifact_path.exists(), "Artifact should exist"
        assert artifact_path.suffix == ".json"
        assert "adg_anomaly_watchlist_" in artifact_path.name

    def test_artifact_contains_required_fields(self, tmp_path):
        """Artifact should have timestamp, source, thresholds, watchlist."""
        import json

        sqlite_path = get_latest_adg_sqlite()
        output_dir = tmp_path / "test_output"
        output_dir.mkdir()

        artifact_path = build_and_emit_watchlist(sqlite_path, output_dir, print_summary=False)

        with open(artifact_path) as f:
            data = json.load(f)

        assert "timestamp" in data
        assert "sqlite_source" in data
        assert "total_items" in data
        assert "thresholds" in data
        assert "watchlist" in data

        thresholds = data["thresholds"]
        assert "fan_in_percentile" in thresholds
        assert "cone_risk_percentile" in thresholds


class TestTerminalSummary:
    """Validate terminal summary is bounded and informative."""

    def test_summary_bounded_to_top_n(self):
        """Summary should only show top N items (default 10)."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            watchlist = builder.build_watchlist()
            summary = builder.emit_terminal_summary(watchlist, top_n=10)

        # Count lines that look like watchlist items (start with rank number)
        lines = summary.split("\n")
        item_lines = [line for line in lines if line.strip() and line.split()[0].isdigit()]

        # Should have at most 10 items shown
        assert len(item_lines) <= 10, f"Summary should show max 10 items, got {len(item_lines)}"

    def test_summary_has_header_and_footer(self):
        """Summary should have clear header and footer."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            watchlist = builder.build_watchlist()
            summary = builder.emit_terminal_summary(watchlist)

        assert "WATCHLIST" in summary.upper()
        assert "Signals:" in summary
        assert "Multi-signal" in summary


class TestAnomalyClassification:
    """Validate anomaly type classification."""

    def test_high_fan_in_classification(self):
        """High fan-in items should be classified correctly."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            watchlist = builder.build_watchlist()

        # Find hotspot_fan_in items
        hotspot_items = [item for item in watchlist if "hotspot_fan_in" == item.anomaly_type]

        for item in hotspot_items:
            assert item.fan_in > 50, "hotspot_fan_in should have meaningful fan-in"

    def test_multi_signal_classification(self):
        """Items with multiple signals should be multi_signal_hotspot."""
        sqlite_path = get_latest_adg_sqlite()

        with ADGWatchlistBuilder(sqlite_path) as builder:
            # Get thresholds from builder
            fi_threshold = int(
                builder._get_percentile_threshold(
                    "mv_hotspot_centrality", "fan_in", builder.FAN_IN_PERCENTILE
                )
            )
            cone_threshold = builder._get_percentile_threshold(
                "mv_dependency_cone_risk", "cone_risk_score", builder.CONE_RISK_PERCENTILE
            )
            watchlist = builder.build_watchlist()

        multi_signal = [item for item in watchlist if item.anomaly_type == "multi_signal_hotspot"]

        if not multi_signal:
            pytest.skip("No multi_signal_hotspot items in current data")

        for item in multi_signal:
            # Use same thresholds as builder
            signals = sum(
                [
                    item.fan_in >= fi_threshold,
                    item.cone_risk >= cone_threshold,
                    item.sc1_violation,
                    item.sc5_violation,
                ]
            )
            assert signals >= 2, (
                f"multi_signal_hotspot should have >=2 signals, got {signals} for {item.file}"
            )
