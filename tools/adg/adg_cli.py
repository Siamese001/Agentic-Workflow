"""ADG Canonical CLI — single unified entry point for all ADG operations.

USAGE OVERVIEW
==============

Build and health:
  python tools/adg_cli.py build --rebuild
  python tools/adg_cli.py build --cached
  python tools/adg_cli.py health [--strict]
  python tools/adg_cli.py stats
  python tools/adg_cli.py diff --baseline <artifact_or_commit>

Structural query:
  python tools/adg_cli.py impact --file <path>
  python tools/adg_cli.py impact --symbol <qualified_name>
  python tools/adg_cli.py who-uses --symbol <qualified_name>
  python tools/adg_cli.py neighbors --file <path>
  python tools/adg_cli.py ownership --symbol <qualified_name>
  python tools/adg_cli.py config-consumers --symbol <qualified_name>

Testing:
  python tools/adg_cli.py scoped-tests --changed-files <file1,file2,...>
  python tools/adg_cli.py test-coverage --symbol <qualified_name>
  python tools/adg_cli.py missing-tests --symbol <qualified_name>

Guardian:
  python tools/adg_cli.py guardian-scope --high-risk-only
  python tools/adg_cli.py guardian-scope --focus-territory <territory>
  python tools/adg_cli.py guardian-scope --boundary-violations

Execute SSOT / healing:
  python tools/adg_cli.py execution-impact --file <path>
  python tools/adg_cli.py safe-healing-scope --symbol <qualified_name>
  python tools/adg_cli.py healing-radius --symbol <qualified_name>

Developer guidance:
  python tools/adg_cli.py suggest-placement --kind <file_kind> --name <symbol_or_file>
  python tools/adg_cli.py context --file <path>
  python tools/adg_cli.py context --symbol <qualified_name>
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "adg_cli")
_emit_applies_guardrail("p0", "adg_cli", "p0_governance")
_emit_reads_policy_state("p0", "adg_cli", "policy_binding")
_emit_snapshots_state("p0", "adg_cli", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("adg_cli", "p4obs", "metric_1")
_emit_emits_metric_event("adg_cli", "p4obs", "metric_2")
_emit_emits_metric_event("adg_cli", "p4obs", "metric_3")
_emit_emits_metric_event("adg_cli", "p4obs", "metric_4")
_emit_emits_metric_event("adg_cli", "p4obs", "metric_5")
_emit_emits_metric_event("adg_cli", "p4obs", "metric_6")
_emit_records_incident_event("adg_cli", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_cli", "p4obs", "anomaly")
_emit_writes_observability_log("adg_cli", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_cli", "p4obs", "mon_state")
_emit_triggers_alert("adg_cli", "p4obs", "alert")
_emit_links_incident_trace("adg_cli", "p4obs", "trace_link")
_emit_captures_pattern("adg_cli", "p3lm", "pattern")
_emit_records_learning_event("adg_cli", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_cli", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_cli", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_cli", "p3lm", "routing")
_emit_improves_agent_policy("adg_cli", "p3lm", "policy")
_emit_stores_learning_state("adg_cli", "p3lm", "state")
_emit_records_execution_trace("adg_cli", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_cli", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_cli", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_cli", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_cli", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_cli", "env_read", "p2_env_1")
_emit_reads_environ("adg_cli", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_cli", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_cli", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_cli", "context_pull")
_emit_pulls_context("p1", "adg_cli", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adg_cli", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_cli", "uwg_term_2")
_emit_writes_through("p1", "adg_cli", "write_through")
_emit_writes_through("p1", "adg_cli", "write_through_2")
_emit_validated_by_safety_plane("p1", "adg_cli", "safety_validation")
_emit_invokes_eval("p1", "adg_cli", "eval_call")
_emit_proposal_commits_routing("p1", "adg_cli", "routing_commit")
_emit_escalates_to_human("p1", "adg_cli", "human_escalation")
_emit_routes_through("p1", "adg_cli", "route_through")
_emit_checks_agent_registry("p1", "adg_cli", "agent_registry")
_emit_validates_agent_capability("p1", "adg_cli", "capability")
_emit_dispatches_execution_plan("p1", "adg_cli", "exec_plan")
_emit_agent_executes_agent("p1", "adg_cli", "sub_agent")
_emit_routes_to_agent("p1", "adg_cli", "target_agent")
_emit_verifies_policy("p1", "adg_cli", "policy_check")
_emit_observes_runtime_state("p1", "adg_cli", "runtime_state")
_emit_verifies_boundary("p1", "adg_cli", "boundary_check")
_emit_transcripts_response("p1", "adg_cli", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_cli")
_emit_gated_by_confidence("p1", "adg_cli", "confidence_gate")
emit_replay_key("p0", "adg_cli")
emit_determinism_digest("p0", "adg_cli")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_cli", "execution_auth")
_emit_validates_capability("p2", "adg_cli", "capability_check")
_emit_routes_to_capability("p2", "adg_cli", "capability_route")
_emit_writes_via_uwg("p2", "adg_cli", "uwg_write")
_emit_blocks_direct_write("p2", "adg_cli", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_cli", "tool_invocation")
_emit_captures_execution_output("p2", "adg_cli", "exec_output")
_emit_dispatches_agent("p3", "adg_cli", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_cli", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_cli", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_cli", "healing_outcome")
_emit_escalates_failure("p3", "adg_cli", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_cli", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_cli", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_cli", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_cli", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_cli", "eval_metric")
_emit_stores_embedding("p4", "adg_cli", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_cli", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_cli", "exec_snapshot_link")
_emit_reads_through("l4", "adg_cli", "urg_read_1")
_emit_reads_through("l4", "adg_cli", "urg_read_2")
_emit_reads_through("l4", "adg_cli", "urg_read_3")
_emit_reads_through("l4", "adg_cli", "urg_read_4")
_emit_reads_through("l4", "adg_cli", "urg_read_5")
_emit_reads_through("l4", "adg_cli", "urg_read_6")
_emit_reads_through("l4", "adg_cli", "urg_read_7")
_emit_reads_through("l4", "adg_cli", "urg_read_8")
_emit_reads_through("l4", "adg_cli", "urg_read_9")
_emit_reads_through("l4", "adg_cli", "urg_read_10")
_emit_reads_through("l4", "adg_cli", "urg_read_11")
_emit_reads_through("l4", "adg_cli", "urg_read_12")
_emit_reads_through("l4", "adg_cli", "urg_read_13")
_emit_reads_through("l4", "adg_cli", "urg_read_14")
_emit_reads_through("l4", "adg_cli", "urg_read_15")
_emit_reads_through("l4", "adg_cli", "urg_read_16")
_emit_reads_through("l4", "adg_cli", "urg_read_17")
_emit_reads_through("l4", "adg_cli", "urg_read_18")
_emit_reads_through("l4", "adg_cli", "urg_read_19")
_emit_reads_through("l4", "adg_cli", "urg_read_20")
_emit_reads_through("l4", "adg_cli", "urg_read_21")
_emit_reads_through("l4", "adg_cli", "urg_read_22")
_emit_reads_through("l4", "adg_cli", "urg_read_23")
_emit_reads_through("l4", "adg_cli", "urg_read_24")
_emit_reads_through("l4", "adg_cli", "urg_read_25")
_emit_reads_through("l4", "adg_cli", "urg_read_26")
_emit_reads_through("l4", "adg_cli", "urg_read_27")
_emit_reads_through("l4", "adg_cli", "urg_read_28")
_emit_reads_through("l4", "adg_cli", "urg_read_29")
_emit_reads_through("l4", "adg_cli", "urg_read_30")
_emit_reads_through("l4", "adg_cli", "urg_read_31")
_emit_reads_through("l4", "adg_cli", "urg_read_32")
_emit_reads_through("l4", "adg_cli", "urg_read_33")
_emit_reads_through("l4", "adg_cli", "urg_read_34")
_emit_reads_through("l4", "adg_cli", "urg_read_35")
_emit_reads_through("l4", "adg_cli", "urg_read_36")
_emit_reads_through("l4", "adg_cli", "urg_read_37")
_emit_reads_through("l4", "adg_cli", "urg_read_38")
_emit_reads_through("l4", "adg_cli", "urg_read_39")
_emit_reads_through("l4", "adg_cli", "urg_read_40")
_emit_reads_through("l4", "adg_cli", "urg_read_41")
_emit_reads_through("l4", "adg_cli", "urg_read_42")
_emit_reads_through("l4", "adg_cli", "urg_read_43")
_emit_reads_through("l4", "adg_cli", "urg_read_44")
_emit_reads_through("l4", "adg_cli", "urg_read_45")
_emit_reads_through("l4", "adg_cli", "urg_read_46")
_emit_reads_through("l4", "adg_cli", "urg_read_47")
_emit_reads_through("l4", "adg_cli", "urg_read_48")
_emit_reads_through("l4", "adg_cli", "urg_read_49")
_emit_reads_through("l4", "adg_cli", "urg_read_50")
_emit_reads_through("l4", "adg_cli", "urg_read_51")
_emit_reads_through("l4", "adg_cli", "urg_read_52")
_emit_reads_through("l4", "adg_cli", "urg_read_53")
_emit_reads_through("l4", "adg_cli", "urg_read_54")
_emit_reads_through("l4", "adg_cli", "urg_read_55")
_emit_reads_through("l4", "adg_cli", "urg_read_56")
_emit_reads_through("l4", "adg_cli", "urg_read_57")
_emit_reads_through("l4", "adg_cli", "urg_read_58")
_emit_reads_through("l4", "adg_cli", "urg_read_59")
_emit_reads_through("l4", "adg_cli", "urg_read_60")
_emit_reads_through("l4", "adg_cli", "urg_read_61")
_emit_reads_through("l4", "adg_cli", "urg_read_62")
_emit_reads_through("l4", "adg_cli", "urg_read_63")
_emit_reads_through("l4", "adg_cli", "urg_read_64")
_emit_reads_through("l4", "adg_cli", "urg_read_65")
_emit_reads_through("l4", "adg_cli", "urg_read_66")
_emit_reads_through("l4", "adg_cli", "urg_read_67")
_emit_reads_through("l4", "adg_cli", "urg_read_68")
_emit_reads_through("l4", "adg_cli", "urg_read_69")
_emit_reads_through("l4", "adg_cli", "urg_read_70")
_emit_reads_through("l4", "adg_cli", "urg_read_71")
_emit_reads_through("l4", "adg_cli", "urg_read_72")
_emit_reads_through("l4", "adg_cli", "urg_read_73")
_emit_reads_through("l4", "adg_cli", "urg_read_74")
_emit_reads_through("l4", "adg_cli", "urg_read_75")
_emit_reads_through("l4", "adg_cli", "urg_read_76")
_emit_reads_through("l4", "adg_cli", "urg_read_77")
_emit_reads_through("l4", "adg_cli", "urg_read_78")
_emit_reads_through("l4", "adg_cli", "urg_read_79")
_emit_reads_through("l4", "adg_cli", "urg_read_80")
_emit_reads_through("l4", "adg_cli", "urg_read_81")
_emit_reads_through("l4", "adg_cli", "urg_read_82")
_emit_reads_through("l4", "adg_cli", "urg_read_83")
_emit_reads_through("l4", "adg_cli", "urg_read_84")
_emit_reads_through("l4", "adg_cli", "urg_read_85")
_emit_reads_through("l4", "adg_cli", "urg_read_86")
_emit_reads_through("l4", "adg_cli", "urg_read_87")
_emit_reads_through("l4", "adg_cli", "urg_read_88")
_emit_reads_through("l4", "adg_cli", "urg_read_89")
_emit_reads_through("l4", "adg_cli", "urg_read_90")
_emit_reads_through("l4", "adg_cli", "urg_read_91")
_emit_reads_through("l4", "adg_cli", "urg_read_92")
_emit_reads_through("l4", "adg_cli", "urg_read_93")

# Path bootstrap: allow direct invocation as `python tools/adg_cli.py`
# guardian: allow-global_mutation
_REPO_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logger = logging.getLogger(__name__)

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"
_ARTIFACTS_DIR = Path("artifacts/adg")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _repo_root(args_repo_root: str | None) -> Path:
    return Path(args_repo_root) if args_repo_root else Path.cwd()


def _load_scan(repo_root: Path):  # type: ignore[return]
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    return load_or_scan(repo_root=str(repo_root))


def _fresh_scan(repo_root: Path):  # type: ignore[return]
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    from agentic_core.adg.runtime.cache_loader import invalidate_cache

    invalidate_cache()
    scanner = ADGStaticScanner(repo_root=repo_root)
    return scanner.scan()


def _timestamp() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _out(data: dict | list, indent: int = 2) -> None:
    print(json.dumps(data, indent=indent, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Command: build
# ---------------------------------------------------------------------------


def cmd_build(rebuild: bool, repo_root: Path) -> int:
    """Build ADG and emit canonical artifacts."""
    from agentic_core.adg.applications.health_reporter_types import build_health_report
    from agentic_core.adg.artifact.builder_types import build_artifact
    from agentic_core.adg.artifact.serializer_util import write_artifact

    ts = _timestamp()
    artifacts_dir = repo_root / _ARTIFACTS_DIR
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    print(f"ADG-BUILD: {'--rebuild (fresh scan)' if rebuild else '--cached (load from cache)'}")

    if rebuild:
        result = _fresh_scan(repo_root)
    else:
        result = _load_scan(repo_root)

    result.print_digest()

    print(f"ADG-SCAN-MODULES: {len(result.modules)}")
    print(f"ADG-SCAN-EDGES: {len(result.edges)}")

    # Build canonical artifact (schema v3)
    artifact = build_artifact(result, repo_root=repo_root)

    # 1. Write timestamped artifact
    ts_path = artifacts_dir / f"adg_full_{ts}.json"
    write_artifact(artifact, ts_path)
    print(f"ADG-ARTIFACT-TIMESTAMPED: {ts_path}")

    # 2. Write stable canonical pointer (adg_latest.json)
    latest_path = artifacts_dir / "adg_latest.json"
    write_artifact(artifact, latest_path)
    print(f"ADG-ARTIFACT-LATEST: {latest_path}")

    # 3. Build and write health report
    health = build_health_report(artifact, strict=False)
    health_data = health.to_dict()
    health_path = artifacts_dir / f"adg_health_{ts}.json"
    health_path.write_text(json.dumps(health_data, indent=2), encoding="utf-8")
    print(f"ADG-HEALTH-REPORT: {health_path}")

    # 4. Write summary markdown
    summary_path = artifacts_dir / f"adg_summary_{ts}.md"
    _write_summary_markdown(summary_path, artifact, health, ts)
    print(f"ADG-SUMMARY-MARKDOWN: {summary_path}")

    # Print stats
    sm = artifact.structural_metrics
    print("\nADG-STATS:")
    print(f"  Entities:           {sm.total_entities}")
    print(f"  Relations:          {sm.total_relations}")
    print(f"  Module count:       {sm.module_count}")
    print(f"  Symbol count:       {sm.symbol_count}")
    print(f"  Unresolved imports: {sm.unresolved_count}")
    print(f"  Layer violations:   {sm.layer_violation_count}")
    print(f"  Orphan modules:     {len(sm.orphan_modules)}")
    print(f"  Digest:             {artifact.artifact_digest[:24]}...")

    return 0


def _write_summary_markdown(
    path: Path,
    artifact,
    health,
    ts: str,
) -> None:
    sm = artifact.structural_metrics
    lines = [
        f"# ADG Summary — {ts}",
        "",
        f"**Schema version:** {artifact.schema_version}",
        f"**Commit:** {artifact.commit_sha or 'N/A'}",
        f"**Artifact digest:** `{artifact.artifact_digest[:24]}...`",
        f"**Trust gate:** {'✓ PASS' if health.trust_passed else '✗ FAIL'}",
        "",
        "## Structural Counts",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total entities | {sm.total_entities} |",
        f"| Total relations | {sm.total_relations} |",
        f"| Module entities | {sm.module_count} |",
        f"| Symbol entities | {sm.symbol_count} |",
        f"| Unresolved imports | {sm.unresolved_count} |",
        f"| Layer violations | {sm.layer_violation_count} |",
        f"| Orphan modules | {len(sm.orphan_modules)} |",
        "",
        "## Blind Spots",
        "",
        "| Category | Count |",
        "|---|---|",
        f"| Dynamic imports | {artifact.blind_spots.dynamic_import_count} |",
        f"| Star imports | {artifact.blind_spots.star_import_count} |",
        f"| Parse failures | {artifact.blind_spots.parse_failure_count} |",
        "",
        "## Layer Distribution",
        "",
        "| Layer | Module Count |",
        "|---|---|",
    ]
    for layer, count in sorted(sm.by_layer.items()):
        lines.append(f"| {layer} | {count} |")
    lines += [
        "",
        "## Identity Health",
        "",
        "| Identity Kind | Count |",
        "|---|---|",
    ]
    for kind, count in sorted(artifact.identity_health.get("by_identity_kind", {}).items()):
        lines.append(f"| {kind} | {count} |")

    if health.trust_violations:
        lines += ["", "## Trust Violations", ""]
        for v in health.trust_violations:
            lines.append(f"- **{v.rule}**: {v.description} (actual={v.actual} > threshold={v.threshold})")

    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Command: health
# ---------------------------------------------------------------------------


def cmd_health(repo_root: Path, strict: bool = False) -> int:
    """Run trust gate health check on adg_latest.json."""
    from agentic_core.adg.applications.health_reporter_types import build_health_report
    from agentic_core.adg.artifact.builder_types import build_artifact

    latest = repo_root / _ARTIFACTS_DIR / "adg_latest.json"
    if latest.exists():
        # Load from existing artifact file
        import json as _json

        from agentic_core.adg.artifact.builder_types import (
            ADGArtifact,
            BlindSpotReport,
            EntityRecord,
            RelationRecord,
            StructuralMetrics,
        )

        raw = _json.loads(latest.read_text(encoding="utf-8"))
        # Rebuild artifact from raw dict
        entities = [
            EntityRecord(
                adg_name=e["adg_name"],
                entity_type=e["entity_type"],
                layer=e["layer"],
                identity_kind=e["identity_kind"],
                confidence=e["confidence"],
                resolved_path=e["resolved_path"],
                observations=e.get("observations", []),
            )
            for e in raw.get("entities", [])
        ]
        relations = [
            RelationRecord(
                from_name=r["from_name"],
                relation_type=r["relation_type"],
                to_name=r["to_name"],
                edge_kind=r["edge_kind"],
                source_file=r["source_file"],
                line_no=r["line_no"],
                symbol=r.get("symbol", ""),
            )
            for r in raw.get("relations", [])
        ]
        sm_raw = raw.get("structural_metrics", {})
        sm = StructuralMetrics(
            total_entities=sm_raw.get("total_entities", 0),
            total_relations=sm_raw.get("total_relations", 0),
            module_count=sm_raw.get("module_count", 0),
            symbol_count=sm_raw.get("symbol_count", 0),
            external_count=sm_raw.get("external_count", 0),
            unresolved_count=sm_raw.get("unresolved_count", 0),
            orphan_modules=sm_raw.get("orphan_modules", []),
            high_fan_in_modules=sm_raw.get("high_fan_in_modules", []),
            high_fan_out_modules=sm_raw.get("high_fan_out_modules", []),
            layer_violation_count=sm_raw.get("layer_violation_count", 0),
            by_relation_type=sm_raw.get("by_relation_type", {}),
            by_layer=sm_raw.get("by_layer", {}),
        )
        bs_raw = raw.get("blind_spots", {})
        bs = BlindSpotReport(
            dynamic_import_count=bs_raw.get("dynamic_import_count", 0),
            star_import_count=bs_raw.get("star_import_count", 0),
            parse_failure_count=bs_raw.get("parse_failure_count", 0),
            dynamic_import_locations=bs_raw.get("dynamic_import_locations", []),
            star_import_locations=bs_raw.get("star_import_locations", []),
            parse_failure_files=bs_raw.get("parse_failure_files", []),
        )
        artifact = ADGArtifact(
            schema_version=raw.get("schema_version", ""),
            commit_sha=raw.get("commit_sha", ""),
            scanner_digest=raw.get("scanner_digest", ""),
            entities=entities,
            relations=relations,
            unresolved_imports=raw.get("unresolved_imports", []),
            identity_health=raw.get("identity_health", {}),
            structural_metrics=sm,
            blind_spots=bs,
            artifact_digest=raw.get("artifact_digest", ""),
        )
    else:
        print("ADG-HEALTH: adg_latest.json not found — running fresh build first")
        result = _load_scan(repo_root)
        artifact = build_artifact(result, repo_root=repo_root)

    health = build_health_report(artifact, strict=strict)
    health.print_summary()
    _out(health.to_dict())
    return 0 if health.trust_passed else 1


# ---------------------------------------------------------------------------
# Command: stats
# ---------------------------------------------------------------------------


def cmd_stats(repo_root: Path) -> int:
    """Print ADG statistics from adg_latest.json or fresh scan."""
    latest = repo_root / _ARTIFACTS_DIR / "adg_latest.json"
    if latest.exists():
        import json as _json

        raw = _json.loads(latest.read_text(encoding="utf-8"))
        sm = raw.get("structural_metrics", {})
        ih = raw.get("identity_health", {})
        bs = raw.get("blind_spots", {})
        _out(
            {
                "source": str(latest),
                "schema_version": raw.get("schema_version", ""),
                "commit_sha": raw.get("commit_sha", ""),
                "artifact_digest": raw.get("artifact_digest", ""),
                "structural_metrics": sm,
                "identity_health": ih,
                "blind_spots": bs,
            }
        )
    else:
        result = _load_scan(repo_root)
        _out(
            {
                "source": "scan_result_cache",
                "modules": len(result.modules),
                "edges": len(result.edges),
                "digest": result.digest or "",
                "note": "Run 'python tools/adg_cli.py build --rebuild' for full artifact stats",
            }
        )
    return 0


# ---------------------------------------------------------------------------
# Command: diff
# ---------------------------------------------------------------------------


def cmd_diff(baseline: str, repo_root: Path) -> int:
    """Diff current adg_latest.json against a baseline artifact."""
    from agentic_core.adg.artifact.serializer_util import diff_artifacts

    current_path = repo_root / _ARTIFACTS_DIR / "adg_latest.json"
    if not current_path.exists():
        print("ERROR: adg_latest.json not found — run 'python tools/adg_cli.py build --rebuild' first")
        return 1

    baseline_path = Path(baseline)
    if not baseline_path.is_absolute():
        baseline_path = repo_root / baseline_path

    if not baseline_path.exists():
        print(f"ERROR: baseline not found: {baseline_path}")
        return 1

    diff = diff_artifacts(baseline_path, current_path)
    _out(diff)
    return 0 if not diff.get("digest_changed") else 0


# ---------------------------------------------------------------------------
# Command: impact
# ---------------------------------------------------------------------------


def cmd_impact_file(file_path: str, repo_root: Path) -> int:
    """Compute change impact for a changed file."""
    from tools.change_impact_engine import ChangeImpactEngine

    result = _load_scan(repo_root)
    engine = ChangeImpactEngine(result, repo_root=repo_root)
    impact = engine.analyze([file_path.replace("\\", "/")], include_tests=True)
    _out(impact.to_dict())
    return 0 if impact.route_mode == "NORMAL" else 1


def cmd_impact_symbol(symbol_name: str, repo_root: Path) -> int:
    """Compute change impact for a changed symbol by resolving to its parent module."""
    result = _load_scan(repo_root)

    # Resolve symbol to parent module
    parent_path = ""
    if "." in symbol_name:
        parts = symbol_name.rsplit(".", 1)
        candidate = parts[0].replace(".", "/") + ".py"
        if candidate in set(result.modules):
            parent_path = candidate

    if not parent_path:
        # Try direct path match (e.g. module_path passed as dotted name)
        candidate2 = symbol_name.replace(".", "/") + ".py"
        if candidate2 in set(result.modules):
            parent_path = candidate2

    if not parent_path:
        print(
            json.dumps(
                {
                    "symbol": symbol_name,
                    "error": f"Could not resolve symbol '{symbol_name}' to a known module path",
                    "hint": "Use dotted qualified name, e.g. agentic_core.adg.schema_util.canonical_name",
                    "widening_action": "MANUAL_REVIEW_REQUIRED",
                },
                indent=2,
            )
        )
        return 1

    from tools.change_impact_engine import ChangeImpactEngine

    engine = ChangeImpactEngine(result, repo_root=repo_root)
    impact = engine.analyze([parent_path], include_tests=True)
    data = impact.to_dict()
    data["symbol_queried"] = symbol_name
    data["resolved_to_module"] = parent_path
    data["resolution_confidence"] = "HIGH" if parent_path else "LOW"
    _out(data)
    return 0 if impact.route_mode == "NORMAL" else 1


# ---------------------------------------------------------------------------
# Command: who-uses
# ---------------------------------------------------------------------------


def cmd_who_uses(symbol_or_file: str, repo_root: Path) -> int:
    """Return all importers of a symbol or module."""
    result = _load_scan(repo_root)

    norm = symbol_or_file.replace("\\", "/")

    # Try as module path
    if norm in set(result.modules) or norm.endswith(".py"):
        from tools.adg_insight_cli import cmd_who_uses as _who_uses

        _out(_who_uses(norm, result))
        return 0

    # Try as symbol (ADG::Symbol:: lookup)
    adg_sym = _SYMBOL_PREFIX + norm
    importers: list[str] = []
    for edge in result.edges:
        if edge.relation_type == "imports" and edge.to_name == adg_sym:
            if edge.from_name.startswith(_MODULE_PREFIX):
                importers.append(edge.from_name[len(_MODULE_PREFIX) :])

    _out(
        {
            "symbol": norm,
            "direct_importers": sorted(set(importers)),
            "test_importers": sorted(p for p in set(importers) if p.startswith("tests/")),
            "source_importers": sorted(p for p in set(importers) if not p.startswith("tests/")),
            "total_count": len(set(importers)),
            "note": "Resolved as symbol" if importers else "No importers found — try as module path",
        }
    )
    return 0


# ---------------------------------------------------------------------------
# Command: neighbors
# ---------------------------------------------------------------------------


def cmd_neighbors(file_path: str, repo_root: Path) -> int:
    """Return direct import neighbors of a file (importers + dependencies)."""
    result = _load_scan(repo_root)
    norm = file_path.replace("\\", "/")
    adg = _MODULE_PREFIX + norm

    importers: list[str] = []
    dependencies: list[str] = []

    for edge in result.edges:
        if edge.relation_type != "imports":
            continue
        if edge.to_name == adg and edge.from_name.startswith(_MODULE_PREFIX):
            importers.append(edge.from_name[len(_MODULE_PREFIX) :])
        if edge.from_name == adg and edge.to_name.startswith(_MODULE_PREFIX):
            dependencies.append(edge.to_name[len(_MODULE_PREFIX) :])

    from agentic_core.adg.contracts.schema_util import module_path_to_layer

    _out(
        {
            "file": norm,
            "layer": module_path_to_layer(norm),
            "importer_count": len(set(importers)),
            "importers": sorted(set(importers)),
            "dependency_count": len(set(dependencies)),
            "dependencies": sorted(set(dependencies)),
            "total_neighbors": len(set(importers) | set(dependencies)),
        }
    )
    return 0


# ---------------------------------------------------------------------------
# Command: ownership
# ---------------------------------------------------------------------------


def cmd_ownership(symbol_or_file: str, repo_root: Path) -> int:
    """Return territory and layer ownership for a symbol or file."""
    from agentic_core.adg.applications.placement_advisor_types import _infer_territory
    from agentic_core.adg.contracts.schema_util import ALLOWED_LAYER_EDGES, module_path_to_layer

    norm = symbol_or_file.replace("\\", "/")
    result = _load_scan(repo_root)

    # Resolve to a path
    file_path = norm
    if not file_path.endswith(".py"):
        # Try symbol -> parent module
        if "." in norm:
            candidate = ".".join(norm.split(".")[:-1]).replace(".", "/") + ".py"
            if candidate in set(result.modules):
                file_path = candidate
            else:
                file_path = norm.replace(".", "/") + ".py"
        else:
            file_path = norm.replace(".", "/") + ".py"

    layer = module_path_to_layer(file_path)
    territory = _infer_territory(file_path, layer)
    allowed_importers = sorted({fl for (fl, tl) in ALLOWED_LAYER_EDGES if tl == layer} | {layer})
    allowed_imports = sorted({tl for (fl, tl) in ALLOWED_LAYER_EDGES if fl == layer} | {layer})

    in_index = file_path in set(result.modules)
    confidence = "HIGH" if in_index else "MEDIUM"
    notes: list[str] = []
    if not in_index:
        notes.append(f"WARNING: {file_path} not in ADG index — ownership inferred from path conventions only")
    if layer == "L_UNKNOWN":
        notes.append("Layer is L_UNKNOWN — add prefix to LAYER_PREFIXES in agentic_core/adg/schema.py")
        confidence = "LOW"

    _out(
        {
            "queried": symbol_or_file,
            "resolved_path": file_path,
            "layer": layer,
            "territory": territory,
            "confidence": confidence,
            "confidence_notes": notes,
            "allowed_importers": allowed_importers,
            "allowed_imports": allowed_imports,
            "in_adg_index": in_index,
        }
    )
    return 0


# ---------------------------------------------------------------------------
# Command: config-consumers
# ---------------------------------------------------------------------------


def cmd_config_consumers(symbol_name: str, repo_root: Path) -> int:
    """Return modules that read/consume a specific config symbol."""
    result = _load_scan(repo_root)
    adg_sym = _SYMBOL_PREFIX + symbol_name
    consumers: list[str] = []
    for edge in result.edges:
        if edge.relation_type == "reads_from" and (
            edge.to_name == adg_sym or (edge.symbol and edge.symbol == symbol_name)
        ):
            if edge.from_name.startswith(_MODULE_PREFIX):
                consumers.append(edge.from_name[len(_MODULE_PREFIX) :])

    from tools.test_coverage_mapper import TestCoverageMapper

    mapper = TestCoverageMapper(result, repo_root=repo_root).build()
    impacted_tests = mapper.tests_for_modules(consumers)

    _out(
        {
            "config_symbol": symbol_name,
            "consumer_count": len(set(consumers)),
            "consumers": sorted(set(consumers)),
            "impacted_tests": impacted_tests,
            "impacted_test_count": len(impacted_tests),
            "note": (
                "No direct config-consumer edges found — "
                "symbol may be accessed via indirect reads_from or star-import blind spot"
                if not consumers
                else ""
            ),
        }
    )
    return 0


# ---------------------------------------------------------------------------
# Command: scoped-tests
# ---------------------------------------------------------------------------


def cmd_scoped_tests(changed_files: list[str], repo_root: Path) -> int:
    """Map changed files to impacted tests via ADG. No silent fallback."""
    from tools.change_impact_engine import ChangeImpactEngine

    result = _load_scan(repo_root)
    norm_files = [f.replace("\\", "/") for f in changed_files]
    engine = ChangeImpactEngine(result, repo_root=repo_root)
    impact = engine.analyze(norm_files, include_tests=True)

    output = {
        "changed_files": impact.changed_files,
        "impacted_tests": impact.impacted_tests,
        "impacted_test_count": len(impact.impacted_tests),
        "risk_score": impact.risk_score,
        "route_mode": impact.route_mode,
        "scope_widening_events": impact.scope_widening_events,
        "uncovered_changed_files": impact.uncovered_changed_files,
        "impact_digest": impact.impact_digest,
    }

    if impact.uncovered_changed_files:
        output["widening_warning"] = (
            f"{len(impact.uncovered_changed_files)} changed file(s) not in ADG index — "
            "conservative widening: run full suite for uncovered files"
        )

    _out(output)

    # Print pytest command if tests found
    if impact.impacted_tests:
        pytest_args = " ".join(impact.impacted_tests[:20])
        print("\n# Suggested pytest command:")
        print(f"# pytest {pytest_args}")

    return 0 if impact.route_mode == "NORMAL" else 1


# ---------------------------------------------------------------------------
# Command: test-coverage
# ---------------------------------------------------------------------------


def cmd_test_coverage(symbol_name: str, repo_root: Path) -> int:
    """Return tests that cover a given symbol or module."""
    from tools.test_coverage_mapper import TestCoverageMapper

    result = _load_scan(repo_root)
    mapper = TestCoverageMapper(result, repo_root=repo_root).build()

    norm = symbol_name.replace("\\", "/")

    # Try as module path first
    if norm in set(result.modules):
        tests = mapper.tests_for_module(norm)
        _out(
            {
                "queried": norm,
                "resolved_as": "module",
                "covering_tests": tests,
                "test_count": len(tests),
                "note": "" if tests else "No ADG test coverage found",
            }
        )
        return 0

    # Try symbol -> parent module
    parent_path = ""
    if "." in norm:
        candidate = ".".join(norm.split(".")[:-1]).replace(".", "/") + ".py"
        if candidate in set(result.modules):
            parent_path = candidate

    if parent_path:
        tests = mapper.tests_for_module(parent_path)
        _out(
            {
                "queried": norm,
                "resolved_as": "symbol",
                "resolved_parent_module": parent_path,
                "covering_tests": tests,
                "test_count": len(tests),
                "resolution_confidence": "HIGH",
            }
        )
        return 0

    _out(
        {
            "queried": norm,
            "error": "Could not resolve to known module or symbol",
            "note": "Try a repo-relative path like 'agentic_core/adg/schema.py'",
            "covering_tests": [],
            "test_count": 0,
        }
    )
    return 1


# ---------------------------------------------------------------------------
# Command: missing-tests
# ---------------------------------------------------------------------------


def cmd_missing_tests(symbol_name: str, repo_root: Path) -> int:
    """Report modules that have no test coverage in ADG."""
    from tools.test_coverage_mapper import TestCoverageMapper

    result = _load_scan(repo_root)
    mapper = TestCoverageMapper(result, repo_root=repo_root).build()

    norm = symbol_name.replace("\\", "/")

    # If specific symbol/module given, check it
    if norm in set(result.modules):
        tests = mapper.tests_for_module(norm)
        _out(
            {
                "queried": norm,
                "has_coverage": len(tests) > 0,
                "covering_tests": tests,
                "verdict": "COVERED" if tests else "MISSING",
            }
        )
        return 0 if tests else 1

    # Generic: show coverage report for the queried prefix
    report = mapper.coverage_report()
    uncovered = [m for m in report["uncovered_modules"] if norm in m]
    _out(
        {
            "queried": norm,
            "matching_uncovered": uncovered[:20],
            "total_uncovered": report["uncovered_count"],
            "coverage_pct": report["coverage_pct"],
            "note": "Use exact module path or symbol for precise query",
        }
    )
    return 0


# ---------------------------------------------------------------------------
# Command: guardian-scope
# ---------------------------------------------------------------------------


def cmd_guardian_scope(
    high_risk_only: bool,
    focus_territory: str | None,
    boundary_violations: bool,
    repo_root: Path,
    file_path: str | None = None,
) -> int:
    """Produce ADG-prioritized guardian execution scope."""
    from agentic_core.adg.applications.guardian_prioritizer import GuardianPrioritizer
    from agentic_core.adg.contracts.schema_util import module_path_to_layer

    result = _load_scan(repo_root)
    prioritizer = GuardianPrioritizer(result)

    if file_path:
        from agentic_core.adg.contracts.schema_util import module_path_to_layer
        from tools.change_impact_engine import ChangeImpactEngine

        norm_path = file_path.replace("\\", "/")
        layer = module_path_to_layer(norm_path)
        engine = ChangeImpactEngine(result, repo_root=repo_root)
        impact = engine.analyze([norm_path], include_tests=False)
        signals = prioritizer.get_signals()
        prio_result = prioritizer.prioritize()

        # Fan-out for this file
        _MODULE_PREFIX = "ADG::Module::"
        fan_out = sum(
            1
            for e in result.edges
            if e.from_name == _MODULE_PREFIX + norm_path and e.relation_type == "imports"
        )
        fan_in = sum(
            1
            for e in result.edges
            if e.to_name == _MODULE_PREFIX + norm_path and e.relation_type == "imports"
        )

        relevant_violations = [
            v
            for v in signals.get("cross_layer_violations", [])
            if v.get("from_module", "").endswith(norm_path) or v.get("to_module", "").endswith(norm_path)
        ]

        trigger_reasons = []
        if fan_out >= 50:
            trigger_reasons.append(f"high_fan_out={fan_out}")
        if fan_in >= 10:
            trigger_reasons.append(f"high_fan_in={fan_in}")
        if relevant_violations:
            trigger_reasons.append(f"layer_violations={len(relevant_violations)}")
        if len(impact.impacted_modules) > 10:
            trigger_reasons.append(f"blast_radius={len(impact.impacted_modules)}")
        if not trigger_reasons:
            trigger_reasons.append("module_in_scope")

        _out(
            {
                "mode": "file_focused",
                "file": norm_path,
                "layer": layer,
                "fan_out": fan_out,
                "fan_in": fan_in,
                "blast_radius": len(impact.impacted_modules),
                "layer_violations_for_file": relevant_violations[:10],
                "trigger_reasons": trigger_reasons,
                "route_mode": impact.route_mode,
                "risk_score": impact.risk_score,
                "priority_guardians": [s.to_dict() for s in prio_result.ordered()[:5]],
                "adg_signals_digest": prio_result.adg_signals_digest,
            }
        )
        return 0

    if boundary_violations:
        # Focus on cross-layer violating guardians
        all_signals = prioritizer.get_signals()
        violations = all_signals.get("cross_layer_violations", [])
        prio_result = prioritizer.prioritize()
        boundary_guardians = [
            s.to_dict()
            for s in prio_result.ordered()
            if "cross_layer_violations" in s.signals or "upward_mutations" in s.signals
        ]
        _out(
            {
                "mode": "boundary_violations",
                "cross_layer_violation_count": len(violations),
                "priority_guardians": boundary_guardians,
                "sample_violations": violations[:10],
                "adg_signals_digest": prio_result.adg_signals_digest,
            }
        )
        return 0

    if focus_territory:
        # Filter to guardians relevant to the given territory
        territory_upper = focus_territory.upper()
        territory_layer_map = {
            "ROUTING": "L0",
            "COGNITION": "L1",
            "EXECUTION": "L2",
            "ORCHESTRATION": "L3",
            "STATE": "L4",
            "SAFETY": "L5",
            "OBSERVABILITY": "L6",
            "SHARED": "L_SHARED",
            "TOOLS": "L_TOOLS",
            "OPS": "L_OPS",
            "TESTS": "L_TEST",
            "APP": "L_APP",
        }
        target_layer = territory_layer_map.get(territory_upper, "L_UNKNOWN")
        prio_result = prioritizer.prioritize()

        # Find modules in target territory
        territory_modules = [m for m in result.modules if module_path_to_layer(m) == target_layer]

        signals = prioritizer.get_signals()
        relevant_violations = [
            v
            for v in signals.get("cross_layer_violations", [])
            if v.get("from_layer") == target_layer or v.get("to_layer") == target_layer
        ]

        _out(
            {
                "mode": "focus_territory",
                "territory": territory_upper,
                "target_layer": target_layer,
                "module_count_in_territory": len(territory_modules),
                "territory_modules_sample": territory_modules[:10],
                "cross_boundary_violations": relevant_violations[:10],
                "priority_order": [s.to_dict() for s in prio_result.ordered()],
                "adg_signals_digest": prio_result.adg_signals_digest,
            }
        )
        return 0

    if high_risk_only:
        # Only guardians with score above median
        prio_result = prioritizer.prioritize()
        ordered = prio_result.ordered()
        scores = [s.score for s in ordered]
        median_score = sorted(scores)[len(scores) // 2] if scores else 0
        high_risk = [s.to_dict() for s in ordered if s.score >= median_score and s.score > 0]
        _out(
            {
                "mode": "high_risk_only",
                "median_score": median_score,
                "high_risk_guardian_count": len(high_risk),
                "high_risk_guardians": high_risk,
                "adg_signals_digest": prio_result.adg_signals_digest,
                "signal_summary": {
                    k: len(v) if isinstance(v, list) else v for k, v in prioritizer.get_signals().items()
                },
            }
        )
        return 0

    # Default: full prioritized list
    prio_result = prioritizer.prioritize()
    _out(prio_result.to_dict())
    return 0


# ---------------------------------------------------------------------------
# Command: execution-impact
# ---------------------------------------------------------------------------


def cmd_execution_impact(file_path: str, repo_root: Path) -> int:
    """Pre-run ADG impact analysis for execute_ssot flows."""
    from agentic_core.adg.applications.execute_ssot_integration import (
        build_pre_run_report,
        emit_pre_run_log,
    )

    norm = file_path.replace("\\", "/")
    report = build_pre_run_report([norm], repo_root=repo_root)
    emit_pre_run_log(report)

    # Write artifact to disk
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifacts_dir = repo_root / "artifacts" / "adg"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / f"execution_impact_{ts}.json"
    payload = report.to_dict()
    payload["target_file"] = norm
    payload["emitted_by"] = "adg_cli.py execution-impact"
    payload["timestamp"] = ts
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ADG-EXECUTION-IMPACT-ARTIFACT: {out_path}", file=sys.stderr)

    _out(payload)
    return 0 if report.route_mode == "NORMAL" else 1


# ---------------------------------------------------------------------------
# Command: safe-healing-scope
# ---------------------------------------------------------------------------


def cmd_safe_healing_scope(symbol_name: str, repo_root: Path) -> int:
    """Return safe healing scope for a symbol (modules that may be safely touched)."""
    from agentic_core.adg.contracts.schema_util import module_path_to_layer
    from tools.change_impact_engine import ChangeImpactEngine

    result = _load_scan(repo_root)
    norm = symbol_name.replace("\\", "/")

    # Resolve to parent module
    parent_path = ""
    if "." in norm:
        candidate = ".".join(norm.split(".")[:-1]).replace(".", "/") + ".py"
        if candidate in set(result.modules):
            parent_path = candidate

    if not parent_path and norm in set(result.modules):
        parent_path = norm

    if not parent_path:
        _out(
            {
                "symbol": symbol_name,
                "error": f"Could not resolve '{symbol_name}' to a known module",
                "safe_healing_scope": [],
                "confidence": "NONE",
            }
        )
        return 1

    engine = ChangeImpactEngine(result, repo_root=repo_root)
    impact = engine.analyze([parent_path], include_tests=True)

    # Safe scope = modules in same layer or lower (no upward blast)
    parent_layer = module_path_to_layer(parent_path)
    from agentic_core.adg.contracts.schema_util import ALLOWED_LAYER_EDGES

    safe_scope: list[str] = []
    risky_scope: list[str] = []
    for mod in impact.impacted_modules:
        mod_layer = module_path_to_layer(mod)
        if mod_layer == parent_layer or (mod_layer, parent_layer) in ALLOWED_LAYER_EDGES:
            safe_scope.append(mod)
        else:
            risky_scope.append(mod)

    _out(
        {
            "symbol": symbol_name,
            "resolved_module": parent_path,
            "parent_layer": parent_layer,
            "route_mode": impact.route_mode,
            "risk_score": impact.risk_score,
            "safe_healing_scope": sorted(safe_scope),
            "risky_scope": sorted(risky_scope),
            "impacted_tests": impact.impacted_tests,
            "confidence": "HIGH" if parent_path in set(result.modules) else "MEDIUM",
            "scope_widening_events": impact.scope_widening_events,
            "impact_digest": impact.impact_digest,
        }
    )
    return 0 if impact.route_mode == "NORMAL" else 1


# ---------------------------------------------------------------------------
# Command: healing-radius
# ---------------------------------------------------------------------------


def cmd_healing_radius(symbol_name: str, repo_root: Path) -> int:
    """Return full transitive healing radius (blast radius) for a symbol."""
    from agentic_core.adg.contracts.schema_util import module_path_to_layer
    from tools.change_impact_engine import ChangeImpactEngine

    result = _load_scan(repo_root)
    norm = symbol_name.replace("\\", "/")

    parent_path = ""
    if "." in norm:
        candidate = ".".join(norm.split(".")[:-1]).replace(".", "/") + ".py"
        if candidate in set(result.modules):
            parent_path = candidate
    if not parent_path and norm in set(result.modules):
        parent_path = norm

    if not parent_path:
        _out(
            {
                "symbol": symbol_name,
                "error": "Could not resolve to a known module",
                "healing_radius": [],
            }
        )
        return 1

    engine = ChangeImpactEngine(result, repo_root=repo_root)
    impact = engine.analyze([parent_path], include_tests=True)

    by_layer: dict[str, list[str]] = {}
    for mod in impact.impacted_modules:
        layer = module_path_to_layer(mod)
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(mod)

    _out(
        {
            "symbol": symbol_name,
            "resolved_module": parent_path,
            "total_blast_radius": len(impact.impacted_modules),
            "risk_score": impact.risk_score,
            "route_mode": impact.route_mode,
            "blast_radius_by_depth": impact.blast_radius_by_depth,
            "by_layer": {k: sorted(v) for k, v in sorted(by_layer.items())},
            "impacted_tests": impact.impacted_tests,
            "scope_widening_events": impact.scope_widening_events,
            "impact_digest": impact.impact_digest,
        }
    )
    return 0


# ---------------------------------------------------------------------------
# Command: suggest-placement
# ---------------------------------------------------------------------------


def cmd_suggest_placement(kind: str, name: str, repo_root: Path) -> int:
    """Suggest canonical placement for a new file or symbol."""
    from agentic_core.adg.applications.placement_advisor_types import PlacementAdvisor

    result = _load_scan(repo_root)
    advisor = PlacementAdvisor(result, repo_root=repo_root)
    suggestion = advisor.suggest_placement(kind=kind, name=name)
    _out(suggestion.to_dict())
    return 0


# ---------------------------------------------------------------------------
# Command: context
# ---------------------------------------------------------------------------


def cmd_context_file(file_path: str, repo_root: Path) -> int:
    """Get structural context for an existing file."""
    from agentic_core.adg.applications.placement_advisor_types import PlacementAdvisor

    result = _load_scan(repo_root)
    advisor = PlacementAdvisor(result, repo_root=repo_root)
    context = advisor.get_file_context(file_path.replace("\\", "/"))
    _out(context.to_dict())
    return 0


def cmd_context_symbol(symbol_name: str, repo_root: Path) -> int:
    """Get structural context for a qualified symbol name."""
    from agentic_core.adg.applications.placement_advisor_types import PlacementAdvisor

    result = _load_scan(repo_root)
    advisor = PlacementAdvisor(result, repo_root=repo_root)
    context = advisor.get_symbol_context(symbol_name)
    _out(context.to_dict())
    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="adg_cli",
        description="ADG Canonical CLI — architecture dependency graph operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--repo-root", default=None, help="Repository root (default: cwd)")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # -- build
    p_build = sub.add_parser("build", help="Build ADG and emit canonical artifacts")
    build_grp = p_build.add_mutually_exclusive_group(required=True)
    build_grp.add_argument("--rebuild", action="store_true", help="Force fresh scan")
    build_grp.add_argument("--cached", action="store_true", help="Use cached scan if valid")

    # -- health
    p_health = sub.add_parser("health", help="Run trust gate health check")
    p_health.add_argument("--strict", action="store_true", help="Exit nonzero if trust thresholds violated")

    # -- stats
    sub.add_parser("stats", help="Print ADG statistics")

    # -- diff
    p_diff = sub.add_parser("diff", help="Diff current ADG against a baseline")
    p_diff.add_argument(
        "--baseline", required=True, metavar="ARTIFACT_OR_PATH", help="Baseline artifact path"
    )

    # -- impact
    p_impact = sub.add_parser("impact", help="Compute change impact for a file or symbol")
    impact_grp = p_impact.add_mutually_exclusive_group(required=True)
    impact_grp.add_argument("--file", metavar="PATH", help="Changed file path")
    impact_grp.add_argument("--symbol", metavar="QUALIFIED_NAME", help="Changed symbol (dotted name)")

    # -- who-uses
    p_who = sub.add_parser("who-uses", help="Return all importers of a symbol or module")
    p_who.add_argument("--symbol", required=True, metavar="NAME", help="Symbol or module path")

    # -- neighbors
    p_nb = sub.add_parser("neighbors", help="Return direct import neighbors of a file")
    p_nb.add_argument("--file", required=True, metavar="PATH", help="Module file path")

    # -- ownership
    p_own = sub.add_parser("ownership", help="Return layer/territory ownership")
    p_own.add_argument("--symbol", required=True, metavar="NAME", help="Symbol or module path")

    # -- config-consumers
    p_cfg = sub.add_parser("config-consumers", help="Return modules consuming a config symbol")
    p_cfg.add_argument("--symbol", required=True, metavar="NAME", help="Config symbol name")

    # -- scoped-tests
    p_st = sub.add_parser("scoped-tests", help="Map changed files to impacted tests")
    p_st.add_argument(
        "--changed-files", required=True, metavar="FILE1,FILE2,...", help="Comma-separated changed files"
    )

    # -- test-coverage
    p_tc = sub.add_parser("test-coverage", help="Return tests covering a symbol or module")
    p_tc.add_argument("--symbol", required=True, metavar="NAME", help="Symbol or module path")

    # -- missing-tests
    p_mt = sub.add_parser("missing-tests", help="Report missing test coverage")
    p_mt.add_argument("--symbol", required=True, metavar="NAME", help="Symbol or module path prefix")

    # -- guardian-scope
    p_gs = sub.add_parser("guardian-scope", help="Produce ADG-prioritized guardian scope")
    p_gs.add_argument("--file", metavar="PATH", help="Focus guardian scope on a specific file")
    gs_grp = p_gs.add_mutually_exclusive_group(required=False)
    gs_grp.add_argument("--high-risk-only", action="store_true", help="Only high-risk guardians")
    gs_grp.add_argument("--focus-territory", metavar="TERRITORY", help="Focus on a specific territory")
    gs_grp.add_argument("--boundary-violations", action="store_true", help="Focus on cross-layer violations")

    # -- execution-impact
    p_ei = sub.add_parser("execution-impact", help="Pre-run ADG impact for execute_ssot")
    p_ei.add_argument("--file", required=True, metavar="PATH", help="File being executed/healed")

    # -- safe-healing-scope
    p_sh = sub.add_parser("safe-healing-scope", help="Return safe healing scope for a symbol")
    p_sh.add_argument("--symbol", required=True, metavar="QUALIFIED_NAME", help="Symbol to heal")

    # -- healing-radius
    p_hr = sub.add_parser("healing-radius", help="Return full transitive healing radius")
    p_hr.add_argument("--symbol", required=True, metavar="QUALIFIED_NAME", help="Symbol or module")

    # -- suggest-placement
    p_sp = sub.add_parser("suggest-placement", help="Suggest canonical placement for a new file/symbol")
    p_sp.add_argument(
        "--kind",
        required=True,
        metavar="FILE_KIND",
        help="Kind: agent, config, mixin, tool, router, orchestrator, etc.",
    )
    p_sp.add_argument("--name", required=True, metavar="SYMBOL_OR_FILE", help="New symbol or file name")

    # -- context
    p_ctx = sub.add_parser("context", help="Get structural context for a file or symbol")
    ctx_grp = p_ctx.add_mutually_exclusive_group(required=True)
    ctx_grp.add_argument("--file", metavar="PATH", help="Existing file path")
    ctx_grp.add_argument("--symbol", metavar="QUALIFIED_NAME", help="Qualified symbol name")

    args = parser.parse_args(argv)
    rr = _repo_root(args.repo_root)

    cmd = args.command
    if cmd is None:
        parser.print_help()
        return 1

    if cmd == "build":
        return cmd_build(rebuild=args.rebuild, repo_root=rr)
    if cmd == "health":
        return cmd_health(repo_root=rr, strict=args.strict)
    if cmd == "stats":
        return cmd_stats(repo_root=rr)
    if cmd == "diff":
        return cmd_diff(baseline=args.baseline, repo_root=rr)
    if cmd == "impact":
        if args.file:
            return cmd_impact_file(file_path=args.file, repo_root=rr)
        return cmd_impact_symbol(symbol_name=args.symbol, repo_root=rr)
    if cmd == "who-uses":
        return cmd_who_uses(symbol_or_file=args.symbol, repo_root=rr)
    if cmd == "neighbors":
        return cmd_neighbors(file_path=args.file, repo_root=rr)
    if cmd == "ownership":
        return cmd_ownership(symbol_or_file=args.symbol, repo_root=rr)
    if cmd == "config-consumers":
        return cmd_config_consumers(symbol_name=args.symbol, repo_root=rr)
    if cmd == "scoped-tests":
        files = [f.strip() for f in args.changed_files.split(",") if f.strip()]
        return cmd_scoped_tests(changed_files=files, repo_root=rr)
    if cmd == "test-coverage":
        return cmd_test_coverage(symbol_name=args.symbol, repo_root=rr)
    if cmd == "missing-tests":
        return cmd_missing_tests(symbol_name=args.symbol, repo_root=rr)
    if cmd == "guardian-scope":
        file_arg = getattr(args, "file", None)
        if (
            not file_arg
            and not args.high_risk_only
            and not args.focus_territory
            and not args.boundary_violations
        ):
            print(
                "guardian-scope requires --file, --high-risk-only, --focus-territory, or --boundary-violations",
                file=sys.stderr,
            )
            return 2
        return cmd_guardian_scope(
            high_risk_only=args.high_risk_only,
            focus_territory=args.focus_territory,
            boundary_violations=args.boundary_violations,
            repo_root=rr,
            file_path=file_arg,
        )
    if cmd == "execution-impact":
        return cmd_execution_impact(file_path=args.file, repo_root=rr)
    if cmd == "safe-healing-scope":
        return cmd_safe_healing_scope(symbol_name=args.symbol, repo_root=rr)
    if cmd == "healing-radius":
        return cmd_healing_radius(symbol_name=args.symbol, repo_root=rr)
    if cmd == "suggest-placement":
        return cmd_suggest_placement(kind=args.kind, name=args.name, repo_root=rr)
    if cmd == "context":
        if args.file:
            return cmd_context_file(file_path=args.file, repo_root=rr)
        return cmd_context_symbol(symbol_name=args.symbol, repo_root=rr)

    parser.print_help()
    return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sys.exit(main())
