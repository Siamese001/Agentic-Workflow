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

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg or python -m apps_rg --section <lane>"
    )


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



