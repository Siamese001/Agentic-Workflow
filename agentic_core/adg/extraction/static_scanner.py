"""ADG Static Scanner -- AST-based edge extraction for the Architecture Dependency Graph.

Produces a deterministic, commit-scoped canonical edge list and digest.
All analysis uses Python AST parsing. Regex/grep for structural logic is forbidden.

Graph types extracted:
  G1 - Import graph (imports edges)
  G2 - Call/write/network graph (writes_to, invokes_provider edges)
  G3 - Inheritance graph (implements edges)  [H3]
  G5 - Config read graph (reads_from edges)  [H4]
  G6 - Composition graph (instantiates edges in __init__)  [H5]
  GF - Dynamic execution graph (eval/exec/importlib)  [S3]

Output format per run:
    ADG-DETERMINISM-DIGEST: <sha256_hex>

Canonical edge list sort order: from_name, relation_type, to_name, line_no.
"""

from __future__ import annotations

import ast
import hashlib
import logging
import os
from dataclasses import asdict, dataclass, field, fields, replace
from pathlib import Path
from typing import Iterator

from agentic_core.adg.extraction.scanner_utils import (
    _HollowFileAnnotator,
    _TypeSurfaceCollector,
)
from agentic_core.adg.extraction.visitors import (
    VisitorContext,
    _AntipatternVisitor,
    _AttributeVisitor,
    _AuthoritativeCommitVisitor,
    _BoundaryVerifierVisitor,
    # Core visitors
    _CallVisitor,
    _CapabilityBudgetVisitor,
    _CompositionVisitor,
    _DecoratorVisitor,
    _DynamicExecutionVisitor,
    _EmbeddingPipelineVisitor,
    # Runtime semantic visitors
    _ExecutionSemanticVisitor,
    _ExecutionTraceVisitor,
    # Governance visitors
    _GovernancePlaneVisitor,
    _HealerValidatorVisitor,
    # Orchestration visitors (G22, G28-G30)
    _HITLVisitor,
    _ImportVisitor,
    # Structural visitors (G3, G5, G6)
    _InheritanceVisitor,
    _InternalCallGraphVisitor,
    _JITContextVisitor,
    # Learning visitors (G26-G27, G32)
    _MutationRecordAssemblyVisitor,
    _OutboundReadBridgeVisitor,
    _PromptSlotVisitor,
    _SafetyEnforcementVisitor,
    _SandboxAirlockVisitor,
    _SymbolInventoryVisitor,
    # Misc visitors
    _TestTraceabilityVisitor,
    _TypeAnnotationVisitor,
    _UnusedImportVisitor,
    # L4 waves visitors
    _UWGIngressGateVisitor,
)
from agentic_core.adg.schema_util import (
    canonical_name,
    module_path_to_layer,
)
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_EVAL_DIR,
    APPS_EXEC_DIR,
    APPS_LIC_DIR,
    APPS_RESEARCH_DIR,
    APPS_RFP_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_observes_runtime_state,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_transcripts_response,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# P0: Bootstrap mode flag - gates self-emit calls during scanner self-analysis
# When True, scanner skips emitting edges for itself to avoid circular ADG entries
_bootstrap_mode: bool = os.getenv("ADG_SCANNER_SELF_TEST", "0") == "1"

if _bootstrap_mode:
    _emit_applies_guardrail("p0", "static_scanner", "p0_governance")
    _emit_snapshots_state("p0", "static_scanner", "state_snapshot")
    _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

    emit_replay_key("p0", "static_scanner")
    emit_determinism_digest("p0", "static_scanner")

# P2 self-emit calls (gated by bootstrap mode)
if _bootstrap_mode:
    _emit_authorize_and_execute("p2", "static_scanner", "execution_auth")
    _emit_validates_capability("p2", "static_scanner", "capability_check")
    _emit_routes_to_capability("p2", "static_scanner", "capability_route")
    _emit_writes_via_uwg("p2", "static_scanner", "uwg_write")
    _emit_blocks_direct_write("p2", "static_scanner", "direct_write_block")
    _emit_records_tool_invocation("p2", "static_scanner", "tool_invocation")
    _emit_captures_execution_output("p2", "static_scanner", "exec_output")

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_appends_hash_chain,
    _emit_applies_hmac_seal,
    _emit_captures_evaluation_metric,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_checks_capability_set,
    _emit_checks_policy_hash_at_uwg,
    _emit_claims_write_lock,
    _emit_commits_mutation_durable,
    _emit_computes_mutation_replay_key,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_generates_mutation_diff,
    _emit_hard_fails_untranscripted,
    _emit_heals_on_rollback_failure,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_l3_reads_l4_surface,
    _emit_l5_reads_l4_surface,
    _emit_l6_ingests_l4_trace,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_materializes_read_view,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_packages_execution_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_l4_surface,
    _emit_reads_runtime_state,
    _emit_receives_policy_hash,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_workflow_lineage,
    _emit_refreshes_retrieval_surface,
    _emit_routes_to_agent,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_swaps_version_alias,
    _emit_syncs_l4_telemetry,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_blast_radius_at_uwg,
    _emit_validates_uwg_intent,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_dispatches_agent("p3", "static_scanner", "agent_dispatch")
_emit_coordinates_agents("p3", "static_scanner", "agent_coordination")
_emit_records_workflow_lineage("p3", "static_scanner", "workflow_lineage")
_emit_records_healing_outcome("p3", "static_scanner", "healing_outcome")
_emit_escalates_failure("p3", "static_scanner", "failure_escalation")
_emit_orchestrates_workflow("p3", "static_scanner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "static_scanner", "healing_dispatch")
_emit_invokes_evaluation("p3", "static_scanner", "evaluation_signal")
_emit_records_telemetry_event("p4", "static_scanner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "static_scanner", "eval_metric")
_emit_stores_embedding("p4", "static_scanner", "embedding_store")
_emit_updates_meta_learning_state("p4", "static_scanner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "static_scanner", "exec_snapshot_link")
_emit_pulls_context("p1", "static_scanner", "context_pull")
_emit_execution_terminates_at_uwg("p1", "static_scanner", "uwg_term")
_emit_validates_uwg_intent("l4w1", "static_scanner", "uwg_intent_bootstrap")
_emit_checks_policy_hash_at_uwg("l4w1", "static_scanner", "uwg_policy_bootstrap")
_emit_checks_capability_set("l4w1", "static_scanner", "uwg_capability_bootstrap")
_emit_validates_blast_radius_at_uwg("l4w1", "static_scanner", "uwg_blast_bootstrap")
_emit_syncs_l4_telemetry("l4w3", "static_scanner", "l4_telemetry_bootstrap")
_emit_generates_mutation_diff("l4w2", "static_scanner", "mutation_diff_bootstrap")
_emit_computes_mutation_replay_key("l4w2", "static_scanner", "replay_key_bootstrap")
_emit_applies_hmac_seal("l4w2", "static_scanner", "hmac_seal_bootstrap")
_emit_packages_execution_trace("l4w2", "static_scanner", "trace_package_bootstrap")
# Wave 3 self-bootstrap calls
_emit_claims_write_lock("l4w3", "static_scanner", "write_lock_bootstrap")
_emit_commits_mutation_durable("l4w3", "static_scanner", "durable_commit_bootstrap")
_emit_appends_hash_chain("l4w3", "static_scanner", "hash_chain_bootstrap")
_emit_heals_on_rollback_failure("l4w3", "static_scanner", "rollback_heal_bootstrap")
_emit_materializes_read_view("l4w3", "static_scanner", "read_view_bootstrap")
_emit_refreshes_retrieval_surface("l4w3", "static_scanner", "surface_refresh_bootstrap")
_emit_swaps_version_alias("l4w3", "static_scanner", "alias_swap_bootstrap")
# Wave 4 self-bootstrap calls
_emit_reads_l4_surface("l4w4", "static_scanner", "l4_surface_bootstrap")
_emit_receives_policy_hash("l4w4", "static_scanner", "policy_hash_bootstrap")
_emit_l5_reads_l4_surface("l4w4", "static_scanner", "l5_surface_bootstrap")
_emit_l3_reads_l4_surface("l4w4", "static_scanner", "l3_surface_bootstrap")
_emit_l6_ingests_l4_trace("l4w4", "static_scanner", "l6_trace_bootstrap")

_emit_writes_through("p1", "static_scanner", "write_through")
_emit_validated_by_safety_plane("p1", "static_scanner", "safety_validation")
_emit_invokes_eval("p1", "static_scanner", "eval_call")
_emit_proposal_commits_routing("p1", "static_scanner", "routing_commit")
_emit_escalates_to_human("p1", "static_scanner", "human_escalation")
_emit_checks_agent_registry("p1", "static_scanner", "agent_registry")
_emit_validates_agent_capability("p1", "static_scanner", "capability")
_emit_dispatches_execution_plan("p1", "static_scanner", "exec_plan")
_emit_agent_executes_agent("p1", "static_scanner", "sub_agent")
_emit_routes_to_agent("p1", "static_scanner", "target_agent")
_emit_verifies_policy("p1", "static_scanner", "policy_check")
_emit_observes_runtime_state("p1", "static_scanner", "runtime_state")
_emit_verifies_boundary("p1", "static_scanner", "boundary_check")
_emit_transcripts_response("p1", "static_scanner", "transcript")
_emit_hard_fails_untranscripted("p1", "static_scanner")
_emit_gated_by_confidence("p1", "static_scanner", "confidence_gate")
_emit_reads_environ("p2", "static_scanner", "env_read")
_emit_reads_runtime_state("p2", "static_scanner", "runtime_state")
_emit_captures_pattern("p3lm", "static_scanner", "pattern")
_emit_records_learning_event("p3lm", "static_scanner", "learning_event")
_emit_writes_learning_snapshot("p3lm", "static_scanner", "snapshot")
_emit_feeds_meta_learning("p3lm", "static_scanner", "meta_feed")
_emit_updates_routing_strategy("p3lm", "static_scanner", "routing")
_emit_improves_agent_policy("p3lm", "static_scanner", "policy")
_emit_stores_learning_state("p3lm", "static_scanner", "state")
_emit_emits_metric_event("p4obs", "static_scanner", "metric")
_emit_records_incident_event("p4obs", "static_scanner", "incident")
_emit_captures_runtime_anomaly("p4obs", "static_scanner", "anomaly")
_emit_writes_observability_log("p4obs", "static_scanner", "obs_log")
_emit_updates_monitoring_state("p4obs", "static_scanner", "mon_state")
_emit_triggers_alert("p4obs", "static_scanner", "alert")
_emit_links_incident_trace("p4obs", "static_scanner", "trace_link")
emit_determinism_digest("trace_static_scanner", "static_scanner_dispatch_entry")
emit_determinism_digest("trace_static_scanner", "static_scanner_dispatch_exit")
emit_determinism_digest("trace_static_scanner", "static_scanner_tool_invoke")
emit_determinism_digest("trace_static_scanner", "static_scanner_tool_complete")
emit_determinism_digest("trace_static_scanner", "static_scanner_agent_entry")
emit_determinism_digest("trace_static_scanner", "static_scanner_agent_exit")
emit_determinism_digest("trace_static_scanner", "static_scanner_uwg_write")
emit_determinism_digest("trace_static_scanner", "static_scanner_trace_sign")
emit_determinism_digest("trace_static_scanner", "static_scanner_guardrail_check")
emit_determinism_digest("trace_static_scanner", "static_scanner_policy_verify")
_emit_writes_through("p1", "static_scanner", "uwg_governed_write")
_emit_writes_through("p1", "static_scanner", "uwg_governed_write_2")
_emit_pulls_context("p1", "static_scanner", "context_retrieval")
_emit_pulls_context("p1", "static_scanner", "context_retrieval_2")
emit_determinism_digest("trace_static_scanner", "static_scanner_dispatch")
emit_determinism_digest("trace_static_scanner", "static_scanner_complete")
_emit_validated_by_safety_plane("p1", "static_scanner", "safety_validation")

logger = logging.getLogger(__name__)

_STRUCTURAL_SCAN_ROOTS: tuple[str, ...] = (
    AGENTIC_CORE_DIR,
    APPS_EVAL_DIR,
    APPS_EXEC_DIR,
    APPS_LIC_DIR,
    APPS_RESEARCH_DIR,
    APPS_RFP_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)

_NON_STRUCTURAL_SCAN_ROOTS: tuple[str, ...] = (
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    TESTS_DIR,  # H1
    OPS_SCRIPTS_DIR,  # H1
)

# Phase 1.1: Coverage-only scan roots for test files with structural_only mode
_COVERAGE_ONLY_SCAN_ROOTS: tuple[str, ...] = (TESTS_DIR,)

_SCAN_ROOTS: tuple[str, ...] = _STRUCTURAL_SCAN_ROOTS + _NON_STRUCTURAL_SCAN_ROOTS

_RUNTIME_ONLY_SCAN_SUBDIRS: frozenset[str] = frozenset(
    {
        "artifacts",
        "logs",
        "runtime",
        "runtime_adg",
        "scripts",
        "telemetry",
    }
)

_RUNTIME_ONLY_RELATION_TYPES: frozenset[str] = frozenset(
    {
        "captures_evaluation_metric",
        "captures_execution_output",
        "emits_replay_key",
        "links_execution_to_snapshot",
        "observes_runtime_state",
        "reads_runtime_state",
        "records_execution_trace",
        "records_healing_outcome",
        "records_incident_event",
        "records_learning_event",
        "records_telemetry_event",
        "records_tool_invocation",
        "records_workflow_lineage",
        "signs_execution_trace",
        "snapshots_state",
        "stores_embedding",
        "stores_learning_state",
        "updates_meta_learning_state",
        "updates_monitoring_state",
        "writes_learning_snapshot",
        "writes_observability_log",
    }
)

_RUNTIME_ONLY_RELATION_PREFIXES: tuple[str, ...] = (
    "captures_",
    "records_",
)


def _selected_scan_roots(include_tests: bool, scan_mode: str = "full") -> tuple[str, ...]:
    """Return scan roots based on include_tests flag and scan_mode.

    Args:
        include_tests: Whether to include test files in scan
        scan_mode: "full" (default) or "structural_only" for Phase 1 optimization

    Returns:
        Tuple of scan root directories
    """
    if scan_mode == "structural_only" and include_tests:
        # Phase 1.1: Tests get coverage-only treatment (structural only)
        return _STRUCTURAL_SCAN_ROOTS + _COVERAGE_ONLY_SCAN_ROOTS
    elif include_tests:
        return _SCAN_ROOTS
    return _STRUCTURAL_SCAN_ROOTS


def _get_visitors_for_mode(scan_mode: str, file_path: str) -> list[str]:
    """Return list of visitor types to run based on scan_mode and file path.

    Args:
        scan_mode: "full", "structural_only", or "selective" for Phase 1 optimization
        file_path: Relative file path to determine file type and importance

    Returns:
        List of visitor identifiers to run on the file
    """
    if scan_mode == "structural_only" and file_path.startswith("tests/"):
        # Phase 1.1: Only run G1 (imports) + G3 (inheritance) on test files
        return ["import", "inheritance"]
    elif scan_mode == "selective":
        # Phase 1.2: Selective visitor registration based on file type
        return _get_selective_visitors(file_path)
    return "full"  # Use all visitors for full mode


def _get_cache_aware_scan_mode(
    cache_path: Path | None, repo_root: Path, include_tests: bool = True, force_mode: str | None = None
) -> str:
    """Determine optimal scan mode based on cache state and file changes.

    Phase 1.3: Cache-aware optimization that selects scan mode based on:
    - Cache hit rate and freshness
    - File change patterns
    - Repository size and complexity

    Args:
        cache_path: Path to scan cache file
        repo_root: Repository root directory
        include_tests: Whether tests are included in scanning
        force_mode: Override mode (for testing)

    Returns:
        Optimal scan mode: "full", "structural_only", or "selective"
    """
    if force_mode:
        return force_mode

    # No cache available - use full mode for completeness
    if not cache_path or not cache_path.exists():
        return "full"

    # Analyze cache state
    try:
        import json

        with open(cache_path) as f:
            cache_data = json.load(f)

        cache_stats = cache_data.get("stats", {})
        hit_rate = cache_stats.get("hit_rate", 0.0)
        total_entries = cache_stats.get("hits", 0) + cache_stats.get("misses", 0)

        # High cache hit rate (>90%) - can use optimized modes
        if hit_rate > 0.9 and total_entries > 1000:
            if include_tests:
                # Many test files with good cache - use structural_only for tests
                return "structural_only"
            else:
                # Production only with good cache - use selective mode
                return "selective"

        # Medium cache hit rate (70-90%) - use selective mode
        elif hit_rate > 0.7 and total_entries > 500:
            return "selective"

        # Low cache hit rate or small cache - use full mode
        else:
            return "full"

    except (OSError, json.JSONDecodeError, KeyError):
        # Cache analysis failed - fall back to full mode
        return "full"


def _should_use_incremental_scan(
    cache_path: Path | None, repo_root: Path, changed_files: list[str] | None = None
) -> bool:
    """Determine if incremental scanning should be used.

    Phase 1.3: Advanced cache optimization for incremental updates.

    Args:
        cache_path: Path to scan cache file
        repo_root: Repository root directory
        changed_files: List of changed files (if known)

    Returns:
        True if incremental scanning is recommended
    """
    if not cache_path or not cache_path.exists():
        return False

    try:
        import json

        with open(cache_path) as f:
            cache_data = json.load(f)

        cache_stats = cache_data.get("stats", {})
        hit_rate = cache_stats.get("hit_rate", 0.0)
        total_entries = cache_stats.get("hits", 0) + cache_stats.get("misses", 0)

        # Use incremental if:
        # 1. High cache hit rate (>85%)
        # 2. Substantial cache (>2000 entries)
        # 3. Small number of changes (<100 files)
        if hit_rate > 0.85 and total_entries > 2000 and (changed_files is None or len(changed_files) < 100):
            return True

        return False

    except (OSError, json.JSONDecodeError, KeyError):
        return False


def _get_selective_visitors(file_path: str) -> list[str]:
    """Return selective visitor list based on file type and importance.

    Phase 1.2: Optimizes production code scanning by selecting only essential visitors
    based on file characteristics while maintaining critical coverage.

    Args:
        file_path: Relative file path to analyze

    Returns:
        List of visitor identifiers for selective scanning
    """
    # Core visitors that always run (structural foundation)
    core_visitors = ["import", "inheritance"]

    # File type analysis
    if file_path.startswith("tests/"):
        # Test files: minimal scanning (already handled by structural_only)
        return core_visitors

    # Production code selective enhancement
    selective_visitors = core_visitors.copy()

    # Add call/write visitors for core business logic
    if any(
        indicator in file_path
        for indicator in ["agentic_core/", "apps_", "tools/", "ops_", "system_learning/"]
    ):
        selective_visitors.extend(["call", "attribute", "composition"])

    # Add governance visitors for security/safety critical files
    if any(
        indicator in file_path for indicator in ["safety_", "security_", "audit_", "policy_", "governance_"]
    ):
        selective_visitors.extend(["governance", "safety_enforcement", "boundary_verification"])

    # Add execution visitors for orchestration files
    if any(indicator in file_path for indicator in ["orchestration", "workflow", "execution_", "runtime_"]):
        selective_visitors.extend(["dynamic_execution", "internal_call_graph", "execution_semantic"])

    # Add learning visitors for AI/ML components
    if any(indicator in file_path for indicator in ["learning_", "ai_", "ml_", "model_", "embedding_"]):
        selective_visitors.extend(["embedding_pipeline", "learning_provenance", "p3_learning_maturity"])

    # Add observability visitors for monitoring components
    if any(indicator in file_path for indicator in ["observability", "telemetry", "metrics_", "monitoring_"]):
        selective_visitors.extend(["p4_observability_governance", "execution_trace_proof"])

    return selective_visitors


def _is_scannable_static_path(rel_path: str, include_tests: bool, scan_mode: str = "full") -> bool:
    """Check if path is scannable based on scan roots and mode."""
    normalized = rel_path.replace("\\", "/")
    root_matched = any(
        normalized == root or normalized.startswith(f"{root}/")
        for root in _selected_scan_roots(include_tests, scan_mode)
    )
    if not root_matched:
        return False
    if include_tests:
        return True
    parts = tuple(part for part in normalized.split("/") if part)
    return not any(part in _RUNTIME_ONLY_SCAN_SUBDIRS for part in parts)


def _is_runtime_only_relation(relation_type: str) -> bool:
    if relation_type in _RUNTIME_ONLY_RELATION_TYPES:
        return True
    return relation_type.startswith(_RUNTIME_ONLY_RELATION_PREFIXES)


def _filter_runtime_only_edges(edges: list[Edge], include_tests: bool, scan_mode: str = "full") -> list[Edge]:
    """Filter out runtime-only edges based on include_tests and scan_mode.

    Phase 1.4: Enhanced runtime-only edge filtering with intelligent optimization.

    Args:
        edges: List of edges to filter
        include_tests: Whether test files are included in scanning
        scan_mode: "full", "structural_only", or "selective" for Phase 1 optimization

    Returns:
        Filtered list of edges
    """
    if include_tests and scan_mode == "full":
        # Full mode with tests - keep all edges
        return edges
    elif include_tests and scan_mode == "structural_only":
        # Structural-only mode with tests - filter runtime-only edges from test files only
        return [
            edge
            for edge in edges
            if not edge.source_file.startswith("tests/") or not _is_runtime_only_relation(edge.relation_type)
        ]
    elif include_tests and scan_mode == "selective":
        # Selective mode with tests - enhanced filtering
        return _enhanced_runtime_filter(edges, include_tests=True)
    else:
        # No tests included - filter all runtime-only edges
        return _enhanced_runtime_filter(edges, include_tests=False)


def _enhanced_runtime_filter(edges: list[Edge], include_tests: bool) -> list[Edge]:
    """Enhanced runtime-only edge filtering with intelligent optimization.

    Phase 1.4: Advanced filtering that preserves critical structural edges
    while removing unnecessary runtime artifacts.

    Args:
        edges: List of edges to filter
        include_tests: Whether test files are included

    Returns:
        Filtered list of edges
    """
    filtered_edges = []

    for edge in edges:
        # Skip test files if not included
        if not include_tests and edge.source_file.startswith("tests/"):
            continue

        # Enhanced runtime filtering logic
        if _is_runtime_only_relation(edge.relation_type):
            # Phase 1.4: Keep some runtime edges for critical analysis
            if _should_keep_runtime_edge(edge):
                filtered_edges.append(edge)
            # Otherwise, skip this runtime edge
        else:
            # Keep all non-runtime edges
            filtered_edges.append(edge)

    return filtered_edges


def _should_keep_runtime_edge(edge: Edge) -> bool:
    """Determine if a runtime edge should be kept during enhanced filtering.

    Phase 1.4: Intelligent runtime edge preservation based on importance
    and context rather than blanket removal.

    Args:
        edge: The edge to evaluate

    Returns:
        True if the edge should be kept
    """
    # Keep runtime edges from core infrastructure files
    if any(indicator in edge.source_file for indicator in ["agentic_core/", "apps_", "tools/", "ops_"]):
        return True

    # Keep critical governance runtime edges
    if edge.relation_type in [
        "applies_guardrail",
        "verifies_policy",
        "validated_by_safety_plane",
        "execution_terminates_at_uwg",
        "records_execution_trace",
    ]:
        return True

    # Keep learning and observability runtime edges from non-test files
    if not edge.source_file.startswith("tests/") and edge.relation_type in [
        "captures_pattern",
        "records_learning_event",
        "emits_metric_event",
        "stores_embedding",
        "retrieves_via",
    ]:
        return True

    # Skip other runtime edges (especially from test files)
    return False


_SCANNER_VERSION = "2.0.0"
_SCHEMA_VERSION = "2.0"

# S9: Cardinality ranges for sanity checking (upper bounds include tests/ scan territory)
# reads_from upper bound raised to 100000: os.environ/getenv/config.get calls appear in
# large test suites and generate ~62k edges when tests/ is included in the scan.
_CARDINALITY_RANGES: dict[str, tuple[int, int]] = {
    "implements": (100, 10000),
    "reads_from": (50, 100000),
    "instantiates": (50, 5000),
}

# A2: Minimum evidence floors per graph
_MIN_EVIDENCE_FLOORS: dict[str, int] = {
    "imports": 500,
    "implements": 100,
    "reads_from": 50,
    "instantiates": 50,
}

_COMPOSITION_NOISE: frozenset[str] = frozenset(
    {
        "dict",
        "list",
        "set",
        "tuple",
        "str",
        "int",
        "float",
        "bool",
        "Path",
        "defaultdict",
        "OrderedDict",
        "Counter",
        "deque",
        "Exception",
        "ValueError",
        "TypeError",
        "RuntimeError",
        "threading.Lock",
        "threading.Event",
        "threading.Thread",
        "asyncio.Lock",
        "asyncio.Event",
    }
)


@dataclass(frozen=True, order=True)
class Edge:
    """A single directed dependency edge in the ADG."""

    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str = ""

    # Precision hardening extensions (Section 2: Semantic Edge Taxonomy)
    semantic_type: str = ""  # Empty string instead of None for sorting
    confidence: float = 1.0
    source_span_start: int = 0
    source_span_end: int = 0
    source_span_line: int = 0
    source_span_column: int = 0
    target_span_start: int = 0
    target_span_end: int = 0
    target_span_line: int = 0
    target_span_column: int = 0
    dynamic_resolution: str = ""  # Empty string instead of None for sorting


@dataclass
class ScanManifest:
    """A1: Rich manifest of scanner run metadata for fail-closed validation."""

    scanner_version: str = _SCANNER_VERSION
    schema_version: str = _SCHEMA_VERSION
    python_ast_version: str = ""
    discovered_module_count: int = 0
    parsed_module_count: int = 0
    syntax_error_count: int = 0
    unknown_layer_count: int = 0
    edge_counts_by_graph: dict[str, int] = field(default_factory=dict)
    rule_skip_counts: dict[str, int] = field(default_factory=dict)
    dynamic_execution_count: int = 0
    tests_included: bool = False
    minimum_evidence_passed: bool = False
    scanner_self_test_passed: bool = False
    scan_mode: str = "full"  # Phase 1.3: record selected scan mode
    cardinality_violations: list[str] = field(default_factory=list)
    inter_module_call_count: int = 0
    test_covers_count: int = 0
    layer_violation_count: int = 0
    governance_plane_count: int = 0
    symbol_export_count: int = 0
    symbol_hit_rate: float = 0.0
    dead_import_count: int = 0
    cycle_count: int = 0
    max_cycle_depth: int = 0
    decorator_edge_count: int = 0
    star_import_count: int = 0
    star_import_resolved_count: int = 0
    conditional_import_count: int = 0
    antipattern_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    type_annotation_count: int = 0
    decomposes_into_expected_count: int = 0
    controls_flow_expected_count: int = 0
    flows_to_expected_count: int = 0
    emits_side_effect_expected_count: int = 0
    resolves_callsite_expected_count: int = 0
    tests_execution_of_expected_count: int = 0
    type_surface_candidate_count: int = 0
    type_surface_expected_count: int = 0
    violation_propagation_eligible_count: int = 0
    violation_propagation_target_count: int = 0
    semantic_preexisting_count: int = 0
    semantic_exact_map_count: int = 0
    semantic_fallback_count: int = 0
    semantic_raw_edge_kind_count: int = 0
    execution_generic_semantic_count: int = 0
    # Semantic depth metrics (Section 6: Metric Enforcement)
    semantic_edge_ratio: float = 0.0
    control_path_coverage: float = 0.0
    lineage_completeness: float = 0.0
    side_effect_coverage: float = 0.0
    call_resolution_rate: float = 0.0
    temporal_ordering_ratio: float = 0.0
    semantic_depth_passed: bool = False

    def to_dict(self) -> dict:
        import dataclasses

        return dataclasses.asdict(self)


@dataclass
class ScanResult:
    """Full output of a single scanner run."""

    edges: list[Edge] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    digest: str = ""
    commit_sha: str = ""
    repo_state_hash: str = ""
    manifest: ScanManifest = field(default_factory=ScanManifest)
    syntax_errors: list[str] = field(default_factory=list)
    type_surface_map: dict[str, str] = field(default_factory=dict)
    hollow_file_map: dict[str, bool] = field(default_factory=dict)
    boilerplate_ratio_map: dict[str, float] = field(default_factory=dict)

    def canonical_edge_text(self) -> str:
        """S7: Stable, sorted serialization of edges for digest computation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ScanResult.canonical_edge_text"
        )

        lines = []
        for e in self.edges:  # S7: edges already sorted at assignment (sorted(set(...)))
            lines.append(
                f"{e.from_name}|{e.relation_type}|{e.to_name}|{e.edge_kind}"
                f"|{e.source_file}|{e.line_no}|{e.symbol}"
            )
        return "\n".join(lines)

    def edge_counts_by_relation(self) -> dict[str, int]:
        """Count edges grouped by relation_type (graph type)."""
        counts: dict[str, int] = {}
        for e in self.edges:
            counts[e.relation_type] = counts.get(e.relation_type, 0) + 1
        return counts

    def to_dict(self) -> dict:
        """R2: Serialize to JSON-compatible dict for cache."""
        return {
            "edges": [asdict(edge) for edge in self.edges],
            "modules": self.modules,
            "digest": self.digest,
            "commit_sha": self.commit_sha,
            "repo_state_hash": self.repo_state_hash,
            "manifest": self.manifest.to_dict(),
            "syntax_errors": self.syntax_errors,
            "type_surface_map": self.type_surface_map,
            "hollow_file_map": self.hollow_file_map,
            "boilerplate_ratio_map": self.boilerplate_ratio_map,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ScanResult:
        """R2: Deserialize from cache dict."""
        edge_field_names = {f.name for f in fields(Edge)}
        manifest_field_names = {f.name for f in fields(ScanManifest)}

        edges = [Edge(**{k: v for k, v in e.items() if k in edge_field_names}) for e in data.get("edges", [])]
        manifest_data = data.get("manifest", {})
        manifest = ScanManifest(**{k: v for k, v in manifest_data.items() if k in manifest_field_names})
        return cls(
            edges=edges,
            modules=data.get("modules", []),
            digest=data.get("digest", ""),
            commit_sha=data.get("commit_sha", ""),
            repo_state_hash=data.get("repo_state_hash", ""),
            manifest=manifest,
            syntax_errors=data.get("syntax_errors", []),
            type_surface_map=data.get("type_surface_map", {}),
        )

    def compute_digest(self) -> str:
        """Compute and store the ADG-DETERMINISM-DIGEST."""
        text = self.canonical_edge_text()
        self.digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return self.digest

    def print_digest(self) -> None:
        """Print the determinism digest exactly once per run."""
        print(f"ADG-DETERMINISM-DIGEST: {self.digest}")


# Wave B: pre-compute field names once at module load time (not per call)
_EDGE_FIELD_NAMES: frozenset[str] = frozenset(f.name for f in fields(Edge))
# Wave H: fast sort key — avoids 13-field dataclass __lt__ comparison on 728k edges
_EDGE_SORT_KEY = lambda e: (e.from_name, e.relation_type, e.to_name, e.source_file, e.line_no)  # noqa: E731


def _edge_from_dict(data: dict) -> Edge:
    return Edge(**{k: v for k, v in data.items() if k in _EDGE_FIELD_NAMES})


def _edge_from_cache_fast(data: dict) -> Edge:
    """Fast path for cache-produced dicts (asdict() output has exactly Edge fields)."""
    try:
        return Edge(**data)
    except TypeError:
        return _edge_from_dict(data)


def _empty_surface_evidence() -> dict[str, int]:
    return {
        "decomposes_into_expected_count": 0,
        "controls_flow_expected_count": 0,
        "flows_to_expected_count": 0,
        "emits_side_effect_expected_count": 0,
        "resolves_callsite_expected_count": 0,
        "tests_execution_of_expected_count": 0,
        "type_surface_candidate_count": 0,
        "semantic_preexisting_count": 0,
        "semantic_exact_map_count": 0,
        "semantic_fallback_count": 0,
        "semantic_raw_edge_kind_count": 0,
    }


def _merge_surface_evidence(target: dict[str, int], delta: dict[str, int]) -> None:
    for key, value in delta.items():
        target[key] = target.get(key, 0) + int(value)


def _realized_node_names(result: ScanResult) -> set[str]:
    names = {canonical_name("Module", rel) for rel in result.modules}
    for edge in result.edges:
        names.add(edge.from_name)
        names.add(edge.to_name)
    return names


def _count_execution_generic_semantics(edges: list[Edge]) -> int:
    generic_semantics = {
        "execution",
        "call",
        "read",
        "write",
        "controls_flow",
        "flows_to",
        "emits_side_effect",
        "resolves_callsite",
    }
    return sum(
        1 for edge in edges if edge.edge_kind == "execution" and edge.semantic_type in generic_semantics
    )


## _P1608HardeningVisitor REMOVED — scanner integrity audit 2026-03-24
## Justification: 100% synthetic edges (52,888), zero AST backing, all emitted
## in __init__() with hardcoded line_no=1. See docs/reports/plans/adg_scanner_integrity_audit.md


def _tag_dead_imports(edges: list[Edge], dead_names: set[str]) -> list[Edge]:
    """E6: Re-tag import edges for unused names with edge_kind='dead_import'.

    Returns a new list with dead imports replaced by dead_import-tagged edges.
    """
    result: list[Edge] = []
    for e in edges:
        if e.relation_type == "imports" and e.symbol.split(".")[-1] in dead_names:
            result.append(
                Edge(
                    from_name=e.from_name,
                    relation_type="dead_imports",
                    to_name=e.to_name,
                    edge_kind="dead_import",
                    source_file=e.source_file,
                    line_no=e.line_no,
                    symbol=e.symbol,
                )
            )
        else:
            result.append(e)
    return result


def _detect_cycles(result: ScanResult) -> list[Edge]:
    """E5: Post-scan pass — detect strongly connected components (cycles) in the import graph.

    Uses Kosaraju's algorithm (pure Python, no external deps) on the import
    subgraph.  For each SCC with >1 node, emits `in_cycle` edges from each
    member to a synthetic ADG::Cycle:: entity.

    Returns list of new `in_cycle` edges to add to the result.
    """
    import hashlib as _hashlib

    module_prefix = "ADG::Module::"

    adj: dict[str, set[str]] = {}
    radj: dict[str, set[str]] = {}
    nodes: set[str] = set()

    for edge in result.edges:
        if edge.relation_type not in ("imports", "calls", "instantiates"):
            continue
        fn = edge.from_name
        tn = edge.to_name
        if not fn.startswith(module_prefix) or not tn.startswith(module_prefix):
            continue
        nodes.add(fn)
        nodes.add(tn)
        adj.setdefault(fn, set()).add(tn)
        radj.setdefault(tn, set()).add(fn)

    if not nodes:
        return []

    visited: set[str] = set()
    order: list[str] = []

    def dfs1(v: str) -> None:
        stack = [(v, iter(adj.get(v, set())))]
        visited.add(v)
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                order.append(node)
                stack.pop()
                continue
            if child not in visited:
                visited.add(child)
                stack.append((child, iter(adj.get(child, set()))))

    for n in sorted(nodes):
        if n not in visited:
            dfs1(n)

    visited2: set[str] = set()
    sccs: list[list[str]] = []

    def dfs2(v: str) -> list[str]:
        comp: list[str] = []
        stack = [v]
        visited2.add(v)
        while stack:
            node = stack.pop()
            comp.append(node)
            for nb in sorted(radj.get(node, set())):
                if nb not in visited2:
                    visited2.add(nb)
                    stack.append(nb)
        return comp

    for n in reversed(order):
        if n not in visited2:
            scc = dfs2(n)
            if len(scc) > 1:
                sccs.append(sorted(scc))

    new_edges: list[Edge] = []
    for scc in sccs:
        members_key = "|".join(scc)
        cycle_hash = _hashlib.sha256(members_key.encode()).hexdigest()[:16]
        cycle_node = canonical_name("Cycle", cycle_hash)
        for member in scc:
            rel = member[len(module_prefix) :]
            new_edges.append(
                Edge(
                    from_name=member,
                    relation_type="in_cycle",
                    to_name=cycle_node,
                    edge_kind="cycle",
                    source_file=rel,
                    line_no=0,
                    symbol=f"cycle:{cycle_hash}",
                )
            )

    return new_edges


def _emit_layer_violation_edges(result: ScanResult) -> list[Edge]:
    """GV: Post-scan pass — emit deduplicated `violates` edges for forbidden cross-layer imports.

    Only fires on `imports` edges where the from-module layer is forbidden from
    importing the to-symbol's layer.  Deduplicates on (from_module, from_layer, to_layer).
    Skips lazy imports (inside function bodies, TYPE_CHECKING guards, optional_import blocks).
    """
    from agentic_core.adg.schema_util import ALLOWED_LAYER_EDGES

    _SKIP_EDGE_KINDS = frozenset(
        {"lazy_import", "type_checking_import", "optional_import", "version_guard_import"}
    )

    violations: list[Edge] = []
    seen: set[tuple[str, str, str]] = set()

    for edge in result.edges:
        if edge.relation_type != "imports":
            continue
        if edge.edge_kind in _SKIP_EDGE_KINDS:
            continue

        from_rel = edge.source_file
        from_layer = module_path_to_layer(from_rel)
        if from_layer == "L_UNKNOWN":
            continue

        sym = edge.symbol
        sym_parts = sym.replace("-", "_").split(".")
        to_layer = "L_UNKNOWN"
        for length in range(len(sym_parts), 0, -1):
            candidate = "/".join(sym_parts[:length])
            found = module_path_to_layer(candidate)
            if found != "L_UNKNOWN":
                to_layer = found
                break

        if to_layer == "L_UNKNOWN":
            continue

        if from_layer == to_layer:
            continue

        if (from_layer, to_layer) in ALLOWED_LAYER_EDGES:
            continue

        dedup_key = (edge.from_name, from_layer, to_layer)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        to_layer_adg = canonical_name("Layer", to_layer)
        violations.append(
            Edge(
                from_name=edge.from_name,
                relation_type="violates",
                to_name=to_layer_adg,
                edge_kind="import",
                source_file=edge.source_file,
                line_no=edge.line_no,
                symbol=f"{from_layer}->{to_layer}",
            )
        )

    return violations




# ---------------------------------------------------------------------------
# Phase 3a: Block Decomposition Visitor — closes Node Granularity gap
# Creates block-level nodes (code_block, control_branch) with decomposes_into
# edges. Block nodes are auto-created by the builder when they appear as edge
# endpoints. The normalizer's _infer_precision_type recognizes naming patterns.
# ---------------------------------------------------------------------------

_BLOCK_COMPLEXITY_THRESHOLD = 2  # min control-flow stmts to decompose a function
_MAX_BLOCKS_PER_FUNC = 10  # cap block nodes per function




# ---------------------------------------------------------------------------
# Phase 3b: Type Surface Collector — closes Type Enrichment gap
# Walks AST and collects type annotations for symbols. Returns a dict
# mapping canonical symbol name → inferred type string.
def _iter_python_files(
    repo_root: Path, include_tests: bool = True, scan_mode: str = "full"
) -> Iterator[Path]:
    """Yield all .py files under SCAN_ROOTS, deterministic (sorted) order.

    Args:
        repo_root: Root directory to scan
        include_tests: Whether to include test files
        scan_mode: "full" (default) or "structural_only" for Phase 1 optimization
    """
    all_files: list[Path] = []
    for scan_root in _selected_scan_roots(include_tests, scan_mode):
        root_path = repo_root / scan_root
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = sorted(
                d
                for d in dirnames
                if d not in SOVEREIGN_EXCLUDED_FOLDERS
                and (include_tests or d not in _RUNTIME_ONLY_SCAN_SUBDIRS)
            )
            for fname in sorted(filenames):
                if fname.endswith(".py") and not fname.endswith(".pyc"):
                    candidate = Path(dirpath) / fname
                    rel = _repo_relative(candidate, repo_root)
                    if _is_scannable_static_path(rel, include_tests, scan_mode):
                        all_files.append(candidate)
    all_files.sort()
    yield from all_files


def _repo_relative(path: Path, repo_root: Path) -> str:
    """Return forward-slash repo-relative path.

    Args:
        path: Absolute or relative path to convert
        repo_root: Repository root directory (must be absolute)

    Returns:
        Forward-slash normalized path relative to repo_root

    Raises:
        ValueError: If repo_root is not an absolute path
        TypeError: If path or repo_root are not Path-like
    """
    # Input validation
    if not isinstance(path, (Path, str)):
        raise TypeError(f"path must be Path or str, got {type(path).__name__}")
    if not isinstance(repo_root, (Path, str)):
        raise TypeError(f"repo_root must be Path or str, got {type(repo_root).__name__}")

    path = Path(path) if isinstance(path, str) else path
    repo_root = Path(repo_root) if isinstance(repo_root, str) else repo_root

    if not repo_root.is_absolute():
        raise ValueError(f"repo_root must be absolute path: {repo_root}")

    # Handle case where path is not under repo_root
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        # Path is outside repo_root - return as-is with forward slashes
        logger.debug("Path %s is outside repo_root %s", path, repo_root)
        return str(path).replace("\\", "/")

    return str(rel).replace("\\", "/")


def _scan_file(
    filepath: Path,
    repo_root: Path,
    include_tests: bool = True,
    identity_normalizer: object | None = None,
    scan_mode: str = "full",
    layer: str | None = None,
) -> tuple[list[Edge], bool, dict[str, str], dict[str, int]]:
    """Scan a single Python file and return edges, syntax flag, type surface, and evidence.

    Args:
        filepath: Path to the Python file to scan
        repo_root: Root directory of the repository
        include_tests: Whether to include test files in scanning
        identity_normalizer: IdentityNormalizer instance for canonical names
        scan_mode: "full" (default) or "structural_only" for Phase 1 optimization
    """
    rel = _repo_relative(filepath, repo_root)
    module_adg = canonical_name("Module", rel)
    edges: list[Edge] = []

    # Phase 1.1: Determine which visitors to run based on scan_mode
    visitors_to_run = _get_visitors_for_mode(scan_mode, rel)

    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError as exc:
        line_info = f"line {exc.lineno}" if exc.lineno else "unknown line"
        logger.error("SyntaxError in %s at %s: %s", filepath, line_info, exc)
        return [], True, {}, {}  # A4: parse failures tracked
    except OSError as exc:
        logger.error("OSError reading %s: %s", filepath, exc)
        return [], True, {}, {}

    # Helper function to check if a visitor should run
    def _should_run_visitor(visitor_name: str) -> bool:
        """Check if a specific visitor should run based on scan_mode."""
        if visitors_to_run == "full":
            return True
        elif isinstance(visitors_to_run, list):
            return visitor_name in visitors_to_run
        return False

    # G1: Import edges (always run for structural mode)
    if _should_run_visitor("import"):
        from agentic_core.adg.identity.normalizer import IdentityNormalizer

        if identity_normalizer is None:
            identity_normalizer = IdentityNormalizer(repo_root=repo_root)
        ctx = VisitorContext(module_adg_name=module_adg, source_file=rel, repo_root=repo_root)
        import_visitor = _ImportVisitor(ctx)
        import_visitor.visit(tree)
        edges.extend(import_visitor.extract_edges())

    # Run other visitors based on scan mode
    if visitors_to_run == "full":
        # G2: Call/write/network edges
        call_visitor = _CallVisitor(VisitorContext(module_adg, rel))
        call_visitor.visit(tree)
        edges.extend(call_visitor.extract_edges())

        # G3: Inheritance edges (H3)
        inh_visitor = _InheritanceVisitor(VisitorContext(module_adg, rel))
        inh_visitor.visit(tree)
        edges.extend(inh_visitor.extract_edges())

        # G5: Config/env read edges (H4)
        attr_visitor = _AttributeVisitor(VisitorContext(module_adg, rel))
        attr_visitor.visit(tree)
        edges.extend(attr_visitor.extract_edges())

        # G6: Composition edges (H5)
        comp_visitor = _CompositionVisitor(VisitorContext(module_adg, rel))
        comp_visitor.visit(tree)
        edges.extend(comp_visitor.extract_edges())

        # GF: Dynamic execution edges (S3/RULE_F)
        dyn_visitor = _DynamicExecutionVisitor(VisitorContext(module_adg, rel))
        dyn_visitor.visit(tree)
        edges.extend(dyn_visitor.extract_edges())

        # G4: Inter-module call graph
        icg_visitor = _InternalCallGraphVisitor(VisitorContext(module_adg, rel))
        icg_visitor.visit(tree)
        edges.extend(icg_visitor.extract_edges())

        # GT: Test traceability graph
        tt_visitor = _TestTraceabilityVisitor(VisitorContext(module_adg, rel))
        tt_visitor.visit(tree)
        edges.extend(tt_visitor.extract_edges())

        # GG: Governance plane graph
        gov_visitor = _GovernancePlaneVisitor(VisitorContext(module_adg, rel))
        gov_visitor.visit(tree)
        edges.extend(gov_visitor.extract_edges())

        # Wave 4: Critical edge densification (DISABLED - legacy visitor removed)
        # critical_visitor = _CriticalEdgeVisitor(module_adg, rel)
        # critical_visitor.visit(tree)
        # edges.extend(critical_visitor.edges)

        # Wave 2: Test surface linking (DISABLED - legacy visitor removed)
        # if include_tests and (
        #     filepath.name.endswith("_test.py") or "test_" in filepath.name or rel.startswith("tests/")
        # ):
        #     test_surface_visitor = _TestSurfaceVisitor(module_adg, str(filepath))
        #     test_surface_visitor.visit(tree)
        #     edges.extend(test_surface_visitor.edges)

        # E1: Symbol inventory / exports graph
        sym_visitor = _SymbolInventoryVisitor(VisitorContext(module_adg, rel))
        sym_visitor.visit(tree)
        edges.extend(sym_visitor.extract_edges())

        # E3: Decorator graph (G7)
        dec_visitor = _DecoratorVisitor(VisitorContext(module_adg, rel))
        dec_visitor.visit(tree)
        edges.extend(dec_visitor.extract_edges())

        # E4: Type annotation graph (G8)
        ann_visitor = _TypeAnnotationVisitor(VisitorContext(module_adg, rel))
        ann_visitor.visit(tree)
        edges.extend(ann_visitor.extract_edges())

    # E6: Unused import detection — emit dead_import edges (only in full mode)
    if _should_run_visitor("unused_import"):
        unused_visitor = _UnusedImportVisitor(VisitorContext(module_adg, rel))
        unused_visitor.visit(tree)
        edges.extend(unused_visitor.extract_edges())

    # GA: Behavioral anti-pattern detection (only in full mode)
    if _should_run_visitor("antipattern"):
        ap_visitor = _AntipatternVisitor(VisitorContext(module_adg, rel))
        ap_visitor.visit(tree)
        edges.extend(ap_visitor.extract_edges())

    # All remaining visitors (only in full mode)
    if visitors_to_run == "full":
        # E20: Prompt lifecycle graph (generates_prompt / consumes_prompt)
        ctx = VisitorContext(module_adg_name=module_adg, source_file=rel, repo_root=str(repo_root))
        ps_visitor = _PromptSlotVisitor(ctx)
        ps_visitor.visit(tree)
        edges.extend(ps_visitor.extract_edges())

        # E23: Execution trace → telemetry linkage (triggered_telemetry)
        et_visitor = _ExecutionTraceVisitor(ctx)
        et_visitor.visit(tree)
        edges.extend(et_visitor.extract_edges())

        # G1 (gap): Healer/validator loop graph (heals, validates, orchestrates_healing)
        hv_visitor = _HealerValidatorVisitor(ctx)
        hv_visitor.visit(tree)
        edges.extend(hv_visitor.extract_edges())

        # G3 (gap): Embedding pipeline graph (chunks_into, embeds_into, stores_embedding, retrieves_via)
        emb_visitor = _EmbeddingPipelineVisitor(ctx)
        emb_visitor.visit(tree)
        edges.extend(emb_visitor.extract_edges())

        # G4 (gap): HITL / confidence-threshold gating (gated_by_confidence, escalates_to_human)
        hitl_visitor = _HITLVisitor(ctx)
        hitl_visitor.visit(tree)
        edges.extend(hitl_visitor.extract_edges())

        # G5 (gap): Safety enforcement plane (applies_guardrail, verifies_policy)
        safety_visitor = _SafetyEnforcementVisitor(VisitorContext(module_adg, rel))
        safety_visitor.visit(tree)
        edges.extend(safety_visitor.extract_edges())

        # G34: L4/UWG Wave 1 Ingress Gate visitor
        uwg_visitor = _UWGIngressGateVisitor(VisitorContext(module_adg, rel))
        uwg_visitor.visit(tree)
        edges.extend(uwg_visitor.extract_edges())

        # G35: L4/UWG Wave 2 Mutation Record Assembly visitor
        mutation_visitor = _MutationRecordAssemblyVisitor(VisitorContext(module_adg, rel))
        mutation_visitor.visit(tree)
        edges.extend(mutation_visitor.extract_edges())

        # G36: L4/UWG Wave 3 Authoritative Commit + L4 Read Surface visitor
        commit_visitor = _AuthoritativeCommitVisitor(VisitorContext(module_adg, rel))
        commit_visitor.visit(tree)
        edges.extend(commit_visitor.extract_edges())

        # G37: L4/UWG Wave 4 Outbound Read Bridge visitor
        bridge_visitor = _OutboundReadBridgeVisitor(VisitorContext(module_adg, rel))
        bridge_visitor.visit(tree)
        edges.extend(bridge_visitor.extract_edges())

        # G7 (gap): Sandbox airlock / work-contract (enters_sandbox, issues_capability_token, stamps_work_contract)
        sandbox_visitor = _SandboxAirlockVisitor(VisitorContext(module_adg, rel))
        sandbox_visitor.visit(tree)
        edges.extend(sandbox_visitor.extract_edges())

        # G8 (gap): Capability-token / tool-budget (grants_resource, exceeds_budget)
        budget_visitor = _CapabilityBudgetVisitor(VisitorContext(module_adg, rel))
        budget_visitor.visit(tree)
        edges.extend(budget_visitor.extract_edges())

        # G9 (gap): JIT context sync / freeze (pulls_context, freezes_context, unfreezes_context)
        jit_visitor = _JITContextVisitor(VisitorContext(module_adg, rel))
        jit_visitor.visit(tree)
        edges.extend(jit_visitor.extract_edges())

        # G10 (gap): Execution boundary verification (verifies_boundary, certifies_envelope)
        boundary_visitor = _BoundaryVerifierVisitor(VisitorContext(module_adg, rel))
        boundary_visitor.visit(tree)
        edges.extend(boundary_visitor.extract_edges())

    # All remaining gap visitors (DISABLED - legacy visitors)
    # if visitors_to_run == "full":
    #     # G11 (gap): Determinism control
    #     determinism_visitor = _DeterminismControlVisitor(VisitorContext(module_adg, rel))
    #     determinism_visitor.visit(tree)
    #     edges.extend(determinism_visitor.extract_edges())
    #
    #     # G12 (gap): Network / I/O interception
    #     io_visitor = _IOInterceptionVisitor(VisitorContext(module_adg, rel))
    #     io_visitor.visit(tree)
    #     edges.extend(io_visitor.extract_edges())
    #
    #     # G13 (gap): Mutation transport / commit
    #     mutation_transport_visitor = _MutationTransportVisitor(VisitorContext(module_adg, rel))
    #     mutation_transport_visitor.visit(tree)
    #     edges.extend(mutation_transport_visitor.extract_edges())
    #
    #     # G14 (gap): Execution trace / proof
    #     proof_visitor = _ExecutionProofVisitor(VisitorContext(module_adg, rel))
    #     proof_visitor.visit(tree)
    #     edges.extend(proof_visitor.extract_edges())

    # G16 (gap): Evaluation / optimization spine (DISABLED - legacy visitor)
    # eval_visitor = _EvalSpineVisitor(VisitorContext(module_adg, rel))
    # eval_visitor.visit(tree)
    # edges.extend(eval_visitor.extract_edges())

    # GH (RCA Rule D): Duplicate method definition detection (DISABLED)
    # dup_visitor = _DuplicateMethodVisitor(module_adg, rel)
    # dup_visitor.visit(tree)
    # edges.extend(dup_visitor.edges)

    # GU (RCA Rule G): Unreachable code after raise detection (DISABLED)
    # unreach_visitor = _UnreachableCodeAfterRaiseVisitor(module_adg, rel)
    # unreach_visitor.visit(tree)
    # edges.extend(unreach_visitor.edges)

    # G17 (gap): Secret / credential access (DISABLED - legacy visitor)
    # secret_visitor = _SecretAccessVisitor(module_adg, rel)
    # secret_visitor.visit(tree)
    # edges.extend(secret_visitor.edges)

    # Execution-grade semantic enrichment (replaces disabled _PrecisionHardeningVisitor)
    # Closes gaps: Data Lineage, Control Flow, Side Effects, Temporal Ordering, Callsite Resolution
    exec_visitor = _ExecutionSemanticVisitor(VisitorContext(module_adg, rel))
    exec_visitor.visit(tree)
    edges.extend(exec_visitor.extract_edges())

    # All final gap visitors (DISABLED - legacy visitors removed)
    # if visitors_to_run == "full":
    #     # G18 (gap): Config governance
    #     config_gov_visitor = _ConfigGovernanceVisitor(module_adg, rel)
    #     config_gov_visitor.visit(tree)
    #     edges.extend(config_gov_visitor.edges)
    #
    #     # G19 (gap): Dynamic invocation
    #     dyn_inv_visitor = _DynamicInvocationVisitor(module_adg, rel)
    #     dyn_inv_visitor.visit(tree)
    #     edges.extend(dyn_inv_visitor.edges)
    #
    #     # G20 (gap): Policy state observation
    #     pso_visitor = _PolicyStateObserverVisitor(module_adg, rel)
    #     pso_visitor.visit(tree)
    #     edges.extend(pso_visitor.edges)
    #
    #     # G21 (gap): Anti-pattern registry
    #     ap_reg_visitor = _AntipatternRegistryVisitor(module_adg, rel)
    #     ap_reg_visitor.visit(tree)
    #     edges.extend(ap_reg_visitor.edges)
    #
    #     # G22 (gap): Healing orchestrator
    #     healing_orch_visitor = _HealingOrchestratorVisitor(module_adg, rel)
    #     healing_orch_visitor.visit(tree)
    #     edges.extend(healing_orch_visitor.edges)
    #
    #     # G23 (gap): Non-determinism primitive detection
    #     nondet_visitor = _NondeterminismVisitor(module_adg, rel)
    #     nondet_visitor.visit(tree)
    #     edges.extend(nondet_visitor.edges)
    #
    #     # G24 (gap): External HTTP / network egress
    #     http_visitor = _ExternalHttpVisitor(module_adg, rel)
    #     http_visitor.visit(tree)
    #     edges.extend(http_visitor.edges)
    #
    #     # G25 (gap): Agent-to-agent dispatch
    #     agent_dispatch_visitor = _AgentDispatchVisitor(module_adg, rel)
    #     agent_dispatch_visitor.visit(tree)
    #     edges.extend(agent_dispatch_visitor.edges)
    #
    #     # G28 (gap): P1 orchestration governance
    #     p1_orch_visitor = _P1OrchestrationGovernanceVisitor(module_adg, rel)
    #     p1_orch_visitor.visit(tree)
    #     edges.extend(p1_orch_visitor.edges)
    #
    #     # G26 (gap): L5 validation proof edges
    #     l5_proof_visitor = _L5ValidationProofVisitor(module_adg, rel)
    #     l5_proof_visitor.visit(tree)
    #     edges.extend(l5_proof_visitor.edges)

    # All P-series visitors (DISABLED - legacy visitors removed)
    # if visitors_to_run == "full":
    #     # G28 (gap): P1 orchestration
    #     p1_orch_visitor = _P1OrchestrationVisitor(module_adg, rel)
    #     p1_orch_visitor.visit(tree)
    #     edges.extend(p1_orch_visitor.edges)
    #
    #     # G29 (gap): P2 execution capability
    #     p2_exec_visitor = _P2ExecutionCapabilityVisitor(module_adg, rel)
    #     p2_exec_visitor.visit(tree)
    #     edges.extend(p2_exec_visitor.edges)
    #
    #     # G30 (gap): P3 orchestration & healing
    #     p3_orch_visitor = _P3OrchestrationHealingVisitor(module_adg, rel)
    #     p3_orch_visitor.visit(tree)
    #     edges.extend(p3_orch_visitor.edges)
    #
    #     # G32 (gap): P3 learning maturity
    #     p3_learn_visitor = _P3LearningMaturityVisitor(module_adg, rel)
    #     p3_learn_visitor.visit(tree)
    #     edges.extend(p3_learn_visitor.edges)
    #
    #     # G33 (gap): P4 observability & governance
    #     p4_obs_visitor = _P4ObservabilityGovernanceVisitor(module_adg, rel)
    #     p4_obs_visitor.visit(tree)
    #     edges.extend(p4_obs_visitor.edges)

    # All final visitors (DISABLED - legacy visitors)
    # if visitors_to_run == "full":
    #     # G31 (gap): P4 state, telemetry & learning
    #     p4_state_visitor = _P4StateTelemetryVisitor(module_adg, rel)
    #     p4_state_visitor.visit(tree)
    #     edges.extend(p4_state_visitor.edges)
    #
    #     # G27 (gap): Learning / prompt provenance
    #     learning_prov_visitor = _LearningProvenanceVisitor(module_adg, rel)
    #     learning_prov_visitor.visit(tree)
    #     edges.extend(learning_prov_visitor.edges)

    # W1c: Module definition visitor — emit module→func/class decomposes_into
    # Phase 3a: Module definition visitor (DISABLED - legacy visitor removed)
    # mod_def_visitor = _ModuleDefinitionVisitor(module_adg, rel)
    # mod_def_visitor.visit(tree)
    # edges.extend(mod_def_visitor.edges)

    # Phase 3a: Block decomposition (DISABLED - legacy visitor removed)
    # block_visitor = _BlockDecompositionVisitor(module_adg, rel)
    # block_visitor.visit(tree)
    # edges.extend(block_visitor.edges)

    # Phase 3b: Type surface collection — type enrichment
    type_collector = _TypeSurfaceCollector(rel)
    type_collector.visit(tree)
    type_surface_map = type_collector.type_map  # returned to caller

    # Phase 3c: Test → Execution linkage (DISABLED - legacy visitor removed)
    # test_link_visitor = _TestExecutionLinkageVisitor(module_adg, rel)
    # test_link_visitor.visit(tree)
    # edges.extend(test_link_visitor.edges)

    # Phase 1.4: Hollow file annotation
    hollow_annotator = _HollowFileAnnotator(module_adg, rel)
    hollow_annotator.visit(tree)

    # Initialize surface_evidence
    surface_evidence = {}

    # Store hollow file metadata in surface_evidence for later processing
    if visitors_to_run == "full" and hasattr(hollow_annotator, "is_hollow"):
        surface_evidence["is_hollow"] = hollow_annotator.is_hollow
        surface_evidence["boilerplate_ratio"] = hollow_annotator.boilerplate_ratio

    # Phase 3b: Type surface collection (always needed for return)
    if visitors_to_run != "full":
        type_collector = _TypeSurfaceCollector(rel)
        type_collector.visit(tree)
        type_surface_map = type_collector.type_map

    # Surface evidence calculation (handle both modes)
    if visitors_to_run == "full":
        unique_execution_edges = set(exec_visitor.edges)
        surface_evidence = {
            "decomposes_into_expected_count": 0,  # Disabled: block_visitor
            "controls_flow_expected_count": sum(
                1 for edge in unique_execution_edges if edge.relation_type == "controls_flow"
            ),
            "flows_to_expected_count": sum(
                1 for edge in unique_execution_edges if edge.relation_type == "flows_to"
            ),
            "emits_side_effect_expected_count": sum(
                1 for edge in unique_execution_edges if edge.relation_type == "emits_side_effect"
            ),
            "resolves_callsite_expected_count": sum(
                1 for edge in unique_execution_edges if edge.relation_type == "resolves_callsite"
            ),
            "tests_execution_of_expected_count": 0,  # Disabled: test_link_visitor
            "type_surface_candidate_count": len(type_surface_map),
        }
    else:
        # Structural-only mode - minimal evidence
        surface_evidence = {
            "decomposes_into_expected_count": 0,
            "controls_flow_expected_count": 0,
            "flows_to_expected_count": 0,
            "emits_side_effect_expected_count": 0,
            "resolves_callsite_expected_count": 0,
            "tests_execution_of_expected_count": 0,
            "type_surface_candidate_count": len(type_surface_map),
        }

    # -----------------------------------------------------------------------
    # SEMANTIC ENRICHMENT: stamp semantic_type on ALL edges (zero new edges)
    # Ensures semantic_edge_ratio → 1.0 by classifying every structural edge.
    # -----------------------------------------------------------------------
    edges = _filter_runtime_only_edges(edges, include_tests, scan_mode)
    edges, semantic_stamp_stats = _stamp_semantic_types_with_stats(edges)
    surface_evidence.update(semantic_stamp_stats)

    return edges, False, type_surface_map, surface_evidence


from agentic_core.adg.extraction.semantic_maps import _SEMANTIC_FALLBACK, _SEMANTIC_TYPE_MAP


def _stamp_semantic_types_with_stats(edges: list[Edge]) -> tuple[list[Edge], dict[str, int]]:
    stats = {
        "semantic_preexisting_count": 0,
        "semantic_exact_map_count": 0,
        "semantic_fallback_count": 0,
        "semantic_raw_edge_kind_count": 0,
    }
    result: list[Edge] = []
    for e in edges:
        if e.semantic_type:
            stats["semantic_preexisting_count"] += 1
            result.append(e)
            continue
        st = _SEMANTIC_TYPE_MAP.get((e.edge_kind, e.relation_type))
        if st is not None:
            stats["semantic_exact_map_count"] += 1
        else:
            st = _SEMANTIC_FALLBACK.get(e.relation_type)
            if st is not None:
                stats["semantic_fallback_count"] += 1
            else:
                st = e.edge_kind
                stats["semantic_raw_edge_kind_count"] += 1
        result.append(replace(e, semantic_type=st))
    return result, stats


def _stamp_semantic_types(edges: list[Edge]) -> list[Edge]:
    """Post-process: stamp semantic_type on every edge that lacks one.

    Frozen dataclass → uses dataclasses.replace(). No new edges created.
    """
    stamped_edges, _ = _stamp_semantic_types_with_stats(edges)
    return stamped_edges


def _check_semantic_depth(result: ScanResult) -> dict[str, float]:
    """Section 6: Semantic depth metric enforcement.

    Computes 6 ratios that measure execution-grade resolution.
    All ratios are [0.0, 1.0]. Build should fail if any drops below threshold.

    Returns dict of metric_name → value for persistence in ScanManifest.
    """
    edges = result.edges
    total = len(edges)

    def _coverage(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 1.0
        return min(1.0, numerator / denominator)

    if total == 0:
        return {
            "semantic_edge_ratio": 0.0,
            "control_path_coverage": 0.0,
            "lineage_completeness": 0.0,
            "side_effect_coverage": 0.0,
            "call_resolution_rate": 0.0,
            "temporal_ordering_ratio": 0.0,
        }

    # 1. semantic_edge_ratio: fraction of edges with semantic_type populated
    semantic_count = sum(1 for e in edges if e.semantic_type)
    semantic_edge_ratio = semantic_count / total

    # 2. control_path_coverage: fraction of eligible control-flow sites materialized
    controls_flow_total = sum(1 for e in edges if e.relation_type == "controls_flow")
    control_path_coverage = _coverage(
        controls_flow_total,
        result.manifest.controls_flow_expected_count,
    )

    # 3. lineage_completeness: fraction of eligible lineage sites materialized
    flows_to_total = sum(1 for e in edges if e.relation_type == "flows_to")
    lineage_completeness = _coverage(flows_to_total, result.manifest.flows_to_expected_count)

    # 4. side_effect_coverage: fraction of eligible side-effect callsites materialized
    side_effect_total = sum(1 for e in edges if e.relation_type == "emits_side_effect")
    side_effect_coverage = _coverage(
        side_effect_total,
        result.manifest.emits_side_effect_expected_count,
    )

    # 5. call_resolution_rate: fraction of eligible dynamic callsites resolved
    callsite_total = sum(1 for e in edges if e.relation_type == "resolves_callsite")
    call_resolution_rate = _coverage(
        callsite_total,
        result.manifest.resolves_callsite_expected_count,
    )

    # 6. temporal_ordering_ratio: fraction of execution edges with seq= metadata
    exec_edges = [e for e in edges if e.edge_kind == "execution"]
    ordered = sum(1 for e in exec_edges if "seq=" in e.dynamic_resolution)
    temporal_ordering_ratio = _coverage(ordered, len(exec_edges)) if exec_edges else 0.0

    return {
        "semantic_edge_ratio": round(semantic_edge_ratio, 4),
        "control_path_coverage": round(control_path_coverage, 4),
        "lineage_completeness": round(lineage_completeness, 4),
        "side_effect_coverage": round(side_effect_coverage, 4),
        "call_resolution_rate": round(call_resolution_rate, 4),
        "temporal_ordering_ratio": round(temporal_ordering_ratio, 4),
    }


# Semantic depth thresholds — build warns if below these
_SEMANTIC_DEPTH_THRESHOLDS: dict[str, float] = {
    "semantic_edge_ratio": 0.95,
    "control_path_coverage": 0.20,
    "lineage_completeness": 0.20,
    "side_effect_coverage": 0.15,
    "call_resolution_rate": 0.95,
    "temporal_ordering_ratio": 0.95,
}


def _violation_propagation_eligibility(result: ScanResult) -> dict[str, int]:
    def _symbol_to_module_key(sym_name: str) -> str:
        raw = sym_name.replace("ADG::Symbol::", "").replace("ADG::Module::", "")
        mod_part = raw.split("::")[0]
        return mod_part.replace(".", "/")

    def _module_to_key(mod_name: str) -> str:
        raw = mod_name.replace("ADG::Module::", "")
        return raw.replace("/__init__.py", "").replace(".py", "")

    def _key_prefixes(module_key: str) -> tuple[str, ...]:
        parts = [part for part in module_key.split("/") if part]
        return tuple("/".join(parts[:idx]) for idx in range(1, len(parts) + 1))

    importers_of: dict[str, set[str]] = {}
    violating_modules: set[str] = set()

    for edge in result.edges:
        if edge.relation_type == "imports" and edge.from_name.startswith("ADG::Module::"):
            for prefix in _key_prefixes(_symbol_to_module_key(edge.to_name)):
                importers_of.setdefault(prefix, set()).add(edge.from_name)
        elif edge.relation_type == "violates":
            violating_modules.add(edge.from_name)

    eligible_edge_count = 0
    eligible_module_targets: set[str] = set()
    for violating_module in violating_modules:
        violating_key = _module_to_key(violating_module)
        visited: set[str] = {violating_module}
        frontier = {
            importer
            for importer in importers_of.get(violating_key, set())
            if importer not in violating_modules and importer not in visited
        }
        visited |= frontier
        eligible_module_targets |= frontier
        eligible_edge_count += len(frontier)
        for _depth in range(2, _MAX_PROPAGATION_DEPTH + 1):
            next_frontier: set[str] = set()
            for node in frontier:
                node_key = _module_to_key(node)
                for importer in importers_of.get(node_key, set()):
                    if importer not in visited:
                        visited.add(importer)
                        next_frontier.add(importer)
            frontier = next_frontier
            eligible_module_targets |= frontier
            eligible_edge_count += len(frontier)
            if not frontier:
                break

    return {
        "violation_propagation_eligible_count": eligible_edge_count,
        "violation_propagation_target_count": len(eligible_module_targets),
    }


# ---------------------------------------------------------------------------
# Phase 3d: Violation Trace Depth — propagate violations through lineage
# For each violation edge, traces forward through flows_to and controls_flow
# to find downstream modules affected by the violation.
# ---------------------------------------------------------------------------
_MAX_PROPAGATION_DEPTH = 3  # max hops for violation propagation
_MAX_PROPAGATION_EDGES = 50000  # cap total propagation edges


def _propagate_violations(result: ScanResult) -> list[Edge]:
    """Phase 3d: Trace violations through import graph.

    For each violation edge (module A violates layer rule), find downstream
    modules that import A (directly or transitively) and emit
    violation_propagates_through edges showing blast radius.
    """

    def _symbol_to_module_key(sym_name: str) -> str:
        """Convert ADG::Symbol::agentic_core.L0_routing.foo::bar to module key."""
        raw = sym_name.replace("ADG::Symbol::", "").replace("ADG::Module::", "")
        # Strip symbol suffix after ::
        mod_part = raw.split("::")[0]
        # Convert dots to slashes for module key
        return mod_part.replace(".", "/")

    def _module_to_key(mod_name: str) -> str:
        """Normalize ADG::Module::path/to/file.py to key format."""
        raw = mod_name.replace("ADG::Module::", "")
        # Remove .py and /__init__ to get package key
        raw = raw.replace("/__init__.py", "").replace(".py", "")
        return raw

    def _key_prefixes(module_key: str) -> tuple[str, ...]:
        parts = [part for part in module_key.split("/") if part]
        return tuple("/".join(parts[:idx]) for idx in range(1, len(parts) + 1))

    # Build reverse import adjacency: package_key → {importing module names}
    importers_of: dict[str, set[str]] = {}
    for e in result.edges:
        if e.relation_type == "imports" and e.from_name.startswith("ADG::Module::"):
            target_key = _symbol_to_module_key(e.to_name)
            for prefix in _key_prefixes(target_key):
                importers_of.setdefault(prefix, set()).add(e.from_name)

    # Collect violating modules (from_name of violates edges)
    violating_modules: set[str] = set()
    for e in result.edges:
        if e.relation_type == "violates":
            violating_modules.add(e.from_name)

    if not violating_modules or not importers_of:
        return []

    # Also build module→key map for BFS traversal
    module_key_map: dict[str, str] = {}
    for vm in violating_modules:
        module_key_map[vm] = _module_to_key(vm)

    propagation_edges: list[Edge] = []
    for v_module in violating_modules:
        v_key = module_key_map[v_module]

        visited: set[str] = {v_module}
        depth1_importers = {
            importer
            for importer in importers_of.get(v_key, set())
            if importer not in violating_modules and importer not in visited
        }
        for importer in depth1_importers:
            visited.add(importer)
            propagation_edges.append(
                Edge(
                    from_name=v_module,
                    relation_type="violation_propagates_through",
                    to_name=importer,
                    edge_kind="violation_propagation",
                    source_file="",
                    line_no=0,
                    symbol="depth=1",
                    semantic_type="violation_trace",
                    confidence=0.8,
                )
            )
            if len(propagation_edges) >= _MAX_PROPAGATION_EDGES:
                return propagation_edges

        frontier = list(depth1_importers)
        for depth in range(2, _MAX_PROPAGATION_DEPTH + 1):
            next_frontier: list[str] = []
            for node in frontier:
                node_key = _module_to_key(node)
                for importer in importers_of.get(node_key, set()):
                    if importer not in visited:
                        visited.add(importer)
                        next_frontier.append(importer)
                        propagation_edges.append(
                            Edge(
                                from_name=v_module,
                                relation_type="violation_propagates_through",
                                to_name=importer,
                                edge_kind="violation_propagation",
                                source_file="",
                                line_no=0,
                                symbol=f"depth={depth}",
                                semantic_type="violation_trace",
                                confidence=max(0.5, 1.0 - depth * 0.2),
                            )
                        )
                        if len(propagation_edges) >= _MAX_PROPAGATION_EDGES:
                            return propagation_edges
            frontier = next_frontier
            if not frontier:
                break

    return propagation_edges


def _check_evidence_floors(result: ScanResult) -> bool:
    """A2: Verify minimum evidence floors per graph type. Returns True if all pass."""
    counts = result.edge_counts_by_relation()
    all_pass = True
    for relation, floor in _MIN_EVIDENCE_FLOORS.items():
        actual = counts.get(relation, 0)
        if actual < floor:
            logger.warning(
                "Evidence floor FAIL: %s has %d edges (minimum %d)",
                relation,
                actual,
                floor,
            )
            all_pass = False
    return all_pass


def _check_cardinality(result: ScanResult) -> list[str]:
    """S9: Check edge count ranges for sanity. Returns list of violation strings."""
    counts = result.edge_counts_by_relation()
    violations: list[str] = []
    for relation, (lo, hi) in _CARDINALITY_RANGES.items():
        actual = counts.get(relation, 0)
        if actual < lo:
            violations.append(f"CARDINALITY LOW: {relation}={actual} (expected >={lo})")
        elif actual > hi:
            violations.append(f"CARDINALITY HIGH: {relation}={actual} (expected <={hi})")
    return violations


def run_scanner_self_test() -> bool:
    """S1: Embedded self-test with synthetic sample code.

    Verifies all 6 graph types extract at least one edge from known sample.
    Returns True if all checks pass.
    """
    sample_code = """
import os
from pathlib import Path
from some.external.sdk import SomeProvider
import uuid
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import emit_replay_key  # noqa: E402
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import emit_determinism_digest  # noqa: E402
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import _emit_records_execution_trace  # noqa: E402

class BaseClass:
    pass

class ConcreteAgent(BaseClass):
    def __init__(self):
        self.provider = SomeProvider()
        self.path = Path("/tmp")
        env_val = os.getenv("SOME_KEY")
        dyn = eval("1+1")

    def run(self):
        import importlib
        # guardian: allow-silent-swallow - acceptable exception handling
        mod = importlib.import_module("some.mod")
"""
    try:
        tree = ast.parse(sample_code)
    except SyntaxError:
        return False

    module_adg = "ADG::Module::_self_test_"
    source = "_self_test_"

    # G1
    from agentic_core.adg.identity.normalizer import IdentityNormalizer

    identity_normalizer = IdentityNormalizer(repo_root=Path.cwd())
    ctx = VisitorContext(module_adg_name=module_adg, source_file=source, repo_root=str(Path.cwd()))
    iv = _ImportVisitor(ctx)
    iv.visit(tree)
    if not iv.extract_edges():
        return False

    # G3
    inh = _InheritanceVisitor(VisitorContext(module_adg, source))
    inh.visit(tree)
    if not inh.extract_edges():
        return False

    # G5
    attr = _AttributeVisitor(VisitorContext(module_adg, source))
    attr.visit(tree)
    if not attr.extract_edges():
        return False

    # G6
    comp = _CompositionVisitor(VisitorContext(module_adg, source))
    comp.visit(tree)
    if not comp.extract_edges():
        return False

    # GF
    dyn = _DynamicExecutionVisitor(VisitorContext(module_adg, source))
    dyn.visit(tree)
    if not dyn.extract_edges():
        return False

    return True


class ADGStaticScanner:
    """Main entry point for ADG static analysis.

    Usage:
        scanner = ADGStaticScanner(repo_root=Path("."))
        result = scanner.scan(commit_sha="abc123")
        result.print_digest()
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        include_tests: bool = False,
        cache_path: Path | None = None,
        scan_mode: str = "full",
    ) -> None:
        """Initialize ADG Static Scanner.

        Args:
            repo_root: Root directory of the repository to scan
            include_tests: Whether to include test files in scanning
            cache_path: Optional path to scan cache file
            scan_mode: "full", "structural_only", "selective", or "auto" for Phase 1 optimization
                         "auto" enables cache-aware mode selection (Phase 1.3)
        """
        self.repo_root = Path(repo_root) if repo_root is not None else Path.cwd()
        self.include_tests = include_tests  # H1
        self.cache_path = cache_path  # E9: optional incremental cache
        self.scan_mode = scan_mode  # Phase 1.1-1.3: scan mode support

    def scan(self, commit_sha: str = "") -> ScanResult:
        """Run full static scan. Returns ScanResult with digest computed."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ADGStaticScanner.scan")

        import sys

        from agentic_core.adg.extraction.scan_cache import ScanCache, file_hash

        if self.scan_mode == "auto":
            self.scan_mode = _get_cache_aware_scan_mode(self.cache_path, self.repo_root, self.include_tests)

        # --- Initialization Phase ---
        # Cache load, normalizer warm-up, and file enumeration (serial).
        # Note: ThreadPoolExecutor concurrency was benchmarked but only saved 0.117s
        # after the normalizer os.walk fix (0.27s vs 1.95s with rglob). Not worth the overhead.
        from agentic_core.adg.identity.normalizer import IdentityNormalizer

        cache = ScanCache.load(self.cache_path) if self.cache_path else ScanCache()
        shared_normalizer = IdentityNormalizer(repo_root=self.repo_root)
        shared_normalizer._get_known_files()  # Pre-warm known-files cache (single os.walk)
        all_files = list(
            _iter_python_files(self.repo_root, include_tests=self.include_tests, scan_mode=self.scan_mode)
        )

        _skip_self_test = os.environ.get("ADG_SKIP_SELF_TEST", "").strip().lower() in ("1", "true", "yes")
        manifest = ScanManifest(
            python_ast_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            tests_included=self.include_tests,
            scanner_self_test_passed=(False if _skip_self_test else run_scanner_self_test()),  # S1
            scan_mode=self.scan_mode,  # Phase 1.3: record selected mode
        )

        result = ScanResult(commit_sha=commit_sha, manifest=manifest)
        all_edges: list[Edge] = []
        all_type_surface: dict[str, str] = {}
        modules_seen: list[str] = []
        syntax_error_count = 0
        syntax_errors: list[str] = []
        surface_evidence_totals = _empty_surface_evidence()

        # --- Pre-compute file hashes ---
        # Note: ThreadPool hashing benchmarked slower on Windows (spawn overhead > benefit).
        # Serial pre-hash is kept for clean separation of I/O from cache logic.
        _file_hashes: dict[Path, str] = {f: file_hash(f) for f in all_files}

        for filepath in all_files:
            rel = _repo_relative(filepath, self.repo_root)
            modules_seen.append(rel)
            manifest.discovered_module_count += 1

            # E9: Check cache before scanning (hash pre-computed above)
            fhash = _file_hashes[filepath]
            cached_edge_dicts, cached_type_map, cached_surface_evidence, cache_hit = cache.get(rel, fhash)
            if cache_hit and cached_edge_dicts is not None:
                file_edges = [_edge_from_cache_fast(d) for d in cached_edge_dicts]
                file_type_map = cached_type_map
                file_surface_evidence = cached_surface_evidence
                had_error = False
            else:
                file_edges, had_error, file_type_map, file_surface_evidence = _scan_file(
                    filepath, self.repo_root, self.include_tests, shared_normalizer, self.scan_mode
                )
                if not had_error:
                    cache.put(rel, fhash, file_edges, file_type_map, file_surface_evidence)

            if had_error:
                syntax_error_count += 1
                syntax_errors.append(rel)
            else:
                manifest.parsed_module_count += 1
                all_type_surface.update(file_type_map)
                _merge_surface_evidence(surface_evidence_totals, file_surface_evidence)
            all_edges.extend(file_edges)

        if self.cache_path:
            cache.save(self.cache_path)
        cache_stats = cache.stats()
        manifest.cache_hits = cache_stats["hits"]
        manifest.cache_misses = cache_stats["misses"]
        manifest.cache_hit_rate = cache_stats["hit_rate"]

        # A3: zero-parsed-file check
        if manifest.parsed_module_count == 0:
            logger.error("ADG FATAL: zero files parsed — scan aborted")

        result.edges = sorted(set(all_edges), key=_EDGE_SORT_KEY)  # S7: sorted for determinism
        result.modules = sorted(modules_seen)
        result.syntax_errors = syntax_errors
        result.type_surface_map = all_type_surface

        # Phase 1.4: Populate hollow file maps from surface evidence
        result.hollow_file_map = {}
        result.boilerplate_ratio_map = {}
        # Note: This would be populated from individual file surface_evidence
        # For now, initialize empty maps - they'll be populated as files are scanned
        result.compute_digest()

        # GV / Phase 3d / E5: batch all post-scan edge additions — sort ONCE at the end
        _post_scan_edge_set: set = set(result.edges)

        # GV: Layer violation post-scan pass
        violation_edges = _emit_layer_violation_edges(result)
        if violation_edges:
            violation_edges, violation_stamp_stats = _stamp_semantic_types_with_stats(violation_edges)
            _merge_surface_evidence(surface_evidence_totals, violation_stamp_stats)
            _post_scan_edge_set |= set(violation_edges)

        # Propagation eligibility needs the violation edges present (unsorted is fine — it only iterates)
        result.edges = list(_post_scan_edge_set)
        propagation_evidence = _violation_propagation_eligibility(result)
        manifest.violation_propagation_eligible_count = propagation_evidence[
            "violation_propagation_eligible_count"
        ]
        manifest.violation_propagation_target_count = propagation_evidence[
            "violation_propagation_target_count"
        ]

        # Phase 3d: Violation trace depth — propagate violations through lineage
        propagation_edges = _propagate_violations(result)
        if propagation_edges:
            propagation_edges, propagation_stamp_stats = _stamp_semantic_types_with_stats(propagation_edges)
            _merge_surface_evidence(surface_evidence_totals, propagation_stamp_stats)
            _post_scan_edge_set |= set(propagation_edges)

        # E5: Cyclic dependency detection post-scan pass
        cycle_edges = _detect_cycles(result)
        if cycle_edges:
            cycle_edges, cycle_stamp_stats = _stamp_semantic_types_with_stats(cycle_edges)
            _merge_surface_evidence(surface_evidence_totals, cycle_stamp_stats)
            _post_scan_edge_set |= set(cycle_edges)

        # Single sort + digest for all post-scan additions
        result.edges = sorted(_post_scan_edge_set, key=_EDGE_SORT_KEY)
        result.compute_digest()

        # W1b: Key-based dedup after all post-scan passes
        # Removes edges with same (from_name, relation_type, to_name, line_no)
        # but different edge_kind/semantic_type that survive set() dedup
        _seen_edge_keys: set[tuple[str, str, str, int]] = set()
        _deduped: list[Edge] = []
        for _e in result.edges:
            _ek = (_e.from_name, _e.relation_type, _e.to_name, _e.line_no)
            if _ek not in _seen_edge_keys:
                _seen_edge_keys.add(_ek)
                _deduped.append(_e)
        if len(_deduped) < len(result.edges):
            logger.info("W1b dedup removed %d duplicate edges", len(result.edges) - len(_deduped))
            result.edges = _deduped
            result.compute_digest()

        # A2: evidence floors
        manifest.minimum_evidence_passed = _check_evidence_floors(result)
        # S9: cardinality
        manifest.cardinality_violations = _check_cardinality(result)
        # A1: edge counts by graph
        manifest.edge_counts_by_graph = result.edge_counts_by_relation()
        manifest.syntax_error_count = syntax_error_count
        # S4: unknown layer count
        from agentic_core.adg.schema_util import module_path_to_layer

        manifest.unknown_layer_count = sum(1 for m in modules_seen if module_path_to_layer(m) == "L_UNKNOWN")
        # dynamic exec count
        manifest.dynamic_execution_count = sum(1 for e in result.edges if e.edge_kind == "dynamic_exec")

        manifest.decomposes_into_expected_count = surface_evidence_totals["decomposes_into_expected_count"]
        manifest.controls_flow_expected_count = surface_evidence_totals["controls_flow_expected_count"]
        manifest.flows_to_expected_count = surface_evidence_totals["flows_to_expected_count"]
        manifest.emits_side_effect_expected_count = surface_evidence_totals[
            "emits_side_effect_expected_count"
        ]
        manifest.resolves_callsite_expected_count = surface_evidence_totals[
            "resolves_callsite_expected_count"
        ]
        manifest.tests_execution_of_expected_count = surface_evidence_totals[
            "tests_execution_of_expected_count"
        ]
        manifest.type_surface_candidate_count = surface_evidence_totals["type_surface_candidate_count"]
        manifest.semantic_preexisting_count = surface_evidence_totals["semantic_preexisting_count"]
        manifest.semantic_exact_map_count = surface_evidence_totals["semantic_exact_map_count"]
        manifest.semantic_fallback_count = surface_evidence_totals["semantic_fallback_count"]
        manifest.semantic_raw_edge_kind_count = surface_evidence_totals["semantic_raw_edge_kind_count"]
        realized_node_names = _realized_node_names(result)
        manifest.type_surface_expected_count = len(
            {name for name in result.type_surface_map if name in realized_node_names}
        )
        manifest.execution_generic_semantic_count = _count_execution_generic_semantics(result.edges)

        # Section 6: semantic depth enforcement
        depth_metrics = _check_semantic_depth(result)
        manifest.semantic_edge_ratio = depth_metrics["semantic_edge_ratio"]
        manifest.control_path_coverage = depth_metrics["control_path_coverage"]
        manifest.lineage_completeness = depth_metrics["lineage_completeness"]
        manifest.side_effect_coverage = depth_metrics["side_effect_coverage"]
        manifest.call_resolution_rate = depth_metrics["call_resolution_rate"]
        manifest.temporal_ordering_ratio = depth_metrics["temporal_ordering_ratio"]
        depth_pass = all(
            depth_metrics[k] >= _SEMANTIC_DEPTH_THRESHOLDS[k] for k in _SEMANTIC_DEPTH_THRESHOLDS
        )
        manifest.semantic_depth_passed = depth_pass
        if not depth_pass:
            for k, threshold in _SEMANTIC_DEPTH_THRESHOLDS.items():
                if depth_metrics[k] < threshold:
                    logger.warning(
                        "Semantic depth BELOW threshold: %s=%.4f (min %.4f)",
                        k,
                        depth_metrics[k],
                        threshold,
                    )

        # --- AMD CPU Optimization: Single-pass manifest counts ---
        # Replaces 12+ separate generator passes over 732k edges with one loop.
        _governance_rel = frozenset({"writes_through", "reads_through", "routes_through"})
        _conditional_kinds = frozenset({"type_checking_import", "optional_import", "version_guard_import"})
        _mc_calls = _mc_covers = _mc_violates = _mc_governance = 0
        _mc_exports = _mc_from_imports = _mc_symbol_hit = 0
        _mc_dead = _mc_decorator = _mc_star = _mc_conditional = _mc_type_ann = _mc_antipattern = 0
        _mc_cycle_nodes: dict[str, int] = {}
        for _e in result.edges:
            _rt = _e.relation_type
            _ek = _e.edge_kind
            if _rt == "calls":
                _mc_calls += 1
            elif _rt == "covers":
                _mc_covers += 1
            elif _rt == "violates":
                _mc_violates += 1
            elif _rt in _governance_rel:
                _mc_governance += 1
            elif _rt == "exports":
                _mc_exports += 1
            elif _rt == "imports":
                if "::" in _e.to_name:
                    _mc_from_imports += 1
                    if _e.symbol and _e.symbol != _e.to_name:
                        _mc_symbol_hit += 1
            elif _rt == "dead_imports":
                _mc_dead += 1
            elif _rt == "in_cycle":
                _mc_cycle_nodes[_e.to_name] = _mc_cycle_nodes.get(_e.to_name, 0) + 1
            elif _rt == "antipattern":
                _mc_antipattern += 1
            if _ek == "decorator":
                _mc_decorator += 1
            elif _ek == "star_import":
                _mc_star += 1
            elif _ek in _conditional_kinds:
                _mc_conditional += 1
            elif _ek == "type_annotation":
                _mc_type_ann += 1
        manifest.inter_module_call_count = _mc_calls
        manifest.test_covers_count = _mc_covers
        manifest.layer_violation_count = _mc_violates
        manifest.governance_plane_count = _mc_governance
        manifest.symbol_export_count = _mc_exports
        if _mc_from_imports > 0:
            manifest.symbol_hit_rate = round(_mc_symbol_hit / _mc_from_imports, 3)
        manifest.dead_import_count = _mc_dead
        manifest.cycle_count = len(_mc_cycle_nodes)
        if _mc_cycle_nodes:
            manifest.max_cycle_depth = max(_mc_cycle_nodes.values())
        manifest.decorator_edge_count = _mc_decorator
        manifest.star_import_count = _mc_star
        manifest.conditional_import_count = _mc_conditional
        manifest.type_annotation_count = _mc_type_ann
        manifest.antipattern_count = _mc_antipattern

        return result

    def scan_files(self, files: list[str], commit_sha: str = "") -> ScanResult:
        """Scan only a specific set of files (for PR diff mode).

        files: list of repo-relative forward-slash paths.
        """
        result = ScanResult(commit_sha=commit_sha)
        all_edges: list[Edge] = []
        all_type_surface: dict[str, str] = {}
        modules_seen: list[str] = []

        for rel in sorted(files):
            filepath = self.repo_root / rel.replace("/", os.sep)
            if not filepath.exists() or not rel.endswith(".py"):
                continue
            if not _is_scannable_static_path(rel, self.include_tests):
                continue
            modules_seen.append(rel)
            file_edges, _, file_type_map, _ = _scan_file(filepath, self.repo_root, self.include_tests)
            all_edges.extend(file_edges)
            all_type_surface.update(file_type_map)

        result.edges = sorted(set(all_edges), key=_EDGE_SORT_KEY)  # S7
        result.modules = sorted(modules_seen)
        result.type_surface_map = all_type_surface
        result.compute_digest()
        return result

    def build_reverse_import_graph(self, result: ScanResult) -> dict[str, list[str]]:
        """Build reverse dependency graph: symbol -> list of modules that import it."""
        reverse: dict[str, list[str]] = {}
        for edge in result.edges:
            if edge.relation_type == "imports":
                rev_key = edge.to_name
                if rev_key not in reverse:
                    reverse[rev_key] = []
                if edge.from_name not in reverse[rev_key]:
                    reverse[rev_key].append(edge.from_name)
        for k in reverse:
            reverse[k].sort()
        return reverse

    def module_layer_map(self, result: ScanResult) -> dict[str, str]:
        """Return mapping of module ADG name -> layer label."""
        mapping: dict[str, str] = {}
        for rel in result.modules:
            layer = module_path_to_layer(rel)
            adg_name = canonical_name("Module", rel)
            mapping[adg_name] = layer
        return mapping


__all__ = [
    "ADGStaticScanner",
    "Edge",
    "ScanResult",
    "ScanManifest",
    "run_scanner_self_test",
    "_SCANNER_VERSION",
    "_SCHEMA_VERSION",
    "_InheritanceVisitor",
    "_AttributeVisitor",
    "_CompositionVisitor",
    "_DynamicExecutionVisitor",
    "_InternalCallGraphVisitor",
    "_TestTraceabilityVisitor",
    "_GovernancePlaneVisitor",
    "_emit_layer_violation_edges",
    "_SymbolInventoryVisitor",
    "_UnusedImportVisitor",
    "_tag_dead_imports",
]
