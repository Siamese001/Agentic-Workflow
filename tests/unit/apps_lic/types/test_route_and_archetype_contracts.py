"""W8 contract tests for zero-cover apps_lic route/archetype/type surfaces."""

from __future__ import annotations

from dataclasses import fields

from apps_lic.types import (
    app_content_validator_agent_types,
    competitor_recon_agent_types,
    message_route_types,
    recipient_archetype_types,
    route_types,
    validation_severity_types,
)

# W8 ADG covers-edge anchors: the `from apps_lic.types import <submodule>` style
# above resolves to the package `__init__` only, so the individual P1 type files
# stay zero-cover in the runtime-proxy. Importing one symbol from each module via
# its FULL module path makes ADG emit a `covers` edge to each individual file.
from apps_lic.types.app_content_validator_agent_types import (
    ContentViolationType as _ContentViolationTypeAnchor,
)
from apps_lic.types.competitor_recon_agent_types import CompetitorMove as _CompetitorMoveAnchor
from apps_lic.types.message_route_types import MessageRoute as _MessageRouteAnchor
from apps_lic.types.recipient_archetype_types import (
    RecipientArchetype as _RecipientArchetypeAnchor,
)
from apps_lic.types.route_types import Route as _RouteAnchor
from apps_lic.types.validation_severity_types import (
    ValidationSeverity as _ValidationSeverityAnchor,
)


def test_route_type_enums_and_connection_request_constraints_are_stable() -> None:
    assert [route.value for route in route_types.Route] == [
        "INMAIL",
        "CONNECTION_REQ",
        "EMAIL",
        "FOLLOW_UP",
        "SHORT_NEW",
        "LONG_NEW",
    ]
    assert [item.value for item in route_types.Archetype] == [
        "C_LEVEL",
        "EXECUTIVE",
        "SENIOR_TA",
        "RECRUITER",
    ]
    assert [item.value for item in route_types.ValidationSeverity] == [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "INFO",
    ]

    cfg = route_types.get_route_config(route_types.Route.CONNECTION_REQ)
    assert cfg is not None
    assert cfg.char_limit is not None
    assert cfg.char_limit.max == 300
    assert cfg.signature_format == "simplified"
    assert cfg.subject_line is False
    assert cfg.attachments_allowed is False
    assert route_types.classify_archetype("Chief Technology Officer") == route_types.Archetype.C_LEVEL


def test_message_route_constraints_pin_no_attachment_connection_requests() -> None:
    assert [route.value for route in message_route_types.MessageRoute] == [
        "CONNECTION_REQ",
        "SHORT_NEW",
        "LONG_NEW",
        "FOLLOW_UP",
        "INMAIL",
    ]
    assert [item.value for item in message_route_types.RecipientArchetype] == [
        "C_LEVEL",
        "EXECUTIVE",
        "SENIOR_TA",
        "RECRUITER",
        "HIRING_MANAGER",
    ]
    assert [item.value for item in message_route_types.SignatureFormat] == [
        "standard",
        "simplified",
        "professional",
        "warm",
    ]

    cfg = message_route_types.get_route_config(message_route_types.MessageRoute.CONNECTION_REQ)
    assert cfg.constraints.char_limit == 300
    assert cfg.constraints.signature_format is message_route_types.SignatureFormat.SIMPLIFIED
    assert cfg.constraints.subject_line_enabled is False
    assert cfg.constraints.attachments_enabled is False
    assert cfg.constraints.cta_format is message_route_types.CTAFormat.MICRO
    tone = message_route_types.get_archetype_tone(
        message_route_types.RecipientArchetype.HIRING_MANAGER
    )
    assert tone.focus == "VALUE_PROPOSITION"


def test_recipient_and_legacy_type_contracts_have_expected_fields() -> None:
    assert [item.value for item in recipient_archetype_types.RecipientArchetype] == [
        "C_LEVEL",
        "EXECUTIVE",
        "SENIOR_TA",
        "RECRUITER",
    ]
    assert [field.name for field in fields(competitor_recon_agent_types.CompetitorMove)] == [
        "competitor_name",
        "recent_launch",
        "source_url",
        "date",
    ]
    assert [field.name for field in fields(competitor_recon_agent_types.StrategicHook)] == [
        "hook_text",
        "relevance_score",
        "competitive_gap",
    ]
    assert [item.value for item in app_content_validator_agent_types.ContentViolationType] == [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
    ]
    assert [field.name for field in fields(app_content_validator_agent_types.ContentConfig)] == [
        "validate_email",
        "validate_linkedin",
        "validate_phone",
        "require_contact",
        "check_profanity",
        "check_spam",
        "check_placeholders",
        "check_similarity",
        "similarity_threshold",
        "min_unique_ratio",
        "min_length",
        "max_length",
        "profanity_patterns",
        "spam_patterns",
        "placeholder_patterns",
    ]


def test_validation_severity_contracts_pin_low_and_claim_config_thresholds() -> None:
    assert [item.value for item in validation_severity_types.ValidationSeverity] == [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
        "INFO",
    ]
    assert [field.name for field in fields(validation_severity_types.ErrorCode)] == [
        "code",
        "Severity",
        "description",
        "remediation",
    ]
    signal_config = validation_severity_types.get_signal_config()
    claim_config = validation_severity_types.get_claim_config()
    assert signal_config.min_signal_threshold > 0.0
    assert claim_config.min_claim_confidence > 0.0
    assert claim_config.min_overlap_words >= 1


def test_w8_full_path_imports_anchor_per_file_covers_edges() -> None:
    """Pin full-module-path imports so each zero-cover type module is a distinct
    ADG `covers` target (submodule-as-name imports collapse onto the package)."""
    for anchor in (
        _RouteAnchor,
        _MessageRouteAnchor,
        _RecipientArchetypeAnchor,
        _CompetitorMoveAnchor,
        _ContentViolationTypeAnchor,
        _ValidationSeverityAnchor,
    ):
        assert anchor is not None
