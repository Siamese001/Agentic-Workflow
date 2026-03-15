"""Structure drift manifest writer — stdlib only, no UWG dependency.

Write counterpart for structure_drift_validator.generate_structure_manifest().
Moved here from validators/ to preserve the pure read-only contract of that module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def save_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    """Save the structure manifest to a file.

    Args:
        manifest: The structure manifest to save
        output_path: Path where to save the manifest
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "save_manifest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "save_manifest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "save_manifest")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


__all__ = ["save_manifest"]
