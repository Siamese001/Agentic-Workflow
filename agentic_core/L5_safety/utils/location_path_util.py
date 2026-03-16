"""
location_path_util.py — Standalone path compliance utilities.

Salvaged from LocationAgent.py during LCD+ decommission (Phase 0.3).

Contains:
- is_path_compliant(): L5 Sovereign Structural SSOT — Supreme Court for path validity
- get_location_agent(): Redirect shim for backward compatibility (→ LocationHealerAgent)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "location_path_util")
emit_determinism_digest("p0", "location_path_util")

_emit_dispatches_healing_run("p1", "location_path_util", "L5")
_emit_routes_through("p1", "location_path_util", "L5")
_emit_escalates_to_human("p1", "location_path_util", "L5")
_emit_reads_policy_state("p1", "location_path_util", "L5")

if TYPE_CHECKING:
    from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent


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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_path_compliant", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_path_compliant", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "is_path_compliant")
    from agentic_core.L5_safety.config.structure_blueprint import (
        DEPTH_RULES,
        PROJECT_ROOT_WHITELIST,
        get_validated_project_root,
    )

    if project_root is None:
        project_root = get_validated_project_root()
    path = Path(file_path)
    try:
        if not path.is_absolute():
            path = project_root / path
        rel_path = path.relative_to(project_root)
    except (ValueError, RuntimeError):
        return False
    parts = rel_path.parts
    if not parts:
        return False
    root_folder = parts[0]
    if root_folder not in PROJECT_ROOT_WHITELIST:
        return False
    max_depth = DEPTH_RULES.get(root_folder, 3)
    if len(parts) > max_depth:
        return False
    if root_folder.startswith(("legacy_", "old_")):
        return False
    forbidden_pattern = re.compile("^\\d+_")
    for part in parts:
        if forbidden_pattern.match(part):
            return False
    return True


_healer_instance: LocationHealerAgent | None = None


def get_location_agent(project_root: Path) -> LocationHealerAgent:
    """Get or create LocationHealerAgent singleton.

    Backward-compatible redirect: callers that previously used
    ``get_location_agent()`` from LocationAgent.py now get a
    LocationHealerAgent instance instead.
    """
    global _healer_instance
    if _healer_instance is None:
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

        _healer_instance = LocationHealerAgent(project_root=project_root)
    return _healer_instance
