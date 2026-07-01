from __future__ import annotations

from apps_rg.runtime import full_resume_review_bundle, full_run_section_status, mandatory_run_outputs
from apps_rg.runtime.run_output_contract import (
    APPS_RG_MANDATORY_RUN_OUTPUT_JSON,
    APPS_RG_MANDATORY_RUN_OUTPUT_MD,
    BCG_EXECUTIVE_OUTPUT_MD,
    FULL_RUN_SECTION_STATUS_JSON,
    FULL_RUN_SECTION_STATUS_MD,
    REVIEW_BUNDLE_FILENAME,
    REVIEW_INDEX_FILENAME,
)


def test_runtime_output_modules_alias_canonical_filename_contract() -> None:
    assert mandatory_run_outputs.MANDATORY_RUN_OUTPUT_JSON == APPS_RG_MANDATORY_RUN_OUTPUT_JSON
    assert mandatory_run_outputs.MANDATORY_RUN_OUTPUT_MD == APPS_RG_MANDATORY_RUN_OUTPUT_MD
    assert mandatory_run_outputs.BCG_EXECUTIVE_OUTPUT_MD == BCG_EXECUTIVE_OUTPUT_MD
    assert full_run_section_status.FULL_RUN_SECTION_STATUS_MD == FULL_RUN_SECTION_STATUS_MD
    assert full_run_section_status.FULL_RUN_SECTION_STATUS_JSON == FULL_RUN_SECTION_STATUS_JSON
    assert full_resume_review_bundle.REVIEW_BUNDLE_FILENAME == REVIEW_BUNDLE_FILENAME
    assert full_resume_review_bundle.REVIEW_INDEX_FILENAME == REVIEW_INDEX_FILENAME
