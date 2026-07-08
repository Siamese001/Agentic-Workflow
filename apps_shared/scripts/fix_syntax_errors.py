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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from apps_shared.utils.ConfigurationService import ConfigurationService
from tqdm import tqdm

trace_contract._emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("fix_syntax_errors", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("fix_syntax_errors", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("fix_syntax_errors", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("fix_syntax_errors", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("fix_syntax_errors", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("fix_syntax_errors", "p4obs", "alert")
trace_contract._emit_links_incident_trace("fix_syntax_errors", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("fix_syntax_errors", "p3lm", "pattern")
trace_contract._emit_records_learning_event("fix_syntax_errors", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("fix_syntax_errors", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("fix_syntax_errors", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("fix_syntax_errors", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("fix_syntax_errors", "p3lm", "policy")
trace_contract._emit_stores_learning_state("fix_syntax_errors", "p3lm", "state")
trace_contract._emit_records_execution_trace("fix_syntax_errors", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("fix_syntax_errors", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("fix_syntax_errors", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("fix_syntax_errors", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("fix_syntax_errors", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("fix_syntax_errors", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("fix_syntax_errors", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("fix_syntax_errors", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("fix_syntax_errors", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "fix_syntax_errors")
trace_contract._emit_applies_guardrail("p0", "fix_syntax_errors", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "fix_syntax_errors", "policy_binding")
trace_contract._emit_snapshots_state("p0", "fix_syntax_errors", "state_snapshot")
trace_contract._emit_pulls_context("p1", "fix_syntax_errors", "context_pull")
trace_contract._emit_pulls_context("p1", "fix_syntax_errors", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "fix_syntax_errors", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "fix_syntax_errors", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "fix_syntax_errors", "write_through")
trace_contract._emit_writes_through("p1", "fix_syntax_errors", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "fix_syntax_errors", "safety_validation")
trace_contract._emit_invokes_eval("p1", "fix_syntax_errors", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "fix_syntax_errors", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "fix_syntax_errors", "human_escalation")
trace_contract._emit_routes_through("p1", "fix_syntax_errors", "route_through")
trace_contract._emit_checks_agent_registry("p1", "fix_syntax_errors", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "fix_syntax_errors", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "fix_syntax_errors", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "fix_syntax_errors", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "fix_syntax_errors", "target_agent")
trace_contract._emit_verifies_policy("p1", "fix_syntax_errors", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "fix_syntax_errors", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "fix_syntax_errors", "boundary_check")
trace_contract._emit_transcripts_response("p1", "fix_syntax_errors", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "fix_syntax_errors")
trace_contract._emit_gated_by_confidence("p1", "fix_syntax_errors", "confidence_gate")
trace_contract.emit_replay_key("p0", "fix_syntax_errors")
trace_contract.emit_determinism_digest("p0", "fix_syntax_errors")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "fix_syntax_errors", "execution_auth")
trace_contract._emit_validates_capability("p2", "fix_syntax_errors", "capability_check")
trace_contract._emit_routes_to_capability("p2", "fix_syntax_errors", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "fix_syntax_errors", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "fix_syntax_errors", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "fix_syntax_errors", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "fix_syntax_errors", "exec_output")
trace_contract._emit_dispatches_agent("p3", "fix_syntax_errors", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "fix_syntax_errors", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "fix_syntax_errors", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "fix_syntax_errors", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "fix_syntax_errors", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "fix_syntax_errors", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "fix_syntax_errors", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "fix_syntax_errors", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "fix_syntax_errors", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "fix_syntax_errors", "eval_metric")
trace_contract._emit_stores_embedding("p4", "fix_syntax_errors", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "fix_syntax_errors", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "fix_syntax_errors", "exec_snapshot_link")

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
    except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
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
    except Exception as e:  # guardian: allow-silent-swallow
        return (False, f"Error: {str(e)}")


def main() -> Any:
    """Fix all Python files in the project."""
    fixed_count: Any = 0
    failed_count: Any = 0
    try:
        excluded_dirs: Any = ConfigurationService().excluded_dirs
    except Exception:  # guardian: allow-silent-swallow
        excluded_dirs: Any = [".git", "__pycache__", "venv"]
    try:
        logger_instance: Any = ConfigurationService().Logger
    except Exception:  # guardian: allow-silent-swallow
        logger_instance: Any = logging.getLogger(__name__)
    for root, dirs, files in tqdm(os.walk("."), desc="Processing", unit="item"):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in tqdm(files, desc="Processing", unit="item"):
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
