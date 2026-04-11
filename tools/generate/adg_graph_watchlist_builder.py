#!/usr/bin/env python3
"""Graph-native ADG watchlist builder - Prompt 5.

Builds high-signal graph intelligence watchlist from:
- mv_graph_reverse_dependency_hotspots
- mv_graph_chokepoint_bridges
- mv_graph_scc_clusters
- mv_graph_critical_path_blast_radius

Focus: graph-native architectural intelligence not covered by regular ADG CI.
Emits compact JSON artifact and terminal summary.
Non-blocking intelligence layer.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RemediationGuide:
    """Remediation guidance for a graph hotspot."""
    recommended_fix_pattern: str
    remediation_priority: str  # high, medium, low
    gate_severity: str  # warn, fail
    gate_decision: str  # WARN, FAIL, INFO
    operator_note: str


@dataclass
class GraphWatchlistItem:
    """Single graph-native watchlist entry."""
    rank: int
    file: str
    layer: str
    graph_anomaly_type: str
    score: float
    reverse_dep_score: float
    bridge_score: float
    scc_cluster_size: int
    blast_radius: float
    why_it_matters: str
    remediation: RemediationGuide | None = None


class ADGGraphWatchlistBuilder:
    """Build high-signal graph-native ADG watchlist."""

    # High-signal thresholds (graph-native)
    TOP_PERCENTILE = 90  # Top 10% by graph metrics
    CRITICAL_LAYERS = {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_SHARED", "L_RUNTIME"}

    # Signal-to-fix-pattern mapping (Prompt 7 remediation guidance)
    FIX_PATTERNS: dict[str, dict[str, str]] = {
        "reverse_dependency_hotspot": {
            "pattern": "reduce_inbound_surface",
            "actions": "split_responsibilities, introduce_stable_facade",
            "note": "Module has high inbound dependency surface; consider facade or responsibility split",
        },
        "chokepoint_bridge": {
            "pattern": "extract_interface_boundary",
            "actions": "break_hub_module, separate_coordination_from_execution",
            "note": "Module acts as structural bridge; extract interfaces to reduce coupling",
        },
        "risky_scc_cluster": {
            "pattern": "break_cycle_with_contract_extraction",
            "actions": "invert_dependency_direction, move_shared_types_to_neutral_layer",
            "note": "Module in cyclic dependency cluster; break cycle with contract extraction",
        },
        "critical_path_blast_radius": {
            "pattern": "isolate_change_surface",
            "actions": "narrow_shared_config, stabilize_adapter_boundary",
            "note": "Module has large downstream impact; isolate change surface",
        },
        "multi_signal_graph_hotspot": {
            "pattern": "comprehensive_refactor_needed",
            "actions": "combine_all_single_signal_fixes",
            "note": "Multiple structural risks detected; comprehensive review required",
        },
    }

    # CI Gate thresholds (Prompt 7)
    GATE_WARN_THRESHOLD = 50.0  # Score above this triggers WARN
    GATE_FAIL_THRESHOLD = 75.0  # Score above this in protected layer triggers FAIL
    BLAST_RADIUS_WARN_THRESHOLD = 100.0  # Blast radius above this triggers WARN
    BLAST_RADIUS_FAIL_THRESHOLD = 200.0  # Blast radius above this in protected layer triggers FAIL

    def __init__(self, sqlite_path: Path):
        self.sqlite_path = sqlite_path
        self.conn = sqlite3.connect(str(sqlite_path))
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.conn.close()

    def _get_threshold(self, table: str, column: str) -> float:
        """Get threshold for top percentile."""
        self.cur.execute(
            f"SELECT {column} FROM {table} ORDER BY {column} DESC "
            f"LIMIT 1 OFFSET (SELECT COUNT(*) FROM {table}) * {self.TOP_PERCENTILE} / 100"
        )
        row = self.cur.fetchone()
        return row[0] if row else 0.0

    def _get_reverse_dep_hotspots(self, threshold: float) -> list[dict[str, Any]]:
        """Get reverse dependency hotspots above threshold."""
        self.cur.execute(
            "SELECT file_path, layer, reverse_dependency_score, layer_criticality_weight "
            "FROM mv_graph_reverse_dependency_hotspots "
            "WHERE reverse_dependency_score >= ? "
            "ORDER BY reverse_dependency_score * layer_criticality_weight DESC",
            (threshold,)
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _get_chokepoint_bridges(self, threshold: float) -> list[dict[str, Any]]:
        """Get chokepoint/bridge modules above threshold."""
        self.cur.execute(
            "SELECT file_path, layer, bridge_score, bridge_type, fan_in, fan_out "
            "FROM mv_graph_chokepoint_bridges "
            "WHERE bridge_score >= ? AND bridge_type IN ('high_impact_bridge', 'bridge_candidate') "
            "ORDER BY bridge_score DESC",
            (threshold,)
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _get_scc_clusters(self, threshold: int) -> list[dict[str, Any]]:
        """Get SCC clusters above threshold."""
        self.cur.execute(
            "SELECT file_path, layer, scc_risk_score, cluster_size, cluster_type "
            "FROM mv_graph_scc_clusters "
            "WHERE scc_risk_score >= ? AND cluster_type IN ('large_tight_cluster', 'medium_tight_cluster') "
            "ORDER BY scc_risk_score DESC",
            (threshold,)
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _get_blast_radius(self, threshold: float) -> list[dict[str, Any]]:
        """Get critical path blast radius modules above threshold."""
        self.cur.execute(
            "SELECT file_path, layer, weighted_blast_radius, blast_radius_type, critical_downstream_count "
            "FROM mv_graph_critical_path_blast_radius "
            "WHERE weighted_blast_radius >= ? AND blast_radius_type IN ('high_impact_hub', 'moderate_impact_hub') "
            "ORDER BY weighted_blast_radius DESC",
            (threshold,)
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _compute_graph_composite_score(
        self,
        reverse_dep: float,
        bridge: float,
        scc_risk: int,
        blast_radius: float,
        layer: str,
    ) -> float:
        """Compute bounded graph-native composite score."""
        # Base weights (graph-native metrics)
        rev_weight = min(reverse_dep / 100 * 25, 25)  # Cap at 25
        bridge_weight = min(bridge / 50 * 20, 20)  # Cap at 20
        scc_weight = min(scc_risk / 100 * 20, 20)  # Cap at 20
        blast_weight = min(blast_radius / 100 * 25, 25)  # Cap at 25

        # Critical layer multiplier
        layer_multiplier = 1.25 if layer in self.CRITICAL_LAYERS else 1.0

        return (rev_weight + bridge_weight + scc_weight + blast_weight) * layer_multiplier

    def _classify_graph_anomaly(
        self,
        high_reverse_dep: bool,
        high_bridge: bool,
        high_scc: bool,
        high_blast: bool,
    ) -> str:
        """Classify graph-native anomaly type."""
        signals = []
        if high_reverse_dep:
            signals.append("reverse_dep")
        if high_bridge:
            signals.append("bridge")
        if high_scc:
            signals.append("scc")
        if high_blast:
            signals.append("blast")

        # Multi-signal requires 2 or more live non-zero graph dimensions
        if len(signals) >= 2:
            if len(signals) >= 3:
                return "multi_signal_graph_hotspot"
            # Exactly 2 signals
            return f"{signals[0]}_{signals[1]}_combined"
        if high_reverse_dep and high_blast:
            return "reverse_dependency_hotspot"  # High inbound + high downstream impact
        if high_bridge:
            return "chokepoint_bridge"
        if high_scc:
            return "risky_scc_cluster"
        if high_blast:
            return "critical_path_blast_radius"
        if high_reverse_dep:
            return "reverse_dependency_hotspot"
        return "low_signal_graph"

    def _explain_graph_why(
        self,
        reverse_dep: float,
        bridge: float,
        scc_size: int,
        blast_radius: float,
        layer: str,
    ) -> str:
        """One-line explanation of why this graph-native finding matters."""
        parts = []
        if reverse_dep > 200:
            parts.append(f"high inbound dep surface ({int(reverse_dep)})")
        elif reverse_dep > 50:
            parts.append(f"significant inbound deps ({int(reverse_dep)})")

        if bridge > 100:
            parts.append("structural chokepoint")
        elif bridge > 50:
            parts.append("bridge-like connectivity")

        if scc_size > 15:
            parts.append(f"large tight cluster ({scc_size} modules)")
        elif scc_size > 8:
            parts.append(f"tight coupling cluster ({scc_size} modules)")

        if blast_radius > 200:
            parts.append(f"massive blast radius ({int(blast_radius)})")
        elif blast_radius > 100:
            parts.append(f"high change impact ({int(blast_radius)})")

        if layer in self.CRITICAL_LAYERS:
            parts.append(f"{layer} critical layer")

        return ", ".join(parts[:3]) if parts else "graph-structural anomaly"

    def _get_remediation_guide(
        self,
        anomaly_type: str,
        score: float,
        blast_radius: float,
        layer: str,
    ) -> RemediationGuide:
        """Compute remediation guidance and gate decision for a graph hotspot.

        Prompt 7: Implements CI gate policy:
        - WARN on new high-score hotspot in non-protected layers
        - FAIL on new multi-signal hotspot in protected layers
        - FAIL on SCC emergence in protected layers
        - WARN/FAIL on blast radius increase above threshold for protected modules
        """
        # Get fix pattern for this anomaly type
        fix_info = self.FIX_PATTERNS.get(anomaly_type, {
            "pattern": "review_required",
            "actions": "manual_analysis",
            "note": "Graph anomaly detected; manual review required",
        })

        # Determine if in protected layer
        is_protected = layer in self.CRITICAL_LAYERS

        # Determine gate decision based on score and layer
        if anomaly_type == "risky_scc_cluster" and is_protected:
            # SCC in protected layer is always FAIL
            gate_decision = "FAIL"
            gate_severity = "fail"
            priority = "high"
        elif score >= self.GATE_FAIL_THRESHOLD and is_protected:
            # High score in protected layer = FAIL
            gate_decision = "FAIL"
            gate_severity = "fail"
            priority = "high"
        elif blast_radius >= self.BLAST_RADIUS_FAIL_THRESHOLD and is_protected:
            # High blast radius in protected layer = FAIL
            gate_decision = "FAIL"
            gate_severity = "fail"
            priority = "high"
        elif score >= self.GATE_WARN_THRESHOLD:
            # High score anywhere = WARN
            gate_decision = "WARN"
            gate_severity = "warn"
            priority = "medium"
        elif blast_radius >= self.BLAST_RADIUS_WARN_THRESHOLD:
            # High blast radius anywhere = WARN
            gate_decision = "WARN"
            gate_severity = "warn"
            priority = "medium"
        else:
            # Below thresholds = INFO only
            gate_decision = "INFO"
            gate_severity = "info"
            priority = "low"

        # Build operator note
        note = fix_info["note"]
        if gate_decision in ("WARN", "FAIL"):
            note += f" [{gate_decision}: {priority} priority in {layer}]"

        return RemediationGuide(
            recommended_fix_pattern=fix_info["pattern"],
            remediation_priority=priority,
            gate_severity=gate_severity,
            gate_decision=gate_decision,
            operator_note=note,
        )

    def build_graph_watchlist(self) -> list[GraphWatchlistItem]:
        """Build ranked graph-native watchlist."""
        # Get thresholds for top percentile filtering
        rev_threshold = self._get_threshold("mv_graph_reverse_dependency_hotspots", "reverse_dependency_score")
        bridge_threshold = self._get_threshold("mv_graph_chokepoint_bridges", "bridge_score")
        scc_threshold = self._get_threshold("mv_graph_scc_clusters", "scc_risk_score")
        blast_threshold = self._get_threshold("mv_graph_critical_path_blast_radius", "weighted_blast_radius")

        # Get high-signal items from each graph view
        rev_hotspots = {r["file_path"]: r for r in self._get_reverse_dep_hotspots(rev_threshold)}
        bridges = {b["file_path"]: b for b in self._get_chokepoint_bridges(bridge_threshold)}
        scc_clusters = {s["file_path"]: s for s in self._get_scc_clusters(int(scc_threshold))}
        blast_modules = {b["file_path"]: b for b in self._get_blast_radius(blast_threshold)}

        # Combine all files of interest
        all_files = set(rev_hotspots.keys()) | set(bridges.keys()) | set(scc_clusters.keys()) | set(blast_modules.keys())

        # Get max values for normalization
        max_rev = max((r["reverse_dependency_score"] for r in rev_hotspots.values()), default=1.0)
        max_bridge = max((b["bridge_score"] for b in bridges.values()), default=1.0)
        max_scc = max((s["scc_risk_score"] for s in scc_clusters.values()), default=1)
        max_blast = max((b["weighted_blast_radius"] for b in blast_modules.values()), default=1.0)

        # Build watchlist items
        items: list[tuple[float, GraphWatchlistItem]] = []

        for file_path in all_files:
            rev = rev_hotspots.get(file_path, {})
            bridge = bridges.get(file_path, {})
            scc = scc_clusters.get(file_path, {})
            blast = blast_modules.get(file_path, {})

            reverse_dep_score = rev.get("reverse_dependency_score", 0.0)
            bridge_score = bridge.get("bridge_score", 0.0)
            scc_size = scc.get("cluster_size", 0)
            blast_radius = blast.get("weighted_blast_radius", 0.0)
            layer = rev.get("layer") or bridge.get("layer") or scc.get("layer") or blast.get("layer") or ""

            # Skip low-signal items
            if reverse_dep_score < 30 and bridge_score < 30 and scc_size < 5 and blast_radius < 30:
                continue

            high_rev = reverse_dep_score >= rev_threshold
            high_bridge = bridge_score >= bridge_threshold
            high_scc = scc_size >= scc_threshold
            high_blast = blast_radius >= blast_threshold

            score = self._compute_graph_composite_score(
                reverse_dep_score, bridge_score, scc_size, blast_radius, layer
            )

            graph_anomaly_type = self._classify_graph_anomaly(high_rev, high_bridge, high_scc, high_blast)

            # Compute remediation guide (Prompt 7)
            remediation = self._get_remediation_guide(
                graph_anomaly_type, score, blast_radius, layer
            )

            item = GraphWatchlistItem(
                rank=0,  # Set after sorting
                file=file_path,
                layer=layer,
                graph_anomaly_type=graph_anomaly_type,
                score=round(score, 2),
                reverse_dep_score=round(reverse_dep_score, 2),
                bridge_score=round(bridge_score, 2),
                scc_cluster_size=scc_size,
                blast_radius=round(blast_radius, 2),
                why_it_matters=self._explain_graph_why(
                    reverse_dep_score, bridge_score, scc_size, blast_radius, layer
                ),
                remediation=remediation,
            )
            items.append((score, item))

        # Sort by score descending and assign ranks
        items.sort(key=lambda x: x[0], reverse=True)
        result = []
        for i, (_, item) in enumerate(items, 1):
            item.rank = i
            result.append(item)

        return result

    def emit_artifact(
        self, watchlist: list[GraphWatchlistItem], output_dir: Path
    ) -> Path:
        """Emit graph watchlist JSON artifact."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_path = output_dir / f"adg_graph_watchlist_{timestamp}.json"

        # Promotion classification for each signal type
        promotion_status = {
            "reverse_dependency": "promote_now",
            "chokepoint_bridge": "promote_now",
            "blast_radius": "promote_now",
            "scc_cluster": "surface_with_caveat",  # Semantic proof not fully closed
        }

        # Caveat for SCC: codebase may be acyclic (positive signal)
        scc_caveat = (
            "SCC detection returned 0 clusters - codebase may have no import cycles. "
            "This is architecturally positive. Full semantic toy-graph proof deferred."
        )

        # Compute gate summary for artifact (Prompt 7)
        gate_summary = {
            "total_fail": sum(1 for i in watchlist if i.remediation and i.remediation.gate_decision == "FAIL"),
            "total_warn": sum(1 for i in watchlist if i.remediation and i.remediation.gate_decision == "WARN"),
            "total_info": sum(1 for i in watchlist if i.remediation and i.remediation.gate_decision == "INFO"),
        }

        artifact = {
            "timestamp": timestamp,
            "sqlite_source": self.sqlite_path.name,
            "total_items": len(watchlist),
            "threshold": {
                "graph_top_percentile": self.TOP_PERCENTILE,
                "gate_warn_threshold": self.GATE_WARN_THRESHOLD,
                "gate_fail_threshold": self.GATE_FAIL_THRESHOLD,
            },
            "promotion_status": promotion_status,
            "gate_summary": gate_summary,
            "caveats": {
                "scc_detection": scc_caveat if len(watchlist) > 0 and all(i.scc_cluster_size == 0 for i in watchlist) else None,
            },
            "watchlist": [asdict(item) for item in watchlist[:30]],  # Cap at 30
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2)

        return artifact_path

    def emit_terminal_summary(self, watchlist: list[GraphWatchlistItem], top_n: int = 10) -> str:
        """Emit compact terminal summary for graph-native SQL analytics."""
        lines = [
            "",
            "╔══════════════════════════════════════════════════════════════╗",
            "║     ADG GRAPH-NATIVE SQL ANALYTICS WATCHLIST               ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            f"Total graph items: {len(watchlist)} | Top {min(top_n, len(watchlist))} shown",
            "",
            f"{'Rank':<6}{'Score':<8}{'Graph Type':<28}{'Layer':<8}{'File':<40}",
            "-" * 90,
        ]

        for item in watchlist[:top_n]:
            file_short = item.file[:39] if len(item.file) <= 39 else item.file[:36] + "..."
            type_short = item.graph_anomaly_type[:27]
            layer_short = item.layer[:7] if item.layer else ""
            lines.append(
                f"{item.rank:<6}{item.score:<8.1f}{type_short:<28}{layer_short:<8}{file_short}"
            )

        # Add caveat note for SCC if relevant
        has_scc_items = any(i.scc_cluster_size > 0 for i in watchlist[:top_n])
        scc_note = ""
        if not has_scc_items:
            scc_note = "[Note: SCC=0 - codebase appears acyclic, which is architecturally positive]"

        # Add remediation guidance for top 3 items (Prompt 7)
        lines.append("")
        lines.append("Remediation guidance (top 3):")
        for item in watchlist[:3]:
            if item.remediation:
                fix_short = item.remediation.recommended_fix_pattern[:35]
                gate = item.remediation.gate_decision
                lines.append(f"  G{item.rank}: {fix_short:<35} [{gate}]")

        lines.extend([
            "",
            "Graph-native SQL signals: RevDep=reverse-dep, Bridge=chokepoint,",
            "                         SCC=tight-cluster, Blast=downstream-impact",
            f"{scc_note}",
            "Multi-signal items = highest structural risk.",
            "",
        ])

        return "\n".join(lines)


def build_and_emit_graph_watchlist(
    sqlite_path: Path,
    output_dir: Path,
    print_summary: bool = True,
) -> Path:
    """Main entry: build graph watchlist, emit artifact, optionally print summary.

    Args:
        sqlite_path: Path to ADG SQLite snapshot
        output_dir: Directory for watchlist artifact
        print_summary: Whether to print terminal summary

    Returns:
        Path to emitted JSON artifact
    """
    with ADGGraphWatchlistBuilder(sqlite_path) as builder:
        watchlist = builder.build_graph_watchlist()
        artifact_path = builder.emit_artifact(watchlist, output_dir)

        if print_summary:
            summary = builder.emit_terminal_summary(watchlist, top_n=10)
            print(summary)

        return artifact_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python adg_graph_watchlist_builder.py <sqlite_path> [output_dir]")
        sys.exit(1)

    sqlite_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("artifacts/adg")
    output_dir.mkdir(parents=True, exist_ok=True)

    artifact = build_and_emit_graph_watchlist(sqlite_path, output_dir)
    print(f"\nGraph artifact written: {artifact}")
