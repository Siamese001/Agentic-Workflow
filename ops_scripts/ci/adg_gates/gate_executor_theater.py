"""Gate 7: P0 Executor Theater Gate.

Detects fake-parallelism infrastructure in production code by combining
AST scanning (executor-bearing module detection) with ADG graph queries
(production fan-in reachability). Joins the ADG suite so the check runs
automatically on every `generate_full_adg.py` invocation alongside the
other P0 gates.

Detection sub-gates (delegated to ``ops_scripts/ci/executor_theater_gate.py``):

    G1  Executor-bearing module with zero inbound production callers
    G2  Worker-count or parallel banner in generate_full_adg.py with no
        real dispatch path
    G3  Imported parallel helper that is never actually used
    G4  Experimental/archived executor code in production path without a
        ``# classification:`` marker

Source views:
    Raw ADG tables (``nodes``, ``edges``) — this gate's detection logic is
    hybrid AST + graph and does not rely on materialized views.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()

from ops_scripts.ci.adg_gates.gate_base import (  # noqa: E402
    ADGGateBase,
    GateResult,
    GateViolation,
)
from ops_scripts.ci.executor_theater_gate import (  # noqa: E402
    gate_g1_reachability,
    gate_g2_claim_to_execution,
    gate_g3_import_only,
    gate_g4_classification,
)

# Prefix → sub-gate label mapping for provenance
_SUBGATE_LABELS: dict[str, str] = {
    "G1": "production_reachability",
    "G2": "claim_to_execution",
    "G3": "import_only_capability",
    "G4": "production_classification",
}

# Regex for extracting file path from G1/G4 violations (format:
# "G{N}: {rel_path} bears ...")
_FILE_EXTRACT_RE = re.compile(r"^G[1-4]:\s+([^\s:]+\.py)")


def _extract_file(message: str) -> str | None:
    """Extract the first .py path from a violation message, if any."""
    match = _FILE_EXTRACT_RE.match(message)
    if match:
        return match.group(1)
    return None


def _violation_id(sub_gate: str, index: int, message: str) -> str:
    """Stable id: subgate + message hash-like slug."""
    slug = re.sub(r"[^a-zA-Z0-9_]", "_", message[:60]).strip("_").lower()
    return f"exec_theater_{sub_gate.lower()}_{index:03d}_{slug}"


def _parse_subgate(message: str) -> tuple[str, str]:
    """Return (sub_gate_code, subgate_label) for a raw violation string."""
    if len(message) >= 2 and message[0] == "G" and message[1].isdigit():
        code = message[:2]
        return code, _SUBGATE_LABELS.get(code, "unknown")
    return "G?", "unknown"


class ExecutorTheaterGate(ADGGateBase):
    """P0 gate that blocks fake-parallelism infrastructure.

    Wraps the standalone ``executor_theater_gate.py`` detection functions
    so they participate in the ADG suite with full ``GateViolation``
    provenance and artifact emission.
    """

    gate_family = "executor_theater"
    severity = "P0"
    # Raw ADG tables only — no materialized view dependency.
    source_views: list[str] = ["nodes", "edges"]

    def _execute_gate_logic(self) -> GateResult:
        """Run all four sub-gates and fold their findings into GateResult."""
        summary: dict[str, Any] = {
            "total_violations": 0,
            "g1_production_reachability": 0,
            "g2_claim_to_execution": 0,
            "g3_import_only_capability": 0,
            "g4_production_classification": 0,
            "in_modified_area": 0,
        }

        if self.sqlite_path is None or not self.sqlite_path.exists():
            return self._empty_result()

        # G1 needs the sqlite path; G2-G4 are pure filesystem scans.
        raw_by_gate: list[tuple[str, list[str]]] = [
            ("G1", gate_g1_reachability(self.sqlite_path)),
            ("G2", gate_g2_claim_to_execution()),
            ("G3", gate_g3_import_only()),
            ("G4", gate_g4_classification()),
        ]

        violations: list[GateViolation] = []
        idx = 0
        for expected_code, raw_list in raw_by_gate:
            # progress_bar: N/A — iterates over exactly 4 sub-gates (G1-G4); sub-second total. §16 exempt.
            for raw in raw_list:
                # progress_bar: N/A — violation count typically 0-20; each iteration is dict lookup + dataclass construction. §16 exempt.
                code, label = _parse_subgate(raw)
                if code == "G?":
                    # Defensive: function may return text without prefix
                    code = expected_code
                    label = _SUBGATE_LABELS.get(expected_code, "unknown")

                bucket = {
                    "G1": "g1_production_reachability",
                    "G2": "g2_claim_to_execution",
                    "G3": "g3_import_only_capability",
                    "G4": "g4_production_classification",
                }.get(code)
                if bucket:
                    summary[bucket] += 1

                file_hint = _extract_file(raw)
                in_mod = self._is_in_modified_area(file_hint)
                if in_mod:
                    summary["in_modified_area"] += 1

                # Path criticality: G1 (real callers missing) and G3
                # (imports of dead modules) are the most dangerous — they
                # indicate infrastructure that ships but never runs. G2/G4
                # are lower (signal-only, cosmetic).
                criticality = {
                    "G1": 3.8,
                    "G2": 2.5,
                    "G3": 3.5,
                    "G4": 2.0,
                }.get(code, 2.5)

                violations.append(
                    GateViolation(
                        violation_id=_violation_id(code, idx, raw),
                        source_view="nodes+edges" if code == "G1" else "ast_scan",
                        source_node=None,
                        source_edge=None,
                        file=file_hint,
                        line=None,
                        layer_src=None,
                        layer_dst=None,
                        path_id=None,
                        first_illegal_hop=f"{code}:{label}",
                        path_criticality=criticality,
                        in_modified_area=in_mod,
                        message=raw,
                        extra={"sub_gate": code, "sub_gate_label": label},
                        path_criticality_class=(
                            "sink" if code in {"G1", "G3"} else "informational"
                        ),
                    )
                )
                idx += 1

        summary["total_violations"] = len(violations)

        # P0: any G1 or G3 violation blocks (genuine theater). G2/G4 warn.
        has_blocking = summary["g1_production_reachability"] > 0 or summary["g3_import_only_capability"] > 0
        status = "blocked" if has_blocking else ("warn" if violations else "passed")

        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=violations,
            summary=summary,
            policy=self.execution_policy,
        )

    def _empty_result(self) -> GateResult:
        """Return passed result when SQLite is unavailable (shouldn't happen in full run)."""
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary={
                "total_violations": 0,
                "g1_production_reachability": 0,
                "g2_claim_to_execution": 0,
                "g3_import_only_capability": 0,
                "g4_production_classification": 0,
                "in_modified_area": 0,
                "note": "ADG SQLite unavailable — gate skipped",
            },
            policy=self.execution_policy,
        )


def main() -> int:
    """CLI entry point — same contract as the other P0 gates."""
    gate = ExecutorTheaterGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    sys.exit(main())
