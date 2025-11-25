"""
Batch processing interface for résumé analysis across multiple job applications and candidates.

Improves résumé processing efficiency by coordinating parallel analysis workflows with consistent quality and telemetry.
"""

from __future__ import annotations

import argparse
import dataclasses
from dataclasses import dataclass, asdict
import json
import os
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, cast

from cli.main_v10_10 import (
    run_workflow,
    RRFStrategy,
    TelemetryRoutingMode,
)


# ---------------------------------------------------------------------------
# Dataclasses for batch execution
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _GlobalDefaults:
    execution_profile_name: str
    routing_policy_name: str
    sandbox_profile_name: str
    meta_profile_name: str
    hyde_enabled: bool
    rrf_strategy: RRFStrategy
    rrf_weights: Optional[Mapping[str, float]]
    council_size: int
    correction_loop_max_iterations: int
    telemetry_routing_mode: TelemetryRoutingMode


@dataclass(frozen=True)
class BatchJobConfig:
    """
    Immutable configuration for a single batch job.

    All Phase‑3 knobs are fully resolved per job so that downstream execution
    can be done deterministically and independently.
    """

    batch_id: str
    job_index: int
    job_id: str
    row: Mapping[str, Any]
    user_request: Any
    execution_profile_name: str
    routing_policy_name: str
    sandbox_profile_name: str
    meta_profile_name: str
    hyde_enabled: bool
    rrf_strategy: RRFStrategy
    rrf_weights: Optional[Mapping[str, float]]
    council_size: int
    correction_loop_max_iterations: int
    telemetry_routing_mode: TelemetryRoutingMode
    workflow_id: str


@dataclass
class BatchJobResult:
    """
    Result for a single batch job.

    The `output` field is whatever run_workflow returns (ideally a
    models.WorkflowOutput), and is normalized for JSON when writing JSONL.
    """

    job_config: BatchJobConfig
    success: bool
    output: Any
    error: Optional[str]
    duration_sec: float


@dataclass
class BatchTelemetrySummary:
    """
    Aggregate telemetry summary for a batch (G15–G18).

    This captures simple but useful metrics that can be used for monitoring,
    regression testing, and cost / performance analyses.
    """

    batch_id: str
    total_jobs: int
    success_count: int
    failure_count: int
    total_duration_sec: float
    avg_job_duration_sec: float
    max_job_duration_sec: float
    min_job_duration_sec: float
    golden_mode: bool
    max_workers: int


# ---------------------------------------------------------------------------
# Helpers: parsing, normalization, utility functions
# ---------------------------------------------------------------------------


def _parse_rrf_weights(pairs: Optional[Sequence[str]]) -> Optional[Dict[str, float]]:
    if not pairs:
        return None
    weights: Dict[str, float] = {}
    for item in pairs:
        if "=" not in item:
            raise ValueError(f"Invalid --rrf-weight spec (expected KEY=VALUE): {item!r}")
        key, value_str = item.split("=", 1)
        key = key.strip()
        value_str = value_str.strip()
        if not key:
            raise ValueError(f"Invalid --rrf-weight key in: {item!r}")
        try:
            value = float(value_str)
        except ValueError as exc:
            raise ValueError(f"Invalid --rrf-weight numeric value in: {item!r}") from exc
        weights[key] = value
    return weights or None


def _normalize_rrf_weights(
    value: Optional[Mapping[str, Any]],
    default: Optional[Mapping[str, float]],
) -> Optional[Dict[str, float]]:
    if value is None:
        if default is None:
            return None
        return {str(k): float(v) for k, v in default.items()}
    out: Dict[str, float] = {}
    for k, v in value.items():
        try:
            out[str(k)] = float(v)
        except (TypeError, ValueError):
            continue
    if not out:
        if default is None:
            return None
        return {str(k): float(v) for k, v in default.items()}
    return out


def _enum_from_row(
    row: Mapping[str, Any],
    key: str,
    enum_cls: Any,
    default_value: Any,
) -> Any:
    if key not in row:
        return default_value
    raw = row[key]
    if isinstance(raw, enum_cls):
        return raw
    try:
        return enum_cls(raw)
    except Exception:
        return default_value


def _bool_from_row(row: Mapping[str, Any], key: str, default: bool) -> bool:
    if key not in row:
        return default
    val = row[key]
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        low = val.strip().lower()
        if low in ("1", "true", "yes", "y", "on"):
            return True
        if low in ("0", "false", "no", "n", "off"):
            return False
    return default


def _extract_user_request(row: Mapping[str, Any]) -> Any:
    """
    Derive the user_request payload from a JSONL row.

    Priority:
    - row["user_request"]
    - row["prompt"]
    - row["input"]
    - otherwise: the full row object itself.
    """
    if "user_request" in row:
        return row["user_request"]
    if "prompt" in row:
        return row["prompt"]
    if "input" in row:
        return row["input"]
    return row


def _clamp_max_workers(requested: int, golden_mode: bool) -> int:
    """
    Enforce safe concurrency limits and deterministic golden mode behavior.

    - If golden_mode is True, we always return 1 worker.
    - Otherwise, we clamp requested to a reasonable bound based on CPU.
    """
    if golden_mode:
        return 1
    if requested <= 0:
        requested = 4
    cpu_count = os.cpu_count() or 4
    auto_cap = min(cpu_count * 4, 32)
    return max(1, min(requested, auto_cap))


def _read_jsonl(path: str) -> List[Mapping[str, Any]]:
    """
    Read a JSONL file or stdin ("-") into a list of dict rows.

    Non-mapping rows are wrapped as {"value": row} to keep a stable schema.
    Lines starting with "#" are treated as comments and ignored.
    """
    if path in ("-", ""):
        stream = sys.stdin
        close_stream = False
    else:
        stream = open(path, "r", encoding="utf-8")
        close_stream = True

    rows: List[Mapping[str, Any]] = []
    try:
        for line_number, line in enumerate(stream, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc
            if not isinstance(obj, Mapping):
                obj = {"value": obj}
            rows.append(obj)
    finally:
        if close_stream:
            stream.close()
    return rows


def _write_jsonl(path: str, rows: Iterable[Mapping[str, Any]]) -> None:
    """
    Write an iterable of JSON-serializable rows to JSONL, using deterministic
    formatting (sorted keys, compact separators).
    """
    if path in ("-", ""):
        out = sys.stdout
        close_stream = False
    else:
        out = open(path, "w", encoding="utf-8")
        close_stream = True

    try:
        for row in rows:
            json.dump(row, out, separators=(",", ":"), sort_keys=True)
            out.write("\n")
        out.flush()
    finally:
        if close_stream:
            out.close()


def _write_json(path: Optional[str], obj: Mapping[str, Any]) -> None:
    """
    Write a single JSON object to a path. If path is None, do nothing.
    If path is "-", write to stdout.
    """
    if path is None:
        return

    if path == "-":
        out = sys.stdout
        close_stream = False
    else:
        out = open(path, "w", encoding="utf-8")
        close_stream = True

    try:
        json.dump(obj, out, indent=2, sort_keys=True)
        out.write("\n")
        out.flush()
    finally:
        if close_stream:
            out.close()


def _normalize_output(output: Any) -> Any:
    """
    Convert a WorkflowOutput (or arbitrary Python object) into a JSON-safe
    structure for JSONL emission.

    The preference order:
    - output.to_dict() if available
    - dataclasses.asdict(output) if dataclass
    - mapping / sequence / primitive used as-is
    - fallback to repr(output)
    """
    if output is None:
        return None

    to_dict = getattr(output, "to_dict", None)
    if callable(to_dict):
        try:
            return to_dict()
        except Exception:
            pass

    if dataclasses.is_dataclass(output):
        try:
            return asdict(output)
        except Exception:
            pass

    if isinstance(output, (str, int, float, bool)) or output is None:
        return output

    if isinstance(output, Mapping):
        return dict(output)

    if isinstance(output, Sequence) and not isinstance(output, (bytes, bytearray)):
        return list(output)

    return repr(output)


# ---------------------------------------------------------------------------
# Job config construction and execution
# ---------------------------------------------------------------------------


def _build_job_config(
    *,
    batch_id: str,
    job_index: int,
    row_raw: Mapping[str, Any],
    defaults: _GlobalDefaults,
) -> BatchJobConfig:
    """
    Construct per-job configuration, resolving overrides from the JSONL row
    on top of the global defaults (G1–G3, G11–G14).
    """
    # Ensure we have a plain dict for stable behavior.
    row: Dict[str, Any] = dict(row_raw)

    job_id = str(row.get("job_id") or row.get("id") or job_index)

    user_request = _extract_user_request(row)

    execution_profile_name = str(
        row.get("execution_profile_name", defaults.execution_profile_name)
    )
    routing_policy_name = str(
        row.get("routing_policy_name", defaults.routing_policy_name)
    )
    sandbox_profile_name = str(
        row.get("sandbox_profile_name", defaults.sandbox_profile_name)
    )
    meta_profile_name = str(
        row.get("meta_profile_name", defaults.meta_profile_name)
    )

    hyde_enabled = _bool_from_row(row, "hyde_enabled", defaults.hyde_enabled)

    rrf_strategy = _enum_from_row(
        row,
        "rrf_strategy",
        RRFStrategy,
        defaults.rrf_strategy,
    )

    rrf_weights_raw = row.get("rrf_weights")
    rrf_weights = _normalize_rrf_weights(
        rrf_weights_raw if isinstance(rrf_weights_raw, Mapping) else None,
        defaults.rrf_weights,
    )

    council_size = int(row.get("council_size", defaults.council_size))
    correction_loop_max_iterations = int(
        row.get(
            "correction_loop_max_iterations",
            defaults.correction_loop_max_iterations,
        )
    )

    telemetry_routing_mode = _enum_from_row(
        row,
        "telemetry_routing_mode",
        TelemetryRoutingMode,
        defaults.telemetry_routing_mode,
    )

    workflow_id = str(row.get("workflow_id") or f"{batch_id}:{job_id}")

    return BatchJobConfig(
        batch_id=batch_id,
        job_index=job_index,
        job_id=job_id,
        row=row,
        user_request=user_request,
        execution_profile_name=execution_profile_name,
        routing_policy_name=routing_policy_name,
        sandbox_profile_name=sandbox_profile_name,
        meta_profile_name=meta_profile_name,
        hyde_enabled=hyde_enabled,
        rrf_strategy=rrf_strategy,
        rrf_weights=rrf_weights,
        council_size=council_size,
        correction_loop_max_iterations=correction_loop_max_iterations,
        telemetry_routing_mode=telemetry_routing_mode,
        workflow_id=workflow_id,
    )


def _execute_job(
    job_config: BatchJobConfig,
    *,
    golden_mode: bool,
) -> BatchJobResult:
    """
    Execute a single job via main_v10_10.run_workflow.

    The ExecutionContext is constructed inside run_workflow; we attach
    per-job metadata (batch_id, job_id, etc.) via extra_workflow_metadata.
    """
    start = time.monotonic()
    try:
        extra_metadata = {
            "batch_id": job_config.batch_id,
            "batch_job_index": job_config.job_index,
            "batch_job_id": job_config.job_id,
            "golden_mode": golden_mode,
        }
        output = run_workflow(
            user_request=job_config.user_request,
            execution_profile_name=job_config.execution_profile_name,
            routing_policy_name=job_config.routing_policy_name,
            sandbox_profile_name=job_config.sandbox_profile_name,
            meta_profile_name=job_config.meta_profile_name,
            hyde_enabled=job_config.hyde_enabled,
            rrf_strategy=job_config.rrf_strategy,
            rrf_weights=job_config.rrf_weights,
            council_size=job_config.council_size,
            correction_loop_max_iterations=job_config.correction_loop_max_iterations,
            telemetry_routing_mode=job_config.telemetry_routing_mode,
            workflow_id=job_config.workflow_id,
            extra_workflow_metadata=extra_metadata,
        )
        duration_sec = time.monotonic() - start
        return BatchJobResult(
            job_config=job_config,
            success=True,
            output=output,
            error=None,
            duration_sec=duration_sec,
        )
    except Exception as exc:
        duration_sec = time.monotonic() - start
        return BatchJobResult(
            job_config=job_config,
            success=False,
            output=None,
            error=str(exc),
            duration_sec=duration_sec,
        )


def _build_batch_summary(
    *,
    batch_id: str,
    results: Sequence[BatchJobResult],
    total_duration_sec: float,
    max_workers: int,
    golden_mode: bool,
) -> BatchTelemetrySummary:
    """
    Compute aggregate batch metrics (G15–G18).
    """
    total_jobs = len(results)
    success_count = sum(1 for r in results if r.success)
    failure_count = total_jobs - success_count

    if total_jobs > 0:
        durations = [r.duration_sec for r in results]
        avg_job_duration_sec = sum(durations) / total_jobs
        max_job_duration_sec = max(durations)
        min_job_duration_sec = min(durations)
    else:
        avg_job_duration_sec = 0.0
        max_job_duration_sec = 0.0
        min_job_duration_sec = 0.0

    return BatchTelemetrySummary(
        batch_id=batch_id,
        total_jobs=total_jobs,
        success_count=success_count,
        failure_count=failure_count,
        total_duration_sec=total_duration_sec,
        avg_job_duration_sec=avg_job_duration_sec,
        max_job_duration_sec=max_job_duration_sec,
        min_job_duration_sec=min_job_duration_sec,
        golden_mode=golden_mode,
        max_workers=max_workers,
    )


# ---------------------------------------------------------------------------
# Public programmatic API
# ---------------------------------------------------------------------------


def run_batch(
    jobs: Sequence[Mapping[str, Any]],
    *,
    # Profile defaults
    execution_profile_name: str = "default",
    routing_policy_name: str = "default",
    sandbox_profile_name: str = "default",
    meta_profile_name: str = "default",
    # Phase‑3 knobs defaults
    hyde_enabled: bool = False,
    rrf_strategy: RRFStrategy = RRFStrategy.SIMPLE,
    rrf_weights: Optional[Mapping[str, float]] = None,
    council_size: int = 1,
    correction_loop_max_iterations: int = 2,
    telemetry_routing_mode: TelemetryRoutingMode = TelemetryRoutingMode.LOG_ONLY,
    # Batch execution behavior
    max_workers: int = 4,
    golden_mode: bool = False,
    base_workflow_id: Optional[str] = None,
) -> Tuple[Sequence[BatchJobResult], BatchTelemetrySummary]:
    """
    Run a batch of jobs through the L1→L5 workflow via main_v10_10.run_workflow.

    Parameters
    ----------
    jobs:
        A sequence of JSON-like mapping rows representing jobs. Each row may
        override Phase‑3 knobs and profiles using the same field names used
        by main_v10_10.run_workflow (e.g. "execution_profile_name", etc.).

    execution_profile_name, routing_policy_name, sandbox_profile_name,
    meta_profile_name:
        Global defaults for configuration profiles (G1, G2).

    hyde_enabled, rrf_strategy, rrf_weights, council_size,
    correction_loop_max_iterations, telemetry_routing_mode:
        Global defaults for Phase‑3 knobs (G3–G10, G11–G14, G15–G18).

    max_workers:
        Upper bound on parallel workers (ThreadPoolExecutor). Actual worker
        count is clamped for safety via _clamp_max_workers.

    golden_mode:
        If True, concurrency is forced to 1 to maximize determinism, and a
        "golden_mode" flag is propagated in workflow metadata.

    base_workflow_id:
        Optional base ID used to derive per-job workflow IDs. If omitted,
        a UUID4 is used as the batch_id and per-job workflow IDs are derived
        from it.
    """
    batch_id = base_workflow_id or str(uuid.uuid4())

    defaults = _GlobalDefaults(
        execution_profile_name=execution_profile_name,
        routing_policy_name=routing_policy_name,
        sandbox_profile_name=sandbox_profile_name,
        meta_profile_name=meta_profile_name,
        hyde_enabled=hyde_enabled,
        rrf_strategy=rrf_strategy,
        rrf_weights=(
            {str(k): float(v) for k, v in rrf_weights.items()}
            if rrf_weights is not None
            else None
        ),
        council_size=council_size,
        correction_loop_max_iterations=correction_loop_max_iterations,
        telemetry_routing_mode=telemetry_routing_mode,
    )

    if not jobs:
        summary = BatchTelemetrySummary(
            batch_id=batch_id,
            total_jobs=0,
            success_count=0,
            failure_count=0,
            total_duration_sec=0.0,
            avg_job_duration_sec=0.0,
            max_job_duration_sec=0.0,
            min_job_duration_sec=0.0,
            golden_mode=golden_mode,
            max_workers=_clamp_max_workers(max_workers, golden_mode),
        )
        return [], summary

    resolved_workers = _clamp_max_workers(max_workers, golden_mode)

    # Build job configs in deterministic order.
    job_configs: List[BatchJobConfig] = [
        _build_job_config(
            batch_id=batch_id,
            job_index=index,
            row_raw=row,
            defaults=defaults,
        )
        for index, row in enumerate(jobs)
    ]

    batch_start = time.monotonic()

    # Execute jobs (possibly in parallel) but preserve deterministic ordering.
    results: List[Optional[BatchJobResult]] = [None] * len(job_configs)

    if resolved_workers == 1:
        for cfg in job_configs:
            res = _execute_job(cfg, golden_mode=golden_mode)
            results[cfg.job_index] = res
    else:
        with ThreadPoolExecutor(max_workers=resolved_workers) as executor:
            future_to_index = {
                executor.submit(_execute_job, cfg, golden_mode=golden_mode): cfg.job_index
                for cfg in job_configs
            }
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    res = future.result()
                except Exception as exc:
                    cfg = job_configs[idx]
                    res = BatchJobResult(
                        job_config=cfg,
                        success=False,
                        output=None,
                        error=f"Unhandled exception in worker: {exc}",
                        duration_sec=0.0,
                    )
                results[idx] = res

    batch_end = time.monotonic()
    concrete_results: List[BatchJobResult] = [
        cast(BatchJobResult, r) for r in results
    ]

    summary = _build_batch_summary(
        batch_id=batch_id,
        results=concrete_results,
        total_duration_sec=batch_end - batch_start,
        max_workers=resolved_workers,
        golden_mode=golden_mode,
    )

    return concrete_results, summary


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a batch of v10_10 workflows through the L1–L5 pipeline.",
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help='Input JSONL path or "-" for stdin.',
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help='Output JSONL path or "-" for stdout.',
    )
    parser.add_argument(
        "--summary-output",
        default=None,
        help=(
            "Optional path to write a batch summary JSON. "
            'If "-", writes to stdout.'
        ),
    )

    # Profile selection defaults
    parser.add_argument(
        "--execution-profile",
        default="default",
        help="ExecutionProfile name (default: %(default)s).",
    )
    parser.add_argument(
        "--routing-policy",
        default="default",
        help="RoutingPolicy name (default: %(default)s).",
    )
    parser.add_argument(
        "--sandbox-profile",
        default="default",
        help="SandboxConfig profile name (default: %(default)s).",
    )
    parser.add_argument(
        "--meta-profile",
        default="default",
        help="Meta-profile name (default: %(default)s).",
    )

    # Phase‑3 knobs (global defaults)
    parser.add_argument(
        "--hyde",
        action="store_true",
        help="Enable HYDE retrieval augmentation (global default).",
    )
    parser.add_argument(
        "--rrf-strategy",
        choices=[s.value for s in RRFStrategy],
        default=RRFStrategy.SIMPLE.value,
        help="RRF strategy for evidence fusion (global default).",
    )
    parser.add_argument(
        "--rrf-weight",
        action="append",
        metavar="KEY=VALUE",
        help=(
            "Global RRF weight override in KEY=VALUE form. "
            "May be specified multiple times."
        ),
    )
    parser.add_argument(
        "--council-size",
        type=int,
        default=1,
        help="Global QA / agent council size (default: %(default)s).",
    )
    parser.add_argument(
        "--correction-max-iters",
        type=int,
        default=2,
        help=(
            "Global maximum iterations of the correction loop "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--telemetry-routing-mode",
        choices=[m.value for m in TelemetryRoutingMode],
        default=TelemetryRoutingMode.LOG_ONLY.value,
        help="Telemetry routing mode (global default).",
    )

    # Concurrency / determinism
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum parallel workers for batch execution (default: %(default)s).",
    )
    parser.add_argument(
        "--golden-mode",
        action="store_true",
        help="Enable deterministic golden mode (forces max_workers=1).",
    )

    # Batch / workflow identifiers
    parser.add_argument(
        "--batch-id",
        default=None,
        help="Optional explicit batch ID; if omitted, a UUID4 is generated.",
    )

    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    """
    CLI wrapper for running batch jobs.

    For programmatic usage, prefer calling run_batch() directly.
    """
    args = _parse_args(argv)

    rrf_weights = _parse_rrf_weights(args.rrf_weight)

    jobs = _read_jsonl(args.input)

    results, summary = run_batch(
        jobs,
        execution_profile_name=args.execution_profile,
        routing_policy_name=args.routing_policy,
        sandbox_profile_name=args.sandbox_profile,
        meta_profile_name=args.meta_profile,
        hyde_enabled=args.hyde,
        rrf_strategy=RRFStrategy(args.rrf_strategy),
        rrf_weights=rrf_weights,
        council_size=args.council_size,
        correction_loop_max_iterations=args.correction_max_iters,
        telemetry_routing_mode=TelemetryRoutingMode(args.telemetry_routing_mode),
        max_workers=args.max_workers,
        golden_mode=args.golden_mode,
        base_workflow_id=args.batch_id,
    )

    # Emit per-job JSONL outputs in deterministic order.
    output_rows: List[Dict[str, Any]] = []
    for res in results:
        row_obj: Dict[str, Any] = {
            "batch_id": res.job_config.batch_id,
            "job_index": res.job_config.job_index,
            "job_id": res.job_config.job_id,
            "workflow_id": res.job_config.workflow_id,
            "success": res.success,
            "error": res.error,
            "duration_sec": res.duration_sec,
            "input": res.job_config.row,
            "output": _normalize_output(res.output),
        }
        output_rows.append(row_obj)

    _write_jsonl(args.output, output_rows)

    # Emit batch-level telemetry summary (either to file/STDOUT or STDERR).
    summary_dict = asdict(summary)

    if args.summary_output:
        _write_json(args.summary_output, summary_dict)
    else:
        # Default: log summary to stderr for human inspection.
        sys.stderr.write(json.dumps(summary_dict, sort_keys=True) + "\n")


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()




