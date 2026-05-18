"""[LEGACY] unify_narrative ``python -m`` seam — **retired from canonical CLI**.

Canonical path: ``python -m apps_rg --section unify_narrative`` via
``apps_rg.runtime.sections.unify_narrative_lane`` and
``apps_rg.runtime.orchestration.canonical_dispatch``.

This module remains for diagnostics and backward-compatible ``python -m`` only.
Do not extend with new runtime logic. Retirement note directory:
``artifacts/apps_rg/unify_narrative_dispatch_retirement/``.

**W3:** ``declared_temporary_slice``.
"""
from __future__ import annotations

from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_DECLARED_TEMPORARY_SLICE,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_DECLARED_TEMPORARY_SLICE
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from apps_rg.runtime.dispatch.unify_narrative_pa import compile_unify_narrative_prompt
from apps_rg.runtime.dispatch.prompt_trace_reasoning import attach_reasoning_to_prompt_trace
from apps_rg.runtime.exit.unify_narrative_x3 import aggregate_x3
from apps_rg.runtime.judges.unify_narrative_x1d import run_unify_narrative_judges
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.qwen_offline_contract_stub import (
    effective_offline_contract_stub_enabled,
    synthetic_qwen_provider_result,
)
from apps_rg.runtime.shadow.unify_narrative_l6 import build_l6_shadow_package
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    MOCK_JUDGES_REJECT_EXIT_CODE,
    allow_non_allow_exit_zero_ok,
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    emit_mock_judges_blocked_stderr,
    infer_product_quality_blocked_or_mock,
    mock_judges_blocked_before_run,
)
from apps_rg.runtime.runtime_proof_layout import (
    finalize_runtime_proof_run,
    prepare_runtime_proof_run_dir,
    resolve_effective_lane_l2_path,
)
from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.sections.unify_narrative_lane import (
    build_mock_output,
    build_selected_fact_plan,
    extract_unify_employment,
    normalize_unify_narrative_parsed,
)

normalize_parsed_output = normalize_unify_narrative_parsed

PROMPT_ID = "unify_position_narrative_v1"
NARRATIVE_TEMP_DEFAULT = 0.45
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text
NARRATIVE_QWEN_MAX_TOKENS = 1200
ACCEPTED_COMPANION_STATUS = "ACCEPTED_FINALIZED"


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "unify_narrative"


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_base_resume() -> tuple[dict[str, Any], Path, str]:
    return load_lane_base_resume_json(repo_root=REPO_ROOT)


def load_companion_bullets_context() -> dict[str, Any]:
    """Resolve finalized Unify bullets before narrative generation.

    The narrative lane must not silently proceed as a production-quality lane when
    bullets are absent, mocked, failed, or not X3-allowed. This keeps the Unify
    workflow bullet-first: bullets -> X2/X1D/X3 -> narrative.
    """
    path = resolve_effective_lane_l2_path(REPO_ROOT, "unify_bullets")
    base: dict[str, Any] = {
        "status": "MISSING",
        "reason": "unify_bullets_l2_output_not_found",
        "text": "",
        "l2_ref": None,
        "x3_ref": None,
        "bullet_ids": [],
        "product_quality_status": "UNKNOWN",
        "x3_code": "UNKNOWN",
    }
    if path is None or not path.is_file():
        return base
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {**base, "status": "INVALID", "reason": f"unify_bullets_l2_unreadable:{type(exc).__name__}", "l2_ref": str(path)}

    bullets = data.get("bullets") or []
    bullet_ids = [str(b.get("bullet_id")) for b in bullets if isinstance(b, dict)]
    text = "\n".join(f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}" for b in bullets if isinstance(b, dict))
    product_quality_status = str(data.get("product_quality_status") or "UNKNOWN")
    x3_path = path.parent / "x3_disposition.json"
    x3_code = "UNKNOWN"
    if x3_path.is_file():
        try:
            x3 = json.loads(x3_path.read_text(encoding="utf-8"))
            x3_code = str(x3.get("x3_code") or x3.get("x3_disposition") or "UNKNOWN")
        except (json.JSONDecodeError, OSError):
            x3_code = "UNREADABLE"

    expected_ids = list(UNIFY_BULLET_IDS)
    status = ACCEPTED_COMPANION_STATUS
    reasons: list[str] = []
    if data.get("section_id") != "unify_bullets":
        reasons.append("section_id_not_unify_bullets")
    if bullet_ids != expected_ids:
        reasons.append("bullet_ids_not_exact_bul_unify_001_to_006")
    if product_quality_status != "PASS":
        reasons.append(f"product_quality_status_not_PASS:{product_quality_status}")
    if x3_code != "X3_ALLOW":
        reasons.append(f"x3_not_ALLOW:{x3_code}")
    if reasons:
        status = "NOT_FINALIZED"

    rel_l2 = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    x3_ref_val: str | None = None
    if x3_path.is_file():
        x3_ref_val = str(x3_path.relative_to(REPO_ROOT)) if x3_path.is_relative_to(REPO_ROOT) else str(x3_path)

    return {
        "status": status,
        "reason": ";".join(reasons) if reasons else "ok",
        "text": text,
        "l2_ref": rel_l2,
        "x3_ref": x3_ref_val,
        "bullet_ids": bullet_ids,
        "product_quality_status": product_quality_status,
        "x3_code": x3_code,
    }


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    unify_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    companion_bullets_ref: str | None,
    companion_bullets_status: str,
    companion_bullets_reason: str,
    companion_bullet_ids: list[str],
    companion_x3_code: str,
    companion_product_quality_status: str,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    candidate_name: str = "",
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("unify_narrative_%Y%m%d_%H%M%S"),
        "section_id": "unify_narrative",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "unify_header": unify_header,
        "candidate_name": candidate_name,
        "companion_unify_bullets_ref": companion_bullets_ref,
        "companion_unify_bullets_status": companion_bullets_status,
        "companion_unify_bullets_reason": companion_bullets_reason,
        "companion_unify_bullet_ids": companion_bullet_ids,
        "companion_unify_bullets_x3_code": companion_x3_code,
        "companion_unify_bullets_product_quality_status": companion_product_quality_status,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "unify_narrative_only",
        "full_resume_writable": False,
    }


def build_prompt_messages(runtime_payload: dict[str, Any], companion_text: str) -> list[dict[str, str]]:
    """W7: PA-compiled system prompt via ``section_prompt_adapter`` (no inline fallback)."""
    rid = str(runtime_payload.get("run_id") or "unify_narrative_prompt_build")
    return compile_unify_narrative_prompt(runtime_payload, companion_text, run_id=rid).artifact.messages


def parse_model_json(raw: str) -> tuple[dict[str, Any] | None, str]:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed, ""
    except json.JSONDecodeError as exc:
        return None, f"JSON parse failed: {exc}"
    return None, "Model output was not a JSON object."


def retry_qwen_for_parse(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parse_error: str,
) -> tuple[str, dict[str, Any] | None, str]:
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                f"JSON INVALID: {parse_error}. Return one NEW compact JSON object only. "
                "Keys: narrative_sentence (one sentence), selected_fact_plan, claim_ledger, jd_alignment, "
                "gap_notes, change_log, self_check. "
                "jd_alignment MUST include selected_jd_themes (non-empty), selected_briefing_themes (array; "
                "non-empty when briefing exists in payload), targeting_rationale (non-empty), "
                "jd_used_as_proof:false, briefing_used_as_proof:false. "
                "Every claim_ledger row MUST have non-empty claim_text and non-empty source_fact_ids from "
                "ALLOWED_SOURCE_FACT_IDS in C0. "
                "narrative_sentence: third person, <=58 words, <=360 characters, no em dash, no inline source tags."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": NARRATIVE_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def infer_product_quality(runtime_generation_status: str, x2_gates: list[dict[str, Any]]) -> tuple[str, str]:
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    return infer_product_quality_blocked_or_mock(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason="REAL_LLM output passed all deterministic unify_narrative gates.",
    )


def write_x2_gate_outputs(path: Path, gates: list[dict[str, Any]]) -> None:
    failed = [g["gate_id"] for g in gates if not g["pass"]]
    write_json(
        path,
        {
            "gates": gates,
            "failed_gates": failed,
            "x2_passed": sum(1 for g in gates if g["pass"]),
            "x2_failed": len(failed),
            "total_x2_gates": len(gates),
        },
    )


def run_dispatch(args: argparse.Namespace) -> int:
    if mock_judges_blocked_before_run(args):
        emit_mock_judges_blocked_stderr(dispatcher_label="unify_narrative_dispatch")
        return MOCK_JUDGES_REJECT_EXIT_CODE

    base, base_path, base_hash = load_base_resume()
    candidate_name = str(
        base.get("candidate_name") or (base.get("header") or {}).get("name") or ""
    ).strip()
    unify_header, unify_facts, allowed_fact_ids = extract_unify_employment(base)
    selected_fact_plan = build_selected_fact_plan(
        unify_facts,
        role_narrative=str(unify_header.get("role_narrative") or ""),
        employment_fact_id=str(unify_header.get("fact_id") or "exp_unify_001"),
    )
    companion_context = load_companion_bullets_context()
    companion_text = str(companion_context.get("text") or "")
    companion_ref = companion_context.get("l2_ref") if companion_text else None
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        unify_header=unify_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        companion_bullets_ref=companion_ref,
        companion_bullets_status=str(companion_context.get("status") or "UNKNOWN"),
        companion_bullets_reason=str(companion_context.get("reason") or ""),
        companion_bullet_ids=list(companion_context.get("bullet_ids") or []),
        companion_x3_code=str(companion_context.get("x3_code") or "UNKNOWN"),
        companion_product_quality_status=str(companion_context.get("product_quality_status") or "UNKNOWN"),
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
        candidate_name=candidate_name,
    )
    artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    write_json(artifact_dir / "companion_unify_bullets_context.json", companion_context)
    (artifact_dir / "companion_unify_bullets_context.txt").write_text((companion_text or "(none)") + "\n", encoding="utf-8")

    from apps_rg.runtime.qwen_transport_diag import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )

    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_unify_narrative_prompt(
        runtime_payload,
        companion_text,
        run_id=runtime_payload["run_id"],
    )
    messages = section_compiled.artifact.messages
    compiled_prompt = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    prompt_hash = sha16(compiled_prompt)
    write_json(artifact_dir / "runtime_payload.json", runtime_payload)
    (artifact_dir / "compiled_prompt.txt").write_text(
        json.dumps(messages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_json(
        artifact_dir / "compiled_prompt_artifact.json",
        {
            "section_id": section_compiled.section_id,
            "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
            "compiler_template_id": section_compiled.artifact.template_id,
            "pa_prompt_hash": section_compiled.artifact.prompt_hash,
            "dispatch_sha256_prompt16": prompt_hash,
            "slot_count": section_compiled.artifact.slot_count,
        },
    )

    provider_request_data = None
    provider_result_data = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "BLOCKED"

    provider_req, provider_payload = build_qwen_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=NARRATIVE_QWEN_MAX_TOKENS,
    )
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_request_data.get("model") or DEFAULT_QWEN_MODEL)
    if effective_offline_contract_stub_enabled():
        stub_doc = normalize_unify_narrative_parsed(build_mock_output(runtime_payload), runtime_payload)
        stub_raw = json.dumps(stub_doc or {}, sort_keys=True, separators=(",", ":"))
        result = synthetic_qwen_provider_result(raw_model_output=stub_raw, requested_model=req_model)
    else:
        result = call_qwen_vllm(tag_reasoning_lane(provider_payload, LANE_KEY))
    provider_result_data = result.to_dict()
    raw_output = result.raw_model_output
    runtime_generation_status = result.runtime_generation_status
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    if result.runtime_generation_status == "REAL_LLM":
        parsed, parse_error = parse_model_json(raw_output)
        if parsed is None:
            raw_output, parsed, parse_error = retry_qwen_for_parse(
                messages, provider_payload, raw_output, parse_error
            )
        if parsed is not None:
            parsed = normalize_parsed_output(parsed, runtime_payload)
    else:
        parsed = None
        parse_error = result.exact_provider_error or "provider blocked"

    narrative = str((parsed or {}).get("narrative_sentence") or "").strip()
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    model_name = None
    if provider_result_data:
        model_name = provider_result_data.get("model")
    elif provider_request_data:
        model_name = provider_request_data.get("model")

    judge_keys = [j.strip() for j in args.x1d_judges.split(",") if j.strip()]
    judge_allowed_mock = bool(args.mock_judges and getattr(args, "allow_test_mock_judges", False))
    judge_mode = "mocked" if judge_allowed_mock else "blocked_if_unavailable"
    x1d = [
        j.to_dict()
        for j in run_unify_narrative_judges(
            narrative_sentence=narrative,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            companion_bullets_context=companion_text,
            mode=judge_mode,
            artifact_base=artifact_dir,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    x2 = [
        g.to_dict()
        for g in run_unify_narrative_x2_gates(
            narrative_sentence=narrative,
            parsed_output=parsed,
            claim_ledger=claim_ledger,
            jd_text=args.jd_text,
            briefing_text=str(args.briefing or ""),
            runtime_generation_status=runtime_generation_status,
            companion_bullet_texts=companion_text or None,
            companion_bullets_status=str(companion_context.get("status") or "UNKNOWN"),
            companion_bullets_reason=str(companion_context.get("reason") or ""),
            candidate_name=candidate_name,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
            allowed_fact_ids=allowed_fact_ids,
            artifacts_dir=artifact_dir,
        )
    ]

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "unify_narrative",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "unify_header": unify_header,
        "companion_unify_bullets_context": companion_context,
        "narrative_sentence": narrative,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment") or {"targeting_only": True},
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
    }
    (artifact_dir / "unify_narrative_output.txt").write_text(narrative + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        attach_reasoning_to_prompt_trace(
            {
                "runtime_path": "apps_rg.runtime.dispatch.unify_narrative_dispatch",
                "prompt_id": PROMPT_ID,
                "provider": args.provider,
                "temperature": args.temperature,
                "section_prompt_adapter": True,
                "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "compiler_template_id": section_compiled.artifact.template_id,
            },
            provider=args.provider,
            lane_key=LANE_KEY,
            provider_result_data=provider_result_data if isinstance(provider_result_data, dict) else None,
        ),
    )

    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2)
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )

    product_quality_status, product_quality_reason = infer_product_quality(runtime_generation_status, x2)

    x3 = aggregate_x3(
        resume_display_text=narrative or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
    )
    write_json(artifact_dir / "x3_disposition.json", x3.to_dict())

    bundle = compute_lane_proof_bundle(
        args,
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
    )
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    write_json(artifact_dir / "l2_output.json", l2_output)

    l6_temp = float(args.temperature)
    l6_max = NARRATIVE_QWEN_MAX_TOKENS
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    rl2 = {
        "provider_attempted": args.provider,
        "runtime_generation_status": runtime_generation_status,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "raw_model_output": raw_output,
        "narrative_sentence": narrative,
        "product_quality_status": product_quality_status,
        "x3_code": x3.x3_code,
    }
    attach_lane_proof_bundle_fields(
        rl2,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )

    write_json(
        artifact_dir / "real_l2_generation_result.json",
        rl2,
    )

    lines = [
        "UNIFY_NARRATIVE_OUTPUT:",
        narrative if narrative else f"BLOCKED: {parse_error}",
        "",
        "X1D_LLM_JUDGE_OUTPUTS:",
        "| Provider | Mode | Status | Score | Pass | Decisive Failure |",
        "|---|---|---|---:|---|---|",
    ]
    for judge in x1d:
        lines.append(
            f"| {judge['provider_name']} | {judge['evaluator_mode']} | {judge.get('provider_status')} | "
            f"{judge.get('score')} | {judge.get('pass')} | {judge.get('decisive_failure')} |"
        )
    lines.extend(["", "X2_DETERMINISTIC_GATE_OUTPUTS:"])
    for gate in x2:
        lines.append(f"- {gate['gate_id']}: {'PASS' if gate['pass'] else 'FAIL'}")
    lines.extend(["", "X3_DISPOSITION:", json.dumps(x3.to_dict(), indent=2), "", "L6_SHADOW_EVAL_PACKAGE:", str(artifact_dir / "l6_shadow_eval_package.json"), "offline_only=true"])
    output_text = "\n".join(lines)
    (artifact_dir / "command_output.txt").write_text(output_text + "\n", encoding="utf-8")
    print(output_text)
    prq = str((provider_request_data or {}).get("provider_requested", args.provider))
    pratt = (provider_request_data or {}).get("provider_attempted", args.provider)
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="unify_narrative",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
    )
    if allow_non_allow_exit_zero_ok(args):
        return 0
    return 0 if x3.x3_code == "X3_ALLOW" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run apps_rg unify_narrative runtime seam.")
    parser.add_argument(
        "--provider",
        choices=["qwen_vllm"],
        default="qwen_vllm",
        help="Generation provider (qwen_vllm only). Offline tests: set APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1.",
    )
    parser.add_argument("--temperature", type=float, default=NARRATIVE_TEMP_DEFAULT)
    parser.add_argument("--x1d-judges", default="gemini_pro,openai_chatgpt,anthropic_claude")
    parser.add_argument(
        "--mock-judges",
        action="store_true",
        help=(
            "Use mocked judge rows for contract-test plumbing only. Blocked unless paired with "
            "`--allow-test-mock-judges`."
        ),
    )
    parser.add_argument(
        "--allow-test-mock-judges",
        action="store_true",
        help=(
            "Test-only hatch: allow `--mock-judges`. Emits judge_proof_eligible=false and proof_eligible=false "
            "(never runtime certification)."
        ),
    )
    parser.add_argument("--target-title", default=TARGET_TITLE_DEFAULT)
    parser.add_argument("--target-company", default=TARGET_COMPANY_DEFAULT)
    parser.add_argument("--jd-text", default=JD_TEXT_DEFAULT)
    parser.add_argument("--briefing", default=BRIEFING_DEFAULT)
    parser.add_argument(
        "--allow-non-allow-exit-zero",
        action="store_true",
        help="Exit 0 for inspection despite X3≠ALLOW — does not bypass mock-judge blocks.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    return run_dispatch(build_parser().parse_args(argv))


if __name__ == "__main__":
    from apps_rg.runtime.deprecated_runtime_cli import exit_deprecated_dispatch_cli

    raise SystemExit(exit_deprecated_dispatch_cli(section="unify_narrative"))
