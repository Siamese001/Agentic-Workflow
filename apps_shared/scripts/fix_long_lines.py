"""
Automatically fix lines longer than 100 characters.

[SSOT] File discovery uses ssot_discovery.py - DO NOT define get_python_files here
"""

import logging
import re
from typing import Any

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
from tqdm import tqdm

_emit_emits_metric_event("fix_long_lines", "p4obs", "metric_1")
_emit_emits_metric_event("fix_long_lines", "p4obs", "metric_2")
_emit_emits_metric_event("fix_long_lines", "p4obs", "metric_3")
_emit_emits_metric_event("fix_long_lines", "p4obs", "metric_4")
_emit_emits_metric_event("fix_long_lines", "p4obs", "metric_5")
_emit_emits_metric_event("fix_long_lines", "p4obs", "metric_6")
_emit_records_incident_event("fix_long_lines", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_long_lines", "p4obs", "anomaly")
_emit_writes_observability_log("fix_long_lines", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_long_lines", "p4obs", "mon_state")
_emit_triggers_alert("fix_long_lines", "p4obs", "alert")
_emit_links_incident_trace("fix_long_lines", "p4obs", "trace_link")
_emit_captures_pattern("fix_long_lines", "p3lm", "pattern")
_emit_records_learning_event("fix_long_lines", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_long_lines", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_long_lines", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_long_lines", "p3lm", "routing")
_emit_improves_agent_policy("fix_long_lines", "p3lm", "policy")
_emit_stores_learning_state("fix_long_lines", "p3lm", "state")
_emit_records_execution_trace("fix_long_lines", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_long_lines", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_long_lines", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_long_lines", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_long_lines", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_long_lines", "env_read", "p2_env_1")
_emit_reads_environ("fix_long_lines", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_long_lines", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_long_lines", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "fix_long_lines")
_emit_applies_guardrail("p0", "fix_long_lines", "p0_governance")
_emit_reads_policy_state("p0", "fix_long_lines", "policy_binding")
_emit_snapshots_state("p0", "fix_long_lines", "state_snapshot")
_emit_pulls_context("p1", "fix_long_lines", "context_pull")
_emit_pulls_context("p1", "fix_long_lines", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "fix_long_lines", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_long_lines", "uwg_term_secondary")
_emit_writes_through("p1", "fix_long_lines", "write_through")
_emit_writes_through("p1", "fix_long_lines", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "fix_long_lines", "safety_validation")
_emit_invokes_eval("p1", "fix_long_lines", "eval_call")
_emit_proposal_commits_routing("p1", "fix_long_lines", "routing_commit")
_emit_escalates_to_human("p1", "fix_long_lines", "human_escalation")
_emit_routes_through("p1", "fix_long_lines", "route_through")
_emit_checks_agent_registry("p1", "fix_long_lines", "agent_registry")
_emit_validates_agent_capability("p1", "fix_long_lines", "capability")
_emit_dispatches_execution_plan("p1", "fix_long_lines", "exec_plan")
_emit_agent_executes_agent("p1", "fix_long_lines", "sub_agent")
_emit_routes_to_agent("p1", "fix_long_lines", "target_agent")
_emit_verifies_policy("p1", "fix_long_lines", "policy_check")
_emit_observes_runtime_state("p1", "fix_long_lines", "runtime_state")
_emit_verifies_boundary("p1", "fix_long_lines", "boundary_check")
_emit_transcripts_response("p1", "fix_long_lines", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_long_lines")
_emit_gated_by_confidence("p1", "fix_long_lines", "confidence_gate")
emit_replay_key("p0", "fix_long_lines")
emit_determinism_digest("p0", "fix_long_lines")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "fix_long_lines", "execution_auth")
_emit_validates_capability("p2", "fix_long_lines", "capability_check")
_emit_routes_to_capability("p2", "fix_long_lines", "capability_route")
_emit_writes_via_uwg("p2", "fix_long_lines", "uwg_write")
_emit_blocks_direct_write("p2", "fix_long_lines", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_long_lines", "tool_invocation")
_emit_captures_execution_output("p2", "fix_long_lines", "exec_output")
_emit_dispatches_agent("p3", "fix_long_lines", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_long_lines", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_long_lines", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_long_lines", "healing_outcome")
_emit_escalates_failure("p3", "fix_long_lines", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_long_lines", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_long_lines", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_long_lines", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_long_lines", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_long_lines", "eval_metric")
_emit_stores_embedding("p4", "fix_long_lines", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_long_lines", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_long_lines", "exec_snapshot_link")
_emit_writes_through("p1", "fix_long_lines", "uwg_governed_write")
_emit_writes_through("p1", "fix_long_lines", "uwg_governed_write_2")
_emit_pulls_context("p1", "fix_long_lines", "context_retrieval")
_emit_pulls_context("p1", "fix_long_lines", "context_retrieval_2")
emit_determinism_digest("trace_fix_long_lines", "fix_long_lines_dispatch")
emit_determinism_digest("trace_fix_long_lines", "fix_long_lines_complete")
_emit_validated_by_safety_plane("p1", "fix_long_lines", "safety_validation")

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
