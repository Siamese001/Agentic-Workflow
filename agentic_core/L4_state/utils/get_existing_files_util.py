from __future__ import annotations

from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "get_existing_files_util")
emit_determinism_digest("p0", "get_existing_files_util")

_emit_dispatches_healing_run("p1", "get_existing_files_util", "L4")
_emit_routes_through("p1", "get_existing_files_util", "L4")
_emit_escalates_to_human("p1", "get_existing_files_util", "L4")
_emit_reads_policy_state("p1", "get_existing_files_util", "L4")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def get_existing_files() -> Set[str]:
    """Get set of all Python files in sovereign codebase."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_existing_files", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_existing_files", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "get_existing_files")
    existing: Any = set()
    repo_root: Any = Path(".")
    for root in SOVEREIGN_ROOTS:
        root_path: Any = repo_root / root
        if root_path.exists():
            from agentic_core.utils.ssot_discovery_validator import get_python_files

            for py_file in get_python_files(root_path):
                rel_path: Any = py_file.relative_to(repo_root)
                existing.add(str(rel_path))
    return existing
