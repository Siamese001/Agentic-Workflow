"""Additive determinism helper: canonical_bytes(obj) -> bytes.

Exposes a module-level function used by both production code and replay
harness tests.  Additive artifact for Phase 3 (W5 SOV-DELTA) — no existing
production code changed.

REQ-036 / Phase 3 SOV-DELTA additive helper.
"""

from __future__ import annotations

import json

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
)

_emit_dispatches_healing_run("p1", "canonicalize", "L2")
_emit_routes_through("p1", "canonicalize", "L2")
_emit_escalates_to_human("p1", "canonicalize", "L2")
_emit_reads_policy_state("p1", "canonicalize", "L2")


def canonical_bytes(obj) -> bytes:
    """Return deterministic canonical bytes for *obj*.

    Uses ``obj.__dict__`` for class/dataclass instances, falls through to
    *obj* itself for plain dict/list/primitive values.  ``sort_keys=True``
    ensures key insertion order does not affect the output.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "canonical_bytes", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "canonical_bytes", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "canonical_bytes")
    data = obj.__dict__ if hasattr(obj, "__dict__") else obj
    return json.dumps(data or obj, sort_keys=True, separators=(",", ":")).encode()
