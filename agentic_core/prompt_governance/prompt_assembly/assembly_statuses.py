"""PA Doctrine Status Vocabulary (PA_*) — canonical status enum.

SSOT for the per-stage status names mandated by the Prompt Assembly
doctrine (``docs/reference/03_L0_Routing/Prompt Assembly/*.md``).

The doctrine specifies a fixed vocabulary of stage statuses that PA must
emit. The internal stage modules use richer / more specific result types
(:class:`BoundaryStatus`, :class:`OverflowStatus`, etc.). This module
provides:

1. The canonical :class:`PAStatus` enum with every doctrine-mandated value.
2. Per-stage mapper helpers that derive a :class:`PAStatus` from the
   existing rich result types so callers can publish doctrine-conformant
   telemetry without duplicating logic.
3. A grouping :data:`STAGE_TO_STATUSES` map listing which statuses each
   stage may legitimately emit. This is used by the doctrine compliance
   tests to ensure no stage status escapes the doctrine.

This module is pure-data / pure-function. No I/O, no side effects.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for typing
    from .pa0_boundary import BoundaryCheckResult
    from .pa3_c0_classifier import C0ClassifierResult
    from .pa3_u0_airlock import U0AirlockResult
    from .pa4_validation import PA4ValidationReport
    from .pa5_budget import BudgetReport


class PAStatus(str, Enum):
    """Canonical Prompt Assembly status vocabulary.

    Every PA stage MUST publish exactly one of these values when emitting
    doctrine receipts. Internal richer enums (BoundaryStatus, OverflowStatus,
    DispatchDisposition...) remain in place and are mapped to a PAStatus
    via the helpers in this module.
    """

    # PA.0 boundary
    PA_READY = "PA_READY"
    PA_INPUT_INCOMPLETE = "PA_INPUT_INCOMPLETE"
    PA_BOUNDARY_MISMATCH = "PA_BOUNDARY_MISMATCH"

    # PA.1 BOM
    PA_BOM_RESOLVED = "PA_BOM_RESOLVED"
    PA_BOM_GAP = "PA_BOM_GAP"

    # PA.2 slot composition
    PA_SLOTS_COMPOSED = "PA_SLOTS_COMPOSED"
    PA_SLOT_COMPOSITION_GAP = "PA_SLOT_COMPOSITION_GAP"
    PA_AUTHORITY_CONFLICT = "PA_AUTHORITY_CONFLICT"

    # PA.3 security pass
    PA_SECURITY_PASS = "PA_SECURITY_PASS"
    PA_SECURITY_GAP = "PA_SECURITY_GAP"
    PA_SAFE_EXTRACTION_PARTIAL = "PA_SAFE_EXTRACTION_PARTIAL"
    PA_SLOT_PAYLOAD_REJECTED = "PA_SLOT_PAYLOAD_REJECTED"

    # PA.4 slot contract validation
    PA_SLOT_CONTRACT_VALID = "PA_SLOT_CONTRACT_VALID"
    PA_SLOT_CONTRACT_INVALID = "PA_SLOT_CONTRACT_INVALID"
    PA_CONTEXT_CONTRACT_GAP = "PA_CONTEXT_CONTRACT_GAP"
    PA_AUTHORITY_INVERSION_GAP = "PA_AUTHORITY_INVERSION_GAP"
    PA_SCHEMA_BINDING_GAP = "PA_SCHEMA_BINDING_GAP"
    PA_TOOL_BINDING_GAP = "PA_TOOL_BINDING_GAP"

    # PA.5 budget / determinism
    PA_BUDGET_FIT = "PA_BUDGET_FIT"
    PA_BUDGET_TRIMMED = "PA_BUDGET_TRIMMED"
    PA_BUDGET_OVERFLOW = "PA_BUDGET_OVERFLOW"

    # PA.6 provider rendering
    PA_RENDERED = "PA_RENDERED"
    PA_RENDER_GAP = "PA_RENDER_GAP"
    PA_PROVIDER_FEATURE_GAP = "PA_PROVIDER_FEATURE_GAP"
    PA_SCHEMA_RENDER_GAP = "PA_SCHEMA_RENDER_GAP"
    PA_TOOL_RENDER_GAP = "PA_TOOL_RENDER_GAP"

    # PA.7 final emit
    PA_ARTIFACT_SIGNED = "PA_ARTIFACT_SIGNED"
    PA_ARTIFACT_NOT_SIGNED = "PA_ARTIFACT_NOT_SIGNED"
    PA_SIGNATURE_GAP = "PA_SIGNATURE_GAP"
    PA_MANIFEST_HASH_GAP = "PA_MANIFEST_HASH_GAP"
    PA_L2_HANDOFF_READY = "PA_L2_HANDOFF_READY"
    PA_L2_HANDOFF_GAP = "PA_L2_HANDOFF_GAP"

    # Cross-stage repair signal
    PA_REQUIRES_UPSTREAM_REPAIR = "PA_REQUIRES_UPSTREAM_REPAIR"


# ---------------------------------------------------------------------------
# Per-stage doctrine grouping
# ---------------------------------------------------------------------------

STAGE_TO_STATUSES: dict[str, frozenset[PAStatus]] = {
    "PA.0": frozenset(
        {
            PAStatus.PA_READY,
            PAStatus.PA_INPUT_INCOMPLETE,
            PAStatus.PA_BOUNDARY_MISMATCH,
            PAStatus.PA_REQUIRES_UPSTREAM_REPAIR,
        }
    ),
    "PA.1": frozenset(
        {
            PAStatus.PA_BOM_RESOLVED,
            PAStatus.PA_BOM_GAP,
            PAStatus.PA_REQUIRES_UPSTREAM_REPAIR,
        }
    ),
    "PA.2": frozenset(
        {
            PAStatus.PA_SLOTS_COMPOSED,
            PAStatus.PA_SLOT_COMPOSITION_GAP,
            PAStatus.PA_AUTHORITY_CONFLICT,
        }
    ),
    "PA.3": frozenset(
        {
            PAStatus.PA_SECURITY_PASS,
            PAStatus.PA_SECURITY_GAP,
            PAStatus.PA_SAFE_EXTRACTION_PARTIAL,
            PAStatus.PA_SLOT_PAYLOAD_REJECTED,
            PAStatus.PA_REQUIRES_UPSTREAM_REPAIR,
        }
    ),
    "PA.4": frozenset(
        {
            PAStatus.PA_SLOT_CONTRACT_VALID,
            PAStatus.PA_SLOT_CONTRACT_INVALID,
            PAStatus.PA_CONTEXT_CONTRACT_GAP,
            PAStatus.PA_AUTHORITY_INVERSION_GAP,
            PAStatus.PA_SCHEMA_BINDING_GAP,
            PAStatus.PA_TOOL_BINDING_GAP,
        }
    ),
    "PA.5": frozenset(
        {
            PAStatus.PA_BUDGET_FIT,
            PAStatus.PA_BUDGET_TRIMMED,
            PAStatus.PA_BUDGET_OVERFLOW,
            PAStatus.PA_REQUIRES_UPSTREAM_REPAIR,
        }
    ),
    "PA.6": frozenset(
        {
            PAStatus.PA_RENDERED,
            PAStatus.PA_RENDER_GAP,
            PAStatus.PA_PROVIDER_FEATURE_GAP,
            PAStatus.PA_SCHEMA_RENDER_GAP,
            PAStatus.PA_TOOL_RENDER_GAP,
        }
    ),
    "PA.7": frozenset(
        {
            PAStatus.PA_ARTIFACT_SIGNED,
            PAStatus.PA_ARTIFACT_NOT_SIGNED,
            PAStatus.PA_SIGNATURE_GAP,
            PAStatus.PA_MANIFEST_HASH_GAP,
            PAStatus.PA_L2_HANDOFF_READY,
            PAStatus.PA_L2_HANDOFF_GAP,
        }
    ),
}


# ---------------------------------------------------------------------------
# Per-stage mappers
# ---------------------------------------------------------------------------


def status_for_pa0(result: "BoundaryCheckResult") -> PAStatus:
    """Map :class:`BoundaryCheckResult` to a doctrine PA.0 status.

    SKIP routes (terminal short-circuit) are reported as
    :data:`PAStatus.PA_READY` because PA.0 has determined PA itself is
    not required — the boundary contract is satisfied without further
    assembly. Callers should branch on the original ``BoundaryStatus``
    before dispatch.
    """
    from .pa0_boundary import BoundaryFailReason, BoundaryStatus

    if result.status is BoundaryStatus.PASS:
        return PAStatus.PA_READY
    if result.status is BoundaryStatus.SKIP:
        return PAStatus.PA_READY
    # FAIL — discriminate by reason.
    reason = result.fail_reason
    if reason in {
        BoundaryFailReason.MISSING_PLAN_CONTRACT,
        BoundaryFailReason.MISSING_ROUTE_CONTRACT,
        BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE,
    }:
        return PAStatus.PA_INPUT_INCOMPLETE
    if reason in {
        BoundaryFailReason.DURABLE_WRITE_NOT_PERMITTED,
        BoundaryFailReason.HITL_REQUIRED_BUT_EXECUTABLE_REQUESTED,
        BoundaryFailReason.POLICY_HASH_MISMATCH,
    }:
        return PAStatus.PA_BOUNDARY_MISMATCH
    return PAStatus.PA_REQUIRES_UPSTREAM_REPAIR


def status_for_pa1(*, missing_required_components: bool) -> PAStatus:
    """Map the BOM resolution outcome to a doctrine PA.1 status."""
    return PAStatus.PA_BOM_GAP if missing_required_components else PAStatus.PA_BOM_RESOLVED


def status_for_pa2(*, authority_violations: int, has_required_slots: bool) -> PAStatus:
    """Map slot composition to a doctrine PA.2 status."""
    if authority_violations > 0:
        return PAStatus.PA_AUTHORITY_CONFLICT
    if not has_required_slots:
        return PAStatus.PA_SLOT_COMPOSITION_GAP
    return PAStatus.PA_SLOTS_COMPOSED


def status_for_pa3(
    *,
    u0: "U0AirlockResult | None" = None,
    classifier: "C0ClassifierResult | None" = None,
    h0_rejected: bool = False,
) -> PAStatus:
    """Map the PA.3 airlock + classifier + healer composite to a status.

    Precedence (most-blocking first):
      * any total rejection (U0 unsafe / all C0 rejected / H0 rejected) →
        PA_SLOT_PAYLOAD_REJECTED
      * any partial extraction (some C0 chunks stripped/quarantined) →
        PA_SAFE_EXTRACTION_PARTIAL
      * any U0 control-claim stripping or H0 receipt warning →
        PA_SECURITY_GAP
      * otherwise → PA_SECURITY_PASS
    """
    if h0_rejected:
        return PAStatus.PA_SLOT_PAYLOAD_REJECTED

    if u0 is not None and not u0.safe_to_proceed:
        return PAStatus.PA_SLOT_PAYLOAD_REJECTED

    if classifier is not None and classifier.total > 0:
        if classifier.reject_count == classifier.total:
            return PAStatus.PA_SLOT_PAYLOAD_REJECTED
        if classifier.strip_count > 0 or classifier.quarantine_count > 0:
            return PAStatus.PA_SAFE_EXTRACTION_PARTIAL

    if u0 is not None and u0.stripped_segments:
        return PAStatus.PA_SECURITY_GAP

    return PAStatus.PA_SECURITY_PASS


def status_for_pa4(report: "PA4ValidationReport") -> PAStatus:
    """Map :class:`PA4ValidationReport` to a doctrine PA.4 status.

    The report carries ``checks: tuple[ValidationCheckResult]`` where each
    entry has a ``passed: bool`` and a ``check_id`` of the form
    ``ctx_*``, ``schema_*``, ``tools_*``, ``authority_*`` etc.
    """
    failed = [c for c in report.checks if not c.passed]
    if not failed:
        return PAStatus.PA_SLOT_CONTRACT_VALID

    ids = {c.check_id for c in failed}
    # Discriminate by failure family — order matters (most-specific first).
    if any(i.startswith("authority_") for i in ids):
        return PAStatus.PA_AUTHORITY_INVERSION_GAP
    if any(i.startswith("ctx_") for i in ids):
        return PAStatus.PA_CONTEXT_CONTRACT_GAP
    if any(i.startswith("schema_") for i in ids):
        return PAStatus.PA_SCHEMA_BINDING_GAP
    if any(i.startswith("tools_") or i.startswith("tool_") for i in ids):
        return PAStatus.PA_TOOL_BINDING_GAP
    return PAStatus.PA_SLOT_CONTRACT_INVALID


def status_for_pa5(report: "BudgetReport") -> PAStatus:
    """Map :class:`BudgetReport` to a doctrine PA.5 status."""
    from .pa5_budget import OverflowStatus

    if report.overflow_status is OverflowStatus.OK:
        return PAStatus.PA_BUDGET_FIT
    if report.overflow_status is OverflowStatus.TRIMMED:
        return PAStatus.PA_BUDGET_TRIMMED
    return PAStatus.PA_BUDGET_OVERFLOW


def status_for_pa6(
    *,
    rendered: bool,
    missing_provider_feature: bool = False,
    schema_render_failed: bool = False,
    tool_render_failed: bool = False,
) -> PAStatus:
    """Map provider-render outcome to a doctrine PA.6 status."""
    if schema_render_failed:
        return PAStatus.PA_SCHEMA_RENDER_GAP
    if tool_render_failed:
        return PAStatus.PA_TOOL_RENDER_GAP
    if missing_provider_feature:
        return PAStatus.PA_PROVIDER_FEATURE_GAP
    if not rendered:
        return PAStatus.PA_RENDER_GAP
    return PAStatus.PA_RENDERED


def status_for_pa7(*, signed: bool, manifest_hash: str | None, handoff_ready: bool) -> PAStatus:
    """Map PA.7 outcome to a doctrine PA.7 status.

    Precedence:
        manifest hash missing  → PA_MANIFEST_HASH_GAP
        signed=False           → PA_ARTIFACT_NOT_SIGNED
        signed but no handoff  → PA_ARTIFACT_SIGNED  (still useful)
        signed and handoff     → PA_L2_HANDOFF_READY
    """
    if not manifest_hash:
        return PAStatus.PA_MANIFEST_HASH_GAP
    if not signed:
        return PAStatus.PA_ARTIFACT_NOT_SIGNED
    if not handoff_ready:
        return PAStatus.PA_ARTIFACT_SIGNED
    return PAStatus.PA_L2_HANDOFF_READY


__all__ = [
    "PAStatus",
    "STAGE_TO_STATUSES",
    "status_for_pa0",
    "status_for_pa1",
    "status_for_pa2",
    "status_for_pa3",
    "status_for_pa4",
    "status_for_pa5",
    "status_for_pa6",
    "status_for_pa7",
]
