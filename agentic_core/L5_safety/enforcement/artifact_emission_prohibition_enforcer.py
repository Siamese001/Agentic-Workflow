"""G-2-6 — Artifact Emission Prohibition for L0/L5/L6.

L0, L5, and L6 MUST NOT emit RESULT or HEALING_PLAN artifacts.
This guard executes at construction-time (not send-time).

Violation raises PermissionError with deterministic message containing:
  - layer
  - artifact type
  - trace_id (if available)
"""

from __future__ import annotations

import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

logger = logging.getLogger(__name__)
FORBIDDEN_EMISSION_LAYERS: frozenset[str] = frozenset({"L0", "L5", "L6"})
FORBIDDEN_ARTIFACT_KINDS: frozenset[str] = frozenset({"RESULT", "HEALING_PLAN"})


def assert_layer_may_emit(artifact_kind: str, layer: str, trace_id: str | None = None) -> None:
    """Fail-closed guard: raises PermissionError if layer may not emit this artifact.

    Args:
        artifact_kind: The artifact type being constructed (e.g. "RESULT", "HEALING_PLAN").
        layer: The calling layer identifier (e.g. "L0", "L2", "L5", "L6").
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If layer is in FORBIDDEN_EMISSION_LAYERS and
            artifact_kind is in FORBIDDEN_ARTIFACT_KINDS.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_layer_may_emit", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_layer_may_emit", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "assert_layer_may_emit")
    if layer not in FORBIDDEN_EMISSION_LAYERS:
        return
    if artifact_kind not in FORBIDDEN_ARTIFACT_KINDS:
        return
    msg_parts = [f"ARTIFACT_EMISSION_PROHIBITED:layer={layer}", f"artifact_kind={artifact_kind}"]
    if trace_id is not None:
        msg_parts.append(f"trace_id={trace_id}")
    msg = "|".join(msg_parts)
    logger.error("ARTIFACT_EMISSION_PROHIBITION DENY: %s", msg)
    raise PermissionError(msg)


__all__ = ["FORBIDDEN_ARTIFACT_KINDS", "FORBIDDEN_EMISSION_LAYERS", "assert_layer_may_emit"]
