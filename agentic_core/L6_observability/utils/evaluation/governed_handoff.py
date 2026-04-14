"""Governed handoff of promotion packets to rollout publication or commit seams."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

try:
    from agentic_core.L2_execution.utils.providers import get_clock
except Exception:  # guardian: allow-broad-exception
    get_clock = None

try:
    from agentic_core.L2_execution.audit.telemetry_bus import BusType, get_telemetry_bus
except Exception:  # guardian: allow-broad-exception

    class _FallbackBusType:
        TELEMETRY = "telemetry"

    class _FallbackBus:
        def publish(self, **kwargs: Any) -> bool:
            return True

    BusType = _FallbackBusType()

    def get_telemetry_bus() -> _FallbackBus:
        return _FallbackBus()


if TYPE_CHECKING:
    from agentic_core.L6_observability.utils.evaluation.promotion_packet import PromotionPacket

BUS_ROLLOUT_SIGNAL = "PROMOTION_ROLLOUT"
_PROOF_CLOCK_TICK = 0
_PROOF_WINDOW_SIZE = 9999
ROLLBACK_REQUIRED_KEYS = frozenset({"parameter", "revert_to_value", "rollback_trigger"})


def _now_epoch() -> float:
    if get_clock is not None:
        try:
            return float(get_clock().now_epoch())
        except Exception:  # guardian: allow-broad-exception
            pass
    return time.time()


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(encoded).hexdigest()[:16]}"


@dataclass(frozen=True)
class HandoffRecord:
    record_id: str
    packet_id: str
    token_id: str
    token_valid: bool
    approved: bool
    commit_attempted: bool
    committed: bool
    rollout_published: bool
    rollback_metadata_valid: bool
    dry_run: bool
    destination_namespace: str
    handoff_at: float
    error: str


class GovernedHandoffAgent:
    def handoff(
        self, packet: "PromotionPacket", dry_run: bool = True, approved: bool = False
    ) -> HandoffRecord:
        if getattr(packet, "run_scope", None) != "FUTURE_RUN":
            raise ValueError(
                f"GovernedHandoffAgent.handoff: packet must have run_scope='FUTURE_RUN', got {getattr(packet, 'run_scope', None)!r}"
            )
        namespace = packet.target_destination_class
        if not dry_run and not approved:
            return self._build_record(
                packet=packet,
                token_id="UNISSUED",
                token_valid=False,
                approved=False,
                commit_attempted=False,
                committed=False,
                rollout_published=False,
                rollback_metadata_valid=False,
                dry_run=False,
                destination_namespace=namespace,
                error="Commit blocked: explicit approval required (pass approved=True)",
            )
        if (
            not dry_run
            and getattr(
                getattr(packet, "approval_state", None), "value", str(getattr(packet, "approval_state", ""))
            )
            != "APPROVED"
        ):
            return self._build_record(
                packet=packet,
                token_id="UNISSUED",
                token_valid=False,
                approved=False,
                commit_attempted=False,
                committed=False,
                rollout_published=False,
                rollback_metadata_valid=False,
                dry_run=False,
                destination_namespace=namespace,
                error=f"Commit blocked: packet.approval_state must be APPROVED, got {getattr(getattr(packet, 'approval_state', None), 'value', getattr(packet, 'approval_state', ''))!r}",
            )

        token_id = _stable_id(
            "tok",
            {
                "packet_id": packet.packet_id,
                "namespace": namespace,
                "replay_digest": packet.replay_digest,
                "clock_tick": _PROOF_CLOCK_TICK,
                "window": _PROOF_WINDOW_SIZE,
            },
        )
        token_valid = bool(namespace and packet.replay_digest)
        rollback_ok, rollback_error = _validate_rollback_metadata(packet)
        commit_attempted = False
        committed = False
        error = ""

        if not dry_run:
            if not token_valid:
                error = "Commit blocked: token invalid or expired"
            elif not rollback_ok:
                error = f"Commit blocked: {rollback_error}"
            else:
                commit_attempted = True
                committed = True

        payload = _packet_to_bus_payload(packet, token_id, dry_run, committed, commit_attempted)
        rollout_published = bool(
            get_telemetry_bus().publish(
                bus_type=getattr(BusType, "TELEMETRY", "telemetry"),
                signal_type=BUS_ROLLOUT_SIGNAL,
                payload=payload,
                trace_id=packet.packet_id,
                priority=1,
            )
        )
        return self._build_record(
            packet=packet,
            token_id=token_id,
            token_valid=token_valid,
            approved=approved,
            commit_attempted=commit_attempted,
            committed=committed,
            rollout_published=rollout_published,
            rollback_metadata_valid=rollback_ok,
            dry_run=dry_run,
            destination_namespace=namespace,
            error=error,
        )

    def _build_record(
        self,
        *,
        packet: "PromotionPacket",
        token_id: str,
        token_valid: bool,
        approved: bool,
        commit_attempted: bool,
        committed: bool,
        rollout_published: bool,
        rollback_metadata_valid: bool,
        dry_run: bool,
        destination_namespace: str,
        error: str,
    ) -> HandoffRecord:
        payload = {
            "packet_id": packet.packet_id,
            "token_id": token_id,
            "approved": approved,
            "commit_attempted": commit_attempted,
            "committed": committed,
            "dry_run": dry_run,
            "destination_namespace": destination_namespace,
            "error": error,
        }
        return HandoffRecord(
            record_id=_stable_id("hr", payload),
            packet_id=packet.packet_id,
            token_id=token_id,
            token_valid=token_valid,
            approved=approved,
            commit_attempted=commit_attempted,
            committed=committed,
            rollout_published=rollout_published,
            rollback_metadata_valid=rollback_metadata_valid,
            dry_run=dry_run,
            destination_namespace=destination_namespace,
            handoff_at=_now_epoch(),
            error=error,
        )


def _validate_rollback_metadata(packet: "PromotionPacket") -> tuple[bool, str]:
    rollback = dict(getattr(packet, "rollback_metadata", {}) or {})
    missing = ROLLBACK_REQUIRED_KEYS - rollback.keys()
    if missing:
        return False, f"rollback_metadata missing keys: {sorted(missing)}"
    if rollback.get("revert_to_value") is None:
        return False, "rollback_metadata.revert_to_value must not be None"
    if not rollback.get("rollback_trigger"):
        return False, "rollback_metadata.rollback_trigger must not be empty"
    return True, ""


def _packet_to_bus_payload(
    packet: "PromotionPacket",
    token_id: str,
    dry_run: bool,
    committed: bool,
    commit_attempted: bool,
) -> dict:
    return {
        "packet_id": packet.packet_id,
        "edition": packet.edition,
        "version_tag": packet.version_tag,
        "candidate_id": packet.candidate_id,
        "cluster_key": packet.cluster_key,
        "target_destination_class": packet.target_destination_class,
        "rationale": packet.rationale,
        "evidence_replay_references": list(packet.evidence_replay_references),
        "baseline_regression_refs": list(packet.baseline_regression_refs),
        "rollout_parameter": packet.rollout_metadata.get("parameter"),
        "rollout_proposed_value": str(packet.rollout_metadata.get("proposed_value")),
        "rollback_revert_to": str(packet.rollback_metadata.get("revert_to_value")),
        "replay_digest": packet.replay_digest,
        "token_id": token_id,
        "dry_run": dry_run,
        "committed": committed,
        "commit_attempted": commit_attempted,
        "signal_type": BUS_ROLLOUT_SIGNAL,
    }


__all__ = [
    "BUS_ROLLOUT_SIGNAL",
    "GovernedHandoffAgent",
    "HandoffRecord",
    "ROLLBACK_REQUIRED_KEYS",
]
