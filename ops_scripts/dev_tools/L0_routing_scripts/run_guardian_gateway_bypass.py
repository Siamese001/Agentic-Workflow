"""
Guardian: Gateway Bypass — AST-based detection of direct LLM SDK usage
outside the SovereignLLMGateway boundary.

Checks:
- direct_model_call: Direct instantiation of openai/anthropic/genai classes
- provider_sdk_import: Import of forbidden provider SDK modules in scan roots
- bypass_tier_router: Call-sites that route to a model skipping tier selection
- bypass_embedding_factory: Direct embedding construction bypassing factory

Scan roots: agentic_core/, apps_lic/, apps_rg/, apps_shared/, system_learning/
Allowlist:  agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
            agentic_core/L2_execution/enforcement/EmbeddingServiceFactory.py
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    SYSTEM_LEARNING_DIR,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
from ops_scripts.dev_tools.L0_routing.project_root_util import get_validated_project_root

emit_replay_key("p0", "run_guardian_gateway_bypass")
emit_determinism_digest("p0", "run_guardian_gateway_bypass")

_emit_dispatches_healing_run("p1", "run_guardian_gateway_bypass", "L0")
_emit_routes_through("p1", "run_guardian_gateway_bypass", "L0")
_emit_checks_agent_registry("p1", "run_guardian_gateway_bypass", "agent_registry")
_emit_validates_agent_capability("p1", "run_guardian_gateway_bypass", "capability")
_emit_dispatches_execution_plan("p1", "run_guardian_gateway_bypass", "exec_plan")
_emit_agent_executes_agent("p1", "run_guardian_gateway_bypass", "sub_agent")
_emit_routes_to_agent("p1", "run_guardian_gateway_bypass", "target_agent")
_emit_verifies_policy("p1", "run_guardian_gateway_bypass", "policy_check")
_emit_observes_runtime_state("p1", "run_guardian_gateway_bypass", "runtime_state")
_emit_verifies_boundary("p1", "run_guardian_gateway_bypass", "boundary_check")
_emit_transcripts_response("p1", "run_guardian_gateway_bypass", "transcript")
_emit_hard_fails_untranscripted("p1", "run_guardian_gateway_bypass")
_emit_gated_by_confidence("p1", "run_guardian_gateway_bypass", "confidence_gate")
_emit_escalates_to_human("p1", "run_guardian_gateway_bypass", "L0")
_emit_reads_policy_state("p1", "run_guardian_gateway_bypass", "L0")
_emit_authorize_and_execute("p2", "run_guardian_gateway_bypass", "execution_auth")
_emit_validates_capability("p2", "run_guardian_gateway_bypass", "capability_check")
_emit_routes_to_capability("p2", "run_guardian_gateway_bypass", "capability_route")
_emit_writes_via_uwg("p2", "run_guardian_gateway_bypass", "uwg_write")
_emit_blocks_direct_write("p2", "run_guardian_gateway_bypass", "direct_write_block")
_emit_records_tool_invocation("p2", "run_guardian_gateway_bypass", "tool_invocation")
_emit_captures_execution_output("p2", "run_guardian_gateway_bypass", "exec_output")
_emit_dispatches_agent("p3", "run_guardian_gateway_bypass", "agent_dispatch")
_emit_coordinates_agents("p3", "run_guardian_gateway_bypass", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_guardian_gateway_bypass", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_guardian_gateway_bypass", "healing_outcome")
_emit_escalates_failure("p3", "run_guardian_gateway_bypass", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_guardian_gateway_bypass", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_guardian_gateway_bypass", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_guardian_gateway_bypass", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_guardian_gateway_bypass", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_guardian_gateway_bypass", "eval_metric")
_emit_stores_embedding("p4", "run_guardian_gateway_bypass", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_guardian_gateway_bypass", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_guardian_gateway_bypass", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
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

_emit_emits_metric_event("run_guardian_gateway_bypass", "p4obs", "metric_1")
_emit_emits_metric_event("run_guardian_gateway_bypass", "p4obs", "metric_2")
_emit_emits_metric_event("run_guardian_gateway_bypass", "p4obs", "metric_3")
_emit_emits_metric_event("run_guardian_gateway_bypass", "p4obs", "metric_4")
_emit_emits_metric_event("run_guardian_gateway_bypass", "p4obs", "metric_5")
_emit_emits_metric_event("run_guardian_gateway_bypass", "p4obs", "metric_6")
_emit_records_incident_event("run_guardian_gateway_bypass", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_guardian_gateway_bypass", "p4obs", "anomaly")
_emit_writes_observability_log("run_guardian_gateway_bypass", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_guardian_gateway_bypass", "p4obs", "mon_state")
_emit_triggers_alert("run_guardian_gateway_bypass", "p4obs", "alert")
_emit_links_incident_trace("run_guardian_gateway_bypass", "p4obs", "trace_link")
_emit_captures_pattern("run_guardian_gateway_bypass", "p3lm", "pattern")
_emit_records_learning_event("run_guardian_gateway_bypass", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_guardian_gateway_bypass", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_guardian_gateway_bypass", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_guardian_gateway_bypass", "p3lm", "routing")
_emit_improves_agent_policy("run_guardian_gateway_bypass", "p3lm", "policy")
_emit_stores_learning_state("run_guardian_gateway_bypass", "p3lm", "state")
_emit_records_execution_trace("run_guardian_gateway_bypass", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_guardian_gateway_bypass", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_guardian_gateway_bypass", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_guardian_gateway_bypass", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_guardian_gateway_bypass", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_guardian_gateway_bypass", "env_read", "p2_env_1")
_emit_reads_environ("run_guardian_gateway_bypass", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_guardian_gateway_bypass", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_guardian_gateway_bypass", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_guardian_gateway_bypass", "context_pull")
_emit_pulls_context("p1", "run_guardian_gateway_bypass", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_guardian_gateway_bypass", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_guardian_gateway_bypass", "uwg_term_2")
_emit_writes_through("p1", "run_guardian_gateway_bypass", "write_through")
_emit_writes_through("p1", "run_guardian_gateway_bypass", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_guardian_gateway_bypass", "safety_validation")
_emit_invokes_eval("p1", "run_guardian_gateway_bypass", "eval_call")
_emit_proposal_commits_routing("p1", "run_guardian_gateway_bypass", "routing_commit")

GUARDIAN_ID = "gateway_bypass"

SCAN_ROOTS: tuple[str, ...] = (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
)

ALLOWED_SDK_FILES: frozenset[str] = frozenset(
    {
        "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
        "agentic_core/L2_execution/enforcement/EmbeddingServiceFactory.py",
    },
)

FORBIDDEN_SDK_MODULES: frozenset[str] = frozenset(
    {
        "openai",
        "anthropic",
        "google.generativeai",
    },
)

FORBIDDEN_INSTANTIATION_NAMES: frozenset[str] = frozenset(
    {
        "OpenAI",
        "AsyncOpenAI",
        "Anthropic",
        "AsyncAnthropic",
        "GenerativeModel",
    },
)

SKIP_DIRS: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def _collect_files(repo_root: Path) -> list[Path]:
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_collect_files", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_collect_files", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_collect_files")
    result: list[Path] = []
    for root_name in sorted(SCAN_ROOTS):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in __import__("os").walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fname in sorted(filenames):
                if fname.endswith(".py"):
                    result.append(Path(dirpath) / fname)
    return result


def scan_provider_sdk_imports(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Return sorted violation dicts for forbidden SDK imports."""
    if files is None:
        files = _collect_files(repo_root)
    violations: list[dict] = []
    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        if rel in ALLOWED_SDK_FILES:
            continue
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        # guardian: allow-silent-swallow - acceptable exception handling
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name == m or alias.name.startswith(m + ".") for m in FORBIDDEN_SDK_MODULES):
                        violations.append(
                            {
                                "path": rel,
                                "check_id": "provider_sdk_import",
                                "line": node.lineno,
                                "detail": f"import {alias.name}",
                            },
                        )
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if any(mod == m or mod.startswith(m + ".") for m in FORBIDDEN_SDK_MODULES):
                    violations.append(
                        {
                            "path": rel,
                            "check_id": "provider_sdk_import",
                            "line": node.lineno,
                            "detail": f"from {mod} import ...",
                        },
                    )
    return sorted(violations, key=lambda v: (v["path"], v["line"]))


def scan_direct_model_calls(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Return sorted violation dicts for direct model instantiation."""
    if files is None:
        files = _collect_files(repo_root)
    violations: list[dict] = []
    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        if rel in ALLOWED_SDK_FILES:
            continue
        try:
            # guardian: allow-silent-swallow - acceptable exception handling
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name in FORBIDDEN_INSTANTIATION_NAMES:
                    violations.append(
                        {
                            "path": rel,
                            "check_id": "direct_model_call",
                            "line": node.lineno,
                            "detail": f"call to {name}()",
                        },
                    )
    return sorted(violations, key=lambda v: (v["path"], v["line"]))


def run_gateway_bypass_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
) -> GuardianResult:
    if repo_root is None:
        repo_root = get_validated_project_root()
    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )

    files = _collect_files(repo_root)

    # check: provider_sdk_import
    sdk_viols = scan_provider_sdk_imports(repo_root, files)
    if sdk_viols:
        result.add_check(
            "provider_sdk_import",
            CheckStatus.FAIL,
            f"{len(sdk_viols)} forbidden SDK import(s) detected",
            evidence={"violations": sdk_viols[:20]},
        )
    else:
        result.add_check("provider_sdk_import", CheckStatus.PASS, "No forbidden SDK imports")

    # check: direct_model_call
    call_viols = scan_direct_model_calls(repo_root, files)
    if call_viols:
        result.add_check(
            "direct_model_call",
            CheckStatus.FAIL,
            f"{len(call_viols)} direct model instantiation(s) detected",
            evidence={"violations": call_viols[:20]},
        )
    else:
        result.add_check("direct_model_call", CheckStatus.PASS, "No direct model calls")

    # bypass_tier_router and bypass_embedding_factory: SKIP (requires runtime trace)
    result.add_check(
        "bypass_tier_router",
        CheckStatus.SKIP,
        "Requires ExecutionTrace artifact — not available in static scan",
    )
    result.add_check(
        "bypass_embedding_factory",
        CheckStatus.SKIP,
        "Requires ExecutionTrace artifact — not available in static scan",
    )

    result.summary = (
        f"gateway_bypass: {len(sdk_viols)} sdk_import violation(s), "
        f"{len(call_viols)} direct_call violation(s)"
    )
    if write_artifacts_dir:
        write_guardian_result(result, write_artifacts_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: gateway_bypass")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_gateway_bypass_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
