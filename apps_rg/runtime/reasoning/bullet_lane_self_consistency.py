"""Execute self-consistency sample paths for bullet-pool lanes (apps_rg only)."""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Callable

from apps_rg.runtime.providers.anthropic_prompt_cache import (
    anthropic_prompt_cache_enabled,
    anthropic_prompt_cache_fanout_enabled,
    anthropic_prompt_cache_prewarm_enabled,
    anthropic_prompt_cache_telemetry_enabled,
)
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.providers.section_provider_call import call_section_model_provider
from apps_rg.runtime.sections.section_generation import tag_reasoning_lane
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    EMPLOYMENT_BULLET_LANES,
    adaptive_sc_enabled_for_lane,
    max_sc_path_count_for_lane,
    sc_path_count_for_lane,
)
from apps_rg.runtime.reasoning.section_reasoning_intensity import (
    profile_to_requested_kw,
    section_reasoning_profile,
)
from apps_rg.runtime.section_execution_plan import BULLET_LANES

ParseFn = Callable[[str], tuple[dict[str, Any] | None, str]]

BULLET_POOL_LANES: frozenset[str] = frozenset((*BULLET_LANES, "competencies"))
PARALLEL_EMPLOYMENT_BULLET_SC_LANES: frozenset[str] = frozenset(
    ("unify_bullets", "ibm_bullets")
)
_DISABLE_FLAGS = frozenset(("0", "false", "no", "off"))


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
    *,
    execution_mode: str = "serial",
    max_parallel: int = 1,
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
    rows_for_doc = sorted(
        [r for r in rows if isinstance(r, dict)],
        key=lambda r: int(r.get("path_index", 0)),
    )
    in_progress = sum(1 for r in rows_for_doc if r.get("completed_at") is None)
    doc = {
        "section_lane": section_lane,
        "path_count": len(rows_for_doc),
        "execution_mode": execution_mode,
        "max_parallel": max(1, int(max_parallel)),
        "paths_in_progress": in_progress,
        "paths_completed": len(rows_for_doc) - in_progress,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "paths": rows_for_doc,
    }
    try:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / PROGRESS_RECEIPT_FILENAME).write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError:  # guardian: allow-silent-swallow -- diagnostic progress board is best-effort, never fatal
        pass


def self_consistency_parallel_enabled(section_lane: str) -> bool:
    lane = str(section_lane or "").strip().lower()
    if lane == "competencies":
        flag = os.environ.get("APPS_RG_COMPETENCIES_SC_PARALLEL", "1").strip().lower()
        return flag not in _DISABLE_FLAGS
    if lane in PARALLEL_EMPLOYMENT_BULLET_SC_LANES:
        flag = os.environ.get("APPS_RG_EMPLOYMENT_BULLET_SC_PARALLEL", "1").strip().lower()
        return flag not in _DISABLE_FLAGS
    return False


def self_consistency_max_parallel(section_lane: str, path_count: int) -> int:
    lane = str(section_lane or "").strip().lower()
    if lane == "competencies":
        env_name = "APPS_RG_COMPETENCIES_SC_MAX_PARALLEL"
        default = 1
    elif lane in PARALLEL_EMPLOYMENT_BULLET_SC_LANES:
        env_name = "APPS_RG_EMPLOYMENT_BULLET_SC_MAX_PARALLEL"
        default = 2
    else:
        return 1
    raw = os.environ.get(env_name, "").strip()
    try:
        requested = int(raw) if raw else default
    except ValueError:
        requested = default
    return max(1, min(max(1, int(path_count)), requested))


def self_consistency_token_budget(
    section_lane: str,
    provider_payload: dict[str, Any],
) -> int | None:
    lane = str(section_lane or "").strip().lower()
    if lane == "competencies":
        from apps_rg.runtime.sections.competencies_lane_defaults import (
            competencies_self_consistency_output_tokens,
        )

        requested = provider_payload.get("max_tokens") or provider_payload.get("max_output_tokens")
        try:
            upper = int(requested) if requested is not None else None
        except (TypeError, ValueError):
            upper = None
        budget = competencies_self_consistency_output_tokens()
        return min(budget, upper) if upper and upper > 0 else budget
    return None


def competencies_sc_parallel_enabled(section_lane: str) -> bool:
    lane = str(section_lane or "").strip().lower()
    return lane == "competencies" and self_consistency_parallel_enabled(lane)


def competencies_sc_max_parallel(path_count: int) -> int:
    return self_consistency_max_parallel("competencies", path_count)


def _tagged_path_payload(
    provider_payload: dict[str, Any],
    *,
    section_lane: str,
    path_index: int,
    path_count: int,
    temperature: float,
) -> dict[str, Any]:
    tagged = tag_reasoning_lane(
        {
            **dict(provider_payload),
            "anthropic_workload_kind": "SELF_CONSISTENCY",
            "sc_path_index": int(path_index),
            "sc_path_count": int(path_count),
            "sc_temperature": float(temperature),
        },
        section_lane,
    )
    if section_lane == "unify_bullets":
        from apps_rg.runtime.sections.unify_bullets_graph_evidence import (
            append_unify_path_framing_to_messages,
        )

        msgs = list(tagged.get("messages") or [])
        return {
            **tagged,
            "messages": append_unify_path_framing_to_messages(
                msgs, path_index=path_index, temperature=temperature
            ),
        }
    if section_lane == "competencies":
        from apps_rg.runtime.sections.competency_capability_evidence import (
            append_competencies_path_diversity_to_messages,
        )

        msgs = list(tagged.get("messages") or [])
        return {
            **tagged,
            "messages": append_competencies_path_diversity_to_messages(
                msgs, path_index=path_index, temperature=temperature
            ),
        }
    return tagged


def _parse_sc_provider_result(
    result: ProviderResult,
    *,
    parse_model_json: ParseFn,
) -> tuple[str, dict[str, Any] | None, str]:
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
    return raw, parsed, parse_error


def _zero_output_provider_timeout(path: SelfConsistencyPath) -> bool:
    err = ""
    if path.provider_result is not None:
        err = str(path.provider_result.exact_provider_error or "")
    err = err or str(path.parse_error or "")
    err_l = err.lower()
    return (
        path.runtime_generation_status != "REAL_LLM"
        and not str(path.raw_output or "").strip()
        and "timeout" in err_l
        and ("chars_received=0" in err_l or "raw_output_chars" not in err_l)
    )


def _run_one_self_consistency_path(
    *,
    section_lane: str,
    provider_payload: dict[str, Any],
    parse_model_json: ParseFn,
    artifact_dir: Path | None,
    run_id: str | None,
    provider_profile: str | None,
    path_index: int,
    path_count: int,
    temperature: float,
    progress_rows: list[dict[str, Any]],
    progress_lock: Lock,
    execution_mode: str,
    max_parallel: int,
) -> SelfConsistencyPath:
    started_at = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()
    progress_row: dict[str, Any] = {
        "section_lane": section_lane,
        "path_index": path_index,
        "temperature": temperature,
        "started_at": started_at,
        "completed_at": None,
        "duration_s": None,
        "runtime_generation_status": "IN_PROGRESS",
        "raw_output_chars": 0,
        "parse_ok": None,
        "provider_error": None,
    }
    token_budget = self_consistency_token_budget(section_lane, provider_payload)
    if token_budget is not None:
        progress_row["token_budget"] = token_budget
    with progress_lock:
        progress_rows.append(progress_row)
        _flush_progress_receipt(
            artifact_dir,
            section_lane,
            progress_rows,
            execution_mode=execution_mode,
            max_parallel=max_parallel,
        )

    tagged = _tagged_path_payload(
        provider_payload,
        section_lane=section_lane,
        path_index=path_index,
        path_count=path_count,
        temperature=temperature,
    )
    result = call_section_model_provider(
        provider_profile,
        tagged,
        artifact_dir=artifact_dir,
        run_id=run_id,
        temperature_override=temperature,
        token_budget=token_budget,
    )
    raw, parsed, parse_error = _parse_sc_provider_result(
        result,
        parse_model_json=parse_model_json,
    )
    path = SelfConsistencyPath(
        path_index=path_index,
        temperature=temperature,
        runtime_generation_status=result.runtime_generation_status,
        raw_output=raw,
        parsed=parsed,
        parse_error=parse_error,
        provider_result=result,
    )
    with progress_lock:
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
        _flush_progress_receipt(
            artifact_dir,
            section_lane,
            progress_rows,
            execution_mode=execution_mode,
            max_parallel=max_parallel,
        )
    return path


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

    progress_lock = Lock()
    max_parallel = (
        self_consistency_max_parallel(section_lane, n_paths)
        if self_consistency_parallel_enabled(section_lane) and n_paths > 1
        else 1
    )
    execution_mode = "parallel" if max_parallel > 1 else "serial"
    thread_prefix = f"apps-rg-{str(section_lane or 'lane').replace('_', '-')}-sc"

    def _run(offset: int, temp: float) -> SelfConsistencyPath:
        return _run_one_self_consistency_path(
            section_lane=section_lane,
            provider_payload=provider_payload,
            parse_model_json=parse_model_json,
            artifact_dir=artifact_dir,
            run_id=run_id,
            provider_profile=provider_profile,
            path_index=path_index_start + offset,
            path_count=n_paths,
            temperature=temp,
            progress_rows=progress_rows,
            progress_lock=progress_lock,
            execution_mode=execution_mode,
            max_parallel=max_parallel,
        )

    prewarm_parallel = (
        execution_mode == "parallel"
        and n_paths > 1
        and anthropic_prompt_cache_enabled()
        and (anthropic_prompt_cache_prewarm_enabled() or anthropic_prompt_cache_fanout_enabled())
    )
    if prewarm_parallel:
        paths.append(_run(0, temps[0]))
        remaining = list(enumerate(temps))[1:]
        with ThreadPoolExecutor(
            max_workers=max_parallel,
            thread_name_prefix=thread_prefix,
        ) as executor:
            future_by_offset = {
                executor.submit(_run, offset, temp): offset
                for offset, temp in remaining
            }
            for future in as_completed(future_by_offset):
                paths.append(future.result())
    elif execution_mode == "parallel":
        with ThreadPoolExecutor(
            max_workers=max_parallel,
            thread_name_prefix=thread_prefix,
        ) as executor:
            future_by_offset = {
                executor.submit(_run, offset, temp): offset
                for offset, temp in enumerate(temps)
            }
            for future in as_completed(future_by_offset):
                paths.append(future.result())
    else:
        for offset, temp in enumerate(temps):
            path = _run(offset, temp)
            paths.append(path)
            if section_lane == "competencies" and _zero_output_provider_timeout(path):
                break

    paths.sort(key=lambda p: p.path_index)
    last_result = paths[-1].provider_result if paths else None

    if artifact_dir is not None:
        _write_paths_artifact(
            artifact_dir,
            section_lane,
            paths,
            append=append_artifacts,
            path_index_start=path_index_start,
            execution_mode=execution_mode,
            max_parallel=max_parallel,
        )

    return paths, last_result


def _write_paths_artifact(
    artifact_dir: Path,
    section_lane: str,
    paths: list[SelfConsistencyPath],
    *,
    append: bool = False,
    path_index_start: int = 0,
    execution_mode: str = "serial",
    max_parallel: int = 1,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)

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

    if section_lane in EMPLOYMENT_BULLET_LANES:
        generation_mode = (
            f"provider_employment_bullet_pool_adaptive_"
            f"{sc_path_count_for_lane(section_lane)}_{max_sc_path_count_for_lane(section_lane)}"
            if adaptive_sc_enabled_for_lane(section_lane)
            else f"provider_employment_bullet_pool_{sc_path_count_for_lane(section_lane)}"
        )
    else:
        generation_mode = "provider_self_consistency"

    doc = {
        "section_lane": section_lane,
        "path_count": len(merged_entries),
        "batch_path_count": len(paths),
        "execution_mode": execution_mode,
        "max_parallel": max(1, int(max_parallel)),
        "generation_mode": generation_mode,
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
    _write_lane_cache_summary(artifact_dir, section_lane, paths)


def _receipt_int(receipt: dict[str, Any], key: str) -> int:
    try:
        return int(receipt.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def _write_lane_cache_summary(
    artifact_dir: Path,
    section_lane: str,
    paths: list[SelfConsistencyPath],
) -> None:
    if not (anthropic_prompt_cache_enabled() or anthropic_prompt_cache_telemetry_enabled()):
        return
    receipts: list[dict[str, Any]] = []
    for path in paths:
        result = path.provider_result
        receipt = getattr(result, "prompt_cache_receipt", None) if result is not None else None
        if isinstance(receipt, dict):
            receipts.append({"path_index": path.path_index, **receipt})
    if not receipts:
        return
    stable_counts: dict[str, int] = {}
    for receipt in receipts:
        stable = str(receipt.get("stable_prefix_hash") or "")
        if stable:
            stable_counts[stable] = stable_counts.get(stable, 0) + 1
    warnings: list[dict[str, Any]] = []
    for stable_hash, count in stable_counts.items():
        matching = [r for r in receipts if r.get("stable_prefix_hash") == stable_hash]
        creation = sum(_receipt_int(r, "cache_creation_input_tokens") for r in matching)
        reads = sum(_receipt_int(r, "cache_read_input_tokens") for r in matching)
        if count >= 3 and creation > 0 and reads == 0:
            warnings.append(
                {
                    "warning": "cache_miss_repeated_prefix_warning",
                    "stable_prefix_hash": stable_hash,
                    "repeated_count": count,
                    "cache_creation_input_tokens": creation,
                    "cache_read_input_tokens": reads,
                }
            )
    creation_total = sum(_receipt_int(r, "cache_creation_input_tokens") for r in receipts)
    read_total = sum(_receipt_int(r, "cache_read_input_tokens") for r in receipts)
    denom = creation_total + read_total
    summary = {
        "schema": "apps_rg_lane_cache_summary_v1",
        "section_lane": section_lane,
        "cache_enabled": anthropic_prompt_cache_enabled(),
        "path_count": len(paths),
        "receipt_count": len(receipts),
        "cache_creation_input_tokens": creation_total,
        "cache_read_input_tokens": read_total,
        "cache_hit_ratio": round(float(read_total) / float(denom), 6) if denom else None,
        "stable_prefix_hashes": sorted(stable_counts),
        "warnings": warnings,
        "receipts": receipts,
    }
    (artifact_dir / "lane_cache_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
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
        row["gap_notes"] = "multi_sample_PROVIDER_MODEL_paths_executed"
        break


__all__ = [
    "BULLET_POOL_LANES",
    "EMPLOYMENT_BULLET_LANES",
    "PARALLEL_EMPLOYMENT_BULLET_SC_LANES",
    "PROGRESS_RECEIPT_FILENAME",
    "SelfConsistencyPath",
    "bullet_lane_sc_enabled",
    "competencies_sc_max_parallel",
    "competencies_sc_parallel_enabled",
    "patch_receipt_samples_executed",
    "run_provider_self_consistency_paths",
    "self_consistency_path_count",
    "self_consistency_max_parallel",
    "self_consistency_token_budget",
    "self_consistency_parallel_enabled",
    "temperature_ladder",
]
