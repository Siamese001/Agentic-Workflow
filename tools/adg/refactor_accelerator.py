"""
Refactor Accelerator — MVP (W3.4)

Ranks refactoring candidates by composite score using ADG + git churn.
Read-only — never modifies code.

Usage:
  python tools/adg/refactor_accelerator.py                     # top 20 candidates, all layers
  python tools/adg/refactor_accelerator.py --top 10
  python tools/adg/refactor_accelerator.py --layer L0
  python tools/adg/refactor_accelerator.py --mode candidates   # default
  python tools/adg/refactor_accelerator.py --mode migration-order
  python tools/adg/refactor_accelerator.py --json
  python tools/adg/refactor_accelerator.py --sqlite artifacts/adg/adg_indexed_<ts>.sqlite
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import json
import sqlite3
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]

# Composite score weights (must sum to 1.0)
W_FAN_IN = 0.30
W_CHURN = 0.25
W_VIOLATIONS = 0.25
W_LINT = 0.20


def _find_latest_sqlite() -> Path:
    adg_dir = ROOT / "artifacts" / "adg"
    candidates = sorted(adg_dir.glob("adg_indexed_*.sqlite"), reverse=True)
    if not candidates:
        print("[RA] ERROR: No adg_indexed_*.sqlite found in artifacts/adg/", file=sys.stderr)
        sys.exit(1)
    return candidates[0]


def _normalize_rel_path(path_str: str) -> str:
    path = Path(path_str)
    if path.is_absolute():
        try:
            path = path.relative_to(ROOT)
        except ValueError:
            path = Path(path.name)
    return path.as_posix()


def _git_churn(days: int = 90) -> dict[str, int]:
    """Return {relative_path: commit_count} for files changed in last N days."""
    if days <= 0:
        return {}
    try:
        result = subprocess.run(
            ["git", "log", f"--since={days} days ago", "--name-only", "--format="],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            return {}
        counts: dict[str, int] = defaultdict(int)
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and not line.startswith("commit "):
                counts[_normalize_rel_path(line)] += 1
        return dict(counts)
    except (OSError, subprocess.TimeoutExpired):
        return {}


def _ruff_lint_counts() -> dict[str, int]:
    """Return {relative_path: violation_count} from ruff."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", ".", "--output-format=json", "--quiet"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if result.returncode not in (0, 1):
            return {}
        if not result.stdout.strip():
            return {}
        violations = json.loads(result.stdout)
        counts: dict[str, int] = defaultdict(int)
        for v in violations:
            fname = v.get("filename", "")
            if fname:
                counts[_normalize_rel_path(fname)] += 1
        return dict(counts)
    except (OSError, json.JSONDecodeError, subprocess.TimeoutExpired, ValueError):
        return {}


def _fetch_candidates(
    conn: sqlite3.Connection,
    layer_filter: str | None,
    top_n: int,
    churn: dict[str, int],
    lint: dict[str, int],
) -> list[dict]:
    """Build scored candidate list from ADG + external signals."""
    cur = conn.cursor()

    layer_clause = "AND n.layer = ?" if layer_filter else ""
    params: list = [layer_filter] if layer_filter else []

    rows = cur.execute(
        f"""
        SELECT
            n.id,
            n.adg_name,
            n.layer,
            n.resolved_path,
            COUNT(DISTINCT e_in.src_id) AS fan_in,
            COUNT(DISTINCT e_out.dst_id) AS fan_out
        FROM nodes n
        JOIN edges e_in ON e_in.dst_id = n.id AND e_in.relation_type IN ('imports','calls')
        LEFT JOIN edges e_out ON e_out.src_id = n.id AND e_out.relation_type IN ('imports','calls')
        WHERE 1=1
        {layer_clause}
        GROUP BY n.id
        HAVING fan_in > 0
        ORDER BY fan_in DESC
        LIMIT 500
    """,
        params,
    ).fetchall()

    violation_counts: dict[int, int] = {}
    vrows = cur.execute(
        """
        SELECT e.dst_id, COUNT(*) as cnt
        FROM edges e
        WHERE e.relation_type = 'violates'
        GROUP BY e.dst_id
    """
    ).fetchall()
    for node_id, cnt in vrows:
        violation_counts[node_id] = cnt

    max_fan_in = max((r[4] for r in rows), default=1)
    max_churn = max(churn.values(), default=1) if churn else 1
    max_violations = max(violation_counts.values(), default=1)
    max_lint = max(lint.values(), default=1) if lint else 1

    candidates = []
    for node_id, adg_name, layer, resolved_path, fan_in, fan_out in tqdm(
        rows, desc="Processing", unit="item"
    ):
        rel_path = (resolved_path or "").replace("\\", "/")
        churn_count = churn.get(rel_path, 0)
        viol_count = violation_counts.get(node_id, 0)
        lint_count = lint.get(rel_path, 0)

        score = (
            W_FAN_IN * (fan_in / max_fan_in)
            + W_CHURN * (churn_count / max_churn)
            + W_VIOLATIONS * (viol_count / max_violations)
            + W_LINT * (lint_count / max_lint)
        )

        candidates.append(
            {
                "node_id": node_id,
                "adg_name": adg_name,
                "layer": layer or "?",
                "resolved_path": rel_path,
                "score": round(score, 4),
                "dimensions": {
                    "fan_in": fan_in,
                    "fan_out": fan_out,
                    "churn_90d": churn_count,
                    "violations": viol_count,
                    "lint_count": lint_count,
                },
            }
        )

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_n]


def _add_blast_radius(conn: sqlite3.Connection, candidates: list[dict], depth: int = 2) -> None:
    """Add blast_radius field to each candidate (transitive fan-in, limited depth)."""
    cur = conn.cursor()
    for candidate in candidates:
        node_id = candidate["node_id"]
        visited: set[int] = {node_id}
        frontier = {node_id}
        depth_map: dict[int, int] = {node_id: 0}

        for d in range(depth):
            if not frontier:
                break
            placeholders = ",".join("?" for _ in frontier)
            importers = cur.execute(
                f"SELECT src_id FROM edges WHERE dst_id IN ({placeholders}) AND relation_type IN ('imports','calls')",
                list(frontier),
            ).fetchall()
            next_frontier: set[int] = set()
            for (src_id,) in importers:
                if src_id not in visited:
                    next_frontier.add(src_id)
                    depth_map[src_id] = d + 1
            visited.update(frontier)
            frontier = next_frontier

        candidate["blast_radius"] = {
            "total_affected": len(depth_map) - 1,
            "max_depth": depth,
        }


def _add_impacted_tests(conn: sqlite3.Connection, candidates: list[dict]) -> None:
    """Add impacted_tests field to each candidate via 'covers' relation."""
    cur = conn.cursor()
    for candidate in tqdm(candidates, desc="Processing", unit="item"):
        node_id = candidate["node_id"]
        test_rows = cur.execute(
            """
            SELECT DISTINCT n.resolved_path
            FROM edges e
            JOIN nodes n ON n.id = e.src_id
            WHERE e.dst_id = ? AND e.relation_type = 'covers'
            LIMIT 10
        """,
            (node_id,),
        ).fetchall()
        candidate["impacted_tests"] = [r[0] for r in test_rows if r[0]]


def _migration_order(conn: sqlite3.Connection, candidates: list[dict]) -> list[str]:
    """
    Topological sort of candidates: refactor leaves before roots.
    Nodes with no outgoing deps to other candidates come first.
    """
    node_ids = {candidate["node_id"] for candidate in candidates}
    id_to_path = {candidate["node_id"]: candidate["resolved_path"] for candidate in candidates}

    cur = conn.cursor()
    in_degree: dict[int, int] = defaultdict(int)
    adj: dict[int, set[int]] = defaultdict(set)

    if node_ids:
        placeholders = ",".join("?" for _ in node_ids)
        edges = cur.execute(
            f"SELECT src_id, dst_id FROM edges WHERE src_id IN ({placeholders}) AND dst_id IN ({placeholders}) AND relation_type IN ('imports','calls')",
            list(node_ids) + list(node_ids),
        ).fetchall()
        for src, dst in edges:
            if dst not in adj[src]:
                adj[src].add(dst)
                in_degree[dst] += 1

    queue = deque(sorted(node for node in node_ids if in_degree[node] == 0))
    ordered_paths: list[str] = []
    seen_paths: set[str] = set()
    while queue:
        node = queue.popleft()
        path = id_to_path.get(node, str(node))
        if path not in seen_paths:
            ordered_paths.append(path)
            seen_paths.add(path)
        for neighbor in sorted(adj[node]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    remaining = [
        id_to_path.get(node, str(node)) for node in sorted(node_ids) if id_to_path.get(node) not in seen_paths
    ]
    return ordered_paths + remaining


def _print_candidates(candidates: list[dict], with_rank: bool = True) -> None:
    print(f"\n[RA] Top {len(candidates)} Refactor Candidates")
    H = "+----+-------+----------+-------+-------+-------+------+------------------------------------------------------+"
    print(H)
    print(
        "| Rk | Score | Layer    | FanIn | Churn | Viol  | Lint | File                                                 |"
    )
    print(H)
    for i, candidate in enumerate(candidates, 1):
        layer = candidate["layer"][:8]
        name = (candidate["resolved_path"] or candidate["adg_name"])[:52]
        dims = candidate["dimensions"]
        print(
            f"| {i:2} | {candidate['score']:.3f} | {layer:<8} | {dims['fan_in']:5} | {dims['churn_90d']:5} | {dims['violations']:5} | {dims['lint_count']:4} | {name:<52} |",
        )
    print(H)


def main() -> None:
    parser = argparse.ArgumentParser(description="Refactor Accelerator MVP (W3.4)")
    parser.add_argument("--sqlite", help="Path to ADG SQLite (auto-detected if omitted)")
    parser.add_argument("--top", type=int, default=20, help="Top-N candidates")
    parser.add_argument("--layer", help="Filter by layer (e.g. L0, L2)")
    parser.add_argument("--mode", choices=["candidates", "migration-order"], default="candidates")
    parser.add_argument("--json", action="store_true", dest="as_json", help="JSON output")
    parser.add_argument("--no-churn", action="store_true", help="Skip git churn (faster)")
    parser.add_argument("--no-lint", action="store_true", help="Skip ruff lint (faster)")
    args = parser.parse_args()

    if args.top <= 0:
        parser.error("--top must be > 0")

    sqlite_path = Path(args.sqlite) if args.sqlite else _find_latest_sqlite()
    if not sqlite_path.exists():
        print(f"[RA] ERROR: SQLite not found: {sqlite_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[RA] Refactor Accelerator — {sqlite_path.name}")

    churn: dict[str, int] = {}
    lint: dict[str, int] = {}

    if not args.no_churn:
        print("[RA] Loading git churn (90d)...")
        churn = _git_churn(90)
        print(f"[RA]   {len(churn)} files with recent commits")

    if not args.no_lint:
        print("[RA] Loading ruff lint counts...")
        lint = _ruff_lint_counts()
        print(f"[RA]   {len(lint)} files with lint violations")

    conn = sqlite3.connect(str(sqlite_path))
    try:
        candidates = _fetch_candidates(conn, args.layer, args.top, churn, lint)
        _add_blast_radius(conn, candidates)
        _add_impacted_tests(conn, candidates)

        if args.mode == "migration-order":
            order = _migration_order(conn, candidates)
            if args.as_json:
                print(json.dumps({"migration_sequence": order}, indent=2))
            else:
                print(f"\n[RA] Migration Order ({len(order)} files — refactor leaves first)")
                for i, path in enumerate(order, 1):
                    print(f"  {i:3}. {path}")
        else:
            if args.as_json:
                output = {
                    "sqlite_used": sqlite_path.name,
                    "layer_filter": args.layer,
                    "candidates": [{k: v for k, v in c.items() if k != "node_id"} for c in candidates],
                }
                print(json.dumps(output, indent=2, default=str))
            else:
                _print_candidates(candidates)
                if candidates:
                    top = candidates[0]
                    dims = top["dimensions"]
                    print(f"\n[RA] Top candidate: {top['resolved_path'] or top['adg_name']}")
                    print(
                        f"     Score: {top['score']} | FanIn: {dims['fan_in']} | Churn: {dims['churn_90d']} | Violations: {dims['violations']}"
                    )
                    print(
                        f"     Blast radius: {top['blast_radius']['total_affected']} modules affected (depth {top['blast_radius']['max_depth']})"
                    )
                    tests = top.get("impacted_tests", [])
                    if tests:
                        print(f"     Impacted tests: {', '.join(tests[:5])}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
