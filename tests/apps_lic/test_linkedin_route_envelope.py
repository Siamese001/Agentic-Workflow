from apps_lic.types.linkedin_route_envelope import (
    CHANNEL_LINKEDIN_CHAT,
    CHANNEL_LINKEDIN_INMAIL,
    CONNECTION_REQUEST_CHAR_CAP,
    INMAIL_BODY_CHAR_CAP,
    ROUTE_CONNECTION_REQUEST,
    ROUTE_INMAIL,
    resolve_linkedin_route_envelope,
)
from apps_lic.types import message_route_types, route_types


def test_not_connected_premium_defaults_to_inmail() -> None:
    envelope = resolve_linkedin_route_envelope(
        channel="linkedin",
        connection_status="NOT_CONNECTED",
        premium_available=True,
    )

    assert envelope.route == ROUTE_INMAIL
    assert envelope.channel == CHANNEL_LINKEDIN_INMAIL
    assert envelope.hard_cap_chars == INMAIL_BODY_CHAR_CAP
    assert envelope.subject_required is True
    assert envelope.signature_required is True
    assert envelope.decision_reason == "not_connected_premium_available"


def test_not_connected_without_premium_uses_connection_request() -> None:
    envelope = resolve_linkedin_route_envelope(
        channel="linkedin",
        connection_status="NOT_CONNECTED",
        premium_available=False,
    )

    assert envelope.route == ROUTE_CONNECTION_REQUEST
    assert envelope.channel == CHANNEL_LINKEDIN_CHAT
    assert envelope.hard_cap_chars == CONNECTION_REQUEST_CHAR_CAP
    assert envelope.subject_required is False


def test_explicit_inmail_override_wins() -> None:
    envelope = resolve_linkedin_route_envelope(
        channel="linkedin_chat",
        connection_status="NOT_CONNECTED",
        premium_available=False,
        route_override="INMAIL",
    )

    assert envelope.route == ROUTE_INMAIL
    assert envelope.channel == CHANNEL_LINKEDIN_INMAIL
    assert envelope.subject_required is True
    assert envelope.premium_available is False
    assert envelope.decision_reason == "explicit_inmail_route_or_channel"


def test_legacy_route_config_surfaces_match_canonical_envelope_for_core_linkedin_routes() -> None:
    inmail = resolve_linkedin_route_envelope(route_override="INMAIL", premium_available=False)
    connection = resolve_linkedin_route_envelope(
        channel="linkedin",
        connection_status="NOT_CONNECTED",
        premium_available=False,
    )

    route_inmail = route_types.get_route_config(route_types.Route.INMAIL)
    assert route_inmail is not None
    assert route_inmail.char_limit is not None
    assert route_inmail.char_limit.max == inmail.hard_cap_chars
    assert route_inmail.subject_line == inmail.subject_required
    assert route_inmail.signature_format == "standard"

    route_connection = route_types.get_route_config(route_types.Route.CONNECTION_REQ)
    assert route_connection is not None
    assert route_connection.char_limit is not None
    assert route_connection.char_limit.max == connection.hard_cap_chars
    assert route_connection.subject_line == connection.subject_required
    assert route_connection.signature_format == "simplified"

    message_inmail = message_route_types.get_route_config(message_route_types.MessageRoute.INMAIL)
    assert message_inmail.constraints.subject_line_enabled == inmail.subject_required
    assert message_inmail.constraints.signature_format is message_route_types.SignatureFormat.PROFESSIONAL

    message_connection = message_route_types.get_route_config(
        message_route_types.MessageRoute.CONNECTION_REQ
    )
    assert message_connection.constraints.char_limit == connection.hard_cap_chars
    assert message_connection.constraints.subject_line_enabled == connection.subject_required
    assert message_connection.constraints.signature_format is message_route_types.SignatureFormat.SIMPLIFIED
