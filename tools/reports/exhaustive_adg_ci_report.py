"""Exhaustive ADG CI report — every gate, every MV, every P-view, every artifact JSON.

This is the canonical "I want to see EVERY ADG CI surface in one place"
renderer. It is the deliberate counterpart to ``adg_burndown_report.py``,
which only covers the 48-gate dispatcher view. The ADG CI surface is much
larger:

  * 48 dispatcher gates (block / ratchet / warn)
  * ~25 wiring_ci ratchets (file-backed baselines)
  *  3 file-counter gates (config_references / lifecycle_pairs / hardcoded_exclusions)
  * ~52 materialized views (mv_*) in the live SQLite snapshot
  * ~15 P-views (v_p0_* .. v_p3_*) classifying architectural concerns
  * ~17 other analytical views (overlays, summaries, witness aggregations)
  * ~20 core tables (nodes / edges / violations / coverage / ...)
  *  9 supplementary report JSONs in the run zip:
        closure_validation_report_*.json
        edge_density_report_*.json
        layer_coverage_report_*.json
        adg_runtime_spine_*.json
        adg_refactor_accelerator_*.json
        adg_snapshot_*.json
        adg_structural_outputs_*.json
        provenance_report_*.json
        adg_graph_watchlist_*.json + adg_anomaly_watchlist_*.json
  *  P0 remediation wave plan (.md + .json)
  *  P1 / P2 ratchet json
  *  Antipattern burndown table

Findings (not just counts): every surface gets a one-line interpretation
of what its current row count / value means. ``findings`` differs from
``count`` — ``count`` is mechanical (``SELECT COUNT(*)``), ``findings`` is
interpretive ("X = current critical hot path bypasses; Y = layer L0 has
density 0.43 vs ceiling 0.50; Z = snapshot integrity anomalies suggest...").

Snapshot resolution order:
  1. ``--snapshot-dir <path>``                       (explicit override)
  2. Latest extracted ``_tmp_extract/run/adg/`` dir  (manual extract)
  3. Latest live ``artifacts/adg/adg_indexed_*.sqlite`` >1 MB
  4. Latest archive ``artifacts/adg/_archive/<month>/adg_run_*.zip.gz``
     auto-extracted to a temp dir.

Usage::

    python tools/reports/exhaustive_adg_ci_report.py
    python tools/reports/exhaustive_adg_ci_report.py --out path/to/report.md
    python tools/reports/exhaustive_adg_ci_report.py --snapshot-dir _tmp_extract/run/adg
"""

from __future__ import annotations

import argparse
import datetime as _dt
import gzip
import json
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts" / "adg"
BASELINE_DIR = REPO / "ops_scripts" / "ci" / "baselines"


# --------------------------------------------------------------------------
# Description / finding templates
# --------------------------------------------------------------------------

# Materialized-view descriptions. Where {n} appears, the finding template
# substitutes the row count. Not every MV needs a fancy template; a generic
# "{n} rows recorded" fallback applies when no entry exists.
MV_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    # (description, finding_template)
    "mv_actionable_surface_without_schema": (
        "Action-class tools published without a JSON Schema contract.",
        "{n} action-class tools lack a schema — schema-less tool calls cannot be validated at the spine.",
    ),
    "mv_authority_boundary_breaches": (
        "L0/L_PG calls that cross authority boundaries other than UWG/spine.",
        "{n} authority-boundary breaches — block-class P0 fail at this count.",
    ),
    "mv_capability_and_egress_gaps": (
        "Outbound provider/SDK calls that bypass the sanctioned capability adapter.",
        "{n} egress paths bypass capability adapters — silent provider sprawl risk.",
    ),
    "mv_critical_path_segments": (
        "Edges that participate in any critical execution path (run → seal → disposition).",
        "{n} edges on the critical path — these are the high-blast-radius edges.",
    ),
    "mv_cross_cutting_witness_tiers": (
        "Tier-1 emit-site witness sites broken down by cross-cutting concern.",
        "{n} witness-tier sites — cross-cutting coverage of trace_root / step.seal / disposition.",
    ),
    "mv_debt_concentration_hotspots": (
        "Modules with concentrated technical debt (multiple SC/AP defects in one file).",
        "{n} debt-concentrated modules — top targets for refactoring waves.",
    ),
    "mv_dependency_cone_risk": (
        "Forward dependency cone (transitive imports) per node, weighted by criticality.",
        "{n} nodes scored for dependency-cone risk — used to rank refactor blast-radius.",
    ),
    "mv_determinism_provenance_drift": (
        "Trace_root emit sites missing determinism digest or replay key.",
        "{n} emit sites with provenance drift — replay/reproduction may be incomplete.",
    ),
    "mv_digest_reconciliation": (
        "Snapshot-to-snapshot digest reconciliation per pipeline phase.",
        "{n} digest reconciliation rows — phase-level integrity check.",
    ),
    "mv_eval_coverage_by_path": (
        "Eval coverage rolled up per repo path.",
        "{n} paths reported — eval coverage by file area.",
    ),
    "mv_exemptions_near_critical_paths": (
        "Guardian exemptions located on or adjacent to critical paths.",
        "{n} exemptions touch critical paths — high-priority audit candidates.",
    ),
    "mv_exit_disposition_coverage": (
        "Tier-1 Exit.disposition emit-site coverage per layer.",
        "{n} layers tracked for Exit.disposition coverage.",
    ),
    "mv_gateway_bypass_paths": (
        "Code paths that mutate state without crossing the L4 UWG.",
        "{n} gateway-bypass paths — direct write sovereignty violation.",
    ),
    "mv_graph_chokepoint_bridges": (
        "Edges whose removal would disconnect a layer subgraph.",
        "{n} chokepoint bridges — single points of layer-connectivity failure.",
    ),
    "mv_graph_critical_path_blast_radius": (
        "Per-symbol blast radius if removed from the critical path.",
        "{n} symbols ranked by critical-path blast radius — refactor priority signal.",
    ),
    "mv_graph_reverse_dependency_hotspots": (
        "Top reverse-dependency centrality (most-imported-from symbols).",
        "{n} reverse-dep hotspots — bottom-up dependency hubs.",
    ),
    "mv_graph_scc_clusters": (
        "Strongly-connected components in the import graph (cycles).",
        "{n} SCCs — non-zero values mean import cycles exist.",
    ),
    "mv_graph_vs_report_mismatches": (
        "Disagreements between graph-derived facts and downstream reports.",
        "{n} graph/report mismatches — non-zero values undermine the canonical-truth invariant.",
    ),
    "mv_handoff_witness_tiers": (
        "Layer-handoff witness coverage (L1→L2, L2→L3, etc.).",
        "{n} handoff witnesses — each is a layer-boundary observability checkpoint.",
    ),
    "mv_heal_retry_exit_gaps": (
        "Healing-loop exit paths missing an Exit.disposition emit site.",
        "{n} healing exits without disposition — silent recovery paths.",
    ),
    "mv_high_fan_in_out_with_defects": (
        "Symbols with high fan-in OR fan-out AND at least one SC/AP defect.",
        "{n} high-fanout/-fanin defective symbols — refactor priority by impact.",
    ),
    "mv_hitl_reclearance_gaps": (
        "Author-Gate / runtime HITL flows missing the modify-then-reclear edge.",
        "{n} HITL re-clearance gaps — incomplete approval chains.",
    ),
    "mv_hotspot_centrality": (
        "Hotspot ranking by graph centrality (PageRank / betweenness blend).",
        "{n} centrality-ranked hotspots — primary input to refactor wave order.",
    ),
    "mv_hotspot_coverage_risk": (
        "Hotspots × test-coverage cross-join with priority bands (P1..P5).",
        "{n} hotspots scored on coverage risk — used by hotspot_coverage_report.py.",
    ),
    "mv_l2_phase_coverage": (
        "L2 execution phase coverage (capability / call / seal / dispatch).",
        "{n} phases tracked for L2 coverage — execution layer observability.",
    ),
    "mv_live_future_mutation_conflicts": (
        "State writes that may race with future mutations on the same key.",
        "{n} mutation conflicts — non-zero values indicate write-write race risk.",
    ),
    "mv_local_heal_first_breaches": (
        "Healing actions that escaped local heal-first containment.",
        "{n} local-first breaches — healing escalated past intended scope.",
    ),
    "mv_manager_sprawl": (
        "Manager / Orchestrator class proliferation per layer.",
        "{n} manager classes — high values often signal orchestration sprawl.",
    ),
    "mv_modified_area_regressions": (
        "SC/AP defects whose source location intersects this run's modified files.",
        "{n} modified-area regressions — defects in code touched this run.",
    ),
    "mv_new_cross_layer_dependencies": (
        "Cross-layer imports introduced since the previous snapshot baseline.",
        "{n} new cross-layer deps — delta vs prev snapshot.",
    ),
    "mv_new_provider_surfaces": (
        "Provider/SDK surfaces that appeared since the previous snapshot.",
        "{n} new provider surfaces — drift watch.",
    ),
    "mv_new_write_bypass_paths": (
        "Write-bypass paths flagged as 'new' (severity ∈ {critical, warning}).",
        "{n} write-bypass paths flagged new — block-class trigger for P0 write_sovereignty gate.",
    ),
    "mv_newly_introduced_critical_paths": (
        "Critical-path edges introduced since previous snapshot baseline.",
        "{n} newly-introduced critical paths — delta drives P0 regressions.",
    ),
    "mv_observability_interference_breaches": (
        "Observability code that interferes with the production code path.",
        "{n} observability interference breaches — non-zero is a §6 invariant violation.",
    ),
    "mv_path_criticality_rollup": (
        "Rolled-up criticality score per node across all critical-path memberships.",
        "{n} nodes with criticality scores — the impact-ordering primitive.",
    ),
    "mv_prompt_assembly_wiring_gaps": (
        "Wiring gaps in the prompt assembly path (S0/D0/I0/C0/U0 slots).",
        "{n} prompt-assembly wiring gaps — block-class P1 trigger when >0.",
    ),
    "mv_provider_surface_sprawl": (
        "Provider SDK surface area (distinct callable symbols per provider).",
        "{n} provider surface entries — sprawl monitor.",
    ),
    "mv_repeated_p3_near_critical_paths": (
        "P3 style warnings that repeatedly land on or near critical paths.",
        "{n} P3 sites near critical paths — promotion candidates to P2.",
    ),
    "mv_replay_surface_gaps": (
        "Replay-surface coverage gaps (state reads/writes not observable).",
        "{n} replay-surface gaps — unobservable mutations.",
    ),
    "mv_runtime_spine_gaps": (
        "Runtime-spine emit sites missing from the live OTEL pipeline.",
        "{n} runtime-spine gaps — Tier-1 telemetry blind spots.",
    ),
    "mv_snapshot_baseline": (
        "Anchor row for the current snapshot (one row per run).",
        "{n} baseline anchor row — used by all delta-class gates.",
    ),
    "mv_snapshot_integrity_anomalies": (
        "Anomalies in the snapshot itself (orphan ids, dup rows, schema drift).",
        "{n} snapshot integrity anomalies — high values indicate ingest-side bugs.",
    ),
    "mv_snapshot_regression_summary": (
        "Aggregate delta vs previous baseline (one row).",
        "{n} regression-summary row — see fields for per-metric deltas.",
    ),
    "mv_structured_output_gaps": (
        "Tool calls missing structured-output schema validation.",
        "{n} structured-output gaps — silent shape drift risk.",
    ),
    "mv_task_contract_gaps": (
        "Task contracts (entry → exit shape) that are incomplete.",
        "{n} task-contract gaps — incomplete shape declarations at task boundaries.",
    ),
    "mv_tool_surface_overlap": (
        "Tool capabilities exposed by multiple adapters (overlap risk).",
        "{n} overlapping tool surfaces — consolidation candidates.",
    ),
    "mv_trace_replay_eval_gaps": (
        "Trace-replay eval coverage gaps (paths where replay would skip).",
        "{n} replay/eval gaps — feeds 8_trace_replay_eval ratchet.",
    ),
    "mv_unknown_taxonomy_and_orphans": (
        "Symbols that did not classify into any taxonomy bucket.",
        "{n} unclassified symbols — gardening backlog.",
    ),
    "mv_untrusted_text_to_action_risk": (
        "User text reaching action-class tools without prompt-governance gating.",
        "{n} text-to-action risk paths — non-zero is a P0 fail in 5_text_to_action.",
    ),
    "mv_write_sovereignty_paths": (
        "Every state-write path with severity classification.",
        "{n} total write paths — feeds 3_write_sovereignty gate.",
    ),
    "mv_agent_specialization_overlap": (
        "Agent classes whose specializations overlap (potential dedup target).",
        "{n} overlapping agent specializations.",
    ),
    "mv_agent_tool_ratio": (
        "Tools-per-agent ratio per agent class.",
        "{n} agent classes scored for tool ratio.",
    ),
}

# P-view descriptions (priority-classified architectural concerns).
PVIEW_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "v_p0_apps_direct_infra": (
        "P0: apps_* directly imports infrastructure/* (forbidden).",
        "{n} apps_*→infra direct imports — must be 0 (block-class).",
    ),
    "v_p0_l0_raw_execution": (
        "P0: L0 invokes raw execution without going through the orchestrator.",
        "{n} L0-raw-execution sites — must be 0 (block-class).",
    ),
    "v_p0_l1_direct_infra": (
        "P0: L1 cognition imports infrastructure directly.",
        "{n} L1→infra direct imports — must be 0.",
    ),
    "v_p0_l6_mutation": (
        "P0: L6 observability code mutates production state.",
        "{n} L6 mutations — must be 0 (observability must not interfere).",
    ),
    "v_p0_provider_bypass": (
        "P0: provider call that bypasses the capability adapter.",
        "{n} provider bypasses — must be 0 (block-class).",
    ),
    "v_p0_write_bypass_uwg": (
        "P0: state write that does not flow through the L4 UWG.",
        "{n} UWG bypasses — must be 0 (block-class).",
    ),
    "v_p1_ad_hoc_imports": (
        "P1: ad-hoc imports of internal modules (not through SSOT seam).",
        "{n} ad-hoc imports — promotion candidates if persistent.",
    ),
    "v_p1_mis_layered_infra": (
        "P1: infrastructure module placed in the wrong layer.",
        "{n} mis-layered infra modules.",
    ),
    "v_p1_not_on_spine": (
        "P1: emit site or seam declared but not reachable from the spine.",
        "{n} non-spine sites — orphan declarations.",
    ),
    "v_p1_raw_http_outside_seam": (
        "P1: raw HTTP call outside the sanctioned HTTP seam.",
        "{n} raw-HTTP outside seam — provider-egress drift.",
    ),
    "v_p1_zero_caller_infra": (
        "P1: infrastructure module with zero callers (dead infra).",
        "{n} zero-caller infra modules — archive candidates.",
    ),
    "v_p2_dormant_ambiguous": (
        "P2: declarations that are dormant AND ambiguous (cannot tell if dead or planned).",
        "{n} dormant-ambiguous sites.",
    ),
    "v_p2_duplicated_adapters": (
        "P2: adapters that duplicate each other's capability.",
        "{n} duplicated adapter pairs.",
    ),
    "v_p2_mixed_usage": (
        "P2: symbols used both inside and outside their declared layer.",
        "{n} mixed-usage symbols.",
    ),
    "v_p3_isolated_experimental": (
        "P3: experimental code with no production reach.",
        "{n} isolated experimental modules — informational only.",
    ),
}

# Other analytical-view descriptions.
OTHER_VIEW_DESCRIPTIONS: dict[str, str] = {
    "edge_view": "Pre-joined edges×nodes×layers projection (read path for analytics).",
    "mv_async_fire_and_forget_hotspots": "Async tasks launched without retention (potential lost futures).",
    "mv_boundary_string_unresolved": "String-typed boundary references that the resolver could not bind.",
    "mv_dead_import_hotspots_overlay": "Imports that resolve but whose target is never used.",
    "mv_external_calls_no_timeout": "External calls without a `timeout=` argument (constitutional §14).",
    "mv_hidden_writes_overlay": "Writes through indirection layers (proxies, getattr, exec).",
    "mv_mcp_contract_drift": "MCP tool declarations that no longer match the canonical contract.",
    "mv_module_duplicate_clusters_overlay": "Modules whose AST signatures match — duplication candidates.",
    "mv_module_load_action_calls_overlay": "Action-class calls invoked at module-load time (side-effect at import).",
    "mv_overlay_debt_summary": "Per-overlay summary of detected debt items.",
    "mv_r6_summary": "R6 review cycle aggregate row (one row, snapshot-scoped).",
    "mv_rename_shim_consumers": "Consumers still importing through deprecation re-export shims.",
    "mv_truth_expansion_summary": "Truth-table expansion / canonical inference one-row summary.",
    "mv_unresolved_config_refs": "Env/config references the resolver could not bind to a declaration.",
    "precision_metrics_view": "Precision-pass metrics (variable attributes, side effects, callsite resolution).",
    "v_infra_violations_summary": "Infra-imports violations rolled up by class.",
}

# Core-table shape interpretation.
CORE_TABLE_DESCRIPTIONS: dict[str, str] = {
    "async_fire_and_forget": "Async-task launches with no retention/await (fire-and-forget instances).",
    "boundary_strings": "All string literals participating in module/symbol boundary references.",
    "config_references": "Every env/config flag read in the codebase (input to check_config_references).",
    "coverage_by_path": "coverage.py data ingested per repo path.",
    "edges": "Canonical edge table (imports / calls / writes / flows_to / etc.).",
    "external_calls": "External (provider/SDK/HTTP) call sites (input for capability_egress checks).",
    "gate_self_consistency": "Per-gate self-consistency probe rows (gate-of-gates).",
    "mcp_config_servers": ".cursor/mcp.json declared servers.",
    "mcp_tool_declarations": "All @mcp.tool decorated functions ingested per MCP server.",
    "meta": "Snapshot meta (commit_sha, timestamp, generator version).",
    "module_entrypoints": "Every module-level entrypoint with classification (test / cli / api / service).",
    "module_origins": "Per-module origin classification (production / test / tool / archive).",
    "nodes": "Canonical node table (modules + symbols + classes + functions).",
    "overlay_violations": "Violations recorded by overlay analyses (vs canonical violations).",
    "side_effect_calls": "Call sites flagged as side-effecting (writes / IO / network / import-time).",
    "snapshot_metadata": "Per-snapshot bookkeeping (one row per run).",
    "sqlite_sequence": "SQLite internal AUTOINCREMENT bookkeeping.",
    "t_infra_importers": "Modules that import infrastructure namespaces (input to v_p0_apps_direct_infra).",
    "test_stubs": "Discovered pytest test_* functions (input to test_harness_coverage).",
    "violations": "Canonical violations table — the SC/AP burndown source.",
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _human(n: int) -> str:
    if n is None:
        return "—"
    return f"{n:,}"


def _row_count(cur: sqlite3.Cursor, name: str) -> int | None:
    try:
        return int(cur.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])
    except sqlite3.Error:
        return None


def _list_objects(cur: sqlite3.Cursor, kind: str) -> list[str]:
    return [r[0] for r in cur.execute(
        f"SELECT name FROM sqlite_master WHERE type=? ORDER BY name", (kind,)
    ).fetchall()]


def _safe_load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        return {"_error": f"could not load {path.name}: {exc}"}


def _latest(glob_root: Path, pattern: str, min_size: int = 0) -> Path | None:
    matches = [p for p in glob_root.rglob(pattern) if p.is_file() and p.stat().st_size > min_size]
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)


def _resolve_snapshot_dir(explicit: Path | None) -> tuple[Path, str]:
    """Return (snapshot_dir, source) where snapshot_dir contains the SQLite + JSONs."""
    if explicit and explicit.exists():
        return explicit, "explicit"

    extracted = REPO / "_tmp_extract" / "run" / "adg"
    if extracted.exists() and any(extracted.glob("adg_indexed_*.sqlite")):
        return extracted, "extracted"

    live = _latest(ARTIFACTS, "adg_indexed_*.sqlite", min_size=1_000_000)
    if live:
        return live.parent, "live"

    archives = sorted((ARTIFACTS / "_archive").rglob("adg_run_*.zip.gz"))
    if archives:
        latest_gz = archives[-1]
        tmp = Path(tempfile.mkdtemp(prefix="adg_extract_"))
        zip_path = tmp / "run.zip"
        with gzip.open(latest_gz, "rb") as fin, zip_path.open("wb") as fout:
            shutil.copyfileobj(fin, fout)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp / "run")
        adg_dir = tmp / "run" / "adg"
        if not adg_dir.exists():
            return tmp / "run", f"archive:{latest_gz.name}"
        return adg_dir, f"archive:{latest_gz.name}"

    raise FileNotFoundError("no ADG snapshot found via explicit/extracted/live/archive resolution")


# --------------------------------------------------------------------------
# Renderers
# --------------------------------------------------------------------------


def render(snapshot_dir: Path, source: str) -> str:
    sqlites = sorted(snapshot_dir.glob("adg_indexed_*.sqlite"),
                     key=lambda p: p.stat().st_size, reverse=True)
    if not sqlites:
        raise FileNotFoundError(f"no adg_indexed_*.sqlite under {snapshot_dir}")
    sqlite_path = sqlites[0]

    burndown_path = snapshot_dir / "adg_burndown_table.json"
    if not burndown_path.exists():
        burndown_path = ARTIFACTS / "adg_burndown_table.json"
    burndown = _safe_load_json(burndown_path)

    gate_results = max(ARTIFACTS.glob("adg_gate_results_*.json"), default=None,
                       key=lambda p: p.stat().st_mtime)
    gate_doc: dict[str, Any] = _safe_load_json(gate_results) if gate_results else {}

    con = sqlite3.connect(str(sqlite_path))
    cur = con.cursor()

    tables = _list_objects(cur, "table")
    views = _list_objects(cur, "view")
    mvs = sorted(t for t in tables if t.startswith("mv_"))
    p_views = sorted(v for v in views if v.startswith("v_p"))
    other_views = sorted(v for v in views if not v.startswith("v_p"))
    core_tables = sorted(t for t in tables if not t.startswith("mv_"))

    lines: list[str] = []
    a = lines.append

    # ============ §1 Header
    a("# Exhaustive ADG CI Report")
    a("")
    a(f"- **Generated:** {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds')}")
    a(f"- **Snapshot SQLite:** `{sqlite_path.name}` ({_human(sqlite_path.stat().st_size)} bytes)")
    a(f"- **Snapshot source:** {source}")
    if gate_results:
        a(f"- **Gate results:** `{gate_results.relative_to(REPO)}`")
    a(f"- **Burndown table:** `{burndown_path}`")
    summary = gate_doc.get("summary", {})
    overall = "PASS" if gate_doc.get("overall_exit_code") == 0 else "BLOCKED"
    a(f"- **Dispatcher overall verdict:** **{overall}**")
    a("")

    # ============ §2 Executive summary
    a("## 1. Executive Summary")
    a("")
    a("> ℹ️ **Two independent dashboards in this report. They do NOT talk to each other.**")
    a("> ")
    a("> | Section | Question it answers | Tier prefix used |")
    a("> |---|---|---|")
    a("> | §1 (this section)        | *How many graded code-defects exist?*    | **`S0`/`S1`/`S2`/`S3`** (Severity) |")
    a("> | §2 (Dispatcher Gates)    | *Which CI gates are angry right now?*    | **`P0`/`P1`/`P2`/`P3`** (Priority of gate) |")
    a("> ")
    a("> **Renamed in this report**: the burndown band column was previously labelled "
      "`P0..P3` and conflicted visually with the gate priorities in §2. To eliminate the "
      "collision, §1 now uses `S` (Severity) and §2 keeps `P` (Priority). "
      "**The underlying JSON is unchanged** — `adg_burndown_table.json` still uses `P0..P3` keys; "
      "this renderer translates them at display time.")
    a("> ")
    a("> **Which one tells me if the run is healthy?** §2 — always §2. "
      "A green run = §2 shows `block_fail=0` AND `ratchet_regressed=0`. "
      "§1 is a debt-burndown trend, not a green-light signal.")
    a("> ")
    a("> **Does a §2 `P0` block-fail block the ADG run?** Yes by default — `generate_full_adg.py` "
      "exits non-zero on any `block`-class fail. The override is "
      "`ADG_CONTINUE_ON_GATE_FAILURE=1`, which lets the run finish so the SQLite + report "
      "JSONs land regardless; the verdict is still recorded.")
    a("")
    a("**Defect severities** (§1 — counts of rule-violation rows in the `violations` table):")
    a("")
    a("| Severity | Label | Gross | Guardian | Net | Diff |")
    a("|----------|-------|------:|---------:|----:|-----:|")
    _band_to_severity = {"P0": "S0", "P1": "S1", "P2": "S2", "P3": "S3"}
    for band in ("P0", "P1", "P2", "P3"):
        row = burndown.get("summary", {}).get(band, {})
        sev = _band_to_severity[band]
        a(f"| **{sev}** | {row.get('label', '?')} | {_human(row.get('gross', 0))} | "
          f"{_human(row.get('guardian', 0))} | {_human(row.get('net', 0))} | "
          f"{row.get('diff', 0):+d} |")
    a("")
    a("_(`S0..S3` is this renderer's display label; the JSON keys remain `P0..P3` for "
      "backward compatibility with `adg_burndown_table.json` consumers.)_")
    a("")

    # ============ Unified defect pane (one table, every non-zero defect)
    a("### One-Pane-of-Glass Defect Table")
    a("")
    a("Every non-zero defect surface in the snapshot, in one rank-ordered table. "
      "Combines failing dispatcher gates (§2), non-zero materialized views (§3), "
      "non-zero P-views (§4), and severity-band totals (§1 — shown as `S*` rows). "
      "Sorted by **action band**, then by **count descending**.")
    a("")
    a("**Action bands:**")
    a("- 🔴 **BLOCK** — gate is `block`-class AND failing → ADG run fails (unless `ADG_CONTINUE_ON_GATE_FAILURE=1`)")
    a("- 🟠 **REGRESSED** — gate is `ratchet`-class AND violation count grew past baseline")
    a("- 🟡 **MONITOR** — non-zero MV / P-view that is NOT directly a failing gate (informational signal)")
    a("- 🔵 **TREND** — §1 severity tally (long-running debt counter, not a green-light signal)")
    a("- ⚪ **OK** — passing gate with non-zero ratchet baseline (counted but at-or-below ceiling)")
    a("")
    a("| # | Action | Source | Item | Count | Tier | Status | Backed By |")
    a("|---|:------:|:------:|------|------:|:----:|:------:|-----------|")

    rows: list[tuple[int, int, str, str, str, int, str, str, str]] = []
    # action_rank, count_neg, action_emoji, source_label, item, count, tier, status, backed_by

    # 1) §1 severity tallies (TREND)
    band_to_severity = {"P0": "S0", "P1": "S1", "P2": "S2", "P3": "S3"}
    for band in ("P0", "P1", "P2", "P3"):
        row = burndown.get("summary", {}).get(band, {})
        net = int(row.get("net", 0) or 0)
        if net <= 0:
            continue
        rows.append((
            3, -net, "🔵 TREND", "§1",
            f"`{row.get('label', band)}` (severity {band_to_severity[band]})",
            net, band_to_severity[band], "—", "`violations` table",
        ))

    # 2) §2 dispatcher gates — separate FAIL / REGR / passing-with-count
    for g in gate_doc.get("gates", []):
        gid = g.get("gate_id", "?")
        cnt = int(g.get("violation_count", 0) or 0)
        cls = g.get("classification", "?")
        enf = g.get("enforcement", "?")
        band = g.get("band", "?")
        owner = g.get("owner", "?")
        if cls == "blocked":
            rows.append((0, -cnt, "🔴 BLOCK", "§2",
                         f"`{gid}`", cnt, band, "FAIL", f"gate ({owner}, {enf})"))
        elif cls == "regressed":
            rows.append((1, -cnt, "🟠 REGR", "§2",
                         f"`{gid}`", cnt, band, "REGR", f"gate ({owner}, {enf})"))
        elif cls == "pass" and cnt > 0:
            rows.append((4, -cnt, "⚪ OK",  "§2",
                         f"`{gid}` (at/under ratchet ceiling)", cnt, band, "PASS",
                         f"gate ({owner}, {enf})"))

    # 3) §3 MV non-zero rows that are NOT already represented as a failing gate
    failing_gate_ids = {g.get("gate_id") for g in gate_doc.get("gates", [])
                        if g.get("classification") in ("blocked", "regressed")}
    for m in mvs:
        n = _row_count(cur, m)
        if not n:
            continue
        # Skip if this MV's content is already represented by a failing dispatcher gate.
        # Heuristic: gate_id substrings often match MV name fragments.
        skip = any(
            (m.replace("mv_", "") in gid.lower() or gid.lower().replace("_", "") in m.replace("mv_", "").replace("_", ""))
            for gid in failing_gate_ids
        )
        if skip:
            continue
        desc, _ = MV_DESCRIPTIONS.get(m, (m, ""))
        rows.append((2, -n, "🟡 MONITOR", "§3",
                     f"`{m}` — {desc[:70]}", n, "—", "—", "MV (informational)"))

    # 4) §4 P-views non-zero
    for p in p_views:
        n = _row_count(cur, p)
        if not n:
            continue
        desc, _ = PVIEW_DESCRIPTIONS.get(p, (p, ""))
        # P-views encode their own band in the name (v_p0_*, v_p1_*, etc.)
        pv_band = p.split("_")[1].upper().replace("V", "")  # p0 -> P0
        action = "🔴 BLOCK" if pv_band == "P0" else "🟡 MONITOR"
        action_rank = 0 if pv_band == "P0" else 2
        rows.append((action_rank, -n, action, "§4",
                     f"`{p}` — {desc[:70]}", n, pv_band, "—", "P-view (graph layer)"))

    # Sort: action_rank asc, count desc (count_neg asc)
    rows.sort(key=lambda r: (r[0], r[1]))

    for i, (_, _, action, src, item, cnt, tier, status, backed) in enumerate(rows, 1):
        a(f"| {i} | {action} | {src} | {item} | {_human(cnt)} | {tier} | {status} | {backed} |")
    a("")
    a(f"_Total: {len(rows)} non-zero defect surfaces across all four tier-systems._")
    a("")

    if summary:
        a("**Dispatcher gates** (from `adg_gate_results_*.json`):")
        a("")
        a(f"- block_pass: **{summary.get('block_pass', 0)}** | "
          f"block_fail: **{summary.get('block_fail', 0)}** | "
          f"ratchet_pass: **{summary.get('ratchet_pass', 0)}** | "
          f"ratchet_regressed: **{summary.get('ratchet_regressed', 0)}** | "
          f"warn: **{summary.get('warn', 0)}**")
        a(f"- Total dispatcher gates: **{gate_doc.get('total_gates', '?')}**")
        a("")

    a("**Snapshot surface inventory:**")
    a("")
    a(f"- Materialized views (`mv_*`): **{len(mvs)}**")
    a(f"- P-views (`v_p0..v_p3`): **{len(p_views)}**")
    a(f"- Other analytical views: **{len(other_views)}**")
    a(f"- Core tables: **{len(core_tables)}**")
    a("")

    # ============ §3 Dispatcher gates (from existing renderer)
    a("## 2. Dispatcher Gates (48)")
    a("")
    a("Every gate registered in `ops_scripts/ci/adg_gates/run.py`. "
      "Enforcement contract: **block** = any violation fails the run; "
      "**ratchet** = only NEW violations beyond baseline fail; **warn** = advisory.")
    a("")
    if gate_doc.get("gates"):
        a("| Gate ID | Band | Enf | Status | Violations | Owner |")
        a("|---------|:----:|:---:|:------:|-----------:|:-----:|")
        sorted_gates = sorted(
            gate_doc["gates"],
            key=lambda g: (
                {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(g.get("band", "P3"), 9),
                {"blocked": 0, "regressed": 1, "pass": 2}.get(g.get("classification", "pass"), 9),
                g.get("gate_id", ""),
            ),
        )
        glyph = {"pass": "PASS", "blocked": "FAIL", "regressed": "REGR"}
        for g in sorted_gates:
            a(f"| `{g['gate_id']}` | {g['band']} | {g['enforcement']} | "
              f"{glyph.get(g['classification'], g['classification'].upper())} | "
              f"{_human(g['violation_count'])} | {g.get('owner', '?')} |")
    else:
        a("_No dispatcher gate results found._")
    a("")

    # ============ §4 Materialized views
    a("## 3. Materialized Views (mv_*)")
    a("")
    a("Pre-computed analytical tables built by `tools/generate/materialized_views/` "
      "during every ADG run. The graph layer (constitutional §22) requires plans "
      "to cite these views as primary evidence.")
    a("")
    a("| View | Rows | Description | Finding |")
    a("|------|-----:|-------------|---------|")
    for m in mvs:
        n = _row_count(cur, m)
        n_str = _human(n) if n is not None else "ERR"
        desc, finding_tpl = MV_DESCRIPTIONS.get(
            m,
            (m.replace("mv_", "").replace("_", " ").title(),
             "{n} rows recorded (no description registered yet)."),
        )
        finding = finding_tpl.format(n=n_str) if n is not None else "could not count"
        a(f"| `{m}` | {n_str} | {desc} | {finding} |")
    a("")

    # ============ §5 P-views
    a("## 4. P-Views (v_p0_* … v_p3_*)")
    a("")
    a("Pre-classified architectural concerns by priority band. P0 rows are "
      "block-class — any non-zero count fails the run unless guardian-exempted.")
    a("")
    a("| View | Rows | Description | Finding |")
    a("|------|-----:|-------------|---------|")
    for p in p_views:
        n = _row_count(cur, p)
        n_str = _human(n) if n is not None else "ERR"
        desc, finding_tpl = PVIEW_DESCRIPTIONS.get(
            p,
            (p.replace("v_p", "P-view ").replace("_", " ").title(), "{n} rows."),
        )
        finding = finding_tpl.format(n=n_str) if n is not None else "could not count"
        a(f"| `{p}` | {n_str} | {desc} | {finding} |")
    a("")

    # ============ §6 Other views
    a("## 5. Other Analytical Views")
    a("")
    a("| View | Rows | Description |")
    a("|------|-----:|-------------|")
    for v in other_views:
        n = _row_count(cur, v)
        desc = OTHER_VIEW_DESCRIPTIONS.get(v, "(no description registered yet)")
        a(f"| `{v}` | {_human(n) if n is not None else 'ERR'} | {desc} |")
    a("")

    # ============ §7 Core tables
    a("## 6. Core Tables")
    a("")
    a("| Table | Rows | Description |")
    a("|-------|-----:|-------------|")
    for t in core_tables:
        n = _row_count(cur, t)
        desc = CORE_TABLE_DESCRIPTIONS.get(t, "(internal — no description registered yet)")
        a(f"| `{t}` | {_human(n) if n is not None else 'ERR'} | {desc} |")
    a("")

    # ============ §8 Wiring CI baselines
    a("## 7. Wiring CI Ratchet Baselines")
    a("")
    a("Per-gate ceiling files in `ops_scripts/ci/baselines/wiring_*_ratchet.json`. "
      "`count` is the absorbed floor; `tighten_history` records pay-down events; "
      "`loosen_history` (added 2026-04-28) records floor-absorb events.")
    a("")
    if BASELINE_DIR.exists():
        a("| Baseline | Gate ID | Count | Last Tightened | Last Loosened |")
        a("|----------|---------|------:|----------------|---------------|")
        for bp in sorted(BASELINE_DIR.glob("wiring_*_ratchet.json")):
            data = _safe_load_json(bp)
            gid = data.get("gate_id", "—")
            cnt = data.get("count", "—")
            tightened = (data.get("tighten_history") or [{}])[-1].get("at", "—") if data.get("tighten_history") else (data.get("tightened_at", "—"))
            loosened = (data.get("loosen_history") or [{}])[-1].get("at", "—") if data.get("loosen_history") else (data.get("loosened_at", "—"))
            a(f"| `{bp.name}` | `{gid}` | {_human(cnt) if isinstance(cnt, int) else cnt} | {tightened or '—'} | {loosened or '—'} |")
    a("")

    # ============ §9 File-counter gate baselines
    a("## 8. File-Counter Gate Baselines")
    a("")
    a("Baselines for the three legacy-debt ratchet gates (`config_references`, "
      "`lifecycle_pairs`, `hardcoded_exclusions`). These gates use a flat list "
      "of locked-in known issues; new issues fail the run.")
    a("")
    a("| Baseline | Tracked Items | Description |")
    a("|----------|--------------:|-------------|")
    for bn, desc in (
        ("config_references_baseline.json", "env-flag reads not declared in `.env.example` (legacy debt)."),
        ("lifecycle_pairs_baseline.json", "open-without-close lifecycle leaks (legacy debt)."),
        ("hardcoded_exclusions_baseline.json", "hardcoded path/pattern exclusions outside `config/excluded_paths.yaml`."),
    ):
        bp = BASELINE_DIR / bn
        n = "—"
        if bp.exists():
            data = _safe_load_json(bp)
            if isinstance(data, list):
                n = _human(len(data))
            elif isinstance(data, dict):
                # Prefer an explicit 'count' field if present (canonical shape).
                if isinstance(data.get("count"), int):
                    n = _human(data["count"])
                else:
                    # Common shapes: {"accepted_undeclared": [...]} /
                    # {"accepted_leaks": [...]} / {"flags": [...]} / {"leaks": [...]}
                    for key in (
                        "accepted_undeclared", "accepted_leaks", "accepted_exclusions",
                        "flags", "leaks", "items", "entries",
                    ):
                        v = data.get(key)
                        if isinstance(v, list):
                            n = _human(len(v))
                            break
                    else:
                        n = _human(len(data))
        a(f"| `{bn}` | {n} | {desc} |")
    a("")

    # ============ §10 Snapshot supplementary reports
    a("## 9. Supplementary Snapshot Reports")
    a("")
    a("Each ADG run emits a fixed family of analytical JSONs alongside the SQLite. "
      "These are interpretive summaries that the materialized views feed.")
    a("")
    a("| Report | Findings |")
    a("|--------|----------|")

    def _report_finding(name_glob: str, summarize: callable) -> None:
        match = next(iter(sorted(snapshot_dir.glob(name_glob))), None)
        if not match:
            a(f"| `{name_glob}` | _not present in snapshot bundle_ |")
            return
        try:
            data = _safe_load_json(match)
            a(f"| `{match.name}` | {summarize(data)} |")
        except (KeyError, TypeError, ValueError) as exc:
            a(f"| `{match.name}` | (could not interpret: {exc}) |")

    def _closure_summary(d: dict[str, Any]) -> str:
        if "_error" in d: return d["_error"]
        s = d.get("summary", {})
        rows = d.get("closure_rows", [])
        det = d.get("determinism", {})
        sp = d.get("semantic_precision", {})
        return (
            f"summary keys={len(s)}, closure_rows={len(rows)}, "
            f"determinism keys={len(det)}, semantic_precision keys={len(sp)}"
        )

    def _edge_density_summary(d: dict[str, Any]) -> str:
        if "_error" in d: return d["_error"]
        total = d.get("total_edges", "?")
        dm = d.get("density_metrics", {})
        crit = d.get("critical_edge_coverage", {})
        dist = d.get("edge_distribution", {})
        return (
            f"total_edges={_human(total) if isinstance(total, int) else total}, "
            f"density_metrics keys={len(dm)}, critical-edge keys={len(crit)}, "
            f"edge_distribution buckets={len(dist)}"
        )

    def _layer_coverage_summary(d: dict[str, Any]) -> str:
        if "_error" in d: return d["_error"]
        total = d.get("total_modules", "?")
        unk = d.get("unknown_modules", [])
        unk_n = len(unk) if isinstance(unk, list) else (unk if isinstance(unk, int) else "?")
        ld = d.get("layer_distribution", {})
        cm = d.get("coverage_metrics", {})
        return (
            f"total_modules={_human(total) if isinstance(total, int) else total}, "
            f"unknown_modules={_human(unk_n) if isinstance(unk_n, int) else unk_n}, "
            f"layers={len(ld)}, coverage_metrics keys={len(cm)}"
        )

    def _runtime_spine_summary(d: dict[str, Any]) -> str:
        if "_error" in d: return d["_error"]
        sites = d.get("emit_sites", d.get("sites", []))
        gaps = d.get("gaps", [])
        return f"emit_sites={len(sites) if hasattr(sites, '__len__') else '?'}, gaps={len(gaps) if hasattr(gaps, '__len__') else '?'}"

    def _refactor_accel_summary(d: dict[str, Any]) -> str:
        if "_error" in d: return d["_error"]
        recs = d.get("recommendations", d.get("waves", []))
        return f"recommendations={len(recs) if hasattr(recs, '__len__') else '?'}"

    def _provenance_summary(d: dict[str, Any]) -> str:
        if "_error" in d: return d["_error"]
        keys = list(d.keys())
        return f"top-level keys: {keys}"

    def _watchlist_summary(d: dict[str, Any]) -> str:
        if "_error" in d: return d["_error"]
        if isinstance(d, dict):
            for k in ("watchlist", "items", "entries"):
                if k in d and hasattr(d[k], "__len__"):
                    return f"items={len(d[k])}"
            return f"top-level keys: {list(d.keys())[:5]}"
        return f"len={len(d)}" if hasattr(d, "__len__") else "?"

    def _wave_plan_summary(d: dict[str, Any]) -> str:
        if "_error" in d: return d["_error"]
        waves = d.get("waves", d.get("phases", []))
        is_clean = d.get("clean", d.get("p0_clean", False))
        return f"waves={len(waves) if hasattr(waves, '__len__') else '?'}, clean_snapshot={is_clean}"

    _report_finding("closure_validation_report_*.json", _closure_summary)
    _report_finding("edge_density_report_*.json", _edge_density_summary)
    _report_finding("layer_coverage_report_*.json", _layer_coverage_summary)
    _report_finding("adg_runtime_spine_*.json", _runtime_spine_summary)
    _report_finding("adg_refactor_accelerator_*.json", _refactor_accel_summary)
    _report_finding("provenance_report_*.json", _provenance_summary)
    _report_finding("adg_graph_watchlist_*.json", _watchlist_summary)
    _report_finding("adg_anomaly_watchlist_*.json", _watchlist_summary)
    _report_finding("p0_remediation_wave_plan_*.json", _wave_plan_summary)
    a("")

    # ============ §11 P1/P2 ratchet json
    a("## 10. Antipattern Ratchet State (P1 / P2)")
    a("")
    for label, fname in (("P1 antipattern ratchet", "p1_ratchet.json"),
                         ("P2 antipattern ratchet", "p2_ratchet.json")):
        p = ARTIFACTS / fname
        if not p.exists():
            a(f"- **{label}**: `{fname}` not found")
            continue
        data = _safe_load_json(p)
        if isinstance(data, dict):
            keys = ", ".join(f"{k}={data[k]}" for k in list(data.keys())[:6])
            a(f"- **{label}** (`{fname}`): {keys}")
        else:
            a(f"- **{label}** (`{fname}`): {data}")
    a("")

    # ============ §12 Top blockers
    a("## 11. Top Blockers (Failing or Regressed)")
    a("")
    blockers = [g for g in gate_doc.get("gates", [])
                if g.get("classification") in ("blocked", "regressed")]
    if not blockers:
        a("_No failing or regressed dispatcher gates._")
    else:
        a("| Gate | Band | Enf | Violations | Owner |")
        a("|------|:----:|:---:|-----------:|:-----:|")
        for g in sorted(blockers, key=lambda r: -int(r.get("violation_count", 0))):
            a(f"| `{g['gate_id']}` | {g['band']} | {g['enforcement']} | "
              f"{_human(g['violation_count'])} | {g.get('owner', '?')} |")
    a("")

    # ============ §13 Provenance
    a("## 12. Provenance & Counting Mode")
    a("")
    prov = burndown.get("provenance", {})
    if prov:
        a("| Field | Value |")
        a("|-------|-------|")
        for k, v in prov.items():
            a(f"| `{k}` | {v} |")
    a("")

    a("---")
    a(f"Renderer: `tools/reports/exhaustive_adg_ci_report.py`. "
      f"Re-run: `python tools/reports/exhaustive_adg_ci_report.py`.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--snapshot-dir", type=Path, default=None,
                        help="Directory containing adg_indexed_*.sqlite + report JSONs.")
    parser.add_argument("--out", type=Path,
                        default=ARTIFACTS / "adg_exhaustive_ci_report.md",
                        help="Output markdown path.")
    args = parser.parse_args(argv)

    snapshot_dir, source = _resolve_snapshot_dir(args.snapshot_dir)
    print(f"[exhaustive_adg_ci_report] snapshot_dir={snapshot_dir} source={source}")
    md = render(snapshot_dir, source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md, encoding="utf-8")
    print(f"[exhaustive_adg_ci_report] wrote {args.out.relative_to(REPO)} "
          f"({len(md.splitlines())} lines, {len(md):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
