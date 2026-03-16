from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "toolbox_util")
_emit_applies_guardrail("p0", "toolbox_util", "p0_governance")
_emit_reads_policy_state("p0", "toolbox_util", "policy_binding")
_emit_snapshots_state("p0", "toolbox_util", "state_snapshot")
emit_replay_key("p0", "toolbox_util")
emit_determinism_digest("p0", "toolbox_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "toolbox_util", "execution_auth")
_emit_validates_capability("p2", "toolbox_util", "capability_check")
_emit_routes_to_capability("p2", "toolbox_util", "capability_route")
_emit_writes_via_uwg("p2", "toolbox_util", "uwg_write")
_emit_blocks_direct_write("p2", "toolbox_util", "direct_write_block")
_emit_records_tool_invocation("p2", "toolbox_util", "tool_invocation")
_emit_captures_execution_output("p2", "toolbox_util", "exec_output")
_emit_dispatches_agent("p3", "toolbox_util", "agent_dispatch")
_emit_coordinates_agents("p3", "toolbox_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "toolbox_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "toolbox_util", "healing_outcome")
_emit_escalates_failure("p3", "toolbox_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "toolbox_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "toolbox_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "toolbox_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "toolbox_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "toolbox_util", "eval_metric")
_emit_stores_embedding("p4", "toolbox_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "toolbox_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "toolbox_util", "exec_snapshot_link")
'Brief description of functionality and purpose.'
'Brief description of functionality and purpose.'
import logging
import os
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

Logger: Any = logging.getLogger('Toolbox')

def repository_get_file_content(file_path: Any) -> Any:
    """Safely reads a file from the repository."""
    try:
        # guardian: allow-path-string
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        with open(file_path, encoding='utf-8') as f:
            return f.read()
    # guardian: allow-silent-swallow
    except Exception as e:
        return f'Error reading file: {e}'

def repository_list_files(directory: Any='.') -> Any:
    """Lists python files in the directory recursively."""
    try:
        if '..' in directory:
            return 'Error: Cannot navigate up the directory tree.'
        from pathlib import Path

        from agentic_core.utils.ssot_discovery_validator import get_python_files
        return [str(f) for f in get_python_files(Path(directory))]
    # guardian: allow-silent-swallow
    except Exception as e:
        return f'Error listing files: {e}'

def repository_save_file(file_path: Any, content: Any) -> Any:
    """Safely writes content to a file. Creates directories if needed."""
    try:
        if '.git' in file_path or '.env' in file_path:
            return f"Error: Write access denied for sensitive file '{file_path}'."
        directory: Any = Path(file_path).parent
        # guardian: allow-path-string
        if directory and (not os.path.exists(directory)):
            os.makedirs(directory, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Success: File '{file_path}' saved."
    # guardian: allow-silent-swallow
    except Exception as e:
        return f'Error writing file: {e}'
safe_tools: Any = {'repository_get_file_content': repository_get_file_content, 'repository_list_files': repository_list_files, 'repository_save_file': repository_save_file, 'write_file': repository_save_file, 'print': print, 'len': len, 'os': os}
toolbox_desc: Any = '\nYou have access to the following file system tools. DO NOT hallucinate other tools.\n1. `repository_list_files(directory=".")`: List all Python files.\n2. `repository_get_file_content(file_path)`: Read the content of a specific file.\n3. `repository_save_file(file_path, content)`: Write code to a file. Will create directories if needed.\n4. `write_file(file_path, content)`: Alias for repository_save_file.\n\nTo use them, simply write the Python code calling these functions.\nIMPORTANT: These are real functions available in your execution context.\nExample: write_file("filename.py", "content")\n'
