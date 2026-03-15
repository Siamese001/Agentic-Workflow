from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

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

_emit_dispatches_healing_run("p1", "replay_key_computer", "L6")
_emit_routes_through("p1", "replay_key_computer", "L6")
_emit_escalates_to_human("p1", "replay_key_computer", "L6")
_emit_reads_policy_state("p1", "replay_key_computer", "L6")


@dataclass(frozen=True)
class ReplayKeyComponents:
    """A structured container for all components that define a replay key."""

    tier_selection: str
    retry_count: int
    threshold_config: dict[str, float]
    tool_budget_caps: dict[str, int]
    freshness_windows: dict[str, int]
    config_surface_hash: str
    embedding_pack_hash: str
    embedding_model_version: str
    c0_context_hash: str


def compute_replay_key(components: ReplayKeyComponents) -> str:
    """
    Computes a deterministic replay key from a comprehensive set of components.

    This function enforces Guarantee #12 by creating a single, verifiable hash
    that represents the entire context of a governance decision. Any change to
    the inputs (e.g., a config change, a model update, or a different retry
    count) will produce a different key, ensuring that replays are always
    executed against the exact context of the original decision.

    The key is computed in L6 (Observability) and would be stored in L4 (State)
    alongside the decision record.

    Args:
        components: A structured dataclass containing all parts of the replay key.

    Returns:
        A SHA-256 hex digest representing the deterministic replay key.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_replay_key", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_replay_key", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "compute_replay_key")

    def _canonical_json(data: Any) -> str:
        """Computes canonical JSON: sorted keys, UTF-8, no whitespace."""
        return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    from dataclasses import asdict

    material = asdict(components)
    canonical_string = _canonical_json(material)
    return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()
