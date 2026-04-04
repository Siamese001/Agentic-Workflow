"""
L2 Deterministic Providers — Replay Mode Enforcement.

Provides structural overrides for nondeterministic modules (time, random, uuid)
during replay mode execution. All providers derive deterministic state from a
trace_id, ensuring byte-identical replay across runs.

Layer: L2 Execution
Authority: May only be activated by ReplayGuardMixin during replay mode.
Invariant: One trace_id per process. Re-patching with a different trace_id is
           a hard error to prevent cross-trace contamination.
"""

from __future__ import annotations

import hashlib
import random as _random_module
import time as _time_module
import uuid as _uuid_module
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_ACTIVE_TRACE_ID: str | None = None
_PATCHED: bool = False
_ORIGINAL_TIME: float = _time_module.time
_ORIGINAL_SLEEP = _time_module.sleep
_ORIGINAL_RANDOM = _random_module.random
_ORIGINAL_RANDINT = _random_module.randint
_ORIGINAL_CHOICE = _random_module.choice
_ORIGINAL_UUID4 = _uuid_module.uuid4


class DeterministicPatchError(Exception):
    """Raised when attempting to re-patch with a different trace_id."""


class FixedTimeProvider:
    """Deterministic time provider for replay mode.

    Derives a stable base timestamp from trace_id via SHA-256.
    Advances monotonically via sleep() and advance() calls.
    """

    def __init__(self, trace_id: str) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "FixedTimeProvider.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "FixedTimeProvider.__init__", "p0_governance")
        seed_bytes = hashlib.sha256(trace_id.encode("utf-8")).digest()
        self._base_time: float = float(int.from_bytes(seed_bytes[:8], byteorder="big") % 1000000000)
        self._offset: float = 0.0

    def time(self) -> float:
        """Return deterministic timestamp."""
        return self._base_time + self._offset

    def sleep(self, seconds: float) -> None:
        """Advance virtual clock instead of blocking."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "FixedTimeProvider.sleep")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:FixedTimeProvider.sleep".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if seconds < 0:
            raise ValueError("sleep duration must be non-negative")
        self._offset += seconds

    def advance(self, seconds: float) -> None:
        """Manually advance virtual clock."""
        if seconds < 0:
            raise ValueError("advance duration must be non-negative")
        self._offset += seconds

    @property
    def current_offset(self) -> float:
        """Return accumulated offset for inspection."""
        return self._offset


class DeterministicRandomSource:
    """Deterministic random source for replay mode.

    Derives seed from trace_id via SHA-256, producing identical sequences
    for identical trace_ids across runs.
    """

    def __init__(self, trace_id: str) -> None:
        seed_bytes = hashlib.sha256(trace_id.encode("utf-8")).digest()
        seed_int = int.from_bytes(seed_bytes[:8], byteorder="big")
        self._rng = _random_module.Random(seed_int)

    def random(self) -> float:
        """Return deterministic float in [0.0, 1.0)."""
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        """Return deterministic integer in [a, b]."""
        return self._rng.randint(a, b)

    def choice(self, seq: Any) -> Any:
        """Return deterministic choice from sequence."""
        return self._rng.choice(seq)

    def shuffle(self, seq: list) -> list:
        """Shuffle sequence deterministically in-place and return it."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "DeterministicRandomSource.shuffle"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DeterministicRandomSource.shuffle".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._rng.shuffle(seq)
        return seq


class DeterministicUUIDProvider:
    """Deterministic UUID4 provider for replay mode.

    Produces a monotonically incrementing sequence of UUIDs derived from
    trace_id, ensuring identical UUID sequences across replays.
    """

    def __init__(self, trace_id: str) -> None:
        seed_bytes = hashlib.sha256(f"{trace_id}-uuid".encode()).digest()
        self._base_int = int.from_bytes(seed_bytes[:16], byteorder="big")
        self._counter = 0

    def uuid4(self) -> _uuid_module.UUID:
        """Return deterministic UUID."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "DeterministicUUIDProvider.uuid4")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DeterministicUUIDProvider.uuid4".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        raw = self._base_int + self._counter & (1 << 128) - 1
        self._counter += 1
        raw = raw & ~(15 << 76) | 4 << 76
        raw = raw & ~(3 << 62) | 2 << 62
        return _uuid_module.UUID(int=raw)


def patch_deterministic(trace_id: str) -> dict[str, Any]:
    """Install deterministic providers for the given trace_id.

    Returns a dict of provider instances for direct use.

    Raises DeterministicPatchError if already patched with a different trace_id.
    """
    global _ACTIVE_TRACE_ID, _PATCHED
    if _PATCHED:
        if _ACTIVE_TRACE_ID != trace_id:
            raise DeterministicPatchError(
                f"Already patched with trace_id={_ACTIVE_TRACE_ID!r}, cannot re-patch with trace_id={trace_id!r}. One trace per process."
            )
        return _get_active_providers()
    time_provider = FixedTimeProvider(trace_id)
    random_source = DeterministicRandomSource(trace_id)
    uuid_provider = DeterministicUUIDProvider(trace_id)
    _time_module.time = time_provider.time
    _time_module.sleep = time_provider.sleep
    _random_module.random = random_source.random
    _random_module.randint = random_source.randint
    _random_module.choice = random_source.choice
    _uuid_module.uuid4 = uuid_provider.uuid4
    _ACTIVE_TRACE_ID = trace_id
    _PATCHED = True
    return {"time_provider": time_provider, "random_source": random_source, "uuid_provider": uuid_provider}


def unpatch_deterministic() -> None:
    """Restore original nondeterministic modules.

    Safe to call even if not patched (no-op).
    Primarily used in tests.
    """
    global _ACTIVE_TRACE_ID, _PATCHED
    _time_module.time = _ORIGINAL_TIME
    _time_module.sleep = _ORIGINAL_SLEEP
    _random_module.random = _ORIGINAL_RANDOM
    _random_module.randint = _ORIGINAL_RANDINT
    _random_module.choice = _ORIGINAL_CHOICE
    _uuid_module.uuid4 = _ORIGINAL_UUID4
    _ACTIVE_TRACE_ID = None
    _PATCHED = False


def is_patched() -> bool:
    """Return True if deterministic providers are currently active."""
    return _PATCHED


def get_active_trace_id() -> str | None:
    """Return the trace_id of the active patch, or None."""
    return _ACTIVE_TRACE_ID


def _get_active_providers() -> dict[str, Any]:
    """Return dict of current provider instances (internal helper)."""
    return {
        "time_provider": _time_module.time,
        "random_source": _random_module.random,
        "uuid_provider": _uuid_module.uuid4,
    }
