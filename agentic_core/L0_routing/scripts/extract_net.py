from __future__ import annotations

import shutil
from pathlib import Path

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def extract_net_incremental() -> None:
    """Extract files that don't exist in sovereign codebase."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "extract_net_incremental", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "extract_net_incremental", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "extract_net_incremental")
    source_dir: Any = Path("archives/legacy_lic")
    staging_dir: Any = Path("archive_code")
    if staging_dir.exists():
        assert_no_persistent_write("L0", "shutil.mutate")
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    existing_files: Any = get_existing_files()
    extracted_files: Any = []
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(source_dir):
        FILENAME: Any = py_file.name
        name_exists: Any = any(FILENAME in existing for existing in existing_files)
        if not name_exists:
            dest_path: Any = staging_dir / FILENAME
            shutil.copy2(py_file, dest_path)
            extracted_files.append(FILENAME)
    return extracted_files
