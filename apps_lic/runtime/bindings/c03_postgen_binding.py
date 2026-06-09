"""Post-generation C0.3 sender-claim enforcement for apps_lic."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_lic.engines.sender_proof_graph import (
    REASON_CLAIM_NOT_IN_PACKET,
    STATUS_CLAIMS_BLOCKED,
    STATUS_CLAIMS_PASS,
    SenderProofClaimValidationResult,
    validate_l2_sender_claims_against_packet,
)
from apps_lic.runtime.bindings.c03_binding import C03SenderProofResult


APPS_LIC_C03_POSTGEN_CERT_REF = "c03-postgen-apps-lic-claim-enforcement-w3b-4c9d2a"
C03_POSTGEN_STATUS_PASS = "C03_POSTGEN_CLAIMS_PASS"
C03_POSTGEN_STATUS_BLOCKED = "C03_POSTGEN_CLAIMS_BLOCKED"
REASON_PROOF_LIKE_TEXT_WITHOUT_CLAIM_ID = "proof_like_text_without_claim_id"
REASON_L2_DRAFT_UNPARSEABLE = "l2_draft_unparseable"

_PROOF_LIKE_TERMS: tuple[str, ...] = (
    "built",
    "led",
    "delivered",
    "improved",
    "launched",
    "architecture",
    "platform",
    "governance",
    "metrics",
)
_PRIOR_COMPANY_PATTERN = re.compile(
    r"\b(?:at|for|with)\s+"
    r"(?:google|meta|amazon|microsoft|openai|ibm|jpmorgan|capital one|aig)\b",
    re.I,
)


@dataclass(frozen=True)
class C03PostgenClaimValidationResult:
    request_id: str
    run_id: str
    app_id: str
    trace_id: str
    status: str
    selected_candidate_id: str
    claims_used: tuple[str, ...]
    packet_allowed_claim_ids: tuple[str, ...]
    blocked_claims: tuple[Mapping[str, Any], ...]
    proof_like_claims_detected: tuple[Mapping[str, str], ...]
    proof_packet_id: str
    claim_permission_map_hash: str
    source_snapshot_ids: tuple[str, ...]
    l2_execution_status: str
    l2_compilation_hash: str
    l2_generated_content_digest: str
    claim_validation: SenderProofClaimValidationResult
    l5_certification_ref: str = APPS_LIC_C03_POSTGEN_CERT_REF

    @property
    def ready(self) -> bool:
        return self.status == C03_POSTGEN_STATUS_PASS

    @property
    def blocking_reasons(self) -> tuple[str, ...]:
        reasons = [
            str(item.get("reason") or "")
            for item in self.blocked_claims
            if str(item.get("reason") or "")
        ]
        return tuple(dict.fromkeys(reasons))

    def to_receipt_payload(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.c03_postgen_claim_validation.v1",
            "status": self.status,
            "ready": self.ready,
            "claim_validation": self.claim_validation.to_packet(),
            "proof_packet_id": self.proof_packet_id,
            "selected_candidate_id": self.selected_candidate_id,
            "claims_used": list(self.claims_used),
            "packet_allowed_claim_ids": list(self.packet_allowed_claim_ids),
            "blocked_claims": [dict(item) for item in self.blocked_claims],
            "blocking_reasons": list(self.blocking_reasons),
            "proof_like_claims_detected": [
                dict(item) for item in self.proof_like_claims_detected
            ],
            "claim_permission_map_hash": self.claim_permission_map_hash,
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "l2_execution_status": self.l2_execution_status,
            "l2_compilation_hash": self.l2_compilation_hash,
            "l2_generated_content_digest": self.l2_generated_content_digest,
            "x2_report": {
                "proof_packet_id": self.proof_packet_id,
                "selected_candidate_id": self.selected_candidate_id,
                "blocked_claim_reasons": list(self.blocking_reasons),
                "source_snapshot_lineage": list(self.source_snapshot_ids),
            },
            "l5_certification_ref": self.l5_certification_ref,
        }


def _sha256_digest(value: Any) -> str:
    import hashlib

    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _parse_l2_draft(l2: SealedL2Artifact) -> tuple[dict[str, Any], str]:
    content = l2.generated_content
    if isinstance(content, Mapping):
        draft = dict(content)
        return _unwrap_draft(draft), ""
    text = str(content or "")
    if not text.strip():
        return {}, ""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {"message_text": text}, REASON_L2_DRAFT_UNPARSEABLE
    if not isinstance(parsed, Mapping):
        return {}, REASON_L2_DRAFT_UNPARSEABLE
    return _unwrap_draft(dict(parsed)), ""


def _unwrap_draft(value: dict[str, Any]) -> dict[str, Any]:
    draft = value.get("draft_message")
    if isinstance(draft, Mapping):
        return dict(draft)
    return value


def _claim_ids(draft: Mapping[str, Any]) -> tuple[str, ...]:
    raw = draft.get("claims_used")
    if not isinstance(raw, (list, tuple)):
        return ()
    return tuple(dict.fromkeys(str(item).strip() for item in raw if str(item).strip()))


def _message_text(draft: Mapping[str, Any]) -> str:
    return str(draft.get("message_text") or draft.get("body") or "").strip()


def _selected_candidate_id(draft: Mapping[str, Any]) -> str:
    for key in ("selected_candidate_id", "candidate_id", "id"):
        value = str(draft.get(key) or "").strip()
        if value:
            return value
    return "l2_inline_draft"


def _proof_like_claims(text: str) -> tuple[Mapping[str, str], ...]:
    lowered = text.lower()
    matches: list[Mapping[str, str]] = []
    for term in _PROOF_LIKE_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", lowered):
            matches.append(
                {
                    "pattern_id": f"sender_claim_term:{term}",
                    "matched_text": term,
                    "reason": REASON_PROOF_LIKE_TEXT_WITHOUT_CLAIM_ID,
                }
            )
    prior_company = _PRIOR_COMPANY_PATTERN.search(text)
    if prior_company:
        matches.append(
            {
                "pattern_id": "sender_claim_prior_company",
                "matched_text": prior_company.group(0),
                "reason": REASON_PROOF_LIKE_TEXT_WITHOUT_CLAIM_ID,
            }
        )
    return tuple(matches)


def validate_l2_c03_postgen_claims(
    *,
    l2_artifact: SealedL2Artifact,
    c03: C03SenderProofResult,
) -> C03PostgenClaimValidationResult:
    """Validate L2 sender claims against the approved C0.3 proof packet."""
    draft, parse_reason = _parse_l2_draft(l2_artifact)
    claims_used = _claim_ids(draft)
    claim_validation = validate_l2_sender_claims_against_packet(
        claims_used,
        packet=c03.sender_proof_packet,
    )
    proof_like = _proof_like_claims(_message_text(draft))
    blocked: list[Mapping[str, Any]] = [dict(item) for item in claim_validation.blocked_claims]
    if parse_reason:
        blocked.append({"proof_id": "", "reason": parse_reason})
    if not claims_used and proof_like:
        blocked.append(
            {
                "proof_id": "",
                "reason": REASON_PROOF_LIKE_TEXT_WITHOUT_CLAIM_ID,
                "matched_patterns": [dict(item) for item in proof_like],
            }
        )
    status = C03_POSTGEN_STATUS_BLOCKED if blocked else C03_POSTGEN_STATUS_PASS
    if claim_validation.status == STATUS_CLAIMS_BLOCKED and status != C03_POSTGEN_STATUS_BLOCKED:
        blocked.append({"proof_id": "", "reason": REASON_CLAIM_NOT_IN_PACKET})
        status = C03_POSTGEN_STATUS_BLOCKED

    return C03PostgenClaimValidationResult(
        request_id=l2_artifact.request_id,
        run_id=l2_artifact.run_id,
        app_id=l2_artifact.app_id,
        trace_id=l2_artifact.trace_id,
        status=status,
        selected_candidate_id=_selected_candidate_id(draft),
        claims_used=claims_used,
        packet_allowed_claim_ids=tuple(c03.sender_proof_packet.proof_ids),
        blocked_claims=tuple(blocked),
        proof_like_claims_detected=proof_like,
        proof_packet_id=c03.proof_packet_id,
        claim_permission_map_hash=c03.sender_proof_packet.claim_permission_map_hash,
        source_snapshot_ids=tuple(c03.source_snapshot_ids),
        l2_execution_status=str(l2_artifact.execution_status or ""),
        l2_compilation_hash=str(l2_artifact.compilation_hash or ""),
        l2_generated_content_digest=_sha256_digest(l2_artifact.generated_content or ""),
        claim_validation=claim_validation,
    )


def c03_postgen_claims_pass(result: C03PostgenClaimValidationResult) -> bool:
    return result.status == C03_POSTGEN_STATUS_PASS


__all__ = [
    "APPS_LIC_C03_POSTGEN_CERT_REF",
    "C03_POSTGEN_STATUS_BLOCKED",
    "C03_POSTGEN_STATUS_PASS",
    "C03PostgenClaimValidationResult",
    "REASON_L2_DRAFT_UNPARSEABLE",
    "REASON_PROOF_LIKE_TEXT_WITHOUT_CLAIM_ID",
    "c03_postgen_claims_pass",
    "validate_l2_c03_postgen_claims",
]
