"""
agentic_core/L6_observability/utils/evaluation/governed_handoff.py

Governed handoff — routes sealed PromotionPackets to the real UWG / BUS T
rollout publication path in future-run-only mode.

Real seams used
---------------
UWG seam:
    PromotionTokenIssuer.issue_promotion_token()    [L2]
    PromotionAuthority.update_pointer_via_gateway() [L4]
    Sources:
        agentic_core.L2_execution.types.promotion_token
        agentic_core.L4_state.enforcement.promotion_authority

BUS U / rollout publication seam:
    TelemetryBus.publish(BusType.TELEMETRY, signal_type="PROMOTION_ROLLOUT", ...)
    Source: agentic_core.L2_execution.audit.telemetry_bus
    NOTE: No separate BUS U bus type exists in the runtime.  BUS T (BusType.TELEMETRY)
    with signal_type="PROMOTION_ROLLOUT" is the governed rollout publication channel.

Default mode dry_run=True:
    - Issues a scoped PromotionToken (single-use nonce).
    - Validates token scope and expiry (does NOT consume nonce).
    - Publishes to BUS T as signal_type="PROMOTION_ROLLOUT".
    - Returns HandoffRecord with committed=False.
    - Completed run is NOT mutated.

dry_run=False (future real mode):
    - Same plus calls PromotionAuthority.update_pointer_via_gateway(), which
      validates and consumes the token nonce.
    - If the gateway is not configured, commit is skipped gracefully.

Future-run only.  No direct L6 write.  No live-run mutation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from agentic_core.L2_execution.audit.telemetry_bus import BusType, get_telemetry_bus
from agentic_core.L2_execution.types.promotion_token import issue_promotion_token
from agentic_core.L2_execution.utils.providers import get_clock

if TYPE_CHECKING:
    from agentic_core.L6_observability.utils.evaluation.promotion_packet import PromotionPacket

# Signal type used on BUS T for promotion rollout publication (the "BUS U" seam)
BUS_ROLLOUT_SIGNAL = "PROMOTION_ROLLOUT"

# Semantic clock tick used for dry-run token issuance (wide window)
_DRY_RUN_CLOCK_TICK = 0
_DRY_RUN_WINDOW_SIZE = 9999


@dataclass(frozen=True)
class HandoffRecord:
    """Sealed record of a governed handoff attempt.

    Fields
    ------
    record_id:           Unique identifier for this handoff record.
    packet_id:           PromotionPacket.packet_id handed off.
    token_id:            PromotionToken.token_id issued for this handoff.
    token_valid:         Whether the token passed scope+expiry check.
    bus_published:       Whether the packet was published to BUS T as PROMOTION_ROLLOUT.
    committed:           True only if update_pointer_via_gateway() succeeded.
                         Always False in dry_run=True mode.
    dry_run:             Whether this was a dry-run handoff.
    destination_namespace: PromotionToken target_namespace (= packet destination class).
    handoff_at:          Monotonic epoch tick at handoff time.
    error:               "" if successful; error message if any step failed.
    """

    record_id: str
    packet_id: str
    token_id: str
    token_valid: bool
    bus_published: bool
    committed: bool
    dry_run: bool
    destination_namespace: str
    handoff_at: float
    error: str


class GovernedHandoffAgent:
    """Route a sealed PromotionPacket to the UWG / BUS T rollout path.

    Default mode is dry_run=True — safe for proofs and CI.
    No live-run mutation in any mode.
    """

    def handoff(
        self,
        packet: "PromotionPacket",
        dry_run: bool = True,
    ) -> HandoffRecord:
        """Route packet to governed UWG / BUS T path.

        Steps
        -----
        1. Issue a scoped, single-use PromotionToken bound to the packet's
           replay_digest and destination namespace.
        2. Validate token scope and expiry (nonce NOT consumed in dry-run mode).
        3. Publish to BUS T with signal_type="PROMOTION_ROLLOUT".
        4. In non-dry-run mode only: call PromotionAuthority.update_pointer_via_gateway()
           (which validates + consumes the nonce).

        Args:
            packet:   Sealed PromotionPacket from PromotionPacketizer.
            dry_run:  If True (default), publish to BUS T but skip UWG commit.

        Returns:
            HandoffRecord — sealed outcome record.
        """
        namespace = packet.target_destination_class
        token_id = "UNISSUED"
        token_valid = False
        bus_published = False
        committed = False
        error = ""

        try:
            # Step 1: Issue scoped PromotionToken
            token = issue_promotion_token(
                target_namespace=namespace,
                semantic_clock_tick=_DRY_RUN_CLOCK_TICK,
                window_size=_DRY_RUN_WINDOW_SIZE,
                replay_digest=packet.replay_digest,
                guardian_signature=f"governed_handoff:{packet.packet_id}",
            )
            token_id = token.token_id

            # Step 2: Validate scope + expiry (non-consuming check)
            token_valid = token.is_valid_for_namespace(namespace) and not token.is_expired(
                _DRY_RUN_CLOCK_TICK
            )

            # Step 3: Publish to BUS T as PROMOTION_ROLLOUT
            bus = get_telemetry_bus()
            bus_published = bus.publish(
                bus_type=BusType.TELEMETRY,
                signal_type=BUS_ROLLOUT_SIGNAL,
                payload=_packet_to_bus_payload(packet, token_id, dry_run),
                trace_id=packet.packet_id,
                priority=1,
            )

            # Step 4: UWG commit — only in non-dry-run mode
            if not dry_run and token_valid:
                from agentic_core.L4_state.enforcement.promotion_authority import (  # noqa: PLC0415
                    get_promotion_authority,
                )

                authority = get_promotion_authority()
                try:
                    authority.update_pointer_via_gateway(
                        new_pointer=packet.packet_id,
                        capability_token=token,
                    )
                    committed = True
                except RuntimeError:
                    # Write gateway not configured in future-run mode — expected.
                    pass

        except (RuntimeError, ValueError, OSError) as exc:
            error = str(exc)

        return HandoffRecord(
            record_id=f"hr-{uuid.uuid4().hex[:12]}",
            packet_id=packet.packet_id,
            token_id=token_id,
            token_valid=token_valid,
            bus_published=bus_published,
            committed=committed,
            dry_run=dry_run,
            destination_namespace=namespace,
            handoff_at=get_clock().now_epoch(),
            error=error,
        )


def _packet_to_bus_payload(
    packet: "PromotionPacket",
    token_id: str,
    dry_run: bool,
) -> dict:
    """Convert a PromotionPacket to a BUS T payload dict."""
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
        "signal_type": BUS_ROLLOUT_SIGNAL,
    }


__all__ = ["BUS_ROLLOUT_SIGNAL", "GovernedHandoffAgent", "HandoffRecord"]
