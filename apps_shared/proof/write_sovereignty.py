"""Write sovereignty validator — ADG-driven assertion that no apps_* code
emits direct infrastructure writes.

Per the prompt §4G and `mv_write_sovereignty_paths`, every state mutation
MUST flow through the UWG (User-Writable Gateway). A direct infrastructure
write from an `apps_*` file is a P0 architectural violation regardless of
runtime behavior.

This validator is **structural** (queries the ADG) — distinct from the runtime
validators in :mod:`apps_shared.proof.validators`. Both must pass for a full
proof.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WriteSovereigntyResult:
    """Result of write-sovereignty check for one or more apps."""

    snapshot_path: str
    apps_checked: tuple[str, ...]
    direct_writes_per_app: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    p0_apps_direct_infra: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    p0_write_bypass_uwg: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    fail_reasons: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.fail_reasons

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_path": self.snapshot_path,
            "apps_checked": list(self.apps_checked),
            "ok": self.ok,
            "direct_writes_per_app": dict(self.direct_writes_per_app),
            "p0_apps_direct_infra": dict(self.p0_apps_direct_infra),
            "p0_write_bypass_uwg": dict(self.p0_write_bypass_uwg),
            "fail_reasons": list(self.fail_reasons),
        }


# Three structural views must all show zero rows for each app:
#   mv_write_sovereignty_paths  — every direct infra write site (direct + uwg)
#   v_p0_apps_direct_infra      — apps_* importing infrastructure directly
#   v_p0_write_bypass_uwg       — write edges that bypass UWG
#
# We filter mv_write_sovereignty_paths to ONLY non-UWG-routed writes (the rest
# is informational), and require zero rows in all three views per app.


def validate_write_sovereignty(*, snapshot: Path, apps: tuple[str, ...]) -> WriteSovereigntyResult:
    """Run the three structural write-sovereignty checks for every app."""
    if not snapshot.exists():
        raise FileNotFoundError(f"ADG snapshot missing: {snapshot}")

    result = WriteSovereigntyResult(
        snapshot_path=str(snapshot),
        apps_checked=tuple(apps),
    )
    con = sqlite3.connect(snapshot)
    try:
        cur = con.cursor()
        for app_id in apps:
            like = f"{app_id}/%"

            # 1. Direct infra writes that DO NOT route through UWG
            try:
                rows = cur.execute(
                    """
                    SELECT edge_id, writer_file, writer_layer, write_symbol,
                           write_line, is_uwg_routed, is_direct_infra_write,
                           severity
                    FROM mv_write_sovereignty_paths
                    WHERE writer_file LIKE ?
                      AND is_direct_infra_write = 1
                      AND COALESCE(is_uwg_routed, 0) = 0
                    """,
                    (like,),
                ).fetchall()
            except sqlite3.Error as exc:
                result.fail_reasons.append(f"{app_id}: mv_write_sovereignty_paths query failed: {exc}")
                rows = []
            cols = (
                "edge_id",
                "writer_file",
                "writer_layer",
                "write_symbol",
                "write_line",
                "is_uwg_routed",
                "is_direct_infra_write",
                "severity",
            )
            sample = [dict(zip(cols, r)) for r in rows]
            result.direct_writes_per_app[app_id] = sample
            if sample:
                result.fail_reasons.append(f"{app_id}: {len(sample)} direct infra writes bypass UWG")

            # 2. apps_* directly importing infrastructure
            try:
                rows2 = cur.execute(
                    """
                    SELECT violation_edge_id, consumer_id, consumer_file,
                           consumer_layer, import_symbol, import_line,
                           violation_type
                    FROM v_p0_apps_direct_infra
                    WHERE consumer_file LIKE ?
                    """,
                    (like,),
                ).fetchall()
            except sqlite3.Error as exc:
                result.fail_reasons.append(f"{app_id}: v_p0_apps_direct_infra query failed: {exc}")
                rows2 = []
            cols2 = (
                "violation_edge_id",
                "consumer_id",
                "consumer_file",
                "consumer_layer",
                "import_symbol",
                "import_line",
                "violation_type",
            )
            sample2 = [dict(zip(cols2, r)) for r in rows2]
            result.p0_apps_direct_infra[app_id] = sample2
            if sample2:
                result.fail_reasons.append(f"{app_id}: {len(sample2)} P0 direct infra import violations")

            # 3. Write edges that bypass UWG
            try:
                rows3 = cur.execute(
                    """
                    SELECT violation_edge_id, writer_id, writer_file,
                           writer_layer, write_symbol, write_line,
                           violation_type
                    FROM v_p0_write_bypass_uwg
                    WHERE writer_file LIKE ?
                    """,
                    (like,),
                ).fetchall()
            except sqlite3.Error as exc:
                result.fail_reasons.append(f"{app_id}: v_p0_write_bypass_uwg query failed: {exc}")
                rows3 = []
            cols3 = (
                "violation_edge_id",
                "writer_id",
                "writer_file",
                "writer_layer",
                "write_symbol",
                "write_line",
                "violation_type",
            )
            sample3 = [dict(zip(cols3, r)) for r in rows3]
            result.p0_write_bypass_uwg[app_id] = sample3
            if sample3:
                result.fail_reasons.append(f"{app_id}: {len(sample3)} P0 write-bypass-UWG violations")
    finally:
        con.close()

    return result


__all__ = ["WriteSovereigntyResult", "validate_write_sovereignty"]
