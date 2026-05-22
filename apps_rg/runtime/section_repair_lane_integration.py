"""Lane helpers for P1 repair ledger wiring (init, X2 snapshot, product quality)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.section_repair_ledger import (
    KIND_MECHANICAL,
    KIND_REGEN_LLM,
    attach_ledger_summary_to_l2,
    init_ledger,
    infer_product_quality_with_repair_ledger,
    load_ledger,
    record_repair,
    record_x2_run,
    set_authoritative_attempt,
)


def start_lane_repair_ledger(
    artifact_dir: Path,
    *,
    section_id: str,
    run_id: str,
) -> None:
    init_ledger(artifact_dir, section_id=section_id, run_id=run_id)


def record_parse_json_retry(
    artifact_dir: Path,
    *,
    reason: str = "",
) -> None:
    record_repair(
        artifact_dir,
        kind=KIND_MECHANICAL,
        operation="parse_json_retry",
        reason=reason or "parse_retry",
        replaced_l2=False,
    )


def record_regen_llm(
    artifact_dir: Path,
    *,
    operation: str,
    reason: str,
    replaced_l2: bool = True,
) -> None:
    record_repair(
        artifact_dir,
        kind=KIND_REGEN_LLM,
        operation=operation,
        reason=reason[:240],
        replaced_l2=replaced_l2,
    )


def record_mechanical(
    artifact_dir: Path,
    *,
    operation: str,
    reason: str = "",
) -> None:
    record_repair(
        artifact_dir,
        kind=KIND_MECHANICAL,
        operation=operation,
        reason=reason[:240],
        replaced_l2=False,
    )


def record_deterministic_rewrite(
    artifact_dir: Path,
    *,
    operation: str,
    reason: str = "",
) -> None:
    from apps_rg.runtime.section_repair_ledger import KIND_DETERMINISTIC_REWRITE

    record_repair(
        artifact_dir,
        kind=KIND_DETERMINISTIC_REWRITE,
        operation=operation,
        reason=reason[:240],
        replaced_l2=True,
    )


def snapshot_lane_x2(
    artifact_dir: Path,
    x2_gates: list[dict[str, Any]],
    *,
    after_l2_source: str | None = None,
) -> None:
    ledger = load_ledger(artifact_dir) or {}
    src = after_l2_source or str(ledger.get("authoritative_l2_source") or "initial_llm")
    record_x2_run(
        artifact_dir,
        run_number=len(list(ledger.get("x2_runs") or [])) + 1,
        after_l2_source=src,
        x2_gates=x2_gates,
    )


def finalize_lane_product_quality(
    artifact_dir: Path,
    *,
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
    pass_reason: str,
    l2_output: dict[str, Any] | None = None,
    regen_authoritative_on_x2_pass: bool = False,
) -> tuple[str, str]:
    """Record X2, optionally bump authoritative attempt after counted regen, infer PASS/FAIL."""
    snapshot_lane_x2(artifact_dir, x2_gates)
    if regen_authoritative_on_x2_pass and not [g for g in x2_gates if not g.get("pass")]:
        ledger = load_ledger(artifact_dir) or {}
        if any(r.get("kind") == KIND_REGEN_LLM and r.get("replaced_l2") for r in ledger.get("repairs") or []):
            set_authoritative_attempt(artifact_dir, 2, reason="counted_regen_x2_pass")
    failed = [str(g.get("gate_id") or "") for g in x2_gates if not g.get("pass")]
    failed = [g for g in failed if g]
    status, reason = infer_product_quality_with_repair_ledger(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason=pass_reason,
        artifact_dir=artifact_dir,
    )
    if l2_output is not None:
        l2_output["product_quality_status"] = status
        l2_output["product_quality_reason"] = reason
        attach_ledger_summary_to_l2(l2_output, artifact_dir)
    return status, reason


def infer_lane_product_quality(
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
    *,
    artifact_dir: Path | None,
    pass_reason: str,
) -> tuple[str, str]:
    failed = [str(g.get("gate_id") or "") for g in x2_gates if not g.get("pass")]
    failed = [g for g in failed if g]
    return infer_product_quality_with_repair_ledger(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason=pass_reason,
        artifact_dir=artifact_dir,
    )


__all__ = [
    "start_lane_repair_ledger",
    "record_parse_json_retry",
    "record_regen_llm",
    "record_mechanical",
    "record_deterministic_rewrite",
    "snapshot_lane_x2",
    "finalize_lane_product_quality",
    "infer_lane_product_quality",
]
