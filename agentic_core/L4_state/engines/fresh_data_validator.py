from __future__ import annotations

import datetime
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "fresh_data_validator")
emit_determinism_digest("p0", "fresh_data_validator")

_emit_dispatches_healing_run("p1", "fresh_data_validator", "L4")
_emit_routes_through("p1", "fresh_data_validator", "L4")
_emit_escalates_to_human("p1", "fresh_data_validator", "L4")
_emit_reads_policy_state("p1", "fresh_data_validator", "L4")


class StaleDataViolation(Exception):
    """Raised when data is served that is older than the freshness policy allows."""

    def __init__(self, data_timestamp: datetime.datetime, policy_max_age: int):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "StaleDataViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "StaleDataViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "StaleDataViolation.__init__")
        self.data_timestamp = data_timestamp
        self.policy_max_age = policy_max_age
        super().__init__(
            f"Data with timestamp {data_timestamp} is stale. Policy requires data to be no older than {policy_max_age} seconds."
        )


@dataclass(frozen=True)
class FreshnessPolicy:
    """Defines the freshness window for a piece of data."""

    max_age_seconds: int


@dataclass(frozen=True)
class VersionedData:
    """Represents a piece of data with a timestamp for freshness validation."""

    content: Any
    timestamp: datetime.datetime


def validate_freshness(data: VersionedData, policy: FreshnessPolicy) -> None:
    """
    Validates that a piece of versioned data is not stale.

    This function enforces Guarantee #11 (Fresh data only at runtime) by comparing
    the data's timestamp against a configurable freshness window. It is a critical
    sovereign gate in L4 to prevent the use of outdated context or knowledge.

    Args:
        data: The versioned data to validate.
        policy: The freshness policy to apply.

    Raises:
        StaleDataViolation: If the data's timestamp is older than the allowed max age.
    """
    now = datetime.datetime.utcnow()
    allowed_age = datetime.timedelta(seconds=policy.max_age_seconds)
    if now - data.timestamp > allowed_age:
        raise StaleDataViolation(data_timestamp=data.timestamp, policy_max_age=policy.max_age_seconds)
