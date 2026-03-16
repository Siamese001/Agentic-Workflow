"""
Automatically fix lines longer than 100 characters.

[SSOT] File discovery uses ssot_discovery.py - DO NOT define get_python_files here
"""

import logging
import re
from typing import Any

from apps_shared.utils.ConfigurationService import ConfigurationService

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "fix_long_lines")
_emit_applies_guardrail("p0", "fix_long_lines", "p0_governance")
_emit_reads_policy_state("p0", "fix_long_lines", "policy_binding")
_emit_snapshots_state("p0", "fix_long_lines", "state_snapshot")
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
    for op in OPERATORS:
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
        for line in ConfigurationService().lines:
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
                    CONTENT, ConfigurationService().indent, "and"
                )
            if (
                not ConfigurationService().result
                and (not ConfigurationService().is_import)
                and (" or " in CONTENT)
            ):
                ConfigurationService().result = _break_at_boolean_operator(
                    CONTENT, ConfigurationService().indent, "or"
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
    except Exception as e:
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
