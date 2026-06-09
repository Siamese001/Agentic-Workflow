from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

import yaml

from apps_lic.config import knowledge_base
from apps_lic.config.knowledge_base import (
    FROZEN_SNAPSHOT,
    get_prompt,
    legacy_prompt_template_fence_receipt,
    list_all_prompts,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "apps_lic"
PROMPT_REGISTRY_PATH = APP_ROOT / "config" / "prompt_registry.yaml"
PA_RUNTIME_FILES = (
    APP_ROOT / "runtime" / "bindings" / "pa_binding.py",
    APP_ROOT / "runtime" / "bindings" / "pa_schema_receipts.py",
    APP_ROOT / "prompt_assembly" / "lic_pa_compiler.py",
    APP_ROOT / "types" / "recipient_archetype_mapping.py",
    APP_ROOT / "types" / "recipient_policy_profile.py",
)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _imported_modules(path: Path) -> Iterable[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def test_w6_legacy_prompt_template_declares_non_runtime_authority() -> None:
    receipt = legacy_prompt_template_fence_receipt()

    assert receipt["status"] == "compatibility_fenced"
    assert receipt["runtime_authority"] is False
    assert receipt["authority"] == "historical_read_only_snapshot"

    for key in (
        "canonical_prompt_registry_ref",
        "canonical_prompt_bom_ref",
        "canonical_prompt_slot_registry_ref",
        "canonical_output_schema_ref",
    ):
        assert (REPO_ROOT / str(receipt[key])).exists()


def test_w6_knowledge_base_is_the_only_prompttemplate_importer() -> None:
    prompt_template_importers: list[str] = []

    for path in APP_ROOT.rglob("*.py"):
        if path.name == "PromptTemplate.py":
            continue
        imports = set(_imported_modules(path))
        if "apps_lic.types.PromptTemplate" in imports:
            prompt_template_importers.append(_relative(path))

    assert prompt_template_importers == ["apps_lic/config/knowledge_base.py"]


def test_w6_pa_runtime_does_not_import_legacy_prompt_authorities() -> None:
    forbidden_imports = {
        "apps_lic.types.PromptTemplate",
        "apps_lic.config.knowledge_base",
    }

    for path in PA_RUNTIME_FILES:
        imports = set(_imported_modules(path))
        assert imports.isdisjoint(forbidden_imports), _relative(path)


def test_w6_active_prompt_registry_has_no_legacy_snapshot_prompt_ids() -> None:
    registry = _load_yaml(PROMPT_REGISTRY_PATH)
    templates = registry["templates"]
    active_templates = {
        template_id: metadata
        for template_id, metadata in templates.items()
        if metadata.get("status") == "active"
    }

    assert set(active_templates).isdisjoint(set(list_all_prompts()))
    for template_id, metadata in active_templates.items():
        assert metadata["path"].startswith("apps_lic/prompt_assembly/templates/"), template_id
        assert metadata["output_contract"], template_id
        assert metadata["allowed_stage"] in {"E2_VALID", "E3_EXEC", "E4_HEAL"}, template_id


def test_w6_legacy_knowledge_base_remains_read_only_compatibility_surface() -> None:
    legacy_prompt_ids = list_all_prompts()

    assert legacy_prompt_ids
    assert isinstance(get_prompt(legacy_prompt_ids[0]), str)
    assert FROZEN_SNAPSHOT.prompts[legacy_prompt_ids[0]].prompt_id == legacy_prompt_ids[0]
    assert knowledge_base.LEGACY_PROMPT_TEMPLATE_RUNTIME_AUTHORITY is False
    assert knowledge_base.LEGACY_PROMPT_TEMPLATE_STATUS == "compatibility_fenced"

