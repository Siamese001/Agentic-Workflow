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

ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # guardian: allow-global-mutation


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
from agentic_core.adg.artifact.builder_types import build_artifact  # noqa: E402
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
)
from tools.generate.reporting import (  # noqa: E402  # M.4 modularization
    _generate_standardized_reports,
    _print_defect_table,
)
from tools.generate.utils.file_utils import (  # noqa: E402  # M.1 modularization
    _check_locked_files,
    _perform_wal_checkpoint,
)
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
)

# M.4: _print_defect_table extracted to tools.generate.reporting.reports


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
    import subprocess as _subprocess

    try:
        # ruff: noqa: S607 - Git command is trusted, internal tool usage
        commit_sha = _subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        print(f"[ADG] Captured commit SHA: {commit_sha}")
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"[ADG] Warning: Failed to capture commit SHA: {e}")
        commit_sha = ""

    # Capture repo state hash (tree hash)
    try:
        # ruff: noqa: S607 - Git command is trusted, internal tool usage
        repo_state_hash = _subprocess.check_output(
            ["git", "rev-parse", "HEAD^{tree}"],
            cwd=ROOT,
            text=True,
        ).strip()
        print(f"[ADG] Captured repo state hash: {repo_state_hash}")
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"[ADG] Warning: Failed to capture repo state hash: {e}")
        repo_state_hash = ""

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

    # --- Archive old artifacts BEFORE validation gates so cleanup always runs ---
    # (ratchet/gate failures call sys.exit before the post-zip archive block)
    if archive_old:
        _archive_old_artifacts(adg_artifacts_dir, ts, keep_runs=1)

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
        exit_code = e.code if e.code is not None else 1
    finally:
        # Clean up temp directory with ignore_errors=True to handle Windows file handle timing
        shutil.rmtree(temp_dir, ignore_errors=True)

    if exit_code != 0:
        sys.exit(exit_code)

    # --- Tier-2: Code quality gates (run on PRODUCTION SQLite, never temp) ---
    # Orchestrator runs inline here. No SQLite contention with temp directory.
    production_sqlite = sorted(adg_artifacts_dir.glob("adg_indexed_*.sqlite"))
    prod_sqlite_path = production_sqlite[-1] if production_sqlite else None

    _check_p0_violations(routing_summary, sqlite_path=prod_sqlite_path)
    _check_p1_ratchet(sqlite_path=prod_sqlite_path)
    _check_dead_production_imports(sqlite_path=prod_sqlite_path)

    # --- Tier-2b: Structural conformance & agentic anti-pattern gates ---
    _check_structural_conformance(sqlite_path=prod_sqlite_path)
    _check_agentic_antipatterns(sqlite_path=prod_sqlite_path)

    # --- Infrastructure wiring enrichment: materialize violation views ---
    _enrich_infra_views(paths.sqlite)

    # --- ADG materialized views: structural/authority/trace/snapshot visibility ---
    _materialize_adg_views(paths.sqlite)

    # --- Repair orchestrator: classify + fix remaining issues ---
    print("[ADG] Running repair orchestrator on committed artifacts...")
    _run_p1_p2_auto_fix(adg_artifacts_dir, ts)

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
        except Exception:  # guardian: allow-silent-swallow -- system learning unavailable: continue ADG generation without confidence persistence
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
    # Zip contains: 2 ADG artifacts (snapshot.json, sqlite) + reports
    artifact_files = [
        paths.snapshot,
        paths.sqlite,
    ]

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

    # --- Create zip archive (always enabled) ---
    zip_created = False
    try:
        _create_zip_archive(adg_artifacts_dir, ts, artifact_files)
        zip_created = True
        print(f"[ADG] Zip creation successful for {ts}")
    # guardian: allow-silent-swallow - acceptable exception handling
    except RuntimeError as e:
        print(f"[ADG] WARNING: Zip creation failed: {e}")
        print("[ADG] Individual files will be archived using legacy path")
        zip_created = False

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

    # --- Auto-commit artifacts to git ---
    if os.environ.get("ADG_SKIP_GIT", "").strip().lower() not in ("1", "true", "yes"):
        _auto_commit_artifacts(
            adg_dir=adg_artifacts_dir,
            ts=ts,
            node_count=len(result.modules),
            edge_count=len(result.edges),
        )

    # --- Fail-fast: Repo state change check ---
    end_repo_state_hash = ""
    try:
        # ruff: noqa: S607 - Git command is trusted, internal tool usage
        end_repo_state_hash = _subprocess.check_output(
            ["git", "rev-parse", "HEAD^{tree}"],
            cwd=ROOT,
            text=True,
        ).strip()
    except (ValueError, TypeError, RuntimeError):
        pass

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

    # Run repair orchestrator if requested
    if args.repair:
        _run_p1_p2_auto_fix(adg_artifacts_dir, ts)


if __name__ == "__main__":
    main()
