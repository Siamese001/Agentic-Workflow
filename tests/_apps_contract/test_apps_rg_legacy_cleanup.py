"""Tests: apps_rg legacy cleanup verification (W3 deferred plan).

Verifies that:
  1. Legacy .md prompt templates under apps_rg/prompts/ are removed.
  2. No Python code references the old apps_rg/prompts/ directory.
  3. The canonical PA pipeline (prompt_assembly/) is intact.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]


class TestLegacyTemplatesRemoved:
    """Legacy .md templates under apps_rg/prompts/ must not exist."""

    def test_prompts_dir_absent(self):
        legacy = _REPO_ROOT / "apps_rg" / "prompts"
        assert not legacy.exists(), (
            f"Legacy prompts directory still exists: {legacy}. "
            "It should have been removed as part of W3.P6."
        )

    def test_no_legacy_md_templates(self):
        legacy = _REPO_ROOT / "apps_rg" / "prompts" / "resume_generation"
        if legacy.exists():
            md_files = list(legacy.glob("*.md"))
            assert md_files == [], (
                f"Legacy .md templates still present: {[f.name for f in md_files]}"
            )

    def test_legacy_bom_absent(self):
        legacy_bom = _REPO_ROOT / "apps_rg" / "prompts" / "prompt_bom.yaml"
        assert not legacy_bom.exists(), (
            f"Legacy prompt_bom.yaml still exists: {legacy_bom}. "
            "Canonical BOM is at apps_rg/prompt_assembly/prompt_bom.yaml."
        )


class TestNoCodeReferencesLegacyPrompts:
    """No Python file should import from or reference apps_rg/prompts/."""

    def test_no_py_imports_legacy_prompts(self):
        apps_rg = _REPO_ROOT / "apps_rg"
        violations = []
        for py_file in apps_rg.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "apps_rg/prompts" in content or "apps_rg.prompts" in content:
                violations.append(str(py_file.relative_to(_REPO_ROOT)))
        assert violations == [], (
            f"Python files still reference legacy apps_rg/prompts/: {violations}"
        )


class TestCanonicalPAPipelineIntact:
    """The canonical prompt_assembly pipeline must remain functional."""

    def test_prompt_assembly_bom_exists(self):
        bom = _REPO_ROOT / "apps_rg" / "prompt_assembly" / "prompt_bom.yaml"
        assert bom.exists(), "Canonical prompt_bom.yaml missing"

    def test_prompt_assembly_registry_exists(self):
        reg = _REPO_ROOT / "apps_rg" / "prompt_assembly" / "prompt_registry.yaml"
        assert reg.exists(), "Canonical prompt_registry.yaml missing"

    def test_compiler_importable(self):
        mod = importlib.import_module("apps_rg.prompt_assembly.compiler")
        assert hasattr(mod, "compile_prompt")

    def test_contracts_importable(self):
        mod = importlib.import_module("apps_rg.prompt_assembly.contracts")
        assert hasattr(mod, "AppsRgCompiledPromptArtifact")
        assert hasattr(mod, "AppsRgPromptRequest")

    def test_provider_request_importable(self):
        mod = importlib.import_module("apps_rg.prompt_assembly.provider_request")
        assert hasattr(mod, "artifact_to_provider_request")

    def test_flow_route_map_has_all_routes(self):
        from apps_rg.prompt_assembly.compiler import FLOW_ROUTE_TO_TEMPLATE
        expected = {
            "strategic_tailor", "strategic_tailor_node",
            "tailor_existing", "generate_scratch", "enhance_current",
            "fact_check", "claim_omission", "bullet_diversity_repair",
            "docx_manifest",
        }
        assert expected.issubset(set(FLOW_ROUTE_TO_TEMPLATE.keys()))
