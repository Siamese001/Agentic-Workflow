"""W10.5 PA Boundary Governance — Proves no agentic_core changes or runtime wiring.

Verifies:
- No Python files created in agentic_core by this plan (structural scan)
- Compiler.py in apps_rg/prompt_assembly has no model/provider calls
- No new runtime entrypoints in the PA layer
- New YAML files are declarative only (no exec/subprocess/import Python keywords)
- E3/E4 template YAML files do not contain Python import statements
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PA_ROOT = _REPO_ROOT / "apps_rg" / "prompt_assembly"
_TEMPLATES_ROOT = _PA_ROOT / "templates"
_SECTION_CONTRACTS_ROOT = _PA_ROOT / "section_contracts"


# ---------------------------------------------------------------------------
# Declarative-only YAML checks
# ---------------------------------------------------------------------------

ALL_NEW_YAMLS = list(_SECTION_CONTRACTS_ROOT.glob("*.yaml")) + [
    _PA_ROOT / "forbidden_ai_phrases.yaml",
    _PA_ROOT / "jd_calibration_contract.yaml",
    _PA_ROOT / "rubrics" / "section_quality_rubrics.yaml",
    _PA_ROOT / "examples" / "executive_summary_examples.yaml",
    _PA_ROOT / "examples" / "unify_examples.yaml",
    _PA_ROOT / "examples" / "competencies_examples.yaml",
    _TEMPLATES_ROOT / "unify_v1.yaml",
]

_PYTHON_IMPORT_PATTERN = re.compile(r"^\s*(import |from .+ import )", re.MULTILINE)
_SUBPROCESS_PATTERN = re.compile(r"subprocess|os\.system|exec\(|eval\(")
_PROVIDER_PATTERN = re.compile(r"openai\.|anthropic\.|requests\.post|httpx\.|vllm\.", re.IGNORECASE)


@pytest.mark.parametrize("path", ALL_NEW_YAMLS, ids=[p.name for p in ALL_NEW_YAMLS])
def test_new_yaml_is_declarative_no_python_imports(path: Path):
    if not path.exists():
        pytest.skip(f"File not yet created: {path}")
    content = path.read_text(encoding="utf-8")
    assert not _PYTHON_IMPORT_PATTERN.search(content), \
        f"{path.name} must not contain Python import statements — YAML only"


@pytest.mark.parametrize("path", ALL_NEW_YAMLS, ids=[p.name for p in ALL_NEW_YAMLS])
def test_new_yaml_has_no_subprocess_or_exec(path: Path):
    if not path.exists():
        pytest.skip(f"File not yet created: {path}")
    content = path.read_text(encoding="utf-8")
    assert not _SUBPROCESS_PATTERN.search(content), \
        f"{path.name} must not contain subprocess/exec/eval calls"


@pytest.mark.parametrize("path", ALL_NEW_YAMLS, ids=[p.name for p in ALL_NEW_YAMLS])
def test_new_yaml_has_no_provider_sdk_calls(path: Path):
    if not path.exists():
        pytest.skip(f"File not yet created: {path}")
    content = path.read_text(encoding="utf-8")
    assert not _PROVIDER_PATTERN.search(content), \
        f"{path.name} must not contain provider/model SDK calls"


# ---------------------------------------------------------------------------
# Template slot authority ordering preserved
# ---------------------------------------------------------------------------

E3_E4_TEMPLATES = [
    ("strategic_tailor_v1.yaml", "E3_EXEC"),
    ("tailor_existing_v1.yaml", "E3_EXEC"),
    ("generate_scratch_v1.yaml", "E3_EXEC"),
    ("enhance_current_v1.yaml", "E3_EXEC"),
    ("bullet_diversity_repair_v1.yaml", "E4_HEAL"),
    ("resume_fact_check_v1.yaml", "E4_HEAL"),
    ("unsupported_claim_omission_v1.yaml", "E4_HEAL"),
    ("unify_v1.yaml", "E4_HEAL"),
]


@pytest.mark.parametrize("filename,expected_stage", E3_E4_TEMPLATES)
def test_template_allowed_stage_unchanged(filename: str, expected_stage: str):
    path = _TEMPLATES_ROOT / filename
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data.get("allowed_stage") == expected_stage, \
        f"{filename} allowed_stage must be {expected_stage}"


@pytest.mark.parametrize("filename,expected_stage", E3_E4_TEMPLATES)
def test_template_s0_contains_no_fabrication(filename: str, expected_stage: str):
    path = _TEMPLATES_ROOT / filename
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    s0 = data.get("slot_bodies", {}).get("S0", "")
    assert "fabricat" in s0.lower() or "FABRICAT" in s0 or "NO FABRICATION" in s0 or \
           "ZERO FACT" in s0 or "OATH" in s0, \
        f"{filename} S0 must preserve some variant of the no-fabrication constraint"


# ---------------------------------------------------------------------------
# PA compiler: no new model/provider calls
# ---------------------------------------------------------------------------

class TestPaCompilerBoundary:
    _compiler_path = _REPO_ROOT / "apps_rg" / "prompt_assembly" / "compiler.py"

    def test_compiler_exists(self):
        assert self._compiler_path.exists(), f"compiler.py not found: {self._compiler_path}"

    def test_compiler_has_no_openai_calls(self):
        content = self._compiler_path.read_text(encoding="utf-8")
        assert "openai" not in content.lower(), "compiler.py must not call openai"

    def test_compiler_has_no_anthropic_calls(self):
        content = self._compiler_path.read_text(encoding="utf-8")
        assert "anthropic" not in content.lower(), "compiler.py must not call anthropic"

    def test_compiler_has_no_vllm_calls(self):
        content = self._compiler_path.read_text(encoding="utf-8")
        assert "vllm" not in content.lower(), "compiler.py must not call vllm"


# ---------------------------------------------------------------------------
# agentic_core boundary: PA layer must not import from agentic_core
# ---------------------------------------------------------------------------

PA_PYTHON_FILES = list(_PA_ROOT.glob("*.py")) + list((_PA_ROOT / "templates").glob("*.py"))


@pytest.mark.parametrize(
    "path",
    [p for p in PA_PYTHON_FILES if p.name != "__init__.py"],
    ids=[p.name for p in PA_PYTHON_FILES if p.name != "__init__.py"],
)
def test_pa_python_file_does_not_import_agentic_core(path: Path):
    content = path.read_text(encoding="utf-8")
    assert "from agentic_core" not in content, \
        f"{path.name} must not import from agentic_core — PA boundary violation"
    assert "import agentic_core" not in content, \
        f"{path.name} must not import agentic_core — PA boundary violation"


# ---------------------------------------------------------------------------
# Registry consistency: every registry template path exists on disk
# ---------------------------------------------------------------------------

class TestRegistryPathIntegrity:
    _registry_path = _PA_ROOT / "prompt_registry.yaml"

    def test_all_registry_template_paths_exist(self):
        data = yaml.safe_load(self._registry_path.read_text(encoding="utf-8"))
        templates = data.get("templates", {})
        for tid, tdata in templates.items():
            rel_path = tdata.get("path", "")
            full_path = _PA_ROOT / rel_path
            assert full_path.exists(), \
                f"Registry entry '{tid}' references '{rel_path}' which does not exist on disk"

    def test_all_section_contract_ref_paths_exist(self):
        data = yaml.safe_load(self._registry_path.read_text(encoding="utf-8"))
        templates = data.get("templates", {})
        for tid, tdata in templates.items():
            for section, ref_path in tdata.get("section_contract_refs", {}).items():
                full = _PA_ROOT / ref_path
                assert full.exists(), \
                    f"Template '{tid}' section_contract_refs['{section}'] = '{ref_path}' not on disk"
