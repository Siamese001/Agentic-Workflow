from __future__ import annotations

import re
from pathlib import Path

import yaml

from agentic_core.L2_execution.reasoning.authority_validator import AuthorityValidator
from agentic_core.L2_execution.reasoning.compiled_artifact import AuthorityLevel


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = (
    REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "prompt_slot_registry.v1.yaml"
)
PROMPT_BOM_PATH = REPO_ROOT / "apps_lic" / "prompt_assembly" / "prompt_bom.yaml"
TEMPLATE_DIR = REPO_ROOT / "apps_lic" / "prompt_assembly" / "templates"
PA_BINDING_PATH = REPO_ROOT / "apps_lic" / "runtime" / "bindings" / "pa_binding.py"

SLOT_KEY_RE = re.compile(r'"([A-Z][A-Z0-9]*)":')


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _registry() -> dict:
    return _load_yaml(REGISTRY_PATH)


def _registered_prompt_slots(registry: dict) -> set[str]:
    return set(registry["prompt_slots"])


def _registered_aliases(registry: dict) -> set[str]:
    return set(registry["runtime_aliases"])


def _registered_terms(registry: dict) -> set[str]:
    return _registered_prompt_slots(registry) | _registered_aliases(registry)


def test_w1_prompt_slot_registry_has_required_ssot_sections() -> None:
    registry = _registry()

    assert registry["schema_version"] == "apps_lic.prompt_slot_registry.v1"
    assert registry["status"] == "active"
    assert registry["governance"]["x1_x2_x3_are_exit_terms_not_prompt_slots"] is True
    assert registry["prompt_slots"]
    assert registry["render_order"]
    assert registry["runtime_aliases"]
    assert registry["non_prompt_terms"]
    assert registry["core_compatibility"]


def test_w1_prompt_bom_slots_are_declared_in_registry() -> None:
    registry = _registry()
    bom = _load_yaml(PROMPT_BOM_PATH)

    bom_slots = set(bom["required_slots"]) | set(bom["slot_definitions"])

    assert bom_slots <= _registered_prompt_slots(registry)


def test_w1_template_required_slots_are_declared_in_registry() -> None:
    registry = _registry()
    registered_slots = _registered_prompt_slots(registry)

    template_slots: dict[str, set[str]] = {}
    for path in sorted(TEMPLATE_DIR.glob("*.yaml")):
        template = _load_yaml(path)
        template_slots[path.name] = set(template.get("required_slots") or ())

    assert template_slots
    for path_name, slots in template_slots.items():
        unknown = slots - registered_slots
        assert not unknown, f"{path_name} has unregistered prompt slots: {sorted(unknown)}"


def test_w1_runtime_slot_lineage_terms_resolve_to_registry_slots_or_aliases() -> None:
    registry = _registry()
    text = PA_BINDING_PATH.read_text(encoding="utf-8")

    start = text.index("slot_lineage_map: dict[str, str]")
    end = text.index("component_hash_map", start)
    lineage_block = text[start:end]
    lineage_terms = {
        item
        for item in SLOT_KEY_RE.findall(lineage_block)
        if item not in {"APPS", "LIC"}
    }

    assert lineage_terms
    assert lineage_terms <= _registered_terms(registry)


def test_w1_x1_x2_x3_are_registered_only_as_non_prompt_terms() -> None:
    registry = _registry()
    non_prompt_terms = registry["non_prompt_terms"]

    assert set(non_prompt_terms) == {"X1", "X2", "X3"}
    assert {"X1", "X2", "X3"}.isdisjoint(_registered_prompt_slots(registry))
    assert {"X1", "X2", "X3"}.isdisjoint(_registered_aliases(registry))
    for term in ("X1", "X2", "X3"):
        assert non_prompt_terms[term]["prompt_slot_allowed"] is False
        assert non_prompt_terms[term]["family"] == "exit_validation"


def test_w1_core_authority_expectations_are_reflected_without_app_slot_leakage() -> None:
    registry = _registry()
    compatibility = registry["core_compatibility"]

    assert AuthorityValidator.SLOT_ORDER == compatibility[
        "authority_validator_slot_order_supported"
    ]

    for slot in compatibility["authority_level_from_slot_code_supported"]:
        assert isinstance(AuthorityLevel.from_slot_code(slot), AuthorityLevel)
        assert slot in _registered_prompt_slots(registry)

    for app_slot in compatibility["apps_lic_extension_slots_not_core_authority_levels"]:
        assert app_slot in _registered_prompt_slots(registry)
        assert app_slot not in AuthorityValidator.SLOT_ORDER
