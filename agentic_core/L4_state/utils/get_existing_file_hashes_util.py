from __future__ import annotations

from pathlib import Path

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.utils.ssot_discovery_validator import get_data_files, get_python_files

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def get_existing_file_hashes() -> dict[str, str]:
    """Get dict of filename -> content hash for existing sovereign files."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_existing_file_hashes", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_existing_file_hashes", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "get_existing_file_hashes")
    existing: Any = {}
    repo_root: Any = Path(".")
    sovereign_roots: Any = {
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
        "schemas",
        "prompt_governance",
        "observability",
        "config",
        "data",
        ARCHIVES_DIR,
        "docs",
    }
    for root in sovereign_roots:
        root_path: Any = repo_root / root
        if root_path.exists():
            for file_path in get_python_files(root_path):
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in get_data_files(root_path, extensions=[".json"]):
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in get_data_files(root_path, extensions=[".md"]):
                existing[file_path.name] = get_file_hash(file_path)
    return existing
