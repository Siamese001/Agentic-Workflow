"""3-touch follow-up cadence engine.

W3-P9 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

Pure state-machine engine that decides, for a given recipient and the
current UTC time, whether to send the next message in a 3-touch sequence
and what message template to use. Persistence is OUT OF SCOPE —
``CadenceStateRecord`` is mutable input/output; callers persist it.

State machine:

    INITIAL (day 0)
        advance() at/after next_action_at_utc → SEND "initial" template
        → next_state = FOLLOWUP_1
        → next_check_at_utc = now + 5 days

    FOLLOWUP_1 (day 5, unless replied)
        advance() at/after next_action_at_utc → SEND "followup_1"
        → next_state = FOLLOWUP_2
        → next_check_at_utc = now + 7 days

    FOLLOWUP_2 (day 12, unless replied)
        advance() at/after next_action_at_utc → SEND "followup_2"
        → next_state = TERMINATED
        → terminated_reason = "sequence_complete"

    TERMINATED (any time)
        advance() → NO_ACTION always

Reply short-circuit:
    record.replied = True at ANY state → TERMINATED, NO_ACTION,
    terminated_reason = "replied".

Operator stop:
    ``terminate(record, reason="operator_stop")`` — callers use this
    to force-stop a cadence (e.g., recipient opted out).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from apps_lic.types.cadence_state_types import (
    DAYS_TO_FOLLOWUP_1,
    DAYS_TO_FOLLOWUP_2,
    CadenceAction,
    CadenceDecision,
    CadenceState,
    CadenceStateRecord,
)


class FollowupCadenceEngine:
    """Stateless engine — all state lives in the caller's ``CadenceStateRecord``.

    The engine is thread-safe because it has no mutable attributes;
    callers are responsible for per-record locking when persisting.
    """

    def advance(
        self,
        record: CadenceStateRecord,
        now_utc: Optional[datetime] = None,
    ) -> CadenceDecision:
        """Advance the cadence state machine once.

        Args:
            record: The recipient's current cadence state. Mutated
                in-place with post-advance state. Callers MUST persist
                ``record`` after the call.
            now_utc: UTC timestamp to treat as "now". When None,
                ``datetime.now(timezone.utc)`` is used. Accepting an
                injected clock makes the engine deterministic in tests.

        Returns:
            ``CadenceDecision`` describing the action. When action is
            SEND, the caller sends the message and then calls
            ``mark_sent(record, sent_at_utc)`` to bind the send timestamp.
        """
        now = now_utc if now_utc is not None else datetime.now(timezone.utc)

        # Reply short-circuit beats everything else.
        if record.replied and record.current_state is not CadenceState.TERMINATED:
            record.current_state = CadenceState.TERMINATED
            record.terminated_reason = "replied"
            record.next_action_at_utc = None
            return CadenceDecision(
                action=CadenceAction.NO_ACTION,
                next_state=CadenceState.TERMINATED,
                message_template=None,
                next_check_at_utc=None,
                reason="reply received; cadence terminated",
            )

        if record.current_state is CadenceState.TERMINATED:
            return CadenceDecision(
                action=CadenceAction.NO_ACTION,
                next_state=CadenceState.TERMINATED,
                message_template=None,
                next_check_at_utc=None,
                reason=(
                    f"cadence terminated ({record.terminated_reason or 'unknown'})"
                ),
            )

        # Not yet time for the next action?
        if record.next_action_at_utc is not None and now < record.next_action_at_utc:
            return CadenceDecision(
                action=CadenceAction.WAIT,
                next_state=record.current_state,
                message_template=None,
                next_check_at_utc=record.next_action_at_utc,
                reason=(
                    f"scheduled send not yet due; current state "
                    f"{record.current_state.value}"
                ),
            )

        # Transition on the SEND.
        if record.current_state is CadenceState.INITIAL:
            next_check = now + timedelta(days=DAYS_TO_FOLLOWUP_1)
            record.current_state = CadenceState.FOLLOWUP_1
            record.next_action_at_utc = next_check
            if record.initial_scheduled_at_utc is None:
                record.initial_scheduled_at_utc = now
            return CadenceDecision(
                action=CadenceAction.SEND,
                next_state=CadenceState.FOLLOWUP_1,
                message_template="initial",
                next_check_at_utc=next_check,
                reason="day-0 initial send",
            )

        if record.current_state is CadenceState.FOLLOWUP_1:
            next_check = now + timedelta(days=DAYS_TO_FOLLOWUP_2)
            record.current_state = CadenceState.FOLLOWUP_2
            record.next_action_at_utc = next_check
            return CadenceDecision(
                action=CadenceAction.SEND,
                next_state=CadenceState.FOLLOWUP_2,
                message_template="followup_1",
                next_check_at_utc=next_check,
                reason="day-5 followup send",
            )

        if record.current_state is CadenceState.FOLLOWUP_2:
            record.current_state = CadenceState.TERMINATED
            record.terminated_reason = "sequence_complete"
            record.next_action_at_utc = None
            return CadenceDecision(
                action=CadenceAction.SEND,
                next_state=CadenceState.TERMINATED,
                message_template="followup_2",
                next_check_at_utc=None,
                reason="day-12 final send; sequence complete",
            )

        # Unreachable if CadenceState stays a closed enum — defensive path.
        return CadenceDecision(
            action=CadenceAction.NO_ACTION,
            next_state=record.current_state,
            message_template=None,
            next_check_at_utc=None,
            reason=f"unknown cadence state {record.current_state!r}",
        )

    def mark_sent(
        self,
        record: CadenceStateRecord,
        sent_at_utc: Optional[datetime] = None,
    ) -> None:
        """Bind the most recent send timestamp and bump ``send_count``.

        Call after a successful message dispatch.
        """
        record.last_sent_at_utc = sent_at_utc or datetime.now(timezone.utc)
        record.send_count += 1

    def mark_replied(self, record: CadenceStateRecord) -> None:
        """Record a reply. Next ``advance`` call transitions to TERMINATED."""
        record.replied = True

    def terminate(
        self,
        record: CadenceStateRecord,
        reason: str = "operator_stop",
    ) -> None:
        """Force-stop the cadence (e.g., recipient opt-out)."""
        record.current_state = CadenceState.TERMINATED
        record.terminated_reason = reason
        record.next_action_at_utc = None


__all__ = [
    "FollowupCadenceEngine",
]
