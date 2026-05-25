"""Employment bullet lanes (Unify / IBM): Qwen pool → Claude top-N with score floor + regen."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Final

from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
from apps_rg.runtime.validators.unify_bullets_x2 import (
    DEFAULT_DISTRIBUTION,
    INTENSITY_BY_BULLET_SSOT,
    UNIFY_BULLET_IDS,
)

EMPLOYMENT_BULLET_LANES: Final[frozenset[str]] = frozenset({"unify_bullets", "ibm_bullets"})

SC_PATH_COUNT_BY_LANE: Final[dict[str, int]] = {
    "unify_bullets": 15,
    "ibm_bullets": 12,
}

REGEN_EXTRA_PATHS_BY_LANE: Final[dict[str, int]] = {
    "unify_bullets": 5,
    "ibm_bullets": 4,
}

COMPETENCIES_SC_PATH_COUNT: Final[int] = 4

FINAL_BULLET_COUNT: Final[dict[str, int]] = {
    "unify_bullets": len(UNIFY_BULLET_IDS),
    "ibm_bullets": len(IBM_BULLET_IDS),
}

REQUIRED_BULLET_IDS: Final[dict[str, tuple[str, ...]]] = {
    "unify_bullets": UNIFY_BULLET_IDS,
    "ibm_bullets": IBM_BULLET_IDS,
}

DEFAULT_MIN_SELECTION_SCORE: Final[float] = 0.72


@dataclass(frozen=True)
class EmploymentSelectionGate:
    ok: bool
    section_lane: str
    final_bullet_count: int
    min_score_threshold: float
    slots_passing: tuple[str, ...]
    slots_below_threshold: tuple[str, ...]
    slots_missing: tuple[str, ...]
    bullets_in_merged: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "section_lane": self.section_lane,
            "final_bullet_count": self.final_bullet_count,
            "min_score_threshold": self.min_score_threshold,
            "slots_passing": list(self.slots_passing),
            "slots_below_threshold": list(self.slots_below_threshold),
            "slots_missing": list(self.slots_missing),
            "bullets_in_merged": self.bullets_in_merged,
        }


def is_employment_bullet_lane(section_lane: str) -> bool:
    return str(section_lane or "").strip().lower() in EMPLOYMENT_BULLET_LANES


def sc_path_count_for_lane(section_lane: str) -> int:
    lane = str(section_lane or "").strip().lower()
    if lane in SC_PATH_COUNT_BY_LANE:
        return SC_PATH_COUNT_BY_LANE[lane]
    if lane == "competencies":
        return COMPETENCIES_SC_PATH_COUNT
    from apps_rg.runtime.reasoning.section_reasoning_intensity import (
        profile_to_requested_kw,
        section_reasoning_profile,
    )

    raw = profile_to_requested_kw(section_reasoning_profile(lane)).get("self_consistency_samples", 1.0)
    try:
        return max(1, int(float(raw)))
    except (TypeError, ValueError):
        return 1


def regen_extra_path_count_for_lane(section_lane: str) -> int:
    lane = str(section_lane or "").strip().lower()
    return REGEN_EXTRA_PATHS_BY_LANE.get(lane, 5)


def max_employment_regen_rounds() -> int:
    raw = os.environ.get("APPS_RG_EMPLOYMENT_BULLET_MAX_REGEN_ROUNDS", "2").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return 2


def min_selection_score_for_lane(section_lane: str) -> float:
    lane = str(section_lane or "").strip().lower().replace("-", "_")
    env_key = f"APPS_RG_{lane.upper()}_MIN_SELECTION_SCORE"
    override = os.environ.get(env_key, "").strip()
    if not override:
        override = os.environ.get("APPS_RG_EMPLOYMENT_BULLET_MIN_SELECTION_SCORE", "").strip()
    if override:
        try:
            return max(0.0, min(1.0, float(override)))
        except ValueError:
            pass
    return DEFAULT_MIN_SELECTION_SCORE


def build_employment_targeting_context(
    runtime_payload: dict[str, Any],
    *,
    section_lane: str,
) -> dict[str, Any]:
    """JD + briefing + skills proof metadata for Claude selection (targeting only, not proof)."""
    pp = runtime_payload.get("proof_pool_metadata") or {}
    lane = str(section_lane or "").strip().lower()
    ctx: dict[str, Any] = {
        "target_title": runtime_payload.get("target_title"),
        "target_company": runtime_payload.get("target_company"),
        "jd_text": (runtime_payload.get("jd_text") or "")[:4000],
        "briefing": (runtime_payload.get("briefing") or "")[:2500],
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "skills_graph_ref": pp.get("graph_ref") or pp.get("augmented_skills_graph_ref"),
        "proof_pool_type": pp.get("proof_pool_type"),
        "selection_method": (runtime_payload.get("selected_fact_plan") or {}).get("selection_method"),
        "pool_path_count": sc_path_count_for_lane(lane),
        "min_selection_score": min_selection_score_for_lane(lane),
        "final_bullet_count": FINAL_BULLET_COUNT.get(lane, 0),
    }
    if lane == "unify_bullets":
        ctx["rewrite_distribution"] = dict(DEFAULT_DISTRIBUTION)
        ctx["rewrite_intensity_by_bullet"] = dict(INTENSITY_BY_BULLET_SSOT)
        ctx["rewrite_intensity_contract"] = "2_HEAVY_3_MODERATE_1_LIGHT_PROTECTED"
    return ctx


def _selection_row_score(row: dict[str, Any]) -> float:
    try:
        return float(row.get("score", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _selection_row_passes(row: dict[str, Any]) -> bool:
    if "passes" not in row:
        return True
    val = row.get("passes")
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("true", "1", "yes")


def evaluate_employment_selection_quality(
    *,
    section_lane: str,
    required_bullet_ids: tuple[str, ...],
    selections: list[dict[str, Any]],
    merged_parsed: dict[str, Any],
    min_score: float | None = None,
) -> EmploymentSelectionGate:
    """True when all required slots have passes=true and score >= min_score threshold."""
    lane = str(section_lane or "").strip().lower()
    threshold = min_score if min_score is not None else min_selection_score_for_lane(lane)
    n_final = FINAL_BULLET_COUNT.get(lane, len(required_bullet_ids))
    bullets = merged_parsed.get("bullets") or []
    bullets_n = len(bullets) if isinstance(bullets, list) else 0

    by_bullet: dict[str, dict[str, Any]] = {}
    for row in selections:
        if not isinstance(row, dict):
            continue
        bid = str(row.get("bullet_id") or "").strip()
        if bid:
            by_bullet[bid] = row

    passing: list[str] = []
    below: list[str] = []
    missing: list[str] = []

    for bid in required_bullet_ids:
        sel = by_bullet.get(bid)
        bullet_present = any(
            isinstance(b, dict) and str(b.get("bullet_id") or "").strip() == bid for b in (bullets or [])
        )
        if sel is None or not _selection_row_passes(sel):
            missing.append(bid)
            continue
        score = _selection_row_score(sel)
        if score < threshold:
            below.append(bid)
        elif bullet_present:
            passing.append(bid)
        else:
            missing.append(bid)

    ok = (
        len(passing) == n_final
        and bullets_n == n_final
        and not below
        and not missing
    )
    return EmploymentSelectionGate(
        ok=ok,
        section_lane=lane,
        final_bullet_count=n_final,
        min_score_threshold=threshold,
        slots_passing=tuple(passing),
        slots_below_threshold=tuple(below),
        slots_missing=tuple(missing),
        bullets_in_merged=bullets_n,
    )


__all__ = [
    "COMPETENCIES_SC_PATH_COUNT",
    "DEFAULT_MIN_SELECTION_SCORE",
    "EMPLOYMENT_BULLET_LANES",
    "EmploymentSelectionGate",
    "FINAL_BULLET_COUNT",
    "REGEN_EXTRA_PATHS_BY_LANE",
    "REQUIRED_BULLET_IDS",
    "SC_PATH_COUNT_BY_LANE",
    "build_employment_targeting_context",
    "evaluate_employment_selection_quality",
    "is_employment_bullet_lane",
    "max_employment_regen_rounds",
    "min_selection_score_for_lane",
    "regen_extra_path_count_for_lane",
    "sc_path_count_for_lane",
]
