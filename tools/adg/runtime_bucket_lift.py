"""Runtime bucket lift — port runtime ADG edges into the unified ADG snapshot.

Per the 2026-04-29 three-bucket authority model (W2): runtime evidence
(OTel traces, sealed receipts) lives in a separate runtime ADG SQLite
emitted by ``tools/generate/generate_runtime_adg.py``. This script lifts
those edges into the canonical static ADG snapshot's ``edges`` table with
``bucket = 'runtime'`` and populates ``evidence_refs`` with the trace
identifiers needed by SSOTDecisionRecord reconciliation.

Lift contract:

* Input: latest static ADG snapshot at
  ``artifacts/adg/adg_indexed_<timestamp>.sqlite`` and latest runtime ADG
  snapshot at ``artifacts/runtime_adg/runtime_adg_<...>.sqlite``.
* Output: in-place INSERT of one row per runtime edge into the static
  snapshot's ``edges`` table, with:

    bucket            = 'runtime'
    resolution_status = 'VERIFIED_RUNTIME' (or PARTIAL_TRACE / MISSING_TRACE)
    authority_status  = 'AUTHORITATIVE_RUNTIME' (verified) / 'PARTIAL'
                        (partial trace) / 'UNKNOWN_NOT_PROOF' (missing)
    authority         = 'runtime_observed' (legacy back-compat)
    evidence_refs     = JSON {"run_id": ..., "trace_id": ..., "span_id": ...}
    edge_kind         = 'RUNTIME_OBSERVED' (or one of the spec runtime kinds)

* The ``edges.dst_id`` / ``edges.src_id`` of runtime rows reference the
  static-ADG ``nodes`` table by adg_name lookup. If the static graph does
  not contain the runtime node, we INSERT a stub node (resolved_path='')
  so the runtime edge is preserved as evidence — this surfaces the
  HIDDEN_PATH outcome class in SSOTDecisionRecord.

Idempotency: The lift uses an UPSERT-equivalent pattern keyed by
(src_id, dst_id, relation_type, source_file, line_no, authority) so
repeated runs do not duplicate rows.

Usage:

    python tools/adg/runtime_bucket_lift.py
        [--static-snapshot artifacts/adg/adg_indexed_<ts>.sqlite]
        [--runtime-snapshot artifacts/runtime_adg/runtime_adg_<...>.sqlite]
        [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass
class LiftStats:
    """Accounting for one lift run."""

    runtime_edges_read: int = 0
    nodes_stubbed: int = 0
    edges_inserted: int = 0
    edges_skipped_duplicate: int = 0
    edges_skipped_invalid: int = 0


def _latest_snapshot(pattern: str, root: Path) -> Path | None:
    """Return the most recent file matching ``pattern`` under ``root``."""
    candidates = sorted(root.glob(pattern))
    return candidates[-1] if candidates else None


def _ensure_static_node(
    static_con: sqlite3.Connection,
    *,
    adg_name: str,
    resolved_path: str = "",
) -> int:
    """Look up or stub a node in the static snapshot's ``nodes`` table.

    Returns the node id. If the runtime evidence references a node not
    present in the static graph, we stub it with an empty resolved_path —
    this is the HIDDEN_PATH signal SSOTDecisionRecord needs.
    """
    row = static_con.execute("SELECT id FROM nodes WHERE adg_name = ?", (adg_name,)).fetchone()
    if row is not None:
        return int(row[0])
    # Stub the node. Static schema requires id (auto), adg_name, optionally resolved_path.
    cur = static_con.execute(
        "INSERT INTO nodes (adg_name, resolved_path) VALUES (?, ?)",
        (adg_name, resolved_path),
    )
    return int(cur.lastrowid or 0)


def _runtime_edge_exists(
    static_con: sqlite3.Connection,
    *,
    src_id: int,
    dst_id: int,
    relation_type: str,
    source_file: str,
    line_no: int,
) -> bool:
    """Idempotency check — return True if an equivalent runtime row exists."""
    row = static_con.execute(
        """
        SELECT 1 FROM edges
        WHERE src_id = ?
          AND dst_id = ?
          AND relation_type = ?
          AND source_file = ?
          AND line_no = ?
          AND authority = 'runtime_observed'
        LIMIT 1
        """,
        (src_id, dst_id, relation_type, source_file, line_no),
    ).fetchone()
    return row is not None


def _classify_runtime_edge(execution_context: str | None) -> tuple[str, str]:
    """Return (resolution_status, authority_status) for a runtime edge.

    Heuristic: ``execution_context`` carries trace/span ids when the trace
    is complete. Empty/missing trace context downgrades the edge.
    """
    if not execution_context or execution_context.strip() in ("", "{}", "null"):
        return ("MISSING_TRACE", "UNKNOWN_NOT_PROOF")
    try:
        ctx = json.loads(execution_context) if execution_context.startswith("{") else {}
    except (ValueError, TypeError):
        ctx = {}
    has_trace = bool(ctx.get("trace_id"))
    has_run = bool(ctx.get("run_id"))
    has_span = bool(ctx.get("span_id"))
    if has_trace and has_run and has_span:
        return ("VERIFIED_RUNTIME", "AUTHORITATIVE_RUNTIME")
    if has_trace or has_run:
        return ("PARTIAL_TRACE", "PARTIAL")
    return ("MISSING_TRACE", "UNKNOWN_NOT_PROOF")


def _build_evidence_refs(
    *,
    execution_context: str | None,
    timestamp: str | None,
    relation_type: str,
) -> str:
    """Build the JSON evidence_refs blob for a runtime edge."""
    ctx: dict[str, object] = {}
    if execution_context and execution_context.startswith("{"):
        try:
            ctx = json.loads(execution_context)
        except (ValueError, TypeError):
            ctx = {}
    blob = {
        "kind": "runtime",
        "run_id": ctx.get("run_id"),
        "trace_id": ctx.get("trace_id"),
        "span_id": ctx.get("span_id"),
        "timestamp": timestamp,
        "relation_type": relation_type,
    }
    return json.dumps(blob, separators=(",", ":"))


def lift(
    *,
    static_snapshot: Path,
    runtime_snapshot: Path,
    dry_run: bool = False,
) -> LiftStats:
    """Lift runtime edges from ``runtime_snapshot`` into ``static_snapshot``.

    Returns a :class:`LiftStats` summary. ``dry_run=True`` runs every
    classification step but rolls back the transaction.
    """
    stats = LiftStats()

    if not static_snapshot.exists():
        raise FileNotFoundError(f"static snapshot not found: {static_snapshot}")
    if not runtime_snapshot.exists():
        raise FileNotFoundError(f"runtime snapshot not found: {runtime_snapshot}")

    static_con = sqlite3.connect(static_snapshot)
    runtime_con = sqlite3.connect(runtime_snapshot)

    try:
        # Read every runtime edge with the joined node names (we need names
        # to look up node ids in the static graph).
        runtime_rows = runtime_con.execute(
            """
            SELECT
                src.adg_name AS src_name,
                dst.adg_name AS dst_name,
                e.relation_type,
                e.edge_kind,
                e.source_file,
                e.line_no,
                e.symbol,
                e.timestamp,
                e.execution_context
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            """
        ).fetchall()
        stats.runtime_edges_read = len(runtime_rows)

        for row in runtime_rows:
            src_name, dst_name, rel, kind, src_file, line_no, symbol, ts, exec_ctx = row
            if not src_name or not dst_name:
                stats.edges_skipped_invalid += 1
                continue

            src_id_before = static_con.execute(
                "SELECT id FROM nodes WHERE adg_name = ?", (src_name,)
            ).fetchone()
            dst_id_before = static_con.execute(
                "SELECT id FROM nodes WHERE adg_name = ?", (dst_name,)
            ).fetchone()

            src_id = _ensure_static_node(static_con, adg_name=src_name)
            dst_id = _ensure_static_node(static_con, adg_name=dst_name)
            if src_id_before is None:
                stats.nodes_stubbed += 1
            if dst_id_before is None:
                stats.nodes_stubbed += 1

            if _runtime_edge_exists(
                static_con,
                src_id=src_id,
                dst_id=dst_id,
                relation_type=rel,
                source_file=src_file or "",
                line_no=line_no or 0,
            ):
                stats.edges_skipped_duplicate += 1
                continue

            res_status, auth_status = _classify_runtime_edge(exec_ctx)
            evidence_refs = _build_evidence_refs(
                execution_context=exec_ctx,
                timestamp=ts,
                relation_type=rel,
            )

            static_con.execute(
                """
                INSERT INTO edges (
                    src_id, dst_id, relation_type, edge_kind,
                    source_file, line_no, symbol,
                    authority, bucket, resolution_status, authority_status, evidence_refs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'runtime_observed', 'runtime', ?, ?, ?)
                """,
                (
                    src_id,
                    dst_id,
                    rel,
                    kind or "RUNTIME_OBSERVED",
                    src_file or "",
                    line_no or 0,
                    symbol or "",
                    res_status,
                    auth_status,
                    evidence_refs,
                ),
            )
            stats.edges_inserted += 1

        if dry_run:
            static_con.rollback()
        else:
            static_con.commit()

    finally:
        static_con.close()
        runtime_con.close()

    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--static-snapshot",
        type=Path,
        default=None,
        help="Path to static ADG SQLite (default: latest under artifacts/adg/)",
    )
    parser.add_argument(
        "--runtime-snapshot",
        type=Path,
        default=None,
        help="Path to runtime ADG SQLite (default: latest under artifacts/runtime_adg/)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Roll back instead of committing")
    args = parser.parse_args(argv)

    static_snap = args.static_snapshot or _latest_snapshot(
        "adg_indexed_*.sqlite", REPO_ROOT / "artifacts" / "adg"
    )
    runtime_snap = args.runtime_snapshot or _latest_snapshot(
        "runtime_adg_*.sqlite", REPO_ROOT / "artifacts" / "runtime_adg"
    )

    if static_snap is None:
        print("[FATAL] no static ADG snapshot found", file=sys.stderr)
        return 2
    if runtime_snap is None:
        print(
            "[INFO] no runtime ADG snapshot found — runtime bucket remains empty (W2 deferred until "
            "a runtime ADG snapshot exists at artifacts/runtime_adg/runtime_adg_*.sqlite)",
            file=sys.stderr,
        )
        return 0

    print(f"[INFO] static snapshot:  {static_snap}")
    print(f"[INFO] runtime snapshot: {runtime_snap}")
    print(f"[INFO] dry_run={args.dry_run}")

    stats = lift(
        static_snapshot=static_snap,
        runtime_snapshot=runtime_snap,
        dry_run=args.dry_run,
    )

    print(f"[OK] runtime_edges_read     = {stats.runtime_edges_read}")
    print(f"[OK] nodes_stubbed          = {stats.nodes_stubbed}")
    print(f"[OK] edges_inserted         = {stats.edges_inserted}")
    print(f"[OK] edges_skipped_duplicate= {stats.edges_skipped_duplicate}")
    print(f"[OK] edges_skipped_invalid  = {stats.edges_skipped_invalid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
