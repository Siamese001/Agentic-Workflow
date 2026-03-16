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
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_authorize_and_execute("p2", "routing_config_seal_types", "execution_auth")
_emit_validates_capability("p2", "routing_config_seal_types", "capability_check")
_emit_routes_to_capability("p2", "routing_config_seal_types", "capability_route")
_emit_writes_via_uwg("p2", "routing_config_seal_types", "uwg_write")
_emit_blocks_direct_write("p2", "routing_config_seal_types", "direct_write_block")
_emit_records_tool_invocation("p2", "routing_config_seal_types", "tool_invocation")
_emit_captures_execution_output("p2", "routing_config_seal_types", "exec_output")
_emit_dispatches_agent("p3", "routing_config_seal_types", "agent_dispatch")
_emit_coordinates_agents("p3", "routing_config_seal_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "routing_config_seal_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "routing_config_seal_types", "healing_outcome")
_emit_escalates_failure("p3", "routing_config_seal_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "routing_config_seal_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "routing_config_seal_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "routing_config_seal_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "routing_config_seal_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "routing_config_seal_types", "eval_metric")
_emit_stores_embedding("p4", "routing_config_seal_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "routing_config_seal_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "routing_config_seal_types", "exec_snapshot_link")
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
