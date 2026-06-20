"""apps_shared.contracts.outreach_history_contract — D6-P3 (DS4).

Plan: .codex/plans/apps-lic-calibration-holdout-e8f1c4.md W2 DS4-P1

Canonical data contract for outreach history passed to
MultiTouchSequencer. Callers populate this contract; the engine accepts
``list[OutreachTouchRecord]`` typed to this module's definition.

Invariants
----------
- Immutable frozen dataclass — no mutable fields.
- No durable state reads or writes.
- No provider API calls.
- No subprocess calls.
- Schema is stable: adding optional fields is allowed; removing or
  renaming existing fields is a breaking change requiring a new version.

Field definitions
-----------------
touch_number      : 1-based index of this outreach touch.
sent_at_iso       : ISO 8601 UTC timestamp when touch was sent.
                    Empty string = unknown (tolerated for legacy data).
channel           : delivery channel — e.g. "email", "linkedin", "phone".
                    Empty string = unspecified.
response_received : True if the recipient replied to this touch (any
                    reply, including negative / out-of-office counts).
response_at_iso   : ISO 8601 UTC timestamp of the first response.
                    Empty string when response_received=False.
message_subject   : Subject line or opening line for reference.
                    Empty string = not recorded.
"""

from __future__ import annotations

from dataclasses import dataclass, field


CONTRACT_VERSION: str = "1.0"
CONTRACT_NAME: str = "apps_shared.outreach_history"


@dataclass(frozen=True)
class OutreachTouchRecord:
    """Canonical record of a single prior outreach touch.

    Attributes
    ----------
    touch_number      : 1-based touch index (1 = first ever sent).
    sent_at_iso       : ISO 8601 UTC timestamp; empty = unknown.
    channel           : delivery channel; empty = unspecified.
    response_received : True when any reply was received.
    response_at_iso   : ISO 8601 UTC timestamp of first reply; empty when none.
    message_subject   : Opening line / subject for reference; empty = not recorded.
    """

    touch_number: int
    sent_at_iso: str = ""
    channel: str = ""
    response_received: bool = False
    response_at_iso: str = ""
    message_subject: str = ""

    def __post_init__(self) -> None:
        if self.touch_number < 1:
            raise ValueError(
                f"OutreachTouchRecord.touch_number must be ≥ 1, got {self.touch_number}"
            )
        if self.response_received and not self.response_at_iso:
            pass  # response_at_iso is optional even when response_received=True


@dataclass(frozen=True)
class OutreachHistory:
    """Ordered sequence of prior touches for a single recipient.

    Wraps ``list[OutreachTouchRecord]`` with basic validation.

    Attributes
    ----------
    touches      : ordered list of touch records (earliest first).
    recipient_id : opaque caller-assigned identifier for the recipient.
                   Not read by the engine; carried for traceability.
    """

    touches: tuple[OutreachTouchRecord, ...]
    recipient_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.touches, tuple):
            object.__setattr__(self, "touches", tuple(self.touches))

    @classmethod
    def from_list(
        cls,
        records: list[OutreachTouchRecord],
        *,
        recipient_id: str = "",
    ) -> "OutreachHistory":
        """Construct from a plain list (convenience)."""
        return cls(touches=tuple(records), recipient_id=recipient_id)

    def as_engine_list(self) -> list[OutreachTouchRecord]:
        """Return touches as a plain list suitable for MultiTouchSequencer."""
        return list(self.touches)

    @property
    def touch_count(self) -> int:
        return len(self.touches)

    @property
    def last_response_received(self) -> bool:
        return any(t.response_received for t in self.touches)


__all__ = [
    "CONTRACT_VERSION",
    "CONTRACT_NAME",
    "OutreachTouchRecord",
    "OutreachHistory",
]
