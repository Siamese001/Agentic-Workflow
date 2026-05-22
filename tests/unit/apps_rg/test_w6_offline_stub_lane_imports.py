"""W6.1 — section lanes must not import dead offline-stub callables."""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_LANES = (
    "apps_rg/runtime/sections/headline_lane.py",
    "apps_rg/runtime/sections/competencies_lane_runtime.py",
    "apps_rg/runtime/sections/ibm_narrative_lane_runtime.py",
    "apps_rg/runtime/sections/executive_summary_lane.py",
    "apps_rg/runtime/sections/unify_bullets_lane.py",
    "apps_rg/runtime/sections/unify_narrative_lane.py",
    "apps_rg/runtime/sections/ibm_bullets_lane.py",
    "apps_rg/runtime/providers/section_qwen_slice.py",
)


@pytest.mark.parametrize("rel_path", _LANES)
def test_lane_files_do_not_import_dead_offline_stub_callables(rel_path: str) -> None:
    text = (_REPO / rel_path).read_text(encoding="utf-8")
    assert "synthetic_qwen_provider_result" not in text
    assert "effective_offline_contract_stub_enabled" not in text
