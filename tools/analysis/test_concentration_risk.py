#!/usr/bin/env python3
"""
test_concentration_risk.py — Test concentration risk analysis.

Maps every subject file under agentic_core/, apps_*/, system_learning/,
tools/, infrastructure/ to:
    - fan_in: number of internal modules that import it (via AST)
    - test_count: number of test_*/Test* test functions targeting it
                  (via AST in tests/, mapped by import + path convention)

Then computes a concentration metric:
    coverage_density = test_count / max(1, fan_in)

Surfaces:
    - OVER-INVESTED: high test_count, low fan_in (candidates for prune)
    - UNDER-INVESTED: low test_count, high fan_in (concentration risk)
    - OK: balanced

Pure AST. No grep, no MCP. One-shot.

Run:
    python tools/analysis/test_concentration_risk.py
    python tools/analysis/test_concentration_risk.py --top 30
"""
from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import ast
import glob
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _latest_adg_snapshot() -> Path | None:
    """Return path to the largest, most recent ADG SQLite snapshot.

    Used as the canonical fan-in source per constitutional §28. Falls back
    to AST-based fan-in when no usable snapshot is found.
    """
    candidates = sorted(
        (Path(p) for p in glob.glob(str(ROOT / "artifacts" / "adg" / "adg_indexed_*.sqlite"))),
        key=lambda p: (p.stat().st_size, p.stat().st_mtime),
        reverse=True,
    )
    for c in candidates:
        # Skip empty smoke-test stubs
        if c.stat().st_size < 1_000_000:
            continue
        try:
            # Open read-only via URI to bypass write-locks held by an
            # in-progress generate_full_adg.py run.
            uri = f"file:{c.as_posix()}?mode=ro&immutable=1"
            con = sqlite3.connect(uri, uri=True)
            con.execute("SELECT 1 FROM nodes LIMIT 1")
            con.close()
            return c
        except sqlite3.DatabaseError:
            continue
    return None


def _fan_in_from_sqlite(snapshot: Path) -> dict[str, int]:
    """Pull fan_in (imports edges only) from the canonical ADG snapshot.

    Returns subject_path → fan_in count. Self-imports excluded.
    """
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

SUBJECT_ROOTS = [
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
    "system_learning",
    "tools",
    "infrastructure",
    "ops_scripts",
]
TEST_ROOT = "tests"

# Map dotted module name → subject path
_module_to_path: dict[str, str] = {}
# Reverse: subject path → dotted module name
_path_to_module: dict[str, str] = {}


def _module_name_for(path: Path) -> str:
    """Convert agentic_core/L0_routing/foo.py → agentic_core.L0_routing.foo"""
    rel = path.relative_to(ROOT).with_suffix("")
    parts = rel.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _iter_python_files(under: Path) -> list[Path]:
    # Use canonical exclusion sets from agentic_core SSOT (constitutional —
    # no hardcoded exclusion lists per ops_scripts/ci/check_hardcoded_exclusions.py).
    from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS
    extra = frozenset({"archives", "_archived_obsolete"})
    excluded = GLOBAL_EXCLUDED_DIRS | extra
    out: list[Path] = []
    for p in under.rglob("*.py"):
        if any(seg in excluded for seg in p.parts):
            continue
        out.append(p)
    return out


def _build_module_index() -> None:
    for sr in SUBJECT_ROOTS:
        base = ROOT / sr
        if not base.exists():
            continue
        for p in _iter_python_files(base):
            mod = _module_name_for(p)
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            _module_to_path[mod] = rel
            _path_to_module[rel] = mod


def _imports_in_file(path: Path) -> set[str]:
    """Return set of dotted modules imported by this file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                # `from x.y import z` → x.y
                out.add(node.module)
                # also try x.y.z if z is a submodule
                for alias in node.names:
                    out.add(f"{node.module}.{alias.name}")
    return out


def _resolve_to_subject(module: str) -> str | None:
    """Return the subject path matching a dotted module name (longest match)."""
    if module in _module_to_path:
        return _module_to_path[module]
    # Walk up dotted parts: x.y.z → x.y → x
    parts = module.split(".")
    while parts:
        candidate = ".".join(parts)
        if candidate in _module_to_path:
            return _module_to_path[candidate]
        parts.pop()
    return None


def _count_test_funcs(path: Path) -> int:
    """Count test_*/Test* test functions in a test file via AST."""
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=25, help="rows per outlier table")
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()

    print("[test_concentration_risk] indexing modules...", file=sys.stderr)
    _build_module_index()
    print(f"[test_concentration_risk] {len(_module_to_path)} subject modules indexed", file=sys.stderr)

    # Fan-in source: prefer canonical ADG SQLite snapshot per constitutional §28.
    # Fall back to AST when no usable snapshot exists.
    snapshot = _latest_adg_snapshot()
    fan_in: dict[str, int] = defaultdict(int)
    fan_in_source = "ast_fallback"
    if snapshot is not None:
        try:
            sqlite_fan_in = _fan_in_from_sqlite(snapshot)
            fan_in.update(sqlite_fan_in)
            fan_in_source = f"sqlite:{snapshot.name}"
            print(
                f"[test_concentration_risk] fan_in from {snapshot.name} "
                f"({len(sqlite_fan_in)} subjects)",
                file=sys.stderr,
            )
        except sqlite3.DatabaseError as exc:
            print(f"[test_concentration_risk] SQLite read failed: {exc}; using AST", file=sys.stderr)
            snapshot = None

    if snapshot is None:
        # AST fallback (DEGRADED). Dedupe at SUBJECT level per importing file
        # so `from X import a, b, c` increments fan_in by 1, not by 4.
        for sr in SUBJECT_ROOTS:
            base = ROOT / sr
            if not base.exists():
                continue
            for p in _iter_python_files(base):
                src = str(p.relative_to(ROOT)).replace("\\", "/")
                subjects_imported: set[str] = set()
                for mod in _imports_in_file(p):
                    subject = _resolve_to_subject(mod)
                    if subject is None or subject == src:
                        continue
                    subjects_imported.add(subject)
                for subject in subjects_imported:
                    fan_in[subject] += 1

    # Build test_count by attributing each test file's test count to every
    # UNIQUE subject it imports (dedupe per file — same fix as fan_in).
    test_count: dict[str, int] = defaultdict(int)
    test_files = _iter_python_files(ROOT / TEST_ROOT)
    total_tests = 0
    for tf in test_files:
        n = _count_test_funcs(tf)
        if n == 0:
            continue
        total_tests += n
        tf_subjects: set[str] = set()
        for mod in _imports_in_file(tf):
            subject = _resolve_to_subject(mod)
            if subject is None:
                continue
            tf_subjects.add(subject)
        for subject in tf_subjects:
            test_count[subject] += n

    # Union of all subjects we care about
    all_subjects = sorted(set(fan_in.keys()) | set(test_count.keys()))
    rows = []
    for s in all_subjects:
        f = fan_in.get(s, 0)
        t = test_count.get(s, 0)
        density = t / max(1, f)
        rows.append({"subject": s, "fan_in": f, "test_count": t, "density": round(density, 2)})

    # Concentration metrics
    sum_tests_attributed = sum(r["test_count"] for r in rows)
    median_density = (
        sorted(r["density"] for r in rows)[len(rows) // 2] if rows else 0.0
    )

    # Outliers
    over_invested = sorted(
        [r for r in rows if r["fan_in"] <= 2 and r["test_count"] >= 20],
        key=lambda r: -r["test_count"],
    )[: args.top]

    under_invested = sorted(
        [r for r in rows if r["fan_in"] >= 10 and r["test_count"] <= 5],
        key=lambda r: -r["fan_in"],
    )[: args.top]

    high_density = sorted(
        [r for r in rows if r["fan_in"] >= 3],
        key=lambda r: -r["density"],
    )[: args.top]

    low_density = sorted(
        [r for r in rows if r["fan_in"] >= 5 and r["test_count"] >= 1],
        key=lambda r: r["density"],
    )[: args.top]

    # Gini coefficient on test-attribution distribution (0=perfectly even,
    # 1=all tests on one module). Industry sweet spot for test allocation
    # is roughly 0.4-0.6 (some natural concentration on hot paths).
    test_counts_only = sorted(r["test_count"] for r in rows if r["test_count"] > 0)
    n = len(test_counts_only)
    if n > 0:
        cum = sum((i + 1) * v for i, v in enumerate(test_counts_only))
        total = sum(test_counts_only)
        gini = (2.0 * cum) / (n * total) - (n + 1) / n if total > 0 else 0.0
    else:
        gini = 0.0

    # Top-decile concentration: what fraction of total test-attributions
    # land on the top-10% most-tested subjects?
    sorted_desc = sorted((r["test_count"] for r in rows), reverse=True)
    top_10_pct = max(1, len(sorted_desc) // 10)
    top_decile_share = (
        sum(sorted_desc[:top_10_pct]) / max(1, sum(sorted_desc))
    )

    summary = {
        "fan_in_source": fan_in_source,
        "total_test_funcs": total_tests,
        "total_test_attributions": sum_tests_attributed,
        "subjects_indexed": len(all_subjects),
        "median_density": round(median_density, 2),
        "gini_test_attributions": round(gini, 3),
        "top_decile_concentration_pct": round(100.0 * top_decile_share, 1),
        "over_invested_count": len(over_invested),
        "under_invested_count": len(under_invested),
    }

    if args.json:
        print(json.dumps({
            "summary": summary,
            "over_invested": over_invested,
            "under_invested": under_invested,
            "high_density": high_density,
            "low_density": low_density,
        }, indent=2))
        return 0

    # Markdown report
    print("# Test Concentration Risk Analysis\n")
    print("## Summary\n")
    print("| Metric | Value |")
    print("|---|---:|")
    print(f"| fan_in source | `{fan_in_source}` |")
    print(f"| Total test functions (AST count) | {total_tests} |")
    print(f"| Total test→subject attributions | {sum_tests_attributed} |")
    print(f"| Subject modules indexed | {len(all_subjects)} |")
    print(f"| Median test/fan_in density | {median_density:.2f} |")
    print(f"| Gini coefficient (test attribution) | {gini:.3f} |")
    print(f"| Top-10% subjects hold this share of all attributions | {100.0*top_decile_share:.1f}% |")
    print(f"| Over-invested subjects (low fan_in, ≥20 tests) | {len(over_invested)} |")
    print(f"| Under-invested subjects (≥10 fan_in, ≤5 tests) | {len(under_invested)} |")
    print()

    print(f"## OVER-INVESTED (top {args.top}) — high test_count, low fan_in\n")
    print("| subject | test_count | fan_in | density |")
    print("|---|---:|---:|---:|")
    for r in over_invested:
        print(f"| `{r['subject']}` | {r['test_count']} | {r['fan_in']} | {r['density']} |")
    print()

    print(f"## UNDER-INVESTED (top {args.top}) — high fan_in, low test_count\n")
    print("| subject | fan_in | test_count | density |")
    print("|---|---:|---:|---:|")
    for r in under_invested:
        print(f"| `{r['subject']}` | {r['fan_in']} | {r['test_count']} | {r['density']} |")
    print()

    print(f"## HIGH-DENSITY (top {args.top}) — most-tested-per-fan_in\n")
    print("| subject | density | test_count | fan_in |")
    print("|---|---:|---:|---:|")
    for r in high_density:
        print(f"| `{r['subject']}` | {r['density']} | {r['test_count']} | {r['fan_in']} |")
    print()

    print(f"## LOW-DENSITY (top {args.top}) — least-tested-per-fan_in (with fan_in ≥ 5)\n")
    print("| subject | density | test_count | fan_in |")
    print("|---|---:|---:|---:|")
    for r in low_density:
        print(f"| `{r['subject']}` | {r['density']} | {r['test_count']} | {r['fan_in']} |")

    return 0


if __name__ == "__main__":
    sys.exit(main())
