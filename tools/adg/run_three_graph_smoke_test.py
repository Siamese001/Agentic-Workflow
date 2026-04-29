"""Three-graph smoke test runner — validate the full ADG bucket pipeline.

Exercises and asserts the end-to-end health of the three-bucket authority
model in one script. Useful for:

  * Local sanity check after generating a fresh ADG snapshot
  * Regression guard for plan three-bucket-gap-remediation-069806
  * Operator probe that surfaces TRIPLET / DEAD_PATH / DRIFT counts at a glance

What this runs:

  1. Static graph    — count edges in the static bucket
  2. Registry graph  — verify registry resolvers + consumer resolvers fired
  3. Runtime graph   — verify v_runtime_proof has fresh attestations
  4. Gap report      — classify edges across all 7 defect classes
  5. Health checks   — assert thresholds:
                          TRIPLET_ATTESTED ≥ floor (default: 1)
                          SHADOW_CHANNEL == 0 (P1 — never tolerated)
                          REGISTRY_DRIFT% ≤ ceiling (default: 5%)
                          CONFIG_BLOAT% ≤ ceiling (default: 1%)

When ``--top-up`` is set, the script seeds additional triplet-eligible
synthetic traces (`--prefer-registry-overlap`) and rebuilds v_runtime_proof
before running the gap classifier — useful for refreshing the runtime view
after the static snapshot has been regenerated.

Usage::

    # Read-only sanity check
    python tools/adg/run_three_graph_smoke_test.py

    # Refresh runtime view first, then check
    python tools/adg/run_three_graph_smoke_test.py --top-up --traces 100

    # Custom thresholds
    python tools/adg/run_three_graph_smoke_test.py --triplet-floor 200

Exit codes:
  0  — all checks passed
  1  — one or more checks failed (see report)
  2  — snapshot missing or schema invalid
"""

from __future__ import annotations

# Read-only: queries edges, v_runtime_proof, mv_*. Does not write to
# canonical static tables. The optional --top-up path writes synthetic
# traces to the runtime store (NOT to static edges) and rebuilds the
# v_runtime_proof view.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR: Final[Path] = REPO_ROOT / "artifacts" / "adg"
DEFAULT_REPORT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "three_graph_smoke_test.json"
)

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass
class GraphCounts:
    static_edges: int = 0
    registry_edges: int = 0
    runtime_attested_rows: int = 0


@dataclass
class GapDistribution:
    triplet_attested: int = 0
    registry_drift: int = 0
    dead_path: int = 0
    unobserved_code: int = 0
    dynamic_dispatch: int = 0
    shadow_channel: int = 0
    config_bloat: int = 0
    total: int = 0

    def pct(self, n: int) -> float:
        return (n / self.total * 100.0) if self.total else 0.0


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass
class SmokeTestReport:
    snapshot: str = ""
    snapshot_size_bytes: int = 0
    counts: GraphCounts = field(default_factory=GraphCounts)
    gap: GapDistribution = field(default_factory=GapDistribution)
    checks: list[CheckResult] = field(default_factory=list)
    top_up_applied: bool = False
    top_up_traces_added: int = 0
    timestamp_utc: str = ""

    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _latest_snapshot() -> Path | None:
    snaps = sorted(ARTIFACTS_DIR.glob("adg_indexed_*.sqlite"))
    return snaps[-1] if snaps else None


def _classify_query(con: sqlite3.Connection) -> str:
    """Mirror tools/adg/three_bucket_gap_report.py classify SQL."""
    has_runtime = (
        con.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type IN ('table','view') AND name='v_runtime_proof'"
        ).fetchone()
        is not None
    )

    # bucket col
    cols = [r[1] for r in con.execute("PRAGMA table_info(edges)").fetchall()]
    bucket_col = next(
        (c for c in ("bucket", "graph_bucket", "authority_bucket") if c in cols),
        None,
    )
    if bucket_col:
        bucket_expr = f"e.{bucket_col}"
    else:
        bucket_expr = (
            "CASE "
            "WHEN authority IN ('verified','unresolved','dynamic','external','test_only') THEN 'static' "
            "WHEN authority IN ('runtime_observed') THEN 'runtime' "
            "WHEN authority IN ('registry') THEN 'registry' "
            "ELSE 'static' END"
        )

    runtime_join = ""
    runtime_present_col = "0 AS in_runtime"
    if has_runtime:
        runtime_join = (
            "LEFT JOIN ("
            "  SELECT static_edge_id, 1 AS rt FROM v_runtime_proof "
            "  WHERE attesting_trace_count >= 1 AND static_edge_id IS NOT NULL"
            ") rt ON rt.static_edge_id = e.id "
        )
        runtime_present_col = "MAX(COALESCE(rt.rt,0)) AS in_runtime"

    return f"""
    WITH per_edge AS (
        SELECT
            e.src_id, e.dst_id, e.relation_type,
            MAX(CASE WHEN {bucket_expr} = 'static'   THEN 1 ELSE 0 END) AS in_static,
            MAX(CASE WHEN {bucket_expr} = 'registry' THEN 1 ELSE 0 END) AS in_registry,
            {runtime_present_col}
        FROM edges e
        {runtime_join}
        GROUP BY e.src_id, e.dst_id, e.relation_type
    )
    SELECT
        CASE
            WHEN in_static=1 AND in_runtime=1 AND in_registry=1 THEN 'TRIPLET_ATTESTED'
            WHEN in_static=1 AND in_runtime=1 AND in_registry=0 THEN 'REGISTRY_DRIFT'
            WHEN in_static=1 AND in_runtime=0 AND in_registry=1 THEN 'DEAD_PATH'
            WHEN in_static=1 AND in_runtime=0 AND in_registry=0 THEN 'UNOBSERVED_CODE'
            WHEN in_static=0 AND in_runtime=1 AND in_registry=1 THEN 'DYNAMIC_DISPATCH'
            WHEN in_static=0 AND in_runtime=1 AND in_registry=0 THEN 'SHADOW_CHANNEL'
            WHEN in_static=0 AND in_runtime=0 AND in_registry=1 THEN 'CONFIG_BLOAT'
        END AS defect_class,
        COUNT(*) AS n
    FROM per_edge
    GROUP BY defect_class
    """


# ---------------------------------------------------------------------------
# Probe phases
# ---------------------------------------------------------------------------


def probe_counts(con: sqlite3.Connection) -> GraphCounts:
    counts = GraphCounts()
    counts.static_edges = con.execute(
        "SELECT COUNT(*) FROM edges WHERE bucket='static'"
    ).fetchone()[0]
    counts.registry_edges = con.execute(
        "SELECT COUNT(*) FROM edges WHERE bucket='registry'"
    ).fetchone()[0]
    has_runtime = (
        con.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type IN ('table','view') AND name='v_runtime_proof'"
        ).fetchone()
        is not None
    )
    if has_runtime:
        counts.runtime_attested_rows = con.execute(
            "SELECT COUNT(*) FROM v_runtime_proof "
            "WHERE attesting_trace_count >= 1"
        ).fetchone()[0]
    return counts


def probe_gap_distribution(con: sqlite3.Connection) -> GapDistribution:
    gap = GapDistribution()
    rows = con.execute(_classify_query(con)).fetchall()
    name_map = {
        "TRIPLET_ATTESTED": "triplet_attested",
        "REGISTRY_DRIFT": "registry_drift",
        "DEAD_PATH": "dead_path",
        "UNOBSERVED_CODE": "unobserved_code",
        "DYNAMIC_DISPATCH": "dynamic_dispatch",
        "SHADOW_CHANNEL": "shadow_channel",
        "CONFIG_BLOAT": "config_bloat",
    }
    for cls_name, n in rows:
        attr = name_map.get(cls_name)
        if attr:
            setattr(gap, attr, int(n))
        gap.total += int(n)
    return gap


# ---------------------------------------------------------------------------
# Optional top-up — re-seed runtime traces and rebuild v_runtime_proof
# ---------------------------------------------------------------------------


def top_up_runtime(
    snapshot: Path,
    *,
    traces: int,
    edges_per_trace: int,
    seed: int,
    use_real_otel: bool = False,
) -> int:
    """Seed N triplet-eligible traces and rebuild v_runtime_proof.

    When ``use_real_otel`` is True, drives the production W3-migrated
    emitter exerciser at ``tools.otel.exercise_real_otel_pipeline`` —
    spans flow through the same ingest helper used by ``heal_router_otel``,
    ``consensus_otel``, and ``runtime_span_emitter`` in production.

    Otherwise falls back to the synthetic seeder.

    Returns number of trace snapshots persisted.
    """
    from tools.otel.runtime_view_builder import build_runtime_view  # noqa: WPS433

    if use_real_otel:
        from tools.otel.exercise_real_otel_pipeline import run as run_real  # noqa: WPS433

        rstats = run_real(
            snapshot=snapshot,
            skip_emitters=False,
            skip_consumer_aligned=False,
            n_traces=traces,
            edges_per_trace=edges_per_trace,
            rebuild=False,  # we rebuild below for parity with synthetic path
        )
        persisted = rstats.consumer_edge_snapshots_persisted + sum(
            r.spans_persisted for r in rstats.emitter_results
        )
    else:
        from tools.otel.seed_synthetic_traces import seed as seed_traces  # noqa: WPS433

        stats = seed_traces(
            n_traces=traces,
            edges_per_trace=edges_per_trace,
            snapshot=snapshot,
            seed=seed,
            prefer_registry_overlap=True,
        )
        persisted = stats.snapshots_persisted

    # Rebuild v_runtime_proof from scratch so the gap classifier sees the
    # latest attestations. Idempotent — safe even if v_runtime_proof had
    # rows already.
    con = sqlite3.connect(str(snapshot))
    try:
        con.execute("DELETE FROM v_runtime_proof")
        con.commit()
    finally:
        con.close()
    build_runtime_view(snapshot, fail_soft=False)

    return persisted


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------


def run_checks(
    counts: GraphCounts,
    gap: GapDistribution,
    *,
    triplet_floor: int,
    drift_pct_ceiling: float,
    bloat_pct_ceiling: float,
) -> list[CheckResult]:
    checks: list[CheckResult] = []

    # 1. All three graphs must have non-zero attestations.
    checks.append(
        CheckResult(
            name="static_graph_non_empty",
            passed=counts.static_edges > 0,
            detail=f"static_edges={counts.static_edges}",
        )
    )
    checks.append(
        CheckResult(
            name="registry_graph_non_empty",
            passed=counts.registry_edges > 0,
            detail=f"registry_edges={counts.registry_edges}",
        )
    )
    checks.append(
        CheckResult(
            name="runtime_graph_non_empty",
            passed=counts.runtime_attested_rows > 0,
            detail=f"runtime_attested_rows={counts.runtime_attested_rows}",
        )
    )

    # 2. P1 SHADOW_CHANNEL must be exactly zero (security-critical).
    checks.append(
        CheckResult(
            name="shadow_channel_zero",
            passed=gap.shadow_channel == 0,
            detail=f"shadow_channel={gap.shadow_channel} (must be 0 — P1)",
        )
    )

    # 3. TRIPLET_ATTESTED must clear the floor.
    checks.append(
        CheckResult(
            name="triplet_floor",
            passed=gap.triplet_attested >= triplet_floor,
            detail=(
                f"triplet_attested={gap.triplet_attested} "
                f"floor={triplet_floor}"
            ),
        )
    )

    # 4. REGISTRY_DRIFT% must be at or below the ceiling.
    drift_pct = gap.pct(gap.registry_drift)
    checks.append(
        CheckResult(
            name="registry_drift_pct_ceiling",
            passed=drift_pct <= drift_pct_ceiling,
            detail=(
                f"registry_drift_pct={drift_pct:.2f} "
                f"ceiling={drift_pct_ceiling}"
            ),
        )
    )

    # 5. CONFIG_BLOAT% must be at or below the ceiling.
    bloat_pct = gap.pct(gap.config_bloat)
    checks.append(
        CheckResult(
            name="config_bloat_pct_ceiling",
            passed=bloat_pct <= bloat_pct_ceiling,
            detail=(
                f"config_bloat_pct={bloat_pct:.2f} "
                f"ceiling={bloat_pct_ceiling}"
            ),
        )
    )

    return checks


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_report(report: SmokeTestReport) -> None:
    print(f"[smoke] snapshot              = {report.snapshot}")
    print(f"[smoke] timestamp_utc         = {report.timestamp_utc}")
    print(f"[smoke] static_edges          = {report.counts.static_edges}")
    print(f"[smoke] registry_edges        = {report.counts.registry_edges}")
    print(f"[smoke] runtime_attested      = {report.counts.runtime_attested_rows}")
    if report.top_up_applied:
        print(f"[smoke] top_up_traces_added   = {report.top_up_traces_added}")
    print("[smoke] gap distribution:")
    g = report.gap
    print(f"          TRIPLET_ATTESTED      {g.triplet_attested:>7d}  ({g.pct(g.triplet_attested):>5.2f}%)")
    print(f"          REGISTRY_DRIFT  [P2]  {g.registry_drift:>7d}  ({g.pct(g.registry_drift):>5.2f}%)")
    print(f"          DEAD_PATH       [P3]  {g.dead_path:>7d}  ({g.pct(g.dead_path):>5.2f}%)")
    print(f"          UNOBSERVED_CODE [P3]  {g.unobserved_code:>7d}  ({g.pct(g.unobserved_code):>5.2f}%)")
    print(f"          DYNAMIC_DISPATCH[P5]  {g.dynamic_dispatch:>7d}  ({g.pct(g.dynamic_dispatch):>5.2f}%)")
    print(f"          SHADOW_CHANNEL  [P1]  {g.shadow_channel:>7d}  ({g.pct(g.shadow_channel):>5.2f}%)")
    print(f"          CONFIG_BLOAT    [P4]  {g.config_bloat:>7d}  ({g.pct(g.config_bloat):>5.2f}%)")
    print("[smoke] checks:")
    for c in report.checks:
        marker = "PASS" if c.passed else "FAIL"
        print(f"          [{marker}] {c.name:32s} -- {c.detail}")
    overall = "PASS" if report.all_passed() else "FAIL"
    print(f"[smoke] overall = {overall}")


def write_report_json(report: SmokeTestReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "snapshot": report.snapshot,
        "snapshot_size_bytes": report.snapshot_size_bytes,
        "timestamp_utc": report.timestamp_utc,
        "counts": {
            "static_edges": report.counts.static_edges,
            "registry_edges": report.counts.registry_edges,
            "runtime_attested_rows": report.counts.runtime_attested_rows,
        },
        "gap_distribution": {
            "triplet_attested": report.gap.triplet_attested,
            "registry_drift": report.gap.registry_drift,
            "dead_path": report.gap.dead_path,
            "unobserved_code": report.gap.unobserved_code,
            "dynamic_dispatch": report.gap.dynamic_dispatch,
            "shadow_channel": report.gap.shadow_channel,
            "config_bloat": report.gap.config_bloat,
            "total": report.gap.total,
        },
        "top_up": {
            "applied": report.top_up_applied,
            "traces_added": report.top_up_traces_added,
        },
        "checks": [
            {"name": c.name, "passed": c.passed, "detail": c.detail}
            for c in report.checks
        ],
        "overall_passed": report.all_passed(),
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run(
    *,
    snapshot: Path | None = None,
    top_up: bool = False,
    traces: int = 100,
    edges_per_trace: int = 5,
    seed: int = 42,
    use_real_otel: bool = False,
    triplet_floor: int = 1,
    drift_pct_ceiling: float = 5.0,
    bloat_pct_ceiling: float = 1.0,
    report_path: Path | None = None,
) -> SmokeTestReport:
    snap = snapshot or _latest_snapshot()
    if snap is None or not snap.exists():
        report = SmokeTestReport(timestamp_utc=datetime.now(timezone.utc).isoformat())
        report.checks.append(
            CheckResult(name="snapshot_exists", passed=False, detail="no snapshot")
        )
        return report

    report = SmokeTestReport()
    report.snapshot = snap.name
    try:
        report.snapshot_size_bytes = snap.stat().st_size
    except OSError:
        pass
    report.timestamp_utc = datetime.now(timezone.utc).isoformat()

    if top_up:
        report.top_up_traces_added = top_up_runtime(
            snap,
            traces=traces,
            edges_per_trace=edges_per_trace,
            seed=seed,
            use_real_otel=use_real_otel,
        )
        report.top_up_applied = True

    con = sqlite3.connect(str(snap))
    try:
        report.counts = probe_counts(con)
        report.gap = probe_gap_distribution(con)
    finally:
        con.close()

    report.checks = run_checks(
        report.counts,
        report.gap,
        triplet_floor=triplet_floor,
        drift_pct_ceiling=drift_pct_ceiling,
        bloat_pct_ceiling=bloat_pct_ceiling,
    )

    if report_path is not None:
        write_report_json(report, report_path)

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument(
        "--top-up",
        action="store_true",
        help="Seed triplet-eligible synthetic traces and rebuild v_runtime_proof first",
    )
    parser.add_argument("--traces", type=int, default=100)
    parser.add_argument("--edges-per-trace", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--use-real-otel",
        action="store_true",
        help=(
            "When --top-up is set, drive the production W3-migrated emitter "
            "exerciser instead of the synthetic seeder. Spans flow through "
            "emit_spans_to_runtime_adg — the same ingest helper used by "
            "heal_router_otel / consensus_otel / runtime_span_emitter."
        ),
    )
    parser.add_argument(
        "--triplet-floor",
        type=int,
        default=1,
        help="Minimum acceptable TRIPLET_ATTESTED count",
    )
    parser.add_argument(
        "--drift-pct-ceiling",
        type=float,
        default=5.0,
        help="Maximum acceptable REGISTRY_DRIFT percentage of total",
    )
    parser.add_argument(
        "--bloat-pct-ceiling",
        type=float,
        default=1.0,
        help="Maximum acceptable CONFIG_BLOAT percentage of total",
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path to write JSON report (default: docs/reports/adg/three_graph_smoke_test.json)",
    )
    args = parser.parse_args(argv)

    report = run(
        snapshot=args.snapshot,
        top_up=args.top_up,
        traces=args.traces,
        edges_per_trace=args.edges_per_trace,
        seed=args.seed,
        use_real_otel=args.use_real_otel,
        triplet_floor=args.triplet_floor,
        drift_pct_ceiling=args.drift_pct_ceiling,
        bloat_pct_ceiling=args.bloat_pct_ceiling,
        report_path=args.report_out,
    )
    print_report(report)

    if not report.snapshot:
        return 2
    return 0 if report.all_passed() else 1


if __name__ == "__main__":
    sys.exit(main())
