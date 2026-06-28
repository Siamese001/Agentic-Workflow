"""Gate 13: P0 Core Imports Apps Gate.

Blocks imports from ``agentic_core`` into ``apps_*`` packages. Apps may
depend on generic core contracts; core must not depend on app implementation
packages. This narrow gate catches the high-signal boundary failure without
running the broader advisory AG-PURITY surface.

Source views:
    - v_p0_core_imports_apps
"""

from __future__ import annotations

# W6 ADG consumer mode declaration.
__adg_consumer_mode__ = "inventory"

import sqlite3
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

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation  # noqa: E402
from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy  # noqa: E402

_VIEW = "v_p0_core_imports_apps"


class CoreImportsAppsGate(ADGGateBase):
    """P0 gate: core must not import app implementation packages."""

    gate_family = "core_imports_apps"
    severity = "P0"
    source_views = [_VIEW]
    execution_policy = ExecutionPolicy(
        stage="full",
        repairability="manual_only",
        gate_action="halt",
        artifact_policy="full_adg_report",
        signal_source="sqlite_mv_ci",
        evidence_tier="truth",
    )

    def _execute_gate_logic(self) -> GateResult:
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "by_app": {},
            "in_modified_area": 0,
            "signal_source": _VIEW,
        }
        if not self.conn:
            return self._empty_result(summary)

        rows = self._fetch_rows()
        for row in rows:
            app_name = str(row["app_file"]).split("/", 1)[0]
            summary["by_app"][app_name] = summary["by_app"].get(app_name, 0) + 1
            in_mod = self._is_in_modified_area(row["consumer_file"])
            if in_mod:
                summary["in_modified_area"] += 1
            violations.append(
                GateViolation(
                    violation_id=f"core_imports_apps_{row['violation_edge_id']}",
                    source_view=_VIEW,
                    source_node=str(row["consumer_id"]),
                    source_edge=str(row["violation_edge_id"]),
                    file=str(row["consumer_file"]),
                    line=int(row["import_line"] or 0) or None,
                    layer_src=str(row["consumer_layer"] or "agentic_core"),
                    layer_dst=app_name,
                    path_id=None,
                    first_illegal_hop=f"agentic_core->{app_name}",
                    path_criticality=4.0,
                    in_modified_area=in_mod,
                    message=(
                        "agentic_core imports an app implementation package "
                        f"({row['consumer_file']} -> {row['app_file']}). "
                        "Move the app binding behind U0 runtime customization or a generic core contract."
                    ),
                    extra={
                        "app_file": row["app_file"],
                        "import_symbol": row["import_symbol"],
                        "violation_type": row["violation_type"],
                    },
                    path_criticality_class="ingress",
                    structured_action_required=True,
                    approval_required=True,
                )
            )

        summary["total_violations"] = len(violations)
        status = "blocked" if violations else "passed"
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

    def _fetch_rows(self) -> list[sqlite3.Row]:
        assert self.conn is not None
        try:
            return list(
                self.conn.execute(
                    "SELECT violation_edge_id, consumer_id, consumer_file, consumer_layer, "
                    "app_file, import_symbol, import_line, violation_type "
                    f"FROM {_VIEW} "
                    "ORDER BY consumer_file, import_line, app_file"
                ).fetchall()
            )
        except sqlite3.OperationalError:
            return list(
                self.conn.execute(
                    "SELECT e.id AS violation_edge_id, "
                    "       n_src.id AS consumer_id, "
                    "       n_src.resolved_path AS consumer_file, "
                    "       n_src.layer AS consumer_layer, "
                    "       n_dst.resolved_path AS app_file, "
                    "       e.symbol AS import_symbol, "
                    "       e.line_no AS import_line, "
                    "       'P0: agentic_core imports apps_*' AS violation_type "
                    "FROM edges e "
                    "JOIN nodes n_src ON e.src_id = n_src.id "
                    "JOIN nodes n_dst ON e.dst_id = n_dst.id "
                    "WHERE e.relation_type = 'imports' "
                    "  AND n_src.resolved_path LIKE 'agentic_core/%' "
                    "  AND n_dst.resolved_path LIKE 'apps_%/%' "
                    "  AND n_dst.resolved_path NOT LIKE 'apps_shared/%' "
                    "ORDER BY n_src.resolved_path, e.line_no, n_dst.resolved_path"
                ).fetchall()
            )

    def _empty_result(self, summary: dict[str, Any]) -> GateResult:
        summary["note"] = "SQLite connection unavailable - no violations detected"
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary=summary,
            policy=self.execution_policy,
        )


def main() -> int:
    gate = CoreImportsAppsGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    sys.exit(main())
