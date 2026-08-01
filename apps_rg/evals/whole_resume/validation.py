"""Fail-closed bindings for whole-resume and W9 evaluation inputs."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping, Sequence

from apps_rg.evals.resume_graph.reporting import canonical_digest

from .constants import (
    INPUT_SCHEMA_VERSION,
    RUBRIC_ID,
    W9_DIMENSIONS,
)

RUBRIC_PATH = Path(__file__).with_name("rubrics") / "whole_resume.v1.yaml"


def rubric_file_digest() -> str:
    return hashlib.sha256(RUBRIC_PATH.read_bytes()).hexdigest()


def digest_matches(value: Mapping[str, Any], field: str) -> bool:
    digest = value.get(field)
    return isinstance(digest, str) and digest == canonical_digest(
        {key: item for key, item in value.items() if key != field}
    )


def pair_payload_digest(pair: Mapping[str, Any]) -> str:
    return canonical_digest(
        {
            key: value
            for key, value in pair.items()
            if key not in {"pair_payload_digest", "reviews", "adjudication"}
        }
    )


def pair_set_digest(pairs: Sequence[Mapping[str, Any]]) -> str:
    return canonical_digest(
        [
            {
                "pair_id": str(pair.get("pair_id") or ""),
                "pair_payload_digest": str(pair.get("pair_payload_digest") or ""),
            }
            for pair in sorted(pairs, key=lambda row: str(row.get("pair_id") or ""))
        ]
    )


def w9_review_bundle_digest(pairs: Sequence[Mapping[str, Any]]) -> str:
    def review_digests(pair: Mapping[str, Any]) -> list[str]:
        reviews = pair.get("reviews")
        if not isinstance(reviews, list):
            return []
        return sorted(
            str(review.get("record_digest") or "") for review in reviews if isinstance(review, Mapping)
        )

    def adjudication_digest(pair: Mapping[str, Any]) -> str:
        adjudication = pair.get("adjudication")
        return str(adjudication.get("record_digest") or "") if isinstance(adjudication, Mapping) else ""

    return canonical_digest(
        [
            {
                "pair_id": str(pair.get("pair_id") or ""),
                "review_digests": review_digests(pair),
                "adjudication_digest": adjudication_digest(pair),
            }
            for pair in sorted(pairs, key=lambda row: str(row.get("pair_id") or ""))
        ]
    )


def _validate_labels(labels: Any, label: str, errors: list[str]) -> None:
    if not isinstance(labels, Mapping):
        errors.append(f"{label}: labels must be an object")
        return
    if set(labels) != {"resume_a", "resume_b", "preference"}:
        errors.append(f"{label}: label fields differ from the W9 rubric")
    for variant in ("resume_a", "resume_b"):
        dimensions = labels.get(variant)
        if not isinstance(dimensions, Mapping):
            errors.append(f"{label}/{variant}: dimensions must be an object")
            continue
        if set(dimensions) != set(W9_DIMENSIONS):
            errors.append(f"{label}/{variant}: dimensions differ from the W9 rubric")
        for dimension in W9_DIMENSIONS:
            score = dimensions.get(dimension)
            if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
                errors.append(f"{label}/{variant}/{dimension}: score must be 1..5")
    if labels.get("preference") not in {"A", "B", "TIE"}:
        errors.append(f"{label}: preference must be A, B, or TIE")


def _validate_artifact(
    artifact: Any, label: str, target_context: Mapping[str, Any], errors: list[str]
) -> None:
    if not isinstance(artifact, Mapping):
        errors.append(f"{label}: resume artifact must be an object")
        return
    content = artifact.get("content")
    if not isinstance(content, str) or not content.strip():
        errors.append(f"{label}: content must be nonempty")
        content = ""
    sections = artifact.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append(f"{label}: sections must be a nonempty array")
        return
    observed_sections: set[str] = set()
    observed_claims: set[str] = set()
    concept_ids = {
        str(row.get("concept_id") or "")
        for row in target_context.get("jd_concepts") or []
        if isinstance(row, Mapping)
    }
    for section_index, section in enumerate(sections):
        section_label = f"{label}/section[{section_index}]"
        if not isinstance(section, Mapping):
            errors.append(f"{section_label}: section must be an object")
            continue
        section_id = str(section.get("section_id") or "")
        section_text = section.get("text")
        if not section_id or section_id in observed_sections:
            errors.append(f"{section_label}: section_id missing or duplicate")
        observed_sections.add(section_id)
        if not isinstance(section_text, str) or not section_text.strip():
            errors.append(f"{section_label}: text must be nonempty")
            section_text = ""
        elif section_text not in content:
            errors.append(f"{section_label}: section text is not bound to resume content")
        claims = section.get("claims")
        if not isinstance(claims, list):
            errors.append(f"{section_label}: claims must be an array")
            continue
        for claim_index, claim in enumerate(claims):
            claim_label = f"{section_label}/claim[{claim_index}]"
            if not isinstance(claim, Mapping):
                errors.append(f"{claim_label}: claim must be an object")
                continue
            claim_id = str(claim.get("claim_id") or "")
            claim_text = claim.get("text")
            if not claim_id or claim_id in observed_claims:
                errors.append(f"{claim_label}: claim_id missing or duplicate")
            observed_claims.add(claim_id)
            if claim.get("section_id") != section_id:
                errors.append(f"{claim_label}: section_id binding mismatch")
            if not isinstance(claim_text, str) or not claim_text.strip():
                errors.append(f"{claim_label}: text must be nonempty")
            elif claim_text not in section_text:
                errors.append(f"{claim_label}: text is not bound to the section")
            if claim.get("material") is True:
                if claim.get("grounding_status") not in {"PASS", "FAIL", "UNKNOWN"}:
                    errors.append(f"{claim_label}: invalid grounding status")
                refs = claim.get("evidence_refs")
                if not isinstance(refs, list):
                    errors.append(f"{claim_label}: evidence_refs must be an array")
            raw_concepts = claim.get("jd_concept_ids")
            if not isinstance(raw_concepts, list) or any(
                str(value) not in concept_ids for value in raw_concepts
            ):
                errors.append(f"{claim_label}: JD concept binding is invalid")
    employment = artifact.get("employment")
    if not isinstance(employment, list):
        errors.append(f"{label}: employment must be an array")
    else:
        employment_ids = [
            str(row.get("employment_id") or "") for row in employment if isinstance(row, Mapping)
        ]
        if len(employment_ids) != len(employment) or any(not value for value in employment_ids):
            errors.append(f"{label}: every employment row needs an identity")
        if len(employment_ids) != len(set(employment_ids)):
            errors.append(f"{label}: employment identities must be unique")


def _validate_pair(pair: Any, index: int, errors: list[str]) -> None:
    label = f"pair[{index}]"
    if not isinstance(pair, Mapping):
        errors.append(f"{label}: pair must be an object")
        return
    pair_id = str(pair.get("pair_id") or "")
    label = f"pair/{pair_id or index}"
    if pair.get("variant_identity_hidden") is not True:
        errors.append(f"{label}: variant identity must remain hidden")
    if pair.get("candidate_variant") not in {"A", "B"}:
        errors.append(f"{label}: candidate_variant must be A or B")
    if pair.get("rubric_id") != RUBRIC_ID:
        errors.append(f"{label}: rubric identity mismatch")
    if pair.get("rubric_digest") != rubric_file_digest():
        errors.append(f"{label}: rubric digest mismatch")
    if pair.get("pair_payload_digest") != pair_payload_digest(pair):
        errors.append(f"{label}: pair payload digest mismatch")
    target_context = pair.get("target_context")
    if not isinstance(target_context, Mapping):
        errors.append(f"{label}: target_context must be an object")
        target_context = {}
    else:
        concepts = target_context.get("jd_concepts")
        relevant = target_context.get("relevant_achievement_ids")
        if not isinstance(concepts, list) or not concepts:
            errors.append(f"{label}: JD concepts must be a nonempty array")
        if not isinstance(relevant, list) or not relevant:
            errors.append(f"{label}: relevant achievements must be a nonempty array")
    _validate_artifact(pair.get("resume_a"), f"{label}/resume_a", target_context, errors)
    _validate_artifact(pair.get("resume_b"), f"{label}/resume_b", target_context, errors)

    reviews = pair.get("reviews")
    if not isinstance(reviews, list) or len(reviews) != 2:
        errors.append(f"{label}: exactly two reviews are required")
        reviews = []
    identities: set[str] = set()
    review_ids: set[str] = set()
    review_digests: set[str] = set()
    for review_index, review in enumerate(reviews):
        review_label = f"{label}/review[{review_index}]"
        if not isinstance(review, Mapping):
            errors.append(f"{review_label}: review must be an object")
            continue
        review_id = str(review.get("review_id") or "")
        identity = str(review.get("reviewer_identity_ref") or "")
        if not review_id or review_id in review_ids:
            errors.append(f"{review_label}: review_id missing or duplicate")
        review_ids.add(review_id)
        if not identity.startswith("human-reviewer://") or identity in identities:
            errors.append(f"{review_label}: reviewer identity missing or not independent")
        identities.add(identity)
        if not str(review.get("qualification_ref") or "").startswith("resume-coach://"):
            errors.append(f"{review_label}: qualified resume coach is required")
        if review.get("independent_review") is not True:
            errors.append(f"{review_label}: independent review attestation is required")
        if review.get("blinded_payload_digest") != pair.get("pair_payload_digest"):
            errors.append(f"{review_label}: blinded payload digest mismatch")
        if review.get("rubric_digest") != pair.get("rubric_digest"):
            errors.append(f"{review_label}: rubric digest mismatch")
        if not digest_matches(review, "record_digest"):
            errors.append(f"{review_label}: record digest mismatch")
        review_digests.add(str(review.get("record_digest") or ""))
        _validate_labels(review.get("labels"), review_label, errors)

    adjudication = pair.get("adjudication")
    if not isinstance(adjudication, Mapping):
        errors.append(f"{label}: one adjudication is required")
        return
    if adjudication.get("status") not in {"CONSENSUS_ACCEPTED", "ADJUDICATED"}:
        errors.append(f"{label}: adjudication status is invalid")
    if adjudication.get("status") == "ADJUDICATED" and (
        not str(adjudication.get("adjudicator_identity_ref") or "").startswith("human-reviewer://")
        or not str(adjudication.get("qualification_ref") or "").startswith("resume-coach://")
        or adjudication.get("human_attestation") is not True
    ):
        errors.append(f"{label}: qualified human adjudicator attestation is required")
    if {str(value) for value in adjudication.get("review_refs") or []} != review_ids:
        errors.append(f"{label}: adjudication review refs do not bind both reviews")
    if {str(value) for value in adjudication.get("review_digests") or []} != review_digests:
        errors.append(f"{label}: adjudication review digests do not bind both reviews")
    if not digest_matches(adjudication, "record_digest"):
        errors.append(f"{label}: adjudication record digest mismatch")
    _validate_labels(adjudication.get("final_labels"), f"{label}/adjudication", errors)
    if adjudication.get("status") == "CONSENSUS_ACCEPTED" and len(reviews) == 2:
        review_label_digests = {
            canonical_digest(review.get("labels")) for review in reviews if isinstance(review, Mapping)
        }
        if (
            len(review_label_digests) != 1
            or canonical_digest(adjudication.get("final_labels")) not in review_label_digests
        ):
            errors.append(f"{label}: consensus labels do not exactly agree")


def validate_input_bundle(bundle: Any) -> list[str]:
    """Return stable reasons why a bundle cannot be evaluated safely."""

    errors: list[str] = []
    if not isinstance(bundle, Mapping):
        return ["input bundle must be an object"]
    if bundle.get("schema_version") != INPUT_SCHEMA_VERSION:
        errors.append("input schema version mismatch")
    if not digest_matches(bundle, "bundle_digest"):
        errors.append("input bundle digest mismatch")
    if bundle.get("official_w6_status") not in {"PASS", "FAIL", "UNKNOWN"}:
        errors.append("official W6 status is invalid")
    if not isinstance(bundle.get("generation_authorized"), bool):
        errors.append("generation authorization must be boolean")
    evidence = bundle.get("human_review_evidence")
    if not isinstance(evidence, Mapping):
        errors.append("human review evidence must be an object")
        evidence = {}
    elif not digest_matches(evidence, "record_digest"):
        errors.append("human review evidence record digest mismatch")
    pairs = bundle.get("pairs")
    if not isinstance(pairs, list):
        errors.append("pairs must be an array")
        pairs = []
    pair_ids: list[str] = []
    for index, pair in enumerate(pairs):
        _validate_pair(pair, index, errors)
        if isinstance(pair, Mapping):
            pair_ids.append(str(pair.get("pair_id") or ""))
    if any(not value for value in pair_ids) or len(pair_ids) != len(set(pair_ids)):
        errors.append("pair identities must be nonempty and unique")
    typed_pairs = [pair for pair in pairs if isinstance(pair, Mapping)]
    if evidence.get("w9_review_bundle_digest") != w9_review_bundle_digest(typed_pairs):
        errors.append("human review evidence does not bind the W9 review bundle")
    return sorted(set(errors))


__all__ = [
    "digest_matches",
    "pair_payload_digest",
    "pair_set_digest",
    "rubric_file_digest",
    "validate_input_bundle",
    "w9_review_bundle_digest",
]
