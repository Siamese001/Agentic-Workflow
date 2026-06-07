"""Classify test files for **pytest-marker ergonomics** using the ADG.

⚠️ NOT THE COVERAGE SSOT.
   The authoritative views for "what is exercised by tests" live INSIDE the
   ADG snapshot itself:

     - `mv_eval_coverage_by_path`   — eval coverage % per layer (action nodes
                                       covered vs. gap)
     - `mv_l2_phase_coverage`        — L2 execution-phase coverage
                                       (enforcement, execution_gateway,
                                       guardrail, healing, phase_unknown)
     - `mv_modified_area_regressions` — recently-modified files with
                                         outstanding violations
     - `test_stubs`                  — Mock-instantiation density per test
                                       file (signal: heavy mocking)

   For any "what's covered / what's missing / what's the testing hotspot"
   question, query those views directly. They are pre-materialized,
   deterministic, and rebuilt with every ADG snapshot.

Why this script still exists:
   The ADG views answer coverage questions but do NOT emit pytest markers.
   This script produces a per-test-file classification JSON
   (`artifacts/test_inventory/test_adg_classification.json`) that the root
   `conftest.py` hook reads to apply markers like `adg_l5`, `adg_apps_rg`,
   `adg_runtime`, `adg_otel`. Those markers are *filter ergonomics* on top
   of the existing pytest marker system — they let you run, e.g.,
   `pytest -m "adg_l5 and not adg_stdlib"` without recomputing anything.

   This file does NOT compute coverage. It infers per-file fan-out from the
   `nodes` and `edges` tables to drive marker assignment. If you find
   yourself reaching for it to answer a coverage question, stop and use the
   `mv_*` views above.

Original docstring follows:
---------------------------

The ADG already records every import edge and resolved call from each test
module to production code, with the production-side layer attached.

For each test file we ask the ADG:
  1. What production modules does it import (transitively, via `imports` edges)?
  2. What layers do those targets live in (L0..L6)?
  3. Does it touch OTel, runtime ADG, real I/O surfaces by node lookup?
  4. Does it have any outgoing `flows_to` / `writes_to` / `emits_side_effect`
     semantic edges (true behavioral exercise)?

Output columns per test file:
  - distinct_prod_imports: count of unique production modules pulled in
  - prod_layers: sorted set of layer codes touched (e.g. "L0,L2,L4")
  - touches_otel_node: bool — imports any OTel-tagged production node
  - touches_runtime_node: bool — imports L2_execution / L3_orchestration runtime
  - touches_safety_node: bool — imports L5_safety
  - has_semantic_edges: bool — at least one flows_to / writes_to / emits_side_effect
                        edge from a test node into production
  - test_class: derived classification

The classification rule is layered:
  - "production_runtime"   : touches L2/L3 runtime AND has semantic edges
  - "production_contract"  : touches production but no semantic edges, only imports
  - "tooling_only"         : only imports `tools/` or `ops_scripts/` (not production)
  - "stdlib_only"          : no production imports detected (likely import_smoke)

Run:
    python tools/analysis/test_adg_classifier.py

Output:
    artifacts/test_inventory/test_adg_classification.json
    artifacts/test_inventory/test_adg_classification.md
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "artifacts" / "test_inventory"

# Layer codes we care about for "runtime" semantics
RUNTIME_LAYERS = {"L2", "L3"}
SAFETY_LAYERS = {"L5"}

# Canonical agentic_core layers (markers will be adg_l0 .. adg_l6)
AGENTIC_CORE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")

# All apps_* roots (markers will be adg_apps_<name>)
APPS_ROOTS = (
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
)

# Semantic edge relation types that prove a test exercises real behavior
SEMANTIC_EDGE_TYPES = (
    "flows_to",
    "writes_to",
    "emits_side_effect",
    "controls_flow",
    "resolves_callsite",
)


def _latest_snapshot() -> Path:
    candidates = sorted((REPO / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
    if not candidates:
        raise SystemExit("ERROR: no ADG snapshot found at artifacts/adg/adg_indexed_*.sqlite")
    return candidates[-1]


def _table_exists(con: sqlite3.Connection, name: str) -> bool:
    cur = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (name,))
    return cur.fetchone() is not None


def _get_columns(con: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in con.execute(f"PRAGMA table_info({table})").fetchall()]


def _detect_schema(con: sqlite3.Connection) -> dict[str, Any]:
    """Adapt to the real ADG schema; return keys we'll use downstream."""
    schema = {
        "nodes_table": "nodes",
        "edges_table": "edges",
        "node_id_col": "id",
        "node_file_col": None,
        "node_layer_col": None,
        "edge_src_col": None,
        "edge_dst_col": None,
        "edge_type_col": None,
    }
    if not _table_exists(con, "nodes") or not _table_exists(con, "edges"):
        raise SystemExit("ERROR: ADG snapshot missing 'nodes' or 'edges' table")

    node_cols = _get_columns(con, "nodes")
    edge_cols = _get_columns(con, "edges")

    for cand in ("file_path", "resolved_path", "path", "file"):
        if cand in node_cols:
            schema["node_file_col"] = cand
            break
    for cand in ("layer", "arch_layer", "layer_code"):
        if cand in node_cols:
            schema["node_layer_col"] = cand
            break

    for cand in ("src_id", "source_id", "from_id"):
        if cand in edge_cols:
            schema["edge_src_col"] = cand
            break
    for cand in ("dst_id", "target_id", "to_id"):
        if cand in edge_cols:
            schema["edge_dst_col"] = cand
            break
    for cand in ("relation_type", "edge_type", "type", "relation"):
        if cand in edge_cols:
            schema["edge_type_col"] = cand
            break

    missing = [k for k, v in schema.items() if v is None]
    if missing:
        raise SystemExit(
            f"ERROR: could not detect ADG columns: {missing}\n"
            f"  node_cols={node_cols}\n  edge_cols={edge_cols}"
        )
    return schema


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = _latest_snapshot()
    print(f"Using snapshot: {snapshot.relative_to(REPO)}")

    con = sqlite3.connect(f"file:{snapshot}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    schema = _detect_schema(con)
    nf = schema["node_file_col"]
    nl = schema["node_layer_col"]
    es = schema["edge_src_col"]
    ed = schema["edge_dst_col"]
    et = schema["edge_type_col"]

    # 1. Map every test-side node id -> file path
    test_nodes = con.execute(
        f"SELECT id, {nf} AS file FROM nodes WHERE {nf} LIKE 'tests/%' AND {nf} NOT LIKE 'tests/_archived_obsolete/%'"
    ).fetchall()
    print(f"Test-side nodes: {len(test_nodes):,}")

    # 2. Build per-test-file aggregates by walking outgoing edges
    by_file: dict[str, dict[str, Any]] = {}
    for row in test_nodes:
        f = row["file"]
        bucket = by_file.setdefault(
            f,
            {
                "file": f,
                "prod_imports": set(),
                "prod_layers": set(),
                "agentic_core_layers": set(),  # subset of L0..L6 actually imported
                "apps_targets": set(),  # apps_* roots actually imported
                "touches_otel_node": False,
                "touches_runtime_node": False,
                "touches_safety_node": False,
                "tooling_imports": set(),
                "semantic_edges": 0,
            },
        )
        # outgoing edges from this test node
        cur = con.execute(
            f"SELECT e.{ed} AS dst, e.{et} AS rtype, n2.{nf} AS dst_file, n2.{nl} AS dst_layer "
            f"FROM edges e JOIN nodes n2 ON n2.id = e.{ed} "
            f"WHERE e.{es} = ?",
            (row["id"],),
        )
        for e in cur:
            dst_file = e["dst_file"] or ""
            dst_layer = (e["dst_layer"] or "").upper()
            rtype = e["rtype"] or ""

            if rtype in SEMANTIC_EDGE_TYPES:
                bucket["semantic_edges"] += 1

            # Classify destination
            if dst_file.startswith("agentic_core/") or dst_file.startswith("apps_"):
                bucket["prod_imports"].add(dst_file)
                if dst_layer:
                    bucket["prod_layers"].add(dst_layer)
                # Per-layer fan-out for agentic_core
                if dst_file.startswith("agentic_core/"):
                    parts = dst_file.split("/", 2)
                    if (
                        len(parts) >= 2
                        and parts[1].startswith("L")
                        and len(parts[1]) >= 2
                        and parts[1][1].isdigit()
                    ):
                        layer_code = parts[1][:2]  # "L0_routing" -> "L0"
                        if layer_code in AGENTIC_CORE_LAYERS:
                            bucket["agentic_core_layers"].add(layer_code)
                # Per-app fan-out
                if dst_file.startswith("apps_"):
                    app_root = dst_file.split("/", 1)[0]
                    if app_root in APPS_ROOTS:
                        bucket["apps_targets"].add(app_root)
                if dst_layer in RUNTIME_LAYERS:
                    bucket["touches_runtime_node"] = True
                if dst_layer in SAFETY_LAYERS:
                    bucket["touches_safety_node"] = True
                if (
                    "otel" in dst_file.lower()
                    or "telemetry" in dst_file.lower()
                    or "trace" in dst_file.lower()
                ):
                    bucket["touches_otel_node"] = True
            elif dst_file.startswith("tools/") or dst_file.startswith("ops_scripts/"):
                bucket["tooling_imports"].add(dst_file)
            elif "opentelemetry" in dst_file or "otel" in dst_file.lower():
                bucket["touches_otel_node"] = True

    # 3. Classify each test file
    rows = []
    for f, b in by_file.items():
        if b["prod_imports"] and b["touches_runtime_node"] and b["semantic_edges"] > 0:
            cls = "production_runtime"
        elif b["prod_imports"] and b["semantic_edges"] > 0:
            cls = "production_behavioral"
        elif b["prod_imports"]:
            cls = "production_contract"
        elif b["tooling_imports"]:
            cls = "tooling_only"
        else:
            cls = "stdlib_only"
        rows.append(
            {
                "file": f,
                "test_class": cls,
                "distinct_prod_imports": len(b["prod_imports"]),
                "prod_layers": ",".join(sorted(b["prod_layers"])),
                "agentic_core_layers": sorted(b["agentic_core_layers"]),
                "apps_targets": sorted(b["apps_targets"]),
                "touches_otel_node": b["touches_otel_node"],
                "touches_runtime_node": b["touches_runtime_node"],
                "touches_safety_node": b["touches_safety_node"],
                "semantic_edges": b["semantic_edges"],
                "tooling_imports": len(b["tooling_imports"]),
            }
        )

    rows.sort(key=lambda r: (r["test_class"], -r["distinct_prod_imports"]))

    # Write per-file JSON
    out_json = OUT_DIR / "test_adg_classification.json"
    out_json.write_text(json.dumps(rows, indent=1), encoding="utf-8")

    # Aggregate summary
    by_class: dict[str, int] = {}
    by_layer: dict[str, int] = {}
    by_core_layer: dict[str, int] = {}
    by_app: dict[str, int] = {}
    otel_files = 0
    safety_files = 0
    runtime_files = 0
    sem_edge_files = 0
    for r in rows:
        by_class[r["test_class"]] = by_class.get(r["test_class"], 0) + 1
        for layer in r["prod_layers"].split(","):
            if layer:
                by_layer[layer] = by_layer.get(layer, 0) + 1
        for cl in r["agentic_core_layers"]:
            by_core_layer[cl] = by_core_layer.get(cl, 0) + 1
        for app in r["apps_targets"]:
            by_app[app] = by_app.get(app, 0) + 1
        if r["touches_otel_node"]:
            otel_files += 1
        if r["touches_safety_node"]:
            safety_files += 1
        if r["touches_runtime_node"]:
            runtime_files += 1
        if r["semantic_edges"] > 0:
            sem_edge_files += 1

    summary = [
        "# ADG-Driven Test Classification",
        "",
        f"Snapshot: `{snapshot.relative_to(REPO).as_posix()}`",
        f"Test files seen by ADG: **{len(rows):,}**",
        "",
        "## Classification",
        "",
        "| Class | Files | % | Definition |",
        "|---|---:|---:|---|",
    ]
    defs = {
        "production_runtime": "Imports L2/L3 production AND has semantic edges (real exercise)",
        "production_behavioral": "Imports production AND has semantic edges (any layer)",
        "production_contract": "Imports production but only `imports` edges (no flows_to/writes_to/...)",
        "tooling_only": "Only imports `tools/` or `ops_scripts/` — not production",
        "stdlib_only": "No production or tooling imports detected (import-smoke / pure stdlib)",
    }
    total = max(len(rows), 1)
    for cls, defn in defs.items():
        n = by_class.get(cls, 0)
        summary.append(f"| `{cls}` | {n:,} | {100 * n / total:.1f}% | {defn} |")

    summary += [
        "",
        "## Behavior axes (orthogonal — a file may match more than one)",
        "",
        "| Axis | Files | % |",
        "|---|---:|---:|",
        f"| Imports OTel/telemetry/trace node | {otel_files:,} | {100 * otel_files / total:.1f}% |",
        f"| Touches L2/L3 runtime layer | {runtime_files:,} | {100 * runtime_files / total:.1f}% |",
        f"| Touches L5 safety layer | {safety_files:,} | {100 * safety_files / total:.1f}% |",
        f"| Has any semantic edge (flows_to / writes_to / emits_side_effect / controls_flow / resolves_callsite) | {sem_edge_files:,} | {100 * sem_edge_files / total:.1f}% |",
        "",
        "## Test-file fan-out by production layer",
        "",
        "| Layer | Files importing it | % |",
        "|---|---:|---:|",
    ]
    for layer in sorted(by_layer):
        n = by_layer[layer]
        summary.append(f"| `{layer}` | {n:,} | {100 * n / total:.1f}% |")

    summary += [
        "",
        "## Test-file fan-out by `agentic_core/L0..L6` (path-derived)",
        "",
        "| Layer | Files importing it | % | pytest marker |",
        "|---|---:|---:|---|",
    ]
    for layer in AGENTIC_CORE_LAYERS:
        n = by_core_layer.get(layer, 0)
        summary.append(
            f"| `agentic_core/{layer}_*` | {n:,} | {100 * n / total:.1f}% | `adg_{layer.lower()}` |"
        )

    summary += [
        "",
        "## Test-file fan-out by `apps_*` target",
        "",
        "| App | Files importing it | % | pytest marker |",
        "|---|---:|---:|---|",
    ]
    for app in APPS_ROOTS:
        n = by_app.get(app, 0)
        summary.append(f"| `{app}/` | {n:,} | {100 * n / total:.1f}% | `adg_{app}` |")

    summary += [
        "",
        "## Example invocations",
        "",
        "```bash",
        "pytest -m adg_l0                    # tests importing agentic_core/L0_*",
        "pytest -m adg_l5                    # safety-layer tests",
        'pytest -m "adg_l2 and adg_l3"       # tests touching both runtime layers',
        'pytest -m "adg_l5 and adg_runtime"  # safety tests with semantic edges',
        "pytest -m adg_apps_rg               # tests touching apps_rg/",
        'pytest -m "adg_apps_eval or adg_apps_exec"',
        'pytest -m "not adg_stdlib"          # everything except no-import tests',
        "```",
    ]

    out_md = OUT_DIR / "test_adg_classification.md"
    out_md.write_text("\n".join(summary) + "\n", encoding="utf-8")

    print(f"\nWrote: {out_json.relative_to(REPO).as_posix()}")
    print(f"Wrote: {out_md.relative_to(REPO).as_posix()}")
    print()
    print("\n".join(summary[:24]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
