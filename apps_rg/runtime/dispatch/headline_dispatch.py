"""App-local headline runtime seam.

Canonical base resume plus read-only companion artifacts -> one headline line (X | Y | Z) -> X1D -> X2 -> X3 -> L6.
Imports read-only helpers from competencies_dispatch without modifying that seam's behavior.

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

from apps_rg.runtime.dispatch.competencies_dispatch import (
    build_resume_support_blob,
    collect_employment_bullets,
    load_base_resume,
    load_companion_context,
)
from apps_rg.runtime.exit.headline_x3 import aggregate_x3
from apps_rg.runtime.judges.headline_x1d import run_headline_judges
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm
from apps_rg.runtime.shadow.headline_l6 import build_l6_shadow_package
from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run, prepare_runtime_proof_run_dir
from apps_rg.runtime.validators.headline_x2 import headline_word_count, run_headline_x2_gates

PROMPT_ID = "headline_dispatch_v1"
HEADLINE_TEMP_DEFAULT = 0.35
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = (
    "enterprise AI platform leadership, agentic AI systems, runtime governance, "
    "LLMOps, retrieval, production reliability, engineering leadership"
)
BRIEFING_DEFAULT = "regulated enterprise environment, platform modernization, AI governance, scalable delivery"
HEADLINE_QWEN_MAX_TOKENS = 900


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "headline"


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def collect_employer_names_lower(base_resume: dict[str, Any]) -> list[str]:
    facts_obj = base_resume.get("facts", base_resume)
    names: list[str] = []
    for emp in facts_obj.get("employment", []):
        e = str(emp.get("employer", "")).strip().lower()
        if e:
            names.append(e)
    return names


def build_selected_fact_plan(facts: list[dict[str, Any]], required_ids: list[str]) -> dict[str, Any]:
    return {
        "section_id": "headline",
        "selection_method": "canonical_base_resume_employment_bullets",
        "facts": facts,
        "required_fact_ids": required_ids,
    }


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("headline_%Y%m%d_%H%M%S"),
        "section_id": "headline",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "headline_only",
        "full_resume_writable": False,
    }


def build_prompt_messages(
    runtime_payload: dict[str, Any],
    companion_context: str,
    fact_lines: str,
    employer_names: str,
) -> list[dict[str, str]]:
    stub = json.dumps(
        {
            "section_id": "headline",
            "selection_method": "canonical_base_resume_employment_bullets",
            "required_fact_ids": runtime_payload["selected_fact_plan"]["required_fact_ids"],
        },
        separators=(",", ":"),
    )
    system = (
        "You write exactly ONE resume headline line. Return RAW JSON only: first character {, last character }. "
        "No markdown fences.\n\n"
        "HEADLINE RULES:\n"
        "- Format MUST be exactly: SegmentOne | SegmentTwo | SegmentThree (single spaces around pipes).\n"
        "- Total word count across all three segments MUST be between 8 and 11 words (count words as tokens separated by spaces; pipes are not words).\n"
        "- No metrics: no dollar amounts, percentages, arrows, or numeric proof.\n"
        "- No company or employer names (see FORBIDDEN_EMPLOYER_NAMES).\n"
        "- No first person, no em dash, no inline source tags.\n"
        "- JD and briefing are targeting context only, never proof.\n"
        "- Executive SVP-level tone; ATS-relevant noun phrases.\n\n"
        "OUTPUT CONTRACT:\n"
        "- headline_line: string matching the rules above\n"
        "- selected_fact_plan: ONLY this stub shape (no facts[] array): "
        f"{stub}\n"
        "- claim_ledger: array of objects with claim_text and source_fact_ids (bul_* only from canonical bullets)\n"
        "- jd_alignment: {targeting_only: true, jd_used_as_proof: false}\n"
        "- gap_notes, change_log, self_check arrays/objects as needed\n"
    )
    user = f"""
TARGET_TITLE (context only): {runtime_payload['target_title']}
TARGET_COMPANY (context only): {runtime_payload['target_company']}
JD_TEXT (context only): {runtime_payload['jd_text']}
BRIEFING (context only): {runtime_payload['briefing']}

FORBIDDEN_EMPLOYER_NAMES (do not appear anywhere in headline_line):
{employer_names}

CANONICAL_EMPLOYMENT_BULLETS (proof only; do not paste into headline):
{fact_lines}

READ_ONLY_ACCEPTED_SECTIONS (context only):
{companion_context if companion_context.strip() else "(no companion artifacts on disk)"}
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


def _fix_fact_id_typos(fid: str) -> str:
    s = str(fid)
    while "bul_ibm__" in s:
        s = s.replace("bul_ibm__", "bul_ibm_", 1)
    if re.match(r"^bul_ib_\d{3}$", s):
        s = "bul_ibm_" + s[7:]
    return s


def ensure_claim_ledger(headline: str, parsed: dict[str, Any], allowed_fact_ids: set[str]) -> None:
    ledger = list(parsed.get("claim_ledger") or [])
    if ledger:
        for entry in ledger:
            if not isinstance(entry, dict):
                continue
            raw_ids = entry.get("source_fact_ids")
            if isinstance(raw_ids, list):
                entry["source_fact_ids"] = [_fix_fact_id_typos(str(x)).split("_metric_")[0] for x in raw_ids]
        return
    default_ids = [x for x in ("bul_unify_001", "bul_ibm_001", "bul_unify_004") if x in allowed_fact_ids]
    if not default_ids:
        default_ids = sorted(allowed_fact_ids)[:3]
    parsed["claim_ledger"] = [{"claim_text": headline.strip(), "source_fact_ids": default_ids}]


def normalize_parsed_output(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
    allowed_fact_ids: set[str],
    headline_line: str,
) -> dict[str, Any] | None:
    if not parsed:
        return parsed
    out = dict(parsed)
    hl = str(out.get("headline_line") or headline_line or "").strip()
    out["headline_line"] = hl
    out["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    out.setdefault("jd_alignment", {"targeting_only": True, "jd_used_as_proof": False})
    out.setdefault("gap_notes", [])
    out.setdefault("change_log", [])
    out.setdefault("self_check", {"normalized_by_dispatch": True})
    ensure_claim_ledger(hl, out, allowed_fact_ids)
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
                f"JSON INVALID: {parse_error}. Return one compact JSON object with headline_line (X | Y | Z, 8-11 words), "
                "selected_fact_plan stub only (section_id, selection_method, required_fact_ids), claim_ledger, "
                "jd_alignment, gap_notes, change_log, self_check."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": HEADLINE_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(repair_payload)
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def retry_headline_word_and_pipe(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any],
    runtime_payload: dict[str, Any],
    allowed_fact_ids: set[str],
    reason: str,
) -> tuple[str, dict[str, Any]]:
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                f"DETERMINISTIC_REVISION: {reason}. "
                "headline_line must be exactly three non-empty segments separated by ' | ', "
                "8 to 11 total words, no employer names, no metrics, no first person."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": HEADLINE_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(repair_payload)
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, parsed
    new_raw = result.raw_model_output
    new_parsed, _e = parse_model_json(new_raw)
    if new_parsed is None:
        return raw_output, parsed
    hl = str(new_parsed.get("headline_line", "")).strip()
    new_parsed = normalize_parsed_output(new_parsed, runtime_payload, allowed_fact_ids, hl) or parsed
    if not isinstance(new_parsed.get("change_log"), list):
        new_parsed["change_log"] = []
    new_parsed["change_log"] = list(parsed.get("change_log") or []) + list(new_parsed.get("change_log") or [])
    new_parsed["change_log"].append({"operation": "headline_format_repair", "reason": reason})
    return json.dumps(new_parsed, sort_keys=True, separators=(",", ":")), new_parsed


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    hl = "AI platform governance | regulated delivery discipline | engineering leadership scale"
    return {
        "headline_line": hl,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": [
            {
                "claim_text": hl,
                "source_fact_ids": ["bul_unify_001", "bul_ibm_001", "bul_unify_004"],
            }
        ],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [{"operation": "mocked_runtime_slice", "reason": "provider not requested"}],
        "self_check": {"one_line": True, "pipe_format": True},
    }


def infer_product_quality(runtime_generation_status: str, x2_gates: list[dict[str, Any]]) -> tuple[str, str]:
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    if failed:
        return "FAIL", f"X2 failed gates: {failed}"
    if runtime_generation_status != "REAL_LLM":
        return "PARTIAL", "Mocked or blocked generation proves plumbing only."
    return "PASS", "REAL_LLM output passed all deterministic headline gates."


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
    bullet_rows, allowed_fact_ids, _bullet_lowers = collect_employment_bullets(base)
    employer_names = collect_employer_names_lower(base)
    required_ids = sorted(allowed_fact_ids)
    selected_fact_plan = build_selected_fact_plan(bullet_rows, required_ids)
    companion_context = load_companion_context()
    resume_blob = build_resume_support_blob(bullet_rows, companion_context)
    employer_blob = "\n".join(f"- {n}" for n in employer_names)

    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
    )
    artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    (artifact_dir / "companion_generated_sections.txt").write_text(companion_context or "(none)\n", encoding="utf-8")

    fact_lines = "\n".join(
        f"- {row['fact_id']}: {row['claim_text']}"
        + (f" | tech: {', '.join(row['technologies'])}" if row.get("technologies") else "")
        for row in bullet_rows
    )
    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    messages = build_prompt_messages(runtime_payload, companion_context, fact_lines, employer_blob)
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
    provider_raw_output: str | None = None

    if args.provider == "qwen_vllm":
        provider_req, provider_payload = build_qwen_request(
            messages=messages,
            prompt_hash=prompt_hash,
            input_payload_hash=input_payload_hash,
            temperature=args.temperature,
            max_tokens=HEADLINE_QWEN_MAX_TOKENS,
        )
        provider_request_data = provider_req.to_dict()
        write_json(artifact_dir / "provider_request.json", provider_request_data)
        result = call_qwen_vllm(provider_payload)
        provider_result_data = result.to_dict()
        raw_output = result.raw_model_output
        provider_raw_output = raw_output
        write_json(artifact_dir / "provider_response.json", provider_result_data)
        runtime_generation_status = result.runtime_generation_status
        if result.runtime_generation_status == "REAL_LLM":
            raw_model_output_original = raw_output
            parsed, parse_error = parse_model_json(raw_model_output_original)
            if parsed is None:
                raw_model_output_original, parsed, parse_error = retry_qwen_for_parse(
                    messages, provider_payload, raw_model_output_original, parse_error
                )
            if parsed is not None:
                hl0 = str(parsed.get("headline_line", "")).strip()
                parsed = normalize_parsed_output(parsed, runtime_payload, allowed_fact_ids, hl0)
                raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
                hl = str(parsed.get("headline_line", "")).strip()
                wc = headline_word_count(hl)
                if hl.count("|") != 2 or not (8 <= wc <= 11):
                    raw_output, parsed = retry_headline_word_and_pipe(
                        messages,
                        provider_payload,
                        raw_output,
                        parsed,
                        runtime_payload,
                        allowed_fact_ids,
                        f"word_count={wc} or pipe_format invalid",
                    )
                    if parsed is not None:
                        raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
            else:
                raw_output = raw_model_output_original
        else:
            parsed = None
            parse_error = result.exact_provider_error or "provider blocked"
    else:
        mo = build_mock_output(runtime_payload)
        parsed = normalize_parsed_output(
            mo,
            runtime_payload,
            allowed_fact_ids,
            str(mo.get("headline_line", "")),
        )
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

    headline_line = str((parsed or {}).get("headline_line") or "").strip()
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
        for j in run_headline_judges(
            headline_line=headline_line,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            companion_context=companion_context,
            mode=judge_mode,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    x2 = [
        g.to_dict()
        for g in run_headline_x2_gates(
            headline_line=headline_line,
            parsed_output=parsed,
            claim_ledger=claim_ledger,
            jd_text=args.jd_text,
            target_company=args.target_company,
            resume_support_blob=resume_blob,
            employer_names_lower=employer_names,
            allowed_fact_ids=allowed_fact_ids,
            runtime_generation_status=runtime_generation_status,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
        )
    ]

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "headline",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "headline_line": headline_line,
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
    (artifact_dir / "headline_output.txt").write_text(headline_line + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        {
            "runtime_path": "apps_rg.runtime.dispatch.headline_dispatch",
            "prompt_id": PROMPT_ID,
            "provider": args.provider,
            "temperature": args.temperature if args.provider == "qwen_vllm" else HEADLINE_TEMP_DEFAULT,
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
        resume_display_text=headline_line or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
    )
    write_json(artifact_dir / "x3_disposition.json", x3.to_dict())

    l6_temp = float(args.temperature) if args.provider == "qwen_vllm" else HEADLINE_TEMP_DEFAULT
    l6_max = HEADLINE_QWEN_MAX_TOKENS if args.provider == "qwen_vllm" else None
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
            "raw_model_output_provider": provider_raw_output,
            "product_quality_status": product_quality_status,
            "x3_code": x3.x3_code,
        },
    )

    wc_final = headline_word_count(headline_line)
    lines = [
        "HEADLINE_OUTPUT:",
        headline_line if headline_line else f"BLOCKED: {parse_error}",
        "",
        f"WORD_COUNT: {wc_final}",
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
        section_id="headline",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
    )
    return 0 if args.allow_non_allow_exit_zero else (0 if x3.x3_code == "X3_ALLOW" else 2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run apps_rg headline runtime seam.")
    parser.add_argument("--provider", choices=["mock", "qwen_vllm"], default="mock")
    parser.add_argument("--temperature", type=float, default=HEADLINE_TEMP_DEFAULT)
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
