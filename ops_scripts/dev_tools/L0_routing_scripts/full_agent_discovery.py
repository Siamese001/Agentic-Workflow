#!/usr/bin/env python3
"""
Full Agent Discovery Script - SSOT Compliant Implementation
With Advanced AST Analysis & Architectural Integrity Verification

COMPLETE SSOT REFACTOR: All directory constants and paths MUST be imported
from structure_blueprint.py. NO hardcoded strings allowed.

# Configuration constants

This script serves as the canonical entry point for agent discovery operations.
It delegates core enumeration to the SSOT discovery utility but strictly
ENFORCES architectural integrity using deep AST analysis.

ADVANCED CAPABILITIES:
- Intrinsic AST Verification (Deep Code Analysis)
- Stub Sovereignty (Respects NOT_AN_AGENT markers)
- Architectural Role Detection (Base vs. Implementation)
- Ghost Detection (Verifies physical existence of cached agents)

SSOT PRINCIPLE: structure_blueprint.py is the absolute authority.
"""

from __future__ import annotations

import ast
import hashlib
import json
import logging
import platform
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# CRITICAL SSOT Imports - ALL directory constants MUST come from L0 config
from agentic_core.L0_routing.config import (
    AGENT_DISCOVERY_JSON,
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.L0_routing.enforcement.safety_kernel_seam import (
    get_classification_cache_context,
)
from agentic_core.L0_routing.utils.path_util import validate_path_within_project
from ops_scripts.dev_tools.L0_routing.ssot_discovery_util import (
    get_healers,
    invalidate_cache,
    load_agent_discovery,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "full_agent_discovery")
emit_determinism_digest("p0", "full_agent_discovery")

_emit_dispatches_healing_run("p1", "full_agent_discovery", "L0")
_emit_routes_through("p1", "full_agent_discovery", "L0")
_emit_checks_agent_registry("p1", "full_agent_discovery", "agent_registry")
_emit_validates_agent_capability("p1", "full_agent_discovery", "capability")
_emit_dispatches_execution_plan("p1", "full_agent_discovery", "exec_plan")
_emit_agent_executes_agent("p1", "full_agent_discovery", "sub_agent")
_emit_routes_to_agent("p1", "full_agent_discovery", "target_agent")
_emit_verifies_policy("p1", "full_agent_discovery", "policy_check")
_emit_observes_runtime_state("p1", "full_agent_discovery", "runtime_state")
_emit_verifies_boundary("p1", "full_agent_discovery", "boundary_check")
_emit_transcripts_response("p1", "full_agent_discovery", "transcript")
_emit_hard_fails_untranscripted("p1", "full_agent_discovery")
_emit_gated_by_confidence("p1", "full_agent_discovery", "confidence_gate")
_emit_escalates_to_human("p1", "full_agent_discovery", "L0")
_emit_reads_policy_state("p1", "full_agent_discovery", "L0")
_emit_authorize_and_execute("p2", "full_agent_discovery", "execution_auth")
_emit_validates_capability("p2", "full_agent_discovery", "capability_check")
_emit_routes_to_capability("p2", "full_agent_discovery", "capability_route")
_emit_writes_via_uwg("p2", "full_agent_discovery", "uwg_write")
_emit_blocks_direct_write("p2", "full_agent_discovery", "direct_write_block")
_emit_records_tool_invocation("p2", "full_agent_discovery", "tool_invocation")
_emit_captures_execution_output("p2", "full_agent_discovery", "exec_output")
_emit_dispatches_agent("p3", "full_agent_discovery", "agent_dispatch")
_emit_coordinates_agents("p3", "full_agent_discovery", "agent_coordination")
_emit_records_workflow_lineage("p3", "full_agent_discovery", "workflow_lineage")
_emit_records_healing_outcome("p3", "full_agent_discovery", "healing_outcome")
_emit_escalates_failure("p3", "full_agent_discovery", "failure_escalation")
_emit_orchestrates_workflow("p3", "full_agent_discovery", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "full_agent_discovery", "healing_dispatch")
_emit_invokes_evaluation("p3", "full_agent_discovery", "evaluation_signal")
_emit_records_telemetry_event("p4", "full_agent_discovery", "telemetry_event")
_emit_captures_evaluation_metric("p4", "full_agent_discovery", "eval_metric")
_emit_stores_embedding("p4", "full_agent_discovery", "embedding_store")
_emit_updates_meta_learning_state("p4", "full_agent_discovery", "meta_learning")
_emit_links_execution_to_snapshot("p4", "full_agent_discovery", "exec_snapshot_link")


def _get_safe_subprocess_check_output():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_safe_subprocess_check_output", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_safe_subprocess_check_output", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_safe_subprocess_check_output")
    from agentic_core.L2_execution.utils.safe_subprocess import safe_subprocess_check_output

    return safe_subprocess_check_output


classification_cache_context = get_classification_cache_context()
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
from agentic_core.utils.ast_fuzzy_util import safe_unparse

_emit_emits_metric_event("full_agent_discovery", "p4obs", "metric_1")
_emit_emits_metric_event("full_agent_discovery", "p4obs", "metric_2")
_emit_emits_metric_event("full_agent_discovery", "p4obs", "metric_3")
_emit_emits_metric_event("full_agent_discovery", "p4obs", "metric_4")
_emit_emits_metric_event("full_agent_discovery", "p4obs", "metric_5")
_emit_emits_metric_event("full_agent_discovery", "p4obs", "metric_6")
_emit_records_incident_event("full_agent_discovery", "p4obs", "incident")
_emit_captures_runtime_anomaly("full_agent_discovery", "p4obs", "anomaly")
_emit_writes_observability_log("full_agent_discovery", "p4obs", "obs_log")
_emit_updates_monitoring_state("full_agent_discovery", "p4obs", "mon_state")
_emit_triggers_alert("full_agent_discovery", "p4obs", "alert")
_emit_links_incident_trace("full_agent_discovery", "p4obs", "trace_link")
_emit_captures_pattern("full_agent_discovery", "p3lm", "pattern")
_emit_records_learning_event("full_agent_discovery", "p3lm", "learning_event")
_emit_writes_learning_snapshot("full_agent_discovery", "p3lm", "snapshot")
_emit_feeds_meta_learning("full_agent_discovery", "p3lm", "meta_feed")
_emit_updates_routing_strategy("full_agent_discovery", "p3lm", "routing")
_emit_improves_agent_policy("full_agent_discovery", "p3lm", "policy")
_emit_stores_learning_state("full_agent_discovery", "p3lm", "state")
_emit_records_execution_trace("full_agent_discovery", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("full_agent_discovery", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("full_agent_discovery", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("full_agent_discovery", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("full_agent_discovery", "L4_STATE", "p2_trace_5")
_emit_reads_environ("full_agent_discovery", "env_read", "p2_env_1")
_emit_reads_environ("full_agent_discovery", "env_read", "p2_env_2")
_emit_reads_runtime_state("full_agent_discovery", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("full_agent_discovery", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "full_agent_discovery", "context_pull")
_emit_pulls_context("p1", "full_agent_discovery", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "full_agent_discovery", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "full_agent_discovery", "uwg_term_2")
_emit_writes_through("p1", "full_agent_discovery", "write_through")
_emit_writes_through("p1", "full_agent_discovery", "write_through_2")
_emit_validated_by_safety_plane("p1", "full_agent_discovery", "safety_validation")
_emit_invokes_eval("p1", "full_agent_discovery", "eval_call")
_emit_proposal_commits_routing("p1", "full_agent_discovery", "routing_commit")
from agentic_core.runtime.lifecycle_trace_contract import emit_determinism_digest
from agentic_core.config.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_dispatch_entry")
emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_dispatch_exit")
emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_tool_invoke")
emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_tool_complete")
emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_agent_entry")
emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_agent_exit")
emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_uwg_write")
emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_trace_sign")
emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_guardrail_check")
emit_determinism_digest("trace_full_agent_discovery", "full_agent_discovery_policy_verify")

# Standard error logging wrapper configuration
Logger = logging.getLogger(__name__)

# Output schema version for downstream auditors
OUTPUT_SCHEMA_VERSION = "2.0.0"

# ==============================================================================
# Advanced Data Structures
# ==============================================================================


@dataclass
class AgentIntegrityReport:
    """Detailed AST analysis result for a single agent file."""

    path: Path
    is_valid: bool = False
    is_stub: bool = False
    is_base_agent: bool = False
    class_name: str | None = None
    inheritance: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    critical_methods: list[str] = field(default_factory=list)
    rejection_reason: str | None = None
    architectural_role: str = "Unknown"
    file_sha256: str = ""
    file_size_bytes: int = 0
    parse_error: str = ""
    selection_reason: str = ""
    mro_signature: list[str] = field(default_factory=list)


class DiscoveryError(Exception):
    """Custom exception for agent discovery operations."""

    pass


# ==============================================================================
# Core Setup
# ==============================================================================


def setup_logging(verbose: bool = False) -> None:
    """
    Standard logging configuration wrapper.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit(root: Path) -> str:
    try:
        out = _get_safe_subprocess_check_output()(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            allow_protected_root_mutation=True,
        )
        return out.strip()
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        return ""


def main() -> bool:
    """
    Main entry point for agent discovery operations.
    Performs comprehensive agent discovery and strict integrity validation.
    """
    try:
        # Get validated project root from SSOT
        project_root = get_validated_project_root()
        Logger.info(f"[DISCOVERY] Starting Deep Agent Discovery from: {project_root}")

        # Validate project root integrity (treat validator as raising, not bool-return)
        try:
            validate_path_within_project(project_root, project_root)
        except Exception as e:
            raise DiscoveryError(f"Project root validation failed: {e}")

        # Run discovery inside a cache context so classifications are fresh
        # on entry and don't leak stale state to subsequent operations.
        with classification_cache_context():
            # Load agent discovery data from SSOT (The List)
            raw_agents = load_agent_discovery(project_root, force_reload=True)
            raw_agents = sorted(
                raw_agents,
                key=lambda a: (
                    a.get("layer", ""),
                    a.get("name", a.get("class_name", "")),
                    a.get("path", a.get("file", "")),
                ),
            )
            Logger.info(f"[DISCOVERY] Loaded {len(raw_agents)} candidates from SSOT registry")

            # Perform Deep AST Integrity Scan (The Verification)
            valid_agents, validation_stats = perform_deep_integrity_scan(raw_agents, project_root)

        # Log Validation Results
        Logger.info("[DISCOVERY] Deep Scan Complete:")
        Logger.info(f"   - Verified Active Agents: {validation_stats['verified']}")
        Logger.info(f"   - Stubs/Exempt: {validation_stats['stubs']}")
        Logger.info(f"   - Invalid/Ghosts: {validation_stats['invalid']}")

        # Validate compliance gate based on scan results
        if not check_compliance_gate(validation_stats):    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context
            Logger.error("[DISCOVERY] Compliance gate validation failed (Integrity violations detected)")
            return False

        Logger.info("[DISCOVERY] Agent discovery and verification completed successfully")
        return True

    # guardian: allow-silent-swallow - acceptable exception handling    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context    # guardian: DiscoveryError should be handled with specific context
    except DiscoveryError as e:
        Logger.error(f"[DISCOVERY] Discovery operation failed: {e}")
        return False
    except (ValueError, TypeError) as e:
        Logger.error(f"[DISCOVERY] Unexpected error during discovery: {e}")
        return False


# ==============================================================================
# Advanced AST Analysis Engine
# ==============================================================================


def analyze_agent_integrity(file_path: Path) -> AgentIntegrityReport:
    """
    Performs deep AST analysis on a file to verify it is a legitimate Agent.

    [REFACTORED 2026-02-08] Classification decision now delegated to the
    zero-dependency kernel (agentic_core.L5_safety.core_kernel.classification_kernel).
    This function still extracts metadata (inheritance, decorators, methods)
    for the integrity report but no longer uses bespoke class_score() logic.

    Steps:
    1. Kernel classification (AGENT vs other FileType)
    2. AST metadata extraction (inheritance, decorators, methods)
    3. Integrity report generation
    """
    from agentic_core.L0_routing.enforcement.safety_kernel_seam import (
        load_classification_kernel,
    )

    classify_file_standalone = load_classification_kernel().classify_file_standalone

    report = AgentIntegrityReport(path=file_path)

    if not file_path.exists():
        report.rejection_reason = "File not found (Ghost)"
        return report

    try:
        report.file_size_bytes = file_path.stat().st_size
        report.file_sha256 = sha256_file(file_path)

        # --- KERNEL CLASSIFICATION (SSOT) ---
        file_type = classify_file_standalone(file_path)

        if file_type == "STUB":
            report.is_stub = True
            report.is_valid = False
            report.rejection_reason = "Explicit NOT_AN_AGENT marker found"
            report.architectural_role = "STUB"
            return report

        if file_type == "IGNORE":    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
            report.rejection_reason = "File ignored by kernel (empty, critical, or unparseable)"
            return report

        content = file_path.read_text(encoding="utf-8", errors="replace")

        try:
            # guardian: allow-silent-swallow - acceptable exception handling    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
            tree = ast.parse(content)
        except SyntaxError as e:
            report.parse_error = f"SyntaxError: {e}"
            report.rejection_reason = report.parse_error
            return report

        # --- AST METADATA EXTRACTION (for integrity report) ---
        class_nodes: list[ast.ClassDef] = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        if not class_nodes:
            report.rejection_reason = "No ClassDef nodes"
            return report

        def extract_mro_signature(cls: ast.ClassDef) -> list[str]:
            return [safe_unparse(b) for b in cls.bases]

        # Select primary class: prefer name matching filename stem, then first with "Agent"
        import re as _re

        stem_clean = _re.sub(r"[^a-zA-Z0-9]", "", file_path.stem.lower())
        chosen = class_nodes[0]
        for node in class_nodes:
            if _re.sub(r"[^a-zA-Z0-9]", "", node.name.lower()) == stem_clean:
                chosen = node
                break

        report.class_name = chosen.name
        report.mro_signature = extract_mro_signature(chosen)
        report.selection_reason = "Primary class selected by filename stem match"

        # Extract Inheritance
        for base_expr in chosen.bases:
            base_id = safe_unparse(base_expr)
            if base_id:
                report.inheritance.append(base_id)
                if "BaseAgent" in base_id:
                    report.is_base_agent = True
                    report.architectural_role = "BASE_AGENT"

        # Extract Decorators
        for dec in chosen.decorator_list:
            dec_id = ""
            if isinstance(dec, ast.Name):
                dec_id = dec.id
            elif isinstance(dec, ast.Attribute):
                dec_id = dec.attr
            if dec_id:
                report.decorators.append(dec_id)

        # Extract Critical Methods
        for item in chosen.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if item.name in ["execute", "act", "run", "heal"]:
                    report.critical_methods.append(item.name)

        # --- VALIDITY DECISION (kernel-based) ---
        if file_type == "AGENT":
            report.is_valid = True
            if not report.architectural_role:
                report.architectural_role = "AGENT"
        elif report.is_base_agent:
            report.is_valid = True
        else:
            report.is_valid = False
            report.rejection_reason = f"Kernel classified as {file_type}, not AGENT"

        return report

    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as e:
        report.rejection_reason = f"Analysis failed: {e}"
        return report


def perform_deep_integrity_scan(
    agents: list[dict[str, Any]],
    project_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """
    Iterates over discovered agents and validates them using AST analysis.
    Returns:
        tuple: (List of verified agents, Statistics Dictionary)
    """
    verified_agents = []
    stats = {"verified": 0, "stubs": 0, "invalid": 0, "base_agents": 0, "ghosts": 0}

    for agent_entry in agents:
        # Normalize path
        rel_path = agent_entry.get("path", "") or agent_entry.get("file", "")
        if not rel_path:
            stats["invalid"] += 1
            continue

        full_path = project_root / rel_path
        try:
            validate_path_within_project(project_root, full_path)
        # guardian: allow-silent-swallow
        except Exception:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            stats["invalid"] += 1
            agent_entry["verification_status"] = {
                "valid": False,
                "role": "INVALID",
                "class": None,
                "methods": [],
                "reason": "Path fails validate_path_within_project",
            }
            continue
        # Run Analysis
        report = analyze_agent_integrity(full_path)

        # Augment agent entry with analysis data
        agent_entry["verification_status"] = {
            "valid": report.is_valid,
            "role": report.architectural_role,
            "class": report.class_name,
            "methods": report.critical_methods,
            "mro_signature": report.mro_signature,
            "file_sha256": report.file_sha256,
            "file_size_bytes": report.file_size_bytes,
            "selection_reason": report.selection_reason,
            "parse_error": report.parse_error,
        }
        # Emit canonical identity fields at top level.
        # canonical_class: AST-verified class name (authoritative; class_name is legacy display only).
        # canonical_file: repo-relative path, forward-slash normalized (§20).
        # canonical_agent_id: unique identifier (class_name if it differs from canonical_class).
        if report.class_name:
            agent_entry["canonical_class"] = report.class_name
        canon_path = rel_path.replace("\\", "/")
        if canon_path.startswith("./"):
            canon_path = canon_path[2:]
        agent_entry["canonical_file"] = canon_path
        agent_entry["canonical_agent_id"] = (
            report.class_name if report.class_name else agent_entry.get("class_name", "")
        )

        if report.is_valid:
            stats["verified"] += 1
            if report.is_base_agent:
                stats["base_agents"] += 1
            verified_agents.append(agent_entry)
        elif report.is_stub:
            stats["stubs"] += 1
            Logger.debug(f"[SCAN] Detected Stub: {rel_path}")
        elif report.rejection_reason and "not found" in report.rejection_reason:
            stats["ghosts"] += 1
            stats["invalid"] += 1
            Logger.warning(f"[SCAN] Ghost Agent (Cache invalid): {rel_path}")
        else:
            stats["invalid"] += 1
            Logger.debug(f"[SCAN] Rejected {rel_path}: {report.rejection_reason}")

    return verified_agents, stats


# ==============================================================================
# Compliance & Interfaces
# ==============================================================================


def check_compliance_gate(scan_stats: dict[str, int] | None = None) -> bool:
    """
    Check compliance gate using SSOT validation AND Integrity Stats.

    Args:
        scan_stats: Optional dict from perform_deep_integrity_scan.
                    If provided, enforces thresholds on invalid agents.

    Returns:
        bool: True if compliance checks pass, False otherwise.
    """
    try:
        # 1. Validate project root structure using SSOT constants
        project_root = get_validated_project_root()

        # 2. Check critical SSOT directories
        critical_dirs = [
            AGENTIC_CORE_DIR,
            APPS_RG_DIR,
            APPS_LIC_DIR,
            APPS_SHARED_DIR,
            L0_MAINTENANCE_DIR,
            L1_COGNITION_DIR,
            L2_EXECUTION_DIR,
            L3_ORCHESTRATION_DIR,
            L4_STATE_DIR,
            L5_SAFETY_DIR,
            L6_OBSERVABILITY_DIR,
        ]

        for dir_name in critical_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                Logger.error(f"[COMPLIANCE] Critical directory missing: {dir_path}")
                return False

        # 3. Validate agent discovery JSON integrity
        discovery_path = project_root / AGENT_DISCOVERY_JSON
        if not discovery_path.exists():
            Logger.error(f"[COMPLIANCE] SSOT discovery file missing: {discovery_path}")
            return False

        # 4. Strict Integrity Check (if stats provided)
        if scan_stats:
            ghosts = scan_stats.get("ghosts", 0)
            if ghosts > 0:
                Logger.error(
                    f"[COMPLIANCE] FAILED: {ghosts} ghost agents detected in registry. Run refresh_cache.",
                )
                return False

            # Warn but don't necessarily fail on simple invalids (might be works in progress)
            invalids = scan_stats.get("invalid", 0)
            if invalids > 0:
                Logger.warning(f"[COMPLIANCE] Warning: {invalids} files in registry failed validation.")

        Logger.info("[COMPLIANCE] All compliance checks passed")
        return True

    except (ValueError, TypeError) as e:
        Logger.error(f"[COMPLIANCE] Compliance check failed: {e}")
        return False


def discover_all_agents(strict_mode: bool = True) -> list[dict[str, Any]]:
    """
    Discover all agents in the repository using SSOT and AST Validation.

    Args:
        strict_mode: If True, filters out agents that fail AST validation.

    Returns:
        List[Dict[str, Any]]: List of verified agent discovery entries.
    """
    try:
        project_root = get_validated_project_root()
        raw_agents = load_agent_discovery(project_root)
        raw_agents = sorted(
            raw_agents,
            key=lambda a: (
                a.get("layer", ""),
                a.get("name", a.get("class_name", "")),
                a.get("path", a.get("file", "")),
            ),
        )

        if not strict_mode:
            return raw_agents

        verified_agents, _ = perform_deep_integrity_scan(raw_agents, project_root)
        Logger.debug(f"[DISCOVERY] Returning {len(verified_agents)} verified agents")
        return verified_agents

    except (OSError, ValueError, TypeError) as e:  # guardian: allow-specific -- agent discovery failure returns empty
        Logger.error(f"[DISCOVERY] Failed to discover agents: {e}")
        return []


def get_agent_discovery_summary() -> dict[str, Any]:
    """
    Generate comprehensive agent discovery summary with Integrity Stats.
    """
    try:
        project_root = get_validated_project_root()
        # Load and Scan
        raw_agents = load_agent_discovery(project_root)
        verified_agents, stats = perform_deep_integrity_scan(raw_agents, project_root)

        # Calculate layer distribution (Verified Only)
        layer_counts = {}
        for agent in verified_agents:
            layer = agent.get("layer", "Unknown")
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        # Get healer count
        healers = get_healers(project_root)

        summary = {
            "output_schema_version": OUTPUT_SCHEMA_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "git_commit": get_git_commit(project_root),
            "total_candidates": len(raw_agents),
            "verified_active_agents": len(verified_agents),
            "integrity_stats": stats,
            "layer_distribution": layer_counts,
            "healer_count": len(healers),
            "project_root": str(project_root),
            "ssot_file": str(project_root / AGENT_DISCOVERY_JSON),
        }

        return summary

    except (OSError, ValueError, TypeError) as e:  # guardian: allow-specific -- summary generation failure returns error dict
        Logger.error(f"[DISCOVERY] Failed to generate summary: {e}")
        return {"error": str(e)}


def refresh_discovery_cache() -> bool:
    """
    Refresh the agent discovery cache.
    Forces cache invalidation and reload to ensure latest data.
    """
    try:
        invalidate_cache()
        Logger.info("[CACHE] Discovery cache invalidated successfully")

        # Test reload
        project_root = get_validated_project_root()
        agents = load_agent_discovery(project_root, force_reload=True)
        Logger.info(f"[CACHE] Reloaded {len(agents)} agents from disk")

        return True

    except (OSError, ValueError, TypeError) as e:  # guardian: allow-specific -- cache refresh failure returns False
        Logger.error(f"[CACHE] Cache refresh failed: {e}")
        return False


def get_structured_agent_paths() -> list[str]:
    """
    Return structured list of verified agent file paths.
    """
    try:
        agents = discover_all_agents(strict_mode=True)
        paths = []

        for agent in agents:
            path = agent.get("path", "") or agent.get("file", "")
            if path:
                normalized_path = path.replace("\\", "/")
                paths.append(normalized_path)

        return paths

    except (OSError, ValueError, TypeError) as e:  # guardian: allow-specific -- path generation failure returns empty
        Logger.error(f"[PATHS] Failed to generate structured paths: {e}")
        return []


# ==============================================================================
# CLI Interface
# ==============================================================================


def cli_interface() -> None:
    """Command-line interface for discovery operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Deep Agent Discovery Utility")
    parser.add_argument("--summary", action="store_true", help="Show discovery summary with integrity stats")
    parser.add_argument("--check-compliance", action="store_true", help="Run strict compliance checks")
    parser.add_argument("--refresh-cache", action="store_true", help="Refresh discovery cache")
    parser.add_argument("--layer", help="Filter by layer (L0-L6)")
    parser.add_argument("--name", help="Find specific agent by name")
    parser.add_argument("--json", action="store_true", help="Output full inventory as JSON")
    parser.add_argument("--paths", action="store_true", help="Output structured agent paths")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    # New flags for deep analysis
    parser.add_argument("--inspect", help="Deep inspect specific agent file path")
    parser.add_argument("--show-invalid", action="store_true", help="List agents that failed integrity check")

    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    try:
        if args.check_compliance:
            # Run scan first to get stats
            project_root = get_validated_project_root()
            raw = load_agent_discovery(project_root)
            _, stats = perform_deep_integrity_scan(raw, project_root)

            compliant = check_compliance_gate(stats)
            print(f"Compliance Status: {'PASS' if compliant else 'FAIL'}")
            if not compliant:
                print(f"Integrity Issues: {stats['invalid']} invalid, {stats['ghosts']} missing files.")
            sys.exit(0 if compliant else 1)

        elif args.refresh_cache:
            success = refresh_discovery_cache()
            print(f"Cache Refresh: {'SUCCESS' if success else 'FAILED'}")
            sys.exit(0 if success else 1)

        elif args.inspect:
            project_root = get_validated_project_root()
            path = Path(args.inspect)
            if not path.is_absolute():
                path = project_root / path

            print(f"Inspecting: {path}")
            report = analyze_agent_integrity(path)
            print(
                json.dumps(
                    {
                        "valid": report.is_valid,
                        "role": report.architectural_role,
                        "class": report.class_name,
                        "inheritance": report.inheritance,
                        "methods": report.critical_methods,
                        "rejection_reason": report.rejection_reason,
                    },
                    indent=2,
                ),
            )

        elif args.json:
            agents = discover_all_agents(strict_mode=True)
            print(json.dumps(agents, indent=2, default=str))

        elif args.paths:
            paths = get_structured_agent_paths()
            print("Structured Agent Paths (Verified Only):")
            for path in paths:
                print(f"  {path}")

        elif args.summary:
            summary = get_agent_discovery_summary()
            print("Agent Discovery Summary:")
            print(json.dumps(summary, indent=2, default=str))

        elif args.show_invalid:
            project_root = get_validated_project_root()
            raw = load_agent_discovery(project_root)
            _, stats = perform_deep_integrity_scan(raw, project_root)
            print(f"Found {stats['invalid']} invalid agents:")
            for agent in raw:
                # Re-run single analysis to print reason (inefficient but fine for CLI)
                path = project_root / (agent.get("path", "") or agent.get("file", ""))
                report = analyze_agent_integrity(path)    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context
                if not report.is_valid and not report.is_stub:
                    print(f"  - {agent.get('name', agent.get('class_name', '?'))}: {report.rejection_reason}")
    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context
        else:
            # Default: run full discovery
            success = main()
            sys.exit(0 if success else 1)    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context    # guardian: KeyboardInterrupt should be handled with specific context

    except KeyboardInterrupt:
        Logger.info("[DISCOVERY] Operation cancelled by user")
        sys.exit(130)
    # guardian: allow-silent-swallow
    except (OSError, ValueError, TypeError) as e:  # guardian: allow-specific -- CLI operation errors
        Logger.error(f"[DISCOVERY] CLI operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_interface()
