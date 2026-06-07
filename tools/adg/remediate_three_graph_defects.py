#!/usr/bin/env python3
"""Remediate the three real defects surfaced by the ADG three-graph quick-strict suite.

Plan: ``docs/archive/windsurf/legacy-tree/plans/adg-three-graph-harness-e57cc7.md`` (W7 — defect remediation).

Defects targeted (from harness commit 8a0f78bdf7 baseline strict run)
-------------------------------------------------------------------

D1 — ``static.snapshot_has_mvs`` projection digest mismatch
   The most-recent ``adg_graph_<ts>.sqlite`` projection has a
   ``proj_meta.source_artifact_digest`` that does not equal the canonical
   snapshot's ``meta.artifact_digest``. The projection is stale because
   the canonical snapshot was re-emitted (registry-bucket-lift,
   schema graduation, snapshot signing) AFTER the last projection build.
   Fix: invoke ``tools/generate/graph_projection.py`` to rebuild the
   projection from the current canonical snapshot.

D2 — ``static.edge_authority_well_formed`` out-of-enum authority values
   Two new authority labels were introduced by ``tools/adg/registry_bucket_lift.py``:

       * ``static_canonical`` — emitted on the static-side twin of a
         consumer-edge (code references a registry concept). These rows
         ARE verified static references and should carry the in-enum
         label ``verified``.
       * ``registry_declared`` — emitted on declarations parsed from
         registry source files (mcp_config.json, agent_specs.yaml, etc.).
         These declarations were parsed and validated by the resolver
         and should also carry ``verified`` per the closed enum's
         semantics for "AST-resolved, well-formed declaration".

   The closed enum is fixed by SSOT
   (``agentic_core/adg/artifact/edge_authority.py:ALL_AUTHORITIES``):
   ``{verified, unresolved, dynamic, external, test_only, runtime_observed}``.
   Per-row classification (NOT mass-fill of NULLs):
       * ``static_canonical`` -> ``verified`` — well-formed code-side reference
       * ``registry_declared`` -> ``verified`` — well-formed declaration
   No NULL-authority rows exist on this snapshot, so the constraint
   "Do not mass-fill NULL authority as verified" is preserved.

D3 — ``cross_bucket.impossible_states`` I3 (29 static edges with NULL source_file)
   Edges with ``relation_type='violation_propagates_through'`` are emitted
   by ``agentic_core/adg/extraction/static_scanner.py:_propagate_violations``
   as a DERIVED enrichment (computed from the static import graph). They
   carry no source_file because they describe a propagation relationship,
   not an AST-extracted code reference. The I3 invariant explicitly
   exempts ``dynamic_resolution IN ('synthetic','derived','external')``
   for exactly this case. Fix: stamp ``dynamic_resolution='derived'`` on
   every violation-propagation edge.

Idempotency
-----------
* D1: ``graph_projection.build_graph_projection()`` overwrites the output
  file; safe to re-run.
* D2: The UPDATE clause is a label rename; once executed, subsequent runs
  are no-ops because no rows match the old labels.
* D3: SET dynamic_resolution='derived' is idempotent.

Usage
-----
    python tools/adg/remediate_three_graph_defects.py            # apply all 3
    python tools/adg/remediate_three_graph_defects.py --dry-run  # report only
    python tools/adg/remediate_three_graph_defects.py --skip-projection  # skip D1

The tool prints structured before/after counts to stdout AND writes a
JSON report at ``docs/reports/adg/three_graph_defect_remediation.json``.
"""

from __future__ import annotations

# Reads + UPDATEs the snapshot directly. Proof-grade because the verdict
# (every row is correctly classified post-run) is enforcement evidence.
__adg_consumer_mode__ = "proof"

import argparse
import glob
import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "adg"
REPORT_PATH = REPO_ROOT / "docs" / "reports" / "adg" / "three_graph_defect_remediation.json"
PROJECTION_BUILDER = REPO_ROOT / "tools" / "generate" / "graph_projection.py"


@dataclass
class DefectMetric:
    name: str
    before: int = 0
    after: int = 0
    fix_applied: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass
class RemediationReport:
    timestamp_utc: str = ""
    snapshot: str = ""
    canonical_artifact_digest: str = ""
    dry_run: bool = False
    d1_projection_digest: dict = field(default_factory=dict)
    d2_authority_enum: dict = field(default_factory=dict)
    d3_impossible_states_i3: dict = field(default_factory=dict)
    overall_status: str = "PENDING"


def _latest_snapshot() -> Path | None:
    if not ARTIFACT_DIR.exists():
        return None
    snaps = sorted(ARTIFACT_DIR.glob("adg_indexed_*.sqlite"))
    return snaps[-1] if snaps else None


def _latest_projection() -> Path | None:
    files = sorted(
        f for f in ARTIFACT_DIR.glob("adg_graph_*.sqlite")
        if not f.name.endswith(".tmp")
    )
    return files[-1] if files else None


def _short(s: str | None) -> str:
    return (s or "")[:24]


# ---------------------------------------------------------------------------
# D1 — projection digest
# ---------------------------------------------------------------------------


def remediate_projection_digest(
    snapshot: Path, *, dry_run: bool
) -> dict[str, Any]:
    canon_con = sqlite3.connect(str(snapshot))
    try:
        row = canon_con.execute(
            "SELECT value FROM meta WHERE key='artifact_digest'"
        ).fetchone()
        canonical_digest = row[0] if row else ""
    finally:
        canon_con.close()

    out: dict[str, Any] = {
        "canonical_digest": _short(canonical_digest),
        "before_projection": "<none>",
        "before_projection_digest": "<none>",
        "before_match": False,
        "after_projection": "<none>",
        "after_projection_digest": "<none>",
        "after_match": False,
        "fix_applied": False,
        "rebuild_log_tail": "",
        "rebuild_exit_code": -1,
    }

    proj_before = _latest_projection()
    if proj_before is not None:
        out["before_projection"] = proj_before.name
        try:
            pcon = sqlite3.connect(str(proj_before))
            try:
                pr = pcon.execute(
                    "SELECT value FROM proj_meta WHERE key='source_artifact_digest'"
                ).fetchone()
                proj_digest = pr[0] if pr else ""
            finally:
                pcon.close()
            out["before_projection_digest"] = _short(proj_digest)
            out["before_match"] = (proj_digest == canonical_digest and bool(canonical_digest))
        except sqlite3.Error as exc:
            out["before_projection_digest"] = f"<read_error:{exc}>"

    if out["before_match"]:
        out["fix_applied"] = False
        return out  # already fresh — no-op

    if dry_run:
        return out

    # Derive timestamp suffix from canonical filename: adg_indexed_<ts>.sqlite
    ts = snapshot.stem.replace("adg_indexed_", "")
    cmd = [
        sys.executable, str(PROJECTION_BUILDER),
        str(snapshot), "--out-dir", str(ARTIFACT_DIR), "--ts", ts,
    ]
    proc = subprocess.run(  # noqa: S603 — args fully constructed
        cmd, cwd=str(REPO_ROOT), capture_output=True, text=True,
        timeout=300, check=False,
    )
    out["rebuild_exit_code"] = proc.returncode
    out["rebuild_log_tail"] = (proc.stdout or proc.stderr or "")[-400:]
    if proc.returncode != 0:
        return out

    # Re-read the new projection's digest.
    proj_after = _latest_projection()
    if proj_after is not None:
        out["after_projection"] = proj_after.name
        try:
            pcon = sqlite3.connect(str(proj_after))
            try:
                pr = pcon.execute(
                    "SELECT value FROM proj_meta WHERE key='source_artifact_digest'"
                ).fetchone()
                proj_digest = pr[0] if pr else ""
            finally:
                pcon.close()
            out["after_projection_digest"] = _short(proj_digest)
            out["after_match"] = (proj_digest == canonical_digest)
            out["fix_applied"] = out["after_match"]
        except sqlite3.Error as exc:
            out["after_projection_digest"] = f"<read_error:{exc}>"
    return out


# ---------------------------------------------------------------------------
# D2 — authority enum migration
# ---------------------------------------------------------------------------


# Per-row classification map. Both labels migrate to ``verified`` because:
#   * ``static_canonical`` rows are AST-resolved code references emitted by
#     the consumer-edge resolver;
#   * ``registry_declared`` rows are well-formed declarations parsed and
#     validated by the registry resolver.
# Both have AUTHORITATIVE-tier semantics; ``verified`` is the in-enum
# equivalent. The migration is per-row label rename, NOT a NULL fill.
AUTHORITY_MIGRATIONS: dict[str, str] = {
    "static_canonical": "verified",
    "registry_declared": "verified",
}

CLOSED_AUTHORITY_ENUM: frozenset[str] = frozenset(
    {"verified", "unresolved", "dynamic", "external", "test_only", "runtime_observed"}
)


def remediate_authority_enum(
    snapshot: Path, *, dry_run: bool
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "before_distribution": {},
        "out_of_enum_before": {},
        "null_authority_before": 0,
        "migrations_applied": {},
        "after_distribution": {},
        "out_of_enum_after": {},
        "null_authority_after": 0,
        "fix_applied": False,
    }
    con = sqlite3.connect(str(snapshot))
    try:
        before_dist = dict(
            con.execute(
                "SELECT COALESCE(authority,'<NULL>'), COUNT(*) FROM edges GROUP BY authority"
            ).fetchall()
        )
        out["before_distribution"] = before_dist
        out["null_authority_before"] = before_dist.get("<NULL>", 0)
        out["out_of_enum_before"] = {
            label: n
            for label, n in before_dist.items()
            if label != "<NULL>" and label not in CLOSED_AUTHORITY_ENUM
        }
        if dry_run:
            return out

        con.execute("BEGIN")
        applied: dict[str, int] = {}
        for old_label, new_label in AUTHORITY_MIGRATIONS.items():
            cur = con.execute(
                "UPDATE edges SET authority=? WHERE authority=?",
                (new_label, old_label),
            )
            applied[f"{old_label}->{new_label}"] = cur.rowcount
        con.commit()

        out["migrations_applied"] = applied
        after_dist = dict(
            con.execute(
                "SELECT COALESCE(authority,'<NULL>'), COUNT(*) FROM edges GROUP BY authority"
            ).fetchall()
        )
        out["after_distribution"] = after_dist
        out["null_authority_after"] = after_dist.get("<NULL>", 0)
        out["out_of_enum_after"] = {
            label: n
            for label, n in after_dist.items()
            if label != "<NULL>" and label not in CLOSED_AUTHORITY_ENUM
        }
        out["fix_applied"] = (
            sum(applied.values()) > 0
            and not out["out_of_enum_after"]
        )
    finally:
        con.close()
    return out


# ---------------------------------------------------------------------------
# D3 — I3 violation_propagates_through
# ---------------------------------------------------------------------------


def remediate_i3_propagation_edges(
    snapshot: Path, *, dry_run: bool
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "before_violators": 0,
        "rows_updated": 0,
        "after_violators": 0,
        "fix_applied": False,
    }
    con = sqlite3.connect(str(snapshot))
    try:
        violator_sql = """
            SELECT COUNT(*) FROM edges
             WHERE bucket='static'
               AND (source_file IS NULL OR source_file = '')
               AND COALESCE(dynamic_resolution,'') NOT IN ('synthetic','derived','external')
            """
        out["before_violators"] = con.execute(violator_sql).fetchone()[0]
        if dry_run:
            return out

        # Stamp 'derived' on the propagation edges. Scope is intentionally
        # narrow: only rows that match the I3 violator pattern AND have the
        # known propagation relation_type.
        con.execute("BEGIN")
        cur = con.execute(
            """
            UPDATE edges
               SET dynamic_resolution='derived'
             WHERE relation_type='violation_propagates_through'
               AND bucket='static'
               AND (source_file IS NULL OR source_file = '')
               AND COALESCE(dynamic_resolution,'') NOT IN ('synthetic','derived','external')
            """
        )
        out["rows_updated"] = cur.rowcount
        con.commit()
        out["after_violators"] = con.execute(violator_sql).fetchone()[0]
        out["fix_applied"] = out["after_violators"] == 0
    finally:
        con.close()
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report before-counts only; apply no fixes.",
    )
    parser.add_argument(
        "--skip-projection",
        action="store_true",
        help="Skip D1 (projection rebuild). Useful for testing D2/D3 alone.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=REPORT_PATH,
        help=f"Path for JSON report (default: {REPORT_PATH})",
    )
    args = parser.parse_args(argv)

    snapshot = args.snapshot or _latest_snapshot()
    if snapshot is None:
        print("[remediate] ERROR: no snapshot found in artifacts/adg/")
        return 2

    started = datetime.now(timezone.utc)
    canon_con = sqlite3.connect(str(snapshot))
    try:
        canon_digest = canon_con.execute(
            "SELECT value FROM meta WHERE key='artifact_digest'"
        ).fetchone()
        canon_digest = canon_digest[0] if canon_digest else ""
    finally:
        canon_con.close()

    print(f"[remediate] snapshot                   = {snapshot.name}")
    print(f"[remediate] canonical artifact_digest  = {_short(canon_digest)}...")
    print(f"[remediate] dry_run                    = {args.dry_run}")
    print()

    # D2 first (in-snapshot UPDATE), then D3 (in-snapshot UPDATE), then D1
    # (rebuild projection from the post-fix snapshot). If we did D1 first,
    # the projection would hash the pre-fix snapshot.
    print("--- D2: edge authority enum migration ---")
    d2 = remediate_authority_enum(snapshot, dry_run=args.dry_run)
    print(f"  out-of-enum before   : {d2['out_of_enum_before']}")
    print(f"  migrations applied   : {d2['migrations_applied']}")
    print(f"  out-of-enum after    : {d2['out_of_enum_after']}")
    print(f"  null-authority before: {d2['null_authority_before']}")
    print(f"  null-authority after : {d2['null_authority_after']}")
    print(f"  fix_applied          : {d2['fix_applied']}")
    print()

    print("--- D3: I3 violation_propagates_through dynamic_resolution ---")
    d3 = remediate_i3_propagation_edges(snapshot, dry_run=args.dry_run)
    print(f"  I3 violators before  : {d3['before_violators']}")
    print(f"  rows updated         : {d3['rows_updated']}")
    print(f"  I3 violators after   : {d3['after_violators']}")
    print(f"  fix_applied          : {d3['fix_applied']}")
    print()

    if args.skip_projection:
        d1 = {"fix_applied": False, "skipped": True}
        print("--- D1: projection rebuild SKIPPED ---")
    else:
        print("--- D1: graph projection rebuild ---")
        d1 = remediate_projection_digest(snapshot, dry_run=args.dry_run)
        print(f"  before projection    : {d1['before_projection']}")
        print(f"  before digest        : {d1['before_projection_digest']}")
        print(f"  before match         : {d1['before_match']}")
        print(f"  after projection     : {d1['after_projection']}")
        print(f"  after digest         : {d1['after_projection_digest']}")
        print(f"  after match          : {d1['after_match']}")
        print(f"  fix_applied          : {d1['fix_applied']}")
    print()

    overall = "OK"
    if not args.dry_run:
        if not d2["fix_applied"] and d2["out_of_enum_before"]:
            overall = "PARTIAL"
        if not d3["fix_applied"] and d3["before_violators"]:
            overall = "PARTIAL"
        if not args.skip_projection and not d1.get("fix_applied") and not d1.get("before_match"):
            overall = "PARTIAL"

    report = RemediationReport(
        timestamp_utc=started.isoformat(),
        snapshot=snapshot.name,
        canonical_artifact_digest=canon_digest,
        dry_run=args.dry_run,
        d1_projection_digest=d1,
        d2_authority_enum=d2,
        d3_impossible_states_i3=d3,
        overall_status=overall,
    )

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    print(f"[remediate] JSON report = {args.json_out.relative_to(REPO_ROOT) if args.json_out.is_absolute() else args.json_out}")
    print(f"[remediate] overall      = {overall}")

    return 0 if overall == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
