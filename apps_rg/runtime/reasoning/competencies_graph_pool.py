"""Competencies graph_8x8 pool — 8 paths → 8 graph-grounded categories."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from apps_rg.runtime.sections.competencies_rigor import (
    CANDIDATE_CATEGORY_COUNT,
    MAX_CATEGORY_COUNT,
    MIN_CATEGORY_COUNT,
)

COMPETENCIES_SC_PATH_COUNT: Final[int] = CANDIDATE_CATEGORY_COUNT
COMPETENCIES_FINAL_CATEGORY_COUNT: Final[int] = MAX_CATEGORY_COUNT
COMPETENCIES_CANDIDATE_CATEGORY_COUNT: Final[int] = CANDIDATE_CATEGORY_COUNT
COMPETENCIES_REGEN_EXTRA_PATHS: Final[int] = 4

DEFAULT_COMPETENCIES_MIN_SELECTION_SCORE: Final[float] = 0.72


@dataclass(frozen=True)
class CompetenciesSelectionGate:
    ok: bool
    section_lane: str
    final_category_count: int
    min_score_threshold: float
    categories_passing: tuple[str, ...]
    categories_below_threshold: tuple[str, ...]
    categories_missing: tuple[str, ...]
    categories_in_merged: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "section_lane": self.section_lane,
            "final_category_count": self.final_category_count,
            "min_score_threshold": self.min_score_threshold,
            "categories_passing": list(self.categories_passing),
            "categories_below_threshold": list(self.categories_below_threshold),
            "categories_missing": list(self.categories_missing),
            "categories_in_merged": self.categories_in_merged,
        }


def min_competencies_selection_score() -> float:
    override = os.environ.get("APPS_RG_COMPETENCIES_MIN_SELECTION_SCORE", "").strip()
    if not override:
        override = os.environ.get("APPS_RG_EMPLOYMENT_BULLET_MIN_SELECTION_SCORE", "").strip()
    if override:
        try:
            return max(0.0, min(1.0, float(override)))
        except ValueError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
            pass
    return DEFAULT_COMPETENCIES_MIN_SELECTION_SCORE


def competencies_regen_extra_path_count() -> int:
    raw = os.environ.get("APPS_RG_COMPETENCIES_REGEN_EXTRA_PATHS", "").strip()
    if raw:
        try:
            return max(0, int(raw))
        except ValueError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
            pass
    return COMPETENCIES_REGEN_EXTRA_PATHS


def max_competencies_regen_rounds() -> int:
    raw = os.environ.get("APPS_RG_COMPETENCIES_MAX_REGEN_ROUNDS", "").strip()
    if not raw:
        raw = os.environ.get("APPS_RG_EMPLOYMENT_BULLET_MAX_REGEN_ROUNDS", "2").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return 2


def is_competencies_pool_generation(gen_meta: dict[str, Any] | None) -> bool:
    mode = str((gen_meta or {}).get("generation_mode") or "")
    return mode.startswith("qwen_competencies_graph_pool")


def build_competencies_targeting_context(
    runtime_payload: dict[str, Any],
    *,
    allowed_fact_ids: set[str] | None = None,
    allowed_skill_ids: set[str] | None = None,
) -> dict[str, Any]:
    """JD/briefing + graph proof metadata for pool selector (targeting only, not proof)."""
    pp = runtime_payload.get("proof_pool_metadata") or {}
    allowed = allowed_fact_ids or set()
    skill_ids: set[str] = set(allowed_skill_ids or [])
    for row in pp.get("selected_skill_rows") or []:
        if isinstance(row, dict):
            sid = str(row.get("skill_id") or "").strip()
            if sid:
                skill_ids.add(sid)
    for sid in pp.get("c03_selected_skill_ids") or []:
        if str(sid).strip():
            skill_ids.add(str(sid).strip())
    return {
        "target_title": runtime_payload.get("target_title"),
        "target_company": runtime_payload.get("target_company"),
        "jd_text": (runtime_payload.get("jd_text") or "")[:4000],
        "briefing": (runtime_payload.get("briefing") or "")[:2500],
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "skills_graph_ref": pp.get("graph_ref") or pp.get("augmented_skills_graph_ref"),
        "proof_pool_type": pp.get("proof_pool_type"),
        "selection_method": (runtime_payload.get("selected_fact_plan") or {}).get("selection_method"),
        "pool_path_count": COMPETENCIES_SC_PATH_COUNT,
        "candidate_category_count": COMPETENCIES_CANDIDATE_CATEGORY_COUNT,
        "final_category_count": COMPETENCIES_FINAL_CATEGORY_COUNT,
        "min_selection_score": min_competencies_selection_score(),
        "selection_model": "graph_8x8_v1",
        "allowed_fact_ids_count": len(allowed),
        "allowed_skill_ids": sorted(skill_ids),
    }


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


def _category_by_label(parsed: dict[str, Any], label: str) -> dict[str, Any] | None:
    norm = label.strip().lower()
    for key in ("competencies", "categories"):
        for row in parsed.get(key) or []:
            if not isinstance(row, dict):
                continue
            if str(row.get("category_label") or "").strip().lower() == norm:
                return row
    return None


def _heuristic_category_score(
    cat: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    allowed_skill_ids: set[str],
    resume_support_blob_lower: str,
) -> float:
    from apps_rg.runtime.validators.competencies_x2 import term_supports_resume_or_graph

    terms = cat.get("terms") or []
    if not isinstance(terms, list) or not terms:
        return 0.0
    supported = 0
    for raw_t in terms:
        term = raw_t if isinstance(raw_t, dict) else {"text": str(raw_t)}
        if term_supports_resume_or_graph(
            term,
            allowed_fact_ids=allowed_fact_ids,
            allowed_skill_ids=allowed_skill_ids,
            resume_support_blob_lower=resume_support_blob_lower,
        ):
            supported += 1
    base = supported / max(1, len(terms))
    cat_ids = [str(x).split("_metric_")[0] for x in (cat.get("source_fact_ids") or []) if x]
    if cat_ids and all(fid in allowed_fact_ids for fid in cat_ids):
        base = min(1.0, base + 0.05)
    return base


def _collect_category_candidates(
    paths: list[Any],
    selections: list[dict[str, Any]],
) -> dict[str, list[tuple[float, int, dict[str, Any]]]]:
    """label_lower -> [(score, path_index, category_dict), ...]"""
    out: dict[str, list[tuple[float, int, dict[str, Any]]]] = {}
    path_by_index = {p.path_index: p for p in paths}

    for sel in selections:
        if not isinstance(sel, dict):
            continue
        label = str(sel.get("category_label") or "").strip()
        if not label:
            continue
        key = label.lower()
        path_idx = int(sel.get("path_index", 0))
        path = path_by_index.get(path_idx)
        cat = _category_by_label(path.parsed or {}, label) if path and path.parsed else None
        if cat is None:
            continue
        score = _selection_row_score(sel)
        out.setdefault(key, []).append((score, path_idx, dict(cat)))

    for path in paths:
        if not path.parsed:
            continue
        for cat in (path.parsed.get("competencies") or path.parsed.get("categories") or []):
            if not isinstance(cat, dict):
                continue
            label = str(cat.get("category_label") or "").strip()
            if not label:
                continue
            key = label.lower()
            if key in out:
                continue
            out.setdefault(key, []).append((0.5, path.path_index, dict(cat)))
    return out


def merge_competencies_graph_pool_top_eight(
    paths: list[Any],
    selections: list[dict[str, Any]],
    *,
    base_parsed: dict[str, Any] | None = None,
    min_score_threshold: float | None = None,
    allowed_fact_ids: set[str] | None = None,
    allowed_skill_ids: set[str] | None = None,
    resume_support_blob_lower: str = "",
) -> tuple[dict[str, Any], dict[str, int]]:
    """Merge pool into exactly eight categories (top scores, graph-reality filtered)."""
    threshold = (
        min_score_threshold
        if min_score_threshold is not None
        else min_competencies_selection_score()
    )
    allowed_fact_ids = allowed_fact_ids or set()
    allowed_skill_ids = allowed_skill_ids or set()
    anchor = dict(base_parsed or (paths[0].parsed if paths else {}) or {})

    candidates = _collect_category_candidates(paths, selections)
    ranked: list[tuple[float, str, int, dict[str, Any]]] = []
    for key, variants in candidates.items():
        best_score = max((v[0] for v in variants), default=0.0)
        best = max(variants, key=lambda v: v[0])
        ranked.append((best_score, key, best[1], best[2]))

    passing_sel = [
        s
        for s in selections
        if isinstance(s, dict)
        and _selection_row_passes(s)
        and _selection_row_score(s) >= threshold
    ]
    if passing_sel:
        ranked = []
        for sel in passing_sel:
            label = str(sel.get("category_label") or "").strip()
            if not label:
                continue
            path_idx = int(sel.get("path_index", 0))
            path = next((p for p in paths if p.path_index == path_idx), paths[0] if paths else None)
            cat = _category_by_label(path.parsed or {}, label) if path and path.parsed else None
            if cat is None:
                continue
            ranked.append((_selection_row_score(sel), label.lower(), path_idx, dict(cat)))
        ranked.sort(key=lambda t: (-t[0], t[1]))
    else:
        for key, variants in candidates.items():
            best = max(variants, key=lambda v: v[0])
            h_score = _heuristic_category_score(
                best[2],
                allowed_fact_ids=allowed_fact_ids,
                allowed_skill_ids=allowed_skill_ids,
                resume_support_blob_lower=resume_support_blob_lower,
            )
            ranked.append((max(best[0], h_score), key, best[1], best[2]))
        ranked.sort(key=lambda t: (-t[0], t[1]))

    comps_out: list[dict[str, Any]] = []
    source_map: dict[str, int] = {}
    for score, key, path_idx, cat in ranked:
        if len(comps_out) >= COMPETENCIES_FINAL_CATEGORY_COUNT:
            break
        if score < threshold and passing_sel:
            continue
        h_score = _heuristic_category_score(
            cat,
            allowed_fact_ids=allowed_fact_ids,
            allowed_skill_ids=allowed_skill_ids,
            resume_support_blob_lower=resume_support_blob_lower,
        )
        if h_score < 0.34 and allowed_fact_ids:
            continue
        label = str(cat.get("category_label") or "").strip()
        comps_out.append(dict(cat))
        source_map[label.lower()] = path_idx

    if len(comps_out) < COMPETENCIES_FINAL_CATEGORY_COUNT:
        for _score, key, path_idx, cat in ranked:
            if len(comps_out) >= COMPETENCIES_FINAL_CATEGORY_COUNT:
                break
            label = str(cat.get("category_label") or "").strip()
            if not label or label.lower() in source_map:
                continue
            comps_out.append(dict(cat))
            source_map[label.lower()] = path_idx

    merged = dict(anchor)
    merged["competencies"] = comps_out[:COMPETENCIES_FINAL_CATEGORY_COUNT]
    if paths and paths[0].parsed and paths[0].parsed.get("claim_ledger"):
        merged["claim_ledger"] = list(paths[0].parsed.get("claim_ledger") or [])
    return merged, source_map


def evaluate_competencies_selection_quality(
    *,
    selections: list[dict[str, Any]],
    merged_parsed: dict[str, Any],
    min_score: float | None = None,
) -> CompetenciesSelectionGate:
    threshold = min_score if min_score is not None else min_competencies_selection_score()
    n_final = COMPETENCIES_FINAL_CATEGORY_COUNT
    comps = merged_parsed.get("competencies") or merged_parsed.get("categories") or []
    comps_n = len(comps) if isinstance(comps, list) else 0

    by_label: dict[str, dict[str, Any]] = {}
    for row in selections:
        if isinstance(row, dict):
            lab = str(row.get("category_label") or "").strip().lower()
            if lab:
                by_label[lab] = row

    passing: list[str] = []
    below: list[str] = []
    missing: list[str] = []

    merged_labels = {
        str(c.get("category_label") or "").strip().lower()
        for c in comps
        if isinstance(c, dict) and str(c.get("category_label") or "").strip()
    }

    for lab in sorted(merged_labels):
        sel = by_label.get(lab)
        if sel is None or not _selection_row_passes(sel):
            missing.append(lab)
            continue
        score = _selection_row_score(sel)
        if score < threshold:
            below.append(lab)
        else:
            passing.append(lab)

    ok = comps_n == n_final and len(passing) == n_final and not below and not missing
    return CompetenciesSelectionGate(
        ok=ok,
        section_lane="competencies",
        final_category_count=n_final,
        min_score_threshold=threshold,
        categories_passing=tuple(passing),
        categories_below_threshold=tuple(below),
        categories_missing=tuple(missing),
        categories_in_merged=comps_n,
    )


def write_competencies_regen_artifact(artifact_dir: Path, doc: dict[str, Any]) -> None:
    path = artifact_dir / "competencies_graph_pool_regen.json"
    prior: list[dict[str, Any]] = []
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded.get("rounds"), list):
                prior = loaded["rounds"]
        except (json.JSONDecodeError, OSError):
            prior = []
    path.write_text(
        json.dumps({"rounds": prior + [doc]}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "COMPETENCIES_CANDIDATE_CATEGORY_COUNT",
    "COMPETENCIES_FINAL_CATEGORY_COUNT",
    "COMPETENCIES_REGEN_EXTRA_PATHS",
    "COMPETENCIES_SC_PATH_COUNT",
    "CompetenciesSelectionGate",
    "build_competencies_targeting_context",
    "competencies_regen_extra_path_count",
    "evaluate_competencies_selection_quality",
    "is_competencies_pool_generation",
    "max_competencies_regen_rounds",
    "merge_competencies_graph_pool_top_eight",
    "min_competencies_selection_score",
    "write_competencies_regen_artifact",
]
