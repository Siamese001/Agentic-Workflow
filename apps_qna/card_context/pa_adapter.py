"""Prompt Assembly Adapter — bridges card context to canonical PA pipeline.

D2.2: Runs the canonical PA.0 → PA.7 staged checks against the assembled
card context. This is NOT a model dispatch — apps_qna produces domain card
context, not model-level prompts. The adapter validates that the assembled
context satisfies PA boundary, classifier, and budget gates before the
pack is finalised.

The adapter is fail-closed at the PA.0 boundary check (missing contracts
block), and fail-open on budget (overflow → dispatch=PASS with warning)
so that the build-time compiler path (which has no LLM call) still works.

Plan (D2.2): .windsurf/plans/apps-qna-spine-deferred-e9c5b3.md D2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.prompt_governance.prompt_assembly.pipeline import (
    PromptAssemblyPipelineResult,
    run_prompt_assembly_pipeline,
)
from agentic_core.prompt_governance.prompt_assembly.pa5_budget import (
    BudgetClass,
    SlotBudgetEntry,
)
from agentic_core.prompt_governance.prompt_assembly.pa7_dispatch_states import (
    DispatchDisposition,
)


@dataclass(frozen=True)
class PAAdapterResult:
    """Result wrapper returned by run_pa_for_card_context().

    Attributes:
        pipeline: Full PromptAssemblyPipelineResult from the PA pipeline.
        dispatchable: True when PA.7 disposition is PASS.
        dispatch_disposition: String value of the PA.7 disposition.
        reason: Human-readable summary of block reason (empty on PASS).
        error: Non-empty when the adapter raised unexpectedly; fail-closed.
    """

    pipeline: PromptAssemblyPipelineResult | None = None
    dispatchable: bool = False
    dispatch_disposition: str = ""
    reason: str = ""
    error: str = ""


def run_pa_for_card_context(
    *,
    card_context: dict[str, Any],
    interview_slug: str,
    route_id: str,
    policy_hash: str = "",
    blueprint_hash: str = "",
    request_id: str = "",
    run_id: str = "",
    model_context_window: int = 200_000,
    reserved_output_tokens: int = 0,
) -> PAAdapterResult:
    """Run PA.0 → PA.7 staged checks on the assembled card context.

    Constructs minimal plan_contract, route_contract, and evidence_contract
    dicts from the card_context assembled by card_context_assembler, then
    delegates to run_prompt_assembly_pipeline.

    The budget stage (PA.5) is run with a single slot entry representing
    the estimated card-context token footprint (len(serialised) / 4). Budget
    overflow is not fatal for the build-time compiler — dispatchable is still
    True when the PA.0 boundary passes, even if PA.5 overflows.

    Args:
        card_context: Dict produced by assemble_card_context().
        interview_slug: The interview slug (used as plan_id / trace).
        route_id: The selected route id.
        policy_hash: Optional policy hash for governance fields.
        blueprint_hash: Optional blueprint hash.
        request_id: Correlation id.
        run_id: Run id.
        model_context_window: Token budget for PA.5.
        reserved_output_tokens: Reserved output tokens for PA.5.

    Returns:
        PAAdapterResult wrapping the full pipeline result.
    """
    try:
        plan_contract: dict[str, Any] = {
            "plan_id": interview_slug or "apps_qna::plan",
            "task_spec": f"Build interview card pack: {interview_slug}",
            "query_spec": route_id,
            "output_target": "card_pack",
            "grounding_required": card_context.get("grounded", False),
            "policy_hash": policy_hash,
        }

        route_contract: dict[str, Any] = {
            "route_id": route_id or "apps_qna::build_time_compiler",
            "execution_form": "terminal",
            "provider_lane": "none",
            "policy_hash": policy_hash,
            "blueprint_hash": blueprint_hash,
            "required_slots": (),
        }

        evidence_sufficiency = card_context.get("evidence_sufficiency", "empty")
        evidence_contract: dict[str, Any] = {
            "status": "PASS" if evidence_sufficiency != "empty" else "EMPTY",
            "support_score": 1.0 if evidence_sufficiency == "grounded" else 0.0,
            "source_ids": tuple(
                s.get("source_id", "") if isinstance(s, dict) else str(s)
                for s in card_context.get("retrieval_sources", [])
            ),
            "policy_hash": policy_hash,
        }

        governance: dict[str, Any] = {
            "policy_hash": policy_hash,
            "system_version_hash": blueprint_hash,
            "durable_write_allowed": False,
            "hitl_required": False,
        }

        execution_metadata: dict[str, Any] = {
            "request_id": request_id or interview_slug or "apps_qna",
            "run_id": run_id or interview_slug or "apps_qna",
            "trace_root": request_id or interview_slug or "apps_qna",
            "replay_key": request_id or interview_slug or "apps_qna",
            "policy_hash": policy_hash,
            "plan_id": interview_slug or "apps_qna::plan",
            "route_id": route_id or "apps_qna::build_time_compiler",
            "executable_requested": False,
        }

        import json as _json
        context_token_estimate = max(1, len(_json.dumps(card_context, default=str)) // 4)
        budget_entries: list[SlotBudgetEntry] = [
            SlotBudgetEntry(
                label="C0:CARD_CONTEXT",
                tokens=context_token_estimate,
                budget_class=BudgetClass.MANDATORY_NEVER_TRIM,
                must_use=True,
                rationale="apps_qna assembled card context",
            ),
        ]

        pipeline = run_prompt_assembly_pipeline(
            plan_contract=plan_contract,
            route_contract=route_contract,
            evidence_contract=evidence_contract,
            governance=governance,
            execution_metadata=execution_metadata,
            budget_entries=budget_entries,
            model_context_window=model_context_window,
            reserved_output_tokens=reserved_output_tokens,
        )

        disposition = pipeline.dispatch.disposition
        is_pass = disposition is DispatchDisposition.PASS
        reason = ""
        if not is_pass:
            block = pipeline.dispatch.block_reason
            reason = block.value if block is not None else disposition.value

        return PAAdapterResult(
            pipeline=pipeline,
            dispatchable=is_pass,
            dispatch_disposition=disposition.value,
            reason=reason,
        )

    except Exception as exc:  # guardian: allow-broad-exception-catch -- PA adapter wraps an optional check; errors must not block the card build pipeline
        return PAAdapterResult(
            dispatchable=False,
            dispatch_disposition="error",
            reason="pa_adapter_error",
            error=str(exc),
        )


__all__ = ["PAAdapterResult", "run_pa_for_card_context"]
