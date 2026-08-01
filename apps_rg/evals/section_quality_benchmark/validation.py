"""Fail-closed validation and sealing for section-quality artifacts."""

from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import yaml

from apps_rg.evals.resume_graph.constants import _SHA256_RE
from apps_rg.evals.resume_graph.reporting import canonical_digest
from apps_rg.evals.section_quality_benchmark.constants import (
    DIMENSIONS,
    INPUT_SCHEMA_VERSION,
    PREFERENCES,
    REVIEW_SCHEMA_VERSION,
    REVIEWER_CLASSES,
    RUBRIC_FILES,
    SECTION_IDS,
)

_ROOT = Path(__file__).resolve().parent
_RUBRIC_ROOT = _ROOT / "rubrics"
_ARTIFACT_FIELDS = frozenset(
    {"artifact_id", "content", "content_digest", "grounding_status", "evidence_refs"}
)
_CASE_FIELDS = frozenset(
    {
        "case_id",
        "section_id",
        "mode",
        "split",
        "target_profile",
        "target_job_digest",
        "prompt_digest",
        "section_contract_ref",
        "candidate",
        "baseline",
        "blinding",
    }
)
_REVIEW_FIELDS = frozenset(
    {
        "review_id",
        "case_id",
        "section_id",
        "mode",
        "candidate_content_digest",
        "baseline_content_digest",
        "reviewer_class",
        "reviewer_identity_ref",
        "rubric_id",
        "rubric_digest",
        "dimension_scores",
        "dimension_preferences",
        "overall_preference",
        "material_worse_dimensions",
        "review_digest",
    }
)


def _is_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.fullmatch(value))


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def artifact_content_digest(artifact: Mapping[str, Any]) -> str:
    return canonical_digest(artifact.get("content"))


def blinding_digest(blinding: Mapping[str, Any]) -> str:
    return canonical_digest({key: value for key, value in blinding.items() if key != "blinding_digest"})


def input_bundle_digest(bundle: Mapping[str, Any]) -> str:
    return canonical_digest({key: value for key, value in bundle.items() if key != "bundle_digest"})


def review_digest(review: Mapping[str, Any]) -> str:
    return canonical_digest({key: value for key, value in review.items() if key != "review_digest"})


def review_bundle_digest(bundle: Mapping[str, Any]) -> str:
    return canonical_digest({key: value for key, value in bundle.items() if key != "bundle_digest"})


def rubric_digest(rubric: Mapping[str, Any]) -> str:
    return canonical_digest(rubric)


def load_rubrics() -> dict[str, dict[str, Any]]:
    """Load and validate the governed rubric for every supported section lane."""

    profile = yaml.safe_load((_RUBRIC_ROOT / "common_dimensions.v1.yaml").read_text(encoding="utf-8"))
    if not isinstance(profile, Mapping) or set(profile.get("dimensions", {})) != set(DIMENSIONS):
        raise ValueError("common section-quality dimension profile is invalid")
    loaded_by_file: dict[str, dict[str, Any]] = {}
    by_section: dict[str, dict[str, Any]] = {}
    for section_id, filename in RUBRIC_FILES.items():
        if filename not in loaded_by_file:
            value = yaml.safe_load((_RUBRIC_ROOT / filename).read_text(encoding="utf-8"))
            if not isinstance(value, Mapping):
                raise ValueError(f"rubric is not an object: {filename}")
            rubric = dict(value)
            if (
                rubric.get("schema_version") != "apps_rg.section_quality_rubric.v1"
                or rubric.get("dimension_profile") != "common_dimensions.v1.yaml"
                or tuple(rubric.get("required_dimensions", ())) != DIMENSIONS
                or not isinstance(rubric.get("minimum_score"), (int, float))
                or not 1 <= float(rubric["minimum_score"]) <= 5
                or not set(rubric.get("critical_dimensions", ())).issubset(DIMENSIONS)
                or rubric.get("pairwise", {}).get("variant_identity_hidden_required") is not True
                or rubric.get("authority", {}).get("release_authorizing") is not False
                or rubric.get("authority", {}).get("promotion_scope") != "future_runs_only"
            ):
                raise ValueError(f"rubric contract is invalid: {filename}")
            rubric["dimension_definitions"] = dict(profile["dimensions"])
            rubric["rubric_digest"] = rubric_digest(rubric)
            loaded_by_file[filename] = rubric
        rubric = loaded_by_file[filename]
        if section_id not in rubric.get("section_ids", ()):
            raise ValueError(f"rubric does not authorize lane {section_id}: {filename}")
        by_section[section_id] = rubric
    return by_section


def seal_input_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Seal an explicitly constructed fixture or completed input bundle."""

    sealed = deepcopy(dict(bundle))
    for case in sealed.get("lane_cases", []):
        for role in ("candidate", "baseline"):
            artifact = case.get(role)
            if isinstance(artifact, Mapping):
                artifact["content_digest"] = artifact_content_digest(artifact)
        blinding = case.get("blinding")
        if isinstance(blinding, Mapping):
            blinding["blinding_digest"] = blinding_digest(blinding)
    sealed["bundle_digest"] = input_bundle_digest(sealed)
    return sealed


def seal_review_bundle(
    bundle: Mapping[str, Any], input_bundle: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Bind completed fixture reviews to current governed rubric digests."""

    sealed = deepcopy(dict(bundle))
    if input_bundle is not None:
        sealed["input_bundle_digest"] = input_bundle.get("bundle_digest")
    rubrics = load_rubrics()
    for review in sealed.get("reviews", []):
        rubric = rubrics.get(review.get("section_id"))
        if rubric is not None:
            review["rubric_id"] = rubric["rubric_id"]
            review["rubric_digest"] = rubric["rubric_digest"]
        review["review_digest"] = review_digest(review)
    sealed["bundle_digest"] = review_bundle_digest(sealed)
    return sealed


def _validate_artifact(artifact: Any, section_id: str, prefix: str) -> list[str]:
    reasons: list[str] = []
    if not isinstance(artifact, Mapping) or set(artifact) != _ARTIFACT_FIELDS:
        return [f"{prefix}_ARTIFACT_SCHEMA_INVALID"]
    if not _is_nonempty_string(artifact.get("artifact_id")):
        reasons.append(f"{prefix}_ARTIFACT_ID_INVALID")
    content = artifact.get("content")
    if section_id == "headline":
        if not _is_nonempty_string(content):
            reasons.append(f"{prefix}_CONTENT_INVALID")
    elif not isinstance(content, Mapping) or not content:
        reasons.append(f"{prefix}_CONTENT_INVALID")
    digest = artifact.get("content_digest")
    if not _is_digest(digest) or digest != artifact_content_digest(artifact):
        reasons.append(f"{prefix}_CONTENT_DIGEST_INVALID")
    if artifact.get("grounding_status") not in ("PASS", "FAIL", "UNKNOWN"):
        reasons.append(f"{prefix}_GROUNDING_STATUS_INVALID")
    evidence_refs = artifact.get("evidence_refs")
    if (
        not isinstance(evidence_refs, list)
        or not evidence_refs
        or any(not _is_nonempty_string(value) for value in evidence_refs)
        or len(set(evidence_refs)) != len(evidence_refs)
    ):
        reasons.append(f"{prefix}_EVIDENCE_REFS_INVALID")
    return reasons


def _validate_blinding(value: Any) -> list[str]:
    if not isinstance(value, Mapping) or set(value) != {
        "candidate_variant",
        "baseline_variant",
        "variant_identity_hidden",
        "blinding_digest",
    }:
        return ["PAIRWISE_BLINDING_SCHEMA_INVALID"]
    reasons: list[str] = []
    candidate_variant = value.get("candidate_variant")
    baseline_variant = value.get("baseline_variant")
    if (
        candidate_variant not in ("VARIANT_A", "VARIANT_B")
        or baseline_variant not in ("VARIANT_A", "VARIANT_B")
        or candidate_variant == baseline_variant
    ):
        reasons.append("PAIRWISE_VARIANT_MAPPING_INVALID")
    if value.get("variant_identity_hidden") is not True:
        reasons.append("PAIRWISE_VARIANT_IDENTITY_NOT_HIDDEN")
    digest = value.get("blinding_digest")
    if not _is_digest(digest) or digest != blinding_digest(value):
        reasons.append("PAIRWISE_BLINDING_DIGEST_INVALID")
    return reasons


def validate_input_bundle(bundle: Any) -> list[str]:
    """Return stable reasons for any invalid or unsealed benchmark input."""

    if not isinstance(bundle, Mapping) or set(bundle) != {
        "schema_version",
        "benchmark_id",
        "lane_cases",
        "bundle_digest",
    }:
        return ["INPUT_BUNDLE_SCHEMA_INVALID"]
    reasons: list[str] = []
    if bundle.get("schema_version") != INPUT_SCHEMA_VERSION:
        reasons.append("INPUT_SCHEMA_VERSION_INVALID")
    if not _is_nonempty_string(bundle.get("benchmark_id")):
        reasons.append("BENCHMARK_ID_INVALID")
    cases = bundle.get("lane_cases")
    if not isinstance(cases, list) or not cases:
        reasons.append("LANE_CASES_EMPTY")
        cases = []
    case_ids: list[str] = []
    for case in cases:
        if not isinstance(case, Mapping) or set(case) != _CASE_FIELDS:
            reasons.append("LANE_CASE_SCHEMA_INVALID")
            continue
        case_id = case.get("case_id")
        if not _is_nonempty_string(case_id):
            reasons.append("CASE_ID_INVALID")
        else:
            case_ids.append(case_id)
        section_id = case.get("section_id")
        if section_id not in SECTION_IDS:
            reasons.append("SECTION_ID_INVALID")
            continue
        mode = case.get("mode")
        if mode not in ("ABSOLUTE", "PAIRWISE"):
            reasons.append("CASE_MODE_INVALID")
        if case.get("split") not in ("CALIBRATION", "HOLDOUT"):
            reasons.append("CASE_SPLIT_INVALID")
        for field in ("target_profile", "section_contract_ref"):
            if not _is_nonempty_string(case.get(field)):
                reasons.append(f"{field.upper()}_INVALID")
        for field in ("target_job_digest", "prompt_digest"):
            if not _is_digest(case.get(field)):
                reasons.append(f"{field.upper()}_INVALID")
        reasons.extend(_validate_artifact(case.get("candidate"), section_id, "CANDIDATE"))
        baseline = case.get("baseline")
        if mode == "ABSOLUTE" and baseline is not None:
            reasons.append("ABSOLUTE_BASELINE_FORBIDDEN")
        elif mode == "ABSOLUTE" and case.get("blinding") is not None:
            reasons.append("ABSOLUTE_BLINDING_FORBIDDEN")
        elif mode == "PAIRWISE":
            reasons.extend(_validate_artifact(baseline, section_id, "BASELINE"))
            reasons.extend(_validate_blinding(case.get("blinding")))
    if len(set(case_ids)) != len(case_ids):
        reasons.append("CASE_ID_DUPLICATE")
    digest = bundle.get("bundle_digest")
    if not _is_digest(digest) or digest != input_bundle_digest(bundle):
        reasons.append("INPUT_BUNDLE_DIGEST_INVALID")
    return sorted(set(reasons))


def _validate_dimension_scores(value: Any) -> list[str]:
    if not isinstance(value, Mapping) or set(value) != set(DIMENSIONS):
        return ["DIMENSION_SCORE_SET_INCOMPLETE"]
    reasons: list[str] = []
    for dimension, result in value.items():
        if not isinstance(result, Mapping) or set(result) != {"score", "reason", "evidence_refs"}:
            reasons.append("DIMENSION_SCORE_SCHEMA_INVALID")
            continue
        score = result.get("score")
        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not math.isfinite(float(score))
            or not 1 <= float(score) <= 5
        ):
            reasons.append(f"DIMENSION_SCORE_INVALID_{dimension.upper()}")
        if not _is_nonempty_string(result.get("reason")):
            reasons.append(f"DIMENSION_REASON_MISSING_{dimension.upper()}")
        refs = result.get("evidence_refs")
        if (
            not isinstance(refs, list)
            or not refs
            or any(not _is_nonempty_string(ref) for ref in refs)
            or len(set(refs)) != len(refs)
        ):
            reasons.append(f"DIMENSION_EVIDENCE_MISSING_{dimension.upper()}")
    return reasons


def _validate_review(
    review: Any,
    cases_by_id: Mapping[str, Mapping[str, Any]],
    rubrics: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    if not isinstance(review, Mapping) or set(review) != _REVIEW_FIELDS:
        return ["REVIEW_SCHEMA_INVALID"]
    reasons: list[str] = []
    for field in ("review_id", "case_id", "reviewer_identity_ref"):
        if not _is_nonempty_string(review.get(field)):
            reasons.append(f"{field.upper()}_INVALID")
    case = cases_by_id.get(str(review.get("case_id", "")))
    if case is None:
        reasons.append("REVIEW_CASE_NOT_FOUND")
    elif review.get("section_id") != case.get("section_id") or review.get("mode") != case.get("mode"):
        reasons.append("REVIEW_CASE_BINDING_MISMATCH")
    else:
        expected_baseline_digest = (
            case["baseline"]["content_digest"] if isinstance(case.get("baseline"), Mapping) else None
        )
        if (
            review.get("candidate_content_digest") != case["candidate"]["content_digest"]
            or review.get("baseline_content_digest") != expected_baseline_digest
        ):
            reasons.append("REVIEW_ARTIFACT_DIGEST_BINDING_MISMATCH")
    section_id = review.get("section_id")
    if section_id not in SECTION_IDS:
        reasons.append("REVIEW_SECTION_ID_INVALID")
    reviewer_class = review.get("reviewer_class")
    if not isinstance(reviewer_class, str) or reviewer_class not in REVIEWER_CLASSES:
        reasons.append("REVIEWER_CLASS_INVALID")
    rubric = rubrics.get(str(section_id))
    if rubric is None or (
        review.get("rubric_id") != rubric.get("rubric_id")
        or review.get("rubric_digest") != rubric.get("rubric_digest")
    ):
        reasons.append("REVIEW_RUBRIC_BINDING_INVALID")
    reasons.extend(_validate_dimension_scores(review.get("dimension_scores")))
    preferences = review.get("dimension_preferences")
    if review.get("mode") == "ABSOLUTE":
        if preferences is not None or review.get("overall_preference") != "NOT_APPLICABLE":
            reasons.append("ABSOLUTE_PREFERENCE_FORBIDDEN")
        if review.get("material_worse_dimensions") != []:
            reasons.append("ABSOLUTE_WORSE_DIMENSIONS_FORBIDDEN")
    elif review.get("mode") == "PAIRWISE":
        if (
            not isinstance(preferences, Mapping)
            or set(preferences) != set(DIMENSIONS)
            or any(not isinstance(value, str) or value not in PREFERENCES for value in preferences.values())
        ):
            reasons.append("PAIRWISE_PREFERENCE_SET_INVALID")
        overall_preference = review.get("overall_preference")
        if not isinstance(overall_preference, str) or overall_preference not in PREFERENCES:
            reasons.append("PAIRWISE_OVERALL_PREFERENCE_INVALID")
        worse = review.get("material_worse_dimensions")
        if (
            not isinstance(worse, list)
            or any(not isinstance(value, str) or value not in DIMENSIONS for value in worse)
            or len(set(worse)) != len(worse)
        ):
            reasons.append("PAIRWISE_WORSE_DIMENSIONS_INVALID")
    else:
        reasons.append("REVIEW_MODE_INVALID")
    digest = review.get("review_digest")
    if not _is_digest(digest) or digest != review_digest(review):
        reasons.append("REVIEW_DIGEST_INVALID")
    return reasons


def validate_review_bundle(
    bundle: Any,
    input_bundle: Mapping[str, Any],
    *,
    rubrics: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[str]:
    """Return stable reasons for invalid, unbound, or unsealed completed reviews."""

    if not isinstance(bundle, Mapping) or set(bundle) != {
        "schema_version",
        "benchmark_id",
        "input_bundle_digest",
        "reviews",
        "bundle_digest",
    }:
        return ["REVIEW_BUNDLE_SCHEMA_INVALID"]
    reasons: list[str] = []
    if bundle.get("schema_version") != REVIEW_SCHEMA_VERSION:
        reasons.append("REVIEW_SCHEMA_VERSION_INVALID")
    if bundle.get("benchmark_id") != input_bundle.get("benchmark_id"):
        reasons.append("REVIEW_BENCHMARK_BINDING_MISMATCH")
    if bundle.get("input_bundle_digest") != input_bundle.get("bundle_digest"):
        reasons.append("REVIEW_INPUT_BUNDLE_DIGEST_MISMATCH")
    reviews = bundle.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        reasons.append("REVIEWS_EMPTY")
        reviews = []
    cases_by_id = {
        str(case.get("case_id", "")): case
        for case in input_bundle.get("lane_cases", [])
        if isinstance(case, Mapping)
    }
    governed_rubrics = dict(rubrics or load_rubrics())
    review_ids: list[str] = []
    reviewer_case_pairs: list[tuple[str, str]] = []
    for review in reviews:
        if isinstance(review, Mapping):
            review_ids.append(str(review.get("review_id", "")))
            reviewer_case_pairs.append(
                (str(review.get("case_id", "")), str(review.get("reviewer_identity_ref", "")))
            )
        reasons.extend(_validate_review(review, cases_by_id, governed_rubrics))
    if len(set(review_ids)) != len(review_ids):
        reasons.append("REVIEW_ID_DUPLICATE")
    if len(set(reviewer_case_pairs)) != len(reviewer_case_pairs):
        reasons.append("REVIEWER_CASE_DUPLICATE")
    digest = bundle.get("bundle_digest")
    if not _is_digest(digest) or digest != review_bundle_digest(bundle):
        reasons.append("REVIEW_BUNDLE_DIGEST_INVALID")
    return sorted(set(reasons))


__all__ = [
    "artifact_content_digest",
    "blinding_digest",
    "input_bundle_digest",
    "load_rubrics",
    "review_bundle_digest",
    "review_digest",
    "rubric_digest",
    "seal_input_bundle",
    "seal_review_bundle",
    "validate_input_bundle",
    "validate_review_bundle",
]
