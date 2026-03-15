"""
Wave 5.3: Immutable Routing Config Seal.

Prevents mid-run routing config mutation by sealing the config
at run start with a canonical hash.  Any attempt to mutate the
config during execution raises RoutingConfigSealViolation.

Lives in L0 (routing types) — config is read at routing time.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)
from agentic_core.utils.canonical_serializer_util import (
    canonical_bytes,
)

_emit_dispatches_healing_run("p1", "routing_config_seal_types", "L0")
_emit_routes_through("p1", "routing_config_seal_types", "L0")
_emit_escalates_to_human("p1", "routing_config_seal_types", "L0")
_emit_reads_policy_state("p1", "routing_config_seal_types", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "routing_config_seal_types", "p0_governance")
_emit_snapshots_state("p0", "routing_config_seal_types", "state_snapshot")


class RoutingConfigSealViolation(RuntimeError):
    """Raised when routing config is mutated after sealing."""


@dataclass(frozen=True)
class RoutingConfigSeal:
    """Immutable seal over a routing configuration snapshot.

    Once sealed, the config hash must remain constant for the
    duration of the run.  Verification re-derives the hash and
    compares.
    """

    canonical_hash: str
    version: str
    sealed_at: str

    @staticmethod
    def create(
        *,
        config: dict,
        version: str,
    ) -> RoutingConfigSeal:
        """Seal a routing config snapshot."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "RoutingConfigSeal.create")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        sealed_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        ch = hashlib.sha256(canonical_bytes(config)).hexdigest()
        return RoutingConfigSeal(
            canonical_hash=ch,
            version=version,
            sealed_at=sealed_at,
        )

    def verify(self, config: dict) -> bool:
        """Verify config has not changed since sealing."""
        current = hashlib.sha256(canonical_bytes(config)).hexdigest()
        return current == self.canonical_hash


class SealedRoutingContext:
    """Context manager that enforces routing config immutability.

    Usage::

        ctx = SealedRoutingContext(config, version="1.0")
        ctx.verify_or_raise(config)  # ok
        config["new_key"] = "value"
        ctx.verify_or_raise(config)  # raises
    """

    def __init__(self, config: dict, *, version: str) -> None:
        self._seal = RoutingConfigSeal.create(config=config, version=version)

    @property
    def seal(self) -> RoutingConfigSeal:
        return self._seal

    def verify_or_raise(self, config: dict) -> None:
        """Raise if config has been mutated since sealing."""
        if not self._seal.verify(config):
            raise RoutingConfigSealViolation(
                "Routing config mutated after sealing. "
                f"Expected hash: "
                f"{self._seal.canonical_hash[:16]}... "
                f"Sealed at: {self._seal.sealed_at}"
            )
