"""Test: apps_rg prompt BOM and registry exist and are well-formed.

Verifies:
- Canonical prompt_bom.yaml exists at apps_rg/prompt_assembly/
- Canonical prompt_registry.yaml exists
- Registry contains all expected template_ids
- Every template YAML file exists on disk
- FLOW_ROUTE_TO_TEMPLATE maps all expected routes
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PA_ROOT = _REPO_ROOT / "apps_rg" / "prompt_assembly"
_BOM_PATH = _PA_ROOT / "prompt_bom.yaml"
_REGISTRY_PATH = _PA_ROOT / "prompt_registry.yaml"

EXPECTED_TEMPLATE_IDS = [
    "strategic_tailor_v1",
    "tailor_existing_v1",
    "generate_scratch_v1",
    "enhance_current_v1",
    "resume_fact_check_v1",
    "unsupported_claim_omission_v1",
    "bullet_diversity_repair_v1",
    "docx_manifest_v1",
]


@pytest.fixture(scope="module")
def bom() -> dict:
    assert _BOM_PATH.exists(), f"prompt_bom.yaml not found at {_BOM_PATH}"
    with open(_BOM_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def registry() -> dict:
    assert _REGISTRY_PATH.exists(), f"prompt_registry.yaml not found at {_REGISTRY_PATH}"
    with open(_REGISTRY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_bom_exists():
    assert _BOM_PATH.exists()


def test_bom_has_schema_version(bom):
    assert bom.get("schema_version") == "1.0"


def test_bom_has_app_name(bom):
    assert bom.get("app") == "apps_rg"


def test_registry_exists():
    assert _REGISTRY_PATH.exists()


def test_registry_has_schema_version(registry):
    assert registry.get("schema_version") == "1.0"


def test_registry_has_all_templates(registry):
    templates = registry.get("templates", {})
    for tid in EXPECTED_TEMPLATE_IDS:
        assert tid in templates, f"Missing template_id: {tid}"


@pytest.mark.parametrize("template_id", EXPECTED_TEMPLATE_IDS)
def test_template_file_exists(registry, template_id):
    entry = registry["templates"][template_id]
    template_path = _REPO_ROOT / entry["path"]
    assert template_path.exists(), f"Template not found: {template_path}"


@pytest.mark.parametrize("template_id", EXPECTED_TEMPLATE_IDS)
def test_template_is_yaml(registry, template_id):
    entry = registry["templates"][template_id]
    assert entry["path"].endswith(".yaml"), f"{template_id} template not YAML"


@pytest.mark.parametrize("template_id", EXPECTED_TEMPLATE_IDS)
def test_template_has_required_slots(registry, template_id):
    entry = registry["templates"][template_id]
    assert "required_slots" in entry
    assert "S0" in entry["required_slots"], f"{template_id} missing S0 slot"


def test_flow_route_map_covers_all():
    from apps_rg.prompt_assembly.compiler import FLOW_ROUTE_TO_TEMPLATE
    expected_routes = {
        "strategic_tailor", "tailor_existing", "generate_scratch",
        "enhance_current", "fact_check", "claim_omission",
        "bullet_diversity_repair", "docx_manifest",
    }
    assert expected_routes.issubset(set(FLOW_ROUTE_TO_TEMPLATE.keys()))
