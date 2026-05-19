"""Wave 9: no-two-path runtime inspection."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.section_one_spine_certification import emit_section_one_spine_certification_artifacts
from apps_rg.runtime.section_one_spine_no_two_path import inspect_no_two_path_lane
from tests.unit.apps_rg.test_one_spine_certification_w8 import _minimal_chain


@pytest.mark.parametrize("section_id", ["headline", "competencies", "unify_bullets"])
def test_no_two_path_passes_after_full_chain(section_id: str, tmp_path: Path):
    payload = _minimal_chain(tmp_path, section_id)
    emit_section_one_spine_certification_artifacts(
        tmp_path,
        section_id=section_id,
        runtime_payload=payload,
        proof_bundle={"proof_eligible": section_id != "unify_bullets", "test_only_mock_provider": False},
        runtime_generation_status="REAL_LLM",
    )
    ntp = inspect_no_two_path_lane(tmp_path)
    assert ntp["no_two_path_preconditions_pass"] is True
    assert ntp["checks"]["raw_proof_pool_direct_to_pa"] is False
    assert ntp["checks"]["section_x3_mirror_not_authoritative"] is True


def test_missing_exit_breaks_no_two_path(tmp_path: Path):
    _minimal_chain(tmp_path, "headline")
    (tmp_path / "exit_disposition_receipt.json").unlink()
    ntp = inspect_no_two_path_lane(tmp_path)
    assert ntp["no_two_path_preconditions_pass"] is False
