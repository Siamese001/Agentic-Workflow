"""App-local ibm_narrative runtime seam.

Canonical JSON plus read-only IBM bullets artifact -> one IBM role sentence -> X1D -> X2 -> X3 -> L6.
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

from apps_rg.runtime.exit.ibm_narrative_x3 import aggregate_x3
from apps_rg.runtime.judges.ibm_narrative_x1d import run_ibm_narrative_judges
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm
from apps_rg.runtime.shadow.ibm_narrative_l6 import build_l6_shadow_package
from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
from apps_rg.runtime.validators.ibm_narrative_x2 import (
    companion_ibm_bullets_have_full_metric_bundle,
    count_ibm_narrative_metric_hits,
    run_ibm_narrative_x2_gates,
)
from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run, prepare_runtime_proof_run_dir, resolve_latest_real_l2

PROMPT_ID = "ibm_position_narrative_dispatch_v1"
NARRATIVE_TEMP_DEFAULT = 0.45
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = (
    "enterprise AI platform leadership, agentic AI systems, runtime governance, "
    "LLMOps, retrieval, production reliability, engineering leadership"
)
BRIEFING_DEFAULT = "regulated enterprise environment, platform modernization, AI governance, scalable delivery"
NARRATIVE_QWEN_MAX_TOKENS = 1200


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
BASE_POINTER = REPO_ROOT / "apps_rg" / "resume" / "base" / "active_base_resume_pointer.json"
BASE_JSON_DEFAULT = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
LANE_KEY = "ibm_narrative"


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
    ordered = sorted(
        facts,
        key=lambda r: IBM_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in IBM_BULLET_IDS else 99,
    )
    return {
        "section_id": "ibm_narrative",
        "selection_method": "canonical_json_ibm_facts",
        "facts": ordered,
        "required_fact_ids": list(IBM_BULLET_IDS),
    }


def load_companion_ibm_bullets_text() -> str:
    path = resolve_latest_real_l2(REPO_ROOT, "ibm_bullets")
    if path is None or not path.is_file():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    bullets = data.get("bullets") or []
    return "\n".join(f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}" for b in bullets)


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    ibm_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    companion_bullets_ref: str | None,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    candidate_name: str = "",
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("ibm_narrative_%Y%m%d_%H%M%S"),
        "section_id": "ibm_narrative",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "ibm_header": ibm_header,
        "candidate_name": candidate_name,
        "companion_ibm_bullets_ref": companion_bullets_ref,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "ibm_narrative_only",
        "full_resume_writable": False,
    }


def build_prompt_messages(runtime_payload: dict[str, Any], companion_text: str) -> list[dict[str, str]]:
    facts = runtime_payload["selected_fact_plan"]["facts"]
    fact_lines = "\n".join(
        f"- {fact['fact_id']}: {fact['claim_text']}"
        + (f" | metric: {fact['metric_raw']}" if fact.get("metric_raw") else "")
        for fact in facts
    )
    header = runtime_payload["ibm_header"]
    cand = str(runtime_payload.get("candidate_name") or "").strip()
    cand_line = f"Executive name from resume (optional, at most once, natural third person): {cand}.\n" if cand else ""
    companion_block = (
        f"\nACCEPTED_IBM_BULLETS (read-only; do not recap each line):\n{companion_text}\n"
        if companion_text.strip()
        else "\n(No companion ibm_bullets artifact; still avoid repeating every metric in one list.)\n"
    )
    system = (
        "You write exactly ONE polished IBM employment narrative sentence. "
        "Return RAW JSON only: first character {, last character }. No markdown fences.\n\n"
        f"READ-ONLY CONTEXT (not copy-paste openers): employer={header['employer']}, title={header['title']}, "
        f"location={header['location']}, dates={header['start_date']} to {header['end_date']}.\n"
        f"{cand_line}"
        "VOICE (mandatory):\n"
        "- Include the exact text \"IBM\" once as the employer anchor (company name).\n"
        "- Third person or implied subject only. No first person. No em dash. No inline source tags.\n"
        "- IBM should read as supporting enterprise and platform credibility, not current agentic runtime ownership.\n\n"
        "SCOPE: Use ONLY bul_ibm_001..005 facts for proof. No Unify, InsurTech, EY, education, certification, or early-career facts.\n"
        "Never use Unify-era runtime vocabulary (agentic AI, GraphRAG, multi-agent orchestration, deterministic routing, "
        "sandboxed execution, replayable traces, governed AI runtime, prompt assembly, C0, L2, Exit, UWG).\n"
        "JD and briefing are targeting context only, never proof.\n\n"
        "METRICS: If companion IBM bullets already carry $15M, 99.9%, 30%, 25%, and 50%, mention at most one metric cluster "
        "in narrative_sentence (prefer a single concrete proof such as 99.9% uptime or $15M where it fits the arc).\n\n"
        "SYNTHESIS: Complement the five bullets with connective framing; do not summarize each bullet or copy a five-word opening from them.\n\n"
        "Required JSON keys: narrative_sentence, selected_fact_plan, claim_ledger, jd_alignment, gap_notes, change_log, self_check.\n"
        "claim_ledger: array of {claim_text, source_fact_ids} with bul_ibm_001 through bul_ibm_005 only (single underscores; no typos).\n"
        "Every substantive clause in narrative_sentence must appear as claim_text in claim_ledger with matching bul_ibm_* IDs."
    )
    user = f"""
Target title (context only): {runtime_payload['target_title']}
Target company (context only): {runtime_payload['target_company']}
JD (context only): {runtime_payload['jd_text']}
Briefing (context only): {runtime_payload['briefing']}

CANONICAL IBM FACTS:
{fact_lines}
{companion_block}
Write one narrative_sentence only: enterprise platform credibility at IBM, third person, one period at the end, under 52 words.
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


def normalize_parsed_output(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not parsed:
        return parsed
    out = dict(parsed)
    narrative = str(out.get("narrative_sentence", "")).strip()
    if narrative and not narrative.endswith((".", "!", "?")):
        narrative += "."
    out["narrative_sentence"] = narrative
    if not isinstance(out.get("selected_fact_plan"), dict):
        out["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    ledger = out.get("claim_ledger")
    if isinstance(ledger, list):
        for entry in ledger:
            raw_ids = entry.get("source_fact_ids")
            if not isinstance(raw_ids, list):
                continue
            fixed: list[str] = []
            for fid in raw_ids:
                s = str(fid)
                while "bul_ibm__" in s:
                    s = s.replace("bul_ibm__", "bul_ibm_", 1)
                if re.match(r"^bul_ib_\d{3}$", s):
                    s = "bul_ibm_" + s[7:]
                fixed.append(s)
            entry["source_fact_ids"] = fixed
    if not out.get("claim_ledger"):
        out["claim_ledger"] = [
            {
                "claim_text": narrative,
                "source_fact_ids": list(IBM_BULLET_IDS),
            }
        ]
    if not isinstance(out.get("jd_alignment"), dict):
        out["jd_alignment"] = {"targeting_only": True, "jd_used_as_proof": False}
    out.setdefault("gap_notes", [])
    out.setdefault("change_log", [])
    out.setdefault("self_check", {"normalized_by_dispatch": True})
    return out


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
                "narrative_sentence: third person, IBM anchor, bul_ibm_* claim_ledger only, no em dash, no inline source tags."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": NARRATIVE_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(repair_payload)
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def retry_qwen_for_metric_budget(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any],
    companion_text: str,
    runtime_payload: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """One repair turn when companion bullets already carry the full metric bundle."""
    narrative = str(parsed.get("narrative_sentence") or "")
    if not companion_text or not companion_ibm_bullets_have_full_metric_bundle(companion_text):
        return raw_output, parsed
    if count_ibm_narrative_metric_hits(narrative) <= 1:
        return raw_output, parsed
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                "DETERMINISTIC_REVISION: Accepted IBM bullets already list $15M, 99.9%, 30%, 25%, and 50%. "
                "narrative_sentence MUST cite at most ONE numeric proof from that set (for example only 99.9% uptime "
                "or only $15M, never both). Remove extra dollar amounts and extra percentage tokens. "
                "Return one full JSON object again with the same required keys."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": NARRATIVE_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(repair_payload)
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, parsed
    new_raw = result.raw_model_output
    new_parsed, _err = parse_model_json(new_raw)
    if new_parsed is None:
        return raw_output, parsed
    new_parsed = normalize_parsed_output(new_parsed, runtime_payload)
    prior_log = list(parsed.get("change_log") or []) if isinstance(parsed.get("change_log"), list) else []
    new_parsed["change_log"] = prior_log + list(new_parsed.get("change_log") or [])
    new_parsed["change_log"].append(
        {"operation": "metric_budget_repair", "reason": "companion_ibm_bullets_full_metrics"}
    )
    return new_raw, new_parsed


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    name = str(runtime_payload.get("candidate_name") or "").strip()
    lead = f"{name} " if name else ""
    narrative = (
        f"{lead}concentrated enterprise cloud and analytics platform outcomes at IBM by tightening reliability posture, "
        "migration cadence, and client-facing instrumentation so regulated-sector delivery stayed predictable, "
        "with production uptime held at 99.9%."
    )
    return {
        "narrative_sentence": narrative,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": [
            {
                "claim_text": narrative,
                "source_fact_ids": ["bul_ibm_001"],
            }
        ],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [{"operation": "mocked_runtime_slice", "reason": "provider not requested"}],
        "self_check": {"one_sentence": True, "third_person": True},
    }


def infer_product_quality(runtime_generation_status: str, x2_gates: list[dict[str, Any]]) -> tuple[str, str]:
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    if failed:
        return "FAIL", f"X2 failed gates: {failed}"
    if runtime_generation_status != "REAL_LLM":
        return "PARTIAL", "Mocked or blocked generation proves plumbing only."
    return "PASS", "REAL_LLM output passed all deterministic ibm_narrative gates."


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
    candidate_name = str(
        base.get("candidate_name") or (base.get("header") or {}).get("name") or ""
    ).strip()
    ibm_header, ibm_facts, allowed_fact_ids = extract_ibm_employment(base)
    selected_fact_plan = build_selected_fact_plan(ibm_facts)
    companion_text = load_companion_ibm_bullets_text()
    ibm_bullets_l2 = resolve_latest_real_l2(REPO_ROOT, "ibm_bullets")
    companion_ref = (
        str(ibm_bullets_l2.relative_to(REPO_ROOT))
        if ibm_bullets_l2 is not None and companion_text
        else None
    )
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        ibm_header=ibm_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        companion_bullets_ref=companion_ref,
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
        candidate_name=candidate_name,
    )
    artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    (artifact_dir / "companion_ibm_bullets_context.txt").write_text(
        companion_text or "(none)\n", encoding="utf-8"
    )

    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    messages = build_prompt_messages(runtime_payload, companion_text)
    compiled_prompt = json.dumps(messages, indent=2)
    prompt_hash = sha16(compiled_prompt)
    write_json(artifact_dir / "runtime_payload.json", runtime_payload)
    (artifact_dir / "compiled_prompt.txt").write_text(compiled_prompt, encoding="utf-8")

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
            max_tokens=NARRATIVE_QWEN_MAX_TOKENS,
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
                raw_output, parsed = retry_qwen_for_metric_budget(
                    messages,
                    provider_payload,
                    raw_output,
                    parsed,
                    companion_text,
                    runtime_payload,
                )
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

    narrative = str((parsed or {}).get("narrative_sentence") or "").strip()
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    model_name = None
    if provider_result_data:
        model_name = provider_result_data.get("model")
    elif provider_request_data:
        model_name = provider_request_data.get("model")

    judge_keys = [j.strip() for j in args.x1d_judges.split(",") if j.strip()]
    judge_mode = "mocked" if args.mock_judges else "blocked_if_unavailable"
    x1d = [
        j.to_dict()
        for j in run_ibm_narrative_judges(
            narrative_sentence=narrative,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            companion_bullets_context=companion_text,
            mode=judge_mode,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    x2 = [
        g.to_dict()
        for g in run_ibm_narrative_x2_gates(
            narrative_sentence=narrative,
            parsed_output=parsed,
            claim_ledger=claim_ledger,
            jd_text=args.jd_text,
            runtime_generation_status=runtime_generation_status,
            companion_bullet_texts=companion_text or None,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
        )
    ]

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "ibm_narrative",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "ibm_header": ibm_header,
        "narrative_sentence": narrative,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment") or {"targeting_only": True},
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
    }
    write_json(artifact_dir / "l2_output.json", l2_output)
    (artifact_dir / "ibm_narrative_output.txt").write_text(narrative + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        {
            "runtime_path": "apps_rg.runtime.dispatch.ibm_narrative_dispatch",
            "prompt_id": PROMPT_ID,
            "provider": args.provider,
            "temperature": args.temperature if args.provider == "qwen_vllm" else NARRATIVE_TEMP_DEFAULT,
        },
    )

    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2)
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )

    product_quality_status, product_quality_reason = infer_product_quality(runtime_generation_status, x2)
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    write_json(artifact_dir / "l2_output.json", l2_output)

    x3 = aggregate_x3(
        resume_display_text=narrative or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
    )
    write_json(artifact_dir / "x3_disposition.json", x3.to_dict())

    l6_temp = float(args.temperature) if args.provider == "qwen_vllm" else NARRATIVE_TEMP_DEFAULT
    l6_max = NARRATIVE_QWEN_MAX_TOKENS if args.provider == "qwen_vllm" else None
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
            "narrative_sentence": narrative,
            "product_quality_status": product_quality_status,
            "x3_code": x3.x3_code,
        },
    )

    lines = [
        "IBM_NARRATIVE_OUTPUT:",
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
    pratt = (provider_request_data or {}).get("provider_attempted", False)
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="ibm_narrative",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
    )
    return 0 if args.allow_non_allow_exit_zero else (0 if x3.x3_code == "X3_ALLOW" else 2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run apps_rg ibm_narrative runtime seam.")
    parser.add_argument("--provider", choices=["mock", "qwen_vllm"], default="mock")
    parser.add_argument("--temperature", type=float, default=NARRATIVE_TEMP_DEFAULT)
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
