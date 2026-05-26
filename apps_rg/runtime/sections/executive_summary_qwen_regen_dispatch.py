"""Mandatory budgeted Qwen dispatch for executive_summary regen/repair (apps_rg W1 SSOT)."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.providers import qwen_vllm_provider
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.sections.executive_summary_token_budget import (
    context_window_provenance_receipt_fields,
    regen_dispatch_allowed,
    resolve_context_window_provenance,
)

LANE_KEY = "executive_summary"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

_REGEN_PHASES = frozenset(
    {"synthesis_regen", "judge_regen", "judge_x2_repair"},
)

_DEFAULT_REGEN_MAX_OUTPUT = 2048
_DEFAULT_SCRATCH_MAX_OUTPUT = 2048
_HARD_CAP_SCRATCH_MAX_OUTPUT = 4096


def resolve_scratch_max_output_tokens() -> int:
    raw = os.environ.get(
        "APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS",
        str(_DEFAULT_SCRATCH_MAX_OUTPUT),
    ).strip()
    try:
        n = int(raw)
    except ValueError:
        n = _DEFAULT_SCRATCH_MAX_OUTPUT
    return max(1, min(n, _HARD_CAP_SCRATCH_MAX_OUTPUT))


def resolve_regen_max_output_tokens() -> int:
    raw = os.environ.get(
        "APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS",
        str(_DEFAULT_REGEN_MAX_OUTPUT),
    ).strip()
    try:
        n = int(raw)
    except ValueError:
        n = _DEFAULT_REGEN_MAX_OUTPUT
    scratch_cap = resolve_scratch_max_output_tokens()
    return max(1, min(n, scratch_cap))


def allocate_call_id(
    *,
    phase: str,
    cycle_index: int,
    attempt_index: int,
    messages: list[dict[str, str]],
) -> str:
    payload = json.dumps(
        {"phase": phase, "cycle_index": cycle_index, "attempt_index": attempt_index, "messages": messages},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    short_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]
    return f"{phase}-{cycle_index:02d}-{attempt_index:02d}-{short_hash}"


def provider_artifact_filename(
    *,
    kind: str,
    phase: str,
    cycle_index: int,
    attempt_index: int,
    call_id: str,
) -> str:
    return f"provider_{kind}_{phase}_cycle{cycle_index:02d}_attempt{attempt_index:02d}_{call_id}.json"


class ExecutiveSummaryRegenBudgetLedger:
    """Per-run regen call records; flushed to call plan + regen_token_budget_receipt."""

    def __init__(self, *, artifact_dir: Path | None = None) -> None:
        self.artifact_dir = Path(artifact_dir) if artifact_dir is not None else None
        self.calls: list[dict[str, Any]] = []

    def register(self, record: dict[str, Any]) -> None:
        self.calls.append(dict(record))

    def update_call(self, call_id: str, **fields: Any) -> None:
        for row in self.calls:
            if row.get("call_id") == call_id:
                row.update(fields)
                if "accepted" not in fields:
                    row["accepted"] = _compute_call_accepted(row)
                return

    def flush(self) -> None:
        if self.artifact_dir is None:
            return
        prov = resolve_context_window_provenance()
        prov_fields = context_window_provenance_receipt_fields(prov)
        plan = {
            "schema": "executive_summary_qwen_call_plan_v1",
            **prov_fields,
            "calls": list(self.calls),
        }
        receipt = {
            "schema": "regen_token_budget_receipt_v1",
            **prov_fields,
            "calls": list(self.calls),
        }
        _write_json(self.artifact_dir / "executive_summary_qwen_call_plan.json", plan)
        _write_json(self.artifact_dir / "regen_token_budget_receipt.json", receipt)


_LEDGERS: dict[str, ExecutiveSummaryRegenBudgetLedger] = {}


def regen_budget_ledger(artifact_dir: Path | str | None) -> ExecutiveSummaryRegenBudgetLedger:
    if artifact_dir is None:
        return ExecutiveSummaryRegenBudgetLedger(artifact_dir=None)
    key = str(Path(artifact_dir).resolve())
    if key not in _LEDGERS:
        _LEDGERS[key] = ExecutiveSummaryRegenBudgetLedger(artifact_dir=Path(artifact_dir))
    return _LEDGERS[key]


def clear_regen_budget_ledger(artifact_dir: Path | str | None) -> None:
    if artifact_dir is None:
        return
    _LEDGERS.pop(str(Path(artifact_dir).resolve()), None)


def _compute_call_accepted(record: dict[str, Any]) -> bool:
    return bool(
        record.get("budget_allowed")
        and record.get("dispatch_allowed")
        and record.get("transport_dispatched")
        and record.get("provider_response_present")
        and record.get("parse_ok")
        and not record.get("transport_timeout")
    )


def _transport_timeout(result: qwen_vllm_provider.ProviderResult) -> bool:
    err = str(getattr(result, "exact_provider_error", None) or "").lower()
    if "timeout" in err:
        return True
    snap = getattr(result, "apps_rg_last_probe_snapshot", None)
    if isinstance(snap, dict):
        for row in snap.get("attempts") or []:
            if isinstance(row, dict) and "timeout" in str(row.get("error_category") or "").lower():
                return True
    return False


@dataclass(frozen=True)
class BudgetedQwenRegenOutcome:
    call_id: str
    call_record: dict[str, Any]
    result: qwen_vllm_provider.ProviderResult | None
    dispatch_allowed: bool
    block_reason: str | None


def budgeted_qwen_regen_call(
    provider_payload: dict[str, Any],
    *,
    messages: list[dict[str, str]],
    phase: str,
    call_site: str,
    cycle_index: int = 0,
    attempt_index: int = 0,
    artifact_dir: Path | str | None = None,
    run_id: str | None = None,
    max_output_tokens: int | None = None,
) -> BudgetedQwenRegenOutcome:
    """Fail-closed regen dispatch SSOT; only internal site that may call transport for regen."""
    if phase not in _REGEN_PHASES:
        raise ValueError(f"unsupported_regen_phase:{phase}")

    max_out = int(max_output_tokens if max_output_tokens is not None else resolve_regen_max_output_tokens())
    max_out = min(max_out, resolve_scratch_max_output_tokens())
    call_id = allocate_call_id(
        phase=phase,
        cycle_index=cycle_index,
        attempt_index=attempt_index,
        messages=messages,
    )
    model_id = str(provider_payload.get("model") or "")
    budget = regen_dispatch_allowed(messages, max_output_tokens=max_out, model=model_id or None)
    provenance = resolve_context_window_provenance(model=model_id or None)
    req_name = provider_artifact_filename(
        kind="request",
        phase=phase,
        cycle_index=cycle_index,
        attempt_index=attempt_index,
        call_id=call_id,
    )
    resp_name = provider_artifact_filename(
        kind="response",
        phase=phase,
        cycle_index=cycle_index,
        attempt_index=attempt_index,
        call_id=call_id,
    )
    art_path = Path(artifact_dir) if artifact_dir is not None else None
    req_ref = req_name
    resp_ref = resp_name

    record: dict[str, Any] = {
        "call_id": call_id,
        "call_site": call_site,
        "phase": phase,
        "cycle_index": int(cycle_index),
        "attempt_index": int(attempt_index),
        "provider_request_ref": req_ref,
        "provider_response_ref": resp_ref,
        "estimated_input_tokens": budget.estimated_input_tokens,
        "max_output_tokens": max_out,
        "reserved_tokens": budget.reserved_tokens,
        "provider_context_window": budget.provider_context_window,
        "available_input_tokens": budget.available_input_tokens,
        "headroom_tokens": budget.headroom_tokens,
        "headroom_pct": budget.headroom_pct,
        **context_window_provenance_receipt_fields(provenance),
        "dispatch_allowed": budget.dispatch_allowed,
        "block_reason": budget.block_reason,
        "budget_allowed": budget.dispatch_allowed,
        "transport_dispatched": False,
        "transport_timeout": False,
        "provider_response_present": False,
        "parse_ok": False,
        "accepted": False,
    }

    ledger = regen_budget_ledger(artifact_dir)
    ledger.register(record)

    if not budget.dispatch_allowed:
        return BudgetedQwenRegenOutcome(
            call_id=call_id,
            call_record=record,
            result=None,
            dispatch_allowed=False,
            block_reason=budget.block_reason,
        )

    payload = {**provider_payload, "messages": messages, "max_tokens": max_out}
    if art_path is not None:
        _write_json(
            art_path / req_name,
            {
                "call_id": call_id,
                "phase": phase,
                "cycle_index": cycle_index,
                "attempt_index": attempt_index,
                "call_site": call_site,
                "payload": payload,
            },
        )

    result = call_qwen_vllm(
        tag_reasoning_lane(payload, LANE_KEY),
        artifact_dir=artifact_dir,
        run_id=run_id,
    )
    record["transport_dispatched"] = True
    record["transport_timeout"] = _transport_timeout(result)
    record["provider_response_present"] = bool(
        getattr(result, "runtime_generation_status", None) == "REAL_LLM"
        and (getattr(result, "raw_model_output", None) or getattr(result, "provider_response", None))
    )
    if art_path is not None and record["provider_response_present"]:
        _write_json(art_path / resp_name, result.to_dict())

    ledger.update_call(call_id, **{k: v for k, v in record.items() if k != "call_id"})
    return BudgetedQwenRegenOutcome(
        call_id=call_id,
        call_record=record,
        result=result,
        dispatch_allowed=True,
        block_reason=None,
    )


def mark_regen_call_parse(
    artifact_dir: Path | str | None,
    call_id: str,
    *,
    parse_ok: bool,
) -> None:
    ledger = regen_budget_ledger(artifact_dir)
    ledger.update_call(call_id, parse_ok=bool(parse_ok))


__all__ = [
    "BudgetedQwenRegenOutcome",
    "ExecutiveSummaryRegenBudgetLedger",
    "allocate_call_id",
    "budgeted_qwen_regen_call",
    "clear_regen_budget_ledger",
    "mark_regen_call_parse",
    "provider_artifact_filename",
    "regen_budget_ledger",
    "resolve_regen_max_output_tokens",
    "resolve_scratch_max_output_tokens",
]
