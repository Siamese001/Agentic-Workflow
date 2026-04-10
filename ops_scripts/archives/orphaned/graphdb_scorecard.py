#!/usr/bin/env python3
"""GraphDB Scorecard Integration — Scorecard and findings integration.

This module integrates GraphDB CI gates with the existing scorecard
infrastructure, populating artifacts/ci_gates/ with gate outputs.

Integration points:
    - P0/P1 gate results → ci_gates/graphdb_gates.json
    - P2/P3 watch results → ci_gates/graphdb_watch.json
    - Aggregate scorecard → ci_gates/graphdb_scorecard.json

Usage:
    python ops_scripts/ci/graphdb_scorecard.py --collect
    python ops_scripts/ci/graphdb_scorecard.py --report

Reference: docs/technical/graphdb_ci_hardening.md
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_GATES_DIR = REPO_ROOT / "artifacts" / "ci_gates"
GRAPHDB_GATES_FILE = CI_GATES_DIR / "graphdb_gates.json"
GRAPHDB_WATCH_FILE = CI_GATES_DIR / "graphdb_watch.json"
SCORECARD_FILE = CI_GATES_DIR / "graphdb_scorecard.json"


@dataclass
class ScorecardEntry:
    """Single scorecard entry for a gate result."""

    gate_id: str
    severity: str  # P0, P1, P2, P3
    status: str  # PASS, FAIL, WARNING, INFO
    timestamp: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    delta: Dict[str, Any] = field(default_factory=dict)
    debt_score: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "severity": self.severity,
            "status": self.status,
            "timestamp": self.timestamp,
            "message": self.message,
            "details": self.details,
            "delta": self.delta,
            "debt_score": self.debt_score,
        }


@dataclass
class GraphDBScorecard:
    """Complete GraphDB CI scorecard."""

    timestamp: str
    run_id: str
    overall_status: str  # PASS, WARN, FAIL
    p0_summary: Dict[str, Any] = field(default_factory=dict)
    p1_summary: Dict[str, Any] = field(default_factory=dict)
    p2_summary: Dict[str, Any] = field(default_factory=dict)
    p3_summary: Dict[str, Any] = field(default_factory=dict)
    entries: List[ScorecardEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "run_id": self.run_id,
            "overall_status": self.overall_status,
            "p0_summary": self.p0_summary,
            "p1_summary": self.p1_summary,
            "p2_summary": self.p2_summary,
            "p3_summary": self.p3_summary,
            "entries": [e.to_dict() for e in self.entries],
        }


class GraphDBScorecardCollector:
    """Collects and aggregates GraphDB CI gate results into scorecards."""

    def __init__(self):
        """Initialize scorecard collector."""
        CI_GATES_DIR.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.run_id = f"graphdb-{self.timestamp.replace(':', '-')}"

    def run_p0_gates(self) -> Dict[str, Any]:
        """Run P0 gates and collect results."""
        print("[SCORECARD] Running P0 gates...")

        try:
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "ops_scripts/ci/graphdb_p0_gate.py")],
                capture_output=True,
                text=True,
                timeout=120,
            )

            # P0 gates output summary to stdout, but we need structured data
            # The gates module can be imported for structured access
            sys.path.insert(0, str(REPO_ROOT))
            from ops_scripts.ci.graphdb_p0_gate import GraphDBP0Gates

            gates = GraphDBP0Gates()
            gate_results = gates.run_all_p0_gates()

            summary = gates.get_summary()

            # Save structured results
            p0_data = {
                "timestamp": self.timestamp,
                "run_id": self.run_id,
                "summary": summary,
                "gate_results": [r.to_dict() for r in gate_results],
            }
            GRAPHDB_GATES_FILE.write_text(json.dumps(p0_data, indent=2))

            return summary

        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            ImportError,
            RuntimeError,
            OSError,
        ) as e:
            error_data = {
                "timestamp": self.timestamp,
                "error": str(e),
                "status": "ERROR",
            }
            GRAPHDB_GATES_FILE.write_text(json.dumps(error_data, indent=2))
            return {"status": "ERROR", "error": str(e)}

    def run_p1_ratchets(self) -> Dict[str, Any]:
        """Run P1 ratchets and collect results."""
        print("[SCORECARD] Running P1 ratchets...")

        try:
            sys.path.insert(0, str(REPO_ROOT))
            from ops_scripts.ci.graphdb_p1_ratchet import GraphDBP1Ratchets

            ratchets = GraphDBP1Ratchets(blocking=False)
            ratchet_results = ratchets.run_all_p1_ratchets()

            summary = ratchets.get_summary()

            # Append to gates file
            p1_data = {
                "timestamp": self.timestamp,
                "run_id": self.run_id,
                "summary": summary,
                "ratchet_results": [r.to_dict() for r in ratchet_results],
            }

            # Merge with existing gates file if present
            if GRAPHDB_GATES_FILE.exists():
                existing = json.loads(GRAPHDB_GATES_FILE.read_text())
                existing["p1_results"] = p1_data
                GRAPHDB_GATES_FILE.write_text(json.dumps(existing, indent=2))
            else:
                GRAPHDB_GATES_FILE.write_text(json.dumps({"p1_results": p1_data}, indent=2))

            return summary

        except (ImportError, RuntimeError, OSError) as e:
            return {"status": "ERROR", "error": str(e)}

    def run_p2p3_watch(self) -> Dict[str, Any]:
        """Run P2/P3 watch gates and collect results."""
        print("[SCORECARD] Running P2/P3 watch gates...")

        try:
            sys.path.insert(0, str(REPO_ROOT))
            from ops_scripts.ci.graphdb_p2p3_watch import GraphDBP2P3Watch

            watch = GraphDBP2P3Watch()
            watch_results = watch.run_all_p2p3_watches()

            summary = watch.get_summary()

            # Save to watch file
            watch_data = {
                "timestamp": self.timestamp,
                "run_id": self.run_id,
                "summary": summary,
                "watch_results": [r.to_dict() for r in watch_results],
            }
            GRAPHDB_WATCH_FILE.write_text(json.dumps(watch_data, indent=2))

            return summary

        except (ImportError, RuntimeError, OSError) as e:
            watch_data = {
                "timestamp": self.timestamp,
                "error": str(e),
                "status": "ERROR",
            }
            GRAPHDB_WATCH_FILE.write_text(json.dumps(watch_data, indent=2))
            return {"status": "ERROR", "error": str(e)}

    def build_aggregate_scorecard(
        self,
        p0_summary: Dict[str, Any],
        p1_summary: Dict[str, Any],
        p2p3_summary: Dict[str, Any],
    ) -> GraphDBScorecard:
        """Build aggregate scorecard from all gate summaries."""

        # Determine overall status
        overall_status = "PASS"
        if p0_summary.get("status") == "BLOCK":
            overall_status = "FAIL"
        elif p1_summary.get("status") == "REGRESSION":
            overall_status = "WARN"

        # Build entries from summaries
        entries: List[ScorecardEntry] = []

        # P0 entries
        for gate in p0_summary.get("gates", []):
            entries.append(
                ScorecardEntry(
                    gate_id=gate["gate_id"],
                    severity="P0",
                    status="PASS" if gate["passed"] else "FAIL",
                    timestamp=self.timestamp,
                    message=gate["message"],
                    details=gate.get("details", {}),
                )
            )

        # P1 entries
        for ratchet in p1_summary.get("ratchets", []):
            entries.append(
                ScorecardEntry(
                    gate_id=ratchet["gate_id"],
                    severity="P1",
                    status="WARN" if ratchet["regression_detected"] else "PASS",
                    timestamp=self.timestamp,
                    message=ratchet["message"],
                    details=ratchet.get("details", {}),
                    delta=ratchet.get("delta", {}),
                )
            )

        # P2/P3 entries
        for watch in p2p3_summary.get("watches", []):
            entries.append(
                ScorecardEntry(
                    gate_id=watch["gate_id"],
                    severity=watch["severity"],
                    status="INFO" if watch["severity"] == "P3" else "WARN",
                    timestamp=self.timestamp,
                    message=watch["message"],
                    details=watch.get("details", {}),
                    debt_score=watch.get("debt_score", 0),
                )
            )

        return GraphDBScorecard(
            timestamp=self.timestamp,
            run_id=self.run_id,
            overall_status=overall_status,
            p0_summary={
                "total": p0_summary.get("total", 0),
                "passed": p0_summary.get("passed", 0),
                "failed": p0_summary.get("failed", 0),
                "blocking": p0_summary.get("blocking", 0),
            },
            p1_summary={
                "total": p1_summary.get("total", 0),
                "regressions": p1_summary.get("regressions", 0),
            },
            p2_summary={
                "warnings": p2p3_summary.get("p2_warnings", 0),
                "total_debt": p2p3_summary.get("total_debt_score", 0),
            },
            p3_summary={
                "watches": p2p3_summary.get("p3_watches", 0),
            },
            entries=entries,
        )

    def collect_all(self) -> GraphDBScorecard:
        """Run all gates and build complete scorecard."""
        print("[SCORECARD] Collecting all GraphDB CI results...")
        print()

        p0_summary = self.run_p0_gates()
        p1_summary = self.run_p1_ratchets()
        p2p3_summary = self.run_p2p3_watch()

        scorecard = self.build_aggregate_scorecard(p0_summary, p1_summary, p2p3_summary)

        # Save aggregate scorecard
        SCORECARD_FILE.write_text(json.dumps(scorecard.to_dict(), indent=2))

        return scorecard

    def print_report(self, scorecard: GraphDBScorecard) -> None:
        """Print formatted scorecard report."""
        print()
        print("=" * 60)
        print("GRAPHDB CI SCORECARD")
        print("=" * 60)
        print(f"Run ID:   {scorecard.run_id}")
        print(f"Status:   {scorecard.overall_status}")
        print(f"Time:     {scorecard.timestamp}")
        print()

        # P0 Section
        print("--- P0: Hard Block Gates ---")
        p0 = scorecard.p0_summary
        print(f"  Total:    {p0.get('total', 0)}")
        print(f"  Passed:   {p0.get('passed', 0)} ✅")
        print(f"  Failed:   {p0.get('failed', 0)} ❌")
        print(f"  Blocking: {p0.get('blocking', 0)}")
        print()

        # P1 Section
        print("--- P1: Ratchet Gates ---")
        p1 = scorecard.p1_summary
        print(f"  Total:       {p1.get('total', 0)}")
        print(f"  Regressions: {p1.get('regressions', 0)}")
        print()

        # P2 Section
        print("--- P2: Warnings ---")
        p2 = scorecard.p2_summary
        print(f"  Warnings:   {p2.get('warnings', 0)}")
        print(f"  Total Debt: {p2.get('total_debt', 0)}/700")
        print()

        # P3 Section
        print("--- P3: Watch/Trend ---")
        p3 = scorecard.p3_summary
        print(f"  Watches: {p3.get('watches', 0)}")
        print()

        print("=" * 60)
        print(f"Artifacts saved to: {CI_GATES_DIR}")
        print(f"  - {GRAPHDB_GATES_FILE.name}")
        print(f"  - {GRAPHDB_WATCH_FILE.name}")
        print(f"  - {SCORECARD_FILE.name}")
        print("=" * 60)


def main() -> int:
    """Main entry point for GraphDB scorecard integration."""
    if len(sys.argv) < 2:
        print("Usage: graphdb_scorecard.py [--collect | --report]")
        print()
        print("  --collect  Run all gates and build scorecard")
        print("  --report   Print existing scorecard report")
        return 1

    cmd = sys.argv[1]

    if cmd == "--collect":
        collector = GraphDBScorecardCollector()
        scorecard = collector.collect_all()
        collector.print_report(scorecard)

        # Exit code based on overall status
        if scorecard.overall_status == "FAIL":
            return 1
        return 0

    elif cmd == "--report":
        if not SCORECARD_FILE.exists():
            print(f"[SCORECARD] No scorecard found. Run with --collect first.")
            return 1

        data = json.loads(SCORECARD_FILE.read_text())
        scorecard = GraphDBScorecard(
            timestamp=data["timestamp"],
            run_id=data["run_id"],
            overall_status=data["overall_status"],
            p0_summary=data.get("p0_summary", {}),
            p1_summary=data.get("p1_summary", {}),
            p2_summary=data.get("p2_summary", {}),
            p3_summary=data.get("p3_summary", {}),
            entries=[ScorecardEntry(**e) for e in data.get("entries", [])],
        )

        collector = GraphDBScorecardCollector()
        collector.print_report(scorecard)
        return 0

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: graphdb_scorecard.py [--collect | --report]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
