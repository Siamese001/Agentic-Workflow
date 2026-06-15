"""C0.3 sender proof graph selection for apps_lic W5.

This module scores approved sender proof points against the target context and
emits a PA-ready data envelope. It is deterministic and read-only.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_COMPANY,
    NAMESPACE_COMPANY_TRIGGER,
    NAMESPACE_JD,
    NAMESPACE_ROLE_OWNERSHIP,
    OpportunityFactDocument,
    OpportunityFactStore,
)
from apps_lic.engines.message_type_requirement_gate import (
    STATUS_REQUIREMENTS_PASS,
    MessageRequirementGateResult,
)
from apps_lic.engines.recipient_classification import (
    CLASS_CEO,
    CLASS_CTO,
    CLASS_C_LEVEL,
    CLASS_EXECUTIVE,
    CLASS_HIRING_MANAGER,
    CLASS_RECRUITER,
    CLASS_SENIOR_TA,
    CLASS_VP_ENG,
    STATUS_DERIVED as RECIPIENT_STATUS_DERIVED,
    RecipientClassDerivation,
)
from apps_lic.engines.standing_sender_knowledge import (
    PERMISSION_ALLOW,
    ApprovedSenderProofPoint,
    load_standing_sender_corpus,
    check_standing_sender_corpus_readiness,
)
from apps_lic.integrations.apps_rg_proof_bridge import (
    proof_provenance_for,
    recipient_fit_weight,
)


STATUS_PROOF_GRAPH_READY = "SENDER_PROOF_GRAPH_READY"
STATUS_PROOF_GRAPH_NO_MATCH = "SENDER_PROOF_GRAPH_NO_MATCH"
STATUS_PROOF_GRAPH_BLOCKED = "SENDER_PROOF_GRAPH_BLOCKED"
STATUS_PROOF_GRAPH_READINESS_ERROR = "SENDER_PROOF_GRAPH_READINESS_ERROR"

STATUS_CLAIMS_PASS = "SENDER_PROOF_CLAIMS_PASS"
STATUS_CLAIMS_BLOCKED = "SENDER_PROOF_CLAIMS_BLOCKED"

PERMISSION_OMIT = "omit"
PERMISSION_BLOCK = "block"
PERMISSION_ESCALATE = "escalate"

REASON_RECIPIENT_CLASS_NOT_DERIVED = "recipient_class_not_derived"
REASON_MESSAGE_REQUIREMENTS_NOT_PASSED = "message_requirements_not_passed"
REASON_SENDER_CORPUS_READINESS_ERROR = "sender_corpus_readiness_error"
REASON_CLAIM_PERMISSION_NOT_ALLOW = "claim_permission_not_allow"
REASON_UNSUPPORTED_SENDER_CLAIM = "unsupported_sender_claim"
REASON_CLAIM_NOT_IN_PACKET = "claim_not_in_c03_packet"
REASON_NOT_ALLOWED_FOR_SCOPE = "not_allowed_for_message_scope"
REASON_LOWER_RELEVANCE = "lower_relevance_than_selected"

PA_INSTRUCTION_DATA_BOUNDARY_RECEIPT = (
    "pass:sender_proof_packet_is_data_only_not_instruction"
)

_STRENGTH_SCORE: dict[str, float] = {
    "strong": 3.0,
    "medium": 2.0,
    "light": 1.0,
    "blocked": -100.0,
}

_EXEC_CLASSES = {
    CLASS_EXECUTIVE,
    CLASS_C_LEVEL,
    CLASS_CEO,
    CLASS_CTO,
    CLASS_VP_ENG,
}

_ROLE_FAMILY_TAGS: dict[str, tuple[str, ...]] = {
    "data_ai": (
        "agentic-platform",
        "governance",
        "reliability",
        "cloud-native",
        "data-platform",
        "decision-systems",
    ),
    "engineering": (
        "agentic-platform",
        "reliability",
        "cloud-native",
        "ai-cicd",
    ),
    "risk_governance": (
        "quantitative-governance",
        "risk",
        "governance",
        "regulated",
    ),
    "product": (
        "productization",
        "platform-economics",
        "leadership",
    ),
}


@dataclass(frozen=True)
class ProofRelevanceSignal:
    reason_code: str
    source: str
    weight: float
    matched_value: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason_code": self.reason_code,
            "source": self.source,
            "weight": self.weight,
            "matched_value": self.matched_value,
        }


@dataclass(frozen=True)
class ProofPermissionDecision:
    proof_id: str
    decision: str
    reason: str
    relevance_score: float
    relevance_signals: tuple[ProofRelevanceSignal, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "decision": self.decision,
            "reason": self.reason,
            "relevance_score": self.relevance_score,
            "relevance_signals": [signal.to_dict() for signal in self.relevance_signals],
        }


@dataclass(frozen=True)
class SenderProofGraphPacket:
    status: str
    ready: bool
    recipient_class: str
    message_type: str
    proof_packet_id: str
    selected_proof_points: tuple[ApprovedSenderProofPoint, ...]
    permission_decisions: tuple[ProofPermissionDecision, ...]
    omitted_claims: tuple[Mapping[str, str], ...]
    blocked_claims: tuple[Mapping[str, str], ...]
    proof_to_target_relevance_score: Mapping[str, float]
    source_lineage: Mapping[str, tuple[str, ...]]
    graph_links: Mapping[str, tuple[Mapping[str, str], ...]]
    claim_permission_map_hash: str
    unsupported_claim_policy: str
    corpus_hash: str
    source_snapshot_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    # W2: apps_rg shared-SSOT provenance per proof_id (lineage + approval).
    apps_rg_provenance: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    @property
    def proof_ids(self) -> tuple[str, ...]:
        return tuple(point.proof_id for point in self.selected_proof_points)

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.c03_sender_proof_graph_packet.v1",
            "status": self.status,
            "ready": self.ready,
            "recipient_class": self.recipient_class,
            "message_type": self.message_type,
            "proof_packet_id": self.proof_packet_id,
            "approved_sender_proof_points": [
                point.to_packet() for point in self.selected_proof_points
            ],
            "proof_ids": list(self.proof_ids),
            "permission_decisions": [
                decision.to_dict() for decision in self.permission_decisions
            ],
            "omitted_claims": [dict(item) for item in self.omitted_claims],
            "blocked_claims": [dict(item) for item in self.blocked_claims],
            "proof_to_target_relevance_score": dict(self.proof_to_target_relevance_score),
            "source_lineage": {
                proof_id: list(source_ids)
                for proof_id, source_ids in self.source_lineage.items()
            },
            "graph_links": {
                proof_id: [dict(link) for link in links]
                for proof_id, links in self.graph_links.items()
            },
            "claim_permission_map_hash": self.claim_permission_map_hash,
            "unsupported_claim_policy": self.unsupported_claim_policy,
            "corpus_hash": self.corpus_hash,
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "reason_codes": list(self.reason_codes),
            "apps_rg_provenance": {
                proof_id: dict(prov)
                for proof_id, prov in self.apps_rg_provenance.items()
            },
        }

    def to_pa_envelope(self) -> dict[str, Any]:
        payload = self.to_packet()
        envelope = {
            "schema_version": "apps_lic.pa_sender_proof_envelope.v1",
            "proof_packet_id": self.proof_packet_id,
            "allowed_claim_ids": list(self.proof_ids),
            "approved_sender_proof_points": payload["approved_sender_proof_points"],
            "source_lineage": payload["source_lineage"],
            "graph_links": payload["graph_links"],
            "apps_rg_provenance": payload["apps_rg_provenance"],
            "claim_permission_map_hash": self.claim_permission_map_hash,
            "omitted_claims": payload["omitted_claims"],
            "blocked_claims": payload["blocked_claims"],
            "proof_to_target_relevance_score": dict(self.proof_to_target_relevance_score),
            "instruction_data_boundary_receipt": PA_INSTRUCTION_DATA_BOUNDARY_RECEIPT,
            "pa_component_hash": _sha256_canonical(
                {
                    "proof_packet_id": self.proof_packet_id,
                    "allowed_claim_ids": list(self.proof_ids),
                    "source_lineage": payload["source_lineage"],
                    "graph_links": payload["graph_links"],
                }
            ),
        }
        return envelope


@dataclass(frozen=True)
class SenderProofClaimValidationResult:
    status: str
    allowed_claim_ids: tuple[str, ...]
    blocked_claims: tuple[Mapping[str, str], ...]
    proof_packet_id: str
    claim_permission_map_hash: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.sender_proof_claim_validation.v1",
            "status": self.status,
            "allowed_claim_ids": list(self.allowed_claim_ids),
            "blocked_claims": [dict(item) for item in self.blocked_claims],
            "proof_packet_id": self.proof_packet_id,
            "claim_permission_map_hash": self.claim_permission_map_hash,
        }


def _sha256_canonical(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.sub(r"[^a-z0-9]+", " ", value.lower()).split()
        if token
    }


def _tag_matches(tag: str, context_text: str, context_tokens: set[str]) -> bool:
    tag_text = tag.lower().replace("_", "-")
    normalized_tag = re.sub(r"[^a-z0-9]+", " ", tag_text).strip()
    if tag_text in context_text.lower() or normalized_tag in context_text.lower():
        return True
    tag_tokens = _tokens(normalized_tag)
    return bool(tag_tokens) and tag_tokens <= context_tokens


def _document_context(documents: Iterable[OpportunityFactDocument]) -> tuple[str, tuple[str, ...]]:
    parts: list[str] = []
    snapshot_ids: list[str] = []
    for document in documents:
        snapshot_ids.append(document.source_snapshot_id)
        parts.append(document.fact_text)
        metadata = dict(document.metadata)
        for value in metadata.values():
            if isinstance(value, (str, int, float, bool)):
                parts.append(str(value))
    return " ".join(_clean(part) for part in parts if _clean(part)), tuple(snapshot_ids)


def _jd_role_families(documents: Iterable[OpportunityFactDocument]) -> tuple[str, ...]:
    families: list[str] = []
    for document in documents:
        if document.namespace != NAMESPACE_JD:
            continue
        family = _clean(dict(document.metadata).get("role_family")).lower()
        if family:
            families.append(family)
    return tuple(dict.fromkeys(families))


def _score_proof(
    point: ApprovedSenderProofPoint,
    *,
    recipient_class: str,
    message_type: str,
    context_text: str,
    context_tokens: set[str],
    jd_role_families: Iterable[str],
) -> tuple[float, tuple[ProofRelevanceSignal, ...]]:
    signals: list[ProofRelevanceSignal] = []
    score = _STRENGTH_SCORE.get(point.claim_strength, 0.0)
    signals.append(
        ProofRelevanceSignal(
            reason_code=f"claim_strength:{point.claim_strength}",
            source="standing_sender_corpus",
            weight=score,
            matched_value=point.claim_strength,
        )
    )

    for tag in point.skill_tags:
        if _tag_matches(tag, context_text, context_tokens):
            score += 0.45
            signals.append(
                ProofRelevanceSignal(
                    reason_code="skill_tag_match",
                    source="sender_proof_point.skill_tags",
                    weight=0.45,
                    matched_value=tag,
                )
            )

    for link in point.graph_links:
        target = _clean(dict(link).get("target"))
        if target and _tag_matches(target, context_text, context_tokens):
            score += 0.35
            signals.append(
                ProofRelevanceSignal(
                    reason_code="graph_link_match",
                    source="sender_proof_point.graph_links",
                    weight=0.35,
                    matched_value=target,
                )
            )

    for role_family in jd_role_families:
        preferred_tags = _ROLE_FAMILY_TAGS.get(role_family, ())
        for tag in point.skill_tags:
            if tag in preferred_tags:
                score += 0.35
                signals.append(
                    ProofRelevanceSignal(
                        reason_code=f"jd_role_family:{role_family}",
                        source=NAMESPACE_JD,
                        weight=0.35,
                        matched_value=tag,
                    )
                )

    if recipient_class in _EXEC_CLASSES:
        for tag in point.skill_tags:
            if tag in {"productization", "leadership", "platform-economics"}:
                score += 0.55
                signals.append(
                    ProofRelevanceSignal(
                        reason_code="executive_value_creation_fit",
                        source="recipient_class",
                        weight=0.55,
                        matched_value=tag,
                    )
                )
            if tag in {"quantitative-governance", "risk", "governance"}:
                score += 0.30
                signals.append(
                    ProofRelevanceSignal(
                        reason_code="executive_risk_governance_fit",
                        source="recipient_class",
                        weight=0.30,
                        matched_value=tag,
                    )
                )

    if recipient_class in {CLASS_HIRING_MANAGER, CLASS_CTO, CLASS_VP_ENG}:
        for tag in point.skill_tags:
            if tag in {"reliability", "cloud-native", "ai-cicd", "data-platform"}:
                score += 0.40
                signals.append(
                    ProofRelevanceSignal(
                        reason_code="technical_hiring_owner_fit",
                        source="recipient_class",
                        weight=0.40,
                        matched_value=tag,
                    )
                )

    if recipient_class in {CLASS_RECRUITER, CLASS_SENIOR_TA} and message_type == "role_specific":
        for tag in point.skill_tags:
            if tag in {"agentic-platform", "governance", "regulated", "reliability"}:
                score += 0.25
                signals.append(
                    ProofRelevanceSignal(
                        reason_code="role_specific_talent_screen_fit",
                        source="recipient_class+message_type",
                        weight=0.25,
                        matched_value=tag,
                    )
                )

    # W3: graph-derived recipient-fit. The apps_rg role_family_weights for the
    # proof point's linked skills weight role/req-fit proof for technical
    # evaluators and business-outcome proof for executives, replacing reliance on
    # hand-authored literal tag sets above.
    fit = recipient_fit_weight(
        apps_rg_skill_ids=getattr(point, "apps_rg_skill_ids", ()),
        recipient_class=recipient_class,
    )
    if fit["weight"] > 0.0:
        graph_weight = round(0.6 * float(fit["weight"]), 4)
        score += graph_weight
        signals.append(
            ProofRelevanceSignal(
                reason_code=f"graph_recipient_fit:{fit['matched_family']}",
                source="apps_rg.role_family_weights",
                weight=graph_weight,
                matched_value=fit["matched_skill"],
            )
        )

    return round(score, 4), tuple(signals)


def _empty_packet(
    *,
    status: str,
    recipient_class: str,
    message_type: str,
    reason_codes: Iterable[str],
    blocked_claims: Iterable[Mapping[str, str]] = (),
) -> SenderProofGraphPacket:
    return SenderProofGraphPacket(
        status=status,
        ready=False,
        recipient_class=recipient_class,
        message_type=message_type,
        proof_packet_id="",
        selected_proof_points=(),
        permission_decisions=(),
        omitted_claims=(),
        blocked_claims=tuple(blocked_claims),
        proof_to_target_relevance_score={},
        source_lineage={},
        graph_links={},
        claim_permission_map_hash="",
        unsupported_claim_policy="block",
        corpus_hash="",
        source_snapshot_ids=(),
        reason_codes=tuple(dict.fromkeys(reason_codes)),
    )


def build_sender_proof_graph_packet(
    *,
    recipient_derivation: RecipientClassDerivation,
    message_gate_result: MessageRequirementGateResult,
    opportunity_documents: Iterable[OpportunityFactDocument] = (),
    campaign_objective: str = "",
    company_context: str = "",
    desired_next_step: str = "",
    max_points: int = 3,
    path: str | None = None,
) -> SenderProofGraphPacket:
    """Build the C0.3 proof graph packet for PA/L2."""
    recipient_class = recipient_derivation.derived_recipient_class
    message_type = message_gate_result.message_type
    if recipient_derivation.status != RECIPIENT_STATUS_DERIVED:
        return _empty_packet(
            status=STATUS_PROOF_GRAPH_BLOCKED,
            recipient_class=recipient_class,
            message_type=message_type,
            reason_codes=(REASON_RECIPIENT_CLASS_NOT_DERIVED,),
            blocked_claims=(
                {
                    "proof_id": "",
                    "reason": REASON_RECIPIENT_CLASS_NOT_DERIVED,
                },
            ),
        )
    if message_gate_result.status != STATUS_REQUIREMENTS_PASS:
        return _empty_packet(
            status=STATUS_PROOF_GRAPH_BLOCKED,
            recipient_class=recipient_class,
            message_type=message_type,
            reason_codes=(REASON_MESSAGE_REQUIREMENTS_NOT_PASSED,),
            blocked_claims=(
                {
                    "proof_id": "",
                    "reason": REASON_MESSAGE_REQUIREMENTS_NOT_PASSED,
                },
            ),
        )

    readiness = check_standing_sender_corpus_readiness(path)
    if not readiness.ready:
        return _empty_packet(
            status=STATUS_PROOF_GRAPH_READINESS_ERROR,
            recipient_class=recipient_class,
            message_type=message_type,
            reason_codes=(REASON_SENDER_CORPUS_READINESS_ERROR, readiness.status),
            blocked_claims=(
                {
                    "proof_id": "",
                    "reason": REASON_SENDER_CORPUS_READINESS_ERROR,
                },
            ),
        )

    corpus = load_standing_sender_corpus(path)
    documents = tuple(opportunity_documents)
    document_text, source_snapshot_ids = _document_context(documents)
    context_text = " ".join(
        part
        for part in (
            campaign_objective,
            company_context,
            desired_next_step,
            document_text,
        )
        if _clean(part)
    )
    context_tokens = _tokens(context_text)
    role_families = _jd_role_families(documents)
    unsupported_policy = _clean(
        corpus.claim_permission_map.get("unsupported_claim_policy")
        or corpus.claim_permission_map.get("default_policy")
        or "block"
    )

    scored: list[tuple[ApprovedSenderProofPoint, float, tuple[ProofRelevanceSignal, ...]]] = []
    decisions: list[ProofPermissionDecision] = []
    omitted: list[Mapping[str, str]] = []
    blocked: list[Mapping[str, str]] = []

    for point in corpus.proof_points:
        score, signals = _score_proof(
            point,
            recipient_class=recipient_class,
            message_type=message_type,
            context_text=context_text,
            context_tokens=context_tokens,
            jd_role_families=role_families,
        )
        if point.permission != PERMISSION_ALLOW:
            blocked.append(
                {"proof_id": point.proof_id, "reason": REASON_CLAIM_PERMISSION_NOT_ALLOW}
            )
            decisions.append(
                ProofPermissionDecision(
                    proof_id=point.proof_id,
                    decision=PERMISSION_BLOCK,
                    reason=REASON_CLAIM_PERMISSION_NOT_ALLOW,
                    relevance_score=score,
                    relevance_signals=signals,
                )
            )
            continue
        if not point.is_scope_allowed(
            recipient_class=recipient_class,
            message_type=message_type,
        ):
            omitted.append({"proof_id": point.proof_id, "reason": REASON_NOT_ALLOWED_FOR_SCOPE})
            decisions.append(
                ProofPermissionDecision(
                    proof_id=point.proof_id,
                    decision=PERMISSION_OMIT,
                    reason=REASON_NOT_ALLOWED_FOR_SCOPE,
                    relevance_score=score,
                    relevance_signals=signals,
                )
            )
            continue
        scored.append((point, score, signals))

    ranked = sorted(scored, key=lambda item: (-item[1], item[0].proof_id))
    chosen = tuple(item[0] for item in ranked[: max(0, max_points)])
    chosen_ids = {point.proof_id for point in chosen}

    for point, score, signals in ranked:
        if point.proof_id in chosen_ids:
            decisions.append(
                ProofPermissionDecision(
                    proof_id=point.proof_id,
                    decision=PERMISSION_ALLOW,
                    reason="selected_for_pa",
                    relevance_score=score,
                    relevance_signals=signals,
                )
            )
        else:
            omitted.append({"proof_id": point.proof_id, "reason": REASON_LOWER_RELEVANCE})
            decisions.append(
                ProofPermissionDecision(
                    proof_id=point.proof_id,
                    decision=PERMISSION_OMIT,
                    reason=REASON_LOWER_RELEVANCE,
                    relevance_score=score,
                    relevance_signals=signals,
                )
            )

    relevance = {
        decision.proof_id: decision.relevance_score
        for decision in decisions
        if decision.proof_id
    }
    source_lineage = {
        point.proof_id: tuple(point.source_ids)
        for point in chosen
    }
    graph_links = {
        point.proof_id: tuple(point.graph_links)
        for point in chosen
    }
    apps_rg_provenance = {
        point.proof_id: proof_provenance_for(
            source_ids=point.source_ids,
            skill_tags=point.skill_tags,
            apps_rg_skill_ids=getattr(point, "apps_rg_skill_ids", ()),
        )
        for point in chosen
    }
    packet_seed = {
        "recipient_class": recipient_class,
        "message_type": message_type,
        "proof_ids": [point.proof_id for point in chosen],
        "relevance": relevance,
        "corpus_hash": corpus.corpus_hash,
        "source_snapshot_ids": source_snapshot_ids,
    }
    ready = bool(chosen)
    return SenderProofGraphPacket(
        status=STATUS_PROOF_GRAPH_READY if ready else STATUS_PROOF_GRAPH_NO_MATCH,
        ready=ready,
        recipient_class=recipient_class,
        message_type=message_type,
        proof_packet_id=_sha256_canonical(packet_seed) if ready else "",
        selected_proof_points=chosen,
        permission_decisions=tuple(decisions),
        omitted_claims=tuple(omitted),
        blocked_claims=tuple(blocked),
        proof_to_target_relevance_score=relevance,
        source_lineage=source_lineage,
        graph_links=graph_links,
        claim_permission_map_hash=corpus.claim_permission_map_hash,
        unsupported_claim_policy=unsupported_policy,
        corpus_hash=corpus.corpus_hash,
        source_snapshot_ids=source_snapshot_ids,
        reason_codes=(
            "standing_corpus_ready",
            "message_requirements_passed",
            "recipient_class_derived",
        ),
        apps_rg_provenance=apps_rg_provenance,
    )


def build_sender_proof_graph_packet_from_store(
    *,
    store: OpportunityFactStore,
    recipient_derivation: RecipientClassDerivation,
    message_gate_result: MessageRequirementGateResult,
    campaign_objective: str = "",
    company_context: str = "",
    desired_next_step: str = "",
    max_points: int = 3,
    path: str | None = None,
) -> SenderProofGraphPacket:
    """Read opportunity context from W2 fact store and build C0.3 packet."""
    documents: list[OpportunityFactDocument] = []
    for namespace in (
        NAMESPACE_COMPANY,
        NAMESPACE_JD,
        NAMESPACE_COMPANY_TRIGGER,
        NAMESPACE_ROLE_OWNERSHIP,
    ):
        documents.extend(store.query_namespace(namespace))
    return build_sender_proof_graph_packet(
        recipient_derivation=recipient_derivation,
        message_gate_result=message_gate_result,
        opportunity_documents=documents,
        campaign_objective=campaign_objective,
        company_context=company_context,
        desired_next_step=desired_next_step,
        max_points=max_points,
        path=path,
    )


def build_pa_sender_proof_envelope(packet: SenderProofGraphPacket) -> dict[str, Any]:
    """Return the PA data-only proof envelope."""
    return packet.to_pa_envelope()


def validate_l2_sender_claims_against_packet(
    claim_ids: Iterable[str],
    *,
    packet: SenderProofGraphPacket,
) -> SenderProofClaimValidationResult:
    """Detect any L2 sender claim not authorized by the C0.3 packet."""
    allowed_set = set(packet.proof_ids)
    allowed: list[str] = []
    blocked: list[Mapping[str, str]] = []
    for claim_id in dict.fromkeys(_clean(item) for item in claim_ids if _clean(item)):
        if claim_id in allowed_set:
            allowed.append(claim_id)
        else:
            blocked.append({"proof_id": claim_id, "reason": REASON_CLAIM_NOT_IN_PACKET})
    return SenderProofClaimValidationResult(
        status=STATUS_CLAIMS_BLOCKED if blocked else STATUS_CLAIMS_PASS,
        allowed_claim_ids=tuple(allowed),
        blocked_claims=tuple(blocked),
        proof_packet_id=packet.proof_packet_id,
        claim_permission_map_hash=packet.claim_permission_map_hash,
    )


__all__ = [
    "PA_INSTRUCTION_DATA_BOUNDARY_RECEIPT",
    "PERMISSION_ALLOW",
    "PERMISSION_BLOCK",
    "PERMISSION_ESCALATE",
    "PERMISSION_OMIT",
    "REASON_CLAIM_NOT_IN_PACKET",
    "REASON_CLAIM_PERMISSION_NOT_ALLOW",
    "REASON_LOWER_RELEVANCE",
    "REASON_MESSAGE_REQUIREMENTS_NOT_PASSED",
    "REASON_NOT_ALLOWED_FOR_SCOPE",
    "REASON_RECIPIENT_CLASS_NOT_DERIVED",
    "REASON_SENDER_CORPUS_READINESS_ERROR",
    "REASON_UNSUPPORTED_SENDER_CLAIM",
    "STATUS_CLAIMS_BLOCKED",
    "STATUS_CLAIMS_PASS",
    "STATUS_PROOF_GRAPH_BLOCKED",
    "STATUS_PROOF_GRAPH_NO_MATCH",
    "STATUS_PROOF_GRAPH_READINESS_ERROR",
    "STATUS_PROOF_GRAPH_READY",
    "ProofPermissionDecision",
    "ProofRelevanceSignal",
    "SenderProofClaimValidationResult",
    "SenderProofGraphPacket",
    "build_pa_sender_proof_envelope",
    "build_sender_proof_graph_packet",
    "build_sender_proof_graph_packet_from_store",
    "validate_l2_sender_claims_against_packet",
]
