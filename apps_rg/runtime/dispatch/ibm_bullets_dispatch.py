"""IBM bullets — **import-only** re-exports; canonical runtime is ``ibm_bullets_lane``.

The historical ``python -m apps_rg.runtime.dispatch.ibm_bullets_dispatch`` entry is **retired**:
running this file as ``__main__`` prints stderr guidance and exits 2.

Use: ``python -m apps_rg --section ibm_bullets``
"""
from __future__ import annotations

from typing import Any

from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_DECLARED_TEMPORARY_SLICE,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_DECLARED_TEMPORARY_SLICE
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.sections import ibm_bullets_lane as lane

# --- Re-exports (implementations live in ``ibm_bullets_lane``) ---
DEFAULT_INTENSITY_BY_BULLET = lane.DEFAULT_INTENSITY_BY_BULLET
BULLET_ID_ALIASES = lane.BULLET_ID_ALIASES
IBM_QWEN_MAX_TOKENS = lane.IBM_QWEN_MAX_TOKENS
PROMPT_ID = lane.PROMPT_ID
IBM_TEMP_DEFAULT = lane.IBM_TEMP_DEFAULT
TARGET_TITLE_DEFAULT = lane.TARGET_TITLE_DEFAULT
TARGET_COMPANY_DEFAULT = lane.TARGET_COMPANY_DEFAULT
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text

sha16 = lane.sha16
write_json = lane.write_json
load_base_resume = lane.load_base_resume
extract_ibm_employment = lane.extract_ibm_employment
build_selected_fact_plan = lane.build_selected_fact_plan
build_runtime_payload = lane.build_runtime_payload
normalize_parsed_output = lane.normalize_parsed_output
build_mock_output = lane.build_mock_output
parse_model_json = lane.parse_model_json
retry_qwen_for_parse = lane.retry_qwen_for_parse
bullets_display_text = lane.bullets_display_text
_canonicalize_bul_ibm_source_fact_id = lane._canonicalize_bul_ibm_source_fact_id
build_prompt_messages = lane.build_prompt_messages

LANE_KEY = lane.LANE_KEY
REPO_ROOT = lane.REPO_ROOT


def infer_product_quality(
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
) -> tuple[str, str]:
    return lane.infer_product_quality(runtime_generation_status, x2_gates)


def write_x2_gate_outputs(path: object, gates: list[dict[str, Any]]) -> None:
    from apps_rg.runtime.sections.executive_summary_lane import write_x2_gate_outputs as _w

    _w(path, gates)


__all__ = [
    "BRIEFING_DEFAULT",
    "BULLET_ID_ALIASES",
    "DEFAULT_INTENSITY_BY_BULLET",
    "IBM_QWEN_MAX_TOKENS",
    "IBM_TEMP_DEFAULT",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "PROMPT_ID",
    "REPO_ROOT",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "_canonicalize_bul_ibm_source_fact_id",
    "build_mock_output",
    "build_prompt_messages",
    "build_runtime_payload",
    "build_selected_fact_plan",
    "bullets_display_text",
    "extract_ibm_employment",
    "infer_product_quality",
    "load_base_resume",
    "normalize_parsed_output",
    "parse_model_json",
    "retry_qwen_for_parse",
    "sha16",
    "write_json",
    "write_x2_gate_outputs",
]


if __name__ == "__main__":
    from apps_rg.runtime.deprecated_runtime_cli import exit_deprecated_dispatch_cli

    raise SystemExit(exit_deprecated_dispatch_cli(section="ibm_bullets"))
