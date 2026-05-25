"""Execute Qwen self-consistency sample paths for bullet-pool lanes (apps_rg only)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    EMPLOYMENT_BULLET_LANES,
    sc_path_count_for_lane,
)
from apps_rg.runtime.reasoning.section_reasoning_intensity import (
    profile_to_requested_kw,
    section_reasoning_profile,
)

ParseFn = Callable[[str], tuple[dict[str, Any] | None, str]]

BULLET_POOL_LANES: frozenset[str] = frozenset({"unify_bullets", "ibm_bullets", "competencies"})


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


def run_qwen_self_consistency_paths(
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
) -> tuple[list[SelfConsistencyPath], ProviderResult | None]:
    """Run N Qwen completions at staggered temperatures; return all paths + last provider result."""
    prof_kw = profile_to_requested_kw(section_reasoning_profile(section_lane))
    base = float(base_temperature if base_temperature is not None else prof_kw["temperature"])
    n_paths = path_count if path_count is not None else self_consistency_path_count(section_lane)
    temps = temperature_ladder(base, n_paths, bounds=temperature_bounds)

    paths: list[SelfConsistencyPath] = []
    last_result: ProviderResult | None = None

    for offset, temp in enumerate(temps):
        idx = path_index_start + offset
        tagged = tag_reasoning_lane(dict(provider_payload), section_lane)
        result = call_qwen_vllm(
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
            f"qwen_employment_bullet_pool_{SC_PATH_COUNT_BY_LANE.get(section_lane, 'n')}"
            if section_lane in EMPLOYMENT_BULLET_LANES
            else "qwen_self_consistency"
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
    "SelfConsistencyPath",
    "bullet_lane_sc_enabled",
    "patch_receipt_samples_executed",
    "run_qwen_self_consistency_paths",
    "self_consistency_path_count",
    "temperature_ladder",
]
