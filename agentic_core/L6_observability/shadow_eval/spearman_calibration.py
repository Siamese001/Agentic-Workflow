"""Evidence-bound Spearman calibration for L6.4.

The module is app-neutral: app identity, thresholds, rubric identity, provider
profile, and label policy are supplied by a declarative profile. It performs no
I/O and imports no L4/UWG surface.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Mapping, Sequence

from agentic_core.L6_observability.shadow_eval._digest import canonical_json, stamp_digest
from agentic_core.L6_observability.shadow_eval.contracts import SpearmanCalibrationResult


class CalibrationMode(str, Enum):
    NO_CALIBRATION = "NO_CALIBRATION"
    USE_APPROVED_BASELINE = "USE_APPROVED_BASELINE"
    RUN_HUMAN_ALIGNMENT_CALIBRATION = "RUN_HUMAN_ALIGNMENT_CALIBRATION"
    RUN_HEURISTIC_SANITY = "RUN_HEURISTIC_SANITY"


@dataclass(frozen=True, slots=True)
class SpearmanCalibrationProfile:
    app_id: str
    task_class: str
    judge_id: str
    judge_version: str
    rubric_hash: str
    rubric_version: str
    provider_profile_ref: str
    minimum_samples: int
    minimum_spearman_rho: float
    maximum_p_value: float
    dataset_id: str = ""
    dataset_version: str = ""
    promotion_requires_human_labels: bool = True
    informational_only: bool = False
    required_for_exit: bool = True


@dataclass(frozen=True, slots=True)
class CalibrationSample:
    sample_id: str
    dataset_id: str
    dataset_version: str
    human_score: float
    label_source: str
    candidate_text: str = ""
    judge_score: float | None = None
    reviewer_refs: tuple[str, ...] = ()
    adjudication_ref: str = ""
    content_digest: str = ""
    target_role: str = ""
    target_level: str = ""
    target_company: str = ""
    task_class: str = ""
    judge_id: str = ""
    rubric_hash: str = ""
    rubric_version: str = ""
    label_policy: str = ""
    split: str = ""
    tags: tuple[str, ...] = ()


JudgeScoreFn = Callable[[CalibrationSample], float | None]


@dataclass(frozen=True, slots=True)
class CalibrationContext:
    mode: CalibrationMode = CalibrationMode.NO_CALIBRATION
    profile: SpearmanCalibrationProfile | None = None
    samples: tuple[CalibrationSample, ...] = ()
    judge_score_fn: JudgeScoreFn | None = None
    approved_result: SpearmanCalibrationResult | None = None
    approved_baseline_ref: str = ""


def profile_from_mapping(
    payload: Mapping[str, object],
    *,
    mode: CalibrationMode,
) -> SpearmanCalibrationProfile:
    section_name = (
        "semantic_alignment"
        if mode == CalibrationMode.RUN_HUMAN_ALIGNMENT_CALIBRATION
        else "heuristic_sanity"
    )
    section = payload.get(section_name)
    if not isinstance(section, Mapping):
        raise ValueError(f"missing calibration profile section {section_name!r}")
    return SpearmanCalibrationProfile(
        app_id=str(payload.get("app_id", "")),
        task_class=str(payload.get("task_class", "")),
        judge_id=str(payload.get("judge_id", "")),
        judge_version=str(payload.get("judge_version", "")),
        rubric_hash=str(payload.get("rubric_hash", "")),
        rubric_version=str(payload.get("rubric_version", "")),
        provider_profile_ref=str(payload.get("provider_profile_ref", "")),
        minimum_samples=int(section.get("minimum_samples", 0)),
        minimum_spearman_rho=float(section.get("minimum_spearman_rho", 0.0)),
        maximum_p_value=float(section.get("maximum_p_value", 1.0)),
        dataset_id=str(payload.get("dataset_id", "")),
        dataset_version=str(payload.get("dataset_version", "")),
        promotion_requires_human_labels=bool(
            section.get("promotion_requires_human_labels", section_name == "semantic_alignment")
        ),
        informational_only=bool(payload.get("informational_only", False)),
        required_for_exit=bool(payload.get("required_for_exit", True)),
    )


def score_calibration_samples(
    samples: Sequence[CalibrationSample],
    score_fn: JudgeScoreFn | None,
) -> tuple[CalibrationSample, ...]:
    scored: list[CalibrationSample] = []
    for sample in samples:
        score = sample.judge_score
        if score is None and score_fn is not None:
            score = score_fn(sample)
        scored.append(
            CalibrationSample(
                sample_id=sample.sample_id,
                dataset_id=sample.dataset_id,
                dataset_version=sample.dataset_version,
                human_score=sample.human_score,
                label_source=sample.label_source,
                candidate_text=sample.candidate_text,
                judge_score=score,
                reviewer_refs=sample.reviewer_refs,
                adjudication_ref=sample.adjudication_ref,
                content_digest=sample.content_digest,
                target_role=sample.target_role,
                target_level=sample.target_level,
                target_company=sample.target_company,
                task_class=sample.task_class,
                judge_id=sample.judge_id,
                rubric_hash=sample.rubric_hash,
                rubric_version=sample.rubric_version,
                label_policy=sample.label_policy,
                split=sample.split,
                tags=sample.tags,
            )
        )
    return tuple(scored)


def _digest_scores(values: Sequence[float]) -> str:
    return hashlib.sha256(canonical_json(list(values)).encode("utf-8")).hexdigest()


def _confidence_interval(rho: float, n: int) -> tuple[float, float] | None:
    if n <= 3 or abs(rho) >= 1.0:
        return None
    z = math.atanh(max(-0.999999, min(0.999999, rho)))
    margin = 1.96 / math.sqrt(n - 3)
    return (math.tanh(z - margin), math.tanh(z + margin))


def _base_result(
    *,
    profile: SpearmanCalibrationProfile,
    samples: Sequence[CalibrationSample],
    human_scores: Sequence[float],
    judge_scores: Sequence[float],
    computed_at: str,
    rho: float | None,
    p_value: float | None,
    status: str,
    failure_reason_codes: Sequence[str],
) -> SpearmanCalibrationResult:
    dataset_ids = sorted({sample.dataset_id for sample in samples if sample.dataset_id})
    dataset_versions = sorted({sample.dataset_version for sample in samples if sample.dataset_version})
    label_sources = sorted({sample.label_source for sample in samples if sample.label_source})
    dataset_id = dataset_ids[0] if len(dataset_ids) == 1 else ""
    dataset_version = dataset_versions[0] if len(dataset_versions) == 1 else ""
    label_source = label_sources[0] if len(label_sources) == 1 else ""
    sample_size_met = len(samples) >= profile.minimum_samples
    threshold_met = bool(
        rho is not None
        and p_value is not None
        and rho >= profile.minimum_spearman_rho
        and p_value <= profile.maximum_p_value
    )
    human_labels = label_source == "human_semantic_review"
    reviewer_evidence = all(len(sample.reviewer_refs) >= 2 for sample in samples)
    promotion_eligible = bool(
        status == "PASS" and sample_size_met and threshold_met and human_labels and reviewer_evidence
    )
    human_digest = _digest_scores(human_scores)
    judge_digest = _digest_scores(judge_scores)
    identity_digest = hashlib.sha256(
        canonical_json(
            {
                "dataset_id": dataset_id,
                "dataset_version": dataset_version,
                "judge_id": profile.judge_id,
                "judge_version": profile.judge_version,
                "rubric_hash": profile.rubric_hash,
                "human_score_digest": human_digest,
                "judge_score_digest": judge_digest,
            }
        ).encode("utf-8")
    ).hexdigest()
    refs = sorted(
        {
            ref
            for sample in samples
            for ref in (sample.content_digest, *sample.reviewer_refs, sample.adjudication_ref)
            if ref
        }
    )
    result = SpearmanCalibrationResult(
        calibration_id=f"spearman::{identity_digest[:24]}",
        dataset_id=dataset_id,
        dataset_version=dataset_version,
        judge_id=profile.judge_id,
        judge_version=profile.judge_version,
        rubric_hash=profile.rubric_hash,
        rubric_version=profile.rubric_version,
        provider_profile_ref=profile.provider_profile_ref,
        n=len(samples),
        spearman_rho=rho,
        p_value=p_value,
        confidence_interval=(_confidence_interval(rho, len(samples)) if rho is not None else None),
        minimum_rho_threshold=profile.minimum_spearman_rho,
        maximum_p_value=profile.maximum_p_value,
        minimum_sample_size=profile.minimum_samples,
        sample_size_met=sample_size_met,
        threshold_met=threshold_met,
        label_source=label_source,
        promotion_eligible=promotion_eligible,
        fallback_only=not promotion_eligible,
        human_score_digest=human_digest,
        judge_score_digest=judge_digest,
        calibration_source_refs=refs,
        computed_at=computed_at,
        status=status,
        failure_reason_codes=list(failure_reason_codes),
    )
    return stamp_digest(result)


def compute_spearman_calibration(
    samples: Sequence[CalibrationSample],
    profile: SpearmanCalibrationProfile,
    *,
    computed_at: str | None = None,
) -> SpearmanCalibrationResult:
    rows = tuple(samples)
    now = computed_at or datetime.now(timezone.utc).isoformat()
    human_scores = [float(sample.human_score) for sample in rows]
    judge_scores = [float(sample.judge_score) for sample in rows if sample.judge_score is not None]
    failures: list[str] = []
    if len(judge_scores) != len(rows):
        failures.append("MISSING_JUDGE_SCORE")
    if len({sample.dataset_id for sample in rows}) != 1 or not rows:
        failures.append("DATASET_IDENTITY_MISSING_OR_MIXED")
    if len({sample.dataset_version for sample in rows}) != 1 or not rows:
        failures.append("DATASET_VERSION_MISSING_OR_MIXED")
    if profile.dataset_id and any(sample.dataset_id != profile.dataset_id for sample in rows):
        failures.append("DATASET_ID_DIFFERS_FROM_PROFILE")
    if profile.dataset_version and any(sample.dataset_version != profile.dataset_version for sample in rows):
        failures.append("DATASET_VERSION_DIFFERS_FROM_PROFILE")
    if len({sample.label_source for sample in rows}) != 1 or not rows:
        failures.append("LABEL_SOURCE_MISSING_OR_MIXED")
    if any(sample.task_class != profile.task_class for sample in rows):
        failures.append("TASK_CLASS_MISSING_OR_MISMATCHED")
    if any(sample.judge_id != profile.judge_id for sample in rows):
        failures.append("JUDGE_ID_MISSING_OR_MISMATCHED")
    if any(sample.rubric_hash != profile.rubric_hash for sample in rows):
        failures.append("RUBRIC_HASH_MISSING_OR_MISMATCHED")
    if any(sample.rubric_version != profile.rubric_version for sample in rows):
        failures.append("RUBRIC_VERSION_MISSING_OR_MISMATCHED")
    if any(not sample.sample_id for sample in rows):
        failures.append("MISSING_SAMPLE_ID")
    if len({sample.sample_id for sample in rows}) != len(rows):
        failures.append("DUPLICATE_SAMPLE_ID")
    if any(not sample.content_digest for sample in rows):
        failures.append("MISSING_DATASET_REF")
    if len({sample.content_digest for sample in rows}) != len(rows):
        failures.append("DUPLICATE_DATASET_REF")
    if rows and rows[0].label_source == "human_semantic_review":
        if any(len(sample.reviewer_refs) < 2 for sample in rows):
            failures.append("MISSING_REVIEWER_REFS")
    if len(rows) < profile.minimum_samples:
        failures.append("MINIMUM_SAMPLE_SIZE_NOT_MET")
    if any(not math.isfinite(value) for value in [*human_scores, *judge_scores]):
        failures.append("NON_FINITE_SCORE")
    if failures:
        return _base_result(
            profile=profile,
            samples=rows,
            human_scores=human_scores,
            judge_scores=judge_scores,
            computed_at=now,
            rho=None,
            p_value=None,
            status="INSUFFICIENT",
            failure_reason_codes=failures,
        )
    if len(set(human_scores)) < 2:
        return _base_result(
            profile=profile,
            samples=rows,
            human_scores=human_scores,
            judge_scores=judge_scores,
            computed_at=now,
            rho=None,
            p_value=None,
            status="INVALID_CALIBRATION_SET",
            failure_reason_codes=["CONSTANT_HUMAN_RANKING"],
        )
    if len(set(judge_scores)) < 2:
        return _base_result(
            profile=profile,
            samples=rows,
            human_scores=human_scores,
            judge_scores=judge_scores,
            computed_at=now,
            rho=None,
            p_value=None,
            status="JUDGE_COLLAPSE",
            failure_reason_codes=["CONSTANT_JUDGE_SCORES"],
        )
    try:
        from scipy.stats import spearmanr  # type: ignore[import-not-found]
    except ImportError:
        return _base_result(
            profile=profile,
            samples=rows,
            human_scores=human_scores,
            judge_scores=judge_scores,
            computed_at=now,
            rho=None,
            p_value=None,
            status="ERROR",
            failure_reason_codes=["SCIPY_UNAVAILABLE_NO_VERIFIED_FALLBACK"],
        )
    statistic = spearmanr(human_scores, judge_scores)
    rho = float(statistic.statistic)
    p_value = float(statistic.pvalue)
    if not math.isfinite(rho) or not math.isfinite(p_value):
        return _base_result(
            profile=profile,
            samples=rows,
            human_scores=human_scores,
            judge_scores=judge_scores,
            computed_at=now,
            rho=None,
            p_value=None,
            status="INSUFFICIENT",
            failure_reason_codes=["UNDEFINED_CORRELATION"],
        )
    if math.isclose(rho, 1.0, abs_tol=1e-12):
        rho = 1.0
    elif math.isclose(rho, -1.0, abs_tol=1e-12):
        rho = -1.0
    threshold_met = rho >= profile.minimum_spearman_rho and p_value <= profile.maximum_p_value
    reasons: list[str] = []
    if rho < profile.minimum_spearman_rho:
        reasons.append("RHO_BELOW_THRESHOLD")
    if p_value > profile.maximum_p_value:
        reasons.append("P_VALUE_ABOVE_MAXIMUM")
    if rows[0].label_source != "human_semantic_review":
        reasons.append("NON_HUMAN_LABEL_SOURCE_NOT_PROMOTION_ELIGIBLE")
    return _base_result(
        profile=profile,
        samples=rows,
        human_scores=human_scores,
        judge_scores=judge_scores,
        computed_at=now,
        rho=rho,
        p_value=p_value,
        status="PASS" if threshold_met else "BELOW_THRESHOLD",
        failure_reason_codes=reasons,
    )


__all__ = [
    "CalibrationContext",
    "CalibrationMode",
    "CalibrationSample",
    "JudgeScoreFn",
    "SpearmanCalibrationProfile",
    "compute_spearman_calibration",
    "profile_from_mapping",
    "score_calibration_samples",
]
