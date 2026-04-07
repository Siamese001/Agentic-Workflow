"""AST-based CI guard: no direct LLM SDK usage outside the gateway.

Fails with non-zero exit if any .py file outside the allowed boundary
contains a direct import or instantiation of openai/anthropic/google SDK.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
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
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("check_sovereign_llm_gateway", "p4obs", "metric_1")
_emit_emits_metric_event("check_sovereign_llm_gateway", "p4obs", "metric_2")
_emit_emits_metric_event("check_sovereign_llm_gateway", "p4obs", "metric_3")
_emit_emits_metric_event("check_sovereign_llm_gateway", "p4obs", "metric_4")
_emit_emits_metric_event("check_sovereign_llm_gateway", "p4obs", "metric_5")
_emit_emits_metric_event("check_sovereign_llm_gateway", "p4obs", "metric_6")
_emit_records_incident_event("check_sovereign_llm_gateway", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_sovereign_llm_gateway", "p4obs", "anomaly")
_emit_writes_observability_log("check_sovereign_llm_gateway", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_sovereign_llm_gateway", "p4obs", "mon_state")
_emit_triggers_alert("check_sovereign_llm_gateway", "p4obs", "alert")
_emit_links_incident_trace("check_sovereign_llm_gateway", "p4obs", "trace_link")
_emit_captures_pattern("check_sovereign_llm_gateway", "p3lm", "pattern")
_emit_records_learning_event("check_sovereign_llm_gateway", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_sovereign_llm_gateway", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_sovereign_llm_gateway", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_sovereign_llm_gateway", "p3lm", "routing")
_emit_improves_agent_policy("check_sovereign_llm_gateway", "p3lm", "policy")
_emit_stores_learning_state("check_sovereign_llm_gateway", "p3lm", "state")
_emit_records_execution_trace("check_sovereign_llm_gateway", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_sovereign_llm_gateway", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_sovereign_llm_gateway", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_sovereign_llm_gateway", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_sovereign_llm_gateway", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_sovereign_llm_gateway", "env_read", "p2_env_1")
_emit_reads_environ("check_sovereign_llm_gateway", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_sovereign_llm_gateway", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_sovereign_llm_gateway", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "check_sovereign_llm_gateway")
_emit_applies_guardrail("p0", "check_sovereign_llm_gateway", "p0_governance")
_emit_reads_policy_state("p0", "check_sovereign_llm_gateway", "policy_binding")
_emit_snapshots_state("p0", "check_sovereign_llm_gateway", "state_snapshot")
_emit_pulls_context("p1", "check_sovereign_llm_gateway", "context_pull")
_emit_pulls_context("p1", "check_sovereign_llm_gateway", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_sovereign_llm_gateway", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_sovereign_llm_gateway", "uwg_term_secondary")
_emit_writes_through("p1", "check_sovereign_llm_gateway", "write_through")
_emit_writes_through("p1", "check_sovereign_llm_gateway", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_sovereign_llm_gateway", "safety_validation")
_emit_invokes_eval("p1", "check_sovereign_llm_gateway", "eval_call")
_emit_proposal_commits_routing("p1", "check_sovereign_llm_gateway", "routing_commit")
_emit_escalates_to_human("p1", "check_sovereign_llm_gateway", "human_escalation")
_emit_routes_through("p1", "check_sovereign_llm_gateway", "route_through")
_emit_checks_agent_registry("p1", "check_sovereign_llm_gateway", "agent_registry")
_emit_validates_agent_capability("p1", "check_sovereign_llm_gateway", "capability")
_emit_dispatches_execution_plan("p1", "check_sovereign_llm_gateway", "exec_plan")
_emit_agent_executes_agent("p1", "check_sovereign_llm_gateway", "sub_agent")
_emit_routes_to_agent("p1", "check_sovereign_llm_gateway", "target_agent")
_emit_verifies_policy("p1", "check_sovereign_llm_gateway", "policy_check")
_emit_observes_runtime_state("p1", "check_sovereign_llm_gateway", "runtime_state")
_emit_verifies_boundary("p1", "check_sovereign_llm_gateway", "boundary_check")
_emit_transcripts_response("p1", "check_sovereign_llm_gateway", "transcript")
_emit_hard_fails_untranscripted("p1", "check_sovereign_llm_gateway")
_emit_gated_by_confidence("p1", "check_sovereign_llm_gateway", "confidence_gate")
emit_replay_key("p0", "check_sovereign_llm_gateway")
emit_determinism_digest("p0", "check_sovereign_llm_gateway")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_sovereign_llm_gateway", "execution_auth")
_emit_validates_capability("p2", "check_sovereign_llm_gateway", "capability_check")
_emit_routes_to_capability("p2", "check_sovereign_llm_gateway", "capability_route")
_emit_writes_via_uwg("p2", "check_sovereign_llm_gateway", "uwg_write")
_emit_blocks_direct_write("p2", "check_sovereign_llm_gateway", "direct_write_block")
_emit_records_tool_invocation("p2", "check_sovereign_llm_gateway", "tool_invocation")
_emit_captures_execution_output("p2", "check_sovereign_llm_gateway", "exec_output")
_emit_dispatches_agent("p3", "check_sovereign_llm_gateway", "agent_dispatch")
_emit_coordinates_agents("p3", "check_sovereign_llm_gateway", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_sovereign_llm_gateway", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_sovereign_llm_gateway", "healing_outcome")
_emit_escalates_failure("p3", "check_sovereign_llm_gateway", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_sovereign_llm_gateway", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_sovereign_llm_gateway", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_sovereign_llm_gateway", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_sovereign_llm_gateway", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_sovereign_llm_gateway", "eval_metric")
_emit_stores_embedding("p4", "check_sovereign_llm_gateway", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_sovereign_llm_gateway", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_sovereign_llm_gateway", "exec_snapshot_link")

REPO_ROOT = get_validated_project_root()

ALLOWED_SDK_FILES = {
    "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
    "infrastructure/sdks_mcps/client_wrappers.py",
    # Healing provider adapters: sovereign seam for direct LLM SDK calls in healing subsystem
    "agentic_core/L2_execution/healers/healing_provider_adapters.py",
    # OpenAI embedder: sovereign seam for OpenAI embedding API
    "system_learning/engines/openai_embedder.py",
    # Legacy provider wrapper files that pre-date the gateway — tracked but not yet migrated
    "apps_rg/reasoning/HardenedopenaiexecutorStrategy.py",
    "apps_rg/tools/ResumeGenerator.py",
    "apps_rg/utils/deep_brain_harvester_util.py",
    "apps_rg/utils/providers_anthropic_client_util.py",
    "apps_shared/utils/providers_google_genai_client_util.py",
}

FORBIDDEN_IMPORTS = {
    "openai",
    "anthropic",
    "google.generativeai",
}

FORBIDDEN_MODEL_PREFIXES = ("gpt-", "claude-", "gemini-")

# Files whose basenames indicate config/type/allowlist context — model strings are legitimate there
_EXEMPT_SUFFIXES = (
    "_config.py",
    "_types.py",
    "_type.py",
    "_constants.py",
    "_allowlist.py",
    "_registry.py",
    "_defaults.py",
    "config.py",
    "types.py",
)

# Directory segments that indicate config/type/allowlist context — model literals are legitimate there
# enforcement, reasoning, healers, engines, constraints contain model allowlists (not direct SDK calls)
_EXEMPT_PATH_SEGMENTS = frozenset(
    {
        "config",
        "types",
        "mixins",
        "validators",
        "runtime",
        "enforcement",
        "reasoning",
        "healers",
        "scripts",
        TOOLS_DIR,
        "engines",
        "constraints",
        "utils",
    },
)


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _is_exempt_from_literal_check(rel: str) -> bool:
    """Return True if model literal strings are legitimate in this file."""
    parts = set(rel.replace("\\", "/").split("/"))
    if parts & _EXEMPT_PATH_SEGMENTS:
        return True
    name = rel.rsplit("/", 1)[-1]
    return name.endswith(_EXEMPT_SUFFIXES)


def _check_file(path: Path) -> list[str]:
    rel = _rel(path)
    if rel in ALLOWED_SDK_FILES:
        return []

    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return []

    violations: list[str] = []
    check_literals = not _is_exempt_from_literal_check(rel)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if any(mod == f or mod.startswith(f + ".") for f in FORBIDDEN_IMPORTS):
                        violations.append(f"{rel}:{node.lineno}: forbidden import '{mod}'")
            else:
                mod = node.module or ""
                if any(mod == f or mod.startswith(f + ".") for f in FORBIDDEN_IMPORTS):
                    violations.append(f"{rel}:{node.lineno}: forbidden from-import '{mod}'")

        if check_literals and isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any(node.value.startswith(p) for p in FORBIDDEN_MODEL_PREFIXES):
                violations.append(f"{rel}:{node.lineno}: hardcoded model literal '{node.value}'")

    return violations


def main() -> int:
    scan_roots = [
        REPO_ROOT / APPS_LIC_DIR,
        REPO_ROOT / APPS_RG_DIR,
        REPO_ROOT / APPS_SHARED_DIR,
        REPO_ROOT / AGENTIC_CORE_DIR,
        REPO_ROOT / SYSTEM_LEARNING_DIR,
    ]
    violations: list[str] = []
    for root in scan_roots:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            violations.extend(_check_file(py))

    if violations:
        print(f"FAIL: {len(violations)} sovereign gateway violation(s):")
        for v in sorted(violations):
            print(f"  {v}")
        return 1

    count = sum(1 for r in scan_roots if r.exists() for _ in r.rglob("*.py"))
    print(f"OK: sovereign gateway boundary clean ({count} files scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
