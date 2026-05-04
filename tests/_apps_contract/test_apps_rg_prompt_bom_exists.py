"""Test: apps_rg prompt BOM exists and is well-formed.

Verifies:
- prompt_bom.yaml exists
- Contains strategic_tailor, tailor_existing, generate_scratch, enhance_current
- Every template file exists on disk
- Every prompt_id starts with apps_rg.
- Every prompt_id has .vN suffix
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

_APPS_RG_ROOT = Path(__file__).resolve().parent.parent.parent / "apps_rg"
_BOM_PATH = _APPS_RG_ROOT / "prompts" / "prompt_bom.yaml"
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

EXPECTED_FLOWS = ["strategic_tailor", "tailor_existing", "generate_scratch", "enhance_current"]


@pytest.fixture(scope="module")
def bom() -> dict:
    assert _BOM_PATH.exists(), f"prompt_bom.yaml not found at {_BOM_PATH}"
    with open(_BOM_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_bom_exists():
    assert _BOM_PATH.exists()


def test_bom_has_schema_version(bom):
    assert bom.get("schema_version") == "1.0"


def test_bom_has_app_name(bom):
    assert bom.get("app_name") == "apps_rg"


def test_bom_has_resume_generation(bom):
    assert "resume_generation" in bom


def test_bom_has_all_four_flows(bom):
    rg = bom["resume_generation"]
    for flow in EXPECTED_FLOWS:
        assert flow in rg, f"Missing flow: {flow}"


@pytest.mark.parametrize("flow", EXPECTED_FLOWS)
def test_flow_has_prompt_id(bom, flow):
    entry = bom["resume_generation"][flow]
    assert "prompt_id" in entry


@pytest.mark.parametrize("flow", EXPECTED_FLOWS)
def test_prompt_id_starts_with_apps_rg(bom, flow):
    pid = bom["resume_generation"][flow]["prompt_id"]
    assert pid.startswith("apps_rg."), f"prompt_id {pid} does not start with apps_rg."


@pytest.mark.parametrize("flow", EXPECTED_FLOWS)
def test_prompt_id_has_version_suffix(bom, flow):
    pid = bom["resume_generation"][flow]["prompt_id"]
    assert re.search(r"\.v\d+$", pid), f"prompt_id {pid} missing .vN suffix"


@pytest.mark.parametrize("flow", EXPECTED_FLOWS)
def test_template_file_exists(bom, flow):
    entry = bom["resume_generation"][flow]
    template_rel = entry["template"]
    template_path = _REPO_ROOT / template_rel
    assert template_path.exists(), f"Template not found: {template_path}"


@pytest.mark.parametrize("flow", EXPECTED_FLOWS)
def test_template_is_markdown(bom, flow):
    entry = bom["resume_generation"][flow]
    assert entry["template"].endswith(".md")


@pytest.mark.parametrize("flow", EXPECTED_FLOWS)
def test_template_has_pa_slots(bom, flow):
    entry = bom["resume_generation"][flow]
    template_path = _REPO_ROOT / entry["template"]
    content = template_path.read_text(encoding="utf-8")
    assert "{{S0_GOVERNANCE}}" in content
    assert "{{C0_JD_DATA}}" in content
    assert "{{U0_USER_TASK}}" in content
    assert "{{R0_OUTPUT_SCHEMA}}" in content
