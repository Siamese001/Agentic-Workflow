"""Runtime-spine materialized views — thin reader layer.

The witness tier computation lives in the official ADG materialized-view pipeline:
  tools/generate/materialized_views/phase_a_path_authority.py
  → table: mv_handoff_witness_tiers  (Family 12, Phase A)

This module is a THIN READER that:
  1. Reads pre-computed rows from ``mv_handoff_witness_tiers`` in the ADG SQLite.
  2. Reconstructs the six ``ViewResult`` objects (grouped by ``view_name`` column).
  3. Formats and reports witness tier breakdowns.
  4. Runs semantic satisfaction check (same failure condition as before).

Tier semantics (authoritative definition in phase_a_path_authority.py):
  plumbing / bootstrap  — graph_persister.py + lifecycle_trace_contract.py
  test                  — tests/* prefix
  live_runtime          — all other production-code edges

Semantic failure condition:
  extraction_wired = True  AND
  (plumbing_wired OR test_covered) = True  AND
  live_runtime_present = False

Six runtime-spine views (reconstructed from mv_handoff_witness_tiers.view_name):
  mv_ingress_before_anything
  mv_l1_plan_before_route
  mv_retrieval_evidence_handoff
  mv_evidence_to_prompt_handoff
  mv_governed_execution_envelope_continuity
  mv_runtime_exit_continuity
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import glob
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR


# ── Data structures (same external interface as before) ───────────────────────


@dataclass
class WitnessRow:
    """Witness tier counts for one relation_type."""

    relation_type: str
    plumbing_witness_count: int = 0
    test_witness_count: int = 0
    live_runtime_witness_count: int = 0

    @property
    def zero_witness_count(self) -> int:
        """1 if no witnesses exist in any tier; 0 otherwise."""
        total = self.plumbing_witness_count + self.test_witness_count + self.live_runtime_witness_count
        return 1 if total == 0 else 0

    @property
    def extraction_wired(self) -> bool:
        return (self.plumbing_witness_count + self.test_witness_count + self.live_runtime_witness_count) > 0

    @property
    def plumbing_wired(self) -> bool:
        return self.plumbing_witness_count > 0

    @property
    def test_covered(self) -> bool:
        return self.test_witness_count > 0

    @property
    def live_runtime_present(self) -> bool:
        return self.live_runtime_witness_count > 0

    @property
    def built_plus_test_or_plumbing_covered_plus_runtime_orphaned(self) -> bool:
        """(plumbing_wired OR test_covered) AND NOT live_runtime_present."""
        return (self.plumbing_wired or self.test_covered) and not self.live_runtime_present

    @property
    def runtime_orphaned(self) -> bool:
        """Semantic failure: wired + covered but no live runtime path."""
        return (
            self.extraction_wired
            and (self.plumbing_wired or self.test_covered)
            and not self.live_runtime_present
        )


@dataclass
class ViewResult:
    """Output of one mv_* view."""

    name: str
    description: str
    rows: list[WitnessRow] = field(default_factory=list)

    @property
    def runtime_orphaned_rows(self) -> list[WitnessRow]:
        return [r for r in self.rows if r.runtime_orphaned]

    @property
    def zero_witnessed_rows(self) -> list[WitnessRow]:
        return [r for r in self.rows if r.zero_witness_count > 0]


@dataclass
class CrossCuttingFamilyResult:
    """Aggregated witness-tier counts for one cross-cutting family."""

    family_name: str
    relation_count: int
    plumbing_total: int
    test_total: int
    live_rt_total: int
    orphaned_count: int
    zero_count: int

    @property
    def runtime_orphaned(self) -> bool:
        """True if any relation in this family is runtime-orphaned."""
        return self.orphaned_count > 0


# ── View metadata (descriptions only — computation is in phase_a_path_authority) ──

_VIEW_DESCRIPTIONS: dict[str, str] = {
    "mv_ingress_before_anything": (
        "L0->L1 ingress gate: request must be validated before any planning starts"
    ),
    "mv_l1_plan_before_route": ("L1->L3 ordering gate: plan must exist before route selection"),
    "mv_retrieval_evidence_handoff": (
        "L1->L2 retrieval gate: scope pre-filter before evidence contract production"
    ),
    "mv_evidence_to_prompt_handoff": (
        "L2->L3 prompt gate: evidence must be sealed into prompt envelope before execution"
    ),
    "mv_governed_execution_envelope_continuity": (
        "GovernedExecutionEnvelope: execution packet stamped, "
        "policy/replay keys propagated, surface published, future runs promoted"
    ),
    "mv_runtime_exit_continuity": (
        "ExitHitlEnvelope + CommitUwgEnvelope: "
        "result sealed, exit chosen, HITL cleared, blast radius verified, UWG committed"
    ),
}

_VIEW_ORDER = [
    "mv_ingress_before_anything",
    "mv_l1_plan_before_route",
    "mv_retrieval_evidence_handoff",
    "mv_evidence_to_prompt_handoff",
    "mv_governed_execution_envelope_continuity",
    "mv_runtime_exit_continuity",
]


# ── Thin reader — queries mv_handoff_witness_tiers ───────────────────────────


def _read_handoff_witness_tiers(conn: sqlite3.Connection) -> list[ViewResult]:
    """Read pre-computed rows from mv_handoff_witness_tiers and group into ViewResult objects."""
    c = conn.cursor()
    try:
        c.execute(
            "SELECT relation_type, view_name,"
            " plumbing_witness_count, test_witness_count, live_runtime_witness_count"
            " FROM mv_handoff_witness_tiers"
            " ORDER BY view_name, relation_type"
        )
        db_rows = c.fetchall()
    except sqlite3.OperationalError as exc:
        raise RuntimeError(
            "mv_handoff_witness_tiers not found in this ADG SQLite.\n"
            "Re-run ADG generation to materialize Phase A tables:\n"
            "  python tools/generate_full_adg.py"
        ) from exc

    by_view: dict[str, list[WitnessRow]] = {}
    for relation_type, view_name, plumbing, test, live_rt in db_rows:
        row = WitnessRow(
            relation_type=relation_type,
            plumbing_witness_count=plumbing,
            test_witness_count=test,
            live_runtime_witness_count=live_rt,
        )
        by_view.setdefault(view_name, []).append(row)

    views: list[ViewResult] = []
    for view_name in _VIEW_ORDER:
        rows = by_view.get(view_name, [])
        views.append(
            ViewResult(
                name=view_name,
                description=_VIEW_DESCRIPTIONS.get(view_name, view_name),
                rows=rows,
            )
        )
    return views


def run_all_views(db_path: str | Path) -> list[ViewResult]:
    """Read all 6 runtime-spine views from the mv_handoff_witness_tiers materialized table."""
    conn = sqlite3.connect(str(db_path))
    try:
        return _read_handoff_witness_tiers(conn)
    finally:
        conn.close()


# ── Reporting ─────────────────────────────────────────────────────────────────

_COL_W = 38
_HDR = (
    f"{'Relation':<{_COL_W}}  {'plumbing':>8}  {'test':>6}  {'live_rt':>7}  {'zero':>5}  {'rt_orphaned':>11}"
)
_SEP = "-" * len(_HDR)


def _fmt_row(row: WitnessRow) -> str:
    orphan_flag = "TRUE  !" if row.runtime_orphaned else "false"
    return (
        f"{row.relation_type:<{_COL_W}}"
        f"  {row.plumbing_witness_count:>8}"
        f"  {row.test_witness_count:>6}"
        f"  {row.live_runtime_witness_count:>7}"
        f"  {row.zero_witness_count:>5}"
        f"  {orphan_flag:>11}"
    )


def print_view_report(view: ViewResult) -> None:
    """Print per-view witness tier breakdown."""
    width = len(_HDR)
    print()
    print("=" * width)
    print(f"  {view.name}")
    print(f"  {view.description}")
    print("=" * width)
    print(_HDR)
    print(_SEP)
    for row in view.rows:
        print(_fmt_row(row))
    print(_SEP)
    orphaned = view.runtime_orphaned_rows
    if orphaned:
        names = ", ".join(r.relation_type for r in orphaned)
        print(f"  [!] Runtime-orphaned: {names}")
    else:
        print("  [ok] No runtime-orphaned rows")


def print_summary_table(views: list[ViewResult]) -> None:
    """Print the cross-view summary table."""
    width = 92
    print()
    print("=" * width)
    print("  RUNTIME-SPINE SUMMARY TABLE")
    print("=" * width)
    fmt_hdr = (
        f"  {'Relation/Family':<38}  {'ext_wired':>9}  {'test_cov':>8}  {'live_rt':>7}  {'rt_orphaned':>13}"
    )
    print(fmt_hdr)
    print("-" * width)
    for view in views:  # tqdm: small fixed result set, no bar needed
        print(f"  [{view.name}]")
        for row in view.rows:
            rt_orphan = "TRUE  !" if row.runtime_orphaned else "false"
            line = (
                f"    {row.relation_type:<36}"
                f"  {str(row.extraction_wired):>9}"
                f"  {str(row.test_covered):>8}"
                f"  {str(row.live_runtime_present):>7}"
                f"  {rt_orphan:>13}"
            )
            print(line)
        print("-" * width)

    all_rows = [r for v in views for r in v.rows]
    orphaned = [r for r in all_rows if r.runtime_orphaned]
    zero = [r for r in all_rows if r.zero_witness_count > 0]
    print(f"  Total relations surveyed : {len(all_rows)}")
    print(f"  Runtime-orphaned         : {len(orphaned)}")
    print(f"  Completely dark (zero)   : {len(zero)}")
    print("=" * width)


# ── Cross-cutting witness-tier reader ────────────────────────────────────────


def _read_cross_cutting_witness_tiers(
    conn: sqlite3.Connection,
) -> list[CrossCuttingFamilyResult]:
    """Aggregate mv_cross_cutting_witness_tiers by family_name."""
    c = conn.cursor()
    try:
        c.execute(
            "SELECT family_name,"
            " COUNT(*) AS relation_count,"
            " COALESCE(SUM(plumbing_witness_count), 0) AS plumbing_total,"
            " COALESCE(SUM(test_witness_count), 0) AS test_total,"
            " COALESCE(SUM(live_runtime_witness_count), 0) AS live_rt_total,"
            " COALESCE(SUM(runtime_orphaned), 0) AS orphaned_count,"
            " COALESCE(SUM(zero_witness_count), 0) AS zero_count"
            " FROM mv_cross_cutting_witness_tiers"
            " GROUP BY family_name"
            " ORDER BY family_name"
        )
        rows = c.fetchall()
    except sqlite3.OperationalError as exc:
        raise RuntimeError(
            "mv_cross_cutting_witness_tiers not found in this ADG SQLite.\n"
            "Re-run ADG generation to materialize Phase A tables:\n"
            "  python tools/generate_full_adg.py"
        ) from exc

    return [
        CrossCuttingFamilyResult(
            family_name=row[0],
            relation_count=row[1],
            plumbing_total=row[2],
            test_total=row[3],
            live_rt_total=row[4],
            orphaned_count=row[5],
            zero_count=row[6],
        )
        for row in rows
    ]


def run_cross_cutting_views(db_path: str | Path) -> list[CrossCuttingFamilyResult]:
    """Read all 13 cross-cutting families from mv_cross_cutting_witness_tiers."""
    conn = sqlite3.connect(str(db_path))
    try:
        return _read_cross_cutting_witness_tiers(conn)
    finally:
        conn.close()


def print_cross_cutting_summary(results: list[CrossCuttingFamilyResult]) -> None:
    """Compact per-family witness-tier table for the 13 cross-cutting obligation families."""
    width = 100
    print()
    print("=" * width)
    print("  CROSS-CUTTING WITNESS-TIER SUMMARY  (mv_cross_cutting_witness_tiers, Phase A)")
    print("=" * width)
    hdr = f"  {'Family':<42}  {'rels':>4}  {'plumbing':>8}  {'test':>6}  {'live_rt':>7}  {'rt_orphaned':>11}"
    print(hdr)
    print("-" * width)
    for r in results:  # tqdm: DB result set, no bar needed
        flag = "TRUE  !" if r.runtime_orphaned else "false"
        line = (
            f"  {r.family_name:<42}"
            f"  {r.relation_count:>4}"
            f"  {r.plumbing_total:>8}"
            f"  {r.test_total:>6}"
            f"  {r.live_rt_total:>7}"
            f"  {flag:>11}"
        )
        print(line)
    print("-" * width)
    total_rels = sum(r.relation_count for r in results)
    total_orphaned = sum(1 for r in results if r.runtime_orphaned)
    total_live_rt = sum(1 for r in results if r.live_rt_total > 0)
    print(f"  Families surveyed          : {len(results)}")
    print(f"  Relations surveyed         : {total_rels}")
    print(f"  Families with live_rt > 0  : {total_live_rt}")
    print(f"  Families runtime-orphaned  : {total_orphaned}")
    print("=" * width)
    if total_orphaned:
        print()
        print("[!] Cross-cutting families wired + covered but lacking live runtime proof:")
        for r in results:
            if r.runtime_orphaned:
                print(f"  [x] {r.family_name}")


# ── Semantic satisfaction check ───────────────────────────────────────────────


def check_semantic_satisfaction(views: list[ViewResult]) -> list[str]:
    """Return list of semantic failures (runtime-orphaned relations).

    Failure condition:
      extraction_wired = True  AND
      (test_covered OR plumbing_wired) = True  AND
      live_runtime_present = False
    """
    failures: list[str] = []
    for view in views:
        for row in view.runtime_orphaned_rows:
            failures.append(f"{view.name}::{row.relation_type}")
    return failures


# ── CLI entrypoint ────────────────────────────────────────────────────────────


def main() -> int:
    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
    else:
        snapshots = sorted(glob.glob(f"{ADG_ARTIFACTS_DIR}/adg_indexed_*.sqlite"))
        if not snapshots:
            print("[ERROR] No ADG SQLite found. Run: python tools/generate_full_adg.py")
            return 1
        db_path = Path(snapshots[-1])

    if not db_path.exists():
        print(f"[ERROR] ADG SQLite not found: {db_path}")
        return 1

    print(f"[mv_runtime_spine] ADG snapshot : {db_path}")
    print("[mv_runtime_spine] Reading from mv_handoff_witness_tiers (Phase A, official pipeline)")

    views = run_all_views(str(db_path))

    for view in views:
        print_view_report(view)

    print_summary_table(views)

    print("[mv_runtime_spine] Reading from mv_cross_cutting_witness_tiers (Phase A, official pipeline)")
    cc_results = run_cross_cutting_views(str(db_path))
    print_cross_cutting_summary(cc_results)

    failures = check_semantic_satisfaction(views)
    if failures:
        print()
        print(
            "[SEMANTIC FAILURE] Runtime-orphaned relations"
            " (extraction_wired=True, live_runtime_present=False):"
        )
        for f in failures:
            print(f"  [x] {f}")
        total = sum(len(v.rows) for v in views)
        print()
        print(
            f"  {len(failures)}/{total} relations are runtime-orphaned"
            " (plumbing/bootstrap-wired, no live production callers yet)."
        )
        return 1

    print()
    print("[ok] All runtime-spine obligations satisfied -- live_runtime_present for every relation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
