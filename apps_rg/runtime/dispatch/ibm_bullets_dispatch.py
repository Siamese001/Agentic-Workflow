"""App-local ibm_bullets runtime seam.

Canonical base resume JSON -> IBM bullet tailor payload -> provider -> X1D -> X2 -> X3 -> L6.
Does not activate registry or modify the shared governed-runtime spine package under apps_rg sibling paths.

**W3:** ``declared_temporary_slice`` — section runtime proof seam; see ``w3_execution_path_convergence_f8e3c1.md``.
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

from apps_rg.runtime.dispatch.ibm_bullets_pa import compile_ibm_bullets_prompt
from apps_rg.runtime.exit.ibm_bullets_x3 import aggregate_x3
from apps_rg.runtime.judges.ibm_bullets_x1d import run_ibm_bullets_judges
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm
from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run, prepare_runtime_proof_run_dir
from apps_rg.runtime.shadow.ibm_bullets_l6 import build_l6_shadow_package
from apps_rg.runtime.validators.ibm_bullets_x2 import (
    IBM_BULLET_IDS,
    IBM_DEFAULT_DISTRIBUTION,
    run_ibm_bullets_x2_gates,
)

PROMPT_ID = "ibm_bullet_tailor_dispatch_v1"
IBM_TEMP_DEFAULT = 0.45
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = (
    "enterprise AI platform leadership, agentic AI systems, runtime governance, "
    "LLMOps, retrieval, production reliability, engineering leadership"
)
BRIEFING_DEFAULT = "regulated enterprise environment, platform modernization, AI governance, scalable delivery"

DEFAULT_INTENSITY_BY_BULLET = {
    "bul_ibm_001": "MODERATE",
    "bul_ibm_002": "MODERATE",
    "bul_ibm_003": "MODERATE",
    "bul_ibm_004": "LIGHT_PROTECTED",
    "bul_ibm_005": "LIGHT_PROTECTED",
}
BULLET_ID_ALIASES = {
    **{f"I{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
    **{f"i{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
    **{f"B{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
    **{f"b{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
}
IBM_QWEN_MAX_TOKENS = 2200


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
BASE_POINTER = REPO_ROOT / "apps_rg" / "resume" / "base" / "active_base_resume_pointer.json"
BASE_JSON_DEFAULT = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
LANE_KEY = "ibm_bullets"


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


def extract_ibm_employment(base_resume: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], set[str]]:
    facts_obj = base_resume.get("facts", base_resume)
    for emp in facts_obj.get("employment", []):
        if "ibm" not in str(emp.get("employer", "")).lower():
            continue
        bullets: list[dict[str, Any]] = []
        allowed: set[str] = set()
        for bullet in emp.get("bullets", []):
            bid = bullet.get("bullet_id")
            if not bid:
                continue
            allowed.add(bid)
            row = {
                "fact_id": bid,
                "claim_text": bullet.get("text", ""),
                "source_employment": emp.get("employer"),
                "has_metric": bool(bullet.get("has_metric")),
                "metric_raw": bullet.get("metric_raw", "") if bullet.get("has_metric") else "",
                "domain": bullet.get("domain", ""),
                "technologies": bullet.get("technologies", []),
            }
            bullets.append(row)
            if row.get("metric_raw"):
                allowed.add(f"{bid}_metric_{sha16(row['metric_raw'])[:8]}")
        header = {
            "employer": emp.get("employer"),
            "title": emp.get("title"),
            "location": emp.get("location"),
            "start_date": emp.get("start_date"),
            "end_date": emp.get("end_date"),
            "is_current": emp.get("is_current"),
            "fact_id": emp.get("fact_id", "exp_ibm_001"),
        }
        return header, bullets, allowed
    raise ValueError("IBM employment entry not found in base resume.")


def build_selected_fact_plan(facts: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(facts, key=lambda r: IBM_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in IBM_BULLET_IDS else 99)
    return {
        "section_id": "ibm_bullets",
        "selection_method": "canonical_json_all_ibm_bullets",
        "facts": ordered,
        "required_fact_ids": list(IBM_BULLET_IDS),
    }


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    ibm_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("ibm_bullets_%Y%m%d_%H%M%S"),
        "section_id": "ibm_bullets",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "ibm_header": ibm_header,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "ibm_bullets_only",
        "full_resume_writable": False,
        "rewrite_distribution_default": IBM_DEFAULT_DISTRIBUTION,
    }


def build_prompt_messages(runtime_payload: dict[str, Any]) -> list[dict[str, str]]:
    """W7: PA-compiled system prompt via ``section_prompt_adapter`` (no inline fallback)."""
    rid = str(runtime_payload.get("run_id") or "ibm_bullets_prompt_build")
    return compile_ibm_bullets_prompt(runtime_payload, run_id=rid).artifact.messages


def _canonicalize_bul_ibm_source_fact_id(fid: str) -> str:
    """Normalize model typos such as ``bul_ibm__002`` → ``bul_ibm_002`` (single underscores)."""
    s = str(fid).strip()
    while "bul_ibm__" in s:
        s = s.replace("bul_ibm__", "bul_ibm_", 1)
    return s


def _normalize_fact_id_list(ids: Any) -> list[str]:
    if ids is None:
        return []
    if not isinstance(ids, list):
        return []
    return [_canonicalize_bul_ibm_source_fact_id(str(x)) for x in ids]


def _normalize_ibm_claim_ledger(parsed: dict[str, Any]) -> None:
    led = parsed.get("claim_ledger")
    if not isinstance(led, list):
        return
    for entry in led:
        if isinstance(entry, dict):
            entry["source_fact_ids"] = _normalize_fact_id_list(entry.get("source_fact_ids"))


def _count_intensities(bullets: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"HEAVY": 0, "MODERATE": 0, "LIGHT_PROTECTED": 0}
    for bullet in bullets:
        key = str(bullet.get("rewrite_intensity", "")).upper()
        if key in counts:
            counts[key] += 1
    return counts


def normalize_parsed_output(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not parsed:
        return parsed
    normalized_bullets: list[dict[str, Any]] = []
    for idx, bullet in enumerate((parsed.get("bullets") or [])[:5]):
        row = dict(bullet)
        bid = str(row.get("bullet_id", "")).strip()
        row["bullet_id"] = BULLET_ID_ALIASES.get(bid, bid)
        if row["bullet_id"] not in IBM_BULLET_IDS and idx < len(IBM_BULLET_IDS):
            row["bullet_id"] = IBM_BULLET_IDS[idx]
        row["rewrite_intensity"] = str(row.get("rewrite_intensity", DEFAULT_INTENSITY_BY_BULLET[row["bullet_id"]])).upper()
        if not row.get("source_fact_ids"):
            row["source_fact_ids"] = [row["bullet_id"]]
        row["source_fact_ids"] = _normalize_fact_id_list(row.get("source_fact_ids"))
        normalized_bullets.append(row)

    parsed = dict(parsed)
    parsed["bullets"] = normalized_bullets
    if not isinstance(parsed.get("selected_fact_plan"), dict):
        parsed["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    if not parsed.get("claim_ledger"):
        parsed["claim_ledger"] = [
            {
                "claim_text": bullet.get("bullet_text", ""),
                "source_fact_ids": list(bullet.get("source_fact_ids") or [bullet["bullet_id"]]),
            }
            for bullet in normalized_bullets
        ]
    _normalize_ibm_claim_ledger(parsed)
    dist = parsed.get("rewrite_distribution") or {}
    if not dist.get("total"):
        counts = _count_intensities(normalized_bullets)
        parsed["rewrite_distribution"] = {**counts, "total": sum(counts.values())}
    if not isinstance(parsed.get("jd_alignment"), dict):
        parsed["jd_alignment"] = {"targeting_only": True, "jd_used_as_proof": False}
    parsed.setdefault("gap_notes", [])
    parsed.setdefault("change_log", [])
    parsed.setdefault("self_check", {"normalized_by_dispatch": True})
    return parsed


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
                f"JSON INVALID: {parse_error}. Return a NEW complete compact JSON object only. "
                "Use bullet_id values bul_ibm_001..bul_ibm_005 exactly. "
                "Include non-empty claim_ledger and rewrite_distribution with total=5, HEAVY=0."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": IBM_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(repair_payload)
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


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
    by_id = {f["fact_id"]: f for f in runtime_payload["selected_fact_plan"]["facts"]}
    bullets = []
    claim_ledger = []
    for bid in IBM_BULLET_IDS:
        fact = by_id[bid]
        intensity = DEFAULT_INTENSITY_BY_BULLET[bid]
        text = fact["claim_text"]
        metric_ids = [bid]
        if fact.get("metric_raw"):
            metric_ids.append(f"{bid}_metric_{sha16(fact['metric_raw'])[:8]}")
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "rewrite_intensity": intensity,
                "has_metric": fact.get("has_metric", False),
                "metric_raw": fact.get("metric_raw") or None,
                "source_fact_ids": metric_ids,
            }
        )
        claim_ledger.append({"claim_text": text, "source_fact_ids": metric_ids})

    return {
        "bullets": bullets,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": claim_ledger,
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [{"operation": "mocked_runtime_slice", "reason": "provider not requested"}],
        "rewrite_distribution": dict(IBM_DEFAULT_DISTRIBUTION),
        "self_check": {
            "bullet_count_valid": True,
            "distribution_valid": True,
            "no_cross_contamination": True,
            "metrics_preserved": True,
        },
    }


def infer_product_quality(
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
) -> tuple[str, str]:
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    if failed:
        return "FAIL", f"X2 failed gates: {failed}"
    if runtime_generation_status != "REAL_LLM":
        return "PARTIAL", "Mocked or blocked generation proves plumbing only."
    return "PASS", "REAL_LLM output passed all deterministic IBM bullet gates."


def bullets_display_text(bullets: list[dict[str, Any]]) -> str:
    return "\n".join(f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}" for b in bullets)


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
    base, base_path, base_hash = load_base_resume()
    ibm_header, ibm_facts, allowed_fact_ids = extract_ibm_employment(base)
    selected_fact_plan = build_selected_fact_plan(ibm_facts)
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        ibm_header=ibm_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
    )
    artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_ibm_bullets_prompt(runtime_payload, run_id=runtime_payload["run_id"])
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
    runtime_generation_status = "MOCKED"

    if args.provider == "qwen_vllm":
        provider_req, provider_payload = build_qwen_request(
            messages=messages,
            prompt_hash=prompt_hash,
            input_payload_hash=input_payload_hash,
            temperature=args.temperature,
            max_tokens=IBM_QWEN_MAX_TOKENS,
        )
        provider_request_data = provider_req.to_dict()
        write_json(artifact_dir / "provider_request.json", provider_request_data)
        result = call_qwen_vllm(provider_payload)
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
    else:
        parsed = normalize_parsed_output(build_mock_output(runtime_payload), runtime_payload)
        raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        runtime_generation_status = "MOCKED"
        provider_request_data = {
            "provider_requested": "mock",
            "provider_attempted": False,
            "mock_fallback_allowed": True,
            "model": DEFAULT_QWEN_MODEL,
            "prompt_hash": prompt_hash,
            "input_payload_hash": input_payload_hash,
        }
        write_json(artifact_dir / "provider_request.json", provider_request_data)

    bullets = list((parsed or {}).get("bullets") or [])
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    rewrite_distribution = (parsed or {}).get("rewrite_distribution") or dict(IBM_DEFAULT_DISTRIBUTION)
    model_name = None
    if provider_result_data:
        model_name = provider_result_data.get("model")
    elif provider_request_data:
        model_name = provider_request_data.get("model")

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "ibm_bullets",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "ibm_header": ibm_header,
        "bullets": bullets,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment") or {"targeting_only": True},
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "rewrite_distribution": rewrite_distribution,
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
    }
    write_json(artifact_dir / "l2_output.json", l2_output)
    (artifact_dir / "ibm_bullets_output.txt").write_text(bullets_display_text(bullets) + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)
    write_json(artifact_dir / "selected_fact_plan.json", l2_output["selected_fact_plan"])
    write_json(artifact_dir / "rewrite_distribution.json", rewrite_distribution)

    judge_keys = [j.strip() for j in args.x1d_judges.split(",") if j.strip()]
    judge_mode = "mocked" if args.mock_judges else "blocked_if_unavailable"
    x1d = [
        j.to_dict()
        for j in run_ibm_bullets_judges(
            bullets=bullets,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            mode=judge_mode,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        {
            "runtime_path": "apps_rg.runtime.dispatch.ibm_bullets_dispatch",
            "prompt_id": PROMPT_ID,
            "provider": args.provider,
            "temperature": args.temperature if args.provider == "qwen_vllm" else IBM_TEMP_DEFAULT,
            "section_prompt_adapter": True,
            "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
            "compiler_template_id": section_compiled.artifact.template_id,
        },
    )

    x2 = [
        g.to_dict()
        for g in run_ibm_bullets_x2_gates(
            bullets=bullets,
            parsed_output=parsed,
            claim_ledger=claim_ledger,
            allowed_fact_ids=allowed_fact_ids,
            jd_text=args.jd_text,
            runtime_generation_status=runtime_generation_status,
            artifacts_dir=artifact_dir,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
            rewrite_distribution=rewrite_distribution,
        )
    ]
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2)
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )

    product_quality_status, product_quality_reason = infer_product_quality(runtime_generation_status, x2)
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    write_json(artifact_dir / "l2_output.json", l2_output)

    display_for_x3 = bullets_display_text(bullets)
    x3 = aggregate_x3(
        resume_display_text=display_for_x3,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
    )
    write_json(artifact_dir / "x3_disposition.json", x3.to_dict())

    l6_temp = float(args.temperature) if args.provider == "qwen_vllm" else IBM_TEMP_DEFAULT
    l6_max = IBM_QWEN_MAX_TOKENS if args.provider == "qwen_vllm" else None
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    write_json(
        artifact_dir / "real_l2_generation_result.json",
        {
            "provider_attempted": args.provider,
            "runtime_generation_status": runtime_generation_status,
            "prompt_hash": prompt_hash,
            "model": model_name,
            "raw_model_output": raw_output,
            "bullets": bullets,
            "rewrite_distribution": rewrite_distribution,
            "product_quality_status": product_quality_status,
            "x3_code": x3.x3_code,
        },
    )

    lines = [
        "IBM_BULLETS_OUTPUT:",
        bullets_display_text(bullets) if bullets else f"BLOCKED: {parse_error}",
        "",
        "REWRITE_DISTRIBUTION:",
        json.dumps(rewrite_distribution, indent=2),
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
    pratt = (provider_request_data or {}).get("provider_attempted", False)
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="ibm_bullets",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
    )
    return 0 if args.allow_non_allow_exit_zero else (0 if x3.x3_code == "X3_ALLOW" else 2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run apps_rg ibm_bullets runtime seam.")
    parser.add_argument("--provider", choices=["mock", "qwen_vllm"], default="mock")
    parser.add_argument("--temperature", type=float, default=IBM_TEMP_DEFAULT)
    parser.add_argument("--x1d-judges", default="gemini_pro,openai_chatgpt,anthropic_claude")
    parser.add_argument("--mock-judges", action="store_true")
    parser.add_argument("--target-title", default=TARGET_TITLE_DEFAULT)
    parser.add_argument("--target-company", default=TARGET_COMPANY_DEFAULT)
    parser.add_argument("--jd-text", default=JD_TEXT_DEFAULT)
    parser.add_argument("--briefing", default=BRIEFING_DEFAULT)
    parser.add_argument("--allow-non-allow-exit-zero", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    return run_dispatch(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
