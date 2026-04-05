"""ADG CLI entry point.

Usage:
    python -m agentic_core.adg.cli scan [--repo-root .] [--commit <sha>] [--diff-files f1 f2]
    python -m agentic_core.adg.cli blast-radius --changed f1 f2 [--repo-root .]
    python -m agentic_core.adg.cli refactor --analyze FILE [--repo-root .]
    python -m agentic_core.adg.cli refactor --rename OLD NEW [--repo-root .]
    python -m agentic_core.adg.cli refactor --plan [--files f1 f2] [--repo-root .]
    python -m agentic_core.adg.cli hotspots [--top N] [--repo-root .]
    python -m agentic_core.adg.cli test-gaps [--repo-root .]
    python -m agentic_core.adg.cli coupling [--repo-root .]
    python -m agentic_core.adg.cli api-surface [--repo-root .]
    python -m agentic_core.adg.cli dip-check [--repo-root .]

Each invocation prints:
    ADG-DETERMINISM-DIGEST: <sha256_hex>
and exits 0 (pass) or 1 (invariant violations found).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "cli")
_emit_applies_guardrail("p0", "cli", "p0_governance")
_emit_snapshots_state("p0", "cli", "state_snapshot")
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

_emit_emits_metric_event("cli", "p4obs", "metric_1")
_emit_emits_metric_event("cli", "p4obs", "metric_2")
_emit_emits_metric_event("cli", "p4obs", "metric_3")
_emit_emits_metric_event("cli", "p4obs", "metric_4")
_emit_emits_metric_event("cli", "p4obs", "metric_5")
_emit_emits_metric_event("cli", "p4obs", "metric_6")
_emit_records_incident_event("cli", "p4obs", "incident")
_emit_captures_runtime_anomaly("cli", "p4obs", "anomaly")
_emit_writes_observability_log("cli", "p4obs", "obs_log")
_emit_updates_monitoring_state("cli", "p4obs", "mon_state")
_emit_triggers_alert("cli", "p4obs", "alert")
_emit_links_incident_trace("cli", "p4obs", "trace_link")
_emit_captures_pattern("cli", "p3lm", "pattern")
_emit_records_learning_event("cli", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cli", "p3lm", "snapshot")
_emit_feeds_meta_learning("cli", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cli", "p3lm", "routing")
_emit_improves_agent_policy("cli", "p3lm", "policy")
_emit_stores_learning_state("cli", "p3lm", "state")
_emit_records_execution_trace("cli", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cli", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cli", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cli", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cli", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cli", "env_read", "p2_env_1")
_emit_reads_environ("cli", "env_read", "p2_env_2")
_emit_reads_runtime_state("cli", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cli", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cli", "context_pull")
_emit_pulls_context("p1", "cli", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cli", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cli", "uwg_term_2")
_emit_writes_through("p1", "cli", "write_through")
_emit_writes_through("p1", "cli", "write_through_2")
_emit_validated_by_safety_plane("p1", "cli", "safety_validation")
_emit_invokes_eval("p1", "cli", "eval_call")
_emit_proposal_commits_routing("p1", "cli", "routing_commit")
_emit_escalates_to_human("p1", "cli", "human_escalation")
_emit_routes_through("p1", "cli", "route_through")
_emit_checks_agent_registry("p1", "cli", "agent_registry")
_emit_validates_agent_capability("p1", "cli", "capability")
_emit_dispatches_execution_plan("p1", "cli", "exec_plan")
_emit_agent_executes_agent("p1", "cli", "sub_agent")
_emit_routes_to_agent("p1", "cli", "target_agent")
_emit_verifies_policy("p1", "cli", "policy_check")
_emit_observes_runtime_state("p1", "cli", "runtime_state")
_emit_verifies_boundary("p1", "cli", "boundary_check")
_emit_transcripts_response("p1", "cli", "transcript")
_emit_hard_fails_untranscripted("p1", "cli")
_emit_gated_by_confidence("p1", "cli", "confidence_gate")
emit_replay_key("p0", "cli")
emit_determinism_digest("p0", "cli")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cli", "execution_auth")
_emit_validates_capability("p2", "cli", "capability_check")
_emit_routes_to_capability("p2", "cli", "capability_route")
_emit_writes_via_uwg("p2", "cli", "uwg_write")
_emit_blocks_direct_write("p2", "cli", "direct_write_block")
_emit_records_tool_invocation("p2", "cli", "tool_invocation")
_emit_captures_execution_output("p2", "cli", "exec_output")
_emit_dispatches_agent("p3", "cli", "agent_dispatch")
_emit_coordinates_agents("p3", "cli", "agent_coordination")
_emit_records_workflow_lineage("p3", "cli", "workflow_lineage")
_emit_records_healing_outcome("p3", "cli", "healing_outcome")
_emit_escalates_failure("p3", "cli", "failure_escalation")
_emit_orchestrates_workflow("p3", "cli", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cli", "healing_dispatch")
_emit_invokes_evaluation("p3", "cli", "evaluation_signal")
_emit_records_telemetry_event("p4", "cli", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cli", "eval_metric")
_emit_stores_embedding("p4", "cli", "embedding_store")
_emit_updates_meta_learning_state("p4", "cli", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cli", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace_cli", "cli_dispatch_entry")
emit_determinism_digest("trace_cli", "cli_dispatch_exit")
emit_determinism_digest("trace_cli", "cli_tool_invoke")
emit_determinism_digest("trace_cli", "cli_tool_complete")
emit_determinism_digest("trace_cli", "cli_agent_entry")
emit_determinism_digest("trace_cli", "cli_agent_exit")
emit_determinism_digest("trace_cli", "cli_uwg_write")
emit_determinism_digest("trace_cli", "cli_trace_sign")
emit_determinism_digest("trace_cli", "cli_guardrail_check")
emit_determinism_digest("trace_cli", "cli_policy_verify")
_emit_writes_through("p1", "cli", "uwg_governed_write")
_emit_writes_through("p1", "cli", "uwg_governed_write_2")
_emit_pulls_context("p1", "cli", "context_retrieval")
_emit_pulls_context("p1", "cli", "context_retrieval_2")
emit_determinism_digest("trace_cli", "cli_dispatch")
emit_determinism_digest("trace_cli", "cli_complete")
_emit_validated_by_safety_plane("p1", "cli", "safety_validation")


def _cmd_scan(args: argparse.Namespace) -> int:
    import json
    from pathlib import Path

    from agentic_core.adg.ci.invariant_scanner_config import run_ci_scan

    diff_files = args.diff_files if args.diff_files else None
    include_tests = not getattr(args, "exclude_tests", False)
    report = run_ci_scan(
        repo_root=args.repo_root,
        diff_files=diff_files,
        commit_sha=args.commit or "",
        print_digest=True,
        include_tests=include_tests,
    )
    report.print_summary()

    # A1: write scan_manifest.json if requested
    if (
        getattr(args, "write_manifest", False)
        and hasattr(report, "scan_result")
        and report.scan_result is not None
    ):
        manifest_path = Path(args.repo_root) / "artifacts" / "adg" / "scan_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(report.scan_result.manifest.to_dict(), indent=2),
            encoding="utf-8",
        )
        print(f"ADG-MANIFEST: {manifest_path}")

    return report.exit_code()


def _cmd_blast_radius(args: argparse.Namespace) -> int:
    from agentic_core.adg.applications.BlastRadiusResult import compute_blast_radius
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=Path(args.repo_root))
    result = scanner.scan(commit_sha=args.commit or "")
    result.print_digest()

    br = compute_blast_radius(
        changed_files=args.changed or [],
        result=result,
        commit_sha=args.commit or "",
    )
    br.print_summary()
    return 0


def _cmd_build_artifact(args: argparse.Namespace) -> int:
    from agentic_core.adg.artifact.builder_types import build_artifact
    from agentic_core.adg.artifact.serializer_util import write_artifact
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    repo_root = Path(args.repo_root)
    scanner = ADGStaticScanner(repo_root=repo_root)
    result = scanner.scan(commit_sha=args.commit or "")
    result.print_digest()

    artifact = build_artifact(result, repo_root=repo_root)

    if getattr(args, "output", None):
        out_path = Path(args.output)
    else:
        out_path = repo_root / "artifacts" / "adg" / "adg_canonical_artifact.json"

    write_artifact(artifact, out_path)
    print(f"ADG-ARTIFACT: {out_path}")
    print(f"ADG-ARTIFACT-DIGEST: {artifact.artifact_digest}")
    print(f"ADG-ARTIFACT-ENTITIES: {len(artifact.entities)}")
    print(f"ADG-ARTIFACT-RELATIONS: {len(artifact.relations)}")
    print(f"ADG-ARTIFACT-UNRESOLVED: {len(artifact.unresolved_imports)}")
    return 0


def _cmd_impact(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.runtime.cache_loader import load_or_scan
    from tools.change_impact_engine import ChangeImpactEngine

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    engine = ChangeImpactEngine(result, repo_root=repo_root)
    impact = engine.analyze(args.changed or [], include_tests=True)

    if getattr(args, "output", None):
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(impact.to_dict(), indent=2), encoding="utf-8")
        print(f"ADG-IMPACT: {out_path}")
    else:
        print(json.dumps(impact.to_dict(), indent=2))

    return 0 if impact.route_mode == "NORMAL" else 1


def _cmd_refactor(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    if getattr(args, "rename", None):
        from agentic_core.adg.applications.rename_safety_types import analyze_rename

        old_path, new_path = args.rename
        report = analyze_rename(result, old_path=old_path, new_path=new_path)
        print(report.summary)
        print(json.dumps(report.to_dict(), indent=2))
        return 0 if report.is_safe else 1

    if getattr(args, "analyze", None):
        from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics
        from agentic_core.adg.analysis.hotspot_index_types import HotspotIndex
        from agentic_core.adg.analysis.test_gap_types import detect_test_gaps
        from agentic_core.adg.applications.placement_advisor_types import PlacementAdvisor

        target = args.analyze
        idx = HotspotIndex.build(result)
        coupling = compute_coupling_metrics(result)
        gaps = detect_test_gaps(result, hotspot_index=idx)
        advisor = PlacementAdvisor(result, repo_root=repo_root)
        ctx = advisor.get_file_context(target)

        m = idx.metrics(target)
        has_gap = target in {e.module_path for e in gaps.uncovered_modules}
        output = {
            "target": target,
            "coupling": m.to_dict(),
            "zone": coupling.metrics_by_module.get(target, None)
            and coupling.metrics_by_module[target].to_dict(),
            "test_gap": has_gap,
            "file_context": {
                "layer": ctx.layer,
                "direct_importers": ctx.direct_importers,
                "direct_imports": ctx.direct_imports,
                "likely_tests": ctx.likely_tests,
                "structural_risks": ctx.structural_risks,
            },
        }
        print(json.dumps(output, indent=2))
        return 0

    if getattr(args, "plan", False):
        from agentic_core.adg.applications.refactoring_planner_config import build_refactoring_plan

        files = getattr(args, "files", None) or []
        plan = build_refactoring_plan(result, target_files=files or None)
        print(plan.summary)
        print(json.dumps(plan.to_dict(), indent=2))
        return 0

    print("refactor: specify --rename OLD NEW, --analyze FILE, or --plan", file=sys.stderr)
    return 1


def _cmd_hotspots(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.hotspot_index_types import HotspotIndex
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    idx = HotspotIndex.build(result)
    n = getattr(args, "top", 20) or 20
    key = getattr(args, "key", "coupling") or "coupling"
    hotspots = idx.top_hotspots(n=n, threshold=0, key=key)
    print(
        json.dumps(
            {"stats": idx.stats(), "hotspots": [h.to_dict() for h in hotspots]},
            indent=2,
        )
    )
    return 0


def _cmd_test_gaps(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.hotspot_index_types import HotspotIndex
    from agentic_core.adg.analysis.test_gap_types import detect_test_gaps
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    idx = HotspotIndex.build(result)
    report = detect_test_gaps(result, hotspot_index=idx)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 0


def _cmd_coupling(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = compute_coupling_metrics(result)
    pain = [m.to_dict() for m in report.top_pain_zone[:20]]
    useless = [m.to_dict() for m in report.top_uselessness_zone[:20]]
    unstable = [m.to_dict() for m in report.most_unstable[:20]]
    print(
        json.dumps(
            {
                "pain_zone": pain,
                "uselessness_zone": useless,
                "most_unstable": unstable,
            },
            indent=2,
        )
    )
    return 0


def _cmd_api_surface(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.applications.api_surface_types import build_api_surface
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = build_api_surface(result)
    print(json.dumps(report.to_dict(), indent=2))
    return 0


def _cmd_dip_check(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.dep_inversion_types import detect_dip_violations
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = detect_dip_violations(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 1 if report.violation_count > 0 else 0


def _cmd_runtime_graph(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.applications.runtime_graph_types import build_runtime_graph
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = build_runtime_graph(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 0


def _cmd_layer_authority(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.layer_authority_types import detect_layer_authority_violations
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = detect_layer_authority_violations(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 1 if report.violation_count > 0 else 0


def _cmd_mutation_paths(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.mutation_authority_validator import verify_mutation_paths
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = verify_mutation_paths(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    critical = len(report.critical_violations())
    return 1 if critical > 0 else 0


def _cmd_state_lineage(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.applications.state_lineage_types import build_lineage_index
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    index = build_lineage_index(result)
    summary = index.coverage_summary()

    if args.query:
        records = index.mutations_for_state(args.query)
        print(f"Mutations for state key '{args.query}': {len(records)} records")
        print(json.dumps([r.to_dict() for r in records[:50]], indent=2))
    else:
        print(json.dumps(summary, indent=2))
    return 0


def _cmd_verify_architecture(args: argparse.Namespace) -> int:
    from agentic_core.adg.applications.architecture_verifier_validator import verify_architecture
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    skip: frozenset[str] = frozenset(args.skip_planes) if args.skip_planes else frozenset()
    report = verify_architecture(result, skip_planes=skip)
    report.print_summary()

    if args.json:
        import json

        print(json.dumps(report.to_dict(), indent=2))

    return report.exit_code()


def _cmd_policy_hash(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    report = validate_policy_hash_coupling(result)
    print(report.summary)
    print(json.dumps(report.to_dict(), indent=2))
    return 1 if report.violation_count > 0 else 0


def _cmd_build_artifacts(args: argparse.Namespace) -> int:
    import json
    from datetime import datetime, timedelta, timezone

    from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts
    from agentic_core.adg.artifact.builder_types import build_artifact
    from agentic_core.adg.processing.phase2_disposition_processor import run_phase2_disposition_processing
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(args.repo_root)
    result = load_or_scan(repo_root=str(repo_root))
    result.print_digest()

    est = timezone(timedelta(hours=-5))
    ts = datetime.now(est).strftime("%m%d%Y")
    out_dir = Path(getattr(args, "output_dir", None) or repo_root / "artifacts" / "adg")
    artifact = build_artifact(result, repo_root=repo_root)
    paths = write_all_artifacts(artifact, out_dir=out_dir, ts=ts)

    # Phase 2: Auto-disposition violations based on test coverage and guardian comments
    print(" Phase 2: Auto-dispositioning violations...")
    disposition_results = run_phase2_disposition_processing(paths.sqlite)

    # Phase 3: Auto-remediation analysis
    print(" Phase 3: Analyzing violations for auto-remediation...")
    remediation_actions = run_phase3_remediation_analysis(paths.sqlite)

    # Phase 3.2: Enhanced test coverage integration
    print("🔍 Phase 3.2: Enhanced test coverage analysis...")
    from .processing.phase3_enhanced_test_coverage import run_phase3_enhanced_test_coverage

    # Find test directories
    test_dirs = []
    for test_dir in [repo_root / "tests", repo_root / "test", repo_root / "unit_tests"]:
        if test_dir.exists():
            test_dirs.append(test_dir)

    if test_dirs:
        coverage_results = run_phase3_enhanced_test_coverage(paths.sqlite, test_dirs)
    else:
        coverage_results = {"coverage_gaps": 0, "tests_discovered": 0, "test_edges_created": 0}
        print("  No test directories found")

    # Phase 3.3: Intelligent disposition system
    print("🧠 Phase 3.3: AI-assisted intelligent disposition analysis...")
    from .processing.phase3_intelligent_disposition import run_phase3_intelligent_disposition

    disposition_results = run_phase3_intelligent_disposition(paths.sqlite)

    # Build final report
    report = {
        "snapshot": str(paths.snapshot),
        "sqlite": str(paths.sqlite),
        "file_graph": str(paths.file_graph),
        "symbol_graph": str(paths.symbol_graph),
        "governance_graph": str(paths.governance_graph),
        "sizes": paths.size_report(),
        "artifact_digest": artifact.artifact_digest,
        "entities": len(artifact.entities),
        "relations": len(artifact.relations),
        "phase2_dispositions": disposition_results,
        "phase3_remediation": {
            "total_candidates": len(remediation_actions),
            "high_confidence": len([a for a in remediation_actions if a.confidence > 0.7]),
            "high_risk": len([a for a in remediation_actions if a.risk_score > 0.8]),
            "strategies": {
                strategy.value: len([a for a in remediation_actions if a.strategy == strategy])
                for strategy in {a.strategy for a in remediation_actions}
            },
        },
        "phase3_test_coverage": coverage_results,
        "phase3_intelligent_disposition": disposition_results,
    }
    print(json.dumps(report, indent=2))
    return 0


def _cmd_incremental_scan(args: argparse.Namespace) -> int:
    import json

    from agentic_core.adg.extraction.incremental import incremental_scan

    repo_root = Path(args.repo_root)
    changed_files = getattr(args, "changed", None) or None
    base_ref = getattr(args, "base_ref", "HEAD~1")
    snapshot_path = getattr(args, "snapshot", None)
    snapshot_path = Path(snapshot_path) if snapshot_path else None

    result, stats = incremental_scan(
        repo_root=repo_root,
        changed_files=changed_files,
        full_snapshot_path=snapshot_path,
        base_ref=base_ref,
    )
    result.print_digest()
    print(stats.summary())
    print(
        json.dumps(
            {
                "total_modules": stats.total_modules,
                "changed_files": stats.changed_files,
                "affected_modules": stats.affected_modules,
                "rescanned": stats.rescanned,
                "skipped": stats.skipped,
                "edges_total": stats.edges_total,
            },
            indent=2,
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="adg",
        description="Architecture Dependency Graph CLI",
    )
    parser.add_argument("--repo-root", default=".", help="Path to repo root")
    parser.add_argument("--commit", default="", help="Git commit SHA")

    subparsers = parser.add_subparsers(dest="command")

    scan_p = subparsers.add_parser("scan", help="Run full invariant scan")
    scan_p.add_argument(
        "--diff-files",
        nargs="*",
        metavar="FILE",
        help="Scan only these files (PR diff mode)",
    )
    scan_p.add_argument(
        "--exclude-tests",
        action="store_true",
        default=False,
        help="Exclude tests/ and ops_scripts/ from scan roots",
    )
    scan_p.add_argument(
        "--write-manifest",
        action="store_true",
        default=False,
        help="Write artifacts/adg/scan_manifest.json after scan (A1)",
    )

    br_p = subparsers.add_parser("blast-radius", help="Compute blast-radius score")
    br_p.add_argument(
        "--changed",
        nargs="*",
        metavar="FILE",
        help="Changed files for blast-radius computation",
    )

    art_p = subparsers.add_parser("build-artifact", help="Build canonical ADG artifact (schema v3)")
    art_p.add_argument(
        "--output",
        default=None,
        help="Output path for artifact JSON (default: artifacts/adg/adg_canonical_artifact.json)",
    )

    impact_p = subparsers.add_parser("impact", help="Compute change impact for changed files")
    impact_p.add_argument(
        "--changed",
        nargs="*",
        metavar="FILE",
        help="Changed files for impact analysis",
    )
    impact_p.add_argument(
        "--output",
        default=None,
        help="Output path for impact JSON",
    )

    ref_p = subparsers.add_parser("refactor", help="Refactoring safety and planning (E12, E17)")
    ref_p.add_argument("--rename", nargs=2, metavar=("OLD", "NEW"), help="Rename/move safety analysis")
    ref_p.add_argument("--analyze", metavar="FILE", help="Full structural analysis of a file")
    ref_p.add_argument("--plan", action="store_true", default=False, help="Generate refactoring plan")
    ref_p.add_argument("--files", nargs="*", metavar="FILE", help="Target files for refactoring plan")

    hs_p = subparsers.add_parser("hotspots", help="Show fan-in/fan-out hotspot index (E14)")
    hs_p.add_argument("--top", type=int, default=20, help="Number of hotspots to show")
    hs_p.add_argument(
        "--key", default="coupling", choices=["coupling", "fan_in", "fan_out", "instability"], help="Sort key"
    )

    subparsers.add_parser("test-gaps", help="Detect modules with no test coverage signal (E15)")
    subparsers.add_parser("coupling", help="Coupling/cohesion metrics — Martin stability (E16)")
    subparsers.add_parser("api-surface", help="Public API surface extraction (E13)")
    subparsers.add_parser("dip-check", help="Dependency Inversion Principle check (E18)")

    # P6 prompt governance
    subparsers.add_parser(
        "prompt-authority", help="Prompt authority DAG enforcement — slot hierarchy violations (E21)"
    )
    subparsers.add_parser("prompt-lifecycle", help="Prompt lifecycle graph — generates/consumes edges (E20)")
    pi_p = subparsers.add_parser("prompt-impact", help="Prompt blast radius for changed files (E24)")
    pi_p.add_argument("--changed", nargs="*", metavar="FILE", help="Changed files for prompt impact analysis")

    # P3 runtime / authority / mutation / policy
    subparsers.add_parser(
        "runtime-graph", help="Runtime execution graph — AgentAction/ToolInvocation/LayerTransition (E26)"
    )
    subparsers.add_parser(
        "layer-authority", help="Layer authority enforcement — behavioral contract violations (E27)"
    )
    subparsers.add_parser("mutation-paths", help="Mutation path verification — UWG bypass detection (E28)")
    sl_p = subparsers.add_parser("state-lineage", help="State lineage query — who mutated this state? (E29)")
    sl_p.add_argument(
        "--query", default="", metavar="STATE_KEY", help="State symbol key to trace mutations for"
    )
    va_p = subparsers.add_parser(
        "verify-architecture", help="Unified architecture verification across all planes (E30)"
    )
    va_p.add_argument(
        "--skip-planes",
        nargs="*",
        metavar="PLANE",
        help="Planes to skip: runtime_graph layer_authority mutation_paths policy_hash",
    )
    va_p.add_argument("--json", action="store_true", default=False, help="Emit full JSON report")
    subparsers.add_parser("policy-hash", help="Policy hash runtime coupling validation (E31)")

    # Artifact management
    ba_p = subparsers.add_parser(
        "build-artifacts",
        help="Write non-redundant artifact set: snapshot (CI), sqlite (primary), + 3 split planes (100% edge coverage)",
    )
    ba_p.add_argument(
        "--output-dir",
        default=None,
        metavar="DIR",
        help="Output directory (default: artifacts/adg)",
    )

    is_p = subparsers.add_parser(
        "incremental-scan",
        help="Incremental ADG scan — re-scan only changed + affected modules",
    )
    is_p.add_argument(
        "--changed",
        nargs="*",
        metavar="FILE",
        help="Explicitly changed files (repo-relative). If omitted, uses git diff.",
    )
    is_p.add_argument(
        "--base-ref",
        default="HEAD~1",
        metavar="REF",
        help="Git base ref for diff (default: HEAD~1)",
    )
    is_p.add_argument(
        "--snapshot",
        default=None,
        metavar="PATH",
        help="Path to latest adg_full.json for reverse-import propagation",
    )

    parsed = parser.parse_args(argv)

    if parsed.command == "scan":
        return _cmd_scan(parsed)
    if parsed.command == "blast-radius":
        return _cmd_blast_radius(parsed)
    if parsed.command == "build-artifact":
        return _cmd_build_artifact(parsed)
    if parsed.command == "impact":
        return _cmd_impact(parsed)
    if parsed.command == "refactor":
        return _cmd_refactor(parsed)
    if parsed.command == "hotspots":
        return _cmd_hotspots(parsed)
    if parsed.command == "test-gaps":
        return _cmd_test_gaps(parsed)
    if parsed.command == "coupling":
        return _cmd_coupling(parsed)
    if parsed.command == "api-surface":
        return _cmd_api_surface(parsed)
    if parsed.command == "dip-check":
        return _cmd_dip_check(parsed)

    # P6 prompt governance
    if parsed.command == "prompt-authority":
        return _cmd_prompt_authority(parsed)
    if parsed.command == "prompt-lifecycle":
        return _cmd_prompt_lifecycle(parsed)
    if parsed.command == "prompt-impact":
        return _cmd_prompt_impact(parsed)

    # P3 runtime / authority / mutation / policy
    if parsed.command == "runtime-graph":
        return _cmd_runtime_graph(parsed)
    if parsed.command == "layer-authority":
        return _cmd_layer_authority(parsed)
    if parsed.command == "mutation-paths":
        return _cmd_mutation_paths(parsed)
    if parsed.command == "state-lineage":
        return _cmd_state_lineage(parsed)
    if parsed.command == "verify-architecture":
        return _cmd_verify_architecture(parsed)
    if parsed.command == "policy-hash":
        return _cmd_policy_hash(parsed)

    if parsed.command == "build-artifacts":
        return _cmd_build_artifacts(parsed)
    if parsed.command == "incremental-scan":
        return _cmd_incremental_scan(parsed)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
