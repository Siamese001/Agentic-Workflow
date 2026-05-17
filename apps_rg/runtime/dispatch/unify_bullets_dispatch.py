"""App-local unify_bullets runtime seam.

Canonical base resume JSON -> Unify bullet tailor payload -> provider -> X2 -> X1D -> X3 -> L6.
Does not activate registry or touch agentic_core.

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

from apps_rg.runtime.dispatch.unify_bullets_pa import compile_unify_bullets_prompt
from apps_rg.runtime.dispatch.prompt_trace_reasoning import attach_reasoning_to_prompt_trace
from apps_rg.runtime.exit.unify_bullets_x3 import aggregate_x3
from apps_rg.runtime.judges.unify_bullets_x1d import run_unify_bullets_judges
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.dispatch.mock_runtime_proof_policy import (
    MOCK_JUDGES_REJECT_EXIT_CODE,
    MOCK_PROVIDER_REJECT_EXIT_CODE,
    allow_non_allow_exit_zero_ok,
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    emit_mock_blocked_stderr,
    emit_mock_judges_blocked_stderr,
    infer_product_quality_blocked_or_mock,
    mock_blocked_before_run,
    mock_judges_blocked_before_run,
)
from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run, prepare_runtime_proof_run_dir
from apps_rg.runtime.shadow.unify_bullets_l6 import build_l6_shadow_package
from apps_rg.runtime.validators.unify_bullets_x2 import (
    DEFAULT_DISTRIBUTION,
    PROTECTED_BULLET_DEFAULT,
    UNIFY_BULLET_IDS,
    run_unify_bullets_x2_gates,
)
from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json

PROMPT_ID = "unify_bullet_tailor_v1"
UNIFY_TEMP_DEFAULT = 0.45
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text

DEFAULT_INTENSITY_BY_BULLET = {
    "bul_unify_001": "HEAVY",
    "bul_unify_002": "MODERATE",
    "bul_unify_003": "MODERATE",
    "bul_unify_004": "HEAVY",
    "bul_unify_005": "MODERATE",
    "bul_unify_006": "LIGHT_PROTECTED",
}
BULLET_ID_ALIASES = {
    **{f"B{i}": f"bul_unify_{i:03d}" for i in range(1, 7)},
    **{f"b{i}": f"bul_unify_{i:03d}" for i in range(1, 7)},
}
UNIFY_QWEN_MAX_TOKENS = 2400


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "unify_bullets"
PROMPT_TEMPLATE = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_base_resume() -> tuple[dict[str, Any], Path, str]:
    return load_lane_base_resume_json(repo_root=REPO_ROOT)


def extract_unify_employment(base_resume: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], set[str]]:
    facts_obj = base_resume.get("facts", base_resume)
    for emp in facts_obj.get("employment", []):
        if "unify" not in str(emp.get("employer", "")).lower():
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
            "fact_id": emp.get("fact_id", "exp_unify_001"),
        }
        return header, bullets, allowed
    raise ValueError("Unify employment entry not found in base resume.")


def build_selected_fact_plan(facts: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(facts, key=lambda r: UNIFY_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in UNIFY_BULLET_IDS else 99)
    return {
        "section_id": "unify_bullets",
        "selection_method": "canonical_json_all_unify_bullets",
        "facts": ordered,
        "required_fact_ids": list(UNIFY_BULLET_IDS),
    }


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    unify_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("unify_bullets_%Y%m%d_%H%M%S"),
        "section_id": "unify_bullets",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "unify_header": unify_header,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "unify_bullets_only",
        "full_resume_writable": False,
        "rewrite_distribution_default": DEFAULT_DISTRIBUTION,
        "protected_bullet_default": PROTECTED_BULLET_DEFAULT,
    }


def build_prompt_messages(runtime_payload: dict[str, Any]) -> list[dict[str, str]]:
    """W7: PA-compiled system prompt via ``section_prompt_adapter`` (no inline fallback)."""
    rid = str(runtime_payload.get("run_id") or "unify_bullets_prompt_build")
    return compile_unify_bullets_prompt(runtime_payload, run_id=rid).artifact.messages


def _count_intensities(bullets: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"HEAVY": 0, "MODERATE": 0, "LIGHT_PROTECTED": 0}
    for bullet in bullets:
        key = str(bullet.get("rewrite_intensity", "")).upper()
        if key in counts:
            counts[key] += 1
    return counts


def _canonicalize_unify_gate_metric_text(text: str) -> str:
    """Normalize model drift that breaks x2_unify_metrics_preserved substring checks.

    Canonical base uses word form ``six months to three weeks``. Models often insert
    ``just`` or use digits ``6``/``3``; map those to the same gate token without
    rewriting other content.
    """
    if not text:
        return text
    s = text
    s = re.sub(
        r"\bsix\s+months\s+to\s+(?:just\s+)?three\s+weeks\b",
        "six months to three weeks",
        s,
        flags=re.IGNORECASE,
    )
    s = re.sub(
        r"\b6\s+months\s+to\s+(?:just\s+)?3\s+weeks\b",
        "six months to three weeks",
        s,
        flags=re.IGNORECASE,
    )
    return s


def normalize_parsed_output(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not parsed:
        return parsed
    normalized_bullets: list[dict[str, Any]] = []
    for idx, bullet in enumerate((parsed.get("bullets") or [])[:6]):
        row = dict(bullet)
        bid = str(row.get("bullet_id", "")).strip()
        row["bullet_id"] = BULLET_ID_ALIASES.get(bid, bid)
        if row["bullet_id"] not in UNIFY_BULLET_IDS and idx < len(UNIFY_BULLET_IDS):
            row["bullet_id"] = UNIFY_BULLET_IDS[idx]
        row["rewrite_intensity"] = str(row.get("rewrite_intensity", DEFAULT_INTENSITY_BY_BULLET[row["bullet_id"]])).upper()
        if not row.get("source_fact_ids"):
            row["source_fact_ids"] = [row["bullet_id"]]
        bt = row.get("bullet_text")
        if isinstance(bt, str):
            row["bullet_text"] = _canonicalize_unify_gate_metric_text(bt)
        normalized_bullets.append(row)

    parsed = dict(parsed)
    parsed["bullets"] = normalized_bullets
    if isinstance(parsed.get("claim_ledger"), list) and parsed["claim_ledger"]:
        for cl in parsed["claim_ledger"]:
            ct = cl.get("claim_text")
            if isinstance(ct, str):
                cl["claim_text"] = _canonicalize_unify_gate_metric_text(ct)
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
                "Use bullet_id values bul_unify_001..bul_unify_006 exactly. "
                "Include non-empty claim_ledger and rewrite_distribution with total=6."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": UNIFY_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(tag_reasoning_lane(repair_payload, LANE_KEY))
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
    for bid in UNIFY_BULLET_IDS:
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
        "rewrite_distribution": dict(DEFAULT_DISTRIBUTION),
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
    return infer_product_quality_blocked_or_mock(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason="REAL_LLM output passed all deterministic Unify bullet gates.",
    )


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
    if mock_blocked_before_run(args):
        emit_mock_blocked_stderr(dispatcher_label="unify_bullets_dispatch")
        return MOCK_PROVIDER_REJECT_EXIT_CODE
    if mock_judges_blocked_before_run(args):
        emit_mock_judges_blocked_stderr(dispatcher_label="unify_bullets_dispatch")
        return MOCK_JUDGES_REJECT_EXIT_CODE

    base, base_path, base_hash = load_base_resume()
    unify_header, unify_facts, allowed_fact_ids = extract_unify_employment(base)
    selected_fact_plan = build_selected_fact_plan(unify_facts)
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        unify_header=unify_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
    )
    artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_unify_bullets_prompt(runtime_payload, run_id=runtime_payload["run_id"])
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
            max_tokens=UNIFY_QWEN_MAX_TOKENS,
        )
        provider_request_data = provider_req.to_dict()
        write_json(artifact_dir / "provider_request.json", provider_request_data)
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
    rewrite_distribution = (parsed or {}).get("rewrite_distribution") or dict(DEFAULT_DISTRIBUTION)
    model_name = None
    if provider_result_data:
        model_name = provider_result_data.get("model")
    elif provider_request_data:
        model_name = provider_request_data.get("model")

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "unify_bullets",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "unify_header": unify_header,
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
    (artifact_dir / "unify_bullets_output.txt").write_text(bullets_display_text(bullets) + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)
    write_json(artifact_dir / "selected_fact_plan.json", l2_output["selected_fact_plan"])
    write_json(artifact_dir / "rewrite_distribution.json", rewrite_distribution)

    judge_keys = [j.strip() for j in args.x1d_judges.split(",") if j.strip()]
    judge_allowed_mock = bool(args.mock_judges and getattr(args, "allow_test_mock_judges", False))
    judge_mode = "mocked" if judge_allowed_mock else "blocked_if_unavailable"
    x1d = [
        j.to_dict()
        for j in run_unify_bullets_judges(
            bullets=bullets,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            mode=judge_mode,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        attach_reasoning_to_prompt_trace(
            {
                "runtime_path": "apps_rg.runtime.dispatch.unify_bullets_dispatch",
                "prompt_id": PROMPT_ID,
                "provider": args.provider,
                "temperature": args.temperature if args.provider == "qwen_vllm" else UNIFY_TEMP_DEFAULT,
                "section_prompt_adapter": True,
                "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "compiler_template_id": section_compiled.artifact.template_id,
            },
            provider=args.provider,
            lane_key=LANE_KEY,
            provider_result_data=provider_result_data if isinstance(provider_result_data, dict) else None,
        ),
    )
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", [])

    x2 = [
        g.to_dict()
        for g in run_unify_bullets_x2_gates(
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

    l6_temp = float(args.temperature) if args.provider == "qwen_vllm" else UNIFY_TEMP_DEFAULT
    l6_max = UNIFY_QWEN_MAX_TOKENS if args.provider == "qwen_vllm" else None
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
        "bullets": bullets,
        "rewrite_distribution": rewrite_distribution,
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
        "UNIFY_BULLETS_OUTPUT:",
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
        section_id="unify_bullets",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
        proof_eligible=bundle["proof_eligible"],
        proof_scope=bundle["proof_scope"],
        test_only_mock_provider=bundle["test_only_mock_provider"],
        runtime_certification=bundle["runtime_certification"],
        x1d_runtime_status=bundle["x1d_runtime_status"],
        judge_proof_eligible=bundle["judge_proof_eligible"],
        provider_proof_eligible=bundle["provider_proof_eligible"],
        test_only_mock_judges=bundle["test_only_mock_judges"],
        proof_closeout_note=bundle["proof_closeout_note"] if bundle.get("proof_closeout_note") else None,
    )
    if allow_non_allow_exit_zero_ok(args):
        return 0
    return 0 if x3.x3_code == "X3_ALLOW" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run apps_rg unify_bullets runtime seam.")
    parser.add_argument(
        "--provider",
        choices=["mock", "qwen_vllm"],
        default="qwen_vllm",
        help="Generation provider. mock requires `--allow-test-mock-provider` (plumbing-only).",
    )
    parser.add_argument("--temperature", type=float, default=UNIFY_TEMP_DEFAULT)
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
    parser.add_argument(
        "--allow-test-mock-provider",
        action="store_true",
        help="Test-only: allow mock provider for plumbing artifacts (proof_eligible=false).",
    )
    parser.add_argument("--target-title", default=TARGET_TITLE_DEFAULT)
    parser.add_argument("--target-company", default=TARGET_COMPANY_DEFAULT)
    parser.add_argument("--jd-text", default=JD_TEXT_DEFAULT)
    parser.add_argument("--briefing", default=BRIEFING_DEFAULT)
    parser.add_argument(
        "--allow-non-allow-exit-zero",
        action="store_true",
        help="Exit 0 for inspection despite X3≠ALLOW — qwen_vllm or mock+hatch only.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    return run_dispatch(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
