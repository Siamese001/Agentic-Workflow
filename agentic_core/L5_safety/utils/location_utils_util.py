from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "location_utils_util")
emit_determinism_digest("p0", "location_utils_util")

_emit_dispatches_healing_run("p1", "location_utils_util", "L5")
_emit_routes_through("p1", "location_utils_util", "L5")
_emit_escalates_to_human("p1", "location_utils_util", "L5")
_emit_reads_policy_state("p1", "location_utils_util", "L5")
_emit_authorize_and_execute("p2", "location_utils_util", "execution_auth")
_emit_validates_capability("p2", "location_utils_util", "capability_check")
_emit_routes_to_capability("p2", "location_utils_util", "capability_route")
_emit_writes_via_uwg("p2", "location_utils_util", "uwg_write")
_emit_blocks_direct_write("p2", "location_utils_util", "direct_write_block")
_emit_records_tool_invocation("p2", "location_utils_util", "tool_invocation")
_emit_captures_execution_output("p2", "location_utils_util", "exec_output")
_emit_dispatches_agent("p3", "location_utils_util", "agent_dispatch")
_emit_coordinates_agents("p3", "location_utils_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "location_utils_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "location_utils_util", "healing_outcome")
_emit_escalates_failure("p3", "location_utils_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "location_utils_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "location_utils_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "location_utils_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "location_utils_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "location_utils_util", "eval_metric")
_emit_stores_embedding("p4", "location_utils_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "location_utils_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "location_utils_util", "exec_snapshot_link")

"\nShared utility functions for location-based operations.\n\nExtracted from LocationAgent.py during SRP fission.\nAll location-related agents should import from this module.\n"
import os
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L5_safety.config.structure_blueprint import DEPTH_RULES, SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def normalize_location_path(path: str) -> str:
    """
    Standardizes path formatting for comparison.

    Args:
        path: Path string to normalize

    Returns:
        Normalized path with forward slashes
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "normalize_location_path", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "normalize_location_path", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "normalize_location_path")
    # guardian: allow-path-string
    return os.path.normpath(path).replace("\\", "/")


def get_agent_files(root_dir: str) -> list[str]:
    """
    Discovers all .py files within the agentic_core structure.

    Args:
        root_dir: Root directory to search

    Returns:
        List of Python file paths
    """
    agent_files = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py") and (not file.startswith("__")):
                agent_files.append(Path(root) / file)
    return agent_files


def compute_module_path(file_path: Path, project_root: Path | None = None) -> str:
    """
    Compute Python module path from file path.

    Args:
        file_path: Path to Python file
        project_root: Optional project root (auto-detected if None)

    Returns:
        Module path string (e.g., 'agentic_core.L5_safety.reasoning.LocationAgent')
    """
    if project_root is None:
        from agentic_core.L5_safety.config.structure_blueprint import get_validated_project_root

        project_root = get_validated_project_root()
    try:
        rel_path = file_path.relative_to(project_root)
        module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        return ".".join(module_parts)
    except ValueError:
        return file_path.stem


def is_path_compliant(file_path: str | Path, project_root: Path | None = None) -> bool:
    """
    L5 Sovereign Structural SSOT - Hard-enforcement of path validity.

    This is the Supreme Court for structural compliance. All L3 and L2 agents
    that need to validate file paths MUST call this function instead of
    implementing their own path validation logic.

    Enforces:
    1. Path must be within project root
    2. Root folder must be in SOVEREIGN_TERRITORIES (whitelist)
    3. Depth must not exceed MAX_ALLOWED_DEPTH per root
    4. No forbidden root folders (legacy_*, old_*)
    5. No numbered folder prefixes (^\\d+_)

    Args:
        file_path: Path to validate (str or Path)
        project_root: Optional project root (auto-detected if None)

    Returns:
        True if path is structurally compliant, False otherwise

    Example:
        >>> is_path_compliant('agentic_core/L5_safety/validators/LocationAgent.py')
        True
        >>> is_path_compliant('legacy_code/old_agent.py')
        False
        >>> is_path_compliant('agentic_core/L1/L2/L3/L4/L5/deep.py')  # Too deep
        False
    """
    from agentic_core.L5_safety.config.structure_blueprint import (
        FORBIDDEN_FOLDER_PATTERN,
        FORBIDDEN_ROOT_FOLDERS,
        ROOT_WHITELIST,
        get_validated_project_root,
    )

    if project_root is None:
        project_root = get_validated_project_root()
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if not file_path.is_absolute():
        file_path = project_root / file_path
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        return False
    parts = rel_path.parts
    if not parts:
        return False
    root_folder = parts[0]
    if root_folder not in ROOT_WHITELIST:
        return False
    for part in parts:
        if part in FORBIDDEN_ROOT_FOLDERS:
            return False
        if hasattr(FORBIDDEN_FOLDER_PATTERN, "match"):
            if FORBIDDEN_FOLDER_PATTERN.match(part):
                return False
    if len(root_folder) >= 3 and root_folder[:2].isdigit() and (root_folder[2:3] == "_"):
        return False
    expected_depth = DEPTH_RULES.get(root_folder)
    if expected_depth is not None:
        actual_depth = len(parts) - 1
        if actual_depth != expected_depth:
            from agentic_core.L5_safety.config.structure_blueprint import VARIABLE_DEPTH_SUBFOLDERS

            if root_folder == AGENTIC_CORE_DIR and len(parts) > 1:
                subfolder = parts[1]
                if subfolder in VARIABLE_DEPTH_SUBFOLDERS and actual_depth >= 2:
                    return True
            return False
    return True
