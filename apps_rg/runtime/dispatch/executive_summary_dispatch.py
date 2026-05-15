"""App-local executive summary runtime seam.

This module intentionally proves one real apps_rg section path only:
canonical JSON -> executive_summary prompt payload -> provider -> X2 -> X1D -> X3 -> L6.

It does not activate registry, does not edit v1 prompts, and does not touch agentic_core.
"""
from __future__ import annotations

import argparse
import json
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on system env

from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request, call_qwen_vllm
from apps_rg.runtime.validators.executive_summary_x2 import build_sentence_claim_coverage, run_x2_gates
from apps_rg.runtime.judges.executive_summary_x1d import run_llm_judges
from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3
from apps_rg.runtime.shadow.executive_summary_l6 import build_l6_shadow_package


PROMPT_ID = "executive_summary.generate_scratch_v1"
EXEC_SUMMARY_TEMP_DEFAULT = 0.45
EXEC_SUMMARY_TEMP_RANGE = (0.35, 0.55)
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = (
    "enterprise AI platform leadership, agentic AI systems, runtime governance, "
    "LLMOps, retrieval, production reliability, engineering leadership"
)
BRIEFING_DEFAULT = "regulated enterprise environment, platform modernization, AI governance, scalable delivery"


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
BASE_POINTER = REPO_ROOT / "apps_rg" / "resume" / "base" / "active_base_resume_pointer.json"
BASE_JSON_DEFAULT = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "executive_summary"
PROMPT_TEMPLATE = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_base_resume() -> tuple[dict[str, Any], Path, str]:
    if BASE_POINTER.exists():
        pointer = json.loads(BASE_POINTER.read_text(encoding="utf-8"))
        ref = pointer.get("active_resume_path") or pointer.get("base_resume_json_ref") or "apps_rg/resume/base/amit_ayer_base_resume_v1.json"
        path = REPO_ROOT / ref
    else:
        path = BASE_JSON_DEFAULT
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw), path, hashlib.sha256(raw.encode()).hexdigest()


def extract_allowed_facts(base_resume: dict[str, Any]) -> tuple[list[dict[str, Any]], set[str]]:
    facts_obj = base_resume.get("facts", base_resume)
    selected: list[dict[str, Any]] = []
    for emp in facts_obj.get("employment", []):
        if "unify" not in str(emp.get("employer", "")).lower():
            continue
        priority = {
            "bul_unify_006": 10,
            "bul_unify_001": 9,
            "bul_unify_003": 8,
            "bul_unify_004": 7,
            "bul_unify_005": 6,
            "bul_unify_002": 5,
        }
        for bullet in emp.get("bullets", []):
            bid = bullet.get("bullet_id")
            if not bid:
                continue
            selected.append({
                "fact_id": bid,
                "claim_text": bullet.get("text", ""),
                "source_employment": emp.get("employer"),
                "priority_rank": priority.get(bid, 1),
                "metric_raw": bullet.get("metric_raw", "") if bullet.get("has_metric") else "",
                "domain": bullet.get("domain", ""),
                "technologies": bullet.get("technologies", []),
            })
    selected.sort(key=lambda row: row.get("priority_rank", 0), reverse=True)
    allowed = {row["fact_id"] for row in selected}
    for row in selected:
        if row.get("metric_raw"):
            allowed.add(f"{row['fact_id']}_metric_{sha16(row['metric_raw'])[:8]}")
    return selected, allowed


def build_selected_fact_plan(selected_facts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "section_id": "executive_summary",
        "selection_method": "canonical_json_priority_rank",
        "facts": selected_facts[:4],
        "required_fact_ids": [row["fact_id"] for row in selected_facts[:4]],
    }


def build_runtime_payload(*, base_json_path: Path, base_hash: str, selected_fact_plan: dict[str, Any], target_title: str, target_company: str, jd_text: str, briefing: str) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("exec_summary_%Y%m%d_%H%M%S"),
        "section_id": "executive_summary",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": selected_fact_plan["required_fact_ids"],
        "writable_context_scope": "executive_summary_only",
        "full_resume_writable": False,
        "monolithic_prompt_invoked": False,
        "strategic_tailor_v1_invoked": False,
    }


def build_prompt_messages(runtime_payload: dict[str, Any]) -> list[dict[str, str]]:
    facts = runtime_payload["selected_fact_plan"]["facts"]
    fact_lines = "\n".join(
        f"- {fact['fact_id']}: {fact['claim_text']}" + (f" Metric: {fact['metric_raw']}" if fact.get("metric_raw") else "")
        for fact in facts
    )
    system = (
        "You are an executive resume summary generator. Output strict JSON only. "
        "Use ONLY selected facts as proof. JD and briefing are targeting context only—never use them as proof. "
        "\n\nSTRICT PROHIBITIONS (violations fail quality gates):\n"
        "- NO first person (I, me, my, we, our).\n"
        "- NO target company presented as employer or experience.\n"
        "- NO generic filler phrases: 'Strategic leader', 'proven track record', 'dynamic', 'visionary', 'results-driven', 'passionate', 'transformative', 'market position'.\n"
        "- NO unsupported industry or regulatory claims unless directly stated in selected facts.\n"
        "- NO inline citations, source tags, or fact IDs in resume_display_text.\n"
        "- NO em dash (—).\n"
        "- NO word count targets. Fit to evidence only.\n"
        "\n\nREQUIRED STRUCTURE:\n"
        "- Every sentence in resume_display_text must map to a selected fact.\n"
        "- Every material claim must have source_fact_ids in claim_ledger.\n"
        "- Synthesize multiple facts into flowing prose—do NOT make one sentence per fact mechanically.\n"
        "- Do NOT invent bridge language unsupported by facts.\n"
        "\n\nOUTPUT FORMAT (strict JSON):\n"
        "- resume_display_text: string, executive summary text only, no source tags\n"
        "- selected_fact_plan: object, echo selected facts used\n"
        "- claim_ledger: array of objects with claim_text and source_fact_ids\n"
        "- jd_alignment: object\n"
        "- gap_notes: array\n"
        "- change_log: array\n"
        "- self_check: object\n"
    )
    user = f"""
Create an executive summary for target title: {runtime_payload['target_title']}.
Target company (targeting context ONLY, never proof): {runtime_payload['target_company']}.
JD focus (targeting context ONLY, never proof): {runtime_payload['jd_text']}.
Briefing notes (targeting context ONLY, never proof): {runtime_payload['briefing']}.

SELECTED CANONICAL FACTS (PROOF SOURCE ONLY—use ONLY these for claims):
{fact_lines}

REMEMBER:
- Use ONLY the selected facts above as proof.
- Do NOT use generic filler phrases.
- Do NOT use first person.
- Every sentence must trace to a selected fact.
- SYNTHESIZE multiple related facts into flowing, natural prose. Do NOT make one sentence per fact.
- Vary sentence structure. Do NOT start 4+ consecutive sentences with action verbs.
- Combine related achievements into compound or complex sentences.
- Return strict JSON only.
""".strip()
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


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


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    facts = runtime_payload["selected_fact_plan"]["facts"]
    by_id = {f["fact_id"]: f for f in facts}
    text = (
        "SVP Engineering leader building governed agentic AI platforms that combine deterministic routing, "
        "multi-agent orchestration, retrieval quality, policy gating, telemetry, and rollback controls for enterprise workflows. "
        "Recent platform work converted reusable AI primitives into $22M of IP-led revenue, expanded gross margin by 20%, "
        "scaled the ML engineering organization from 8 to 28 specialists, and reduced lab-to-production cycle time from six months to three weeks."
    )
    claims = [
        {"claim_text": "governed agentic AI platform with deterministic routing and multi-agent orchestration", "source_fact_ids": ["bul_unify_001"]},
        {"claim_text": "retrieval quality, policy gating, telemetry, and rollback controls", "source_fact_ids": ["bul_unify_003"]},
        {"claim_text": "$22M IP-led revenue, 20% gross margin expansion, 8 to 28 specialists", "source_fact_ids": ["bul_unify_006", f"bul_unify_006_metric_{sha16(by_id.get('bul_unify_006', {}).get('metric_raw', ''))[:8]}"]},
        {"claim_text": "reduced lab-to-production cycle from six months to three weeks", "source_fact_ids": ["bul_unify_004", f"bul_unify_004_metric_{sha16(by_id.get('bul_unify_004', {}).get('metric_raw', ''))[:8]}"]},
    ]
    return {
        "resume_display_text": text,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": claims,
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [{"operation": "mocked_runtime_slice", "reason": "provider not requested"}],
        "self_check": {"no_first_person": True, "no_inline_source_tags": True, "fit_to_evidence": True},
    }


def infer_product_quality(runtime_generation_status: str, x2_gates: list[dict[str, Any]], resume_display_text: str) -> tuple[str, str]:
    """Infer product quality with honest PARTIAL classification for stacked/bullet-like output."""
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    if failed:
        return "FAIL", f"X2 failed gates: {failed}"
    if runtime_generation_status != "REAL_LLM":
        return "PARTIAL", "Mocked or blocked generation can prove plumbing only."
    
    # Check for synthesis quality even if gates pass
    from apps_rg.runtime.validators.executive_summary_x2 import check_synthesis_quality
    synthesis_ok, synthesis_reason = check_synthesis_quality(resume_display_text)
    if not synthesis_ok:
        return "PARTIAL", f"Synthesis quality below executive summary standard: {synthesis_reason}"
    
    return "PASS", "REAL_LLM output passed all deterministic gates and synthesis quality."


def enrich_parsed_for_x2(
    parsed: dict[str, Any] | None,
    *,
    coverage: dict[str, Any],
    input_payload_hash: str,
    allowed_fact_ids: set[str],
) -> dict[str, Any] | None:
    """Attach coverage and stable hashes for X2 metadata gates (same coverage object as artifact)."""
    if parsed is None:
        return None
    enriched = dict(parsed)
    enriched["text_claim_coverage"] = coverage
    output_body = {
        key: enriched[key]
        for key in (
            "resume_display_text",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
            "text_claim_coverage",
        )
        if key in enriched
    }
    enriched["input_payload_hash"] = input_payload_hash
    enriched["output_payload_hash"] = sha16(json.dumps(output_body, sort_keys=True))
    enriched["claim_ledger_hash"] = sha16(json.dumps(enriched.get("claim_ledger") or [], sort_keys=True))
    enriched["allowed_fact_ids_hash"] = sha16(json.dumps(sorted(allowed_fact_ids), sort_keys=True))
    return enriched


def resolve_provider_model_name(
    provider_request_data: dict[str, Any] | None,
    provider_result_data: dict[str, Any] | None,
) -> str | None:
    if provider_result_data:
        model = provider_result_data.get("model")
        if model:
            return model
    if provider_request_data:
        model = provider_request_data.get("model")
        if model:
            return model
    return None


def write_x2_gate_outputs(path: Path, gates: list[dict[str, Any]]) -> None:
    failed = [g["gate_id"] for g in gates if not g["pass"]]
    passed_count = sum(1 for g in gates if g["pass"])
    failed_count = len(failed)
    write_json(
        path,
        {
            "gates": gates,
            "failed_gates": failed,
            "x2_passed": passed_count,
            "x2_failed": failed_count,
            "total_x2_gates": len(gates),
        },
    )


def run_dispatch(args: argparse.Namespace) -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    base, base_path, base_hash = load_base_resume()
    selected, allowed_fact_ids = extract_allowed_facts(base)
    selected_fact_plan = build_selected_fact_plan(selected)
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        selected_fact_plan=selected_fact_plan,
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
    )
    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    messages = build_prompt_messages(runtime_payload)
    compiled_prompt = json.dumps(messages, indent=2)
    prompt_hash = sha16(compiled_prompt)
    write_json(ARTIFACT_DIR / "runtime_payload.json", runtime_payload)
    (ARTIFACT_DIR / "compiled_prompt.txt").write_text(compiled_prompt, encoding="utf-8")

    provider_request_data = None
    provider_result_data = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "MOCKED"

    if args.provider == "qwen_vllm":
        provider_req, provider_payload = build_qwen_request(
            messages=messages,
            prompt_hash=prompt_hash,
            input_payload_hash=input_payload_hash,
            temperature=args.temperature,
        )
        provider_request_data = provider_req.to_dict()
        write_json(ARTIFACT_DIR / "provider_request.json", provider_request_data)
        result = call_qwen_vllm(provider_payload)
        provider_result_data = result.to_dict()
        raw_output = result.raw_model_output
        runtime_generation_status = result.runtime_generation_status
        write_json(ARTIFACT_DIR / "provider_response.json", provider_result_data)
        if result.runtime_generation_status == "REAL_LLM":
            parsed, parse_error = parse_model_json(raw_output)
        else:
            parsed = None
            parse_error = result.exact_provider_error or "provider blocked"
    else:
        parsed = build_mock_output(runtime_payload)
        raw_output = json.dumps(parsed, indent=2)
        runtime_generation_status = "MOCKED"
        provider_request_data = {
            "provider_requested": "mock",
            "provider_attempted": False,
            "mock_fallback_allowed": True,
            "model": DEFAULT_QWEN_MODEL,
            "prompt_hash": prompt_hash,
            "input_payload_hash": input_payload_hash,
        }
        write_json(ARTIFACT_DIR / "provider_request.json", provider_request_data)

    resume_display_text = (parsed or {}).get("resume_display_text") or raw_output or ""
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    coverage = build_sentence_claim_coverage(resume_display_text, claim_ledger, allowed_fact_ids)
    parsed_for_x2 = enrich_parsed_for_x2(
        parsed,
        coverage=coverage,
        input_payload_hash=input_payload_hash,
        allowed_fact_ids=allowed_fact_ids,
    )
    model_name = resolve_provider_model_name(provider_request_data, provider_result_data)
    selected_facts_for_x2 = (parsed or {}).get("selected_fact_plan", {}).get("facts", selected_fact_plan.get("facts", []))
    temperature = args.temperature if args.provider == "qwen_vllm" else EXEC_SUMMARY_TEMP_DEFAULT

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "executive_summary",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "product_quality_reason": "",
        "resume_display_text": resume_display_text,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment") or {"targeting_only": True},
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "text_claim_coverage": coverage,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "allowed_fact_ids_hash": (parsed_for_x2 or {}).get("allowed_fact_ids_hash"),
    }
    write_json(ARTIFACT_DIR / "l2_output.json", l2_output)
    (ARTIFACT_DIR / "resume_display_text.txt").write_text(resume_display_text + "\n", encoding="utf-8")
    write_json(ARTIFACT_DIR / "selected_fact_plan.json", l2_output["selected_fact_plan"])
    write_json(ARTIFACT_DIR / "claim_ledger.json", claim_ledger)
    write_json(ARTIFACT_DIR / "text_claim_coverage.json", coverage)

    judge_keys = [j.strip() for j in args.x1d_judges.split(",") if j.strip()]
    judge_mode = "mocked" if args.mock_judges else "blocked_if_unavailable"
    x1d = [j.to_dict() for j in run_llm_judges(resume_display_text=resume_display_text, claim_ledger=claim_ledger, judge_keys=judge_keys, mode=judge_mode)]
    write_json(ARTIFACT_DIR / "x1d_llm_judge_outputs.json", {"judges": x1d})

    trace = {
        "runtime_path": "apps_rg.runtime.dispatch.executive_summary_dispatch",
        "prompt_id": PROMPT_ID,
        "provider": args.provider,
        "temperature": temperature,
        "strategic_tailor_v1_invoked": False,
        "monolithic_prompt_invoked": False,
    }
    write_json(ARTIFACT_DIR / "prompt_selection_trace.json", trace)
    write_json(ARTIFACT_DIR / "fact_check_result.json", {"passed": False, "failed_gates": [], "status": "pending"})
    write_json(
        ARTIFACT_DIR / "real_l2_generation_result.json",
        {
            "provider_attempted": args.provider,
            "runtime_generation_status": runtime_generation_status,
            "prompt_hash": prompt_hash,
            "model": model_name,
            "input_payload_hash": input_payload_hash,
            "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
            "status": "pending",
        },
    )
    write_json(ARTIFACT_DIR / "x3_disposition.json", {"x3_code": "PENDING", "status": "pending"})
    write_json(ARTIFACT_DIR / "section_metric_receipt.json", {"status": "pending", "prompt_hash": prompt_hash})
    write_x2_gate_outputs(ARTIFACT_DIR / "x2_gate_outputs.json", [])

    x2 = [g.to_dict() for g in run_x2_gates(
        resume_display_text=resume_display_text,
        parsed_output=parsed_for_x2,
        claim_ledger=claim_ledger,
        text_claim_coverage=coverage,
        allowed_fact_ids=allowed_fact_ids,
        target_company=args.target_company,
        jd_text=args.jd_text,
        temperature=temperature,
        runtime_generation_status=runtime_generation_status,
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        artifacts_dir=ARTIFACT_DIR,
        provider_requested=args.provider,
        provider_attempted=args.provider,
        model_name=model_name,
        prompt_hash=prompt_hash,
        compiled_prompt=compiled_prompt,
        raw_output=raw_output,
        target_role=args.target_role if hasattr(args, "target_role") else None,
        selected_facts=selected_facts_for_x2,
        x1d_judges=x1d,
    )]
    write_x2_gate_outputs(ARTIFACT_DIR / "x2_gate_outputs.json", x2)
    write_json(
        ARTIFACT_DIR / "fact_check_result.json",
        {
            "passed": not [g for g in x2 if not g["pass"]],
            "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        },
    )

    product_quality_status, product_quality_reason = infer_product_quality(runtime_generation_status, x2, resume_display_text)
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    write_json(ARTIFACT_DIR / "l2_output.json", l2_output)

    x3 = aggregate_x3(
        resume_display_text=resume_display_text,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
    )
    write_json(ARTIFACT_DIR / "x3_disposition.json", x3.to_dict())

    l6 = build_l6_shadow_package(
        run_id=runtime_payload["run_id"],
        l2_output_ref=str(ARTIFACT_DIR / "l2_output.json"),
        x1d_judge_refs=[j["judge_id"] for j in x1d],
        x2_gate_refs=[g["gate_id"] for g in x2],
        x3_disposition_ref=str(ARTIFACT_DIR / "x3_disposition.json"),
    )
    write_json(ARTIFACT_DIR / "l6_shadow_eval_package.json", l6.to_dict())
    real_result = {
        "provider_attempted": args.provider,
        "provider_available": bool(provider_result_data and provider_result_data.get("provider_available")),
        "exact_provider_error": (provider_result_data or {}).get("exact_provider_error"),
        "runtime_generation_status": runtime_generation_status,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "temperature": temperature,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "allowed_fact_ids_hash": (parsed_for_x2 or {}).get("allowed_fact_ids_hash"),
        "raw_model_output": raw_output,
        "parsed_model_output": parsed_for_x2,
        "resume_display_text": resume_display_text,
        "selected_fact_plan": l2_output["selected_fact_plan"],
        "claim_ledger": claim_ledger,
        "text_claim_coverage": coverage,
        "fact_check_result": {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
        "product_quality_status": product_quality_status,
        "x3_disposition_ref": str(ARTIFACT_DIR / "x3_disposition.json"),
        "l6_shadow_eval_package_ref": str(ARTIFACT_DIR / "l6_shadow_eval_package.json"),
    }
    write_json(ARTIFACT_DIR / "real_l2_generation_result.json", real_result)
    write_json(ARTIFACT_DIR / "section_metric_receipt.json", {
        "run_id": runtime_payload["run_id"],
        "lane_id": "executive_summary",
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": product_quality_status,
        "x2_failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        "x3_code": x3.x3_code,
    })
    output_lines = []
    output_lines.append("L2_EXECUTIVE_SUMMARY_OUTPUT:")
    output_lines.append(resume_display_text if resume_display_text else f"BLOCKED: {parse_error}")
    output_lines.append("")
    output_lines.append("X1D_LLM_JUDGE_OUTPUTS:")
    output_lines.append("| Provider | Mode | Score | Threshold | Pass | Decisive Failure | Error |")
    output_lines.append("|---|---|---:|---:|---|---|---|")
    for judge in x1d:
        output_lines.append(
            f"| {judge['provider_name']} | {judge['evaluator_mode']} | {judge.get('score')} | {judge.get('threshold')} | {judge.get('pass')} | {judge.get('decisive_failure')} | {judge.get('exact_provider_error') or ''} |"
        )
    output_lines.append("")
    output_lines.append("X2_DETERMINISTIC_GATE_OUTPUTS:")
    for gate in x2:
        output_lines.append(f"- {gate['gate_id']}: {'PASS' if gate['pass'] else 'FAIL'}")
    output_lines.append("")
    output_lines.append("X3_DISPOSITION:")
    output_lines.append(json.dumps(x3.to_dict(), indent=2))
    output_lines.append("")
    output_lines.append("L6_SHADOW_EVAL_PACKAGE:")
    output_lines.append(str(ARTIFACT_DIR / "l6_shadow_eval_package.json"))
    output_lines.append("offline_only=true")
    output_text = "\n".join(output_lines)
    (ARTIFACT_DIR / "command_output.txt").write_text(output_text + "\n", encoding="utf-8")
    print(output_text)
    return 0 if args.allow_non_allow_exit_zero else (0 if x3.x3_code == "X3_ALLOW" else 2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run apps_rg executive_summary runtime seam.")
    parser.add_argument("--provider", choices=["mock", "qwen_vllm"], default="mock")
    parser.add_argument("--temperature", type=float, default=EXEC_SUMMARY_TEMP_DEFAULT)
    parser.add_argument("--x1d-judges", default="gemini_pro,openai_chatgpt,anthropic_claude")
    parser.add_argument("--mock-judges", action="store_true", help="Use mocked judge rows for plumbing tests only.")
    parser.add_argument("--target-title", default=TARGET_TITLE_DEFAULT)
    parser.add_argument("--target-company", default=TARGET_COMPANY_DEFAULT)
    parser.add_argument("--jd-text", default=JD_TEXT_DEFAULT)
    parser.add_argument("--briefing", default=BRIEFING_DEFAULT)
    parser.add_argument("--allow-non-allow-exit-zero", action="store_true", help="Return exit code 0 even when X3 blocks/reviews, useful for inspection.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())
