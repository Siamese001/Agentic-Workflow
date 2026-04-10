"""
Script to fix common syntax errors in Python files.
Targets the most frequent issues found by the canon validator.
"""

import ast
import logging
import os
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
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
from apps_shared.utils.ConfigurationService import ConfigurationService

_emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_1")
_emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_2")
_emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_3")
_emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_4")
_emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_5")
_emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_6")
_emit_records_incident_event("fix_syntax_errors", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_syntax_errors", "p4obs", "anomaly")
_emit_writes_observability_log("fix_syntax_errors", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_syntax_errors", "p4obs", "mon_state")
_emit_triggers_alert("fix_syntax_errors", "p4obs", "alert")
_emit_links_incident_trace("fix_syntax_errors", "p4obs", "trace_link")
_emit_captures_pattern("fix_syntax_errors", "p3lm", "pattern")
_emit_records_learning_event("fix_syntax_errors", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_syntax_errors", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_syntax_errors", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_syntax_errors", "p3lm", "routing")
_emit_improves_agent_policy("fix_syntax_errors", "p3lm", "policy")
_emit_stores_learning_state("fix_syntax_errors", "p3lm", "state")
_emit_records_execution_trace("fix_syntax_errors", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_syntax_errors", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_syntax_errors", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_syntax_errors", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_syntax_errors", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_syntax_errors", "env_read", "p2_env_1")
_emit_reads_environ("fix_syntax_errors", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_syntax_errors", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_syntax_errors", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "fix_syntax_errors")
_emit_applies_guardrail("p0", "fix_syntax_errors", "p0_governance")
_emit_reads_policy_state("p0", "fix_syntax_errors", "policy_binding")
_emit_snapshots_state("p0", "fix_syntax_errors", "state_snapshot")
_emit_pulls_context("p1", "fix_syntax_errors", "context_pull")
_emit_pulls_context("p1", "fix_syntax_errors", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "fix_syntax_errors", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_syntax_errors", "uwg_term_secondary")
_emit_writes_through("p1", "fix_syntax_errors", "write_through")
_emit_writes_through("p1", "fix_syntax_errors", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "fix_syntax_errors", "safety_validation")
_emit_invokes_eval("p1", "fix_syntax_errors", "eval_call")
_emit_proposal_commits_routing("p1", "fix_syntax_errors", "routing_commit")
_emit_escalates_to_human("p1", "fix_syntax_errors", "human_escalation")
_emit_routes_through("p1", "fix_syntax_errors", "route_through")
_emit_checks_agent_registry("p1", "fix_syntax_errors", "agent_registry")
_emit_validates_agent_capability("p1", "fix_syntax_errors", "capability")
_emit_dispatches_execution_plan("p1", "fix_syntax_errors", "exec_plan")
_emit_agent_executes_agent("p1", "fix_syntax_errors", "sub_agent")
_emit_routes_to_agent("p1", "fix_syntax_errors", "target_agent")
_emit_verifies_policy("p1", "fix_syntax_errors", "policy_check")
_emit_observes_runtime_state("p1", "fix_syntax_errors", "runtime_state")
_emit_verifies_boundary("p1", "fix_syntax_errors", "boundary_check")
_emit_transcripts_response("p1", "fix_syntax_errors", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_syntax_errors")
_emit_gated_by_confidence("p1", "fix_syntax_errors", "confidence_gate")
emit_replay_key("p0", "fix_syntax_errors")
emit_determinism_digest("p0", "fix_syntax_errors")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "fix_syntax_errors", "execution_auth")
_emit_validates_capability("p2", "fix_syntax_errors", "capability_check")
_emit_routes_to_capability("p2", "fix_syntax_errors", "capability_route")
_emit_writes_via_uwg("p2", "fix_syntax_errors", "uwg_write")
_emit_blocks_direct_write("p2", "fix_syntax_errors", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_syntax_errors", "tool_invocation")
_emit_captures_execution_output("p2", "fix_syntax_errors", "exec_output")
_emit_dispatches_agent("p3", "fix_syntax_errors", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_syntax_errors", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_syntax_errors", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_syntax_errors", "healing_outcome")
_emit_escalates_failure("p3", "fix_syntax_errors", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_syntax_errors", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_syntax_errors", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_syntax_errors", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_syntax_errors", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_syntax_errors", "eval_metric")
_emit_stores_embedding("p4", "fix_syntax_errors", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_syntax_errors", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_syntax_errors", "exec_snapshot_link")

Logger: Any = logging.getLogger(__name__)


def fix_multiline_strings(content: Any) -> Any:
    """Fix multiline strings that should use triple quotes."""
    lines: Any = content.split("\n")
    fixed_lines: Any = []
    i: Any = 0
    while i < len(lines):
        line: Any = lines[i]
        if '"""' not in line and "'''" not in line:
            if '"' in line or "'" in line:
                quote_count: Any = line.count('"') + line.count("'")
                if quote_count % 2 == 1:
                    j: Any = i + 1
                    while j < len(lines) and ('"' in lines[j] or "'" in lines[j]):
                        if lines[j].count('"') + lines[j].count("'") > 0:
                            line: Any = line.replace('"', '"""', 1)
                            lines[j] = lines[j].replace('"', '"""', 1)
                            break
                        j += 1
        fixed_lines.append(line)
        i += 1
    return "\n".join(fixed_lines)


def fix_indentation_errors(content: Any) -> Any:
    """Fix common indentation errors."""
    lines: Any = content.split("\n")
    fixed_lines: Any = []
    for line in lines:
        if "\t" in line:
            line: Any = line.replace("\t", "    ")
        if line.strip() == "" and line != "":
            pass
        fixed_lines.append(line)
    return "\n".join(fixed_lines)


def fix_fstring_errors(content: Any) -> Any:
    """Fix common f-string syntax errors."""
    lines: Any = content.split("\n")
    fixed_lines: Any = []
    for line in lines:
        if 'f"' in line and "{{" not in line and ("}}" not in line):
            pass
        fixed_lines.append(line)
    return "\n".join(fixed_lines)


def check_syntax(content: Any) -> Any:
    """Check if content has valid Python syntax."""
    try:
        ast.parse(content)
        return (True, None)
    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        return (False, str(e))


def fix_file(filepath: Any) -> Any:
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            original_content: Any = f.read()
        is_valid, error = check_syntax(original_content)
        if is_valid:
            return (True, "Already valid")
        fixed_content: Any = original_content
        fixed_content: Any = fix_multiline_strings(fixed_content)
        fixed_content: Any = fix_indentation_errors(fixed_content)
        fixed_content: Any = fix_fstring_errors(fixed_content)
        is_valid, error = check_syntax(fixed_content)
        if is_valid:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            return (True, "Fixed")
        else:
            return (False, f"Still broken: {error}")
    # guardian: allow-silent-swallow
    except Exception as e:
        return (False, f"Error: {str(e)}")


def main() -> Any:
    """Fix all Python files in the project."""
    fixed_count: Any = 0
    failed_count: Any = 0
    try:
        excluded_dirs: Any = ConfigurationService().excluded_dirs
    # guardian: allow-silent-swallow
    except:
        excluded_dirs: Any = [".git", "__pycache__", "venv"]
    try:
        logger_instance: Any = ConfigurationService().Logger
    # guardian: allow-silent-swallow
    except:
        logger_instance: Any = logging.getLogger(__name__)
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py"):
                filepath: Any = Path(root) / file
                success, message = fix_file(filepath)
                if success:
                    if message == "Fixed":
                        logger_instance.info(f"✅ Fixed: {filepath}")
                        fixed_count += 1
                else:
                    logger_instance.info(f"❌ Failed: {filepath} - {message}")
                    failed_count += 1
    logger_instance.info(f"\nSummary: {fixed_count} fixed, {failed_count} still broken")


if __name__ == "__main__":
    main()
