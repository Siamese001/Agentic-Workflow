"""Audit: find tests/CIs/governance redundant with the enhanced ADG.

Cross-references:
  1. ADG materialized views (mv_*) — what computed signals exist
  2. ADG P-views (v_p0_*, v_p1_*, v_p2_*, v_p3_*) — pre-classified concerns
  3. R5-W1 detectors (A6 entrypoint, A8 hidden_write, A12 gate_self_test)
  4. R6 backlog detectors (async, no-timeout, mcp-drift, etc.)
  5. Truth expansion tables (module_entrypoints, side_effect_calls, config_references)

Against:
  - CI gates in ops_scripts/ci/check_*.py
  - Test files in tests/unit/**/*.py
  - Governance hooks in .codex/governance/scripts/

Output: a markdown report listing each gate/test with overlap classification.
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADG_DIR = REPO / "artifacts" / "adg"


def _latest_enriched() -> Path:
    candidates = sorted(
        f
        for f in ADG_DIR.iterdir()
        if f.name.startswith("adg_indexed")
        and f.suffix == ".sqlite"
        and "tmp" not in f.name
        and "shm" not in f.name
        and "wal" not in f.name
    )
    for path in reversed(candidates):
        # progress_bar: bounded loop — §16 exempt (small fixed-cost iteration)
        try:
            con = sqlite3.connect(path)
            tables = {
                r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")
            }
            con.close()
            if {"module_entrypoints", "gate_self_consistency", "overlay_violations"} <= tables:
                return path
        except sqlite3.DatabaseError:
            continue
    raise RuntimeError("No enriched snapshot")


# ---------- ADG capability inventory ----------


def adg_inventory(con: sqlite3.Connection) -> dict:
    """Pull all ADG materialized views, P-views, and detector tables."""
    inv: dict = {"mv": [], "p_views": [], "tables": [], "detectors": {}}
    for name, kind in con.execute(
        # progress_bar: bounded loop — §16 exempt (small fixed-cost iteration)
        "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"
    ):
        if name.startswith("mv_"):
            try:
                cnt = con.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
            except sqlite3.OperationalError:
                cnt = -1
            inv["mv"].append((name, cnt))
        elif name.startswith("v_p"):
            try:
                cnt = con.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
            except sqlite3.OperationalError:
                cnt = -1
            inv["p_views"].append((name, cnt))
        elif kind == "table":
            inv["tables"].append(name)
    # Detector counts
    for tbl, label in [
        # progress_bar: bounded loop — §16 exempt (small fixed-cost iteration)
        ("module_entrypoints", "A6"),
        ("side_effect_calls", "A7"),
        ("config_references", "A9"),
        ("test_stubs", "A11"),
        ("gate_self_consistency", "A12"),
        ("overlay_violations", "Overlay"),
        ("violations", "Core SC/AP"),
    ]:
        try:
            cnt = con.execute(f"SELECT COUNT(*) FROM [{tbl}]").fetchone()[0]
            inv["detectors"][label] = (tbl, cnt)
        except sqlite3.OperationalError:
            pass
    return inv


# ---------- CI / test inventory ----------

CI_DIR = REPO / "ops_scripts" / "ci"
WINDSURF_SCRIPTS = REPO / ".codex" / "governance" / "scripts"


def collect_ci_gates() -> list[tuple[Path, str]]:
    """Return [(path, docstring_first_line)] for all CI gate scripts."""
    out: list[tuple[Path, str]] = []
    for py in CI_DIR.rglob("check_*.py"):
        try:
            text = py.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        m = re.search(r'^"""(.+?)(?:"""|\n)', text, re.DOTALL | re.MULTILINE)
        doc = (m.group(1).strip().splitlines()[0] if m else "").strip()
        out.append((py, doc))
    return out


# Keyword → ADG capability mapping. If a gate's name or docstring matches a
# keyword set, flag it as a redundancy candidate against the listed ADG view.
REDUNDANCY_RULES: list[tuple[str, str, tuple[str, ...]]] = [
    # (gate_keyword_regex, adg_capability, related_mv_or_pview)
    (
        r"dead[_-]?(symbol|import|module|code|folder)",
        "mv_unknown_taxonomy_and_orphans / overlay dead_import_resolved",
        ("mv_unknown_taxonomy_and_orphans",),
    ),
    (
        r"layer[_-]?skip|gravity|cross[_-]?layer",
        "v_p0_apps_direct_infra / v_p1_mis_layered_infra",
        ("v_p0_apps_direct_infra", "v_p1_mis_layered_infra"),
    ),
    (
        r"write[_-]?(bypass|sovereignty|surface)",
        "v_p0_write_bypass_uwg / mv_write_sovereignty_paths / A8 hidden_write_outside_uwg",
        ("v_p0_write_bypass_uwg",),
    ),
    (
        r"hardcoded|magic[_-]?(constant|string|number)|literal[_-]?ssot",
        "mv_unknown_taxonomy_and_orphans + grep — partial coverage",
        (),
    ),
    (
        r"observabilit|otel|trace|witness",
        "mv_cross_cutting_witness_tiers / mv_handoff_witness_tiers / mv_runtime_spine_gaps",
        ("mv_cross_cutting_witness_tiers",),
    ),
    (
        r"fanin|fanout|hotspot|chokepoint|centrality",
        "mv_hotspot_centrality / mv_graph_chokepoint_bridges / mv_graph_reverse_dependency_hotspots",
        ("mv_hotspot_centrality",),
    ),
    (
        r"mcp[_-]?(sync|coverage|registry|config|drift)",
        "R6 mcp_contract_drift detector + mcp_tool_declarations",
        ("mv_mcp_contract_drift",),
    ),
    (
        r"agents[_-]?md|coverage",
        "mv_agent_specialization_overlap / mv_agent_tool_ratio",
        ("mv_agent_tool_ratio",),
    ),
    (
        r"entrypoint|cli[_-]?only|hook[_-]?presence",
        "A6 entrypoint_scanner / mv_entrypoint_kind_summary / module_entrypoints",
        ("mv_entrypoint_kind_summary",),
    ),
    (
        r"gate[_-]?(doc|self[_-]?test|consistency|drift)",
        "A12 gate_self_test_scanner / gate_self_consistency",
        (),
    ),
    (
        r"async|fire[_-]?and[_-]?forget|timeout",
        "R6 async_fire_and_forget / external_calls_no_timeout",
        ("mv_async_fire_and_forget_hotspots", "mv_external_calls_no_timeout"),
    ),
    (
        r"shim|rename[_-]?consumer|backward[_-]?compat",
        "R6 mv_rename_shim_consumers / overlay rename_shim_module",
        ("mv_rename_shim_consumers",),
    ),
    (r"cyclomatic|module[_-]?loc|complexity", "(no direct ADG view) — file-level metric", ()),
    (
        r"snapshot|integrity|baseline[_-]?staleness",
        "mv_snapshot_baseline / mv_snapshot_integrity_anomalies / mv_snapshot_regression_summary",
        ("mv_snapshot_integrity_anomalies",),
    ),
    (r"violation[_-]?(aging|sla|backlog)|sc[_-]?ap", "violations table + core SC/AP burndown", ()),
    (
        r"prompt[_-]?(assembly|wiring)|template",
        "mv_prompt_assembly_wiring_gaps",
        ("mv_prompt_assembly_wiring_gaps",),
    ),
    (
        r"replay|trace[_-]?replay|eval[_-]?coverage",
        "mv_replay_surface_gaps / mv_trace_replay_eval_gaps / mv_eval_coverage_by_path",
        ("mv_replay_surface_gaps",),
    ),
    (
        r"task[_-]?contract|structured[_-]?output",
        "mv_task_contract_gaps / mv_structured_output_gaps",
        ("mv_task_contract_gaps",),
    ),
    (r"hitl|reclearance", "mv_hitl_reclearance_gaps", ("mv_hitl_reclearance_gaps",)),
    (
        r"manager[_-]?sprawl|provider[_-]?surface",
        "mv_manager_sprawl / mv_provider_surface_sprawl",
        ("mv_manager_sprawl",),
    ),
    (
        r"critical[_-]?path|blast[_-]?radius",
        "mv_graph_critical_path_blast_radius / mv_critical_path_segments / mv_path_criticality_rollup",
        ("mv_graph_critical_path_blast_radius",),
    ),
    (
        r"exit[_-]?disposition|p7|exit[_-]?gate",
        "mv_exit_disposition_coverage",
        ("mv_exit_disposition_coverage",),
    ),
    (
        r"observability[_-]?(high[_-]?fanin|interference)",
        "mv_observability_interference_breaches / mv_high_fan_in_out_with_defects",
        ("mv_high_fan_in_out_with_defects",),
    ),
    (
        r"determinism|provenance|drift",
        "mv_determinism_provenance_drift / mv_digest_reconciliation",
        ("mv_determinism_provenance_drift",),
    ),
]


def classify_gate(path: Path, doc: str) -> list[tuple[str, str]]:
    """Return list of (capability, related_views) flags for this gate."""
    name = path.name.lower()
    text = name + " " + doc.lower()
    hits: list[tuple[str, str]] = []
    for pattern, capability, _views in REDUNDANCY_RULES:
        if re.search(pattern, text):
            hits.append((pattern, capability))
    return hits


def main() -> int:
    snapshot = _latest_enriched()
    print(f"# ADG Redundancy Audit\n")
    print(f"Snapshot: `{snapshot.name}`\n")
    con = sqlite3.connect(snapshot)

    inv = adg_inventory(con)
    print(f"## ADG Capability Inventory\n")
    print(f"- Materialized views: {len(inv['mv'])} (non-empty: {sum(1 for _, c in inv['mv'] if c > 0)})")
    print(f"- P-views (P0/P1/P2/P3 classifiers): {len(inv['p_views'])}")
    print(f"- Detector tables:")
    for label, (tbl, cnt) in inv["detectors"].items():
        print(f"  - {label}: `{tbl}` = {cnt:,} rows")
    print()

    gates = collect_ci_gates()
    print(f"## CI Gates Analysis ({len(gates)} gates in ops_scripts/ci/)\n")

    redundant: list[tuple[Path, list[tuple[str, str]], str]] = []
    no_overlap: list[tuple[Path, str]] = []
    for path, doc in gates:
        flags = classify_gate(path, doc)
        if flags:
            redundant.append((path, flags, doc))
        else:
            no_overlap.append((path, doc))

    print(f"### Redundancy candidates: {len(redundant)} gates flagged\n")
    print("| Gate | Doc (first line) | ADG capability that may cover it |")
    print("|------|-------------------|----------------------------------|")
    for path, flags, doc in sorted(redundant, key=lambda x: x[0].name):
        rel = path.relative_to(REPO).as_posix()
        cap = "; ".join(set(c for _, c in flags))
        doc_short = (doc[:80] + "…") if len(doc) > 80 else doc
        print(f"| `{rel}` | {doc_short} | {cap} |")

    print(f"\n### No-overlap gates: {len(no_overlap)}\n")
    print(
        "These gates appear unique (no obvious ADG view covers them). They may "
        "be **legitimate non-ADG concerns** (config schema, file-format, "
        "process-level checks) or **gaps in ADG coverage** worth filing.\n"
    )
    print("| Gate | Doc (first line) |")
    print("|------|-------------------|")
    for path, doc in sorted(no_overlap, key=lambda x: x[0].name):
        rel = path.relative_to(REPO).as_posix()
        doc_short = (doc[:100] + "…") if len(doc) > 100 else doc
        print(f"| `{rel}` | {doc_short} |")

    # ---------- Tests cross-check ----------
    print(f"\n## Test Files vs ADG Coverage\n")
    test_dir = REPO / "tests" / "unit"
    test_count = sum(1 for _ in test_dir.rglob("test_*.py"))
    print(f"Total unit tests: {test_count}")

    # Heuristic: tests that re-derive what ADG materializes
    redundant_test_patterns = [
        (
            r"test_.*hotspot|test_.*chokepoint|test_.*centrality",
            "Hotspot/centrality tests likely redeclared by mv_hotspot_centrality",
        ),
        (
            r"test_.*dead[_-](import|symbol|module)",
            "Dead-code tests covered by mv_unknown_taxonomy_and_orphans",
        ),
        (
            r"test_.*write[_-]?bypass|test_.*sovereignty",
            "Write-bypass tests covered by v_p0_write_bypass_uwg / mv_write_sovereignty_paths",
        ),
        (r"test_.*entrypoint", "Entrypoint tests covered by A6 / module_entrypoints"),
        (r"test_.*gate[_-]self|test_.*gate[_-]doc", "Gate self-test covered by A12 / gate_self_consistency"),
        (
            r"test_.*layer[_-]?skip|test_.*gravity",
            "Gravity tests covered by v_p0_apps_direct_infra / v_p1_mis_layered_infra",
        ),
        (r"test_.*shim", "Shim tests covered by R6 mv_rename_shim_consumers"),
        (r"test_.*mcp[_-]?(sync|drift)", "MCP-sync tests covered by R6 mcp_contract_drift"),
    ]

    print(f"\n### Tests that may be ADG-redundant\n")
    print("| Test file | Suggested ADG coverage |")
    print("|-----------|------------------------|")
    flagged_tests: list[tuple[Path, str]] = []
    for tpath in test_dir.rglob("test_*.py"):
        for pat, hint in redundant_test_patterns:
            if re.search(pat, tpath.name.lower()):
                flagged_tests.append((tpath, hint))
                break
    for tpath, hint in sorted(flagged_tests, key=lambda x: x[0].name):
        rel = tpath.relative_to(REPO).as_posix()
        print(f"| `{rel}` | {hint} |")
    if not flagged_tests:
        print("| (none) | — |")

    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
