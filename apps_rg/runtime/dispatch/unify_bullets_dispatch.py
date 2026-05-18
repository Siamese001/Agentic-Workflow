"""Legacy CLI entry for unify_bullets — **retired from canonical CLI**.

Canonical path: ``python -m apps_rg --section unify_bullets`` (see
``apps_rg.runtime.sections.unify_bullets_lane`` via
``apps_rg.runtime.orchestration.canonical_dispatch``).

This module remains as a **narrow wrapper** for hatch-gated mock runs and re-exports helpers
used by contract tests. No prompt or X2 logic lives here anymore.
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


def run_dispatch(args: argparse.Namespace) -> int:
    if mock_judges_blocked_before_run(args):
        from apps_rg.runtime.section_proof.mock_runtime_proof_policy import emit_mock_judges_blocked_stderr

        emit_mock_judges_blocked_stderr(dispatcher_label="unify_bullets_dispatch")
        return MOCK_JUDGES_REJECT_EXIT_CODE

    ns = SimpleNamespace(
        provider=str(getattr(args, "provider", "qwen_vllm")),
        temperature=float(getattr(args, "temperature", UNIFY_TEMP_DEFAULT)),
        x1d_judges=str(getattr(args, "x1d_judges", "gemini_pro,openai_chatgpt,anthropic_claude")),
        mock_judges=bool(getattr(args, "mock_judges", False)),
        allow_non_allow_exit_zero=bool(getattr(args, "allow_non_allow_exit_zero", False)),
        allow_test_mock_judges=bool(getattr(args, "allow_test_mock_judges", False)),
        target_title=str(getattr(args, "target_title", TARGET_TITLE_DEFAULT)),
        target_company=str(getattr(args, "target_company", TARGET_COMPANY_DEFAULT)),
        jd_text=str(getattr(args, "jd_text", JD_TEXT_DEFAULT)),
        briefing=str(getattr(args, "briefing", BRIEFING_DEFAULT)),
    )
    ctx = lane.run_unify_bullets_execution(ns)
    print(ctx.get("output_text", ""))
    x3 = ctx["x3"]
    if allow_non_allow_exit_zero_ok(args):
        return 0
    return 0 if x3.x3_code == "X3_ALLOW" else 2


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


def main(argv: list[str] | None = None) -> int:
    return run_dispatch(build_parser().parse_args(argv))


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
    "main",
    "normalize_parsed_output",
    "parse_model_json",
    "retry_qwen_for_parse",
    "run_dispatch",
    "sha16",
    "write_json",
    "write_x2_gate_outputs",
]


if __name__ == "__main__":
    from apps_rg.runtime.deprecated_runtime_cli import exit_deprecated_dispatch_cli

    raise SystemExit(exit_deprecated_dispatch_cli(section="unify_bullets"))
