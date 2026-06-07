"""Bridge apps_rg GRADE_ONLY judge path to the local X1D panel runner."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.x1d_panel_harness import (
    CanonicalJudgeContract,
    JudgePanelRunner,
    PanelAdapterRegistry,
)
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    judge_contract_hash as exec_judge_contract_hash,
)
from apps_rg.runtime.judges.executive_summary_x1d import (
    JudgeOutput,
    PROVIDERS,
    _make_blocked_output,
    _mocked_output,
    resolve_x1d_provider_credentials,
)
from apps_rg.runtime.judges.executive_summary_x1d_gate_closure_map import (
    core_gate_closure_map,
)
from apps_rg.runtime.judges.section_judge_profile import resolve_section_proof_judge_model
from apps_rg.runtime.judges.x1d_panel_adapters import build_panel_adapter
from apps_rg.runtime.judges.x1d_panel_context import X1dPanelProviderContext
from apps_rg.runtime.section_judge_policy import normalize_section_id


def build_core_contract_from_packet(
    judge_packet: dict[str, Any],
    user_prompt: str,
    *,
    canonical_hash: str | None = None,
) -> CanonicalJudgeContract:
    """Map apps_rg JudgePacket to the panel CanonicalJudgeContract."""
    boundary = judge_packet.get("proof_boundary") or {}
    packet_hash = canonical_hash
    if packet_hash is None and str(judge_packet.get("judge_packet_version", "")).startswith(
        "executive_summary"
    ):
        packet_hash = exec_judge_contract_hash(judge_packet)
    return CanonicalJudgeContract(
        section_id=str(judge_packet.get("section") or "executive_summary"),
        user_prompt=user_prompt,
        deterministic_gate_summary=dict(judge_packet.get("deterministic_gate_summary") or {}),
        judge_task=str(judge_packet.get("judge_task") or "GRADE_ONLY"),
        output_schema_ref=str(judge_packet.get("rubric_ref") or ""),
        proof_boundary=dict(boundary) if boundary else None,
        canonical_hash=packet_hash,
    )


def judge_output_from_panel_raw(panel_raw: dict[str, Any] | None) -> JudgeOutput | None:
    """Rehydrate JudgeOutput saved on PanelJudgeOutcome.raw_body."""
    if not panel_raw:
        return None
    blob = panel_raw.get("judge_output")
    if not isinstance(blob, dict):
        return None
    data = dict(blob)
    pass_val = data.pop("pass", False)
    data["pass_"] = pass_val
    from dataclasses import fields as dc_fields

    field_names = {f.name for f in dc_fields(JudgeOutput)}
    kwargs = {k: v for k, v in data.items() if k in field_names}
    return JudgeOutput(**kwargs)


def run_grade_only_judges_via_core_panel(
    *,
    judge_keys: list[str],
    judge_packet: dict[str, Any],
    user_prompt: str,
    input_hash: str,
    section_id: str,
    mode: str,
    artifact_base: Path | None,
    judge_packet_ref: str | None,
    contract_hash: str | None,
) -> list[JudgeOutput]:
    """Run proof panel through the apps_rg X1D panel runner."""
    sid = normalize_section_id(section_id)
    contract = build_core_contract_from_packet(
        judge_packet,
        user_prompt,
        canonical_hash=contract_hash,
    )
    gate_summary = dict(judge_packet.get("deterministic_gate_summary") or {})
    base_receipt: dict[str, Any] = {
        "judge_packet_hash": input_hash,
        "packet_hash": input_hash,
        "canonical_contract_hash": contract.contract_hash(),
        "judge_packet_ref": judge_packet_ref,
        "candidate_output_ref": "candidate_output.resume_display_text",
        "allowed_fact_packet_ref": "allowed_fact_packet",
        "rubric_ref": judge_packet.get("rubric_ref"),
        "deterministic_gate_summary": gate_summary,
        "gate_closure_map_version": core_gate_closure_map().version,
    }

    outputs: list[JudgeOutput] = []
    contexts: dict[str, X1dPanelProviderContext] = {}
    eligible: list[str] = []

    for key in judge_keys:
        if key not in PROVIDERS:
            outputs.append(
                _make_blocked_output(
                    key,
                    input_hash,
                    "BLOCKED_PROVIDER_UNAVAILABLE",
                    "BLOCKED_PROVIDER_UNAVAILABLE",
                    f"Unknown judge provider key: {key}",
                )
            )
            continue

        if mode == "mocked":
            outputs.append(_mocked_output(key, input_hash))
            continue

        import os

        api_key, env_checked = resolve_x1d_provider_credentials(key, os.environ)
        if not api_key:
            outputs.append(
                _make_blocked_output(
                    key,
                    input_hash,
                    "BLOCKED_PROVIDER_UNAVAILABLE",
                    "BLOCKED_PROVIDER_UNAVAILABLE",
                    (
                        f"No non-empty API credential in {env_checked}; "
                        f"Gemini resolves GOOGLE_API_KEY then deprecated GEMINI_API_KEY alias."
                        if key == "gemini_pro"
                        else f"{PROVIDERS[key]['env']} environment variable not set"
                    ),
                )
            )
            continue

        resolution = resolve_section_proof_judge_model(sid, key)
        if resolution.blocked:
            blocked = _make_blocked_output(
                key,
                input_hash,
                "BLOCKED_MODEL_CONFIG",
                "BLOCKED_MODEL_CONFIG",
                resolution.block_reason or "proof judge model unavailable",
                model_name=resolution.model_requested or "unconfigured",
            )
            blocked.judge_packet_hash = base_receipt.get("judge_packet_hash")
            blocked.judge_packet_ref = judge_packet_ref
            blocked.model_requested = resolution.model_requested
            blocked.section_id = sid
            blocked.model_tier = resolution.model_tier
            blocked.proof_eligible_judge = False
            outputs.append(blocked)
            continue

        ctx = X1dPanelProviderContext(
            provider_key=key,
            api_key=api_key,
            model=resolution.model_actual,
            input_hash=input_hash,
            model_source=resolution.model_source,
            model_requested=resolution.model_requested,
            artifact_base=artifact_base,
            judge_receipt=dict(base_receipt),
            reasoning_effort=resolution.reasoning_effort,
            allow_model_fallback=False,
            canonical_contract_hash=contract.contract_hash(),
            deterministic_gate_summary=gate_summary,
        )
        contexts[key] = ctx
        eligible.append(key)

    if eligible:
        registry = PanelAdapterRegistry()
        for key in eligible:
            registry.register(build_panel_adapter(contexts[key]))
        runner = JudgePanelRunner(registry)
        panel_result = runner.run(contract, eligible, max_attempts=1)

        for panel_outcome in panel_result.outcomes:
            ctx = contexts[panel_outcome.provider_key]
            judge_out = ctx.last_judge_output or judge_output_from_panel_raw(
                panel_outcome.raw_body
            )
            if judge_out is None:
                outputs.append(
                    _make_blocked_output(
                        panel_outcome.provider_key,
                        input_hash,
                        "BLOCKED_PROVIDER_UNAVAILABLE",
                        "BLOCKED_PROVIDER_UNAVAILABLE",
                        "panel adapter returned no judge output",
                    )
                )
                continue
            judge_out = _apply_post_panel_metadata(
                judge_out,
                section_id=sid,
                ctx=contexts[panel_outcome.provider_key],
                judge_packet_ref=judge_packet_ref,
                base_receipt=base_receipt,
            )
            outputs.append(judge_out)

    return outputs


def _apply_post_panel_metadata(
    output: JudgeOutput,
    *,
    section_id: str,
    ctx: X1dPanelProviderContext,
    judge_packet_ref: str | None,
    base_receipt: dict[str, Any],
) -> JudgeOutput:
    from apps_rg.runtime.judges.section_judge_profile import (
        is_forbidden_proof_judge_model,
        resolve_section_proof_judge_model,
    )

    resolution = resolve_section_proof_judge_model(section_id, output.provider_key)
    proof_eligible = bool(
        resolution.proof_eligible_judge
        and output.evaluator_mode == "MODEL_BACKED"
        and not output.provider_blocked
    )
    fallback_used = bool(output.fallback_model)
    if output.fallback_model and is_forbidden_proof_judge_model(str(output.fallback_model)):
        proof_eligible = False
        fallback_used = True

    return replace(
        output,
        section_id=section_id,
        model_tier=resolution.model_tier,
        judge_packet_hash=base_receipt.get("judge_packet_hash"),
        judge_packet_ref=judge_packet_ref,
        proof_eligible_judge=proof_eligible,
        fallback_used=fallback_used,
    )


__all__ = [
    "build_core_contract_from_packet",
    "run_grade_only_judges_via_core_panel",
]
