"""Legacy CLI entry for unify_bullets — **retired from canonical CLI**.

Canonical path: ``python -m apps_rg --section unify_bullets`` (see
``apps_rg.runtime.sections.unify_bullets_lane`` via
``apps_rg.runtime.orchestration.canonical_dispatch``).

This module remains as a **narrow wrapper** for hatch-gated mock runs and re-exports helpers
used by contract tests. No prompt or X2 logic lives here anymore.
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
import sys
from types import SimpleNamespace
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    MOCK_JUDGES_REJECT_EXIT_CODE,
    allow_non_allow_exit_zero_ok,
    mock_judges_blocked_before_run,
)
from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.sections import unify_bullets_lane as lane

# --- Re-exports for legacy tests / tooling (canonical implementations live in unify_bullets_lane) ---
DEFAULT_INTENSITY_BY_BULLET = lane.DEFAULT_INTENSITY_BY_BULLET
BULLET_ID_ALIASES = lane.BULLET_ID_ALIASES
UNIFY_QWEN_MAX_TOKENS = lane.UNIFY_QWEN_MAX_TOKENS

PROMPT_ID = lane.PROMPT_ID
UNIFY_TEMP_DEFAULT = lane.UNIFY_TEMP_DEFAULT
TARGET_TITLE_DEFAULT = lane.TARGET_TITLE_DEFAULT
TARGET_COMPANY_DEFAULT = lane.TARGET_COMPANY_DEFAULT
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text

sha16 = lane.sha16
write_json = lane.write_json
load_base_resume = lane.load_base_resume
extract_unify_employment = lane.extract_unify_employment
build_selected_fact_plan = lane.build_selected_fact_plan
build_runtime_payload = lane.build_runtime_payload
normalize_unify_parsed_without_ledger_synthesis = lane.normalize_unify_parsed_without_ledger_synthesis
build_mock_output = lane.build_mock_output
parse_model_json = lane.parse_model_json
retry_qwen_for_parse = lane.retry_qwen_for_parse
bullets_display_text = lane.bullets_display_text


def normalize_parsed_output(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Compatibility name: lane normalize only (no ledger / claim_text fabrication)."""
    return normalize_unify_parsed_without_ledger_synthesis(parsed, runtime_payload)


def infer_product_quality(
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
) -> tuple[str, str]:
    return lane.infer_unify_bullets_product_quality(runtime_generation_status, x2_gates)


def write_x2_gate_outputs(path, gates: list[dict[str, Any]]) -> None:
    from apps_rg.runtime.sections.executive_summary_lane import write_x2_gate_outputs as _w

    _w(path, gates)


LANE_KEY = lane.LANE_KEY
REPO_ROOT = lane.REPO_ROOT
PROMPT_TEMPLATE = lane.PROMPT_TEMPLATE



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="[LEGACY] Run apps_rg unify_bullets — prefer `python -m apps_rg --section unify_bullets`.")
    parser.add_argument(
        "--provider",
        choices=["qwen_vllm"],
        default="qwen_vllm",
        help="Generation provider (qwen_vllm only). Offline tests: set APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1.",
    )
    parser.add_argument("--temperature", type=float, default=UNIFY_TEMP_DEFAULT)
    parser.add_argument("--x1d-judges", default="gemini_pro,openai_chatgpt,anthropic_claude")
    parser.add_argument("--mock-judges", action="store_true")
    parser.add_argument("--allow-test-mock-judges", action="store_true")
    parser.add_argument("--target-title", default=TARGET_TITLE_DEFAULT)
    parser.add_argument("--target-company", default=TARGET_COMPANY_DEFAULT)
    parser.add_argument("--jd-text", default=JD_TEXT_DEFAULT)
    parser.add_argument("--briefing", default=BRIEFING_DEFAULT)
    parser.add_argument("--allow-non-allow-exit-zero", action="store_true")
    return parser



__all__ = [
    "BULLET_ID_ALIASES",
    "BRIEFING_DEFAULT",
    "DEFAULT_INTENSITY_BY_BULLET",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "PROMPT_ID",
    "PROMPT_TEMPLATE",
    "REPO_ROOT",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "UNIFY_QWEN_MAX_TOKENS",
    "UNIFY_TEMP_DEFAULT",
    "build_mock_output",
    "build_parser",
    "build_runtime_payload",
    "build_selected_fact_plan",
    "bullets_display_text",
    "extract_unify_employment",
    "infer_product_quality",
    "load_base_resume",
    
    "normalize_parsed_output",
    "parse_model_json",
    "retry_qwen_for_parse",
    
    "sha16",
    "write_json",
    "write_x2_gate_outputs",
]


