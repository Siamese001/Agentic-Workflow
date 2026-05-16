"""Lightweight existence/family checks for stable IBM and Unify prompt lanes.

Full prompt-body hash parity is intentionally out of scope for this wave. Several
lane templates embed pseudo-JSON ``schema:`` blobs that are not valid full-document
YAML for PyYAML ``safe_load``; we only assert on-disk presence + ``template_id`` family.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_LANE_YAMLS: tuple[tuple[str, str], ...] = (
    ("apps_rg/prompt_assembly/templates/unify_v1.yaml", "unify"),
    ("apps_rg/prompt_assembly/templates/final_unify_v2.yaml", "unify"),
    ("apps_rg/prompt_assembly/templates/unify_bullet_tailor_v1.yaml", "unify"),
    ("apps_rg/prompt_assembly/templates/unify_position_narrative_v1.yaml", "unify"),
    ("apps_rg/prompt_assembly/templates/ibm_bullet_tailor_v1.yaml", "ibm"),
    ("apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml", "ibm"),
)

_TEMPLATE_ID_RE = re.compile(r"(?m)^template_id:\s*(?:\"([^\"]+)\"|'([^']+)'|([^#\n]+))\s*$")
_ALLOWED_STAGE_RE = re.compile(r"(?m)^allowed_stage:\s*(?:\"([^\"]+)\"|'([^']+)'|([^#\n]+))\s*$")


def _first_group(m: re.Match[str] | None) -> str | None:
    if m is None:
        return None
    for g in m.groups():
        if g:
            return g.strip().strip('"').strip("'")
    return None


@pytest.mark.parametrize("rel_path,family", _LANE_YAMLS)
def test_lane_template_exists_and_family(rel_path: str, family: str) -> None:
    path = REPO_ROOT / rel_path
    assert path.is_file(), f"missing lane template: {rel_path}"
    text = path.read_text(encoding="utf-8")
    tid = _first_group(_TEMPLATE_ID_RE.search(text))
    assert tid, f"template_id not found in {rel_path}"
    low = tid.lower()
    if family == "unify":
        assert "unify" in low, f"expected unify family in template_id, got {tid!r} ({rel_path})"
    else:
        assert "ibm" in low, f"expected ibm family in template_id, got {tid!r} ({rel_path})"
    stage = _first_group(_ALLOWED_STAGE_RE.search(text))
    assert stage, f"allowed_stage not found in {rel_path}"
