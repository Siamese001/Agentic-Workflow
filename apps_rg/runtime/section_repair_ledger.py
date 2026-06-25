"""Section repair ledger — counted regen and documented mechanical repairs (P1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

LEDGER_FILENAME = "section_repair_ledger.json"
SCHEMA_VERSION = 1

KIND_INITIAL_LLM = "initial_llm"
KIND_MECHANICAL = "mechanical"
KIND_REGEN_LLM = "regen_llm"
KIND_DETERMINISTIC_REWRITE = "deterministic_rewrite"


def ledger_path(artifact_dir: Path) -> Path:
    return Path(artifact_dir) / LEDGER_FILENAME


def load_ledger(artifact_dir: Path) -> dict[str, Any] | None:
    path = ledger_path(artifact_dir)
    if not path.is_file():
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):  # guardian: allow-return-none-swallow -- P2 burndown: missing repair ledger is non-fatal
        return None
    return doc if isinstance(doc, dict) else None


def write_ledger(artifact_dir: Path, ledger: dict[str, Any]) -> None:
    path = ledger_path(artifact_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def init_ledger(
    artifact_dir: Path,
    *,
    section_id: str,
    run_id: str,
) -> dict[str, Any]:
    ledger: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "section_id": section_id,
        "run_id": run_id,
        "product_fail_closed": product_fail_closed_runtime(),
        "scored_attempt_number": 1,
        "authoritative_attempt_number": 1,
        "authoritative_l2_source": KIND_INITIAL_LLM,
        "attempt_1_x2_failed": False,
        "attempt_1_x2_failed_gate_ids": [],
        "repairs": [],
        "x2_runs": [],
    }
    write_ledger(artifact_dir, ledger)
    return ledger


def ensure_ledger(
    artifact_dir: Path,
    *,
    section_id: str,
    run_id: str,
) -> dict[str, Any]:
    existing = load_ledger(artifact_dir)
    if existing is not None:
        return existing
    return init_ledger(artifact_dir, section_id=section_id, run_id=run_id)


def record_repair(
    artifact_dir: Path,
    *,
    kind: str,
    operation: str,
    reason: str = "",
    replaced_l2: bool = False,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ledger = ensure_ledger(artifact_dir, section_id="", run_id="")
    if not ledger.get("section_id"):
        ledger["section_id"] = str(detail.get("section_id") if detail else "")
    repairs = list(ledger.get("repairs") or [])
    seq = len(repairs) + 1
    entry: dict[str, Any] = {
        "seq": seq,
        "kind": kind,
        "operation": operation,
        "reason": (reason or "")[:500],
        "replaced_l2": bool(replaced_l2),
    }
    if detail:
        entry["detail"] = detail
    repairs.append(entry)
    ledger["repairs"] = repairs
    if kind == KIND_REGEN_LLM and replaced_l2:
        ledger["authoritative_l2_source"] = KIND_REGEN_LLM
    write_ledger(artifact_dir, ledger)
    return ledger


def record_x2_run(
    artifact_dir: Path,
    *,
    run_number: int,
    after_l2_source: str,
    x2_gates: list[dict[str, Any]],
) -> dict[str, Any]:
    ledger = load_ledger(artifact_dir) or {}
    failed = [str(g.get("gate_id") or "") for g in x2_gates if not g.get("pass")]
    failed = [g for g in failed if g]
    runs = list(ledger.get("x2_runs") or [])
    runs.append(
        {
            "run": run_number,
            "after_l2_source": after_l2_source,
            "failed_gate_ids": failed,
            "passed": not failed,
        }
    )
    ledger["x2_runs"] = runs
    if run_number == 1:
        ledger["attempt_1_x2_failed"] = bool(failed)
        ledger["attempt_1_x2_failed_gate_ids"] = failed
    write_ledger(artifact_dir, ledger)
    return ledger


def set_authoritative_attempt(
    artifact_dir: Path,
    attempt_number: int,
    *,
    reason: str = "",
) -> dict[str, Any]:
    ledger = load_ledger(artifact_dir) or {}
    ledger["authoritative_attempt_number"] = max(1, int(attempt_number))
    ledger["authoritative_attempt_reason"] = (reason or "")[:500]
    write_ledger(artifact_dir, ledger)
    return ledger


def attach_ledger_summary_to_l2(l2_output: dict[str, Any], artifact_dir: Path) -> None:
    ledger = load_ledger(artifact_dir)
    if ledger is None:
        return
    l2_output["section_repair_ledger"] = ledger_path(artifact_dir).name
    l2_output["authoritative_attempt_number"] = ledger.get("authoritative_attempt_number", 1)
    l2_output["authoritative_l2_source"] = ledger.get("authoritative_l2_source", KIND_INITIAL_LLM)


def ledger_blocks_product_pass(ledger: dict[str, Any] | None) -> tuple[bool, str]:
    """Return (blocked, reason) when ledger proves pass would hide failure."""
    if ledger is None or not ledger.get("product_fail_closed"):
        return False, ""

    repairs = list(ledger.get("repairs") or [])
    # Authorized deterministic post-processing ops that do NOT hide X2 gate failures:
    # - graph_only_generation_quality_repair: only with explicit repair-mode receipt
    # - finalize_competencies_v3_output: capability projection on competencies lane (always runs)
    # - repair_protected_unify_bullet_metrics: canonical metric restoration on unify_bullets lane
    # - repair_required_brushstroke_citation: ledger-only attachment of a required fact to an
    #   already-materialized executive_summary sentence; no visible prose is introduced.
    # - bullet_judge_feedback_reselection (W4.1/G14): judge-feedback pool reselection on the
    #   employment bullet lanes. Honest because the swap (a) re-runs the FULL X2 gate set on
    #   the swapped doc and fully reverts on any regression, (b) re-judges the new content
    #   exactly once at the SAME rubric/threshold (revert-on-worse on the soft-fail arm), and
    #   (c) always writes reselection_receipt.json naming trigger, slots, and outcome.
    _AUTHORIZED_DET_OPS: frozenset[str] = frozenset(
        {
            "finalize_competencies_v3_output",
            "repair_protected_unify_bullet_metrics",
            "repair_required_brushstroke_citation",
            "bullet_judge_feedback_reselection",
        }
    )

    def _authorized_graph_only_quality_repair(row: dict[str, Any]) -> bool:
        detail = row.get("detail")
        detail_map = detail if isinstance(detail, dict) else {}
        return (
            row.get("operation")
            in {
                "graph_only_generation_quality_repair",
                "graph_only_display_authority_fallback",
            }
            and detail_map.get("explicit_repair_mode") is True
            and detail_map.get("repair_mode") == "explicit_graph_only_repair"
        )

    det_ops = [
        r.get("operation")
        for r in repairs
        if r.get("kind") == KIND_DETERMINISTIC_REWRITE
        and r.get("operation") not in _AUTHORIZED_DET_OPS
        and not _authorized_graph_only_quality_repair(r)
    ]
    if det_ops:
        return True, f"deterministic_rewrite_without_counted_regen:{det_ops}"

    auth_attempt = int(ledger.get("authoritative_attempt_number") or 1)
    regen_replaced = any(
        r.get("kind") == KIND_REGEN_LLM and r.get("replaced_l2")
        for r in repairs
    )
    if regen_replaced and auth_attempt < 2:
        return True, "regen_replaced_l2_but_authoritative_attempt_still_1"

    if ledger.get("attempt_1_x2_failed") and auth_attempt == 1:
        x2_runs = list(ledger.get("x2_runs") or [])
        last = x2_runs[-1] if x2_runs else {}
        if last.get("passed"):
            return True, "attempt_1_x2_failed_then_pass_without_authoritative_regen"

    return False, ""


def infer_product_quality_with_repair_ledger(
    *,
    runtime_generation_status: str,
    x2_failed_gate_ids: list[str],
    pass_reason: str,
    artifact_dir: Path | None = None,
) -> tuple[str, str]:
    from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
        infer_product_quality_blocked_or_mock,
    )

    status, reason = infer_product_quality_blocked_or_mock(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=x2_failed_gate_ids,
        pass_reason=pass_reason,
    )
    if status != "PASS" or artifact_dir is None:
        return status, reason

    ledger = load_ledger(artifact_dir)
    blocked, block_reason = ledger_blocks_product_pass(ledger)
    if blocked:
        return "FAIL", block_reason
    return status, reason


__all__ = [
    "LEDGER_FILENAME",
    "KIND_INITIAL_LLM",
    "KIND_MECHANICAL",
    "KIND_REGEN_LLM",
    "KIND_DETERMINISTIC_REWRITE",
    "ledger_path",
    "load_ledger",
    "write_ledger",
    "init_ledger",
    "ensure_ledger",
    "record_repair",
    "record_x2_run",
    "set_authoritative_attempt",
    "attach_ledger_summary_to_l2",
    "ledger_blocks_product_pass",
    "infer_product_quality_with_repair_ledger",
]
