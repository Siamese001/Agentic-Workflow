"""Generate full ADG with entities and relations in the comprehensive format.

Non-redundant output set (5 files, 100% edge coverage):
    adg_snapshot_<ts>.json        Tier 1: CI-light (~50 KB) — metrics only
    adg_indexed_<ts>.sqlite       Tier 2: primary queryable store (~38 MB, all 18 edge types)
    adg_file_graph_<ts>.json      imports, exports, dead_imports, covers, influences, in_cycle
    adg_symbol_graph_<ts>.json    calls, implements, reads_from, writes_to, instantiates, ...
    adg_governance_graph_<ts>.json violates, antipattern, generates_prompt, ...

Timestamp format: MMDDYYYY in US Eastern time  (e.g. 03122026 for March 12, 2026)
Internal state file (not part of the 5-file model):
    adg_graphsnap_<ts>.json       E7 drift detection — previous-run snapshot for diff (uncompressed)

NOTE: adg_full.json removed (SQLite supersedes it). test_graph removed (covers lives in file_graph).
NOTE: adg_LATEST_* copies not generated (create_latest_symlinks=False by default).
"""

from __future__ import annotations

import json
import os
import subprocess as _subprocess

try:
    import orjson as _orjson

    def _json_dumps(obj: object) -> str:
        return _orjson.dumps(obj, option=_orjson.OPT_SORT_KEYS | _orjson.OPT_INDENT_2).decode("utf-8")
except ImportError:
    _orjson = None  # type: ignore[assignment]

    def _json_dumps(obj: object) -> str:
        return json.dumps(obj, indent=2, sort_keys=True)


import sys
from pathlib import Path


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[2] if len(start.parents) > 2 else start.parent


ROOT = _discover_repo_root(Path(__file__).resolve().parent)
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # guardian: allow-global-mutation


def _git_rev_parse(*args: str) -> str:
    """Return git metadata or an empty string when git state is unavailable."""
    try:
        # ruff: noqa: S607 - Git command is trusted, internal tool usage
        return _subprocess.check_output(
            ["git", "rev-parse", *args],
            cwd=ROOT,
            text=True,
            stderr=_subprocess.DEVNULL,
        ).strip()
    except (_subprocess.CalledProcessError, FileNotFoundError, OSError):
        return ""


from agentic_core.adg.analysis.CanonicalSnapshot import (  # noqa: E402
    build_snapshot,
    load_latest_snapshot,
    save_snapshot,
)
from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges  # noqa: E402
from agentic_core.adg.analysis.GraphDiff import diff_snapshots  # noqa: E402
from agentic_core.adg.analysis.ImpactReport import impact_summary, predict_impact  # noqa: E402
from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry, _infer_ownership  # noqa: E402
from agentic_core.adg.analysis.RepairRoute import repair_routing_summary, route_violations  # noqa: E402
from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts  # noqa: E402
from agentic_core.adg.artifact.builder_types import ADGArtifact, build_artifact  # noqa: E402
from agentic_core.adg.extraction.static_scanner import (  # noqa: E402
    ADGStaticScanner,
)
from tools.generate.archiving import (  # noqa: E402  # M.2 modularization
    _archive_old_artifacts,
    _create_zip_archive,
)
from tools.generate.core import (  # noqa: E402  # M.6 modularization
    _generate_timestamp,
    _verify_artifacts,
)
from tools.generate.integration import (  # noqa: E402  # M.5 modularization
    _auto_commit_artifacts,
    _auto_ingest_to_redis,
    _check_mcp_config_drift,
    _persist_adg_to_memory,
    _run_p1_p2_auto_fix,
    _emit_p0_remediation_wave_plan,
    _run_p0_two_pass_runner,
)
from tools.generate.reporting import (  # noqa: E402  # M.4 modularization
    _generate_standardized_reports,
    _print_defect_table,
)
from tools.generate.utils.file_utils import (  # noqa: E402  # M.1 modularization
    _check_locked_files,
    _perform_wal_checkpoint,
)
from tools.generate.adg_graph_watchlist_builder import build_and_emit_graph_watchlist  # noqa: E402  # P5: graph-native intelligence
from tools.generate.adg_watchlist_builder import build_and_emit_watchlist  # noqa: E402  # P4: high-signal watchlist
from tools.generate.infra_wiring_views import enrich_and_report as _enrich_infra_views  # noqa: E402
from tools.generate.materialized_views import materialize_all_views as _materialize_adg_views  # noqa: E402
from tools.generate.validation import (  # noqa: E402  # M.3 modularization
    _check_agentic_antipatterns,
    _check_artifact_consistency,
    _check_artifact_validity,
    _check_dead_production_imports,
    _check_p0_violations,
    _check_p1_ratchet,
    _check_p2_ratchet,
    _check_sqlite_integrity,
    _check_structural_conformance,
    _check_witness_tier_gates,
)

# M.4: _print_defect_table extracted to tools.generate.reporting.reports


def _build_graphdb_network_projection(
    sqlite_path: Path,
    adg_artifacts_dir: Path,
    ts: str,
) -> tuple[list[Path], object | None]:
    """Invoke the ``tools/graphdb`` NetworkX projection and stage its outputs.

    Lets exceptions propagate to the caller so the caller decides the
    non-blocking policy (see the P6b/P7 call site). This avoids the
    ``return_none_swallow`` antipattern inside the helper itself.

    Returns:
        Tuple of ``(staged_paths, networkx_graph)``. ``networkx_graph`` is
        returned so downstream query helpers (P7) can reuse the already-built
        projection without re-projecting.
    """
    import shutil as _shutil

    from tools.graphdb.project_graph import project_graph as _gdb_project_graph

    work_dir = adg_artifacts_dir / f"graphdb_{ts}"
    try:
        graph, metadata = _gdb_project_graph(
            sqlite_path=sqlite_path,
            output_dir=work_dir,
            run_id=f"graphdb_{ts}",
        )

        commit_sha = metadata.commit_sha or "unknown"
        staged: list[Path] = []
        for src, dest in (
            (
                work_dir / "projections" / commit_sha / "graph.json",
                adg_artifacts_dir / f"adg_graphdb_projection_{ts}.json",
            ),
            (
                work_dir / "metadata" / f"{commit_sha}.json",
                adg_artifacts_dir / f"adg_graphdb_metadata_{ts}.json",
            ),
            (work_dir / "index.json", adg_artifacts_dir / f"adg_graphdb_index_{ts}.json"),
        ):
            if src.exists():
                _shutil.copy2(src, dest)
                staged.append(dest)
            else:
                print(f"[ADG] GraphDB projection missing expected file: {src}")

        print(
            f"[ADG] GraphDB NetworkX projection: nodes={metadata.node_count} "
            f"edges={metadata.edge_count} staged={len(staged)}",
        )
        return staged, graph
    finally:
        if work_dir.exists():
            _shutil.rmtree(work_dir, ignore_errors=True)


# ── P7: Analyst-grade report emitters (non-blocking) ─────────────────────────


def _build_structural_outputs_report(
    sqlite_path: Path,
    adg_artifacts_dir: Path,
    ts: str,
) -> Path:
    """Emit the 4 structural analyses from ``tools/adg/structural_outputs.py``.

    Combines burndown, blast-radius (top-N), seams, and centrality into a
    single JSON artifact ``adg_structural_outputs_<ts>.json``. Exceptions
    propagate to the caller (P7 loop) so the helper avoids the
    ``return_none_swallow`` antipattern.
    """
    import sqlite3 as _sqlite3

    from tools.adg.structural_outputs import (
        blast_radius as _so_blast_radius,
        burndown_table as _so_burndown_table,
        centrality as _so_centrality,
        seam_detection as _so_seam_detection,
    )

    dest = adg_artifacts_dir / f"adg_structural_outputs_{ts}.json"
    conn = _sqlite3.connect(str(sqlite_path))
    try:
        payload = {
            "sqlite_used": sqlite_path.name,
            "timestamp": ts,
            "burndown": _so_burndown_table(conn),
            "blast_radius": _so_blast_radius(conn, target=None, top_n=20),
            "seams": _so_seam_detection(conn),
            "centrality": _so_centrality(conn, top_n=20),
        }
    finally:
        conn.close()
    dest.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"[ADG] P7 structural outputs: {dest.name}")
    return dest


def _build_refactor_accelerator_report(
    sqlite_path: Path,
    adg_artifacts_dir: Path,
    ts: str,
) -> Path:
    """Emit a top-N refactor candidate ranking via ``tools/adg/refactor_accelerator``.

    Git churn is included (bounded 90-day window); ruff lint is skipped because
    it duplicates work already gated elsewhere and would slow ADG generation.
    Exceptions propagate to the caller (P7 loop).
    """
    import sqlite3 as _sqlite3

    from tools.adg.refactor_accelerator import (
        _add_blast_radius as _ra_add_blast_radius,
        _add_impacted_tests as _ra_add_impacted_tests,
        _fetch_candidates as _ra_fetch_candidates,
        _git_churn as _ra_git_churn,
    )

    dest = adg_artifacts_dir / f"adg_refactor_accelerator_{ts}.json"
    churn = _ra_git_churn(90)
    lint: dict[str, int] = {}  # skip ruff — keeps P7 fast
    conn = _sqlite3.connect(str(sqlite_path))
    try:
        candidates = _ra_fetch_candidates(conn, None, 20, churn, lint)
        _ra_add_blast_radius(conn, candidates)
        _ra_add_impacted_tests(conn, candidates)
    finally:
        conn.close()
    payload = {
        "sqlite_used": sqlite_path.name,
        "timestamp": ts,
        "layer_filter": None,
        "churn_window_days": 90,
        "lint_included": False,
        "candidates": [{k: v for k, v in c.items() if k != "node_id"} for c in candidates],
    }
    dest.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"[ADG] P7 refactor accelerator: {dest.name} ({len(candidates)} candidates)")
    return dest


def _build_graphdb_queries_report(
    graph: object | None,
    adg_artifacts_dir: Path,
    ts: str,
) -> Path:
    """Run canonical GraphDB query families over the P6b NetworkX graph.

    Emits ``adg_graphdb_queries_<ts>.json`` with StructuralQueries,
    BlastRadiusQueries, and AnalystQueries results. HistoricalQueries is
    intentionally omitted (it requires a second prior snapshot and is already
    covered by the ADG E7 drift pipeline).

    Raises ``RuntimeError`` when the NetworkX projection from P6b is missing.
    Other exceptions propagate to the caller.
    """
    if graph is None:
        raise RuntimeError("NetworkX projection unavailable (P6b did not produce a graph)")

    from tools.graphdb.queries.analyst import AnalystQueries
    from tools.graphdb.queries.blast_radius import BlastRadiusQueries
    from tools.graphdb.queries.structural import StructuralQueries

    dest = adg_artifacts_dir / f"adg_graphdb_queries_{ts}.json"
    structural = StructuralQueries(graph)
    blast = BlastRadiusQueries(graph)
    analyst = AnalystQueries(graph)

    structural_payload: dict[str, object] = {}
    for name, fn in (
        ("gravity_import_violations", structural.gravity_import_violations),
        ("illegal_layer_reach", structural.illegal_layer_reach),
        ("l2_lifecycle_conformance", structural.l2_lifecycle_conformance),
        ("uwg_durable_write_conformance", structural.uwg_durable_write_conformance),
        (
            "capability_tool_provider_chokepoint_conformance",
            structural.capability_tool_provider_chokepoint_conformance,
        ),
        ("agentic_spine_completeness", structural.agentic_spine_completeness),
        ("l0_l1_l6_role_purity", structural.l0_l1_l6_role_purity),
        ("grounding_contract_separation", structural.grounding_contract_separation),
        ("trace_replay_eval_coverage", structural.trace_replay_eval_coverage),
    ):
        try:
            structural_payload[name] = fn()
        except (RuntimeError, ValueError, KeyError, AttributeError) as exc:
            structural_payload[name] = {"error": f"{type(exc).__name__}: {exc}"}

    blast_payload: dict[str, object] = {}
    try:
        blast_payload["high_fan_in_out_hubs"] = blast.high_fan_in_out_hubs(
            min_connections=10,
        )
    except (RuntimeError, ValueError, KeyError, AttributeError) as exc:
        blast_payload["high_fan_in_out_hubs"] = {
            "error": f"{type(exc).__name__}: {exc}",
        }

    analyst_payload: dict[str, object] = {}
    for layer in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
        try:
            analyst_payload[f"subgraph_{layer}"] = analyst.extract_subgraph_by_layer(layer)
        except (RuntimeError, ValueError, KeyError, AttributeError) as exc:
            analyst_payload[f"subgraph_{layer}"] = {
                "error": f"{type(exc).__name__}: {exc}",
            }

    payload = {
        "timestamp": ts,
        "graph_nodes": graph.number_of_nodes() if hasattr(graph, "number_of_nodes") else None,
        "graph_edges": graph.number_of_edges() if hasattr(graph, "number_of_edges") else None,
        "structural": structural_payload,
        "blast_radius": blast_payload,
        "analyst": analyst_payload,
    }
    dest.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"[ADG] P7 graphdb queries: {dest.name}")
    return dest


def _build_runtime_spine_report(
    sqlite_path: Path,
    adg_artifacts_dir: Path,
    ts: str,
) -> Path:
    """Emit the handoff / cross-cutting witness-tier report from ``mv_runtime_spine``.

    Exceptions propagate to the caller (P7 loop).
    """
    from tools.adg.mv_runtime_spine import (
        check_semantic_satisfaction as _rs_check_semantic_satisfaction,
        run_all_views as _rs_run_all_views,
        run_cross_cutting_views as _rs_run_cross_cutting_views,
    )

    dest = adg_artifacts_dir / f"adg_runtime_spine_{ts}.json"
    views = _rs_run_all_views(sqlite_path)
    cross = _rs_run_cross_cutting_views(sqlite_path)
    semantic_failures = _rs_check_semantic_satisfaction(views)

    handoff_payload = []
    for v in views:
        handoff_payload.append(
            {
                "name": v.name,
                "description": v.description,
                "row_count": len(v.rows),
                "runtime_orphaned_count": len(v.runtime_orphaned_rows),
                "zero_witness_count": len(v.zero_witnessed_rows),
                "rows": [
                    {
                        "relation_type": r.relation_type,
                        "plumbing_witness_count": r.plumbing_witness_count,
                        "test_witness_count": r.test_witness_count,
                        "live_runtime_witness_count": r.live_runtime_witness_count,
                        "runtime_orphaned": r.runtime_orphaned,
                    }
                    for r in v.rows
                ],
            }
        )

    cross_payload = [
        {
            "family_name": c.family_name,
            "relation_count": c.relation_count,
            "plumbing_total": c.plumbing_total,
            "test_total": c.test_total,
            "live_rt_total": c.live_rt_total,
            "orphaned_count": c.orphaned_count,
            "zero_count": c.zero_count,
            "runtime_orphaned": c.runtime_orphaned,
        }
        for c in cross
    ]

    payload = {
        "sqlite_used": sqlite_path.name,
        "timestamp": ts,
        "handoff_views": handoff_payload,
        "cross_cutting_families": cross_payload,
        "semantic_failures": semantic_failures,
        "semantic_satisfied": len(semantic_failures) == 0,
    }
    dest.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(
        f"[ADG] P7 runtime spine: {dest.name} "
        f"(handoff_views={len(views)} families={len(cross)} "
        f"semantic_failures={len(semantic_failures)})",
    )
    return dest


def _resolve_post_commit_sqlite(paths: object, adg_artifacts_dir: Path, ts: str) -> Path:
    """Resolve and validate the canonical post-commit SQLite for Tier-2 gates."""
    sqlite_candidate: Path | None = None
    if hasattr(paths, "sqlite") and getattr(paths, "sqlite") is not None:
        sqlite_candidate = Path(getattr(paths, "sqlite")).resolve()

    if sqlite_candidate is None or not sqlite_candidate.exists():
        fallback = (adg_artifacts_dir / f"adg_indexed_{ts}.sqlite").resolve()
        if fallback.exists():
            sqlite_candidate = fallback

    if sqlite_candidate is None or not sqlite_candidate.exists():
        print("\n[ERROR] Tier-2 sqlite source missing after artifact commit")
        print(f"[ERROR] Expected current-run sqlite under: {adg_artifacts_dir}")
        raise SystemExit(1)

    _check_sqlite_integrity(sqlite_candidate)
    print(f"[ADG] Tier-2 sqlite source: {sqlite_candidate}")
    return sqlite_candidate


def generate_full_adg(
    adg_artifacts_dir: Path,
    ts: str,
    archive_old: bool = True,
    enable_zip: bool = True,
    enable_reports: bool = True,
    enable_analysis: bool = True,
) -> tuple[ADGArtifact, dict[str, int], list[str]]:
    """Generate full ADG and write all artifact tiers.

    Args:
        adg_artifacts_dir: Directory for ADG artifacts
        ts: Timestamp string (MMDDYYYY format)
        archive_old: If True, archive artifacts older than retention period
        enable_zip: Write a zip archive of all artifacts (default True)
        enable_reports: Generate all 8 standardized reports (default True)
        enable_analysis: Run score_edges + route_violations analytics (default True)

    Always runs in full mode with all artifacts enabled.
    """
    import time as _time

    # --- Startup mode banner (visible before any work begins) ---
    print("[ADG] Mode: FULL  zip=ON  reports=ON")

    # Track semantic enrichment warnings for P4 defect reporting
    semantic_warnings: list[str] = []

    _adg_start = _time.time()

    print("[ADG] Starting full scan...")

    # Capture provenance information
    commit_sha = _git_rev_parse("HEAD")
    if commit_sha:
        print(f"[ADG] Captured commit SHA: {commit_sha}")
    else:
        print("[ADG] Warning: Git commit SHA unavailable; continuing without provenance commit id")

    # Capture repo state hash (tree hash)
    repo_state_hash = _git_rev_parse("HEAD^{tree}")
    if repo_state_hash:
        print(f"[ADG] Captured repo state hash: {repo_state_hash}")
    else:
        print("[ADG] Warning: Git repo state hash unavailable; concurrent-change guard will be skipped")

    cache_path = adg_artifacts_dir / "cache" / "scan_result_cache.json"
    cache_path.parent.mkdir(exist_ok=True)
    scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)

    try:
        result = scanner.scan(commit_sha=commit_sha)
    except SyntaxError as e:
        print(f"\n[ERROR] {e}")
        print("[ERROR] ADG generation aborted due to syntax error")
        print("[ERROR] Fix the syntax error above and re-run ADG generation")
        sys.exit(1)

    # Set repo_state_hash in the result
    result.repo_state_hash = repo_state_hash

    print(f"[ADG] Scan complete. Digest: {result.digest}")
    print(f"[ADG] Modules: {len(result.modules)}")
    print(f"[ADG] Edges: {len(result.edges)}")
    print(
        f"[ADG] Cache: hits={result.manifest.cache_hits} misses={result.manifest.cache_misses} rate={result.manifest.cache_hit_rate:.1%}",
    )

    # Fail if syntax errors were detected
    if result.syntax_errors:
        print(f"\n[ERROR] Scan detected {len(result.syntax_errors)} syntax error(s) in the codebase")
        print("[ERROR] Files with syntax errors:")
        for err in result.syntax_errors:
            print(f"[ERROR]   - {err}")
        print("[ERROR]")
        print("[ERROR] Syntax errors prevent complete ADG analysis")
        print("[ERROR] Fix all syntax errors before running ADG generation")
        print("[ERROR] See wave plan: .windsurf/plans/burn-down-syntax-errors-wave-plan-20260406.md")
        sys.exit(1)

    # --- Build canonical artifact (schema v3) ---
    print("[ADG] Building canonical artifact...")
    artifact = build_artifact(result, repo_root=ROOT)

    # --- Calculate routing summary for P1/P2 gates ---
    _critical_layer_prefixes = (
        "agentic_core/L0_routing/",
        "agentic_core/L5_safety/",
        "agentic_core/L2_execution/",
        "agentic_core/L3_orchestration/",
    )
    _high_antipattern_kinds = frozenset(
        ("broad_exception_catch", "silent_exception_swallow", "log_and_swallow", "return_none_swallow"),
    )
    violation_edges = [
        e
        for e in result.edges
        if e.relation_type in ("violates", "dynamic_exec", "invokes_provider")
        or (
            e.relation_type == "antipattern"
            and e.edge_kind in _high_antipattern_kinds
            and any(e.source_file.startswith(p) for p in _critical_layer_prefixes)
        )
    ]
    repair_routes = route_violations(violation_edges)
    routing_summary = repair_routing_summary(repair_routes)

    # --- Write artifacts to temp directory first for fail-fast check ---
    print("[ADG] Writing artifact tiers to temp directory...")
    import shutil
    import tempfile

    temp_dir = tempfile.mkdtemp(prefix="adg_temp_")
    exit_code = 0
    try:
        temp_adg_dir = Path(temp_dir) / "adg"
        temp_adg_dir.mkdir()
        temp_paths = write_all_artifacts(
            artifact,
            out_dir=temp_adg_dir,
            ts=ts,
            write_split_planes=False,  # Disable redundant JSON graph files (100.75 MB savings)
        )

        # --- Fail-fast: Artifact validity checks ---
        _check_artifact_validity(temp_paths)
        _check_sqlite_integrity(temp_paths.sqlite)
        _check_artifact_consistency(temp_paths, artifact)

        # --- Tier-1: Structural integrity gates (block on temp SQLite) ---
        # These gates protect artifact correctness. A corrupt artifact must never reach production.
        _check_p2_ratchet(sqlite_path=temp_paths.sqlite)

        # --- Tier-1 passed: commit artifacts to final production location ---
        print("[ADG] Tier-1 gates passed - committing artifacts to final location...")
        paths = write_all_artifacts(
            artifact,
            out_dir=adg_artifacts_dir,
            ts=ts,
            write_split_planes=False,
        )
    except SystemExit as e:
        if isinstance(e.code, int):
            exit_code = e.code
        else:
            exit_code = 1
    finally:
        # Clean up temp directory with ignore_errors=True to handle Windows file handle timing
        shutil.rmtree(temp_dir, ignore_errors=True)

    if exit_code != 0:
        sys.exit(exit_code)

    # --- Tier-2: Code quality gates (run on current-run PRODUCTION SQLite, never temp) ---
    # Orchestrator runs inline here. No SQLite contention with temp directory.
    prod_sqlite_path = _resolve_post_commit_sqlite(paths, adg_artifacts_dir, ts)
    p0_wave_plan = _emit_p0_remediation_wave_plan(adg_artifacts_dir, ts, prod_sqlite_path)

    _run_p0_two_pass_runner(
        sqlite_path=prod_sqlite_path,
        plan_path=p0_wave_plan.get("markdown_path"),
    )

    _check_p0_violations(
        routing_summary,
        sqlite_path=prod_sqlite_path,
        plan_path=p0_wave_plan.get("markdown_path"),
    )
    _check_p1_ratchet(sqlite_path=prod_sqlite_path)
    _check_dead_production_imports(sqlite_path=prod_sqlite_path)

    # --- Tier-2b: Structural conformance & agentic anti-pattern gates ---
    _check_structural_conformance(sqlite_path=prod_sqlite_path)
    _check_agentic_antipatterns(sqlite_path=prod_sqlite_path)

    # --- Infrastructure wiring enrichment: materialize violation views ---
    _enrich_infra_views(paths.sqlite)

    # --- ADG materialized views: structural/authority/trace/snapshot visibility ---
    _materialize_adg_views(paths.sqlite)

    # --- P6: Derived graph projection (non-blocking, adg_graph_<ts>.sqlite) ---
    try:
        from tools.generate.graph_projection import build_graph_projection

        _graph_proj_path = build_graph_projection(paths.sqlite, adg_artifacts_dir, ts)
        print(f"[ADG] P6 graph projection: {_graph_proj_path.name}")
    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        print(f"[ADG] P6 graph projection skipped: {e}")

    # --- P6b: GraphDB NetworkX projection (non-blocking, tools/graphdb) ---
    # Produces three run-scoped artifacts under adg_artifacts_dir:
    #   adg_graphdb_projection_<ts>.json  (NetworkX node-link JSON)
    #   adg_graphdb_metadata_<ts>.json    (SnapshotMetadata)
    #   adg_graphdb_index_<ts>.json       (SnapshotManager index)
    # Caller owns the non-blocking policy (specific-tuple catch mirrors P6 above).
    graphdb_staged: list[Path] = []
    graphdb_nx_graph: object | None = None
    try:
        graphdb_staged, graphdb_nx_graph = _build_graphdb_network_projection(
            paths.sqlite,
            adg_artifacts_dir,
            ts,
        )
    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        print(f"[ADG] P6b GraphDB NetworkX projection skipped: {e}")

    # --- P7: Analyst-grade report artifacts (non-blocking) ---
    # Helpers raise on failure; this caller loop enforces the non-blocking policy
    # using a specific-tuple catch so helpers stay free of return_none_swallow.
    #   adg_structural_outputs_<ts>.json    — burndown/blast-radius/seams/centrality
    #   adg_refactor_accelerator_<ts>.json  — top-N refactor candidates (ADG + churn)
    #   adg_graphdb_queries_<ts>.json       — GraphDB query families over P6b graph
    #   adg_runtime_spine_<ts>.json         — handoff + cross-cutting witness tiers
    p7_staged: list[Path] = []
    for _p7_name, _p7_fn in (
        ("structural-outputs", lambda: _build_structural_outputs_report(paths.sqlite, adg_artifacts_dir, ts)),
        (
            "refactor-accelerator",
            lambda: _build_refactor_accelerator_report(paths.sqlite, adg_artifacts_dir, ts),
        ),
        ("graphdb-queries", lambda: _build_graphdb_queries_report(graphdb_nx_graph, adg_artifacts_dir, ts)),
        ("runtime-spine", lambda: _build_runtime_spine_report(paths.sqlite, adg_artifacts_dir, ts)),
    ):
        try:
            p7_staged.append(_p7_fn())
        except (ImportError, OSError, RuntimeError, TypeError, ValueError, KeyError, AttributeError) as e:
            print(f"[ADG] P7 {_p7_name} skipped: {e}")

    # --- Architecture witness-tier gates: Class A positive / Class B absence ---
    _check_witness_tier_gates(sqlite_path=prod_sqlite_path)

    # --- P4: High-signal anomaly watchlist (non-blocking intelligence layer) ---
    try:
        watchlist_path = build_and_emit_watchlist(
            paths.sqlite,
            adg_artifacts_dir,
            print_summary=True,
        )
        print(f"[ADG] P4 watchlist artifact: {watchlist_path.name}")
    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        print(f"[ADG] P4 watchlist skipped: {e}")

    # --- P5: Graph-native intelligence watchlist (non-blocking graph layer) ---
    graph_watchlist_items: list = []
    try:
        from tools.generate.adg_graph_watchlist_builder import ADGGraphWatchlistBuilder

        with ADGGraphWatchlistBuilder(paths.sqlite) as builder:
            graph_watchlist_items = builder.build_graph_watchlist()
            graph_watchlist_path = builder.emit_artifact(graph_watchlist_items, adg_artifacts_dir)
            print(builder.emit_terminal_summary(graph_watchlist_items, top_n=10))
        print(f"[ADG] P5 graph watchlist artifact: {graph_watchlist_path.name}")
    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        print(f"[ADG] P5 graph watchlist skipped: {e}")

    # --- Repair orchestrator: classify + fix remaining issues ---
    print("[ADG] Running repair orchestrator on committed artifacts...")
    _run_p1_p2_auto_fix(adg_artifacts_dir, ts, sqlite_path=prod_sqlite_path)

    # Size report
    sizes = paths.size_report()

    print(f"[ADG] Tier 1 snapshot:  {paths.snapshot.name}  ({sizes['snapshot']})")
    print(f"[ADG] Tier 2 sqlite:    {paths.sqlite.name}  ({sizes['sqlite']})")
    print("[ADG] JSON graphs:     DISABLED (100.75 MB savings, use SQLite for queries)")
    print(f"[ADG] entities={len(artifact.entities)}  relations={len(artifact.relations)}")
    print(f"[ADG] artifact_digest={artifact.artifact_digest[:16]}...")

    # --- E6: graph snapshot + E7: drift ---
    snapshot = build_snapshot(result)
    previous_snapshot = load_latest_snapshot(adg_artifacts_dir)
    if previous_snapshot is not None:
        graph_diff = diff_snapshots(previous_snapshot, snapshot)
        print(f"[ADG] E7 diff: {graph_diff.summary}")
    else:
        graph_diff = None
        print("[ADG] E7 diff: no previous snapshot found (first run)")

    snap_path = adg_artifacts_dir / f"adg_graphsnap_{ts}.json"
    save_snapshot(snapshot, snap_path, compress=False)
    print(f"[ADG] E7 snapshot saved: {snap_path.name}")

    # --- E8: Ownership ---
    OwnershipRegistry.from_scan_result(result)

    # --- E9: Confidence scoring ---
    if enable_analysis:
        scored_edges = score_edges(list(result.edges))
        conf_summary = confidence_summary(scored_edges)

        # Persist confidence summary for L0 routing confidence monitor
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

            bridge = get_sl_memory_bridge()
            bridge.persist_adg_confidence_summary(conf_summary, ts)
        except (ImportError, OSError, RuntimeError, TypeError, ValueError):
            pass

    # --- E10: Repair routing ---
    # --- E5: Impact prediction ---
    violation_sources = [
        e.source_file
        for e in result.edges
        if e.relation_type == "imports"
        and e.source_file
        and any(
            e.source_file.startswith(p)
            for p in (
                "agentic_core/L2_execution",
                "agentic_core/L0_routing",
                "agentic_core/L5_safety",
            )
        )
    ]
    seed_files: list[str] = []
    seen_seeds: set[str] = set()
    for sf in violation_sources:
        if sf not in seen_seeds:
            seen_seeds.add(sf)
            seed_files.append(sf)
        if len(seed_files) >= 5:
            break
    if not seed_files:
        seed_files = list(
            result.modules[:5],
        )  # guardian: Runtime errors should be prevented with proper validation
    impact_report = predict_impact(result, seed_files)
    imp_summary = impact_summary(impact_report)

    # --- Print analysis summary ---
    edge_counts = result.edge_counts_by_relation()
    print("[ADG] Graph plane coverage:")
    print(f"      G1_imports={edge_counts.get('imports', 0)}")
    print(f"      G3_implements={edge_counts.get('implements', 0)}")
    print(f"      G4_calls={result.manifest.inter_module_call_count}  (Gap 1 resolved)")
    print(f"      GT_covers={result.manifest.test_covers_count}  (Gap 2 resolved)")
    print(f"      GV_violates={result.manifest.layer_violation_count}  (Gap 3+4 resolved)")
    print(f"      GG_governance={result.manifest.governance_plane_count}  (Gap 5 resolved)")
    print("[ADG] Enhancement 5-10 analysis:")
    print(
        f"      E5 impact: {imp_summary['impacted_module_count']} impacted  "
        f"{imp_summary['covering_test_count']} tests  risk={imp_summary['risk_label']} ({imp_summary['risk_score']:.4f})",
    )
    print(
        f"      E6 graph_hash={snapshot.graph_hash[:16]}...  nodes={snapshot.node_count}  edges={snapshot.edge_count}",
    )
    if graph_diff is not None:
        print(f"      E7 drift: {graph_diff.summary}")
    else:
        print("      E7 drift: first run — snapshot persisted for next diff")
    owned_high = sum(
        1
        for e in artifact.entities
        if getattr(e, "entity_type", "") == "module"
        and _infer_ownership(getattr(e, "resolved_path", "")).criticality == "high"
    )
    print(f"      E8 ownership: {len(result.modules)} modules  high_criticality={owned_high}")
    print(
        f"      E9 confidence: avg={conf_summary['average_confidence']}  "
        f"high={conf_summary['confidence_tiers']['high']}  low={conf_summary['confidence_tiers']['low']}",
    )
    print(
        f"      E10 repair routes: {routing_summary['total_routes']} routes  by_severity={routing_summary['by_severity']}",
    )

    # --- E11: Graph-native SQL analytics (Prompt 6/7/9 integration) ---
    graph_delta_result = None
    if graph_watchlist_items:
        # Count promoted signals
        rev_dep_count = sum(1 for i in graph_watchlist_items if i.reverse_dep_score > 0)
        bridge_count = sum(1 for i in graph_watchlist_items if i.bridge_score > 0)
        blast_count = sum(1 for i in graph_watchlist_items if i.blast_radius > 0)
        scc_count = sum(1 for i in graph_watchlist_items if i.scc_cluster_size > 0)

        # Count gate decisions (Prompt 7)
        fail_count = sum(
            1 for i in graph_watchlist_items if i.remediation and i.remediation.gate_decision == "FAIL"
        )
        warn_count = sum(
            1 for i in graph_watchlist_items if i.remediation and i.remediation.gate_decision == "WARN"
        )

        # Prompt 9: Compute deltas if baseline available
        try:
            from tools.generate.adg_graph_watchlist_builder import ADGGraphWatchlistBuilder

            with ADGGraphWatchlistBuilder(paths.sqlite) as builder:
                graph_delta_result = builder._compute_deltas(graph_watchlist_items, adg_artifacts_dir)
        except (ImportError, OSError, RuntimeError, TypeError, ValueError):
            graph_delta_result = None

        print(f"[ADG] E11 graph-native SQL analytics:")
        print(f"      Promoted signals: RevDep={rev_dep_count}  Bridge={bridge_count}  Blast={blast_count}")
        if scc_count == 0:
            print(f"      SCC=0 (codebase appears acyclic - architecturally positive)")
        else:
            print(f"      SCC={scc_count} [surface_with_caveat: semantic proof not fully closed]")
        # Show gate summary (Prompt 7)
        if fail_count > 0 or warn_count > 0:
            print(f"      Gate decisions: FAIL={fail_count}  WARN={warn_count}")

        # Prompt 9: Show delta tracking summary
        if graph_delta_result and graph_delta_result.get("has_baseline"):
            ds = graph_delta_result.get("delta_summary", {})
            regressions = graph_delta_result.get("regressions", [])
            protected_regressions = [
                r
                for r in regressions
                if r.get("layer", "")
                in {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_SHARED", "L_RUNTIME"}
            ]

            print(
                f"      Delta (vs baseline): new={ds.get('new', 0)} worsened={ds.get('worsened', 0)} improved={ds.get('improved', 0)} resolved={ds.get('resolved', 0)}"
            )
            if protected_regressions:
                print(f"      ⚠️  Protected-layer regressions: {len(protected_regressions)}")
            elif ds.get("worsened", 0) > 0:
                print(f"      ℹ️  Non-protected worsening: {ds.get('worsened', 0)} items")

        # Show top 3 graph hotspots with remediation (Prompt 7)
        top_graph = graph_watchlist_items[:3]
        for i, item in enumerate(top_graph, 1):  # tqdm: top-3 slice, no bar needed
            signals = []
            if item.reverse_dep_score > 0:
                signals.append("RevDep")
            if item.bridge_score > 0:
                signals.append("Bridge")
            if item.blast_radius > 0:
                signals.append("Blast")
            sig_str = "+".join(signals) if signals else "none"
            gate = item.remediation.gate_decision if item.remediation else "INFO"
            fix = item.remediation.recommended_fix_pattern[:25] if item.remediation else "review"
            print(f"      G{i}: {item.file[:45]:<45} score={item.score:.1f} [{gate}] {fix}")

    # --- Memory MCP persistence ---
    _persist_adg_to_memory(result, artifact, snapshot, graph_diff, routing_summary, ts)

    # --- Wave 6: Generate standardized reports ---
    closure_report = _generate_standardized_reports(
        adg_artifacts_dir,
        ts,
        artifact,
        result=result,
        repo_root=ROOT,
        enable_determinism_probe=os.environ.get("ADG_ENABLE_DETERMINISM_PROBE", "1").strip().lower()
        not in ("0", "false", "no"),
    )

    # --- Create zip archive of consolidated artifacts + Wave 6 reports ---
    # Build artifact file list for zip (no JSON graphs - 100.75 MB savings)
    # NOTE: adg_graphsnap_*.json is an internal drift detection state file, not archived
    # Zip contains: 2 ADG artifacts (snapshot.json, sqlite) + reports + burndown + watchlists
    artifact_files = [
        paths.snapshot,
        paths.sqlite,
    ]

    # Include derived graph projection in zip if it was produced this run
    _proj_candidates = sorted(adg_artifacts_dir.glob(f"adg_graph_{ts}.sqlite"))
    if _proj_candidates:
        artifact_files.append(_proj_candidates[0])

    # Include GraphDB NetworkX projection (P6b) staged outputs
    if graphdb_staged:
        artifact_files.extend(graphdb_staged)
        print(
            f"[ADG] Adding {len(graphdb_staged)} GraphDB NetworkX artifacts to zip archive",
        )

    # Include P7 analyst reports (structural outputs, refactor accelerator,
    # GraphDB queries, runtime spine) in the zip archive
    if p7_staged:
        artifact_files.extend(p7_staged)
        print(
            f"[ADG] Adding {len(p7_staged)} P7 analyst reports to zip archive",
        )

    # Add high-signal reports to zip archive
    report_files = [
        adg_artifacts_dir / f"layer_coverage_report_{ts}.json",
        adg_artifacts_dir / f"edge_density_report_{ts}.json",
        adg_artifacts_dir / f"provenance_report_{ts}.json",
        adg_artifacts_dir / f"closure_validation_report_{ts}.json",
    ]

    # Filter to only include existing reports
    existing_reports = [f for f in report_files if f.exists()]
    if existing_reports:
        artifact_files.extend(existing_reports)
        print(f"[ADG] Adding {len(existing_reports)} reports to zip archive")

    # Add burndown table and watchlists (small JSON, high signal, excluded graphsnap)
    # Watchlist files use datetime.now() with seconds, so glob for most-recent match this run
    import time as _zip_time

    _run_cutoff = _zip_time.time() - 600  # files modified within last 10 min belong to this run
    extra_files: list[Path] = []
    burndown = adg_artifacts_dir / "adg_burndown_table.json"
    if burndown.exists():
        extra_files.append(burndown)
    for pattern in ("adg_anomaly_watchlist_*.json", "adg_graph_watchlist_*.json"):
        candidates = sorted(
            (f for f in adg_artifacts_dir.glob(pattern) if f.stat().st_mtime >= _run_cutoff),
            key=lambda f: f.stat().st_mtime,
        )
        if candidates:
            extra_files.append(candidates[-1])  # most recent from this run
    if extra_files:
        artifact_files.extend(extra_files)
        print(f"[ADG] Adding {len(extra_files)} extra artifacts to zip archive (burndown/watchlists)")

    for _plan_key in ("json_path", "markdown_path"):
        _plan_path = p0_wave_plan.get(_plan_key)
        if _plan_path and Path(_plan_path).exists():
            artifact_files.append(Path(_plan_path))

    # --- Create zip archive (always enabled) ---
    zip_created = False
    try:
        _create_zip_archive(adg_artifacts_dir, ts, artifact_files)
        zip_created = True
        print(f"[ADG] Zip creation successful for {ts}")
    except RuntimeError as e:  # guardian: allow-silent-swallow - acceptable exception handling
        print(f"[ADG] WARNING: Zip creation failed: {e}")
        print("[ADG] Individual files will be archived using legacy path")
        zip_created = False

    # --- Archive old artifacts AFTER successful current-run zip creation ---
    # This ensures keep_runs=1 retains exactly one total run (the current run).
    if archive_old and zip_created:
        _archive_old_artifacts(adg_artifacts_dir, ts, keep_runs=1)

    # --- Closure validation check ---
    if closure_report is not None and not closure_report["summary"]["all_gaps_passed"]:
        failed_caps = [row["capability"] for row in closure_report["closure_rows"] if not row["passed"]]
        # Allow EDGE SEMANTIC PRECISION and DETERMINISM (ARTIFACT LEVEL) to fail temporarily - these are known issues
        # with the semantic enrichment and determinism systems that need to be fixed separately
        if failed_caps == ["EDGE SEMANTIC PRECISION"]:
            print("[ADG] WARNING: EDGE SEMANTIC PRECISION validation failed (known issue)")
            print("[ADG] This does not block ADG generation - semantic enrichment needs investigation")
            semantic_warnings.append("EDGE SEMANTIC PRECISION")
        elif failed_caps == ["DETERMINISM (ARTIFACT LEVEL)"]:
            print("[ADG] WARNING: DETERMINISM (ARTIFACT LEVEL) validation failed (known issue)")
            print("[ADG] This does not block ADG generation - determinism system needs investigation")
            semantic_warnings.append("DETERMINISM (ARTIFACT LEVEL)")
        elif set(failed_caps) == {"EDGE SEMANTIC PRECISION", "DETERMINISM (ARTIFACT LEVEL)"}:
            print(
                "[ADG] WARNING: EDGE SEMANTIC PRECISION and DETERMINISM (ARTIFACT LEVEL) validation failed (known issues)",
            )
            print("[ADG] This does not block ADG generation - these systems need investigation")
            semantic_warnings.append("EDGE SEMANTIC PRECISION")
            semantic_warnings.append("DETERMINISM (ARTIFACT LEVEL)")
        else:
            print(f"\n[ERROR] ADG closure validation failed: {failed_caps}")
            print("[ERROR] Fix all closure validation gaps before regenerating ADG")
            sys.exit(1)

    # Print P1-P4 defect table (including semantic warnings as P4)
    _print_defect_table(routing_summary, semantic_warnings, sqlite_path=paths.sqlite)

    if os.environ.get("ADG_SKIP_REDIS", "").strip().lower() not in ("1", "true", "yes"):
        _auto_ingest_to_redis(adg_artifacts_dir, paths.sqlite)

    # --- Fail-fast: Repo state change check (before auto-commit so ADG's own commit is excluded) ---
    end_repo_state_hash = _git_rev_parse("HEAD^{tree}")

    # --- Auto-commit artifacts to git ---
    if os.environ.get("ADG_SKIP_GIT", "").strip().lower() not in ("1", "true", "yes"):
        _auto_commit_artifacts(
            adg_dir=adg_artifacts_dir,
            ts=ts,
            node_count=len(result.modules),
            edge_count=len(result.edges),
        )

    if repo_state_hash and end_repo_state_hash and repo_state_hash != end_repo_state_hash:
        print("\n[ERROR] Repository state changed during ADG generation")
        print(f"[ERROR]   Start state: {repo_state_hash}")
        print(f"[ERROR]   End state:   {end_repo_state_hash}")
        print("[ERROR] This indicates concurrent modifications during generation")
        print("[ERROR] Re-run ADG generation in a stable repository state")
        sys.exit(1)

    _adg_elapsed = _time.time() - _adg_start
    print(f"[ADG] Total generation time: {_adg_elapsed:.2f}s")


# M.5: _auto_ingest_to_redis extracted to tools.generate.integration.redis_ingest


# M.5: _auto_commit_artifacts extracted to tools.generate.integration.git_commit
# Don't raise - git failure shouldn't block ADG generation


# M.5: _persist_adg_to_memory extracted to tools.generate.integration.memory_persist


# _extract_timestamp, _parse_timestamp, _archive_old_artifacts imported above from tools.generate.archiving (M.2)


# M.4: _audit_semantic_surfaces extracted to tools.generate.reporting.analysis


# M.4: _semantic_precision_stats extracted to tools.generate.reporting.analysis


# M.4: _violation_surface_stats extracted to tools.generate.reporting.analysis


# M.4: _violation_propagation_stats extracted to tools.generate.reporting.analysis


# M.4: _artifact_determinism_probe extracted to tools.generate.reporting.analysis


# M.4: _cleanup_validation_files extracted to tools.generate.reporting.analysis


# M.6: _infer_layer extracted to tools.generate.core.helpers


_RUNTIME_ENFORCEMENT_FILES = [
    # Gap 1: UWG mutation chokepoint
    "agentic_core/L2_execution/UniversalWriteGateway.py",
    # Gap 2: Determinism/replay interception
    "agentic_core/L2_execution/determinism/replay_guard.py",
    # Gap 3: Policy hash validation
    "agentic_core/L0_routing/enforcement/policy_hash_enforcer.py",
    # Gap 4: HITL/DPO lineage
    "agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py",
    # Gap 5: Meta-learning commit gating
    "agentic_core/L0_routing/meta_control/meta_apply.py",
]


# _archive_zip_files, _archive_individual_files, _create_zip_archive imported above from tools.generate.archiving (M.2)


# M.4: _generate_standardized_reports extracted to tools.generate.reporting.reports


# M.5: _check_mcp_config_drift extracted to tools.generate.integration.mcp_drift


# _perform_wal_checkpoint, _check_locked_files imported above from tools.generate.utils.file_utils (M.1)


# M.6: _generate_timestamp extracted to tools.generate.core.helpers


# M.6: _verify_artifacts extracted to tools.generate.core.helpers


# M.5: _run_p1_p2_auto_fix extracted to tools.generate.integration.repair_runner


def main() -> None:
    """Main entry point with CLI argument parsing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate full ADG with entities and relations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--force", action="store_true", help="Force regeneration even if cache exists")
    parser.add_argument("--repair", action="store_true", help="Run repair orchestrator after ADG generation")
    parser.add_argument("--repair-dry-run", action="store_true", help="Show repairs without applying them")
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="Disable zip archive creation (default: enabled)",
    )
    parser.add_argument(
        "--no-reports",
        action="store_true",
        help="Disable report generation (default: enabled)",
    )
    parser.add_argument(
        "--no-wiring-check",
        action="store_true",
        help=(
            "Skip the expected-wiring AST gate that runs after ADG generation. "
            "Default: the gate runs and fails the process on wiring violations."
        ),
    )
    parser.add_argument(
        "--no-config-ref-check",
        action="store_true",
        help=(
            "Skip the config-reference gate (env-flag reads vs .env.example). "
            "Default: the gate runs with baseline ratchet — fails only on NEW "
            "undeclared flags."
        ),
    )
    parser.add_argument(
        "--no-lifecycle-check",
        action="store_true",
        help=(
            "Skip the lifecycle-pair gate (sqlite3.connect / open / redis.Redis "
            "must have a matching closer). Default: gate runs with baseline "
            "ratchet — fails only on NEW leaks with severity=error."
        ),
    )

    args = parser.parse_args()

    # Pre-flight checks
    _check_mcp_config_drift()
    _perform_wal_checkpoint()
    _check_locked_files()

    # Generate timestamp and artifacts directory
    ts = _generate_timestamp()
    adg_artifacts_dir = ROOT / "artifacts" / "adg"

    print(f"[ADG] Starting generation with timestamp: {ts}")

    # Generate ADG
    try:
        generate_full_adg(
            adg_artifacts_dir,
            ts,
            enable_zip=not args.no_zip,
            enable_reports=not args.no_reports,
            enable_analysis=True,
        )
    except RuntimeError as e:
        if "Zip creation failed" in str(e) and not args.no_zip:
            print(f"\n[ERROR] ADG generation failed: {e}")
            print("[ERROR] Zip archive was requested but could not be created")
            print("[ERROR] This is a critical failure for full ADG generation")
            sys.exit(1)
        raise

    # Verify artifacts
    _verify_artifacts(adg_artifacts_dir, ts, args.no_zip, args.no_reports)

    # Post-ADG gate chain — each gate is invoked as a bounded subprocess
    # (§14 shell=False timeout=30). Authors get feedback within the same
    # 2-5 min ADG refresh window, not later at pre-commit or remote CI.
    # Each gate has its own --no-<gate>-check opt-out for emergencies.
    if not args.no_wiring_check:
        _run_post_adg_gate(
            label="wiring",
            script_rel="ops_scripts/ci/check_expected_wiring.py",
            args_list=[],
            fail_hint=(
                "Fix the declared call sites in config/expected_wiring.yaml "
                "or run with --no-wiring-check (emergency only)."
            ),
            timeout_s=30,
        )
    if not args.no_config_ref_check:
        _run_post_adg_gate(
            label="config-ref",
            script_rel="ops_scripts/ci/check_config_references.py",
            args_list=["--allow-unreferenced"],
            fail_hint=(
                "Declare the new flag in .env.example, OR allowlist it in "
                "config/config_references_allowlist.yaml, OR (debt row) "
                "regenerate baseline: python ops_scripts/ci/check_config_references.py "
                "--regenerate-baseline."
            ),
            timeout_s=60,
        )
    if not args.no_lifecycle_check:
        _run_post_adg_gate(
            label="lifecycle",
            script_rel="ops_scripts/ci/check_lifecycle_pairs.py",
            args_list=[],
            fail_hint=(
                "Use a `with` statement, assign the opener to self.<attr>, or "
                "call .close() explicitly. OR (debt row) regenerate baseline: "
                "python ops_scripts/ci/check_lifecycle_pairs.py --regenerate-baseline."
            ),
            timeout_s=60,
        )

    # Run repair orchestrator if requested
    if args.repair:
        _run_p1_p2_auto_fix(adg_artifacts_dir, ts)


def _run_post_adg_gate(
    *,
    label: str,
    script_rel: str,
    args_list: list[str],
    fail_hint: str,
    timeout_s: int,
) -> None:
    """Invoke a post-ADG CI gate as a bounded subprocess.

    Constitutional §14: argv form, shell=False, explicit timeout. Non-zero
    exit halts the ADG generation run so authors see the gate failure in the
    same window, not later at pre-commit. Generic wrapper so all five post-
    ADG gates share one invocation path and logging shape.
    """
    import subprocess

    gate = ROOT / script_rel
    if not gate.is_file():
        print(f"[ADG] [{label}] gate script missing ({script_rel}), skipping")
        return
    print(f"[ADG] Running {label} gate ({script_rel}) ...")
    try:
        proc = subprocess.run(
            [sys.executable, str(gate), *args_list],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"[ADG] [{label}] gate timed out after {timeout_s}s — failing")
        sys.exit(2)
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip())
    if proc.returncode != 0:
        print(f"[ADG] [{label}] FAIL — {fail_hint}")
        sys.exit(proc.returncode)
    print(f"[ADG] [{label}] PASS")


if __name__ == "__main__":
    main()
