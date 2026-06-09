"""W4 candidate-batch materialization for apps_lic canonical outreach."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_lic.engines.whole_message_generation import (
    GENERATOR_MODEL_ID,
    GENERATOR_PROVIDER_ID,
    NO_DURABLE_WRITE_RECEIPT,
    STATUS_CANDIDATES_BLOCKED,
    STATUS_CANDIDATES_READY,
    WholeMessageCandidate,
    WholeMessageCandidateBatch,
)
from apps_lic.runtime.bindings.c03_binding import C03SenderProofResult


APPS_LIC_W4_CERT_REF = "w4-apps-lic-candidate-batch-wireup-4c9d2a"
W4_STATUS_READY = "W4_CANDIDATE_BATCH_READY"
W4_STATUS_BLOCKED = "W4_CANDIDATE_BATCH_BLOCKED"
REASON_CANDIDATE_BATCH_MISSING = "candidate_batch_missing_for_multi_candidate_path"
REASON_CANDIDATE_COUNT_METADATA_ONLY = "candidate_count_metadata_without_candidate_objects"
REASON_CANDIDATE_COUNT_MISMATCH = "candidate_batch_count_mismatch"
REASON_SELECTED_CANDIDATE_ID_MISSING = "selected_candidate_id_missing"
REASON_SELECTED_CANDIDATE_ID_NOT_IN_BATCH = "selected_candidate_id_not_in_batch"
REASON_REJECTED_CANDIDATES_MISSING = "rejected_candidates_missing_for_multi_candidate_path"
REASON_SELECTED_CANDIDATE_NOT_REFLECTED = "selected_candidate_not_reflected_in_l2_draft"
REASON_CANDIDATE_TEXT_MISSING = "candidate_text_missing"
SELECTION_STRATEGY_MODEL_SELECTED = "model_selected_candidate"
SELECTION_STRATEGY_LENGTH_POLICY_OVERRIDE = "length_policy_selected_compliant_candidate"
_SIGNATURE_PATTERN = re.compile(
    r"(?:\r?\n|\A)\s*(?:best|thanks|regards|warmly|cheers)?[,]?\s*Amit(?: Ayer)?\.?\s*\Z",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class W4CandidateBatchResult:
    request_id: str
    run_id: str
    app_id: str
    trace_id: str
    status: str
    sc_level: str
    expected_candidate_count: int
    candidate_count_materialized: int
    selected_candidate_id: str
    selection_strategy: str
    rejected_candidate_ids: tuple[str, ...]
    batch: WholeMessageCandidateBatch
    blocking_reasons: tuple[str, ...]
    model_call_refs: tuple[str, ...]
    provider_receipts: tuple[str, ...]
    l2_generated_content_digest: str
    proof_packet_id: str
    l5_certification_ref: str = APPS_LIC_W4_CERT_REF

    @property
    def ready(self) -> bool:
        return self.status == W4_STATUS_READY

    def to_receipt_payload(self) -> dict[str, Any]:
        selected = _candidate_by_id(self.batch, self.selected_candidate_id)
        return {
            "schema_version": "apps_lic.w4_candidate_batch_result.v1",
            "status": self.status,
            "ready": self.ready,
            "sc_level": self.sc_level,
            "expected_candidate_count": self.expected_candidate_count,
            "candidate_count_materialized": self.candidate_count_materialized,
            "selected_candidate_id": self.selected_candidate_id,
            "selection_strategy": self.selection_strategy,
            "rejected_candidate_ids": list(self.rejected_candidate_ids),
            "whole_message_candidate_batch": self.batch.to_packet(),
            "selected_candidate": selected.to_packet() if selected is not None else {},
            "blocking_reasons": list(self.blocking_reasons),
            "model_call_refs": list(self.model_call_refs),
            "provider_receipts": list(self.provider_receipts),
            "l2_generated_content_digest": self.l2_generated_content_digest,
            "proof_packet_id": self.proof_packet_id,
            "l5_certification_ref": self.l5_certification_ref,
        }


def _sha256_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _parse_l2_draft(l2: SealedL2Artifact) -> dict[str, Any]:
    content = l2.generated_content
    if isinstance(content, Mapping):
        parsed = dict(content)
    else:
        try:
            parsed = json.loads(str(content or "{}"))
        except json.JSONDecodeError:
            parsed = {"message_text": str(content or "")}
    if isinstance(parsed.get("draft_message"), Mapping):
        return dict(parsed["draft_message"])
    return parsed if isinstance(parsed, dict) else {}


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _message_text(value: Any) -> str:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _canonical_message_text(value: Any) -> str:
    text = _message_text(value)
    if not text:
        return ""
    text = re.sub(r"\s+Amit\s*[;:].*\Z", "", text, flags=re.IGNORECASE).rstrip()
    text = re.sub(
        r"(?:\s|\n)+(?:best|thanks|regards|warmly|cheers)[,.]?\s*\Z",
        "",
        text,
        flags=re.IGNORECASE,
    ).rstrip()
    if _SIGNATURE_PATTERN.search(text):
        return text
    text = re.sub(r"\s+Amit\.?\s*\Z", "", text, flags=re.IGNORECASE).rstrip()
    return f"{text}\n\nAmit"


def _subject_line(value: Any) -> str:
    return _clean(value)[:200]


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _sentence_count(text: str) -> int:
    text = _SIGNATURE_PATTERN.sub("", str(text or "")).strip()
    return len([part for part in re.split(r"[.!?]+", text) if part.strip()])


def _candidate_entries(draft: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    raw = draft.get("candidates")
    if not isinstance(raw, list):
        raw = (draft.get("candidate_batch") or {}).get("candidates") if isinstance(draft.get("candidate_batch"), Mapping) else []
    if not isinstance(raw, list):
        return ()
    return tuple(item for item in raw if isinstance(item, Mapping))


def _claim_ids(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(dict.fromkeys(_clean(item) for item in value if _clean(item)))


def _candidate_id(seed: Mapping[str, Any], index: int, text: str) -> str:
    value = _clean(seed.get("candidate_id") or seed.get("id"))
    if value:
        return value
    return _sha256_digest({"index": index, "draft_text": text})[:32]


def _model_call_ref(
    *,
    entry: Mapping[str, Any],
    l2: SealedL2Artifact,
    index: int,
) -> str:
    explicit = _clean(entry.get("model_call_ref"))
    if explicit:
        return explicit
    refs = tuple(getattr(l2, "model_call_refs", ()) or ())
    if refs:
        return str(refs[min(index, len(refs) - 1)])
    return f"mref:{l2.run_id[:8]}:candidate{index}"


def _provider_receipt(
    *,
    entry: Mapping[str, Any],
    l2: SealedL2Artifact,
    index: int,
) -> str:
    explicit = _clean(entry.get("provider_receipt"))
    if explicit:
        return explicit
    receipts = tuple(getattr(l2, "provider_receipts", ()) or ())
    if receipts:
        return str(receipts[min(index, len(receipts) - 1)])
    return f"prov:apps_lic:candidate{index}:{l2.run_id[:8]}"


def _candidate_from_entry(
    *,
    entry: Mapping[str, Any],
    l2: SealedL2Artifact,
    index: int,
) -> WholeMessageCandidate:
    text = _canonical_message_text(
        entry.get("draft_text") or entry.get("message_text") or entry.get("body")
    )
    candidate_id = _candidate_id(entry, index, text)
    model_call_ref = _model_call_ref(entry=entry, l2=l2, index=index)
    provider_receipt = _provider_receipt(entry=entry, l2=l2, index=index)
    generation_receipt = _clean(entry.get("generation_receipt")) or f"model_call_ref:{model_call_ref}"
    return WholeMessageCandidate(
        candidate_id=candidate_id,
        subject_line=_subject_line(entry.get("subject_line") or entry.get("subject")),
        draft_text=text,
        attempt_seed=_clean(entry.get("attempt_seed")) or _sha256_digest(
            {"candidate_id": candidate_id, "index": index}
        ),
        model_id=_clean(entry.get("model_id") or entry.get("model")) or GENERATOR_MODEL_ID,
        provider_id=_clean(entry.get("provider_id") or entry.get("provider")) or GENERATOR_PROVIDER_ID,
        temperature=float(entry.get("temperature") or entry.get("generation_temperature") or 0.0),
        top_p=float(entry.get("top_p") or 0.0),
        word_count=_word_count(text),
        sentence_count=_sentence_count(text),
        char_count=len(text),
        claims_used=_claim_ids(entry.get("claims_used")),
        is_whole_message=bool(entry.get("is_whole_message", True)),
        no_durable_write_receipt=_clean(
            entry.get("no_durable_write_receipt")
        )
        or NO_DURABLE_WRITE_RECEIPT,
        generation_receipt=generation_receipt or f"provider_receipt:{provider_receipt}",
    )


def _candidate_by_id(
    batch: WholeMessageCandidateBatch,
    candidate_id: str,
) -> WholeMessageCandidate | None:
    for candidate in batch.candidates:
        if candidate.candidate_id == candidate_id:
            return candidate
    return None


def _within_c03_length_budget(candidate: WholeMessageCandidate, c03: C03SenderProofResult) -> bool:
    budget = c03.length_budget
    # Word bands are advisory; hard runtime length controls are chars + sentences.
    return (
        candidate.char_count <= budget.hard_cap_chars
        and candidate.sentence_count <= budget.max_sentences
    )


def _select_candidate_id_with_length_policy(
    *,
    requested_candidate_id: str,
    candidates: tuple[WholeMessageCandidate, ...],
    c03: C03SenderProofResult,
) -> tuple[str, str]:
    requested = requested_candidate_id
    if requested:
        selected = next(
            (candidate for candidate in candidates if candidate.candidate_id == requested),
            None,
        )
        if selected is not None and _within_c03_length_budget(selected, c03):
            return requested, SELECTION_STRATEGY_MODEL_SELECTED
    for candidate in candidates:
        if _within_c03_length_budget(candidate, c03):
            return candidate.candidate_id, SELECTION_STRATEGY_LENGTH_POLICY_OVERRIDE
    return requested, SELECTION_STRATEGY_MODEL_SELECTED


def _expected_count(policy: Mapping[str, Any]) -> int:
    try:
        value = int(policy.get("max_candidates") or 1)
    except (TypeError, ValueError):
        value = 1
    return max(1, min(value, 3))


def _sc_level(policy: Mapping[str, Any]) -> str:
    return _clean(policy.get("sc_level")) or "SC-1"


def _prompt_contract_id(l2: SealedL2Artifact) -> str:
    value = _clean(l2.prompt_artifact_digest or l2.compilation_hash)
    if value.startswith("sha256:"):
        return value
    if len(value) == 64:
        return f"sha256:{value}"
    return value


def _fallback_single_entry(draft: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "candidate_id": _clean(draft.get("selected_candidate_id")) or "l2_inline_candidate",
        "subject_line": _subject_line(draft.get("subject_line") or draft.get("subject")),
        "draft_text": _canonical_message_text(draft.get("message_text") or draft.get("body")),
        "claims_used": list(_claim_ids(draft.get("claims_used"))),
        "model": _clean(draft.get("model")),
        "provider": _clean(draft.get("target_provider") or draft.get("provider_profile")),
        "generation_temperature": draft.get("generation_temperature"),
        "top_p": draft.get("top_p"),
        "is_whole_message": True,
    }


def materialize_w4_candidate_batch(
    *,
    l2_artifact: SealedL2Artifact,
    route_reasoning_policy: Mapping[str, Any],
    c03: C03SenderProofResult,
) -> W4CandidateBatchResult:
    """Materialize externally inspectable whole-message candidates from L2."""
    draft = _parse_l2_draft(l2_artifact)
    expected = _expected_count(route_reasoning_policy)
    sc_level = _sc_level(route_reasoning_policy)
    entries = _candidate_entries(draft)
    blocking: list[str] = []

    if not entries and expected == 1:
        entries = (_fallback_single_entry(draft),)
    elif not entries:
        blocking.extend(
            (
                REASON_CANDIDATE_BATCH_MISSING,
                REASON_CANDIDATE_COUNT_METADATA_ONLY,
            )
        )

    candidates = tuple(
        _candidate_from_entry(entry=entry, l2=l2_artifact, index=index)
        for index, entry in enumerate(entries)
    )
    if any(not candidate.draft_text for candidate in candidates):
        blocking.append(REASON_CANDIDATE_TEXT_MISSING)
    if len(candidates) != expected:
        blocking.append(REASON_CANDIDATE_COUNT_MISMATCH)

    selected_candidate_id = _clean(draft.get("selected_candidate_id"))
    if not selected_candidate_id and len(candidates) == 1:
        selected_candidate_id = candidates[0].candidate_id
    elif not selected_candidate_id:
        blocking.append(REASON_SELECTED_CANDIDATE_ID_MISSING)
    model_selected_candidate_id = selected_candidate_id
    selected_candidate_id, selection_strategy = _select_candidate_id_with_length_policy(
        requested_candidate_id=selected_candidate_id,
        candidates=candidates,
        c03=c03,
    )

    selected = _candidate_by_id(
        WholeMessageCandidateBatch(
            status=STATUS_CANDIDATES_READY,
            request_id=l2_artifact.request_id,
            prompt_contract_id=_prompt_contract_id(l2_artifact),
            candidates=candidates,
            blocking_reasons=(),
        ),
        selected_candidate_id,
    )
    if selected_candidate_id and selected is None:
        blocking.append(REASON_SELECTED_CANDIDATE_ID_NOT_IN_BATCH)

    top_level_text = _canonical_message_text(draft.get("message_text") or draft.get("body"))
    top_level_claims = _claim_ids(draft.get("claims_used"))
    selection_overrode_model = (
        bool(model_selected_candidate_id)
        and selected_candidate_id != model_selected_candidate_id
        and selection_strategy == SELECTION_STRATEGY_LENGTH_POLICY_OVERRIDE
    )
    if selected is not None and not selection_overrode_model and (
        selected.draft_text != top_level_text
        or selected.claims_used != top_level_claims
    ):
        blocking.append(REASON_SELECTED_CANDIDATE_NOT_REFLECTED)

    rejected_ids = tuple(
        candidate.candidate_id
        for candidate in candidates
        if candidate.candidate_id != selected_candidate_id
    )
    if expected > 1 and not rejected_ids:
        blocking.append(REASON_REJECTED_CANDIDATES_MISSING)

    blocking = list(dict.fromkeys(reason for reason in blocking if reason))
    batch_status = STATUS_CANDIDATES_BLOCKED if blocking else STATUS_CANDIDATES_READY
    batch = WholeMessageCandidateBatch(
        status=batch_status,
        request_id=l2_artifact.request_id,
        prompt_contract_id=_prompt_contract_id(l2_artifact),
        candidates=candidates,
        blocking_reasons=tuple(blocking),
    )
    status = W4_STATUS_BLOCKED if blocking else W4_STATUS_READY
    model_refs = tuple(dict.fromkeys(str(ref) for ref in getattr(l2_artifact, "model_call_refs", ()) or ()))
    provider_receipts = tuple(
        dict.fromkeys(str(ref) for ref in getattr(l2_artifact, "provider_receipts", ()) or ())
    )
    return W4CandidateBatchResult(
        request_id=l2_artifact.request_id,
        run_id=l2_artifact.run_id,
        app_id=l2_artifact.app_id,
        trace_id=l2_artifact.trace_id,
        status=status,
        sc_level=sc_level,
        expected_candidate_count=expected,
        candidate_count_materialized=len(candidates),
        selected_candidate_id=selected_candidate_id,
        selection_strategy=selection_strategy,
        rejected_candidate_ids=rejected_ids,
        batch=batch,
        blocking_reasons=tuple(blocking),
        model_call_refs=model_refs,
        provider_receipts=provider_receipts,
        l2_generated_content_digest=_sha256_digest(l2_artifact.generated_content or ""),
        proof_packet_id=c03.proof_packet_id,
    )


def w4_candidate_batch_ready(result: W4CandidateBatchResult) -> bool:
    return result.status == W4_STATUS_READY


__all__ = [
    "APPS_LIC_W4_CERT_REF",
    "REASON_CANDIDATE_BATCH_MISSING",
    "REASON_CANDIDATE_COUNT_METADATA_ONLY",
    "REASON_CANDIDATE_COUNT_MISMATCH",
    "REASON_REJECTED_CANDIDATES_MISSING",
    "REASON_SELECTED_CANDIDATE_ID_MISSING",
    "REASON_SELECTED_CANDIDATE_ID_NOT_IN_BATCH",
    "REASON_SELECTED_CANDIDATE_NOT_REFLECTED",
    "SELECTION_STRATEGY_LENGTH_POLICY_OVERRIDE",
    "SELECTION_STRATEGY_MODEL_SELECTED",
    "W4_STATUS_BLOCKED",
    "W4_STATUS_READY",
    "W4CandidateBatchResult",
    "materialize_w4_candidate_batch",
    "w4_candidate_batch_ready",
]
