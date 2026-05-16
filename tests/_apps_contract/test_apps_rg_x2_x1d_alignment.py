"""W11 — X2 deterministic gates vs X1D soft judges; matrix SSOT."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_MATRIX = _REPO / "artifacts" / "apps_rg" / "prompt_authority" / "x2_x1d_alignment_matrix.json"
_CONTRACT_DIR = _REPO / "apps_rg" / "prompt_assembly" / "section_prompt_contracts"


def _matrix() -> dict:
    return json.loads(_MATRIX.read_text(encoding="utf-8"))


def test_alignment_matrix_exists_and_covers_all_section_contracts() -> None:
    matrix = _matrix()
    rows = {r["section_id"]: r for r in matrix["sections"]}
    for p in sorted(_CONTRACT_DIR.glob("*.contract.yaml")):
        doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        sid = doc["section_id"]
        assert sid in rows, f"matrix missing {sid}"
        assert rows[sid]["x2_gate_profile_ref"] == doc.get(
            "x2_gate_profile_ref"
        ), f"x2 mismatch for {sid}"
        judge = doc.get("x1d_judge_profile_ref")
        if judge:
            assert rows[sid]["x1d_judge_profile_ref"] == judge, sid
        else:
            assert rows[sid]["x1d_judge_profile_ref"] in (None, ""), sid


@pytest.mark.parametrize(
    "section_id",
    [
        "headline",
        "executive_summary",
        "competencies",
        "unify_narrative",
        "unify_bullets",
        "ibm_narrative",
        "ibm_bullets",
    ],
)
def test_generated_sections_have_substantive_x2_determinism(section_id: str) -> None:
    rows = {r["section_id"]: r for r in _matrix()["sections"]}
    row = rows[section_id]
    assert row["llm_generation_allowed"] is True
    facts = row.get("x2_deterministic_facts") or []
    assert len(facts) >= 3, section_id
    x2path = _REPO / row["x2_gate_profile_ref"]
    text = x2path.read_text(encoding="utf-8")
    gate = row["x2_gates_sample"][0]
    assert gate in text, f"{gate} not found in {x2path.name}"


def test_locked_sections_have_no_x1d_judge() -> None:
    rows = {r["section_id"]: r for r in _matrix()["sections"]}
    for sid in ("education", "certifications", "early_career"):
        assert rows[sid]["llm_generation_allowed"] is False
        assert rows[sid]["x1d_judge_profile_ref"] is None
        assert rows[sid].get("x1d_na_reason")


def test_generated_sections_have_x1d_path() -> None:
    rows = {r["section_id"]: r for r in _matrix()["sections"]}
    for sid, row in rows.items():
        if not row.get("llm_generation_allowed"):
            continue
        ref = row.get("x1d_judge_profile_ref")
        assert ref, sid
        assert (_REPO / ref).is_file(), sid
