"""Risk-weighted test COVERAGE report (Stage 1 + Stage 2).

Reports structural test coverage (% of modules with >=1 test-importer), NOT
the inverted gap rate. A layer showing "Coverage 29%" has 71% of modules
uncovered. Rank still uses gap_score (low-coverage + high-blast-radius first)
so the top-N tables prioritize the same modules, just with human-friendly
coverage framing in the summary.

Stage 1 — structural test coverage via ADG:
  For every source module (non-L_TEST), count incoming `imports` edges whose
  source module lives in `L_TEST`. A module with zero such imports is a
  structural test gap. Rank by:

      gap_score = (1 - clamp(test_importers / 2, 0, 1))
                  * (1 + log10(1 + prod_fan_in))
                  * layer_multiplier(layer)

  where `prod_fan_in` is incoming `imports` from non-test modules (blast radius)
  and layer_multiplier follows adg-canonical-invariants.md §6
  (L0/L5 x2.0, L3/L4 x1.75, L1/L2 x1.0, L6 x0.75, L_* x1.0).

Stage 2 — changed-code TGA:
  Filter Stage 1 output to modules touched in the last N days (default 14)
  using `git log --since=...`. Recently-changed + untested + high fan-in is
  the highest-risk bucket.

Outputs:
  artifacts/test_gaps/risk_weighted_<timestamp>.json
  artifacts/test_gaps/risk_weighted_<timestamp>.md
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]

LAYER_MULTIPLIER: Dict[str, float] = {
    "L0": 2.0,
    "L5": 2.0,
    "L3": 1.75,
    "L4": 1.75,
    "L1": 1.0,
    "L2": 1.0,
    "L6": 0.75,
}


def layer_mult(layer: str) -> float:
    return LAYER_MULTIPLIER.get(layer, 1.0)


def _latest_adg() -> Path:
    cands = sorted(
        p
        for p in glob.glob(str(REPO_ROOT / "artifacts" / "adg" / "adg_indexed_*.sqlite"))
        if "99999999" not in p
    )
    if not cands:
        sys.exit("ERROR: no adg_indexed_*.sqlite snapshot found under artifacts/adg/")
    return Path(cands[-1])


def _progress(i: int, total: int, label: str, start: float) -> None:
    if total <= 0:
        return
    pct = i / total
    fill = int(40 * pct)
    bar = "\u2588" * fill + "\u2591" * (40 - fill)
    if pct >= 0.90:
        color = "\033[92m"
    elif pct >= 0.70:
        color = "\033[94m"
    elif pct >= 0.40:
        color = "\033[93m"
    else:
        color = "\033[91m"
    eta = ""
    elapsed = time.monotonic() - start
    if pct > 0.02 and elapsed > 1:
        remaining = elapsed * (1 - pct) / pct
        eta = f" - ETA: {int(remaining)}s"
    sys.stderr.write(f"\r{color}[{bar}]\033[0m {int(pct * 100):3d}% ({i}/{total}) {label}{eta}   ")
    sys.stderr.flush()
    if i >= total:
        sys.stderr.write("\n")


_SYMBOL_PREFIX = "ADG::Symbol::"


def _symbol_to_module_paths(sym_name: str) -> List[str]:
    """Return candidate enclosing module file paths for a symbol adg_name.

    Handles three shapes observed in ADG:
      - `ADG::Symbol::path/to/file.py::func`        -> ['path/to/file.py']
      - `ADG::Symbol::a.b.c.module_name`            -> ['a/b/c/module_name.py',
                                                        'a/b/c.py']
      - `ADG::Symbol::a.b.c.func`                   -> same candidates

    The dotted form is ambiguous because `from pkg.sub import module_name`
    and `from pkg.sub.module import func` both produce `pkg.sub.module_name`
    / `pkg.sub.module.func` respectively. We emit both candidates (full
    dotted path as module, and stripped-final-segment path as module) and
    let the caller pick whichever matches a known module id. This closes
    the false-negative where tests doing `from pkg import module as seam`
    were not credited to `pkg/module.py`.
    """
    if not sym_name or not sym_name.startswith(_SYMBOL_PREFIX):
        return []
    body = sym_name[len(_SYMBOL_PREFIX) :]
    if "::" in body:
        return [body.split("::", 1)[0].replace("\\", "/")]
    if body.endswith(".*"):
        body = body[:-2]
    candidates: List[str] = []
    # Candidate 1: treat the FULL dotted path as a module path.
    # Covers `from pkg import module_name` producing `pkg.module_name`.
    candidates.append(body.replace(".", "/") + ".py")
    # Candidate 2: strip trailing segment (assume it is a symbol name inside a module).
    # Covers `from pkg.module import func` producing `pkg.module.func`.
    if "." in body:
        candidates.append(body.rsplit(".", 1)[0].replace(".", "/") + ".py")
    return candidates


def load_modules_and_fanin(db: Path) -> Tuple[List[dict], Dict[int, int], Dict[int, int]]:
    """Return (modules, test_importer_count_by_id, prod_fanin_by_id).

    Resolves symbol-target imports back to their enclosing module so we count
    test -> module coverage rather than leaving every module at zero.
    """
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, adg_name, layer, resolved_path
        FROM nodes
        WHERE entity_type='module' AND identity_kind='repo_module'
        """
    )
    modules = [
        {"id": r[0], "adg_name": r[1], "layer": r[2], "path": (r[3] or "").replace("\\", "/")}
        for r in cur.fetchall()
    ]
    path_to_module_id: Dict[str, int] = {m["path"]: m["id"] for m in modules if m["path"]}
    # Also index by "dotted/form.py" reconstruction, plus __init__.py fallback.

    print(
        "[info] computing test-importer and prod fan-in via symbol->module resolution...",
        file=sys.stderr,
    )
    test_importers: Dict[int, set] = {}
    prod_fanin: Dict[int, set] = {}

    cur.execute(
        """
        SELECT e.src_id, n_src.layer, n_dst.adg_name
        FROM edges e
        JOIN nodes n_src ON n_src.id = e.src_id
        JOIN nodes n_dst ON n_dst.id = e.dst_id
        WHERE e.relation_type='imports'
        """
    )
    rows = cur.fetchall()
    start = time.monotonic()
    total = len(rows)
    unresolved = 0
    for i, (src_id, src_layer, dst_name) in enumerate(rows, 1):
        if i % 10000 == 0 or i == total:
            _progress(i, total, "resolving imports", start)
        candidates = _symbol_to_module_paths(dst_name)
        if not candidates:
            unresolved += 1
            continue
        dst_mod_id: int | None = None
        for mod_path in candidates:
            dst_mod_id = path_to_module_id.get(mod_path)
            if dst_mod_id is not None:
                break
            # Try __init__.py form.
            if mod_path.endswith(".py"):
                dst_mod_id = path_to_module_id.get(mod_path[:-3] + "/__init__.py")
                if dst_mod_id is not None:
                    break
        if dst_mod_id is None:
            unresolved += 1
            continue
        bucket = test_importers if src_layer == "L_TEST" else prod_fanin
        bucket.setdefault(dst_mod_id, set()).add(src_id)
    _progress(total, total, "resolving imports", start)
    print(f"[info] unresolved import targets: {unresolved}/{total}", file=sys.stderr)

    # Stage 1b: augment with dynamic imports via `pytest.importorskip("a.b.c")`.
    # ADG edges are static-only, so tests that load their subject via importorskip
    # register zero `imports` edges. Scan tests/** for this pattern and credit the
    # target module's test-importer count.
    test_importers = _augment_with_importorskip(REPO_ROOT / "tests", path_to_module_id, test_importers)

    test_counts = {k: len(v) for k, v in test_importers.items()}
    prod_counts = {k: len(v) for k, v in prod_fanin.items()}
    conn.close()
    return modules, test_counts, prod_counts


_IMPORTORSKIP_RE = re.compile(
    r"""importorskip\(\s*['"]([\w\.]+)['"]""",
    re.MULTILINE,
)


def _augment_with_importorskip(
    tests_dir: Path,
    path_to_module_id: Dict[str, int],
    test_importers: Dict[int, set],
) -> Dict[int, set]:
    """Parse `pytest.importorskip('a.b.c')` in test files and credit the target module.

    The ADG records only static `imports` edges. Tests that resolve their subject
    via `pytest.importorskip` show up as untested in Stage 1 despite substantive
    coverage. This pass closes that false-negative.
    """
    if not tests_dir.is_dir():
        return test_importers
    # Build a synthetic src_id per test file to count distinct importers.
    synthetic_src_base = 10**9
    test_files = list(tests_dir.rglob("*.py"))
    print(f"[info] scanning {len(test_files)} test files for importorskip() refs...", file=sys.stderr)
    augmented = 0
    for idx, test_file in enumerate(test_files):
        try:
            text = test_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        matches = _IMPORTORSKIP_RE.findall(text)
        if not matches:
            continue
        synthetic_src = synthetic_src_base + idx
        for dotted in matches:
            mod_path = dotted.replace(".", "/") + ".py"
            dst_mod_id = path_to_module_id.get(mod_path)
            if dst_mod_id is None:
                init_path = mod_path[:-3] + "/__init__.py"
                dst_mod_id = path_to_module_id.get(init_path)
            if dst_mod_id is None:
                continue
            test_importers.setdefault(dst_mod_id, set()).add(synthetic_src)
            augmented += 1
    print(f"[info] importorskip augmented {augmented} (test_file, module) pairs", file=sys.stderr)
    return test_importers


def git_changed_files(since_days: int) -> set[str]:
    """Return set of repo-relative paths changed in the last N days."""
    try:
        out = subprocess.run(
            ["git", "log", f"--since={since_days} days ago", "--name-only", "--pretty=format:"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        print(f"[warn] git log failed: {exc}", file=sys.stderr)
        return set()
    files = {ln.strip().replace("\\", "/") for ln in out.stdout.splitlines() if ln.strip()}
    return files


def is_source_file(path: str) -> bool:
    """Exclude tests, archives, vendored, and non-Python-source paths."""
    if not path or not path.endswith(".py"):
        return False
    bad_prefixes = (
        "tests/",
        "archives/",
        "tools/archive/",
        "docs/archive/windsurf/legacy-tree/",
        "docs/",
        "artifacts/",
        "reports/",
        "data/",
        "node_modules/",
    )
    return not any(path.startswith(p) for p in bad_prefixes)


def score_module(mod: dict, test_importers: int, prod_fanin: int) -> float:
    test_coverage_proxy = min(test_importers / 2.0, 1.0)  # 2+ test files => "covered"
    gap = 1.0 - test_coverage_proxy
    blast = 1.0 + math.log10(1.0 + prod_fanin)
    return round(gap * blast * layer_mult(mod["layer"]), 4)


def build_report(db: Path, since_days: int) -> dict:
    start = time.monotonic()
    print(f"[info] ADG snapshot: {db.name}", file=sys.stderr)
    modules, test_imp, prod_fi = load_modules_and_fanin(db)
    print(f"[info] {len(modules)} modules loaded", file=sys.stderr)

    changed = git_changed_files(since_days)
    print(f"[info] {len(changed)} files changed in last {since_days}d", file=sys.stderr)

    rows: List[dict] = []
    total = len(modules)
    for i, mod in enumerate(modules, 1):
        if i % 500 == 0 or i == total:
            _progress(i, total, "scoring modules", start)
        path = (mod["path"] or "").replace("\\", "/")
        if not is_source_file(path):
            continue
        ti = test_imp.get(mod["id"], 0)
        pf = prod_fi.get(mod["id"], 0)
        score = score_module(mod, ti, pf)
        rows.append(
            {
                "path": path,
                "layer": mod["layer"],
                "test_importers": ti,
                "prod_fan_in": pf,
                "gap_score": score,
                "changed_recently": path in changed,
            }
        )
    _progress(total, total, "scoring modules", start)

    rows.sort(key=lambda r: r["gap_score"], reverse=True)
    untested = [r for r in rows if r["test_importers"] == 0]
    tested = [r for r in rows if r["test_importers"] > 0]
    untested_changed = [r for r in untested if r["changed_recently"]]
    total_mods = max(1, len(rows))
    summary: Dict[str, object] = {
        "snapshot": db.name,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "since_days": since_days,
        "total_source_modules": len(rows),
        "tested_modules": len(tested),
        "coverage_pct": round(100 * len(tested) / total_mods, 2),
        "untested_modules": len(untested),
        "gap_pct": round(100 * len(untested) / total_mods, 2),
        "changed_and_untested": len(untested_changed),
        "by_layer": {},
    }
    by_layer: Dict[str, Dict[str, object]] = {}
    for layer in sorted({r["layer"] for r in rows}):
        in_layer = [r for r in rows if r["layer"] == layer]
        tested_in_layer = [r for r in in_layer if r["test_importers"] > 0]
        denom = max(1, len(in_layer))
        by_layer[layer] = {
            "modules": len(in_layer),
            "tested_modules": len(tested_in_layer),
            "untested_modules": len(in_layer) - len(tested_in_layer),
            "coverage_pct": round(100 * len(tested_in_layer) / denom, 2),
            "gap_pct": round(100 * (len(in_layer) - len(tested_in_layer)) / denom, 2),
        }
    summary["by_layer"] = by_layer
    return {"summary": summary, "rows": rows}


def write_outputs(report: dict, out_dir: Path) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%m%d%Y_%H%M")
    json_path = out_dir / f"risk_weighted_{ts}.json"
    md_path = out_dir / f"risk_weighted_{ts}.md"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    s = report["summary"]
    rows = report["rows"]
    top_overall = [r for r in rows if r["test_importers"] == 0][:30]
    top_changed = [r for r in rows if r["test_importers"] == 0 and r["changed_recently"]][:30]

    lines = [
        "# Risk-Weighted Test Coverage Report",
        "",
        f"- **Snapshot**: `{s['snapshot']}`",
        f"- **Generated (UTC)**: {s['generated_utc']}",
        f"- **Changed-file window**: last {s['since_days']} days",
        f"- **Total source modules scored**: {s['total_source_modules']}",
        f"- **Structural coverage**: {s['tested_modules']}/{s['total_source_modules']} "
        f"(**{s['coverage_pct']}% covered**, {s['gap_pct']}% gap)",
        f"- **Changed AND untested**: {s['changed_and_untested']}",
        "",
        "## Coverage Rate by Layer",
        "",
        "| Layer | Modules | Tested | Coverage % | Untested | Gap % |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for layer, agg in sorted(s["by_layer"].items()):
        lines.append(
            f"| `{layer}` | {agg['modules']} | {agg['tested_modules']} | "
            f"{agg['coverage_pct']}% | {agg['untested_modules']} | {agg['gap_pct']}% |"
        )

    lines += [
        "",
        "## Stage 1 — Top Untested Modules by Risk (all)",
        "",
        "| # | Layer | Path | Prod Fan-In | Gap Score |",
        "|---:|---|---|---:|---:|",
    ]
    for i, r in enumerate(top_overall, 1):
        lines.append(f"| {i} | `{r['layer']}` | `{r['path']}` | {r['prod_fan_in']} | {r['gap_score']} |")

    lines += [
        "",
        f"## Stage 2 — Top Untested + Changed in last {s['since_days']}d",
        "",
        "| # | Layer | Path | Prod Fan-In | Gap Score |",
        "|---:|---|---|---:|---:|",
    ]
    if not top_changed:
        lines.append("| _(none — no recently-changed untested modules)_ |  |  |  |  |")
    else:
        for i, r in enumerate(top_changed, 1):
            lines.append(f"| {i} | `{r['layer']}` | `{r['path']}` | {r['prod_fan_in']} | {r['gap_score']} |")

    lines += [
        "",
        "## Method",
        "",
        "- **Test-importer proxy**: incoming `imports` edges from `L_TEST` modules.",
        "- **Prod fan-in**: incoming `imports` edges from non-test modules (blast radius).",
        "- **Layer multiplier**: L0/L5 x2.0, L3/L4 x1.75, L1/L2 x1.0, L6 x0.75 "
        "(adg-canonical-invariants.md §6).",
        "- **Gap score**: `(1 - min(test_importers/2, 1)) * (1 + log10(1 + prod_fan_in)) * layer_mult`.",
        "- **Stage 2 filter**: `git log --since=<N>d --name-only` intersect untested set.",
        "",
        "ADG Provenance: backend=sqlite, snapshot=" + s["snapshot"],
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--adg", type=Path, default=None, help="Path to adg_indexed_*.sqlite")
    ap.add_argument("--since-days", type=int, default=14, help="Stage 2 window (days)")
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "artifacts" / "test_gaps")
    args = ap.parse_args()

    db = args.adg or _latest_adg()
    report = build_report(db, args.since_days)
    json_path, md_path = write_outputs(report, args.out_dir)
    print(f"\nWrote: {json_path}")
    print(f"Wrote: {md_path}")

    s = report["summary"]
    print(
        f"Summary: {s['tested_modules']}/{s['total_source_modules']} "
        f"modules are structurally covered "
        f"({s['coverage_pct']}% coverage, {s['gap_pct']}% gap); "
        f"{s['changed_and_untested']} untested modules changed in last {s['since_days']}d."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
