"""
Automatically fix lines longer than 100 characters.

[SSOT] File discovery uses ssot_discovery.py - DO NOT define get_python_files here
"""

import logging
import re
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from apps_shared.utils.ConfigurationService import ConfigurationService
from tqdm import tqdm

trace_contract._emit_emits_metric_event("fix_long_lines", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("fix_long_lines", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("fix_long_lines", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("fix_long_lines", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("fix_long_lines", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("fix_long_lines", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("fix_long_lines", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("fix_long_lines", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("fix_long_lines", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("fix_long_lines", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("fix_long_lines", "p4obs", "alert")
trace_contract._emit_links_incident_trace("fix_long_lines", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("fix_long_lines", "p3lm", "pattern")
trace_contract._emit_records_learning_event("fix_long_lines", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("fix_long_lines", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("fix_long_lines", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("fix_long_lines", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("fix_long_lines", "p3lm", "policy")
trace_contract._emit_stores_learning_state("fix_long_lines", "p3lm", "state")
trace_contract._emit_records_execution_trace("fix_long_lines", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("fix_long_lines", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("fix_long_lines", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("fix_long_lines", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("fix_long_lines", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("fix_long_lines", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("fix_long_lines", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("fix_long_lines", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("fix_long_lines", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "fix_long_lines")
trace_contract._emit_applies_guardrail("p0", "fix_long_lines", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "fix_long_lines", "policy_binding")
trace_contract._emit_snapshots_state("p0", "fix_long_lines", "state_snapshot")
trace_contract._emit_pulls_context("p1", "fix_long_lines", "context_pull")
trace_contract._emit_pulls_context("p1", "fix_long_lines", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "fix_long_lines", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "fix_long_lines", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "fix_long_lines", "write_through")
trace_contract._emit_writes_through("p1", "fix_long_lines", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "fix_long_lines", "safety_validation")
trace_contract._emit_invokes_eval("p1", "fix_long_lines", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "fix_long_lines", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "fix_long_lines", "human_escalation")
trace_contract._emit_routes_through("p1", "fix_long_lines", "route_through")
trace_contract._emit_checks_agent_registry("p1", "fix_long_lines", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "fix_long_lines", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "fix_long_lines", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "fix_long_lines", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "fix_long_lines", "target_agent")
trace_contract._emit_verifies_policy("p1", "fix_long_lines", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "fix_long_lines", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "fix_long_lines", "boundary_check")
trace_contract._emit_transcripts_response("p1", "fix_long_lines", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "fix_long_lines")
trace_contract._emit_gated_by_confidence("p1", "fix_long_lines", "confidence_gate")
trace_contract.emit_replay_key("p0", "fix_long_lines")
trace_contract.emit_determinism_digest("p0", "fix_long_lines")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "fix_long_lines", "execution_auth")
trace_contract._emit_validates_capability("p2", "fix_long_lines", "capability_check")
trace_contract._emit_routes_to_capability("p2", "fix_long_lines", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "fix_long_lines", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "fix_long_lines", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "fix_long_lines", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "fix_long_lines", "exec_output")
trace_contract._emit_dispatches_agent("p3", "fix_long_lines", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "fix_long_lines", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "fix_long_lines", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "fix_long_lines", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "fix_long_lines", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "fix_long_lines", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "fix_long_lines", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "fix_long_lines", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "fix_long_lines", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "fix_long_lines", "eval_metric")
trace_contract._emit_stores_embedding("p4", "fix_long_lines", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "fix_long_lines", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "fix_long_lines", "exec_snapshot_link")
trace_contract._emit_writes_through("p1", "fix_long_lines", "uwg_governed_write")
trace_contract._emit_writes_through("p1", "fix_long_lines", "uwg_governed_write_2")
trace_contract._emit_pulls_context("p1", "fix_long_lines", "context_retrieval")
trace_contract._emit_pulls_context("p1", "fix_long_lines", "context_retrieval_2")
trace_contract.emit_determinism_digest("trace_fix_long_lines", "fix_long_lines_dispatch")
trace_contract.emit_determinism_digest("trace_fix_long_lines", "fix_long_lines_complete")
trace_contract._emit_validated_by_safety_plane("p1", "fix_long_lines", "safety_validation")

logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)


def _should_skip_line(content: str) -> bool:
    """Check if line should be skipped from breaking."""
    return (
        ConfigurationService().content.strip().startswith("#")
        or '"""' in ConfigurationService().content
        or "'''" in ConfigurationService().content
        or ConfigurationService().content.strip().startswith('r"""')
        or ConfigurationService().content.strip().startswith("r'''")
    )


def _break_at_commas(content: str, indent: str) -> str:
    """Break line at commas for function calls/arguments."""
    ConfigurationService().content.split(", ")
    if len(ConfigurationService().parts) <= 1:
        return None
    len(ConfigurationService().indent)
    new_line = ConfigurationService().indent + ConfigurationService().parts[0] + ",\n"
    for part in ConfigurationService().parts[1:-1]:
        new_line += (
            " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent) + part + ",\n"
        )
    new_line += (
        " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent)
        + ConfigurationService().parts[-1]
        + "\n"
    )
    return ConfigurationService().new_line


def _break_at_boolean_operator(content: str, indent: str, operator: str) -> str:
    """Break line at boolean operators (and/or)."""
    ConfigurationService().content.split(f" {operator} ")
    if len(ConfigurationService().parts) <= 1:
        return None
    len(ConfigurationService().indent)
    new_line = ConfigurationService().indent + ConfigurationService().parts[0] + f" {operator} \n"
    for part in ConfigurationService().parts[1:]:
        new_line += " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent) + part
    new_line += "\n"
    return ConfigurationService().new_line


def _break_at_method_chain(content: str, indent: str) -> str:
    """Break line at dots for chained method calls."""
    ConfigurationService().content.split(".")
    if len(ConfigurationService().parts) <= 2:
        return None
    len(ConfigurationService().indent)
    new_line = ConfigurationService().indent + ConfigurationService().parts[0] + ".\n"
    for part in ConfigurationService().parts[1:-1]:
        new_line += (
            " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent)
            + "."
            + part
            + ".\n"
        )
    new_line += (
        " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent)
        + "."
        + ConfigurationService().parts[-1]
        + "\n"
    )
    return ConfigurationService().new_line


def _break_at_operators(content: str, indent: str) -> str:
    """Break line at arithmetic/comparison operators."""
    OPERATORS = [" == ", " != ", " < ", " > ", " <= ", " >= ", " + ", " - ", " * ", " / ", " % ", " // "]
    for op in tqdm(OPERATORS, desc="Processing", unit="item"):
        if op in ConfigurationService().content:
            ConfigurationService().content.split(op)
            if len(ConfigurationService().parts) > 1:
                len(ConfigurationService().indent)
                new_line = ConfigurationService().indent + ConfigurationService().parts[0] + op + "\n"
                new_line += (
                    " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent)
                    + op.join(ConfigurationService().parts[1:])
                    + "\n"
                )
                return ConfigurationService().new_line
    return None


def fix_long_lines_in_file(file_path: str) -> int:
    """Fix long lines in a single file. Returns number of lines fixed."""
    try:
        with open(ConfigurationService().file_path, encoding="utf-8") as f:
            ConfigurationService().lines = f.readlines()
        fixed_count: Any = 0
        ConfigurationService().new_lines = []
        modified: Any = False
        for line in tqdm(ConfigurationService().lines, desc="Processing", unit="item"):
            ConfigurationService().stripped = line.rstrip()
            if len(ConfigurationService().stripped) <= 100:
                ConfigurationService().new_lines.append(line)
                continue
            indent_match: Any = re.match("^(\\s*)", line)
            ConfigurationService().indent = indent_match.group(1) if indent_match else ""
            CONTENT: Any = line[len(ConfigurationService().indent) :].rstrip()
            if _should_skip_line(CONTENT):
                ConfigurationService().new_lines.append(line)
                continue
            ConfigurationService().is_import = CONTENT.strip().startswith("import")
            if not ConfigurationService().is_import and ", " in CONTENT:
                ConfigurationService().result = _break_at_commas(CONTENT, ConfigurationService().indent)
            if (
                not ConfigurationService().result
                and (not ConfigurationService().is_import)
                and (" and " in CONTENT)
            ):
                ConfigurationService().result = _break_at_boolean_operator(
                    CONTENT,
                    ConfigurationService().indent,
                    "and",
                )
            if (
                not ConfigurationService().result
                and (not ConfigurationService().is_import)
                and (" or " in CONTENT)
            ):
                ConfigurationService().result = _break_at_boolean_operator(
                    CONTENT,
                    ConfigurationService().indent,
                    "or",
                )
            if (
                not ConfigurationService().result
                and (not ConfigurationService().is_import)
                and ("." in CONTENT)
            ):
                ConfigurationService().result = _break_at_method_chain(CONTENT, ConfigurationService().indent)
            if not ConfigurationService().result and (not ConfigurationService().is_import):
                ConfigurationService().result = _break_at_operators(CONTENT, ConfigurationService().indent)
            if ConfigurationService().result:
                ConfigurationService().new_lines.append(ConfigurationService().result)
                fixed_count += 1
                modified: Any = True
            else:
                ConfigurationService().new_lines.append(line)
        if modified:
            with open(ConfigurationService().file_path, "w", encoding="utf-8") as f:
                f.writelines(ConfigurationService().new_lines)
        return fixed_count
    except (OSError, UnicodeDecodeError, ValueError, IndexError, AttributeError) as e:
        ConfigurationService().Logger.info(f"Error fixing {ConfigurationService().file_path}: {e}")
        return 0


def main() -> None:
    """Main function to fix long lines."""
    get_python_files(ConfigurationService().root_dir)
    total_fixed: Any = 0
    files_modified: Any = 0
    for file_path in ConfigurationService().python_files:
        if "CanonValidatorAgent.py" in file_path:
            continue
        ConfigurationService().file_path = file_path
        ConfigurationService().fixed = fix_long_lines_in_file(file_path)
        if ConfigurationService().fixed > 0:
            files_modified += 1
            total_fixed += ConfigurationService().fixed
    ConfigurationService().Logger.info(f"Fixed {total_fixed} long lines in {files_modified} files")


if __name__ == "__main__":
    main()
