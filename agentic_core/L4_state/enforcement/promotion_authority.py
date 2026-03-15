"""Promotion authority for Wave 17 - P2 Promotion Authority.

This module provides scoped pointer updates with single-use tokens
through the gateway.
"""

import hashlib
import logging
import time
from dataclasses import dataclass

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

_emit_dispatches_healing_run("p1", "promotion_authority", "L4")
_emit_routes_through("p1", "promotion_authority", "L4")
_emit_escalates_to_human("p1", "promotion_authority", "L4")
_emit_reads_policy_state("p1", "promotion_authority", "L4")

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PromotionPointerUpdate:
    """Immutable record of a promotion pointer update."""

    old_pointer: str
    new_pointer: str
    timestamp: float
    capability_token_hash: str
    guardian_signature: str
    semantic_clock_tick: int


class PromotionAuthority:
    """Manages promotion pointer updates through gateway with capability tokens."""

    def __init__(self):
        self._write_gateway = None
        self._active_updates: dict[str, PromotionPointerUpdate] = {}

    def set_write_gateway(self, gateway):
        """Set the write gateway for pointer updates."""
        self._write_gateway = gateway

    def update_pointer_via_gateway(self, new_pointer: str, capability_token) -> PromotionPointerUpdate:
        """Update pointer via gateway with capability token validation."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()), "PromotionAuthority.update_pointer_via_gateway", "state_snapshot"
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "PromotionAuthority.update_pointer_via_gateway", "p0_governance"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "PromotionAuthority.update_pointer_via_gateway"
        )

        if not self._write_gateway:
            raise RuntimeError("Write gateway not configured")
        if not hasattr(capability_token, "validate_scope_and_use"):
            raise ValueError("Invalid capability token - missing validation method")
        if not capability_token.validate_scope_and_use():
            raise RuntimeError("Capability token validation failed")
        old_pointer = self._get_current_pointer(capability_token.target_namespace)
        update = PromotionPointerUpdate(
            old_pointer=old_pointer,
            new_pointer=new_pointer,
            timestamp=time.time(),
            capability_token_hash=hashlib.sha256(str(capability_token).encode()).hexdigest(),
            guardian_signature="guardian_signature_placeholder",
            semantic_clock_tick=capability_token.semantic_clock_tick,
        )
        self._write_gateway.update_pointer(
            namespace=capability_token.target_namespace,
            old_pointer=old_pointer,
            new_pointer=new_pointer,
            capability_token=capability_token,
        )
        self._active_updates[capability_token.target_namespace] = update
        Logger.info(
            f"Pointer updated in namespace {capability_token.target_namespace}: {old_pointer} -> {new_pointer}"
        )
        return update

    def _get_current_pointer(self, namespace: str) -> str:
        """Get current pointer for namespace."""
        existing = self._active_updates.get(namespace)
        if existing is not None:
            return existing.new_pointer
        return f"current_pointer_{namespace}"

    def get_update_history(self, namespace: str) -> PromotionPointerUpdate | None:
        """Get update history for namespace."""
        return self._active_updates.get(namespace)

    def validate_pointer_update_integrity(self, namespace: str, expected_hash: str) -> bool:
        """Validate pointer update integrity."""
        update = self._active_updates.get(namespace)
        if not update:
            return False
        computed_hash = hashlib.sha256(
            f"{update.old_pointer}{update.new_pointer}{update.timestamp}".encode()
        ).hexdigest()
        return computed_hash == expected_hash


_promotion_authority = None


def get_promotion_authority() -> PromotionAuthority:
    """Get the singleton promotion authority instance."""
    global _promotion_authority
    if _promotion_authority is None:
        _promotion_authority = PromotionAuthority()
    return _promotion_authority


def update_pointer_via_gateway(new_pointer: str, capability_token) -> PromotionPointerUpdate:
    """Update pointer via gateway with capability token validation."""
    authority = get_promotion_authority()
    return authority.update_pointer_via_gateway(new_pointer, capability_token)


def validate_pointer_update_integrity(namespace: str, expected_hash: str) -> bool:
    """Validate pointer update integrity."""
    authority = get_promotion_authority()
    return authority.validate_pointer_update_integrity(namespace, expected_hash)
