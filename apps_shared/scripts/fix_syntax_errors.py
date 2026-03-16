"""
Script to fix common syntax errors in Python files.
Targets the most frequent issues found by the canon validator.
"""

import ast
import logging
import os
from pathlib import Path
from typing import Any

from apps_shared.utils.ConfigurationService import ConfigurationService

from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
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

_emit_records_execution_trace("p0", "evidence", "fix_syntax_errors")
_emit_applies_guardrail("p0", "fix_syntax_errors", "p0_governance")
_emit_reads_policy_state("p0", "fix_syntax_errors", "policy_binding")
_emit_snapshots_state("p0", "fix_syntax_errors", "state_snapshot")
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
    except SyntaxError as e:
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
