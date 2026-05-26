"""Delegate executive_summary judge regen to core SameAuthorityRegenRunner (ADR-085 W3)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.reasoning.prompt_messages import PromptMessages
from agentic_core.L2_execution.regen import (
    AnchorClassification,
    DefectClass,
    IncrementalRepairContract,
    SameAuthorityRegenRunner,
    TriggerSource,
    format_regen_delta_user_turn,
)
from agentic_core.L2_execution.regen.prefix_digest import (
    compute_system_prefix_hash,
    sha256_hex,
)

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    collect_judge_remediation_delta_lines,
)


def messages_to_prompt_messages(messages: list[dict[str, str]]) -> PromptMessages:
    """Project initial provider thread (system + first user) to PromptMessages IR."""
    slot_map: dict[str, str] = {}
    ordered: list[str] = []
    for msg in messages:
        role = str(msg.get("role") or "").lower()
        content = str(msg.get("content") or "")
        if role == "system" and "SYSTEM" not in slot_map:
            slot_map["SYSTEM"] = content
            ordered.append("SYSTEM")
        elif role == "developer" and "D0" not in slot_map:
            slot_map["D0"] = content
            ordered.append("D0")
        elif role == "user" and "U0" not in slot_map:
            slot_map["U0"] = content
            ordered.append("U0")
    if not slot_map and messages:
        slot_map["USER"] = str(messages[-1].get("content") or "")
        ordered.append("USER")
    return PromptMessages(
        slot_map=slot_map,
        ordered_slots=tuple(ordered),
        metadata={"source": "apps_rg_exec_summary_bridge"},
    )


def _load_compiled_context(artifact_dir: Path | None) -> dict[str, Any]:
    if artifact_dir is None:
        return {}
    path = artifact_dir / "compiled_prompt_artifact.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_regen_delta_user_turn(
    *,
    x1d_judges: list[dict[str, Any]],
    unused_fact_ids: list[str],
    allowed_fact_count: int,
    prior_word_count: int = 0,
    prior_ledger_rows: int = 0,
    baseline_resume_display_text: str = "",
    prior_attempt_resume_display_text: str = "",
    prior_cycle_judges: list[dict[str, Any]] | None = None,
) -> str:
    """App delta lines + floors; core owns REGEN_DELTA header and PROMPT_LOCK."""
    lines = list(
        collect_judge_remediation_delta_lines(
            x1d_judges,
            unused_fact_ids=unused_fact_ids,
            allowed_fact_count=allowed_fact_count,
            prior_word_count=prior_word_count,
            prior_ledger_rows=prior_ledger_rows,
            baseline_resume_display_text=baseline_resume_display_text,
            prior_attempt_resume_display_text=prior_attempt_resume_display_text,
            prior_cycle_judges=prior_cycle_judges,
        ),
    )
    return format_regen_delta_user_turn(tuple(lines))


def build_incremental_repair_contract(
    *,
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    x1d_judges: list[dict[str, Any]],
    trigger_receipt: dict[str, Any],
    unused_fact_ids: list[str],
    allowed_fact_count: int,
    anchor_output_text: str,
    prior_word_count: int,
    prior_ledger_rows: int,
    artifact_dir: Path | None,
    run_id: str | None,
    semantic_regen_attempt_index: int = 1,
    transport_retry_count: int = 0,
    max_semantic_regen_attempts: int = 1,
    nested_heal_without_new_attempt: bool = False,
    baseline_resume_display_text: str = "",
    prior_attempt_resume_display_text: str = "",
    prior_cycle_judges: list[dict[str, Any]] | None = None,
) -> IncrementalRepairContract:
    compile_ctx = _load_compiled_context(artifact_dir)
    pm = messages_to_prompt_messages(messages)
    sys_hash = compute_system_prefix_hash(pm.system_text())
    frozen_ref = str(
        compile_ctx.get("compilation_hash")
        or compile_ctx.get("prompt_hash")
        or "",
    ).strip()
    if not frozen_ref and artifact_dir is not None:
        frozen_ref = sha256_hex(
            json.dumps(messages[:2], sort_keys=True, separators=(",", ":")),
        )

    model = str(provider_payload.get("model") or compile_ctx.get("target_model") or "")
    provider_lane = str(
        provider_payload.get("provider")
        or compile_ctx.get("target_provider")
        or "vllm",
    )

    trigger_source = TriggerSource.X3_JUDGE
    if str(trigger_receipt.get("trigger_mode") or "").startswith("x2"):
        trigger_source = TriggerSource.X2

    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        judge_regen_max_delta_lines,
        judge_regen_max_delta_tokens,
    )

    max_delta_tokens = judge_regen_max_delta_tokens()
    max_delta_lines = judge_regen_max_delta_lines()
    delta_lines = tuple(
        collect_judge_remediation_delta_lines(
            x1d_judges,
            unused_fact_ids=unused_fact_ids,
            allowed_fact_count=allowed_fact_count,
            prior_word_count=prior_word_count,
            prior_ledger_rows=prior_ledger_rows,
            baseline_resume_display_text=baseline_resume_display_text,
            prior_attempt_resume_display_text=prior_attempt_resume_display_text,
            prior_cycle_judges=prior_cycle_judges,
        ),
    )

    return IncrementalRepairContract(
        request_id=str(run_id or compile_ctx.get("run_id") or "exec-summary-run"),
        run_id=str(run_id or compile_ctx.get("run_id") or "exec-summary-run"),
        trace_root=str(compile_ctx.get("trace_id") or run_id or "trace-root"),
        parent_contract_ref=str(trigger_receipt.get("parent_attempt_receipt_id") or "attempt-1"),
        parent_attempt_receipt_id=str(
            trigger_receipt.get("parent_attempt_receipt_id") or "attempt-1",
        ),
        replay_key=str(compile_ctx.get("replay_key") or "replay-key-unset"),
        policy_hash=str(compile_ctx.get("policy_hash") or "policy-unset"),
        blueprint_hash=str(compile_ctx.get("blueprint_hash") or "blueprint-unset"),
        registry_digest_set=tuple(
            str(x) for x in (compile_ctx.get("registry_digest_set") or []) if x
        )
        or ("registry-unset",),
        frozen_compile_ref=frozen_ref or "compile-unset",
        prompt_hash=frozen_ref or "compile-unset",
        provider_lane=provider_lane,
        model_lane=model or "model-unset",
        parent_provider_lane=provider_lane,
        parent_model_lane=model or "model-unset",
        anchor_output_hash=sha256_hex(anchor_output_text),
        anchor_output_text=anchor_output_text,
        anchor_classification=AnchorClassification.LAST_APPROVED,
        defect_class=DefectClass.SOFT_REPAIRABLE,
        trigger_source=trigger_source,
        delta_lines=delta_lines,
        semantic_regen_attempt_index=semantic_regen_attempt_index,
        transport_retry_count=transport_retry_count,
        max_semantic_regen_attempts=max_semantic_regen_attempts,
        max_delta_tokens=max_delta_tokens,
        max_delta_lines=max_delta_lines,
        prompt_messages=pm,
        expected_system_prefix_hash=sys_hash,
        nested_heal_without_new_attempt=nested_heal_without_new_attempt,
        runtime_gate_refs=("G19", "G20", "G21", "G24"),
        l5_governance_context_digest=str(compile_ctx.get("l5_certification_ref") or ""),
    )


def run_core_same_authority_regen(
    *,
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    contract: IncrementalRepairContract,
    artifact_dir: Path | None,
    run_id: str | None,
) -> tuple[str, dict[str, Any], dict[str, Any], tuple[dict[str, str], ...]]:
    """Invoke core runner; persist receipt + provider_request proof artifacts."""
    from apps_rg.runtime.sections.executive_summary_lane import write_json
    from apps_rg.runtime.sections.executive_summary_qwen_regen_dispatch import (
        budgeted_qwen_regen_call,
        mark_regen_call_parse,
    )

    runner = SameAuthorityRegenRunner()
    _semantic_index = int(contract.semantic_regen_attempt_index or 1)

    def _provider_generate(chat_messages: list[dict[str, str]]) -> dict[str, Any]:
        regen_outcome = budgeted_qwen_regen_call(
            provider_payload,
            messages=list(chat_messages),
            phase="judge_regen",
            call_site="run_core_same_authority_regen",
            cycle_index=max(0, _semantic_index - 1),
            attempt_index=0,
            artifact_dir=artifact_dir,
            run_id=run_id,
        )
        result = regen_outcome.result
        if not regen_outcome.dispatch_allowed or result is None:
            return {"content": "", "mocked_allow": True}
        if result.runtime_generation_status != "REAL_LLM":
            return {"content": "", "mocked_allow": True}
        from apps_rg.runtime.sections.executive_summary_lane import parse_model_json

        _parsed, _ = parse_model_json(str(result.raw_model_output or ""))
        mark_regen_call_parse(artifact_dir, regen_outcome.call_id, parse_ok=bool(_parsed))
        return {"content": result.raw_model_output or ""}

    result = runner.run(
        contract,
        provider_generate=_provider_generate,
        provider_request_ref=str((artifact_dir or Path(".")) / "provider_request_regen.json"),
        provider_response_ref=str(
            (artifact_dir or Path(".")) / "provider_response_judge_regen.json",
        ),
    )

    receipt_dict: dict[str, Any] = {
        "schema": "executive_summary_core_same_authority_regen_v1",
        "accepted": result.accepted,
        "regen_engine": "agentic_core.L2_execution.regen.SameAuthorityRegenRunner",
        "max_delta_tokens": int(contract.max_delta_tokens),
    }
    if result.receipt is not None:
        receipt_dict["same_authority_regen_receipt"] = result.receipt.as_dict()
        receipt_dict["heal_receipt_bridge"] = {
            "repair_tactic": result.receipt.repair_tactic,
            "next_action": result.receipt.next_action,
            "heal_outcome": result.receipt.heal_outcome.value,
        }
    if result.refusal is not None:
        receipt_dict["refusal"] = result.refusal.to_dict()

    chat_messages = tuple(result.chat_messages)
    if artifact_dir is not None:
        write_json(artifact_dir / "same_authority_regen_receipt.json", receipt_dict)
        if chat_messages:
            write_json(
                artifact_dir / "provider_request_regen.json",
                {
                    "model": contract.model_lane,
                    "provider_lane": contract.provider_lane,
                    "messages": list(chat_messages),
                    "system_prefix_hash": contract.expected_system_prefix_hash,
                    "frozen_compile_ref": contract.frozen_compile_ref,
                    "parent_provider_lane": contract.parent_provider_lane,
                    "parent_model_lane": contract.parent_model_lane,
                    "no_prompt_recompile_assertion": bool(
                        result.receipt and result.receipt.no_prompt_recompile_assertion,
                    ),
                },
            )

    return (
        result.regenerated_text,
        receipt_dict,
        result.receipt.as_dict() if result.receipt else {},
        chat_messages,
    )
