"""apps_lic sender identity resolver.

Resolves SENDER identity from the OutreachRequest and runtime config —
NOT recipient identity. Recipient identity is part of the
PreloadedOutreachContextManifest (built by apps_research or pre-loaded).

This module is decision-only:
- No subprocess, no provider calls, no durable state writes.
- Reads config via open(path, "r") / yaml.safe_load / json.load only.
- Produces a frozen LicSenderIdentity dataclass.

Plan: .windsurf/plans/apps-lic-canonical-spine-wireup-e7c2a5.md W4 P13
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# apps_lic spine identity constants
# ---------------------------------------------------------------------------

APP_NAME: str = "apps_lic"
SOURCE_CHANNEL: str = "apps_lic_cli"
DECLARED_SCHEMA: str = "apps_lic_outreach_v1"

# Allowed recipient classes (matches outreach_schema.json enum)
ALLOWED_RECIPIENT_CLASSES = frozenset({
    "RECRUITER",
    "SENIOR_TA",
    "HIRING_MANAGER",
    "EXECUTIVE",
    "C_LEVEL",
    "VP_ENG",
    "CTO",
    "REFERRAL_CONTACT",
})

# Allowed send modes (matches outreach_schema.json enum)
ALLOWED_SEND_MODES = frozenset({
    "draft_only",
    "review_required",
    "send_ready_candidate",
})

# Forbidden send modes (rejected at U0 / L0)
FORBIDDEN_SEND_MODES = frozenset({
    "send_now",
    "auto_send",
    "connector_send",
})


# ---------------------------------------------------------------------------
# Sender identity type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LicSenderIdentity:
    """Resolved sender identity for an apps_lic outreach request.

    Contains the verified spine identity constants and per-request
    sender context extracted from the request and runtime config.

    This is SENDER identity — who is sending the outreach.
    Recipient identity is in PreloadedOutreachContextManifest.
    """

    app_name: str          # always "apps_lic"
    source_channel: str    # always "apps_lic_cli"
    declared_schema: str   # always "apps_lic_outreach_v1"

    # Per-request sender context
    request_id: str
    run_id: str
    trace_id: str

    # Sender config refs (bound to manifest)
    policy_hash: str       # sha256 of policy config used
    blueprint_hash: str    # sha256 of blueprint config used
    resume_ref: str        # sha256 of sender resume snapshot

    # Request-level fields
    recipient_class: str
    channel: str
    outreach_mode: str
    send_mode: str = "draft_only"
    omission_policy: str = "omit_unsupported"

    # Validation state
    is_valid: bool = True
    validation_errors: tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class IdentityResolutionResult:
    """Result of resolving sender identity.

    is_valid=True means the identity is fully resolved and consistent.
    is_valid=False means validation failed; errors contains the reason(s).
    """

    identity: Optional[LicSenderIdentity]
    is_valid: bool
    errors: tuple   # tuple[str, ...] of validation error messages


# ---------------------------------------------------------------------------
# Identity resolver
# ---------------------------------------------------------------------------

def resolve_sender_identity(
    *,
    request_id: str,
    run_id: str,
    trace_id: str,
    policy_hash: str,
    blueprint_hash: str,
    resume_ref: str,
    recipient_class: str,
    channel: str,
    outreach_mode: str,
    send_mode: str = "draft_only",
    omission_policy: str = "omit_unsupported",
    source_channel: str = SOURCE_CHANNEL,
    declared_schema: str = DECLARED_SCHEMA,
) -> IdentityResolutionResult:
    """Resolve and validate sender identity for an apps_lic request.

    Pure function — no side effects, no I/O.

    Validates:
    - source_channel == SOURCE_CHANNEL ("apps_lic_cli")
    - declared_schema == DECLARED_SCHEMA ("apps_lic_outreach_v1")
    - recipient_class in ALLOWED_RECIPIENT_CLASSES
    - send_mode not in FORBIDDEN_SEND_MODES
    - send_mode in ALLOWED_SEND_MODES

    Returns IdentityResolutionResult with is_valid=True on success,
    or is_valid=False with errors describing the validation failures.
    """
    errors = []

    if source_channel != SOURCE_CHANNEL:
        errors.append(
            f"source_channel={source_channel!r} does not match expected "
            f"{SOURCE_CHANNEL!r} for apps_lic."
        )

    if declared_schema != DECLARED_SCHEMA:
        errors.append(
            f"declared_schema={declared_schema!r} does not match expected "
            f"{DECLARED_SCHEMA!r} for apps_lic."
        )

    if recipient_class not in ALLOWED_RECIPIENT_CLASSES:
        errors.append(
            f"recipient_class={recipient_class!r} is not in the allowed set: "
            f"{sorted(ALLOWED_RECIPIENT_CLASSES)}"
        )

    if send_mode in FORBIDDEN_SEND_MODES:
        errors.append(
            f"send_mode={send_mode!r} is forbidden. "
            f"Allowed: {sorted(ALLOWED_SEND_MODES)}"
        )
    elif send_mode not in ALLOWED_SEND_MODES:
        errors.append(
            f"send_mode={send_mode!r} is not in allowed set: "
            f"{sorted(ALLOWED_SEND_MODES)}"
        )

    if errors:
        return IdentityResolutionResult(
            identity=None,
            is_valid=False,
            errors=tuple(errors),
        )

    identity = LicSenderIdentity(
        app_name=APP_NAME,
        source_channel=SOURCE_CHANNEL,
        declared_schema=DECLARED_SCHEMA,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        resume_ref=resume_ref,
        recipient_class=recipient_class,
        channel=channel,
        outreach_mode=outreach_mode,
        send_mode=send_mode,
        omission_policy=omission_policy,
        is_valid=True,
        validation_errors=(),
    )

    return IdentityResolutionResult(
        identity=identity,
        is_valid=True,
        errors=(),
    )
