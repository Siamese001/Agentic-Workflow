"""apps_rg provider adapters for agentic_core JudgePanelRunner."""

from __future__ import annotations

from apps_rg.runtime.judges.executive_summary_x1d import (
    GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS,
    PROVIDERS,
    _invoke_judge_with_bounded_retries,
    _resolved_openai_judge_max_completion_tokens,
    _resolved_x1d_judge_max_output_tokens,
)
from apps_rg.runtime.judges.x1d_panel_context import X1dPanelProviderContext
from agentic_core.runtime.judges.panel.adapter_protocol import (
    AdapterInvokeError,
    DeclaredTransportPolicy,
)
from agentic_core.runtime.judges.panel.canonical_contract import CanonicalJudgeContract
from agentic_core.runtime.judges.panel.panel_types import PanelJudgeOutcome, TransportReceipt


def _transport_receipt(
    ctx: X1dPanelProviderContext,
    contract: CanonicalJudgeContract,
    *,
    attempt: int,
    finish_reason: str | None = "stop",
    parse_status: str = "ok",
) -> TransportReceipt:
    if ctx.provider_key == "openai_chatgpt":
        max_tokens = _resolved_openai_judge_max_completion_tokens(attempt=attempt)
        json_lock = "json_object"
    elif ctx.provider_key == "anthropic_claude":
        max_tokens = _resolved_x1d_judge_max_output_tokens(attempt=attempt)
        json_lock = "json_object"
    else:
        max_tokens = GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS
        json_lock = "responseSchema"
    return TransportReceipt(
        provider_key=ctx.provider_key,
        contract_hash=contract.contract_hash(),
        max_output_tokens=max_tokens,
        temperature=0.1,
        json_output_lock=json_lock,
        finish_or_stop_reason=finish_reason,
        parse_status=parse_status,
        attempt=attempt,
    )


def _panel_outcome_from_judge(
    ctx: X1dPanelProviderContext,
    contract: CanonicalJudgeContract,
    *,
    attempt: int,
) -> tuple[PanelJudgeOutcome, TransportReceipt]:
    out = ctx.last_judge_output
    if out is None:
        raise AdapterInvokeError(f"{ctx.provider_key} produced no JudgeOutput")

    parse_status = "ok"
    finish: str | None = "stop"
    if out.provider_blocked or out.evaluator_mode.startswith("BLOCKED"):
        parse_status = "blocked"
        finish = None

    panel = PanelJudgeOutcome(
        provider_key=ctx.provider_key,
        contract_hash=contract.contract_hash(),
        input_hash=ctx.input_hash,
        evaluator_mode=out.evaluator_mode,
        provider_status=out.provider_status,
        score=out.score,
        score_scale=str(out.score_scale or "0_to_5"),
        threshold=float(out.threshold),
        pass_=out.pass_,
        decisive_failure=out.decisive_failure,
        findings=tuple(out.findings),
        cited_sentence_indexes=tuple(out.cited_sentence_indexes),
        remediation_suggestions=tuple(out.remediation_suggestions),
        raw_body={"judge_output": out.to_dict()},
    )
    return panel, _transport_receipt(ctx, contract, attempt=attempt, finish_reason=finish, parse_status=parse_status)


class AppsRgX1dPanelAdapter:
    """Thin wrapper: core panel protocol → existing apps_rg _call_* transport."""

    def __init__(self, ctx: X1dPanelProviderContext) -> None:
        self._ctx = ctx

    @property
    def provider_key(self) -> str:
        return self._ctx.provider_key

    def declared_policy(self, *, attempt: int = 1) -> DeclaredTransportPolicy:
        if self.provider_key == "openai_chatgpt":
            return DeclaredTransportPolicy(
                max_output_tokens=_resolved_openai_judge_max_completion_tokens(attempt=attempt),
                json_output_lock="json_object",
                temperature=0.1,
            )
        if self.provider_key == "anthropic_claude":
            return DeclaredTransportPolicy(
                max_output_tokens=_resolved_x1d_judge_max_output_tokens(attempt=attempt),
                json_output_lock="json_object",
                temperature=0.1,
            )
        return DeclaredTransportPolicy(
            max_output_tokens=GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS,
            json_output_lock="responseSchema",
            temperature=0.1,
        )

    def invoke(
        self,
        contract: CanonicalJudgeContract,
        *,
        attempt: int = 1,
    ) -> tuple[PanelJudgeOutcome, TransportReceipt]:
        ctx = self._ctx
        prompt = contract.user_prompt
        gate_summary = dict(ctx.deterministic_gate_summary or contract.deterministic_gate_summary)

        from apps_rg.runtime.judges import executive_summary_x1d as x1d_mod

        def _dispatch(attempt_no: int):
            if ctx.provider_key == "openai_chatgpt":
                return x1d_mod._call_openai(
                    ctx.api_key,
                    prompt,
                    ctx.model,
                    ctx.input_hash,
                    ctx.provider_key,
                    artifact_base=ctx.artifact_base,
                    reasoning_effort=ctx.reasoning_effort,
                    model_requested=ctx.model_requested,
                    judge_receipt=ctx.judge_receipt,
                    attempt=attempt_no,
                    model_env_source=ctx.model_source,
                )
            if ctx.provider_key == "anthropic_claude":
                return x1d_mod._call_anthropic(
                    ctx.api_key,
                    prompt,
                    ctx.model,
                    ctx.input_hash,
                    ctx.provider_key,
                    model_source=ctx.model_source,
                    artifact_base=ctx.artifact_base,
                    allow_model_fallback=ctx.allow_model_fallback,
                    model_requested=ctx.model_requested,
                    judge_receipt=ctx.judge_receipt,
                    attempt=attempt_no,
                    packet_hash=ctx.input_hash,
                    canonical_contract_hash=ctx.canonical_contract_hash or contract.contract_hash(),
                )
            return x1d_mod._call_gemini(
                ctx.api_key,
                prompt,
                ctx.model,
                ctx.input_hash,
                ctx.provider_key,
                model_source=ctx.model_source,
                artifact_base=ctx.artifact_base,
                model_requested=ctx.model_requested,
                judge_receipt=ctx.judge_receipt,
            )

        try:
            ctx.last_judge_output = _invoke_judge_with_bounded_retries(
                _dispatch,
                provider_key=ctx.provider_key,
            )
        except Exception as exc:
            raise AdapterInvokeError(str(exc)) from exc

        out = ctx.last_judge_output
        if out.provider_blocked and _is_hard_blocked(out):
            raise AdapterInvokeError(out.exact_provider_error or out.provider_status)

        return _panel_outcome_from_judge(ctx, contract, attempt=attempt)


def _is_hard_blocked(out) -> bool:
    """Retriable blocked outputs are handled inside _invoke_judge_with_bounded_retries."""
    status = str(out.provider_status or "")
    return status.startswith("BLOCKED_") and "RETRIABLE" not in status.upper()


def build_panel_adapter(ctx: X1dPanelProviderContext) -> AppsRgX1dPanelAdapter:
    if ctx.provider_key not in PROVIDERS:
        raise KeyError(f"unknown provider key: {ctx.provider_key}")
    return AppsRgX1dPanelAdapter(ctx)


__all__ = ["AppsRgX1dPanelAdapter", "build_panel_adapter"]
