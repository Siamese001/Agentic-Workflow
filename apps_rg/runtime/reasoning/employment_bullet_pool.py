"""Employment bullet lanes (Unify / IBM): model pool -> Claude top-N with score floor + regen."""

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
from apps_rg.runtime.reasoning.competencies_graph_pool import (
    COMPETENCIES_SC_PATH_COUNT,
    competencies_initial_sc_path_count,
)
from apps_rg.runtime.section_execution_plan import (
    BULLET_LANES,
    DEFAULT_ACTIVE_SC_PATHS,
    MAX_SECTION_ATTEMPTS,
)
from apps_rg.runtime.section_model_limits import (
    resolve_selector_provider_model,
    selector_role_for_section,
)
from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

EMPLOYMENT_BULLET_LANES: Final[frozenset[str]] = frozenset(BULLET_LANES)

# Employment bullets: Claude is the advisory pool selector, not an X1D proof judge.
EMPLOYMENT_BULLET_SELECTOR_PROVIDERS: Final[tuple[str, ...]] = ("anthropic_claude",)
# Backward-compatible name for code that still imports the symbol; validators must not use it
# as a proof-provider roster.
EMPLOYMENT_BULLET_JUDGE_PROVIDERS: Final[tuple[str, ...]] = EMPLOYMENT_BULLET_SELECTOR_PROVIDERS

# Variance-class alignment (2026-06): bullet lanes generate over a FIXED slot count
# (unify=6, ibm=5, insurtech=3, ey=3). Generation variance is handled by the Claude pool
# selector + min_selection_score floor + employment X2 metric/anchor gates, NOT by
# brute-force sampling. Unify/IBM are adaptive: start with 2 paths and expand to 4 only
# when the selector gate reports missing slots or below-threshold winners. EY/InsurTech
# run the 2-path SC pool directly.
EMPLOYMENT_BULLET_SC_PATHS: Final[int] = 2
EMPLOYMENT_BULLET_WIDE_MAX_SC_PATHS: Final[int] = DEFAULT_ACTIVE_SC_PATHS
ADAPTIVE_EMPLOYMENT_BULLET_LANES: Final[frozenset[str]] = frozenset(
    {"unify_bullets", "ibm_bullets"}
)
SC_PATH_COUNT_BY_LANE: Final[dict[str, int]] = {
    "unify_bullets": EMPLOYMENT_BULLET_SC_PATHS,
    "ibm_bullets": EMPLOYMENT_BULLET_SC_PATHS,
    "insurtech_bullets": EMPLOYMENT_BULLET_SC_PATHS,
    "ey_bullets": EMPLOYMENT_BULLET_SC_PATHS,
}
MAX_SC_PATH_COUNT_BY_LANE: Final[dict[str, int]] = {
    "unify_bullets": EMPLOYMENT_BULLET_WIDE_MAX_SC_PATHS,
    "ibm_bullets": EMPLOYMENT_BULLET_WIDE_MAX_SC_PATHS,
    "insurtech_bullets": EMPLOYMENT_BULLET_SC_PATHS,
    "ey_bullets": EMPLOYMENT_BULLET_SC_PATHS,
}

REGEN_EXTRA_PATHS_BY_LANE: Final[dict[str, int]] = {
    lane: 3 for lane in BULLET_LANES
} | {"unify_bullets": 2, "ibm_bullets": 2, "competencies": 4}

FINAL_BULLET_COUNT: Final[dict[str, int]] = {
    "unify_bullets": len(UNIFY_BULLET_IDS),
    "ibm_bullets": len(IBM_BULLET_IDS),
    "insurtech_bullets": 3,
    "ey_bullets": 3,
}

PROOF_UNIQUE_SOURCE_FACT_LANES: Final[frozenset[str]] = frozenset(
    {"insurtech_bullets", "ey_bullets"}
)

REQUIRED_BULLET_IDS: Final[dict[str, tuple[str, ...]]] = {
    "unify_bullets": UNIFY_BULLET_IDS,
    "ibm_bullets": IBM_BULLET_IDS,
    "insurtech_bullets": ("bul_insurtech_001", "bul_insurtech_002", "bul_insurtech_003"),
    "ey_bullets": ("bul_ey_001", "bul_ey_002", "bul_ey_003"),
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
    unique_source_fact_ids: tuple[str, ...] = ()
    duplicate_source_fact_ids: tuple[str, ...] = ()
    slots_missing_source_fact_ids: tuple[str, ...] = ()
    proof_unique_source_fact_gate_active: bool = False

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
            "unique_source_fact_ids": list(self.unique_source_fact_ids),
            "unique_source_fact_count": len(self.unique_source_fact_ids),
            "duplicate_source_fact_ids": list(self.duplicate_source_fact_ids),
            "slots_missing_source_fact_ids": list(self.slots_missing_source_fact_ids),
            "proof_unique_source_fact_gate_active": self.proof_unique_source_fact_gate_active,
        }


def is_employment_bullet_lane(section_lane: str) -> bool:
    return str(section_lane or "").strip().lower() in EMPLOYMENT_BULLET_LANES


def sc_path_count_for_lane(section_lane: str) -> int:
    lane = str(section_lane or "").strip().lower()
    if lane in SC_PATH_COUNT_BY_LANE:
        return SC_PATH_COUNT_BY_LANE[lane]
    if lane == "competencies":
        return competencies_initial_sc_path_count()
    from apps_rg.runtime.reasoning.section_reasoning_intensity import (
        profile_to_requested_kw,
        section_reasoning_profile,
    )

    raw = profile_to_requested_kw(section_reasoning_profile(lane)).get("self_consistency_samples", 1.0)
    try:
        return max(1, int(float(raw)))
    except (TypeError, ValueError):
        return 1


def adaptive_sc_enabled_for_lane(section_lane: str) -> bool:
    lane = str(section_lane or "").strip().lower()
    return lane in ADAPTIVE_EMPLOYMENT_BULLET_LANES


def max_sc_path_count_for_lane(section_lane: str) -> int:
    lane = str(section_lane or "").strip().lower()
    if lane in MAX_SC_PATH_COUNT_BY_LANE:
        return MAX_SC_PATH_COUNT_BY_LANE[lane]
    return sc_path_count_for_lane(lane)


def regen_extra_path_count_for_lane(section_lane: str) -> int:
    lane = str(section_lane or "").strip().lower()
    if lane == "competencies":
        from apps_rg.runtime.reasoning.competencies_graph_pool import (
            competencies_regen_extra_path_count,
        )

        return competencies_regen_extra_path_count()
    return REGEN_EXTRA_PATHS_BY_LANE.get(lane, 5)


def max_employment_regen_rounds() -> int:
    raw = os.environ.get(
        "APPS_RG_EMPLOYMENT_BULLET_MAX_REGEN_ROUNDS",
        str(max(0, MAX_SECTION_ATTEMPTS - 1)),
    ).strip()
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
    from apps_rg.runtime.reasoning.bullet_fact_entailment import build_slot_entailment_corpus

    pp = runtime_payload.get("proof_pool_metadata") or {}
    lane = str(section_lane or "").strip().lower()
    allowed_fact_ids = [str(x) for x in (runtime_payload.get("allowed_fact_ids") or []) if str(x).strip()]
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
        "max_pool_path_count": max_sc_path_count_for_lane(lane),
        "adaptive_sc_enabled": adaptive_sc_enabled_for_lane(lane),
        "min_selection_score": min_selection_score_for_lane(lane),
        "final_bullet_count": FINAL_BULLET_COUNT.get(lane, 0),
        "allowed_fact_ids": allowed_fact_ids,
        "selector_requires_valid_candidates": bool(allowed_fact_ids),
    }
    # W4.3 (G15/G17): per-slot numeric-entailment corpus from the C0-pool selected_fact_plan
    # (NOT base-resume extract_*_employment rows) + slot bundle non-metric text.
    ctx["slot_entailment_corpus"] = build_slot_entailment_corpus(
        lane,
        runtime_payload.get("selected_fact_plan") or {},
    )
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


def _root_source_fact_id(value: Any) -> str:
    return str(value or "").strip().split("_metric_")[0]


def _bullet_source_fact_ids_by_slot(bullets: list[Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in bullets:
        if not isinstance(row, dict):
            continue
        bid = str(row.get("bullet_id") or "").strip()
        if not bid:
            continue
        ids: list[str] = []
        for raw in row.get("source_fact_ids") or []:
            fid = _root_source_fact_id(raw)
            if fid and fid not in ids:
                ids.append(fid)
        out[bid] = ids
    return out


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
    source_ids_by_slot = _bullet_source_fact_ids_by_slot(bullets if isinstance(bullets, list) else [])

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
    slots_missing_source_fact_ids: list[str] = []

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
            if lane in PROOF_UNIQUE_SOURCE_FACT_LANES and not source_ids_by_slot.get(bid):
                slots_missing_source_fact_ids.append(bid)
        else:
            missing.append(bid)

    unique_source_fact_ids: list[str] = []
    duplicate_source_fact_ids: list[str] = []
    if lane in PROOF_UNIQUE_SOURCE_FACT_LANES:
        for bid in required_bullet_ids:
            for fid in source_ids_by_slot.get(bid, []):
                if fid in unique_source_fact_ids:
                    if fid not in duplicate_source_fact_ids:
                        duplicate_source_fact_ids.append(fid)
                    continue
                unique_source_fact_ids.append(fid)

    proof_unique_ok = True
    if lane in PROOF_UNIQUE_SOURCE_FACT_LANES:
        proof_unique_ok = (
            len(unique_source_fact_ids) >= n_final
            and not duplicate_source_fact_ids
            and not slots_missing_source_fact_ids
        )

    ok = (
        len(passing) == n_final
        and bullets_n == n_final
        and not below
        and not missing
        and proof_unique_ok
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
        unique_source_fact_ids=tuple(unique_source_fact_ids),
        duplicate_source_fact_ids=tuple(duplicate_source_fact_ids),
        slots_missing_source_fact_ids=tuple(slots_missing_source_fact_ids),
        proof_unique_source_fact_gate_active=lane in PROOF_UNIQUE_SOURCE_FACT_LANES,
    )


def is_employment_pool_generation(gen_meta: dict[str, Any] | None) -> bool:
    mode = str((gen_meta or {}).get("generation_mode") or "")
    return mode.startswith("model_employment_pool")


def _selector_model_row(section_id: str, *, slot_kind: str) -> tuple[str, str, str]:
    role = selector_role_for_section(section_id, slot_kind=slot_kind)
    return resolve_selector_provider_model(role)


def competencies_pool_x1d_judge_rows(
    *,
    artifact_dir: Path,
    section_id: str,
    gen_meta: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Selector receipt row for the competencies graph pool.

    This is the pool-selection receipt, not the formal competencies X1D proof judge. The
    competencies proof judge is model-backed OpenAI and is wired separately in the lane runtime.
    """
    from apps_rg.runtime.judges.competencies_x1d import JUDGE_RUBRIC_VERSION
    from apps_rg.runtime.reasoning.competencies_graph_pool import (
        COMPETENCIES_FINAL_CATEGORY_COUNT,
        COMPETENCIES_MIN_CATEGORY_COUNT,
        min_competencies_selection_score,
    )

    lane = str(section_id or "").strip().lower() or "competencies"
    gate = dict((gen_meta or {}).get("selection_gate") or {})
    gate_ok = bool(gate.get("ok"))
    threshold = min_competencies_selection_score()
    n_min = COMPETENCIES_MIN_CATEGORY_COUNT
    n_max = COMPETENCIES_FINAL_CATEGORY_COUNT

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
    passed = gate_ok and categories_ok and n_min <= len(selections) <= n_max

    # E2E-08 guard: distinguish an EMPTY selection input (selector returned no candidates,
    # or bullet_pool_selection.json absent) from a genuine below-threshold model-quality
    # failure. Without this, an empty merge silently emits a score=0.0 / pass=False row that
    # reads downstream as a judge/content failure when the real condition is upstream "no
    # candidates selected". Fail closed either way, but name the cause.
    empty_selection = not selections
    selection_file_present = sel_path.is_file()
    diagnostic_reason = None
    if empty_selection:
        diagnostic_reason = (
            "selector_returned_no_candidates"
            if selection_file_present
            else "no_selection_input_artifact"
        )

    selector_provider_key, selector_model, selector_model_source = _selector_model_row(
        lane,
        slot_kind="competencies",
    )
    selector_provider_name = (
        "Anthropic Claude" if selector_provider_key == "anthropic_claude" else "OpenAI ChatGPT"
    )
    row.setdefault("judge_id", f"x1d_{selector_provider_key}_{lane}_pool")
    row.setdefault("provider_name", selector_provider_name)
    row.setdefault("model_name", selector_model)
    row["model_source"] = str(row.get("model_source") or selector_model_source)
    row["provider_key"] = selector_provider_key
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
    row["proof_eligible_judge"] = False
    row["advisory_only"] = True
    row["judge_role"] = "competencies_graph_pool_selector"
    row["rubric_ref"] = "apps_rg/runtime/judges/competencies_x1d.py#graph_pool"
    row["rubric_version"] = JUDGE_RUBRIC_VERSION
    row["selection_mode"] = str(
        (gen_meta or {}).get("selection_mode")
        or (
            "claude_competencies_adaptive_6_8_pass"
            if selector_provider_key == "anthropic_claude"
            else "openai_competencies_adaptive_6_8_pass"
        )
    )
    row["min_category_count"] = n_min
    row["max_category_count"] = n_max
    row["final_category_count"] = int(gate.get("categories_in_merged") or len(selections))
    if empty_selection:
        # Truthful diagnostic: this is an upstream selector/data condition, not a model
        # judge-quality failure. Stamp an explicit reason so it cannot be mistaken for one.
        row["empty_selection"] = True
        row["diagnostic_reason"] = diagnostic_reason
        row["selection_file_present"] = selection_file_present
        row["provider_status"] = "BLOCKED_NO_SELECTION"
        row["proof_eligible_judge"] = False
        row["advisory_only"] = True
        row["findings"] = [
            (
                f"Competencies graph pool selector BLOCKED: {diagnostic_reason} "
                f"(0 category selections, selection_file_present={selection_file_present}, "
                f"gate_ok={gate_ok}, target_emit={n_min}-{n_max}). Upstream selector/data condition, "
                f"not a model-quality judge failure."
            )
        ]
    else:
        row["empty_selection"] = False
        row["findings"] = [
            (
                f"Competencies graph pool selector: {len(selections)} category selections, "
                f"min_score={min_score:.2f}, threshold={threshold:.2f}, gate_ok={gate_ok}, "
                f"target_emit={n_min}-{n_max}"
            )
        ]
    return [row]


def employment_pool_x1d_judge_rows(
    *,
    artifact_dir: Path,
    section_id: str,
    gen_meta: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Single X1D row from Claude pool selection (multi-path model pool -> top-N pass)."""
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

    selector_provider_key, selector_model, selector_model_source = _selector_model_row(
        lane,
        slot_kind="bullets",
    )
    row.setdefault("judge_id", f"x1d_{selector_provider_key}_{lane}_pool")
    row.setdefault(
        "provider_name",
        "Anthropic Claude" if selector_provider_key == "anthropic_claude" else selector_provider_key,
    )
    row.setdefault("model_name", selector_model)
    row["model_source"] = str(row.get("model_source") or selector_model_source)
    row["provider_key"] = selector_provider_key
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
    row["proof_eligible_judge"] = False
    row["advisory_only"] = True
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
    "ADAPTIVE_EMPLOYMENT_BULLET_LANES",
    "COMPETENCIES_SC_PATH_COUNT",
    "DEFAULT_MIN_SELECTION_SCORE",
    "EMPLOYMENT_BULLET_SELECTOR_PROVIDERS",
    "EMPLOYMENT_BULLET_JUDGE_PROVIDERS",
    "EMPLOYMENT_BULLET_LANES",
    "EMPLOYMENT_BULLET_SC_PATHS",
    "EMPLOYMENT_BULLET_WIDE_MAX_SC_PATHS",
    "EmploymentSelectionGate",
    "MAX_SC_PATH_COUNT_BY_LANE",
    "competencies_pool_x1d_judge_rows",
    "employment_pool_x1d_judge_rows",
    "FINAL_BULLET_COUNT",
    "REGEN_EXTRA_PATHS_BY_LANE",
    "REQUIRED_BULLET_IDS",
    "SC_PATH_COUNT_BY_LANE",
    "build_employment_targeting_context",
    "adaptive_sc_enabled_for_lane",
    "evaluate_employment_selection_quality",
    "is_employment_bullet_lane",
    "is_employment_pool_generation",
    "max_employment_regen_rounds",
    "max_sc_path_count_for_lane",
    "min_selection_score_for_lane",
    "regen_extra_path_count_for_lane",
    "sc_path_count_for_lane",
]
