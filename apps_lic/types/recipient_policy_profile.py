"""Recipient policy profile receipt for apps_lic live harness rows."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

from apps_lic.types.recipient_archetype_mapping import (
    ARCHETYPE_C_LEVEL,
    ARCHETYPE_EXECUTIVE,
    map_lic_recipient_class_to_archetype,
)


SCORE_PROFILE_X1D_MIN_REQUIRED = "apps_lic.score_profile.x1d_min_required_judge.v1"
SCORE_PROFILE_X2_ONLY = "apps_lic.score_profile.x2_only.v1"

_REQUESTED_SLOT_TO_ARCHETYPE: dict[str, str] = {
    "RECRUITER": "RECRUITER",
    "RECRUITER_TA": "RECRUITER",
    "TA": "RECRUITER",
    "SENIOR_TA": "SENIOR_TA",
    "SENIOR_TALENT_ACQUISITION": "SENIOR_TA",
    "EXECUTIVE": "EXECUTIVE",
    "C_LEVEL": "C_LEVEL",
    "CLEVEL": "C_LEVEL",
    "CEO": "C_LEVEL",
    "C_SUITE": "C_LEVEL",
}


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _token(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_") or "unknown"


def normalize_requested_slot_to_archetype(requested_slot: str) -> str:
    normalized = _clean(requested_slot).upper().replace("-", "_").replace(" ", "_")
    return _REQUESTED_SLOT_TO_ARCHETYPE.get(normalized, normalized)


@dataclass(frozen=True)
class RecipientPolicyProfile:
    policy_profile_id: str
    requested_slot: str
    requested_slot_archetype: str
    actual_linkedin_title: str
    derived_lic_recipient_class: str
    mapped_prompt_archetype: str
    expected_prompt_archetype: str
    message_type: str
    required_route_family: str
    required_x1d_judge_profile_ids: tuple[str, ...]
    x1d_thresholds_by_judge_id: tuple[tuple[str, float], ...]
    minimum_score_profile_id: str
    minimum_x1d_threshold: float | None
    reason_codes: tuple[str, ...]

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.recipient_policy_profile.v1",
            "policy_profile_id": self.policy_profile_id,
            "requested_slot": self.requested_slot,
            "requested_slot_archetype": self.requested_slot_archetype,
            "actual_linkedin_title": self.actual_linkedin_title,
            "derived_lic_recipient_class": self.derived_lic_recipient_class,
            "mapped_prompt_archetype": self.mapped_prompt_archetype,
            "expected_prompt_archetype": self.expected_prompt_archetype,
            "message_type": self.message_type,
            "required_route_family": self.required_route_family,
            "required_x1d_judge_profile_ids": list(self.required_x1d_judge_profile_ids),
            "x1d_thresholds_by_judge_id": {
                judge_id: threshold
                for judge_id, threshold in self.x1d_thresholds_by_judge_id
            },
            "minimum_score_profile_id": self.minimum_score_profile_id,
            "minimum_x1d_threshold": self.minimum_x1d_threshold,
            "reason_codes": list(self.reason_codes),
        }

    def to_row_fields(self) -> dict[str, Any]:
        return {
            "recipient_policy_profile_id": self.policy_profile_id,
            "recipient_policy_profile": self.to_packet(),
            "recipient_policy_reason_codes": list(self.reason_codes),
            "minimum_score_profile_id": self.minimum_score_profile_id,
            "minimum_x1d_threshold": self.minimum_x1d_threshold,
        }


def build_recipient_policy_profile(
    *,
    requested_slot: str,
    actual_linkedin_title: str,
    derived_recipient_class: str,
    message_type: str,
    required_route_family: str,
    required_x1d_judge_profile_ids: tuple[str, ...] | list[str],
    x1d_thresholds_by_judge_id: Mapping[str, float] | None = None,
    expected_prompt_archetype: str = "",
) -> RecipientPolicyProfile:
    requested_slot_clean = _clean(requested_slot)
    requested_archetype = normalize_requested_slot_to_archetype(requested_slot_clean)
    derived_class = _clean(derived_recipient_class).upper()
    mapped_archetype = map_lic_recipient_class_to_archetype(derived_class)
    expected_archetype = _clean(expected_prompt_archetype).upper() or requested_archetype
    required_judges = tuple(str(judge_id) for judge_id in required_x1d_judge_profile_ids)
    threshold_source = dict(x1d_thresholds_by_judge_id or {})
    threshold_pairs = tuple(
        (judge_id, float(threshold_source[judge_id]))
        for judge_id in required_judges
        if judge_id in threshold_source
    )
    minimum_threshold = (
        min(threshold for _, threshold in threshold_pairs)
        if threshold_pairs
        else None
    )
    score_profile_id = (
        SCORE_PROFILE_X1D_MIN_REQUIRED
        if required_judges
        else SCORE_PROFILE_X2_ONLY
    )
    reasons: list[str] = [
        f"mapped_lic_class_to_prompt_archetype:{derived_class}->{mapped_archetype}",
        f"route_family:{_clean(required_route_family).upper()}",
        f"minimum_score_profile:{score_profile_id}",
    ]
    if requested_archetype != derived_class:
        reasons.append(
            f"requested_slot_differs_from_derived_class:{requested_archetype}!={derived_class}"
        )
    if expected_archetype == mapped_archetype:
        reasons.append(
            f"requested_slot_maps_to_prompt_archetype:{requested_archetype}->{mapped_archetype}"
        )
    else:
        reasons.append(
            f"requested_slot_archetype_mismatch:{expected_archetype}!={mapped_archetype}"
        )
    if required_judges:
        reasons.append("required_x1d_profiles_present")
    else:
        reasons.append("x1d_not_required_by_current_policy")
        if mapped_archetype in {ARCHETYPE_EXECUTIVE, ARCHETYPE_C_LEVEL}:
            reasons.append("executive_archetype_has_no_required_x1d_current_policy")

    policy_profile_id = ".".join(
        (
            "apps_lic",
            "recipient_policy",
            _token(requested_archetype),
            _token(derived_class),
            _token(mapped_archetype),
            _token(message_type),
            _token(required_route_family),
            "v1",
        )
    )
    return RecipientPolicyProfile(
        policy_profile_id=policy_profile_id,
        requested_slot=requested_slot_clean,
        requested_slot_archetype=requested_archetype,
        actual_linkedin_title=_clean(actual_linkedin_title),
        derived_lic_recipient_class=derived_class,
        mapped_prompt_archetype=mapped_archetype,
        expected_prompt_archetype=expected_archetype,
        message_type=_clean(message_type),
        required_route_family=_clean(required_route_family).upper(),
        required_x1d_judge_profile_ids=required_judges,
        x1d_thresholds_by_judge_id=threshold_pairs,
        minimum_score_profile_id=score_profile_id,
        minimum_x1d_threshold=minimum_threshold,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


__all__ = [
    "RecipientPolicyProfile",
    "SCORE_PROFILE_X1D_MIN_REQUIRED",
    "SCORE_PROFILE_X2_ONLY",
    "build_recipient_policy_profile",
    "normalize_requested_slot_to_archetype",
]
