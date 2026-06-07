"""Employment bullet lanes (Unify / IBM): Qwen pool → Claude top-N with score floor + regen."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from apps_rg.runtime.judges.employment_bullet_judge_rubric import (
    EMPLOYMENT_BULLET_RUBRIC_VERSION,
    pool_selector_dimension_ids,
)
from apps_rg.runtime.reasoning.competencies_graph_pool import COMPETENCIES_SC_PATH_COUNT
from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

EMPLOYMENT_BULLET_LANES: Final[frozenset[str]] = frozenset({"unify_bullets", "ibm_bullets"})

# Employment bullets: Claude pool selector is the sole X1D judge (not the 3-provider panel).
EMPLOYMENT_BULLET_JUDGE_PROVIDERS: Final[tuple[str, ...]] = ("anthropic_claude",)

# Variance-class alignment (2026-06): bullet lanes generate over a FIXED slot count
# (unify=6, ibm=5). Generation variance is handled by the Claude pool selector +
# min_selection_score floor + employment X2 metric/anchor gates, NOT by brute-force
# sampling. SC lowered 15/12 -> 4 to match section_reasoning_intensity.py profile
# (the prior variance-class redesign that had not reached the execution path).
SC_PATH_COUNT_BY_LANE: Final[dict[str, int]] = {
    "unify_bullets": 4,
    "ibm_bullets": 4,
}

REGEN_EXTRA_PATHS_BY_LANE: Final[dict[str, int]] = {
    "unify_bullets": 3,
    "ibm_bullets": 3,
    "competencies": 4,
}

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
    if lane == "competencies":
        from apps_rg.runtime.reasoning.competencies_graph_pool import (
            competencies_regen_extra_path_count,
        )

        return competencies_regen_extra_path_count()
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
        except ValueError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
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


def is_employment_pool_generation(gen_meta: dict[str, Any] | None) -> bool:
    mode = str((gen_meta or {}).get("generation_mode") or "")
    return mode.startswith("qwen_employment_pool")


def competencies_pool_x1d_judge_rows(
    *,
    artifact_dir: Path,
    section_id: str,
    gen_meta: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Single X1D row from graph pool selection (10× Qwen paths → top-6 pass), gemini_pro only."""
    from apps_rg.runtime.judges.competencies_x1d import JUDGE_RUBRIC_VERSION
    from apps_rg.runtime.judges.executive_summary_x1d import PROVIDERS
    from apps_rg.runtime.reasoning.competencies_graph_pool import (
        COMPETENCIES_FINAL_CATEGORY_COUNT,
        min_competencies_selection_score,
    )

    lane = str(section_id or "").strip().lower() or "competencies"
    gate = dict((gen_meta or {}).get("selection_gate") or {})
    gate_ok = bool(gate.get("ok"))
    threshold = min_competencies_selection_score()
    n_final = COMPETENCIES_FINAL_CATEGORY_COUNT

    judge_path = artifact_dir / "bullet_pool_claude_selector_judge.json"
    sel_path = artifact_dir / "bullet_pool_selection.json"
    row: dict[str, Any] = {}
    if judge_path.is_file():
        loaded = json.loads(judge_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            row = dict(loaded)

    selections: list[dict[str, Any]] = []
    if sel_path.is_file():
        sel_doc = json.loads(sel_path.read_text(encoding="utf-8"))
        if isinstance(sel_doc, dict):
            selections = [s for s in (sel_doc.get("selections") or []) if isinstance(s, dict)]

    scores = [float(s.get("score") or 0.0) for s in selections if s.get("passes", True) is not False]
    min_score = min(scores) if scores else 0.0
    categories_ok = bool(selections) and all(float(s.get("score") or 0.0) >= threshold for s in selections)
    passed = gate_ok and categories_ok and len(selections) >= n_final

    gemini_meta = PROVIDERS.get("gemini_pro") or {}
    row.setdefault("judge_id", f"x1d_gemini_pro_{lane}_pool")
    row.setdefault("provider_name", gemini_meta.get("provider_name", "Google Gemini"))
    row["provider_key"] = "gemini_pro"
    row["section_id"] = lane
    row["evaluator_mode"] = "MODEL_BACKED"
    row["provider_available"] = True
    row["provider_blocked"] = False
    row["score_scale"] = "0_to_1"
    row["score"] = min_score
    row["normalized_score"] = min_score
    row["threshold"] = threshold
    row["normalized_threshold"] = threshold
    row["pass"] = passed
    row["pass_"] = passed
    row["decisive_failure"] = not passed
    row["provider_status"] = "MODEL_BACKED_PASS" if passed else "MODEL_BACKED_FAIL"
    row["proof_eligible_judge"] = True
    row["advisory_only"] = False
    row["judge_role"] = "competencies_graph_pool_selector"
    row["rubric_ref"] = "apps_rg/runtime/judges/competencies_x1d.py#graph_pool"
    row["rubric_version"] = JUDGE_RUBRIC_VERSION
    row["selection_mode"] = str(
        (gen_meta or {}).get("selection_mode") or "claude_competencies_top_6_pass"
    )
    row["final_category_count"] = n_final
    row["findings"] = [
        (
            f"Competencies graph pool selector: {len(selections)} category selections, "
            f"min_score={min_score:.2f}, threshold={threshold:.2f}, gate_ok={gate_ok}, "
            f"target_emit={n_final}"
        )
    ]
    return [row]


def employment_pool_x1d_judge_rows(
    *,
    artifact_dir: Path,
    section_id: str,
    gen_meta: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Single X1D row from Claude pool selection (15× Qwen paths → top-N pass)."""
    lane = str(section_id or "").strip().lower()
    gate = dict((gen_meta or {}).get("selection_gate") or {})
    gate_ok = bool(gate.get("ok"))
    threshold = min_selection_score_for_lane(lane)

    judge_path = artifact_dir / "bullet_pool_claude_selector_judge.json"
    sel_path = artifact_dir / "bullet_pool_selection.json"
    row: dict[str, Any] = {}
    if judge_path.is_file():
        loaded = json.loads(judge_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            row = dict(loaded)

    selections: list[dict[str, Any]] = []
    if sel_path.is_file():
        sel_doc = json.loads(sel_path.read_text(encoding="utf-8"))
        if isinstance(sel_doc, dict):
            selections = [s for s in (sel_doc.get("selections") or []) if isinstance(s, dict)]

    scores = [float(s.get("score") or 0.0) for s in selections if s.get("passes", True) is not False]
    min_score = min(scores) if scores else 0.0
    slots_ok = bool(selections) and all(float(s.get("score") or 0.0) >= threshold for s in selections)
    passed = gate_ok and slots_ok

    row.setdefault("judge_id", f"x1d_anthropic_claude_{lane}_pool")
    row.setdefault("provider_name", "Anthropic Claude")
    row["provider_key"] = "anthropic_claude"
    row["section_id"] = lane
    row["evaluator_mode"] = "MODEL_BACKED"
    row["provider_available"] = True
    row["provider_blocked"] = False
    row["score_scale"] = "0_to_1"
    row["score"] = min_score
    row["normalized_score"] = min_score
    row["threshold"] = threshold
    row["normalized_threshold"] = threshold
    row["pass"] = passed
    row["pass_"] = passed
    row["decisive_failure"] = not passed
    row["provider_status"] = "MODEL_BACKED_PASS" if passed else "MODEL_BACKED_FAIL"
    row["proof_eligible_judge"] = True
    row["advisory_only"] = False
    row["judge_role"] = "employment_bullet_pool_selector"
    row["rubric_ref"] = f"apps_rg/runtime/judges/employment_bullet_judge_rubric.py#{lane}"
    row["rubric_version"] = EMPLOYMENT_BULLET_RUBRIC_VERSION
    row["pool_selector_dimensions"] = list(pool_selector_dimension_ids(lane))
    row["selection_mode"] = str((gen_meta or {}).get("selection_mode") or "claude_employment_top_n_pass")
    row["findings"] = [
        (
            f"Employment pool selector: {len(selections)} slots, min_score={min_score:.2f}, "
            f"threshold={threshold:.2f}, gate_ok={gate_ok}"
        )
    ]
    return [row]


__all__ = [
    "COMPETENCIES_SC_PATH_COUNT",
    "DEFAULT_MIN_SELECTION_SCORE",
    "EMPLOYMENT_BULLET_JUDGE_PROVIDERS",
    "EMPLOYMENT_BULLET_LANES",
    "EmploymentSelectionGate",
    "competencies_pool_x1d_judge_rows",
    "employment_pool_x1d_judge_rows",
    "FINAL_BULLET_COUNT",
    "REGEN_EXTRA_PATHS_BY_LANE",
    "REQUIRED_BULLET_IDS",
    "SC_PATH_COUNT_BY_LANE",
    "build_employment_targeting_context",
    "evaluate_employment_selection_quality",
    "is_employment_bullet_lane",
    "is_employment_pool_generation",
    "max_employment_regen_rounds",
    "min_selection_score_for_lane",
    "regen_extra_path_count_for_lane",
    "sc_path_count_for_lane",
]
