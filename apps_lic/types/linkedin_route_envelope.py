"""Canonical LinkedIn route envelope for apps_lic outreach drafts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ROUTE_INMAIL = "INMAIL"
ROUTE_CONNECTION_REQUEST = "CONNECTION_REQ"
ROUTE_LINKEDIN_DIRECT = "LINKEDIN_DIRECT"

CHANNEL_LINKEDIN_INMAIL = "linkedin_inmail"
CHANNEL_LINKEDIN_CHAT = "linkedin_chat"
CHANNEL_LEGACY_LINKEDIN = "linkedin"

CONNECTION_NOT_CONNECTED = "NOT_CONNECTED"
CONNECTION_CONNECTED = "CONNECTED"

INMAIL_BODY_CHAR_CAP = 1900
CONNECTION_REQUEST_CHAR_CAP = 300


@dataclass(frozen=True)
class LinkedInRouteEnvelope:
    route: str
    channel: str
    connection_status: str
    premium_available: bool
    hard_cap_chars: int
    subject_required: bool
    signature_required: bool
    decision_reason: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.linkedin_route_envelope.v1",
            "route": self.route,
            "channel": self.channel,
            "connection_status": self.connection_status,
            "premium_available": self.premium_available,
            "hard_cap_chars": self.hard_cap_chars,
            "subject_required": self.subject_required,
            "signature_required": self.signature_required,
            "decision_reason": self.decision_reason,
        }


def _normalize(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _normalize_channel(value: Any) -> str:
    channel = str(value or "").strip().lower()
    return channel or CHANNEL_LEGACY_LINKEDIN


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "y"}


def resolve_linkedin_route_envelope(
    *,
    channel: str = CHANNEL_LEGACY_LINKEDIN,
    connection_status: str = CONNECTION_NOT_CONNECTED,
    premium_available: bool = True,
    route_override: str = "",
) -> LinkedInRouteEnvelope:
    """Resolve the draft route before prompt assembly.

    The canonical default is InMail because the user-visible apps_lic use case
    is mostly not-yet-connected LinkedIn outreach where Premium/InMail is
    available. Explicit chat/connection overrides keep the <300 path available.
    """
    normalized_channel = _normalize_channel(channel)
    normalized_status = _normalize(connection_status) or CONNECTION_NOT_CONNECTED
    premium = _coerce_bool(premium_available)
    route = _normalize(route_override)

    if route in {ROUTE_INMAIL, "IN_MAIL"} or normalized_channel == CHANNEL_LINKEDIN_INMAIL:
        return LinkedInRouteEnvelope(
            route=ROUTE_INMAIL,
            channel=CHANNEL_LINKEDIN_INMAIL,
            connection_status=normalized_status,
            premium_available=premium,
            hard_cap_chars=INMAIL_BODY_CHAR_CAP,
            subject_required=True,
            signature_required=True,
            decision_reason="explicit_inmail_route_or_channel",
        )
    if route in {ROUTE_CONNECTION_REQUEST, "CONNECTION_REQUEST"} or normalized_channel == CHANNEL_LINKEDIN_CHAT:
        return LinkedInRouteEnvelope(
            route=ROUTE_CONNECTION_REQUEST,
            channel=CHANNEL_LINKEDIN_CHAT,
            connection_status=normalized_status,
            premium_available=premium,
            hard_cap_chars=CONNECTION_REQUEST_CHAR_CAP,
            subject_required=False,
            signature_required=False,
            decision_reason="explicit_connection_request_or_chat_channel",
        )
    if normalized_status == CONNECTION_NOT_CONNECTED and premium:
        return LinkedInRouteEnvelope(
            route=ROUTE_INMAIL,
            channel=CHANNEL_LINKEDIN_INMAIL,
            connection_status=normalized_status,
            premium_available=True,
            hard_cap_chars=INMAIL_BODY_CHAR_CAP,
            subject_required=True,
            signature_required=True,
            decision_reason="not_connected_premium_available",
        )
    if normalized_status == CONNECTION_NOT_CONNECTED:
        return LinkedInRouteEnvelope(
            route=ROUTE_CONNECTION_REQUEST,
            channel=CHANNEL_LINKEDIN_CHAT,
            connection_status=normalized_status,
            premium_available=False,
            hard_cap_chars=CONNECTION_REQUEST_CHAR_CAP,
            subject_required=False,
            signature_required=False,
            decision_reason="not_connected_no_premium_connection_request",
        )
    return LinkedInRouteEnvelope(
        route=ROUTE_LINKEDIN_DIRECT,
        channel=CHANNEL_LINKEDIN_INMAIL,
        connection_status=normalized_status or CONNECTION_CONNECTED,
        premium_available=premium,
        hard_cap_chars=INMAIL_BODY_CHAR_CAP,
        subject_required=False,
        signature_required=True,
        decision_reason="connected_long_form_direct_draft",
    )


def subject_required_for_channel(channel: str) -> bool:
    return _normalize_channel(channel) == CHANNEL_LINKEDIN_INMAIL


def hard_cap_for_channel(channel: str, default: int) -> int:
    normalized = _normalize_channel(channel)
    if normalized == CHANNEL_LINKEDIN_INMAIL:
        return INMAIL_BODY_CHAR_CAP
    if normalized == CHANNEL_LINKEDIN_CHAT:
        return CONNECTION_REQUEST_CHAR_CAP
    return default


__all__ = [
    "CHANNEL_LEGACY_LINKEDIN",
    "CHANNEL_LINKEDIN_CHAT",
    "CHANNEL_LINKEDIN_INMAIL",
    "CONNECTION_CONNECTED",
    "CONNECTION_NOT_CONNECTED",
    "CONNECTION_REQUEST_CHAR_CAP",
    "INMAIL_BODY_CHAR_CAP",
    "LinkedInRouteEnvelope",
    "ROUTE_CONNECTION_REQUEST",
    "ROUTE_INMAIL",
    "ROUTE_LINKEDIN_DIRECT",
    "hard_cap_for_channel",
    "resolve_linkedin_route_envelope",
    "subject_required_for_channel",
]
