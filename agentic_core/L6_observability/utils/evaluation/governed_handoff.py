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
    Rollout publication is COUPLED to the commit result — it is emitted AFTER the UWG
    commit attempt completes (with the commit result included in the payload).

Approval / commit model
-----------------------
dry_run=True (default — safe for proofs and CI):
    - Issues token, validates token+rollback metadata.
    - Skips UWG commit (commit_attempted=False, committed=False).
    - Publishes BUS T PROMOTION_ROLLOUT with committed=False label.
    - No live-run mutation.

dry_run=False, approved=False (BLOCKED):
    - Returns immediately with error="Commit blocked: explicit approval required".
    - No token issued, no commit, no BUS T publish.

dry_run=False, approved=True (REAL GOVERNED COMMIT):
    - Issues token, validates token scope+expiry.
    - Validates rollback metadata contract (parameter, revert_to_value, rollback_trigger).
    - If any pre-commit gate fails → commit_attempted=False, returns with error.
    - Calls PromotionAuthority.update_pointer_via_gateway() (validates+consumes nonce).
    - Publishes BUS T AFTER commit attempt (with committed status in payload).
    - committed=True only if update_pointer_via_gateway() succeeded.

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

# Signal type used on BUS T for rollout publication (the governed "BUS U" seam)
BUS_ROLLOUT_SIGNAL = "PROMOTION_ROLLOUT"

# Semantic clock tick used for all proof / CI handoffs (wide window, no expiry risk)
_PROOF_CLOCK_TICK = 0
_PROOF_WINDOW_SIZE = 9999

# Rollback metadata keys that MUST be present and non-empty for a non-dry-run commit
ROLLBACK_REQUIRED_KEYS = frozenset({"parameter", "revert_to_value", "rollback_trigger"})


@dataclass(frozen=True)
class HandoffRecord:
    """Sealed record of a governed handoff attempt.

    Fields
    ------
    record_id:              Unique identifier for this handoff record.
    packet_id:              PromotionPacket.packet_id handed off.
    token_id:               PromotionToken.token_id issued ("UNISSUED" if blocked pre-token).
    token_valid:            Whether the token passed scope+expiry check.
    approved:               Whether explicit approval was provided by the caller.
    commit_attempted:       True if the UWG commit path was entered (approved non-dry-run).
    committed:              True only if update_pointer_via_gateway() succeeded.
    rollout_published:      True if BUS T PROMOTION_ROLLOUT was published.
    rollback_metadata_valid: True if rollback contract keys are present and non-empty.
    dry_run:                Whether this was a dry-run handoff.
    destination_namespace:  PromotionToken target_namespace (= packet destination class).
    handoff_at:             Monotonic epoch tick at handoff time.
    error:                  "" if successful; block reason or runtime error otherwise.
    """

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
    """Route a sealed PromotionPacket to the UWG / BUS T rollout path.

    Default mode is dry_run=True — safe for proofs and CI.
    Non-dry-run commit requires explicit approved=True.
    No live-run mutation in any mode.
    """

    def handoff(
        self,
        packet: "PromotionPacket",
        dry_run: bool = True,
        approved: bool = False,
    ) -> HandoffRecord:
        """Route packet to governed UWG / BUS T path.

        Execution order
        ---------------
        Blocked path (dry_run=False, approved=False):
            → return immediately; no token, no commit, no BUS T publish.

        Dry-run path (dry_run=True):
            1. Issue PromotionToken (scoped, single-use nonce).
            2. Validate token scope + expiry (non-consuming check).
            3. Validate rollback metadata contract (informational only in dry-run).
            4. Skip commit (commit_attempted=False).
            5. Publish BUS T with committed=False label.

        Real commit path (dry_run=False, approved=True):
            1. Issue PromotionToken (scoped, single-use nonce).
            2. Validate token scope + expiry.
            3. Validate rollback metadata contract — block if invalid.
            4. Call PromotionAuthority.update_pointer_via_gateway() [nonce consumed].
            5. Publish BUS T AFTER commit with committed result in payload.

        Args:
            packet:   Sealed PromotionPacket from PromotionPacketizer.
            dry_run:  If True (default), skip UWG commit.
            approved: Must be True for non-dry-run commit.  Ignored in dry-run mode.

        Returns:
            HandoffRecord — sealed outcome record.
        """
        # Scope invariant: only future-run packets may be handed off.
        if getattr(packet, "run_scope", None) != "FUTURE_RUN":
            raise ValueError(
                f"GovernedHandoffAgent.handoff: packet must have run_scope='FUTURE_RUN', "
                f"got {getattr(packet, 'run_scope', None)!r}"
            )

        namespace = packet.target_destination_class

        # ── Gate: non-dry-run requires explicit approval ───────────────────────
        if not dry_run and not approved:
            return HandoffRecord(
                record_id=f"hr-{uuid.uuid4().hex[:12]}",
                packet_id=packet.packet_id,
                token_id="UNISSUED",
                token_valid=False,
                approved=False,
                commit_attempted=False,
                committed=False,
                rollout_published=False,
                rollback_metadata_valid=False,
                dry_run=False,
                destination_namespace=namespace,
                handoff_at=get_clock().now_epoch(),
                error="Commit blocked: explicit approval required (pass approved=True)",
            )

        # ── Gate: non-dry-run commit requires packet.approval_state = APPROVED ───
        if not dry_run and approved and hasattr(packet, "approval_state"):
            actual_state = getattr(packet.approval_state, "value", str(packet.approval_state))
            if actual_state != "APPROVED":
                return HandoffRecord(
                    record_id=f"hr-{uuid.uuid4().hex[:12]}",
                    packet_id=packet.packet_id,
                    token_id="UNISSUED",
                    token_valid=False,
                    approved=False,
                    commit_attempted=False,
                    committed=False,
                    rollout_published=False,
                    rollback_metadata_valid=False,
                    dry_run=False,
                    destination_namespace=namespace,
                    handoff_at=get_clock().now_epoch(),
                    error=f"Commit blocked: packet.approval_state must be APPROVED, got {actual_state!r}",
                )

        token_id = "UNISSUED"
        token_valid = False
        commit_attempted = False
        committed = False
        rollout_published = False
        rollback_ok, rollback_error = False, ""
        error = ""

        try:
            # Step 1: Issue scoped PromotionToken
            token = issue_promotion_token(
                target_namespace=namespace,
                semantic_clock_tick=_PROOF_CLOCK_TICK,
                window_size=_PROOF_WINDOW_SIZE,
                replay_digest=packet.replay_digest,
                guardian_signature=f"governed_handoff:{packet.packet_id}",
            )
            token_id = token.token_id

            # Step 2: Validate scope + expiry (non-consuming check)
            token_valid = token.is_valid_for_namespace(namespace) and not token.is_expired(_PROOF_CLOCK_TICK)

            # Step 3: Validate rollback metadata contract
            rollback_ok, rollback_error = _validate_rollback_metadata(packet)

            if not dry_run:
                # Real commit path — block if any pre-commit gate fails
                if not token_valid:
                    error = "Commit blocked: token invalid or expired"
                elif not rollback_ok:
                    error = f"Commit blocked: {rollback_error}"
                else:
                    # Step 4: UWG commit (nonce is consumed here)
                    commit_attempted = True
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
                    except RuntimeError as exc:
                        error = str(exc)

                # Step 5: Publish BUS T AFTER commit attempt (commit status in payload)
                rollout_published = get_telemetry_bus().publish(
                    bus_type=BusType.TELEMETRY,
                    signal_type=BUS_ROLLOUT_SIGNAL,
                    payload=_packet_to_bus_payload(packet, token_id, dry_run, committed, commit_attempted),
                    trace_id=packet.packet_id,
                    priority=1,
                )
            else:
                # Dry-run: publish informational rollout signal (no commit)
                rollout_published = get_telemetry_bus().publish(
                    bus_type=BusType.TELEMETRY,
                    signal_type=BUS_ROLLOUT_SIGNAL,
                    payload=_packet_to_bus_payload(packet, token_id, dry_run, committed, commit_attempted),
                    trace_id=packet.packet_id,
                    priority=1,
                )

        except (ValueError, OSError) as exc:
            error = str(exc)

        return HandoffRecord(
            record_id=f"hr-{uuid.uuid4().hex[:12]}",
            packet_id=packet.packet_id,
            token_id=token_id,
            token_valid=token_valid,
            approved=approved,
            commit_attempted=commit_attempted,
            committed=committed,
            rollout_published=rollout_published,
            rollback_metadata_valid=rollback_ok,
            dry_run=dry_run,
            destination_namespace=namespace,
            handoff_at=get_clock().now_epoch(),
            error=error,
        )


def _validate_rollback_metadata(packet: "PromotionPacket") -> tuple[bool, str]:
    """Check that rollback_metadata meets the minimum contract.

    Required keys: parameter, revert_to_value, rollback_trigger.
    All three must be present and non-empty/non-None.

    Returns:
        (True, "")         — contract met
        (False, <reason>)  — contract violated
    """
    rb = packet.rollback_metadata
    missing = ROLLBACK_REQUIRED_KEYS - rb.keys()
    if missing:
        return False, f"rollback_metadata missing keys: {sorted(missing)}"
    if rb.get("revert_to_value") is None:
        return False, "rollback_metadata.revert_to_value must not be None"
    if not rb.get("rollback_trigger"):
        return False, "rollback_metadata.rollback_trigger must not be empty"
    return True, ""


def _packet_to_bus_payload(
    packet: "PromotionPacket",
    token_id: str,
    dry_run: bool,
    committed: bool,
    commit_attempted: bool,
) -> dict:
    """Convert a PromotionPacket to a BUS T PROMOTION_ROLLOUT payload."""
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
