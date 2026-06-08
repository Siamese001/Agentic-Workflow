"""Bullet-pool generation: Qwen self-consistency paths + Claude per-slot selection."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from typing import Any, Callable

from apps_rg.runtime.judges.bullet_pool_claude_selector import (
    PoolSelectionResult,
    run_claude_bullet_pool_selection,
)
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.reasoning.bullet_lane_self_consistency import (
    SelfConsistencyPath,
    bullet_lane_sc_enabled,
    patch_receipt_samples_executed,
    run_qwen_self_consistency_paths,
    self_consistency_path_count,
)
from apps_rg.runtime.reasoning.competencies_graph_pool import (
    COMPETENCIES_CANDIDATE_CATEGORY_COUNT,
    COMPETENCIES_FINAL_CATEGORY_COUNT,
    evaluate_competencies_selection_quality,
    max_competencies_regen_rounds,
    min_competencies_selection_score,
    write_competencies_regen_artifact,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    REQUIRED_BULLET_IDS,
    evaluate_employment_selection_quality,
    is_employment_bullet_lane,
    max_employment_regen_rounds,
    min_selection_score_for_lane,
    regen_extra_path_count_for_lane,
    sc_path_count_for_lane,
)

NormalizeFn = Callable[[dict[str, Any]], dict[str, Any]]
ParseFn = Callable[[str], tuple[dict[str, Any] | None, str]]


def _normalize_selector_paths(
    paths: list[SelfConsistencyPath],
    normalize_parsed: NormalizeFn,
) -> list[SelfConsistencyPath]:
    """Canonicalize parsed path payloads before selector ranking sees them."""
    normalized: list[SelfConsistencyPath] = []
    for path in paths:
        if isinstance(path.parsed, dict):
            normalized.append(replace(path, parsed=normalize_parsed(dict(path.parsed))))
        else:
            normalized.append(path)
    return normalized


SELECTOR_EMPTY_BLOCK_REASON = "selector_returned_no_candidates_above_threshold"


def truthful_block_reason(
    result: ProviderResult | None,
    runtime_generation_status: str,
    parse_error: str,
) -> str:
    """Truthful block reason that does NOT claim 'provider blocked' when the provider actually
    produced output (REAL_LLM).

    E2E-09/10: an empty selector result or a parse failure on REAL_LLM output was being labeled
    'provider blocked', which is false — the provider succeeded; the block is downstream
    (selector returned no candidates above threshold, or JSON parse failed).
    """
    if result is not None and getattr(result, "exact_provider_error", None):
        return str(result.exact_provider_error)
    status = str(runtime_generation_status or "").upper()
    if status == "REAL_LLM":
        return str(parse_error or "") or "selector_returned_no_candidates_or_parse_failed"
    return str(parse_error or "") or "provider blocked"


def summarize_selector_emptiness(*, pool: PoolSelectionResult, gate: Any) -> dict[str, Any]:
    """Detect an empty bullet/competency selection and capture the sub-threshold scores so a
    downstream block is truthful and the < 0.72 selector scores are observable (W5 containment).

    Returns meta fields (not a control-flow change): ``selector_empty`` flags the empty case,
    ``selector_block_reason`` names it, ``subthreshold_scores`` records the scores that failed
    the gate so the deferred content-quality follow-up has data.
    """
    selections = list(getattr(pool, "selections", []) or [])
    selection_mode = str(getattr(pool, "selection_mode", "") or "")
    bullets_in_merged = int(getattr(gate, "bullets_in_merged", 0) or 0)
    empty = (not selections) or bullets_in_merged == 0 or selection_mode == "fallback_empty"
    subthreshold_scores: list[float] = []
    for s in selections:
        if isinstance(s, dict):
            try:
                subthreshold_scores.append(round(float(s.get("score") or 0.0), 4))
            except (TypeError, ValueError):  # guardian: allow-silent-swallow -- non-numeric score is skipped, not fatal
                continue
    out: dict[str, Any] = {
        "selector_empty": bool(empty),
        "selector_selection_mode": selection_mode,
        "selector_bullets_in_merged": bullets_in_merged,
        "selector_selection_count": len(selections),
        "selector_subthreshold_scores": subthreshold_scores,
    }
    if empty:
        out["selector_block_reason"] = SELECTOR_EMPTY_BLOCK_REASON
    return out


def _write_employment_regen_artifact(artifact_dir: Path, doc: dict[str, Any]) -> None:
    path = artifact_dir / "employment_bullet_regen.json"
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


def _generate_employment_bullet_lane(
    *,
    section_lane: str,
    provider_payload: dict[str, Any],
    parse_model_json: ParseFn,
    normalize_parsed: NormalizeFn,
    artifact_dir: Path | None,
    run_id: str | None,
    temperature_bounds: tuple[float, float],
    base_temperature: float | None,
    required_bullet_ids: tuple[str, ...],
    targeting_context: dict[str, Any] | None,
    judge_mode: str,
    provider_profile: str | None,
) -> tuple[ProviderResult | None, str, dict[str, Any] | None, str, dict[str, Any]]:
    min_score = min_selection_score_for_lane(section_lane)
    all_paths: list[SelfConsistencyPath] = []
    last_result: ProviderResult | None = None
    pool: PoolSelectionResult | None = None
    gate = evaluate_employment_selection_quality(
        section_lane=section_lane,
        required_bullet_ids=required_bullet_ids,
        selections=[],
        merged_parsed={},
        min_score=min_score,
    )
    regen_round = 0
    max_regen = 0 if judge_mode == "mocked" else max_employment_regen_rounds()

    while True:
        batch = (
            sc_path_count_for_lane(section_lane)
            if regen_round == 0
            else regen_extra_path_count_for_lane(section_lane)
        )
        new_paths, last_result = run_qwen_self_consistency_paths(
            section_lane=section_lane,
            provider_payload=provider_payload,
            parse_model_json=parse_model_json,
            artifact_dir=artifact_dir,
            run_id=run_id,
            temperature_bounds=temperature_bounds,
            base_temperature=base_temperature,
            path_count=batch,
            path_index_start=len(all_paths),
            append_artifacts=regen_round > 0,
            provider_profile=provider_profile,
        )
        new_paths = _normalize_selector_paths(new_paths, normalize_parsed)
        all_paths.extend(new_paths)

        regen_note = ""
        if regen_round > 0 and not gate.ok:
            failed = list(gate.slots_below_threshold) + list(gate.slots_missing)
            regen_note = (
                "REGEN ROUND: prior selection did not meet minimum score or slot coverage. "
                f"Re-score pool including new paths. Slots needing stronger winners: {', '.join(failed)}. "
                f"Only select variants with score >= {min_score:.2f} and passes=true."
            )

        pool = run_claude_bullet_pool_selection(
            section_id=section_lane,
            slot_kind="bullets",
            paths=all_paths,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
            artifact_dir=artifact_dir,
            mode=judge_mode,
            min_score_threshold=min_score,
            regen_note=regen_note,
        )
        gate = evaluate_employment_selection_quality(
            section_lane=section_lane,
            required_bullet_ids=required_bullet_ids,
            selections=pool.selections,
            merged_parsed=pool.merged_parsed,
            min_score=min_score,
        )

        if artifact_dir is not None:
            _write_employment_regen_artifact(
                artifact_dir,
                {
                    "regen_round": regen_round,
                    "batch_paths": batch,
                    "total_paths": len(all_paths),
                    "gate": gate.to_dict(),
                    "selection_mode": pool.selection_mode,
                },
            )

        if gate.ok or regen_round >= max_regen:
            break
        regen_round += 1

    completed = sum(1 for p in all_paths if p.parsed is not None)
    patch_receipt_samples_executed(
        last_result,
        paths_requested=len(all_paths),
        paths_completed=completed,
    )

    assert pool is not None
    merged = normalize_parsed(dict(pool.merged_parsed))
    meta: dict[str, Any] = {
        "generation_mode": "qwen_employment_pool_claude_top_n_regen",
        "section_lane": section_lane,
        "initial_path_count": sc_path_count_for_lane(section_lane),
        "total_paths_executed": len(all_paths),
        "regen_rounds_executed": regen_round,
        "min_selection_score": min_score,
        "selection_gate": gate.to_dict(),
        "selection_mode": pool.selection_mode,
        "source_path_by_slot": pool.source_path_by_slot,
        "claude_selection_count": len(pool.selections),
    }
    meta.update(summarize_selector_emptiness(pool=pool, gate=gate))
    if artifact_dir is not None:
        (artifact_dir / "bullet_pool_selection.json").write_text(
            json.dumps(
                {
                    "selection_mode": pool.selection_mode,
                    "selections": pool.selections,
                    "source_path_by_slot": pool.source_path_by_slot,
                    "selection_gate": gate.to_dict(),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    raw = json.dumps(merged, sort_keys=True, separators=(",", ":"))
    return last_result, raw, merged, "", meta


def _generate_competencies_graph_pool_lane(
    *,
    provider_payload: dict[str, Any],
    parse_model_json: ParseFn,
    normalize_parsed: NormalizeFn,
    artifact_dir: Path | None,
    run_id: str | None,
    temperature_bounds: tuple[float, float],
    base_temperature: float | None,
    targeting_context: dict[str, Any] | None,
    judge_mode: str,
    provider_profile: str | None,
) -> tuple[ProviderResult | None, str, dict[str, Any] | None, str, dict[str, Any]]:
    section_lane = "competencies"
    min_score = min_competencies_selection_score()
    all_paths: list[SelfConsistencyPath] = []
    last_result: ProviderResult | None = None
    pool: PoolSelectionResult | None = None
    gate = evaluate_competencies_selection_quality(
        selections=[],
        merged_parsed={},
        min_score=min_score,
    )
    regen_round = 0
    max_regen = 0 if judge_mode == "mocked" else max_competencies_regen_rounds()

    while True:
        batch = (
            sc_path_count_for_lane(section_lane)
            if regen_round == 0
            else regen_extra_path_count_for_lane(section_lane)
        )
        new_paths, last_result = run_qwen_self_consistency_paths(
            section_lane=section_lane,
            provider_payload=provider_payload,
            parse_model_json=parse_model_json,
            artifact_dir=artifact_dir,
            run_id=run_id,
            temperature_bounds=temperature_bounds,
            base_temperature=base_temperature,
            path_count=batch,
            path_index_start=len(all_paths),
            append_artifacts=regen_round > 0,
            provider_profile=provider_profile,
        )
        new_paths = _normalize_selector_paths(new_paths, normalize_parsed)
        all_paths.extend(new_paths)

        regen_note = ""
        if regen_round > 0 and not gate.ok:
            failed = list(gate.categories_below_threshold) + list(gate.categories_missing)
            regen_note = (
                "REGEN ROUND: prior selection did not meet minimum score or category coverage. "
                f"Re-score pool including new paths. Categories needing stronger winners: {', '.join(failed)}. "
                f"Select exactly {gate.final_category_count} categories with score >= {min_score:.2f} and passes=true."
            )

        pool = run_claude_bullet_pool_selection(
            section_id=section_lane,
            slot_kind="competencies",
            paths=all_paths,
            required_bullet_ids=None,
            targeting_context=targeting_context,
            artifact_dir=artifact_dir,
            mode=judge_mode,
            min_score_threshold=min_score,
            regen_note=regen_note,
        )
        gate = evaluate_competencies_selection_quality(
            selections=pool.selections,
            merged_parsed=pool.merged_parsed,
            min_score=min_score,
        )

        if artifact_dir is not None:
            write_competencies_regen_artifact(
                artifact_dir,
                {
                    "regen_round": regen_round,
                    "batch_paths": batch,
                    "total_paths": len(all_paths),
                    "gate": gate.to_dict(),
                    "selection_mode": pool.selection_mode,
                },
            )

        if gate.ok or regen_round >= max_regen:
            break
        regen_round += 1

    completed = sum(1 for p in all_paths if p.parsed is not None)
    patch_receipt_samples_executed(
        last_result,
        paths_requested=len(all_paths),
        paths_completed=completed,
    )

    assert pool is not None
    merged = normalize_parsed(dict(pool.merged_parsed))
    meta: dict[str, Any] = {
        "generation_mode": "qwen_competencies_graph_pool_claude_top_8_regen",
        "section_lane": section_lane,
        "initial_path_count": sc_path_count_for_lane(section_lane),
        "total_paths_executed": len(all_paths),
        "regen_rounds_executed": regen_round,
        "min_selection_score": min_score,
        "selection_gate": gate.to_dict(),
        "selection_mode": pool.selection_mode,
        "source_path_by_slot": pool.source_path_by_slot,
        "claude_selection_count": len(pool.selections),
        "candidate_category_count": COMPETENCIES_CANDIDATE_CATEGORY_COUNT,
        "final_category_count": COMPETENCIES_FINAL_CATEGORY_COUNT,
    }
    meta.update(summarize_selector_emptiness(pool=pool, gate=gate))
    if artifact_dir is not None:
        (artifact_dir / "bullet_pool_selection.json").write_text(
            json.dumps(
                {
                    "selection_mode": pool.selection_mode,
                    "selections": pool.selections,
                    "source_path_by_slot": pool.source_path_by_slot,
                    "selection_gate": gate.to_dict(),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    raw = json.dumps(merged, sort_keys=True, separators=(",", ":"))
    return last_result, raw, merged, "", meta


def generate_bullet_lane_with_sc_and_claude(
    *,
    section_lane: str,
    slot_kind: str,
    provider_payload: dict[str, Any],
    parse_model_json: ParseFn,
    normalize_parsed: NormalizeFn,
    artifact_dir: Path | None = None,
    run_id: str | None = None,
    temperature_bounds: tuple[float, float] = (0.0, 0.99),
    base_temperature: float | None = None,
    required_bullet_ids: tuple[str, ...] | None = None,
    targeting_context: dict[str, Any] | None = None,
    judge_mode: str = "blocked_if_unavailable",
    use_sc_path: bool | None = None,
    provider_profile: str | None = "external_claude",
) -> tuple[ProviderResult | None, str, dict[str, Any] | None, str, dict[str, Any]]:
    """
    Returns (provider_result, raw_output, parsed, parse_error, generation_meta).

    When SC path is active: raw_output is JSON of merged selection; meta includes pool receipt.
    """
    from apps_rg.runtime.providers.section_provider_call import call_section_model_provider
    from apps_rg.runtime.sections.section_generation import tag_reasoning_lane

    sc_on = bullet_lane_sc_enabled(section_lane) if use_sc_path is None else bool(use_sc_path)
    lane = str(section_lane or "").strip().lower()
    bullet_ids = required_bullet_ids or REQUIRED_BULLET_IDS.get(lane, ())

    if not sc_on:
        meta: dict[str, Any] = {"generation_mode": "singleton", "section_lane": section_lane}
        tagged = tag_reasoning_lane(dict(provider_payload), section_lane)
        result = call_section_model_provider(
            provider_profile,
            tagged,
            artifact_dir=artifact_dir,
            run_id=run_id,
        )
        raw = result.raw_model_output or ""
        parsed, err = (None, "")
        if result.runtime_generation_status == "REAL_LLM":
            parsed, err = parse_model_json(raw)
            if parsed is not None:
                parsed = normalize_parsed(parsed)
        else:
            err = result.exact_provider_error or "provider blocked"
        return result, raw, parsed, err, meta

    if lane == "competencies" and slot_kind == "competencies":
        return _generate_competencies_graph_pool_lane(
            provider_payload=provider_payload,
            parse_model_json=parse_model_json,
            normalize_parsed=normalize_parsed,
            artifact_dir=artifact_dir,
            run_id=run_id,
            temperature_bounds=temperature_bounds,
            base_temperature=base_temperature,
            targeting_context=targeting_context,
            judge_mode=judge_mode,
            provider_profile=provider_profile,
        )

    if is_employment_bullet_lane(lane) and slot_kind == "bullets" and bullet_ids:
        return _generate_employment_bullet_lane(
            section_lane=lane,
            provider_payload=provider_payload,
            parse_model_json=parse_model_json,
            normalize_parsed=normalize_parsed,
            artifact_dir=artifact_dir,
            run_id=run_id,
            temperature_bounds=temperature_bounds,
            base_temperature=base_temperature,
            required_bullet_ids=bullet_ids,
            targeting_context=targeting_context,
            judge_mode=judge_mode,
            provider_profile=provider_profile,
        )

    meta = {
        "generation_mode": "qwen_sc_claude_pool",
        "section_lane": section_lane,
    }
    paths, last_result = run_qwen_self_consistency_paths(
        section_lane=section_lane,
        provider_payload=provider_payload,
        parse_model_json=parse_model_json,
        artifact_dir=artifact_dir,
        run_id=run_id,
        temperature_bounds=temperature_bounds,
        base_temperature=base_temperature,
        provider_profile=provider_profile,
    )
    paths = _normalize_selector_paths(paths, normalize_parsed)
    completed = sum(1 for p in paths if p.parsed is not None)
    patch_receipt_samples_executed(
        last_result,
        paths_requested=self_consistency_path_count(section_lane),
        paths_completed=completed,
    )
    meta["self_consistency_paths_requested"] = self_consistency_path_count(section_lane)
    meta["self_consistency_paths_completed"] = completed

    pool: PoolSelectionResult = run_claude_bullet_pool_selection(
        section_id=section_lane,
        slot_kind="bullets" if slot_kind == "bullets" else "competencies",
        paths=paths,
        required_bullet_ids=required_bullet_ids,
        targeting_context=targeting_context,
        artifact_dir=artifact_dir,
        mode=judge_mode,
    )
    merged = normalize_parsed(dict(pool.merged_parsed))
    meta.update(
        {
            "selection_mode": pool.selection_mode,
            "source_path_by_slot": pool.source_path_by_slot,
            "claude_selection_count": len(pool.selections),
        }
    )
    if artifact_dir is not None:
        (artifact_dir / "bullet_pool_selection.json").write_text(
            json.dumps(
                {
                    "selection_mode": pool.selection_mode,
                    "selections": pool.selections,
                    "source_path_by_slot": pool.source_path_by_slot,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    raw = json.dumps(merged, sort_keys=True, separators=(",", ":"))
    return last_result, raw, merged, "", meta


__all__ = ["generate_bullet_lane_with_sc_and_claude"]
