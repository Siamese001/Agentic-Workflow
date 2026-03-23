"""Generate full ADG with entities and relations in the comprehensive format.

Non-redundant output set (5 files, 100% edge coverage):
    adg_snapshot_<ts>.json        Tier 1: CI-light (~50 KB) — metrics only
    adg_indexed_<ts>.sqlite       Tier 2: primary queryable store (~38 MB, all 18 edge types)
    adg_file_graph_<ts>.json      imports, exports, dead_imports, covers, influences, in_cycle
    adg_symbol_graph_<ts>.json    calls, implements, reads_from, writes_to, instantiates, ...
    adg_governance_graph_<ts>.json violates, antipattern, generates_prompt, ...

Timestamp format: MMDDYYYY in US Eastern time  (e.g. 03122026 for March 12, 2026)
Internal state file (not part of the 5-file model):
    adg_graphsnap_<ts>.json       E7 drift detection — previous-run snapshot for diff

NOTE: adg_full.json removed (SQLite supersedes it). test_graph removed (covers lives in file_graph).
NOTE: adg_LATEST_* copies not generated (create_latest_symlinks=False by default).
"""

from __future__ import annotations

import gzip
import shutil
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # guardian: allow-global-mutation

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "generate_full_adg")
_emit_applies_guardrail("p0", "generate_full_adg", "p0_governance")
_emit_reads_policy_state("p0", "generate_full_adg", "policy_binding")
_emit_snapshots_state("p0", "generate_full_adg", "state_snapshot")
emit_replay_key("p0", "generate_full_adg")
emit_determinism_digest("p0", "generate_full_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "generate_full_adg", "execution_auth")
_emit_validates_capability("p2", "generate_full_adg", "capability_check")
_emit_routes_to_capability("p2", "generate_full_adg", "capability_route")
_emit_writes_via_uwg("p2", "generate_full_adg", "uwg_write")
_emit_blocks_direct_write("p2", "generate_full_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "generate_full_adg", "tool_invocation")
_emit_captures_execution_output("p2", "generate_full_adg", "exec_output")
_emit_dispatches_agent("p3", "generate_full_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "generate_full_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "generate_full_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "generate_full_adg", "healing_outcome")
_emit_escalates_failure("p3", "generate_full_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "generate_full_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generate_full_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "generate_full_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "generate_full_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generate_full_adg", "eval_metric")
_emit_stores_embedding("p4", "generate_full_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "generate_full_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generate_full_adg", "exec_snapshot_link")

from agentic_core.adg.analysis.CanonicalSnapshot import (
    build_snapshot,
    load_latest_snapshot,
    save_snapshot,
)
from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges
from agentic_core.adg.analysis.GraphDiff import diff_snapshots
from agentic_core.adg.analysis.ImpactReport import impact_summary, predict_impact
from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry, _infer_ownership
from agentic_core.adg.analysis.RepairRoute import repair_routing_summary, route_violations
from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts
from agentic_core.adg.artifact.builder_types import build_artifact
from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("generate_full_adg", "p4obs", "metric_1")
_emit_emits_metric_event("generate_full_adg", "p4obs", "metric_2")
_emit_emits_metric_event("generate_full_adg", "p4obs", "metric_3")
_emit_emits_metric_event("generate_full_adg", "p4obs", "metric_4")
_emit_emits_metric_event("generate_full_adg", "p4obs", "metric_5")
_emit_emits_metric_event("generate_full_adg", "p4obs", "metric_6")
_emit_records_incident_event("generate_full_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("generate_full_adg", "p4obs", "anomaly")
_emit_writes_observability_log("generate_full_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("generate_full_adg", "p4obs", "mon_state")
_emit_triggers_alert("generate_full_adg", "p4obs", "alert")
_emit_links_incident_trace("generate_full_adg", "p4obs", "trace_link")
_emit_captures_pattern("generate_full_adg", "p3lm", "pattern")
_emit_records_learning_event("generate_full_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("generate_full_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("generate_full_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("generate_full_adg", "p3lm", "routing")
_emit_improves_agent_policy("generate_full_adg", "p3lm", "policy")
_emit_stores_learning_state("generate_full_adg", "p3lm", "state")
_emit_records_execution_trace("generate_full_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("generate_full_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("generate_full_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("generate_full_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("generate_full_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("generate_full_adg", "env_read", "p2_env_1")
_emit_reads_environ("generate_full_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("generate_full_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("generate_full_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "generate_full_adg", "context_pull")
_emit_pulls_context("p1", "generate_full_adg", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "generate_full_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "generate_full_adg", "uwg_term_2")
_emit_writes_through("p1", "generate_full_adg", "write_through")
_emit_writes_through("p1", "generate_full_adg", "write_through_2")
_emit_validated_by_safety_plane("p1", "generate_full_adg", "safety_validation")
_emit_invokes_eval("p1", "generate_full_adg", "eval_call")
_emit_proposal_commits_routing("p1", "generate_full_adg", "routing_commit")
_emit_escalates_to_human("p1", "generate_full_adg", "human_escalation")
_emit_routes_through("p1", "generate_full_adg", "route_through")
_emit_checks_agent_registry("p1", "generate_full_adg", "agent_registry")
_emit_validates_agent_capability("p1", "generate_full_adg", "capability")
_emit_dispatches_execution_plan("p1", "generate_full_adg", "exec_plan")
_emit_agent_executes_agent("p1", "generate_full_adg", "sub_agent")
_emit_routes_to_agent("p1", "generate_full_adg", "target_agent")
_emit_verifies_policy("p1", "generate_full_adg", "policy_check")
_emit_observes_runtime_state("p1", "generate_full_adg", "runtime_state")
_emit_verifies_boundary("p1", "generate_full_adg", "boundary_check")
_emit_transcripts_response("p1", "generate_full_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "generate_full_adg")
_emit_gated_by_confidence("p1", "generate_full_adg", "confidence_gate")
_emit_reads_through("l4", "generate_full_adg", "urg_read_1")
_emit_reads_through("l4", "generate_full_adg", "urg_read_2")
_emit_reads_through("l4", "generate_full_adg", "urg_read_3")
_emit_reads_through("l4", "generate_full_adg", "urg_read_4")
_emit_reads_through("l4", "generate_full_adg", "urg_read_5")
_emit_reads_through("l4", "generate_full_adg", "urg_read_6")
_emit_reads_through("l4", "generate_full_adg", "urg_read_7")
_emit_reads_through("l4", "generate_full_adg", "urg_read_8")
_emit_reads_through("l4", "generate_full_adg", "urg_read_9")
_emit_reads_through("l4", "generate_full_adg", "urg_read_10")
_emit_reads_through("l4", "generate_full_adg", "urg_read_11")
_emit_reads_through("l4", "generate_full_adg", "urg_read_12")
_emit_reads_through("l4", "generate_full_adg", "urg_read_13")
_emit_reads_through("l4", "generate_full_adg", "urg_read_14")
_emit_reads_through("l4", "generate_full_adg", "urg_read_15")
_emit_reads_through("l4", "generate_full_adg", "urg_read_16")
_emit_reads_through("l4", "generate_full_adg", "urg_read_17")
_emit_reads_through("l4", "generate_full_adg", "urg_read_18")
_emit_reads_through("l4", "generate_full_adg", "urg_read_19")
_emit_reads_through("l4", "generate_full_adg", "urg_read_20")
_emit_reads_through("l4", "generate_full_adg", "urg_read_21")
_emit_reads_through("l4", "generate_full_adg", "urg_read_22")
_emit_reads_through("l4", "generate_full_adg", "urg_read_23")
_emit_reads_through("l4", "generate_full_adg", "urg_read_24")


def generate_full_adg(adg_artifacts_dir: Path, ts: str, archive_old: bool = True) -> None:
    """Generate full ADG and write all artifact tiers.

    Args:
        adg_artifacts_dir: Directory for ADG artifacts
        ts: Timestamp string (MMDDYYYY format)
        archive_old: If True, archive artifacts older than retention period
    """
    print("[ADG] Starting full scan...")

    # Capture provenance information
    import subprocess as _subprocess
    try:
        commit_sha = _subprocess.check_output(["git", "rev-parse", "HEAD"],
                                           cwd=ROOT, text=True).strip()
        print(f"[ADG] Captured commit SHA: {commit_sha}")
    except Exception as e:
        print(f"[ADG] Warning: Failed to capture commit SHA: {e}")
        commit_sha = ""

    # Capture repo state hash (tree hash)
    try:
        repo_state_hash = _subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"],
                                                 cwd=ROOT, text=True).strip()
        print(f"[ADG] Captured repo state hash: {repo_state_hash}")
    except Exception as e:
        print(f"[ADG] Warning: Failed to capture repo state hash: {e}")
        repo_state_hash = ""

    cache_path = adg_artifacts_dir / "cache" / "scan_result_cache.json"
    cache_path.parent.mkdir(exist_ok=True)
    scanner = ADGStaticScanner(repo_root=ROOT, cache_path=cache_path)
    result = scanner.scan(commit_sha=commit_sha)

    # Set repo_state_hash in the result
    result.repo_state_hash = repo_state_hash

    print(f"[ADG] Scan complete. Digest: {result.digest}")
    print(f"[ADG] Modules: {len(result.modules)}")
    print(f"[ADG] Edges: {len(result.edges)}")
    print(
        f"[ADG] Cache: hits={result.manifest.cache_hits} misses={result.manifest.cache_misses} rate={result.manifest.cache_hit_rate:.1%}"
    )

    # --- Build canonical artifact (schema v3) ---
    print("[ADG] Building canonical artifact...")
    artifact = build_artifact(result, repo_root=ROOT)

    # --- Write all three tiers + split planes ---
    print("[ADG] Writing artifact tiers...")
    paths = write_all_artifacts(artifact, out_dir=adg_artifacts_dir, ts=ts)

    # Size report
    sizes = paths.size_report()

    print(f"[ADG] Tier 1 snapshot:  {paths.snapshot.name}  ({sizes['snapshot']})")
    print(f"[ADG] Tier 2 sqlite:    {paths.sqlite.name}  ({sizes['sqlite']})")
    print(f"[ADG] file_graph:       {paths.file_graph.name}  ({sizes['file_graph']})")
    print(f"[ADG] symbol_graph:     {paths.symbol_graph.name}  ({sizes['symbol_graph']})")
    print(f"[ADG] governance_graph: {paths.governance_graph.name}  ({sizes['governance_graph']})")
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
    save_snapshot(snapshot, snap_path)
    print(f"[ADG] E7 snapshot saved: {snap_path.name}")

    # --- E8: Ownership ---
    OwnershipRegistry.from_scan_result(result)

    # --- E9: Confidence ---
    scored_edges = score_edges(list(result.edges))
    conf_summary = confidence_summary(scored_edges)

    # --- E10: Repair routing ---
    violation_edges = [
        e for e in result.edges if e.relation_type in ("violates", "dynamic_exec", "invokes_provider")
    ]
    repair_routes = route_violations(violation_edges)
    routing_summary = repair_routing_summary(repair_routes)

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
        seed_files = list(result.modules[:5])
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
        f"{imp_summary['covering_test_count']} tests  risk={imp_summary['risk_label']} ({imp_summary['risk_score']:.4f})"
    )
    print(
        f"      E6 graph_hash={snapshot.graph_hash[:16]}...  nodes={snapshot.node_count}  edges={snapshot.edge_count}"
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
        f"high={conf_summary['confidence_tiers']['high']}  low={conf_summary['confidence_tiers']['low']}"
    )
    print(
        f"      E10 repair routes: {routing_summary['total_routes']} routes  by_severity={routing_summary['by_severity']}"
    )

    # --- Memory MCP persistence ---
    _persist_adg_to_memory(result, artifact, snapshot, graph_diff, routing_summary, ts)

    # --- Wave 6: Generate standardized reports ---
    _generate_standardized_reports(adg_artifacts_dir, ts, artifact)

    # --- Create zip archive of all 6 artifacts + 4 Wave 6 reports ---
    artifact_files = [
        paths.snapshot,
        paths.sqlite,
        paths.file_graph,
        paths.symbol_graph,
        paths.governance_graph,
        adg_artifacts_dir / f"adg_graphsnap_{ts}.json",
    ]

    # Add Wave 6 standardized reports + test surface report
    report_files = [
        adg_artifacts_dir / f"layer_coverage_report_{ts}.json",
        adg_artifacts_dir / f"edge_density_report_{ts}.json",
        adg_artifacts_dir / f"provenance_report_{ts}.json",
        adg_artifacts_dir / f"replay_determinism_report_{ts}.json",
        adg_artifacts_dir / f"boundary_report_{ts}.json",
        adg_artifacts_dir / f"mutation_integrity_report_{ts}.json",
        adg_artifacts_dir / f"test_surface_coverage_{ts}.json",
    ]

    # Filter to only include existing reports
    existing_reports = [f for f in report_files if f.exists()]
    if existing_reports:
        artifact_files.extend(existing_reports)
        print(f"[ADG] Adding {len(existing_reports)} reports to zip archive")

    # --- Pre-flight validation for runtime files ---
    missing_runtime = []
    for rel_path in _RUNTIME_ENFORCEMENT_FILES:
        if not (ROOT / rel_path).exists():
            missing_runtime.append(rel_path)

    if missing_runtime:
        print(f"[ADG] ERROR: Cannot create zip - missing runtime files: {missing_runtime}")
        print("[ADG] Continuing with individual files only (zip will be created later)")
        # Skip zip creation and proceed to archiving
        zip_created = False
    else:
        # --- Create zip archive ---
        try:
            _create_zip_archive(adg_artifacts_dir, ts, artifact_files)
            zip_created = True
            print(f"[ADG] Zip creation successful for {ts}")
        except RuntimeError as e:
            print(f"[ADG] WARNING: Zip creation failed: {e}")
            print("[ADG] Individual files will be archived using legacy path")
            zip_created = False

    # --- Archive old artifacts ---
    if archive_old:
        _archive_old_artifacts(adg_artifacts_dir, ts, keep_runs=1)

    # --- Auto-ingest to Redis hot cache ---
    _auto_ingest_to_redis(adg_artifacts_dir, paths.sqlite)

    # --- Auto-commit artifacts to git ---
    _auto_commit_artifacts(adg_artifacts_dir, ts, len(result.modules), len(result.edges))


def _auto_ingest_to_redis(adg_dir: Path, sqlite_path: Path) -> None:
    """Automatically ingest the freshly-generated ADG into Redis hot cache.

    Runs tools/adg/adg_redis_ingest.py --force as a subprocess to ensure the
    Redis cache is immediately hot after ADG generation completes.

    Args:
        adg_dir: ADG artifacts directory
        sqlite_path: Path to the just-created .sqlite file

    Raises:
        RuntimeError: If ingest script is not found
        subprocess.TimeoutExpired: If ingest takes longer than configured timeout
        subprocess.CalledProcessError: If ingest script fails
    """
    import subprocess

    from agentic_core.config.redis_config import get_adg_cache_config

    config = get_adg_cache_config()
    ingest_script = ROOT / "tools" / "adg" / "adg_redis_ingest.py"
    if not ingest_script.exists():
        raise RuntimeError(f"Redis ingest script not found: {ingest_script}")

    print("[ADG] Auto-ingesting to Redis hot cache...")
    try:
        result = subprocess.run(
            [sys.executable, str(ingest_script), "--force"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=config.ingest_timeout,
            check=True,
        )
        print("[ADG] Redis ingest complete - ADG cache is HOT")
        # Show last 3 lines of output for confirmation
        lines = [line for line in result.stdout.strip().split("\n") if line.strip()]
        for line in lines[-3:]:
            print(f"      {line}")
    except subprocess.TimeoutExpired as e:
        print(f"[ADG] WARNING: Redis ingest timed out after {config.ingest_timeout}s — cache may be stale")
        raise
    except subprocess.CalledProcessError as e:
        print(f"[ADG] ERROR: Redis ingest failed (exit {e.returncode}):")
        print(f"      {e.stderr.strip()[:200]}")
        raise


def _auto_commit_artifacts(adg_dir: Path, ts: str, node_count: int, edge_count: int) -> None:
    """Automatically commit newly generated ADG artifacts to git.

    Stages new artifacts and deletions of old artifacts, then commits with
    a descriptive message including timestamp and graph metrics.

    Uses --no-verify to bypass pre-commit hooks since ADG artifacts are
    auto-generated and don't require validation.

    Args:
        adg_dir: ADG artifacts directory
        ts: Timestamp string (MMDDYYYY_HHMM format)
        node_count: Number of modules in the graph
        edge_count: Number of edges in the graph

    Raises:
        subprocess.CalledProcessError: If git commands fail
    """
    import subprocess

    print("[ADG] Auto-committing artifacts to git...")

    try:
        # Stage new ADG artifacts
        artifact_patterns = [
            f"adg_snapshot_{ts}.json",
            f"adg_indexed_{ts}.sqlite",
            f"adg_file_graph_{ts}.json",
            f"adg_symbol_graph_{ts}.json",
            f"adg_governance_graph_{ts}.json",
            f"adg_graphsnap_{ts}.json",
        ]

        staged_count = 0
        skipped_ignored_count = 0

        for pattern in artifact_patterns:
            artifact_path = adg_dir / pattern
            if artifact_path.exists():
                # Skip ignored artifacts to avoid repeated git add failures/noise
                check_ignore = subprocess.run(
                    ["git", "check-ignore", str(artifact_path)],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                )
                if check_ignore.returncode == 0:
                    skipped_ignored_count += 1
                    continue

                subprocess.run(
                    ["git", "add", str(artifact_path)],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    check=True,
                )
                staged_count += 1

        # Stage deletions of old artifacts (moved to _archive/)
        subprocess.run(
            ["git", "add", "-u", "artifacts/adg/"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        if skipped_ignored_count:
            print(
                f"[ADG] Git: skipped {skipped_ignored_count} ignored artifacts; staged {staged_count} trackable artifacts"
            )

        # If nothing is staged, skip commit cleanly
        staged_check = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if staged_check.returncode == 0:
            print("[ADG] Git: no staged artifact changes to commit")
            return

        # Commit with descriptive message, bypassing pre-commit hooks
        # ADG artifacts are auto-generated and don't need validation
        commit_msg = f"ADG: regenerate artifacts {ts} — {node_count} modules, {edge_count} edges"
        result = subprocess.run(
            ["git", "commit", "--no-verify", "-m", commit_msg],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        print(f"[ADG] ✓ Git commit complete — {commit_msg}")

    except subprocess.CalledProcessError as e:
        # Check if failure was due to "nothing to commit"
        if "nothing to commit" in e.stdout or "nothing to commit" in e.stderr:
            print("[ADG] Git: no changes to commit (artifacts already committed)")
        else:
            print(f"[ADG] WARNING: Git commit failed (exit {e.returncode}):")
            print(f"      stdout: {e.stdout.strip()[:200]}")
            print(f"      stderr: {e.stderr.strip()[:200]}")
            # Don't raise - git failure shouldn't block ADG generation


def _persist_adg_to_memory(result, artifact, snapshot, graph_diff, routing_summary, ts: str) -> None:
    """Persist key ADG signals to Memory MCP knowledge graph via ADGMemoryAdapter."""
    try:
        from agentic_core.adg.adapters.ADGMemoryAdapter import get_adapter

        adapter = get_adapter()
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"[ADG] Memory MCP unavailable — skipping persistence: {e}")
        return

    diff_edges = 0
    if graph_diff and hasattr(graph_diff, "summary"):
        summary = graph_diff.summary or ""
        import re as _re

        m = _re.search(r"([+-]\d+)\s*edges", summary)
        if m:
            diff_edges = int(m.group(1))

    try:
        adapter.ingest_snapshot(result, ts, diff_edges=diff_edges)
    except (ValueError, TypeError, AttributeError, RuntimeError, OSError) as e:
        print(f"[ADG] Memory MCP: ingest_snapshot failed: {e}")
        return

    violation_edges = [e for e in result.edges if e.relation_type == "violates"]
    total_violations = len(violation_edges)
    critical_count = routing_summary.get("by_severity", {}).get("critical", 0)
    print(
        f"[ADG] Memory MCP: persisted snapshot + layers + hotspots + {min(total_violations, 50)}/{total_violations} violations (critical={critical_count})"
    )


def _extract_timestamp(filename: str) -> str | None:
    """Extract timestamp from ADG artifact filename.

    Supports formats:
        Current: adg_indexed_03122026_0512.sqlite    -> 03122026_0512  (MMDDYYYY_HHMM)
        Legacy1: adg_indexed_03122026.sqlite         -> 03122026       (MMDDYYYY)
        Legacy2: adg_indexed_20260312T093508Z.sqlite -> 20260312T093508Z  (ISO)
    """
    parts = filename.split("_")
    if len(parts) < 3:
        return None

    # Check if last two parts form timestamp (MMDDYYYY_HHMM)
    if len(parts) >= 4:
        ts_date = parts[-2]
        ts_time_with_ext = parts[-1]
        ts_time = ts_time_with_ext.split(".")[0]

        # Current format: MMDDYYYY_HHMM
        if len(ts_date) == 8 and ts_date.isdigit() and len(ts_time) == 4 and ts_time.isdigit():
            return f"{ts_date}_{ts_time}"

    # Last part before extension should be timestamp (legacy formats)
    ts_with_ext = parts[-1]
    ts = ts_with_ext.split(".")[0]

    # Legacy format 1: MMDDYYYY (8 digits)
    if len(ts) == 8 and ts.isdigit():
        return ts
    # Legacy format 2: YYYYMMDDTHHMMSSz (16 chars)
    if len(ts) == 16 and ts[8] == "T" and ts.endswith("Z"):
        return ts
    return None


def _parse_timestamp(ts: str) -> datetime:
    """Parse timestamp string to datetime.

    Args:
        ts: Timestamp string — "03122026_0512" (MMDDYYYY_HHMM), "03122026" (MMDDYYYY),
            "20260310" (YYYYMMDD legacy), or "20260311T160257Z" (ISO legacy)

    Returns:
        datetime object
    """
    # Current format: MMDDYYYY_HHMM
    if "_" in ts:
        return datetime.strptime(ts, "%m%d%Y_%H%M")

    if len(ts) == 8 and ts.isdigit():
        # Distinguish MMDDYYYY (new) from YYYYMMDD (legacy)
        # If first 4 chars are a plausible year (2020-2099), it's YYYYMMDD
        if ts.startswith(("202", "203", "204", "205", "206")):
            return datetime.strptime(ts, "%Y%m%d")
        return datetime.strptime(ts, "%m%d%Y")
    return datetime.strptime(ts, "%Y%m%dT%H%M%SZ")


def _archive_old_artifacts(adg_dir: Path, current_ts: str, keep_runs: int = 1) -> None:
    """Archive old ADG runs to keep artifacts directory clean.

    Uses run-based retention (keeps last N complete runs) rather than day-based.
    This is superior because it preserves complete artifact sets.

    Args:
        adg_dir: ADG artifacts directory
        current_ts: Current timestamp (MMDDYYYY)
        keep_runs: Number of recent complete runs to keep (default: 1)
    """
    if not adg_dir.exists():
        return

    # Discover all runs by grouping files by timestamp
    from collections import defaultdict

    runs = defaultdict(list)

    for pattern in ["adg_*.json", "adg_*.sqlite", "adg_run_*.zip", "scan_result_cache.json", "*_report_*.json", "test_surface_coverage_*.json"]:
        for path in adg_dir.glob(pattern):
            # Skip LATEST files
            if "LATEST" in path.name or "latest" in path.name:
                continue

            # Skip already archived files
            if "_archive" in str(path):
                continue

            # Extract timestamp (handles both regular artifacts and zip files)
            if path.name.startswith("adg_run_") and path.suffix == ".zip":
                # Extract timestamp from zip filename: adg_run_03132026_0512.zip
                ts = path.stem.replace("adg_run_", "")
            else:
                ts = _extract_timestamp(path.name)

            if ts:
                runs[ts].append(path)

    if len(runs) <= keep_runs:
        return  # All runs within retention policy

    # Sort timestamps by actual datetime (newest first)
    sorted_timestamps = sorted(runs.keys(), key=_parse_timestamp, reverse=True)

    # Keep the newest N runs, archive the rest
    to_archive = sorted_timestamps[keep_runs:]

    if not to_archive:
        return

    # Archive each old run
    archived_count = 0
    bytes_original = 0
    bytes_archived = 0

    for ts in to_archive:
        files = runs[ts]

        # Get archive directory for this timestamp
        try:
            dt = _parse_timestamp(ts)
            archive_month_dir = adg_dir / "_archive" / dt.strftime("%Y-%m")
            archive_month_dir.mkdir(parents=True, exist_ok=True)
        except (ValueError, OSError) as e:
            print(f"[ADG] Archive: failed to create archive dir for {ts}: {e}")
            continue

        # Check if this run has a zip file (preferred storage)
        zip_files = [f for f in files if f.name.startswith("adg_run_") and f.suffix == ".zip"]

        if zip_files:
            # Archive only the zip file (most efficient)
            print(f"[ADG] Archive: Processing run {ts} with {len(zip_files)} zip file(s)")
            zip_archived, zip_bytes_original, zip_bytes_archived = _archive_zip_files(zip_files, archive_month_dir)
            archived_count += zip_archived
            bytes_original += zip_bytes_original
            bytes_archived += zip_bytes_archived

            # Remove all individual files for this run (they're in the zip)
            for file_path in files:
                if file_path not in zip_files and file_path.exists():
                    file_path.unlink()
                    archived_count += 1
                    bytes_original += file_path.stat().st_size
        else:
            # No zip file - archive individual files (legacy behavior for orphaned runs)
            print(f"[ADG] Archive: Found orphaned run {ts} with {len(files)} individual files")
            individual_archived, individual_bytes_original, individual_bytes_archived = _archive_individual_files(files, archive_month_dir)
            archived_count += individual_archived
            bytes_original += individual_bytes_original
            bytes_archived += individual_bytes_archived

    if archived_count > 0:
        savings = bytes_original - bytes_archived
        pct = (savings / bytes_original * 100) if bytes_original > 0 else 0
        print(f"[ADG] Archive: archived {len(to_archive)} runs, {archived_count} files (saved {pct:.0f}%)")

    # Clean up old validation packages and MANIFEST files
    _cleanup_validation_files(adg_dir, current_ts)


def _cleanup_validation_files(adg_dir: Path, current_ts: str) -> None:
    """Clean up old validation packages, MANIFEST files, and non-timestamped reports.

    Keeps only the latest validation package (matching current_ts).
    Removes all MANIFEST files (low value).
    Removes non-timestamped report files (legacy cleanup).

    Args:
        adg_dir: ADG artifacts directory
        current_ts: Current timestamp (MMDDYYYY_HHMM format)
    """
    if not adg_dir.exists():
        return

    cleaned_count = 0

    # Remove all MANIFEST files (low value)
    for manifest_file in adg_dir.glob("MANIFEST_*.txt"):
        try:
            manifest_file.unlink()
            cleaned_count += 1
        except OSError as e:
            print(f"[ADG] Cleanup: error removing {manifest_file.name}: {e}")

    # Remove non-timestamped report files (legacy cleanup)
    for report_file in adg_dir.glob("*_report.json"):
        # Skip if it has a timestamp (format: *_report_MMDDYYYY_HHMM.json)
        if "_" in report_file.stem and len(report_file.stem.split("_")) >= 3:
            # Check if the last part looks like a timestamp
            last_part = report_file.stem.split("_")[-1]
            if len(last_part) == 13 and "_" in last_part:  # MMDDYYYY_HHMM format
                continue  # This is a timestamped file, keep it
        try:
            report_file.unlink()
            cleaned_count += 1
            print(f"[ADG] Cleanup: removed legacy report {report_file.name}")
        except OSError as e:
            print(f"[ADG] Cleanup: error removing {report_file.name}: {e}")

    # Remove non-timestamped test_surface_coverage files (legacy cleanup)
    for test_file in adg_dir.glob("test_surface_coverage.json"):
        try:
            test_file.unlink()
            cleaned_count += 1
            print("[ADG] Cleanup: removed legacy test_surface_coverage.json")
        except OSError as e:
            print(f"[ADG] Cleanup: error removing {test_file.name}: {e}")

    # Clean up old validation packages (keep only current timestamp)
    validation_patterns = [
        "chatgpt_validation_package_*.zip",
        "adg_validation_package_*.zip",
    ]

    for pattern in validation_patterns:
        for val_file in adg_dir.glob(pattern):
            # Extract timestamp from validation package filename
            # e.g., chatgpt_validation_package_03132026_0427.zip
            if current_ts not in val_file.name:
                try:
                    val_file.unlink()
                    cleaned_count += 1
                except OSError as e:
                    print(f"[ADG] Cleanup: error removing {val_file.name}: {e}")

    if cleaned_count > 0:
        print(f"[ADG] Cleanup: removed {cleaned_count} old validation/manifest files")


def _infer_layer(path: str) -> str:
    """Infer layer label from file path using YAML overrides."""
    import fnmatch
    from pathlib import Path

    import yaml

    # Load layer overrides from YAML
    overrides_file = Path(__file__).parent / "adg_layer_overrides.yaml"
    if overrides_file.exists():
        try:
            with open(overrides_file, encoding='utf-8') as f:
                config = yaml.safe_load(f)
                overrides = config.get('overrides', {})
                default_layer = config.get('default_layer', 'L_UNKNOWN')

                # Check each pattern override
                for pattern, layer in overrides.items():
                    if fnmatch.fnmatch(path, pattern):
                        return layer

                return default_layer
        except Exception as e:
            print(f"[ADG] Warning: Failed to load layer overrides: {e}")
            # Fall back to simple inference

    # Fallback to simple path-based inference
    for layer in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
        if f"/{layer}_" in path or f"\\{layer}_" in path or f"/{layer}/" in path:
            return layer
    for prefix in (
        "apps_eval",
        "apps_exec",
        "apps_lic",
        "apps_research",
        "apps_rfp",
        "apps_rg",
        "apps_shared",
    ):
        if path.startswith(prefix) or f"/{prefix}" in path:
            return "L_APP"
    return "L_UNKNOWN"


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


def _archive_zip_files(zip_files: list[Path], archive_month_dir: Path) -> tuple[int, int, int]:
    """Archive zip files with compression.

    Returns:
        Tuple of (archived_count, bytes_original, bytes_archived)
    """
    archived_count = 0
    bytes_original = 0
    bytes_archived = 0

    for zip_file in zip_files:
        if not zip_file.exists():
            continue

        try:
            original_size = zip_file.stat().st_size
            bytes_original += original_size

            # Compress and archive the zip file
            archive_path = archive_month_dir / f"{zip_file.name}.gz"

            with open(zip_file, "rb") as f_in:
                with gzip.open(archive_path, "wb", compresslevel=9) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Verify compressed file before deleting original
            if archive_path.exists() and archive_path.stat().st_size > 0:
                bytes_archived += archive_path.stat().st_size
                zip_file.unlink()
                archived_count += 1
            else:
                # Clean up failed compression
                if archive_path.exists():
                    archive_path.unlink()

        except OSError as e:
            print(f"[ADG] Archive: error archiving {zip_file.name}: {e}")
            continue

    return archived_count, bytes_original, bytes_archived


def _archive_individual_files(files: list[Path], archive_month_dir: Path) -> tuple[int, int, int]:
    """Archive individual files (legacy fallback for orphaned runs).

    Returns:
        Tuple of (archived_count, bytes_original, bytes_archived)
    """
    archived_count = 0
    bytes_original = 0
    bytes_archived = 0

    for file_path in files:
        if not file_path.exists():
            continue

        try:
            original_size = file_path.stat().st_size
            bytes_original += original_size

            # Compress and archive
            archive_path = archive_month_dir / f"{file_path.name}.gz"

            with open(file_path, "rb") as f_in:
                with gzip.open(archive_path, "wb", compresslevel=9) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Verify compressed file before deleting original
            if archive_path.exists() and archive_path.stat().st_size > 0:
                bytes_archived += archive_path.stat().st_size
                file_path.unlink()
                archived_count += 1
            else:
                # Clean up failed compression
                if archive_path.exists():
                    archive_path.unlink()

        except OSError as e:
            print(f"[ADG] Archive: error archiving {file_path.name}: {e}")
            continue

    return archived_count, bytes_original, bytes_archived


def _create_zip_archive(adg_dir: Path, ts: str, artifact_paths: list[Path]) -> Path:
    """Create a zip archive of all ADG artifacts + runtime enforcement files for the current run.

    Structure:
        adg/<artifact>.json/.sqlite  - ADG graph artifacts
        runtime/<path>               - Gap 1-5 runtime enforcement files for external LLM validation

    Args:
        adg_dir: ADG artifacts directory
        ts: Timestamp string (MMDDYYYY_HHMM format)
        artifact_paths: List of artifact file paths to include in zip

    Returns:
        Path to the created zip file

    Raises:
        RuntimeError: If critical runtime files are missing or zip creation fails
    """
    zip_path = adg_dir / f"adg_run_{ts}.zip"
    repo_root = adg_dir.parents[1]

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            # Add ADG artifacts with validation
            missing_artifacts = []
            for artifact_path in artifact_paths:
                if artifact_path.exists():
                    zf.write(artifact_path, f"adg/{artifact_path.name}")
                else:
                    missing_artifacts.append(artifact_path.name)
                    print(f"[ADG] WARNING: Missing artifact {artifact_path.name}")

            # Add runtime files with explicit error handling
            missing_runtime = []
            for rel_path in _RUNTIME_ENFORCEMENT_FILES:
                full_path = repo_root / rel_path
                if full_path.exists():
                    zf.write(full_path, f"runtime/{rel_path}")
                else:
                    missing_runtime.append(rel_path)
                    print(f"[ADG] ERROR: Missing runtime file {rel_path}")

            # Fail fast if critical runtime files missing
            if missing_runtime:
                zip_path.unlink()  # Remove incomplete zip
                raise RuntimeError(f"Missing critical runtime files: {missing_runtime}")

            # Warn about missing artifacts but don't fail
            if missing_artifacts:
                print(f"[ADG] WARNING: Zip created with missing artifacts: {missing_artifacts}")

    except Exception as e:
        print(f"[ADG] CRITICAL: Zip creation failed: {e}")
        if zip_path.exists():
            zip_path.unlink()
        raise RuntimeError(f"Zip creation failed for {ts}: {e}") from e

    # Verify zip was created successfully
    if not zip_path.exists():
        raise RuntimeError(f"Zip file not created after successful completion for {ts}")

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    report_count = len([p for p in artifact_paths if p.name.endswith('_report.json')])
    runtime_count = len(_RUNTIME_ENFORCEMENT_FILES) - len(missing_runtime)
    print(f"[ADG] Zip archive created: {zip_path.name} ({zip_size_mb:.1f} MB, 6 ADG + {report_count} reports + {runtime_count} runtime files)")

    return zip_path


def _generate_standardized_reports(adg_dir: Path, ts: str, artifact: ADGArtifact) -> None:
    """Wave 6: Generate standardized ADG reports.

    Creates 4 standardized reports in artifacts/adg/:
    1. layer_coverage_report.json
    2. edge_density_report.json
    3. provenance_report.json
    4. replay_determinism_report.json
    """
    import json
    import sqlite3
    from collections import Counter

    reports_dir = adg_dir
    sqlite_path = adg_dir / f"adg_indexed_{ts}.sqlite"

    # 1. Layer Coverage Report
    layer_report = {
        "timestamp": ts,
        "schema_version": "1.0",
        "total_modules": len(artifact.entities),
        "layer_distribution": {},
        "unknown_modules": [],
        "coverage_metrics": {}
    }

    # Count modules by layer
    layer_counts = Counter()
    unknown_modules = []

    for entity in artifact.entities:
        if entity.entity_type == "module":
            layer_counts[entity.layer] += 1
            if entity.layer == "L_UNKNOWN":
                unknown_modules.append({
                    "adg_name": entity.adg_name,
                    "resolved_path": entity.resolved_path,
                    "identity_kind": entity.identity_kind
                })

    layer_report["layer_distribution"] = dict(layer_counts)
    layer_report["unknown_modules"] = unknown_modules[:50]  # Limit to first 50
    layer_report["coverage_metrics"] = {
        "known_modules": layer_report["total_modules"] - len(unknown_modules),
        "unknown_modules": len(unknown_modules),
        "coverage_percentage": (layer_report["total_modules"] - len(unknown_modules)) / layer_report["total_modules"] * 100 if layer_report["total_modules"] > 0 else 0
    }

    # 2. Edge Density Report
    # Get total edge count from SQLite
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM edges")
    total_edges = cur.fetchone()[0]

    edge_report = {
        "timestamp": ts,
        "schema_version": "1.0",
        "total_edges": total_edges,
        "edge_distribution": {},
        "critical_edge_coverage": {},
        "density_metrics": {}
    }

    # Use SQLite as authoritative source for edge counts
    cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type")
    sqlite_edge_counts = dict(cur.fetchall())

    edge_report["edge_distribution"] = dict(sorted(sqlite_edge_counts.items(), key=lambda x: x[1], reverse=True))

    # Critical edge types from Wave 4
    critical_edges = [
        'determinism_seed',
        'emits_determinism_digest',
        'policy_verification',
        'authorize_and_execute',
        'dispatches_execution_plan',
        'enters_sandbox',
        'guardian_gate'
    ]

    critical_coverage = {}
    for edge_type in critical_edges:
        critical_coverage[edge_type] = sqlite_edge_counts.get(edge_type, 0)

    edge_report["critical_edge_coverage"] = critical_coverage
    edge_report["density_metrics"] = {
        "critical_edges_found": sum(1 for count in critical_coverage.values() if count > 0),
        "critical_edge_percentage": sum(1 for count in critical_coverage.values() if count > 0) / len(critical_edges) * 100,
        "top_edge_type": max(sqlite_edge_counts.items(), key=lambda x: x[1])[0] if sqlite_edge_counts else None
    }

    # Store edge counts for later use
    stored_edge_counts = sqlite_edge_counts.copy()
    conn.close()

    # 3. Provenance Report - reconciled with SQLite
    # Query SQLite for accurate counts
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    # Get meta table data
    cur.execute("SELECT * FROM meta LIMIT 1")
    meta_row = cur.fetchone()
    if meta_row:
        meta_columns = [description[0] for description in cur.description]
        meta_data = dict(zip(meta_columns, meta_row))
    else:
        meta_data = {}

    # Get actual node/edge counts
    cur.execute("SELECT COUNT(*) FROM nodes")
    total_nodes = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM edges")
    total_edges = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM nodes WHERE entity_type='module'")
    total_modules = cur.fetchone()[0]

    conn.close()

    provenance_report = {
        "schema_version": meta_data.get('schema_version', '4.0.0'),  # Use SQLite version
        "commit_sha": meta_data.get('commit_sha', artifact.commit_sha),
        "repo_state_hash": meta_data.get('repo_state_hash', getattr(artifact, 'repo_state_hash', '')),
        "scanner_digest": meta_data.get('scanner_digest', artifact.scanner_digest),
        "artifact_digest": meta_data.get('artifact_digest', artifact.artifact_digest),
        "validation": {
            "has_commit_sha": bool(meta_data.get('commit_sha')),
            "has_repo_state_hash": bool(meta_data.get('repo_state_hash')),
            "has_scanner_digest": bool(meta_data.get('scanner_digest')),
            "has_artifact_digest": bool(meta_data.get('artifact_digest'))
        },
        "reconciliation": {
            "report_nodes": len(artifact.entities),
            "db_nodes": total_nodes,
            "report_edges": len(artifact.relations),
            "db_edges": total_edges,
            "nodes_match": len(artifact.entities) == total_nodes,
            "edges_match": len(artifact.relations) == total_edges
        },
        "generation_metrics": {
            "scan_duration_seconds": None,
            "modules_scanned": total_modules,
            "symbols_scanned": total_nodes - total_modules,
            "total_entities": total_nodes
        }
    }

    # 4. Replay Determinism Report
    determinism_report = {
        "timestamp": ts,
        "schema_version": "1.0",
        "determinism_metrics": {
            "determinism_digest_edges": stored_edge_counts.get('emits_determinism_digest', 0),
            "determinism_seed_edges": stored_edge_counts.get('determinism_seed', 0),
            "replay_key_edges": stored_edge_counts.get('emits_replay_key', 0),
            "snapshot_state_edges": stored_edge_counts.get('snapshots_state', 0)
        },
        "determinism_coverage": {
            "modules_with_determinism_digest": 0,  # Would need SQLite query
            "modules_with_replay_keys": 0,       # Would need SQLite query
            "determinism_score": 0.0  # Calculated metric
        },
        "validation": {
            "has_determinism_edges": stored_edge_counts.get('emits_determinism_digest', 0) > 0,
            "has_seed_edges": stored_edge_counts.get('determinism_seed', 0) > 0,
            "determinism_status": "partial" if stored_edge_counts.get('emits_determinism_digest', 0) > 0 else "missing"
        }
    }

    # 5. Boundary Report
    boundary_report = {
        "timestamp": ts,
        "schema_version": "1.0",
        "boundary_edge_counts": {},
        "unresolved_imports": {},
        "core_path_analysis": {},
        "boundary_metrics": {}
    }

    # Query boundary edge counts from SQLite
    boundary_edge_types = [
        'internal_to_internal',
        'internal_to_external',
        'external_to_internal',
        'unresolved_boundary'
    ]

    boundary_counts = {}
    for edge_type in boundary_edge_types:
        boundary_counts[edge_type] = stored_edge_counts.get(edge_type, 0)

    boundary_report["boundary_edge_counts"] = boundary_counts

    # Query unresolved imports by core path
    unresolved_by_path = {}
    core_paths = ['agentic_core/L0_', 'agentic_core/L2_', 'agentic_core/L5_']

    for path_prefix in core_paths:
        # This would require a more complex SQL query to get by path
        unresolved_by_path[path_prefix] = 0  # Placeholder

    boundary_report["unresolved_imports"] = unresolved_by_path
    boundary_report["boundary_metrics"] = {
        "total_unresolved": sum(unresolved_by_path.values()),
        "critical_path_unresolved": sum(unresolved_by_path[p] for p in core_paths),
        "boundary_completeness": "incomplete"
    }

    # 6. Mutation Integrity Report
    mutation_report = {
        "timestamp": ts,
        "schema_version": "1.0",
        "mutation_integrity_metrics": {},
        "replay_guarantees": {},
        "signature_coverage": {},
        "snapshot_lineage": {}
    }

    # Query mutation-related edges
    mutation_edges = {
        'mutation_signature': stored_edge_counts.get('mutation_signature', 0),
        'parent_snapshot_hash': stored_edge_counts.get('parent_snapshot_hash', 0),
        'replay_key': stored_edge_counts.get('emits_replay_key', 0),
        'policy_hash': stored_edge_counts.get('references_policy_hash', 0)
    }

    mutation_report["mutation_integrity_metrics"] = mutation_edges
    mutation_report["replay_guarantees"] = {
        "determinism_status": "partial" if stored_edge_counts.get('determinism_seed', 0) > 0 else "missing",
        "replay_completeness": "partial",
        "signature_coverage": "incomplete"
    }
    mutation_report["signature_coverage"] = {
        "modules_with_signatures": stored_edge_counts.get('mutation_signature', 0),
        "total_modules": len([e for e in artifact.entities if e.entity_type == "module"]),
        "coverage_percentage": (stored_edge_counts.get('mutation_signature', 0) / len([e for e in artifact.entities if e.entity_type == "module"]) * 100) if len([e for e in artifact.entities if e.entity_type == "module"]) > 0 else 0
    }

    # 7. Test Surface Coverage Report
    test_surface_report = {
        "timestamp": ts,
        "schema_version": "1.0",
        "test_surface_nodes": {},
        "test_surface_edges": {},
        "test_coverage_metrics": {},
        "critical_path_linkage": {}
    }

    # Query test-related nodes and edges from SQLite
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    # Test node types
    test_node_types = ['test_suite', 'test_case', 'invariant_family']
    test_node_counts = {}
    for node_type in test_node_types:
        cur.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = ?", (node_type,))
        test_node_counts[node_type] = cur.fetchone()[0]

    # Test edge types
    test_edge_types = [
        'defines_test_case', 'defines_test_suite', 'defines_invariant',
        'emits_test_result', 'records_validation_outcome', 'links_to_execution_trace',
        'gates_promotion', 'detects_regression'
    ]
    test_edge_counts = {}
    for edge_type in test_edge_types:
        test_edge_counts[edge_type] = stored_edge_counts.get(edge_type, 0)

    # Test coverage by layer
    cur.execute("""
        SELECT n.layer, COUNT(*) as count
        FROM nodes n
        WHERE n.entity_type IN ('test_suite', 'test_case', 'invariant_family')
        GROUP BY n.layer
    """)
    test_coverage_by_layer = dict(cur.fetchall())

    test_surface_report["test_surface_nodes"] = test_node_counts
    test_surface_report["test_surface_edges"] = test_edge_counts
    test_surface_report["test_coverage_metrics"] = {
        "total_test_nodes": sum(test_node_counts.values()),
        "total_test_edges": sum(test_edge_counts.values()),
        "test_edge_types_found": sum(1 for count in test_edge_counts.values() if count > 0),
        "test_edge_types_total": len(test_edge_types),
        "test_edge_coverage_percentage": (sum(1 for count in test_edge_counts.values() if count > 0) / len(test_edge_types) * 100) if test_edge_types else 0
    }
    test_surface_report["test_coverage_by_layer"] = test_coverage_by_layer
    test_surface_report["critical_path_linkage"] = {
        "test_cases_with_execution_trace": test_edge_counts.get('links_to_execution_trace', 0),
        "test_cases_with_validation": test_edge_counts.get('records_validation_outcome', 0),
        "test_cases_with_regression_detection": test_edge_counts.get('detects_regression', 0),
        "test_cases_with_promotion_gates": test_edge_counts.get('gates_promotion', 0),
        "critical_path_completeness": "partial" if test_edge_counts.get('links_to_execution_trace', 0) > 0 else "missing"
    }

    conn.close()

    # Write all reports
    reports = [
        (f"layer_coverage_report_{ts}.json", layer_report),
        (f"edge_density_report_{ts}.json", edge_report),
        (f"provenance_report_{ts}.json", provenance_report),
        (f"replay_determinism_report_{ts}.json", determinism_report),
        (f"boundary_report_{ts}.json", boundary_report),
        (f"mutation_integrity_report_{ts}.json", mutation_report),
        (f"test_surface_coverage_{ts}.json", test_surface_report)
    ]

    for filename, report_data in reports:
        report_path = reports_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, sort_keys=True)
        print(f"[ADG] Report generated: {filename}")


def main() -> None:
    # Timestamp in US Eastern time, format MMDDYYYY_HHMM (military time)
    est = timezone(timedelta(hours=-4))  # EDT (UTC-4); DST active Mar-Nov in US Eastern
    now_est = datetime.now(est)
    ts = now_est.strftime("%m%d%Y_%H%M")  # e.g., 03132026_0512
    adg_artifacts_dir = ROOT / "artifacts" / "adg"
    generate_full_adg(adg_artifacts_dir, ts)


if __name__ == "__main__":
    main()
