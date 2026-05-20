"""Legacy ``python -m`` entry for executive_summary — **retired from canonical CLI**.

Canonical path: ``python -m apps_rg --section executive_summary`` (see
``apps_rg.runtime.sections.executive_summary_lane`` via
``apps_rg.runtime.orchestration.canonical_dispatch``).

This module remains as a **thin re-export** for tests and in-process recipe calls only.
**Do not run** ``python -m apps_rg.runtime.sections.executive_summary_lane_api`` — it exits 2 with a
deprecation message. Use ``python -m apps_rg --section executive_summary`` instead.

For retirement inventory and replacement mapping, see:
``artifacts/apps_rg/executive_summary_dispatch_retirement/*.md``.
"""
from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg or python -m apps_rg --section <lane>"
    )


import argparse
import sys

from apps_rg.runtime.sections.executive_summary_lane import (  # noqa: F401 — public re-export
    BRIEFING_DEFAULT,
    EXEC_SUMMARY_TEMP_DEFAULT,
    EXEC_SUMMARY_TEMP_RANGE,
    JD_TEXT_DEFAULT,
    LANE_KEY,
    PROMPT_ID,
    PROMPT_TEMPLATE,
    REPO_ROOT,
    TARGET_COMPANY_DEFAULT,
    TARGET_TITLE_DEFAULT,
    BASE_JSON_DEFAULT,
    BASE_POINTER,
    build_mock_output,
    build_prompt_messages,
    build_runtime_payload,
    build_selected_fact_plan,
    check_executive_summary_narrative_shape,
    check_l2_resume_voice,
    enrich_parsed_for_x2,
    extract_allowed_facts,
    infer_product_quality,
    load_base_resume,
    parse_model_json,
    resolve_provider_model_name,
    retry_qwen_for_synthesis,
    run_executive_summary_execution,
    sha16,
    write_json,
    write_x2_gate_outputs,
)

# W3 / import-time validation: keep on legacy module path for fixture stability.
from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_DECLARED_TEMPORARY_SLICE,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_DECLARED_TEMPORARY_SLICE
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

__all__ = [
    "BRIEFING_DEFAULT",
    "EXEC_SUMMARY_TEMP_DEFAULT",
    "EXEC_SUMMARY_TEMP_RANGE",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "PROMPT_ID",
    "PROMPT_TEMPLATE",
    "REPO_ROOT",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "BASE_JSON_DEFAULT",
    "BASE_POINTER",
    "W3_EXECUTION_PATH_BUCKET",
    "W3_EXECUTION_PATH_PLAN_SLUG",
    "build_mock_output",
    "build_prompt_messages",
    "build_runtime_payload",
    "build_selected_fact_plan",
    "build_parser",
    "check_executive_summary_narrative_shape",
    "check_l2_resume_voice",
    "enrich_parsed_for_x2",
    "extract_allowed_facts",
    "infer_product_quality",
    "load_base_resume",
    
    "parse_model_json",
    "resolve_provider_model_name",
    "retry_qwen_for_synthesis",
    
    "run_executive_summary_execution",
    "sha16",
    "write_json",
    "write_x2_gate_outputs",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="[LEGACY] Run apps_rg executive_summary — prefer `python -m apps_rg --section executive_summary`.")
    parser.add_argument("--provider", choices=["mock", "qwen_vllm"], default="mock")
    parser.add_argument("--temperature", type=float, default=EXEC_SUMMARY_TEMP_DEFAULT)
    parser.add_argument("--x1d-judges", default="gemini_pro,openai_chatgpt,anthropic_claude")
    parser.add_argument("--mock-judges", action="store_true", help="Use mocked judge rows for plumbing tests only.")
    parser.add_argument("--target-title", default=TARGET_TITLE_DEFAULT)
    parser.add_argument("--target-company", default=TARGET_COMPANY_DEFAULT)
    parser.add_argument("--jd-text", default=JD_TEXT_DEFAULT)
    parser.add_argument("--briefing", default=BRIEFING_DEFAULT)
    parser.add_argument(
        "--allow-non-allow-exit-zero",
        action="store_true",
        help="Return exit code 0 even when X3 blocks/reviews, useful for inspection.",
    )
    return parser



