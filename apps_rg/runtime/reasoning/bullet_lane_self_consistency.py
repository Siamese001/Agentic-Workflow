"""Execute self-consistency sample paths for bullet-pool lanes (apps_rg only)."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.providers.section_provider_call import call_section_model_provider
from apps_rg.runtime.sections.section_generation import tag_reasoning_lane
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    EMPLOYMENT_BULLET_LANES,
    sc_path_count_for_lane,
)
from apps_rg.runtime.reasoning.section_reasoning_intensity import (
    profile_to_requested_kw,
    section_reasoning_profile,
)
from apps_rg.runtime.section_execution_plan import BULLET_LANES

ParseFn = Callable[[str], tuple[dict[str, Any] | None, str]]

BULLET_POOL_LANES: frozenset[str] = frozenset((*BULLET_LANES, "competencies"))


def bullet_lane_sc_enabled(section_lane: str) -> bool:
    lane = str(section_lane or "").strip().lower()
    if lane not in BULLET_POOL_LANES:
        return False
    flag = os.environ.get("APPS_RG_BULLET_SC_DISABLE", "").strip().lower()
    return flag not in ("1", "true", "yes")


def self_consistency_path_count(section_lane: str) -> int:
    return sc_path_count_for_lane(section_lane)


def _clamp_temperature(value: float, bounds: tuple[float, float]) -> float:
    low, high = bounds
    return max(low, min(high, value))


def temperature_ladder(
    base_temperature: float,
    path_count: int,
    *,
    bounds: tuple[float, float],
) -> list[float]:
    """Spread ``path_count`` samples across a bounded band (supports 15 employment paths)."""
    n = max(1, path_count)
    if n == 1:
        return [_clamp_temperature(base_temperature, bounds)]
    low_b, high_b = bounds
    half_span = min(0.07, (high_b - base_temperature), (base_temperature - low_b))
    start = base_temperature - half_span
    end = base_temperature + half_span
    if n == 2:
        return [_clamp_temperature(start, bounds), _clamp_temperature(end, bounds)]
    step = (end - start) / float(n - 1)
    return [_clamp_temperature(start + step * i, bounds) for i in range(n)]


@dataclass
class SelfConsistencyPath:
    path_index: int
    temperature: float
    runtime_generation_status: str
    raw_output: str
    parsed: dict[str, Any] | None
    parse_error: str
    provider_result: ProviderResult | None


PROGRESS_RECEIPT_FILENAME = "self_consistency_progress.json"


def _flush_progress_receipt(
    artifact_dir: Path | None,
    section_lane: str,
    rows: list[dict[str, Any]],
) -> None:
    """Flush the live per-path progress board to disk after EVERY path (not just the batch).

    W4: ``self_consistency_paths.json`` is written only after the whole batch finishes, so a long
    competencies pool run looks dead until the last path lands. This companion artifact is
    rewritten after each path starts AND after each completes, so a stuck-looking run reveals
    exactly which ``path_index`` is active / last completed without waiting for the batch.
    Best-effort: a write failure never aborts generation.
    """
    if artifact_dir is None:
        return
    in_progress = sum(1 for r in rows if r.get("completed_at") is None)
    doc = {
        "section_lane": section_lane,
        "path_count": len(rows),
        "paths_in_progress": in_progress,
        "paths_completed": len(rows) - in_progress,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "paths": rows,
    }
    try:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / PROGRESS_RECEIPT_FILENAME).write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError:  # guardian: allow-silent-swallow -- diagnostic progress board is best-effort, never fatal
        pass


def run_provider_self_consistency_paths(
    *,
    section_lane: str,
    provider_payload: dict[str, Any],
    parse_model_json: ParseFn,
    artifact_dir: Path | None = None,
    run_id: str | None = None,
    temperature_bounds: tuple[float, float] = (0.0, 0.99),
    base_temperature: float | None = None,
    path_count: int | None = None,
    path_index_start: int = 0,
    append_artifacts: bool = False,
    provider_profile: str | None = "external_claude",
) -> tuple[list[SelfConsistencyPath], ProviderResult | None]:
    """Run N completions at staggered temperatures; return all paths + last provider result."""
    prof_kw = profile_to_requested_kw(section_reasoning_profile(section_lane))
    base = float(base_temperature if base_temperature is not None else prof_kw["temperature"])
    n_paths = path_count if path_count is not None else self_consistency_path_count(section_lane)
    temps = temperature_ladder(base, n_paths, bounds=temperature_bounds)

    paths: list[SelfConsistencyPath] = []
    last_result: ProviderResult | None = None

    # W4: live per-path progress board. On append/regen batches, carry prior rows forward so the
    # board shows the full accumulated pool, not just the current batch.
    progress_rows: list[dict[str, Any]] = []
    if artifact_dir is not None and (append_artifacts or path_index_start > 0):
        prior_path = artifact_dir / PROGRESS_RECEIPT_FILENAME
        if prior_path.is_file():
            try:
                prior_doc = json.loads(prior_path.read_text(encoding="utf-8"))
                if isinstance(prior_doc, dict) and isinstance(prior_doc.get("paths"), list):
                    progress_rows = [r for r in prior_doc["paths"] if isinstance(r, dict)]
            except (json.JSONDecodeError, OSError):
                progress_rows = []

    for offset, temp in enumerate(temps):
        idx = path_index_start + offset
        # Append a "started" row BEFORE the provider call and flush — a stuck path is now visible.
        started_at = datetime.now(timezone.utc).isoformat()
        t0 = time.monotonic()
        progress_row: dict[str, Any] = {
            "section_lane": section_lane,
            "path_index": idx,
            "temperature": temp,
            "started_at": started_at,
            "completed_at": None,
            "duration_s": None,
            "runtime_generation_status": "IN_PROGRESS",
            "raw_output_chars": 0,
            "parse_ok": None,
            "provider_error": None,
        }
        progress_rows.append(progress_row)
        _flush_progress_receipt(artifact_dir, section_lane, progress_rows)

        tagged = tag_reasoning_lane(dict(provider_payload), section_lane)
        if section_lane == "unify_bullets":
            from apps_rg.runtime.sections.unify_bullets_graph_evidence import (
                append_unify_path_framing_to_messages,
            )

            msgs = list(tagged.get("messages") or [])
            tagged = {
                **tagged,
                "messages": append_unify_path_framing_to_messages(
                    msgs, path_index=idx, temperature=temp
                ),
            }
        result = call_section_model_provider(
            provider_profile,
            tagged,
            artifact_dir=artifact_dir,
            run_id=run_id,
            temperature_override=temp,
        )
        last_result = result
        raw = result.raw_model_output or ""
        parsed: dict[str, Any] | None = None
        parse_error = ""
        if result.runtime_generation_status == "REAL_LLM":
            parsed, parse_error = parse_model_json(raw)
            if parsed is not None:
                from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
                    strip_employment_bullet_intensity_model,
                )

                parsed = strip_employment_bullet_intensity_model(parsed)
        elif result.runtime_generation_status not in ("REAL_LLM",):
            parse_error = result.exact_provider_error or "provider blocked"
        paths.append(
            SelfConsistencyPath(
                path_index=idx,
                temperature=temp,
                runtime_generation_status=result.runtime_generation_status,
                raw_output=raw,
                parsed=parsed,
                parse_error=parse_error,
                provider_result=result,
            )
        )
        # Update the row with the completed outcome and flush — last-completed is now observable.
        progress_row.update(
            {
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "duration_s": round(time.monotonic() - t0, 4),
                "runtime_generation_status": result.runtime_generation_status,
                "raw_output_chars": len(raw),
                "parse_ok": parsed is not None,
                "provider_error": (result.exact_provider_error or None)
                if result.runtime_generation_status != "REAL_LLM"
                else None,
            }
        )
        _flush_progress_receipt(artifact_dir, section_lane, progress_rows)

    if artifact_dir is not None:
        _write_paths_artifact(
            artifact_dir,
            section_lane,
            paths,
            append=append_artifacts,
            path_index_start=path_index_start,
        )

    return paths, last_result


def _write_paths_artifact(
    artifact_dir: Path,
    section_lane: str,
    paths: list[SelfConsistencyPath],
    *,
    append: bool = False,
    path_index_start: int = 0,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    from apps_rg.runtime.reasoning.employment_bullet_pool import SC_PATH_COUNT_BY_LANE

    new_entries = [
        {
            "path_index": p.path_index,
            "temperature": p.temperature,
            "runtime_generation_status": p.runtime_generation_status,
            "parse_error": p.parse_error,
            "parsed_ok": p.parsed is not None,
            "raw_output_chars": len(p.raw_output or ""),
        }
        for p in paths
    ]
    if append and (artifact_dir / "self_consistency_paths.json").is_file():
        try:
            prior = json.loads((artifact_dir / "self_consistency_paths.json").read_text(encoding="utf-8"))
            merged_entries = list(prior.get("paths") or []) + new_entries
        except (json.JSONDecodeError, OSError):
            merged_entries = new_entries
    else:
        merged_entries = new_entries

    doc = {
        "section_lane": section_lane,
        "path_count": len(merged_entries),
        "generation_mode": (
            f"provider_employment_bullet_pool_{SC_PATH_COUNT_BY_LANE.get(section_lane, 'n')}"
            if section_lane in EMPLOYMENT_BULLET_LANES
            else "provider_self_consistency"
        ),
        "paths": merged_entries,
    }
    (artifact_dir / "self_consistency_paths.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for p in paths:
        (artifact_dir / f"self_consistency_path_{p.path_index}_raw.txt").write_text(
            p.raw_output or "",
            encoding="utf-8",
        )
        if p.parsed is not None:
            (artifact_dir / f"self_consistency_path_{p.path_index}_parsed.json").write_text(
                json.dumps(p.parsed, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )


def patch_receipt_samples_executed(
    provider_result: ProviderResult | None,
    *,
    paths_requested: int,
    paths_completed: int,
) -> None:
    """Honest receipt: orchestration self-consistency ran on multi-call runner."""
    if provider_result is None:
        return
    rec = provider_result.reasoning_execution_receipt
    if not isinstance(rec, dict):
        return
    ledger = rec.get("ledger")
    if not isinstance(ledger, list):
        return
    for row in ledger:
        if not isinstance(row, dict):
            continue
        if row.get("control_name") != "self_consistency_samples":
            continue
        ref = row.get("proved_reference")
        blob: dict[str, Any] = {}
        if isinstance(ref, str) and ref.strip().startswith("{"):
            try:
                blob = json.loads(ref)
            except json.JSONDecodeError:
                blob = {}
        blob.update(
            {
                "orch_runner_mode": "bullet_lane_multi_sample_runner",
                "executed_observed": True,
                "samples_requested": max(1, paths_requested),
                "samples_completed": max(0, paths_completed),
            }
        )
        row["proved_reference"] = json.dumps(blob)
        row["receipt_state"] = "APPLIED"
        row["gap_notes"] = "multi_sample_qwen_paths_executed"
        break


__all__ = [
    "BULLET_POOL_LANES",
    "EMPLOYMENT_BULLET_LANES",
    "PROGRESS_RECEIPT_FILENAME",
    "SelfConsistencyPath",
    "bullet_lane_sc_enabled",
    "patch_receipt_samples_executed",
    "run_provider_self_consistency_paths",
    "self_consistency_path_count",
    "temperature_ladder",
]
