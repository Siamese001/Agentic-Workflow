"""apps_underwriting_ai FEC producer — builds FinalEvidenceContract dict.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-underwriting-ai-c0-fec-producer-wiring-f6b3d9.md`` W1.P1.
W5.1 extension: adds ``PublicTrustReceipt``, ``route_family``,
``reason_code_bundle``, evidence coverage, hitl_posture, and
``deterministic_rationale_fallback_used`` fields.

Pattern source: ``apps_qna/cert/fec_producer.py`` (completed via
``apps-qna-c0-fec-producer-wiring-d4f1e8``).

Shape
-----
Returned dict follows ``ExitReviewPacket.final_evidence_contract``:

    {
        "schema_version": "1.1",
        "producer": "apps_underwriting_ai.cert.fec_producer",
        "grounded": <bool>,
        "retrieval_sources": [<document_id | section_anchor>, ...],
        "template_ids": ["decision_packet_v1"],
        "route_id": "apps_underwriting_ai.decision_packet_v1",
        "route_family": "R3R4_MANAGED_WORKFLOW",
        "evidence_sufficiency": "grounded" | "template_only" | "empty",
        "reason_code_bundle": [<str>, ...],
        "evidence_coverage": {
            "required_classes_present": [<str>, ...],
            "optional_classes_present": [<str>, ...],
            "missing_required_classes": [<str>, ...],
            "contradiction_flags_count": <int>,
            "documents_received_count": <int>,
            "documents_missing_count": <int>,
        },
        "hitl_posture": "HITL_REQUIRED" | "HITL_ADVISORY" | "HITL_NONE",
        "deterministic_rationale_fallback_used": <bool>,
        "public_trust_receipt": {PublicTrustReceipt.to_dict()},
    }

Source extraction — in priority order:

1. Explicit ``run_context["c0_retrieval_sources"]`` (forward-compat override).
2. ``run_context["uw_result"].register`` — EvidenceRegister rows expose
   ``source_doc`` / ``source_id`` attributes per parser convention.
3. ``run_context["uw_result"].request.statements`` — parsed document
   ids carried on the request envelope.

When none yields sources, returns ``grounded=False``,
``evidence_sufficiency="template_only"``. Empty/malformed context never
raises — producer is READ-ONLY and degrades to an ``empty`` packet.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.1"
_PRODUCER_ID = "apps_underwriting_ai.cert.fec_producer"
_DEFAULT_ROUTE = "apps_underwriting_ai.decision_packet_v1"
_DEFAULT_TEMPLATE_IDS = ("decision_packet_v1",)
_DEFAULT_ROUTE_FAMILY = "R3R4_MANAGED_WORKFLOW"


# ---------------------------------------------------------------------------
# PublicTrustReceipt
# ---------------------------------------------------------------------------

@dataclass
class PublicTrustReceipt:
    """Public-facing trust receipt attached to every FEC.

    Carries the fields listed in the spine plan PublicTrustReceipt section.
    All fields are read-only post-construction — the receipt is sealed when
    ``produce_fec()`` returns.

    Fields
    ------
    route_family : str
        Route family used for this decision (e.g. ``R3R4_MANAGED_WORKFLOW``).
    underwriting_route_mode : str
        Mode within the route family (e.g. ``FULL_DECISION_PACKET``).
    evidence_contract_status : str
        C0 state of the FinalEvidenceContract (``PASS`` / ``WEAK_WITH_CAVEATS`` / ``FAIL``).
    documents_received_count : int
        Total documents received from the applicant.
    documents_missing_count : int
        Count of required document classes absent from the submission.
    contradiction_flags_count : int
        Number of contradiction flags raised by the C0 adapter.
    demo_scorer_version : str
        Version tag of the DeterministicRiskScorer used.
    demo_policy_hash : str
        Policy hash bound to this run (empty when not available).
    replay_key_prefix : str
        Prefix of the replay key for exact-cache gate (first 12 chars).
    exit_disposition : str
        Exit X3 disposition class emitted for this run.
    hitl_posture : str
        HITL posture resolved by the L3 adapter.
    generated_rationale_used : bool
        True when the LLM rationale was accepted by the firewall.
    deterministic_rationale_fallback_used : bool
        True when the firewall fell back to the deterministic rationale.
    demo_packet_id : str
        Unique ID for this decision packet instance.
    demo_mode : bool
        Always True — this app produces synthetic demo packets only.
    """

    route_family: str = _DEFAULT_ROUTE_FAMILY
    underwriting_route_mode: str = "FULL_DECISION_PACKET"
    evidence_contract_status: str = "UNKNOWN"
    documents_received_count: int = 0
    documents_missing_count: int = 0
    contradiction_flags_count: int = 0
    demo_scorer_version: str = "deterministic_risk_scorer_v1"
    demo_policy_hash: str = ""
    replay_key_prefix: str = ""
    exit_disposition: str = "UNKNOWN"
    hitl_posture: str = "HITL_NONE"
    generated_rationale_used: bool = False
    deterministic_rationale_fallback_used: bool = True
    demo_packet_id: str = ""
    demo_mode: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float)) and str(item)]


def _safe_str(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _extract_register_sources(uw_result: Any) -> list[str]:
    register = getattr(uw_result, "register", None)
    rows = getattr(register, "rows", None) if register is not None else None
    if not isinstance(rows, (list, tuple)):
        return []
    ids: list[str] = []
    for row in rows:
        for attr in ("source_doc", "source_id", "doc_id", "anchor"):
            value = getattr(row, attr, None)
            if isinstance(value, str) and value:
                ids.append(value)
                break
    return ids


def _extract_statement_ids(uw_result: Any) -> list[str]:
    request = getattr(uw_result, "request", None)
    statements = getattr(request, "statements", None) if request is not None else None
    if not isinstance(statements, (list, tuple)):
        return []
    ids: list[str] = []
    for stmt in statements:
        for attr in ("document_id", "id", "path"):
            value = getattr(stmt, attr, None)
            if isinstance(value, str) and value:
                ids.append(value)
                break
    return ids


def _extract_evidence_coverage(ctx: Mapping[str, Any]) -> dict[str, Any]:
    """Extract evidence coverage fields from C0 FinalEvidenceContract in run_context."""
    fec: Any = ctx.get("final_evidence_contract")
    if not isinstance(fec, Mapping):
        return {
            "required_classes_present": [],
            "optional_classes_present": [],
            "missing_required_classes": [],
            "contradiction_flags_count": 0,
            "documents_received_count": 0,
            "documents_missing_count": 0,
        }
    return {
        "required_classes_present": _safe_list(fec.get("required_classes_present")),
        "optional_classes_present": _safe_list(fec.get("optional_classes_present")),
        "missing_required_classes": _safe_list(fec.get("missing_evidence_flags")),
        "contradiction_flags_count": len(_safe_list(fec.get("contradiction_flags"))),
        "documents_received_count": int(fec.get("document_count", 0)),
        "documents_missing_count": len(_safe_list(fec.get("missing_evidence_flags"))),
    }


def _build_public_trust_receipt(
    ctx: Mapping[str, Any],
    coverage: dict[str, Any],
    exit_disposition: str,
    hitl_posture: str,
    deterministic_fallback: bool,
    firewall_passed: bool,
    demo_packet_id: str,
) -> PublicTrustReceipt:
    """Construct a PublicTrustReceipt from run_context and computed fields."""
    fec: Any = ctx.get("final_evidence_contract")
    c0_state = "UNKNOWN"
    if isinstance(fec, Mapping):
        c0_state = _safe_str(fec.get("c0_state"), "UNKNOWN")

    demo_policy_hash = _safe_str(ctx.get("demo_policy_hash"))
    replay_key = _safe_str(ctx.get("replay_key"))
    replay_key_prefix = replay_key[:12] if replay_key else ""

    route_family = _safe_str(ctx.get("route_family"), _DEFAULT_ROUTE_FAMILY)

    return PublicTrustReceipt(
        route_family=route_family,
        underwriting_route_mode=_safe_str(
            ctx.get("underwriting_route_mode"), "FULL_DECISION_PACKET"
        ),
        evidence_contract_status=c0_state,
        documents_received_count=coverage["documents_received_count"],
        documents_missing_count=coverage["documents_missing_count"],
        contradiction_flags_count=coverage["contradiction_flags_count"],
        demo_scorer_version=_safe_str(
            ctx.get("demo_scorer_version"), "deterministic_risk_scorer_v1"
        ),
        demo_policy_hash=demo_policy_hash,
        replay_key_prefix=replay_key_prefix,
        exit_disposition=exit_disposition,
        hitl_posture=hitl_posture,
        generated_rationale_used=firewall_passed and not deterministic_fallback,
        deterministic_rationale_fallback_used=deterministic_fallback,
        demo_packet_id=demo_packet_id,
        demo_mode=True,
    )


def produce_fec(run_context: Mapping[str, Any]) -> dict[str, Any]:
    """Produce FEC dict from apps_underwriting_ai run_context. Never raises."""
    ctx = run_context if isinstance(run_context, Mapping) else {}

    route_id = _safe_str(ctx.get("route_id")) or _DEFAULT_ROUTE
    rc = ctx.get("route_contract")
    if isinstance(rc, Mapping):
        route_id = _safe_str(rc.get("route_id"), route_id) or route_id

    route_family = _safe_str(ctx.get("route_family"), _DEFAULT_ROUTE_FAMILY)

    template_ids = _safe_list(ctx.get("template_ids")) or list(_DEFAULT_TEMPLATE_IDS)

    # Source extraction ladder.
    retrieval_sources = _safe_list(ctx.get("c0_retrieval_sources"))
    if not retrieval_sources:
        uw_result = ctx.get("uw_result")
        if uw_result is not None:
            retrieval_sources = _extract_register_sources(uw_result)
            if not retrieval_sources:
                retrieval_sources = _extract_statement_ids(uw_result)

    # Also pull evidence_ids from FinalEvidenceContract when present.
    fec: Any = ctx.get("final_evidence_contract")
    if not retrieval_sources and isinstance(fec, Mapping):
        retrieval_sources = _safe_list(fec.get("evidence_ids"))

    # De-duplicate preserving order.
    seen: set[str] = set()
    deduped: list[str] = []
    for src in retrieval_sources:
        if src not in seen:
            deduped.append(src)
            seen.add(src)
    retrieval_sources = deduped

    explicit_grounded = ctx.get("grounded")
    grounded = (
        explicit_grounded if isinstance(explicit_grounded, bool) else bool(retrieval_sources)
    )

    if grounded:
        sufficiency = "grounded"
    elif template_ids:
        sufficiency = "template_only"
    else:
        sufficiency = "empty"

    # W5.1 — new fields.
    reason_code_bundle = _safe_list(ctx.get("reason_code_bundle"))
    hitl_posture = _safe_str(ctx.get("hitl_posture"), "HITL_NONE")
    deterministic_fallback = bool(ctx.get("deterministic_rationale_fallback_used", True))
    firewall_passed = bool(ctx.get("firewall_passed", False))
    exit_disposition = _safe_str(ctx.get("exit_disposition"), "UNKNOWN")
    demo_packet_id = _safe_str(ctx.get("demo_packet_id"))

    coverage = _extract_evidence_coverage(ctx)

    ptr = _build_public_trust_receipt(
        ctx=ctx,
        coverage=coverage,
        exit_disposition=exit_disposition,
        hitl_posture=hitl_posture,
        deterministic_fallback=deterministic_fallback,
        firewall_passed=firewall_passed,
        demo_packet_id=demo_packet_id,
    )

    return {
        "schema_version": _SCHEMA_VERSION,
        "producer": _PRODUCER_ID,
        "grounded": grounded,
        "retrieval_sources": retrieval_sources,
        "template_ids": template_ids,
        "route_id": route_id,
        "route_family": route_family,
        "evidence_sufficiency": sufficiency,
        "reason_code_bundle": reason_code_bundle,
        "evidence_coverage": coverage,
        "hitl_posture": hitl_posture,
        "deterministic_rationale_fallback_used": deterministic_fallback,
        "public_trust_receipt": ptr.to_dict(),
    }


__all__ = ["produce_fec", "PublicTrustReceipt"]
