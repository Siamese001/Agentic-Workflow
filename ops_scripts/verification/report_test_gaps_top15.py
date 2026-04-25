"""Top-15 test coverage gap report — fan-in (blast radius) + fan-out (integration seam) + layer.

This is a thin companion to ``report_risk_weighted_test_gaps.py``. It reuses
that module's resolver and scoring primitives, then ranks the top-15
opportunities to improve testing coverage along TWO complementary axes:

  - **Fan-In rank** (already computed by the parent module): untested module
    with high prod fan-in = high blast radius if it breaks. Highest-leverage
    UNIT-test target.

  - **Fan-Out rank** (new here): untested module with high outgoing imports
    to first-party prod modules = many internal seams. Highest-leverage
    INTEGRATION-test target — one test exercises many downstream paths.

The Top-15 selection is a 50/50 union of both ranks, deduplicated, then
ordered by combined score = ``gap_score_in + 0.6 * gap_score_out``. Layer
multiplier (adg-canonical-invariants.md §6) is applied to both axes.

Outputs:
  artifacts/test_gaps/top15_<timestamp>.json
  artifacts/test_gaps/top15_<timestamp>.md
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.verification.report_risk_weighted_test_gaps import (  # noqa: E402
    LAYER_MULTIPLIER,
    _augment_with_importorskip,
    _symbol_to_module_paths,
    is_source_file,
    layer_mult,
)


def _latest_adg() -> Path:
    cands = sorted(
        p for p in glob.glob(str(REPO_ROOT / "artifacts" / "adg" / "adg_indexed_*.sqlite"))
        if "99999999" not in p and not p.endswith(".tmp")
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
    sys.stderr.write(
        f"\r{color}[{bar}]\033[0m {int(pct*100):3d}% ({i}/{total}) {label}{eta}   "
    )
    sys.stderr.flush()
    if i >= total:
        sys.stderr.write("\n")


def load_modules_with_fanin_and_fanout(
    db: Path,
) -> Tuple[List[dict], Dict[int, int], Dict[int, int], Dict[int, int]]:
    """Return (modules, test_importer_count, prod_fanin, prod_fanout) by module id.

    fanout = count of distinct first-party (non-test) destination modules this
    module imports. Symbol-targeted imports are resolved back to their owning
    module so dotted ``a.b.c.symbol`` and ``path/to/file.py::symbol`` both
    collapse to the module id.
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
    id_to_layer: Dict[int, str] = {m["id"]: m["layer"] for m in modules}

    print("[info] loading import edges (fan-in + fan-out)...", file=sys.stderr)
    test_importers: Dict[int, set] = {}
    prod_fanin: Dict[int, set] = {}
    prod_fanout: Dict[int, set] = {}

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
            if mod_path.endswith(".py"):
                dst_mod_id = path_to_module_id.get(mod_path[:-3] + "/__init__.py")
                if dst_mod_id is not None:
                    break
        if dst_mod_id is None:
            unresolved += 1
            continue
        is_test = src_layer == "L_TEST"
        if is_test:
            test_importers.setdefault(dst_mod_id, set()).add(src_id)
        else:
            prod_fanin.setdefault(dst_mod_id, set()).add(src_id)
            # fan-out only counts edges where BOTH endpoints are first-party prod modules
            if id_to_layer.get(src_id) != "L_TEST":
                prod_fanout.setdefault(src_id, set()).add(dst_mod_id)
    _progress(total, total, "resolving imports", start)
    print(f"[info] unresolved import targets: {unresolved}/{total}", file=sys.stderr)

    test_importers = _augment_with_importorskip(REPO_ROOT / "tests", path_to_module_id, test_importers)

    test_counts = {k: len(v) for k, v in test_importers.items()}
    fanin_counts = {k: len(v) for k, v in prod_fanin.items()}
    fanout_counts = {k: len(v) for k, v in prod_fanout.items()}
    conn.close()
    return modules, test_counts, fanin_counts, fanout_counts


def gap_score_fanin(layer: str, ti: int, fi: int) -> float:
    test_proxy = min(ti / 2.0, 1.0)
    return round((1 - test_proxy) * (1.0 + math.log10(1.0 + fi)) * layer_mult(layer), 4)


def gap_score_fanout(layer: str, ti: int, fo: int) -> float:
    test_proxy = min(ti / 2.0, 1.0)
    return round((1 - test_proxy) * (1.0 + math.log10(1.0 + fo)) * layer_mult(layer), 4)


def build_top15(db: Path) -> dict:
    print(f"[info] ADG snapshot: {db.name}", file=sys.stderr)
    modules, test_imp, prod_fi, prod_fo = load_modules_with_fanin_and_fanout(db)
    rows: List[dict] = []
    for mod in modules:
        path = (mod["path"] or "").replace("\\", "/")
        if not is_source_file(path):
            continue
        ti = test_imp.get(mod["id"], 0)
        fi = prod_fi.get(mod["id"], 0)
        fo = prod_fo.get(mod["id"], 0)
        rows.append({
            "path": path,
            "layer": mod["layer"],
            "test_importers": ti,
            "prod_fan_in": fi,
            "prod_fan_out": fo,
            "gap_score_fanin": gap_score_fanin(mod["layer"], ti, fi),
            "gap_score_fanout": gap_score_fanout(mod["layer"], ti, fo),
        })
    untested = [r for r in rows if r["test_importers"] == 0]

    # Top-N by each axis
    by_fanin = sorted(untested, key=lambda r: r["gap_score_fanin"], reverse=True)
    by_fanout = sorted(untested, key=lambda r: r["gap_score_fanout"], reverse=True)

    # Combined Top-15: union ranked by fanin + 0.6 * fanout, then dedup
    seen: set[str] = set()
    combined_pool: List[dict] = []
    # Take top 25 from each axis to give the combined ranker a generous pool
    for r in by_fanin[:25] + by_fanout[:25]:
        if r["path"] in seen:
            continue
        seen.add(r["path"])
        r2 = dict(r)
        r2["combined_score"] = round(
            r["gap_score_fanin"] + 0.6 * r["gap_score_fanout"], 4
        )
        combined_pool.append(r2)
    combined_pool.sort(key=lambda r: r["combined_score"], reverse=True)
    top15 = combined_pool[:15]

    return {
        "snapshot": db.name,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_source_modules": len(rows),
        "untested_modules": len(untested),
        "top15": top15,
        "top10_fanin_only": by_fanin[:10],
        "top10_fanout_only": by_fanout[:10],
    }


def write_outputs(report: dict, out_dir: Path) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%m%d%Y_%H%M")
    json_path = out_dir / f"top15_{ts}.json"
    md_path = out_dir / f"top15_{ts}.md"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# Top 15 Test Coverage Opportunities (ADG fan-in + fan-out)",
        "",
        f"- **Snapshot**: `{report['snapshot']}`",
        f"- **Generated (UTC)**: {report['generated_utc']}",
        f"- **Total source modules**: {report['total_source_modules']}",
        f"- **Untested**: {report['untested_modules']}",
        "",
        "## Top 15 — Combined (fan-in + 0.6 × fan-out, layer-weighted)",
        "",
        "| # | Layer | Path | Test Imp | Fan-In | Fan-Out | Score-In | Score-Out | Combined |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(report["top15"], 1):
        lines.append(
            f"| {i} | `{r['layer']}` | `{r['path']}` | {r['test_importers']} | "
            f"{r['prod_fan_in']} | {r['prod_fan_out']} | {r['gap_score_fanin']} | "
            f"{r['gap_score_fanout']} | **{r['combined_score']}** |"
        )

    lines += [
        "",
        "## Top 10 — Fan-In only (unit-test priority: high blast radius)",
        "",
        "| # | Layer | Path | Fan-In | Score |",
        "|---:|---|---|---:|---:|",
    ]
    for i, r in enumerate(report["top10_fanin_only"], 1):
        lines.append(
            f"| {i} | `{r['layer']}` | `{r['path']}` | {r['prod_fan_in']} | {r['gap_score_fanin']} |"
        )

    lines += [
        "",
        "## Top 10 — Fan-Out only (integration-test priority: many seams)",
        "",
        "| # | Layer | Path | Fan-Out | Score |",
        "|---:|---|---|---:|---:|",
    ]
    for i, r in enumerate(report["top10_fanout_only"], 1):
        lines.append(
            f"| {i} | `{r['layer']}` | `{r['path']}` | {r['prod_fan_out']} | {r['gap_score_fanout']} |"
        )

    lines += [
        "",
        "## Method",
        "",
        "- **Fan-In** = incoming `imports` edges from non-test modules → blast radius.",
        "- **Fan-Out** = outgoing `imports` edges to first-party prod modules → seam count.",
        "- **Layer multiplier**: L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75 "
        "(adg-canonical-invariants.md §6).",
        "- **Score-In**: `(1 - min(test_importers/2, 1)) * (1 + log10(1 + fan_in)) * layer_mult`",
        "- **Score-Out**: same shape with `fan_out`.",
        "- **Combined**: `Score-In + 0.6 × Score-Out` — fan-in is the primary signal "
        "(blast radius is what you protect against); fan-out is a tie-breaker that "
        "favors integration-rich seams.",
        "",
        f"ADG Provenance: backend=sqlite, snapshot={report['snapshot']}",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--adg", type=Path, default=None, help="Path to adg_indexed_*.sqlite")
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "artifacts" / "test_gaps")
    args = ap.parse_args()

    db = args.adg or _latest_adg()
    report = build_top15(db)
    json_path, md_path = write_outputs(report, args.out_dir)
    print(f"\nWrote: {json_path}")
    print(f"Wrote: {md_path}")
    print("\nTop 15 untested modules (combined fan-in + fan-out, layer-weighted):")
    for i, r in enumerate(report["top15"], 1):
        print(
            f"  {i:2d}. [{r['layer']}] {r['path']}  "
            f"(in={r['prod_fan_in']} out={r['prod_fan_out']} score={r['combined_score']})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
