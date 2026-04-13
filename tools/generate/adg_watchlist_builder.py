#!/usr/bin/env python3
"""Bounded ADG anomaly watchlist builder - Prompt 4.

Builds a high-signal watchlist from:
- mv_hotspot_centrality (fan-in)
- mv_dependency_cone_risk (cone risk)
- SC-1 (gravity violations)
- SC-5 (spine gaps)

Emits compact JSON artifact and terminal summary.
Stays non-blocking - for intelligence only.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from tqdm import tqdm


_ALLOWED_PERCENTILE_TABLES = frozenset({"mv_hotspot_centrality", "mv_dependency_cone_risk"})
_ALLOWED_PERCENTILE_COLUMNS = frozenset({"fan_in", "cone_risk_score"})


@dataclass
class WatchlistItem:
    """Single watchlist entry."""

    rank: int
    file: str
    layer: str
    anomaly_type: str
    score: float
    fan_in: int
    cone_risk: float
    sc1_violation: bool
    sc5_violation: bool
    why_it_matters: str


class ADGWatchlistBuilder:
    """Build high-signal ADG anomaly watchlist from repaired signals."""

    # High-signal thresholds
    FAN_IN_PERCENTILE = 95  # Top 5% by fan-in
    CONE_RISK_PERCENTILE = 95  # Top 5% by cone risk
    CRITICAL_LAYERS = {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}

    def __init__(self, sqlite_path: Path):
        self.sqlite_path = sqlite_path
        db_uri = f"file:{sqlite_path.resolve()}?mode=ro"
        self.conn = sqlite3.connect(db_uri, uri=True)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.conn.close()

    def _get_percentile_threshold(self, table: str, column: str, percentile: int) -> float:
        """Get threshold for top Nth percentile from an allow-listed table/column pair."""
        if table not in _ALLOWED_PERCENTILE_TABLES:
            raise ValueError(f"Unexpected percentile table: {table}")
        if column not in _ALLOWED_PERCENTILE_COLUMNS:
            raise ValueError(f"Unexpected percentile column: {column}")
        if not 0 <= percentile <= 100:
            raise ValueError(f"Percentile must be between 0 and 100: {percentile}")

        self.cur.execute(f"SELECT COUNT(*) FROM {table}")
        total_rows = int(self.cur.fetchone()[0] or 0)
        if total_rows == 0:
            return 0.0

        offset = max(int(total_rows * (100 - percentile) / 100), 0)
        self.cur.execute(
            f"SELECT {column} FROM {table} ORDER BY {column} DESC LIMIT 1 OFFSET ?",
            (offset,),
        )
        row = self.cur.fetchone()
        return float(row[0]) if row else 0.0

    def _get_top_hotspots(self, threshold: int) -> list[dict[str, Any]]:
        """Get modules with fan-in above threshold."""
        self.cur.execute(
            "SELECT resolved_path, layer, fan_in, fan_out FROM mv_hotspot_centrality "
            "WHERE fan_in >= ? ORDER BY fan_in DESC",
            (threshold,),
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _get_top_cone_risk(self, threshold: float) -> list[dict[str, Any]]:
        """Get modules with cone risk above threshold."""
        self.cur.execute(
            "SELECT resolved_path, layer, direct_fan_in, cone_risk_score "
            "FROM mv_dependency_cone_risk WHERE cone_risk_score >= ? "
            "ORDER BY cone_risk_score DESC",
            (threshold,),
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _get_sc1_violations(self) -> set[str]:
        """Get set of files with SC-1 violations."""
        self.cur.execute("SELECT DISTINCT file_path FROM violations WHERE category = 'SC-1'")
        return {r[0] for r in self.cur.fetchall() if r[0]}

    def _get_sc5_violations(self) -> set[str]:
        """Get set of files with SC-5 violations."""
        self.cur.execute("SELECT DISTINCT file_path FROM violations WHERE category = 'SC-5'")
        return {r[0] for r in self.cur.fetchall() if r[0]}

    def _compute_composite_score(
        self,
        fan_in: int,
        max_fan_in: int,
        cone_risk: float,
        max_cone_risk: float,
        sc1: bool,
        sc5: bool,
        layer: str,
    ) -> float:
        """Compute bounded composite anomaly score."""
        # Base weights
        fi_weight = (fan_in / max_fan_in * 40) if max_fan_in else 0
        cone_weight = (cone_risk / max_cone_risk * 35) if max_cone_risk else 0

        # Multipliers
        sc1_multiplier = 1.5 if sc1 else 1.0
        sc5_multiplier = 1.3 if sc5 else 1.0
        layer_multiplier = 1.2 if layer in self.CRITICAL_LAYERS else 1.0

        return (fi_weight + cone_weight) * sc1_multiplier * sc5_multiplier * layer_multiplier

    def _classify_anomaly(
        self,
        sc1: bool,
        sc5: bool,
        high_fi: bool,
        high_cone: bool,
    ) -> str:
        """Classify anomaly type based on signal combination."""
        signals = []
        if high_fi:
            signals.append("hotspot")
        if high_cone:
            signals.append("cone_risk")
        if sc1:
            signals.append("gravity_violation")
        if sc5:
            signals.append("spine_gap")

        if len(signals) >= 2:
            return "multi_signal_hotspot"
        if sc1 and high_fi:
            return "gravity_violation_hotspot"
        if sc1 and high_cone:
            return "gravity_violation_cone_risk"
        if sc5:
            return "spine_gap_critical"
        if high_fi:
            return "hotspot_fan_in"
        if high_cone:
            return "hotspot_cone_risk"
        return "low_signal"

    def _explain_why(
        self,
        fan_in: int,
        cone_risk: float,
        sc1: bool,
        sc5: bool,
        layer: str,
    ) -> str:
        """One-line explanation of why this matters."""
        parts = []
        if fan_in > 500:
            parts.append(f"high inbound usage ({fan_in})")
        elif fan_in > 100:
            parts.append(f"moderate inbound usage ({fan_in})")

        if cone_risk > 500:
            parts.append("high transitive risk")
        elif cone_risk > 100:
            parts.append("moderate transitive risk")

        if sc1:
            parts.append("gravity/layer violation")
        if sc5:
            parts.append("spine gap")
        if layer in self.CRITICAL_LAYERS:
            parts.append(f"{layer} critical layer")

        return ", ".join(parts[:3]) if parts else "structural anomaly"

    def build_watchlist(self) -> list[WatchlistItem]:
        """Build ranked watchlist from repaired signals."""
        # Get thresholds
        fi_threshold = self._get_percentile_threshold(
            "mv_hotspot_centrality", "fan_in", self.FAN_IN_PERCENTILE
        )
        cone_threshold = self._get_percentile_threshold(
            "mv_dependency_cone_risk", "cone_risk_score", self.CONE_RISK_PERCENTILE
        )

        # Get top items
        hotspots = self._get_top_hotspots(int(fi_threshold))
        cone_risks = self._get_top_cone_risk(cone_threshold)

        # Get violations
        sc1_files = self._get_sc1_violations()
        sc5_files = self._get_sc5_violations()

        # Get max values for normalization
        max_fi = max((h["fan_in"] for h in hotspots), default=1)
        max_cone = max((c["cone_risk_score"] for c in cone_risks), default=1.0)

        # Combine all files of interest
        all_files = (
            {h["resolved_path"] for h in hotspots}
            | {c["resolved_path"] for c in cone_risks}
            | sc1_files
            | sc5_files
        )

        # Build watchlist items
        items: list[tuple[float, WatchlistItem]] = []

        for file_path in tqdm(all_files, desc="[ADG] Building watchlist", unit="module"):
            # Get data for this file
            hotspot = next((h for h in hotspots if h["resolved_path"] == file_path), None)
            cone = next((c for c in cone_risks if c["resolved_path"] == file_path), None)

            fan_in = hotspot["fan_in"] if hotspot else 0
            layer = hotspot["layer"] if hotspot else (cone["layer"] if cone else "")
            cone_risk = cone["cone_risk_score"] if cone else 0.0

            sc1 = file_path in sc1_files
            sc5 = file_path in sc5_files

            # Skip low-signal items
            if fan_in < 50 and cone_risk < 50 and not sc1 and not sc5:
                continue

            high_fi = fan_in >= fi_threshold
            high_cone = cone_risk >= cone_threshold

            score = self._compute_composite_score(fan_in, max_fi, cone_risk, max_cone, sc1, sc5, layer)

            anomaly_type = self._classify_anomaly(sc1, sc5, high_fi, high_cone)

            item = WatchlistItem(
                rank=0,  # Set after sorting
                file=file_path,
                layer=layer,
                anomaly_type=anomaly_type,
                score=round(score, 2),
                fan_in=fan_in,
                cone_risk=round(cone_risk, 2),
                sc1_violation=sc1,
                sc5_violation=sc5,
                why_it_matters=self._explain_why(fan_in, cone_risk, sc1, sc5, layer),
            )
            items.append((score, item))

        # Sort by score descending and assign ranks
        items.sort(key=lambda x: x[0], reverse=True)
        result = []
        for i, (_, item) in enumerate(items, 1):
            item.rank = i
            result.append(item)

        return result

    def emit_artifact(self, watchlist: list[WatchlistItem], output_dir: Path) -> Path:
        """Emit watchlist JSON artifact."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_path = output_dir / f"adg_anomaly_watchlist_{timestamp}.json"

        artifact = {
            "timestamp": timestamp,
            "sqlite_source": self.sqlite_path.name,
            "total_items": len(watchlist),
            "thresholds": {
                "fan_in_percentile": self.FAN_IN_PERCENTILE,
                "cone_risk_percentile": self.CONE_RISK_PERCENTILE,
            },
            "watchlist": [asdict(item) for item in watchlist[:50]],  # Cap at 50
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2)

        return artifact_path

    def emit_terminal_summary(self, watchlist: list[WatchlistItem], top_n: int = 10) -> str:
        """Emit compact terminal summary."""
        lines = [
            "",
            "╔══════════════════════════════════════════════════════════════╗",
            "║           ADG HIGH-SIGNAL ANOMALY WATCHLIST                  ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            f"Total items: {len(watchlist)} | Top {min(top_n, len(watchlist))} shown",
            "",
            f"{'Rank':<6}{'Score':<8}{'Type':<25}{'Layer':<8}{'File':<45}",
            "-" * 92,
        ]

        for item in watchlist[:top_n]:
            file_short = item.file[:44] if len(item.file) <= 44 else item.file[:41] + "..."
            type_short = item.anomaly_type[:24]
            layer_short = item.layer[:7] if item.layer else ""
            lines.append(f"{item.rank:<6}{item.score:<8.1f}{type_short:<25}{layer_short:<8}{file_short}")

        lines.extend(
            [
                "",
                "Signals: FI=fan-in, CR=cone-risk, SC1=gravity-violation, SC5=spine-gap",
                "Multi-signal hotspots indicate highest architectural risk.",
                "",
            ]
        )

        return "\n".join(lines)


def build_and_emit_watchlist(
    sqlite_path: Path,
    output_dir: Path,
    print_summary: bool = True,
) -> Path:
    """Main entry: build watchlist, emit artifact, optionally print summary.

    Args:
        sqlite_path: Path to ADG SQLite snapshot
        output_dir: Directory for watchlist artifact
        print_summary: Whether to print terminal summary

    Returns:
        Path to emitted JSON artifact
    """
    with ADGWatchlistBuilder(sqlite_path) as builder:
        watchlist = builder.build_watchlist()
        artifact_path = builder.emit_artifact(watchlist, output_dir)

        if print_summary:
            summary = builder.emit_terminal_summary(watchlist, top_n=10)
            print(summary)

        return artifact_path


if __name__ == "__main__":
    # CLI usage for testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python adg_watchlist_builder.py <sqlite_path> [output_dir]")
        sys.exit(1)

    sqlite_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("artifacts/adg")
    output_dir.mkdir(parents=True, exist_ok=True)

    artifact = build_and_emit_watchlist(sqlite_path, output_dir)
    print(f"\nArtifact written: {artifact}")
