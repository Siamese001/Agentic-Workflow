#!/usr/bin/env python3
"""check_test_concentration_ratio.py — CI gate against test concentration drift.

Two failing conditions (constitutional §22 graph-layer evidence + §28 SQLite
canonical fan_in):

    1. OVER-INVESTMENT: any subject with density > MAX_DENSITY where
       density = test_attribution_count / max(1, fan_in).
       Indicates a single subject pulling >50× the median tests-per-importer
       — usually attribution multiplication via re-export, not real coverage.

    2. UNDER-INVESTMENT: any subject with fan_in >= MIN_FANIN_FOR_RISK
       AND test_count == 0 AND has at least one ADG semantic edge
       (resolves_callsite, emits_side_effect, writes_to, controls_flow,
       reads_from, flows_to). The semantic-edge filter excludes pure
       type-stub / re-export modules that don't deserve tests.

Reads the canonical ADG SQLite snapshot (largest `adg_indexed_*.sqlite` in
artifacts/adg/). Falls back to advisory-only mode if no snapshot exists,
so the gate never hard-fails on a fresh clone before the first ADG run.

Modes:
    advisory (default): prints findings, exit 0 — establishes baseline drift
    strict (TEST_CONCENTRATION_GATE_STRICT=1): exits 1 on any finding

Baseline ratchet: Once strict mode is enabled, only NEW under-investment
relative to ops_scripts/ci/baselines/test_concentration_ratchet.json fails.
Over-investment drift always fails in strict mode (shouldn't grow).

Bypass: TEST_CONCENTRATION_GATE_BYPASS=1
"""
from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import ast
import glob
import json
import os
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = ROOT / "ops_scripts" / "ci" / "baselines" / "test_concentration_ratchet.json"

# Tunable thresholds — keep in sync with concentration analysis
MAX_DENSITY = 50.0          # tests/fan_in above this is over-investment
MIN_FANIN_FOR_RISK = 15      # below this fan_in, missing tests aren't critical
SEMANTIC_EDGE_TYPES = (
    "resolves_callsite",
    "emits_side_effect",
    "writes_to",
    "controls_flow",
    "reads_from",
    "flows_to",
)


def _latest_snapshot() -> Path | None:
    candidates = sorted(
        (Path(p) for p in glob.glob(str(ROOT / "artifacts" / "adg" / "adg_indexed_*.sqlite"))),
        key=lambda p: (p.stat().st_size, p.stat().st_mtime),
        reverse=True,
    )
    for c in candidates:
        if c.stat().st_size < 1_000_000:
            continue
        try:
            uri = f"file:{c.as_posix()}?mode=ro&immutable=1"
            con = sqlite3.connect(uri, uri=True)
            con.execute("SELECT 1 FROM nodes LIMIT 1")
            con.close()
            return c
        except sqlite3.DatabaseError:
            continue
    return None


def _fan_in_from_sqlite(snapshot: Path) -> dict[str, int]:
    uri = f"file:{snapshot.as_posix()}?mode=ro&immutable=1"
    con = sqlite3.connect(uri, uri=True)
    cur = con.cursor()
    cur.execute("""
      SELECT n.resolved_path AS path, COUNT(DISTINCT e.source_file) AS fan_in
      FROM edges e JOIN nodes n ON n.id = e.dst_id
      WHERE e.relation_type = 'imports'
        AND n.resolved_path IS NOT NULL
        AND n.resolved_path != ''
        AND n.resolved_path NOT LIKE 'tests/%'
        AND e.source_file != n.resolved_path
      GROUP BY n.resolved_path
    """)
    out: dict[str, int] = {}
    for path, count in cur.fetchall():
        if path:
            out[path.replace("\\", "/")] = int(count)
    con.close()
    return out


def _subjects_with_semantic_edges(snapshot: Path) -> set[str]:
    """Return set of resolved_paths that have at least one semantic edge.

    Semantic edges (per constitutional §22) indicate operational behavior;
    type-stub / re-export modules don't have them and don't deserve tests.
    """
    uri = f"file:{snapshot.as_posix()}?mode=ro&immutable=1"
    con = sqlite3.connect(uri, uri=True)
    cur = con.cursor()
    placeholders = ",".join("?" * len(SEMANTIC_EDGE_TYPES))
    cur.execute(f"""
      SELECT DISTINCT n.resolved_path
      FROM edges e JOIN nodes n ON n.id = e.dst_id
      WHERE e.relation_type IN ({placeholders})
        AND n.resolved_path IS NOT NULL
        AND n.resolved_path != ''
    """, SEMANTIC_EDGE_TYPES)
    out = {row[0].replace("\\", "/") for row in cur.fetchall() if row[0]}
    con.close()
    return out


def _count_test_funcs(path: Path) -> int:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return 0
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                n += 1
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name.startswith("test_"):
                    n += 1
    return n


def _imports_from_sqlite(snapshot: Path) -> dict[str, set[str]]:
    """For each test file, return the set of subject paths it imports."""
    uri = f"file:{snapshot.as_posix()}?mode=ro&immutable=1"
    con = sqlite3.connect(uri, uri=True)
    cur = con.cursor()
    cur.execute("""
      SELECT DISTINCT e.source_file, n.resolved_path
      FROM edges e JOIN nodes n ON n.id = e.dst_id
      WHERE e.relation_type = 'imports'
        AND e.source_file LIKE 'tests/%'
        AND n.resolved_path IS NOT NULL
        AND n.resolved_path != ''
        AND n.resolved_path NOT LIKE 'tests/%'
    """)
    out: dict[str, set[str]] = defaultdict(set)
    for src, dst in cur.fetchall():
        out[src.replace("\\", "/")].add(dst.replace("\\", "/"))
    con.close()
    return out


def _build_test_attribution(snapshot: Path) -> dict[str, int]:
    """test_count = sum over test files importing this subject of that file's
    AST-counted test_* func count."""
    test_files_subjects = _imports_from_sqlite(snapshot)
    attribution: dict[str, int] = defaultdict(int)
    for tf_rel, subjects in test_files_subjects.items():
        tf_abs = ROOT / tf_rel
        if not tf_abs.exists():
            continue
        n = _count_test_funcs(tf_abs)
        if n == 0:
            continue
        for subj in subjects:
            attribution[subj] += n
    return attribution


def _load_baseline() -> dict:
    if not BASELINE_PATH.exists():
        return {"over_invested_count": 0, "under_invested_subjects": []}
    try:
        return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"over_invested_count": 0, "under_invested_subjects": []}


def _write_baseline(over_count: int, under_subjects: list[str]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(
        json.dumps(
            {
                "over_invested_count": over_count,
                "under_invested_subjects": sorted(under_subjects),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    if os.environ.get("TEST_CONCENTRATION_GATE_BYPASS") == "1":
        print("[check_test_concentration_ratio] BYPASSED (env TEST_CONCENTRATION_GATE_BYPASS=1)")
        return 0

    strict = os.environ.get("TEST_CONCENTRATION_GATE_STRICT") == "1"
    write_baseline = os.environ.get("TEST_CONCENTRATION_GATE_WRITE_BASELINE") == "1"

    snapshot = _latest_snapshot()
    if snapshot is None:
        print(
            "[check_test_concentration_ratio] no usable ADG SQLite snapshot — "
            "advisory-only (no fail). Run: python tools/generate_full_adg.py",
        )
        return 0

    print(f"[check_test_concentration_ratio] using snapshot: {snapshot.name}")
    print(f"[check_test_concentration_ratio] mode: {'STRICT' if strict else 'advisory'}")

    fan_in = _fan_in_from_sqlite(snapshot)
    test_count = _build_test_attribution(snapshot)
    semantic = _subjects_with_semantic_edges(snapshot)

    over_invested: list[tuple[str, int, int, float]] = []
    under_invested: list[tuple[str, int]] = []

    all_subjects = set(fan_in) | set(test_count)
    for subj in all_subjects:
        f = fan_in.get(subj, 0)
        t = test_count.get(subj, 0)
        density = t / max(1, f)
        if density > MAX_DENSITY and t >= 20:
            over_invested.append((subj, t, f, density))
        if (
            f >= MIN_FANIN_FOR_RISK
            and t == 0
            and subj in semantic
        ):
            under_invested.append((subj, f))

    over_count = len(over_invested)
    under_subjects = [s for s, _ in under_invested]

    if write_baseline:
        _write_baseline(over_count, under_subjects)
        print(f"[check_test_concentration_ratio] BASELINE WRITTEN: {BASELINE_PATH}")
        print(f"  over_invested_count={over_count}  under_invested={len(under_subjects)}")
        return 0

    baseline = _load_baseline()
    bl_over = baseline.get("over_invested_count", 0)
    bl_under = set(baseline.get("under_invested_subjects", []))

    new_under = [s for s in under_subjects if s not in bl_under]
    over_grew = over_count > bl_over

    # Always report findings (advisory)
    if over_invested:
        print(
            f"[check_test_concentration_ratio] over-invested: {over_count} "
            f"(baseline={bl_over}, drift={'+' if over_grew else ''}{over_count - bl_over}):",
        )
        for subj, t, f, d in sorted(over_invested, key=lambda x: -x[3])[:5]:
            print(f"  density={d:7.1f}  tests={t:5d}  fan_in={f:3d}  {subj}")
    if under_invested:
        print(
            f"[check_test_concentration_ratio] under-invested: {len(under_invested)} "
            f"(baseline={len(bl_under)}, NEW={len(new_under)}):",
        )
        for subj, f in sorted(under_invested, key=lambda x: -x[1])[:5]:
            tag = " [NEW]" if subj in new_under else ""
            print(f"  fan_in={f:3d}  tests=0  {subj}{tag}")

    if not strict:
        print("[check_test_concentration_ratio] PASS (advisory mode — no enforcement)")
        return 0

    # Strict mode: fail on any growth or new under-investment
    failed = False
    if over_grew:
        print(
            f"[check_test_concentration_ratio] FAIL — over-invested grew "
            f"({bl_over} → {over_count})",
        )
        failed = True
    if new_under:
        print(
            f"[check_test_concentration_ratio] FAIL — {len(new_under)} NEW "
            f"under-invested subjects (high fan_in, zero tests, semantic edges):",
        )
        for s in new_under[:10]:
            print(f"  - {s}")
        failed = True

    if failed:
        print(
            "Bypass: TEST_CONCENTRATION_GATE_BYPASS=1. "
            "Constitutional §22 / §28.",
        )
        return 1

    print("[check_test_concentration_ratio] PASS (no drift vs baseline)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
