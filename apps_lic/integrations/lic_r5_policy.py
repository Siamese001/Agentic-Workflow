"""L0 R5 policy for apps_lic.

Decision-only module. This module emits RouteContract decisions — it never
executes work, calls providers, writes durable state, or dispatches agents.

All 14 R5ReasonCode values per plan:
  apps-lic-canonical-spine-wireup-e7c2a5.md §"R5 Policy — All Reason Codes"

Forbidden in this module:
- subprocess.run / subprocess.Popen / os.system / os.popen
- Direct apps_research imports or calls
- Any provider call (LLM, search, embedding)
- open(..., mode containing "w", "a", "x", or "+")
- Path.write_text / Path.write_bytes
- json.dump / yaml.dump to any durable path
- shutil.copy / shutil.move into durable or artifact paths
- Direct L4 write APIs or any durable state mutation
- Fallback draft generation

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-canonical-spine-wireup-e7c2a5.md W4 P13
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class R5ReasonCode(str, Enum):
    """All 14 R5 reason codes for apps_lic fail-closed terminals.

    Codes are grouped by trigger category:
      - Briefing/research authorization failures (no outreach possible)
      - apps_research result quality failures (research ran but was unusable)
      - Content policy failures (structurally valid request, blocked at generation)
      - Runtime/schema errors
    """

    # --- Briefing / research authorization ---
    BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED = "BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED"
    # ^ Only fires when: (a) tenant/run policy explicitly disables governed apps_research,
    #   (b) required research capability is unavailable, (c) registry/capability/sandbox
    #   binding for apps_research fails, or (d) run explicitly forbids research.
    #   Normal missing/stale briefing routes to R3R4_MANAGED_WORKFLOW — NOT this code.

    # --- apps_research result quality (P9 fail-closed codes) ---
    APPS_RESEARCH_FAILED       = "APPS_RESEARCH_FAILED"
    APPS_RESEARCH_EMPTY        = "APPS_RESEARCH_EMPTY"
    APPS_RESEARCH_BLOCKED      = "APPS_RESEARCH_BLOCKED"
    APPS_RESEARCH_STALE        = "APPS_RESEARCH_STALE"
    APPS_RESEARCH_WEAK_SUPPORT = "APPS_RESEARCH_WEAK_SUPPORT"

    # --- Content policy failures ---
    SEND_MODE_FORBIDDEN        = "SEND_MODE_FORBIDDEN"
    HIGH_FRICTION_ASK          = "HIGH_FRICTION_ASK"
    UNSUPPORTED_MANDATORY_CLAIMS = "UNSUPPORTED_MANDATORY_CLAIMS"
    LOW_CONFIDENCE             = "LOW_CONFIDENCE"
    LOW_CONFIDENCE_SENIOR_EXEC = "LOW_CONFIDENCE_SENIOR_EXEC"
    INVALID_RECIPIENT_CLASS    = "INVALID_RECIPIENT_CLASS"

    # --- Runtime / schema errors ---
    INVALID_ROUTE_CONTRACT     = "INVALID_ROUTE_CONTRACT"
    L0_POLICY_VIOLATION        = "L0_POLICY_VIOLATION"


# ---------------------------------------------------------------------------
# Route decision type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LicRouteDecision:
    """Immutable L0 routing decision for apps_lic.

    L0 produces exactly one of these; downstream layers consume it.
    L0 never executes the route — it only decides.
    """

    route_id: str
    reason_code: Optional[str] = None
    detail: str = ""
    is_terminal: bool = False


# ---------------------------------------------------------------------------
# Run result type (for R4 path)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LicR4RunResult:
    """Result of an R4_SINGLE_ACTION run.

    Produced after L2 hop draft composition and Exit V6 evaluation.
    """

    run_id: str
    request_id: str
    trace_id: str
    route_id: str = "R4_SINGLE_ACTION"
    draft_ref: str = ""              # content hash of sealed OutreachDraft
    manifest_hash: str = ""          # bound to the manifest used
    send_mode: str = "draft_only"
    omitted_claims: List[str] = field(default_factory=list)
    is_terminal: bool = False
    r5_reason_code: Optional[str] = None
    detail: str = ""


# ---------------------------------------------------------------------------
# Routing decision functions
# ---------------------------------------------------------------------------

def decide_route(
    *,
    has_fresh_briefing: bool,
    research_authorized: bool,
    request_is_briefing_only: bool,
) -> LicRouteDecision:
    """Pure L0 routing decision — no side effects, no I/O.

    Minimal form: covers the three core route branches.
    For full decision matrix including all R5 conditions, use decide_route_full().

    Args:
        has_fresh_briefing: True if a valid, non-stale PreloadedOutreachContextManifest
            is present and passes BriefingReady validation.
        research_authorized: True if policy, capability, and registry binding for
            apps_research are all available for this tenant/run.
        request_is_briefing_only: True if the request targets briefing artifact
            production only (R3_SIMPLE_GROUNDED_READ path).

    Returns:
        LicRouteDecision with the selected route_id.
    """
    if request_is_briefing_only:
        return LicRouteDecision(route_id="R3_SIMPLE_GROUNDED_READ")

    if has_fresh_briefing:
        return LicRouteDecision(route_id="R4_SINGLE_ACTION")

    if research_authorized:
        return LicRouteDecision(route_id="R3R4_MANAGED_WORKFLOW")

    return LicRouteDecision(
        route_id="R5_FALLBACK",
        reason_code=R5ReasonCode.BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED.value,
        detail=(
            "Briefing missing or stale and research is not authorized for this run. "
            "Trigger conditions: policy disables governed apps_research, required "
            "research capability is unavailable, registry/capability/sandbox binding "
            "for apps_research fails, or the run explicitly forbids research."
        ),
        is_terminal=True,
    )


def decide_route_full(
    *,
    has_fresh_briefing: bool,
    research_authorized: bool,
    request_is_briefing_only: bool,
    send_mode: str = "draft_only",
    personalization_confidence: float = 1.0,
    recipient_class: str = "RECRUITER",
    has_safe_generic_note: bool = True,
    recipient_class_valid: bool = True,
    has_high_friction_ask: bool = False,
    has_unsupported_mandatory_claims: bool = False,
) -> LicRouteDecision:
    """Full L0 routing decision matrix — all R5 conditions evaluated.

    Evaluates the complete decision matrix from l0_policy.yaml including
    all content policy failures and confidence gates.

    All R5 terminals produce is_terminal=True. No outreach draft is
    generated for any R5 terminal.

    Args:
        has_fresh_briefing: Manifest present and passes BriefingReady validation.
        research_authorized: Policy + capability + registry all permit apps_research.
        request_is_briefing_only: briefing_only=True in request.
        send_mode: Requested send mode (forbidden modes → R5).
        personalization_confidence: 0.0–1.0; <0.3 → LOW_CONFIDENCE.
        recipient_class: For senior exec confidence gate.
        has_safe_generic_note: When True, low-confidence senior exec may proceed.
        recipient_class_valid: False → INVALID_RECIPIENT_CLASS.
        has_high_friction_ask: True → HIGH_FRICTION_ASK R5 terminal.
        has_unsupported_mandatory_claims: True + fail_closed policy → R5.

    Returns:
        LicRouteDecision with the selected route_id and optional R5 reason code.
    """
    _FORBIDDEN_SEND_MODES = frozenset({"send_now", "auto_send", "connector_send"})
    _SENIOR_EXEC_CLASSES = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"})

    # --- Structural checks first ---
    if not recipient_class_valid:
        return LicRouteDecision(
            route_id="R5_FALLBACK",
            reason_code=R5ReasonCode.INVALID_RECIPIENT_CLASS.value,
            detail=f"recipient_class={recipient_class!r} is not in the allowed set.",
            is_terminal=True,
        )

    if send_mode in _FORBIDDEN_SEND_MODES:
        return LicRouteDecision(
            route_id="R5_FALLBACK",
            reason_code=R5ReasonCode.SEND_MODE_FORBIDDEN.value,
            detail=f"send_mode={send_mode!r} is forbidden. Allowed: draft_only, review_required, send_ready_candidate.",
            is_terminal=True,
        )

    if has_high_friction_ask:
        return LicRouteDecision(
            route_id="R5_FALLBACK",
            reason_code=R5ReasonCode.HIGH_FRICTION_ASK.value,
            detail="HIGH_FRICTION_ASK pattern detected pre-generation. Blocked to avoid wasting generation tokens.",
            is_terminal=True,
        )

    if has_unsupported_mandatory_claims:
        return LicRouteDecision(
            route_id="R5_FALLBACK",
            reason_code=R5ReasonCode.UNSUPPORTED_MANDATORY_CLAIMS.value,
            detail="Mandatory claims have no source_items backing and omission_policy=fail_closed.",
            is_terminal=True,
        )

    # --- Confidence gates ---
    if personalization_confidence < 0.3:
        return LicRouteDecision(
            route_id="R5_FALLBACK",
            reason_code=R5ReasonCode.LOW_CONFIDENCE.value,
            detail=f"personalization_confidence={personalization_confidence:.2f} < 0.3 threshold.",
            is_terminal=True,
        )

    if (
        recipient_class.upper() in _SENIOR_EXEC_CLASSES
        and personalization_confidence < 0.5
        and not has_safe_generic_note
    ):
        return LicRouteDecision(
            route_id="R5_FALLBACK",
            reason_code=R5ReasonCode.LOW_CONFIDENCE_SENIOR_EXEC.value,
            detail=(
                f"recipient_class={recipient_class!r} requires confidence >= 0.5 "
                f"(got {personalization_confidence:.2f}) and no safe generic note is available."
            ),
            is_terminal=True,
        )

    # --- Route selection (normal paths) ---
    return decide_route(
        has_fresh_briefing=has_fresh_briefing,
        research_authorized=research_authorized,
        request_is_briefing_only=request_is_briefing_only,
    )
