"""P1.5 Governance tests — apps_research Prompt Assembly layer.

Enforces that:
1. prompt_assembly/ package exists with all required files
2. prompt_bom.yaml declares the 6 required slots (S0 I0 C0 U0 D0 R0)
3. prompt_registry.yaml registers all 5 templates
4. All 5 template files exist with required fields
5. company_brief_synthesis_v1 has real slot bodies (not placeholder strings)
6. research_pa_compiler.py exports compile_prompt and CompiledPromptArtifact
7. Compiler is functionally isolated (no forbidden imports)
8. compile_prompt produces a CompiledPromptArtifact with populated hashes
9. Compiler rejects missing required slot
10. Compiler rejects missing input contract field

Plan: apps-research-spine-alignment-d4e8f2 P1.5.

Tests 22-31 in the governance suite.
"""
from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PA_DIR = REPO_ROOT / "apps_research" / "prompt_assembly"
TEMPLATES_DIR = PA_DIR / "templates"

REQUIRED_TEMPLATE_IDS = [
    "company_brief_synthesis_v1",
    "research_retrieval_plan_v1",
    "evidence_gap_analysis_v1",
    "brief_citation_repair_v1",
    "depth_profile_downgrade_v1",
]

REQUIRED_BOM_SLOTS = {"S0", "I0", "C0", "U0", "D0", "R0"}

FORBIDDEN_COMPILER_IMPORTS = [
    "openai",
    "anthropic",
    "cohere",
    "litellm",
    "groq",
    "tavily_retrieval",
    "reranker_adapter",
    "llm_client",
    "research_brief_uwg_writer",
    "DurableWriteGateway",
    "x3_dispositions",
    "exit_eval",
    "governed_research_run",
    "route_registry",
]


# ---------------------------------------------------------------------------
# 22. PA package exists
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_prompt_assembly_package_exists() -> None:
    """apps_research/prompt_assembly/ must exist with __init__.py."""
    assert PA_DIR.exists(), (
        f"apps_research/prompt_assembly/ missing: {PA_DIR}. "
        "P1.5 requires creating the governed Prompt Assembly layer."
    )
    assert (PA_DIR / "__init__.py").exists(), (
        "apps_research/prompt_assembly/__init__.py missing."
    )
    assert (PA_DIR / "prompt_bom.yaml").exists(), (
        "apps_research/prompt_assembly/prompt_bom.yaml missing."
    )
    assert (PA_DIR / "prompt_registry.yaml").exists(), (
        "apps_research/prompt_assembly/prompt_registry.yaml missing."
    )
    assert (PA_DIR / "research_pa_compiler.py").exists(), (
        "apps_research/prompt_assembly/research_pa_compiler.py missing."
    )
    assert TEMPLATES_DIR.exists(), (
        "apps_research/prompt_assembly/templates/ missing."
    )


# ---------------------------------------------------------------------------
# 23. BOM declares 6 required slots
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_prompt_bom_declares_required_slots() -> None:
    """prompt_bom.yaml must declare S0 I0 C0 U0 D0 R0 as required_slots."""
    bom_path = PA_DIR / "prompt_bom.yaml"
    assert bom_path.exists(), f"prompt_bom.yaml missing: {bom_path}"
    bom = yaml.safe_load(bom_path.read_text(encoding="utf-8"))

    assert bom.get("app") == "apps_research", (
        f"prompt_bom.yaml must declare app: apps_research. Got: {bom.get('app')}"
    )
    required_slots = set(bom.get("required_slots", []))
    missing = REQUIRED_BOM_SLOTS - required_slots
    assert not missing, (
        f"prompt_bom.yaml missing required slots: {missing}. "
        f"Must declare: {sorted(REQUIRED_BOM_SLOTS)}"
    )
    # All slots must have slot_definitions
    defs = bom.get("slot_definitions", {})
    for slot in REQUIRED_BOM_SLOTS:
        assert slot in defs, (
            f"prompt_bom.yaml missing slot_definitions entry for {slot}."
        )


# ---------------------------------------------------------------------------
# 24. Registry registers all 5 templates
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_prompt_registry_registers_all_templates() -> None:
    """prompt_registry.yaml must register all 5 required template IDs."""
    registry_path = PA_DIR / "prompt_registry.yaml"
    assert registry_path.exists(), f"prompt_registry.yaml missing: {registry_path}"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    templates = registry.get("templates", {})
    missing = [tid for tid in REQUIRED_TEMPLATE_IDS if tid not in templates]
    assert not missing, (
        f"prompt_registry.yaml missing template registrations: {missing}. "
        f"Required: {REQUIRED_TEMPLATE_IDS}"
    )
    # Each template entry must have a path
    for tid in REQUIRED_TEMPLATE_IDS:
        entry = templates[tid]
        assert entry.get("path"), (
            f"Template '{tid}' in prompt_registry.yaml missing 'path' field."
        )


# ---------------------------------------------------------------------------
# 25. All 5 template files exist with required fields
# ---------------------------------------------------------------------------

@pytest.mark.governance
@pytest.mark.parametrize("template_id", REQUIRED_TEMPLATE_IDS)
def test_apps_research_template_file_exists_and_valid(template_id: str) -> None:
    """Each registered template file must exist and have required fields."""
    registry_path = PA_DIR / "prompt_registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    raw_path = registry["templates"][template_id]["path"]
    template_path = REPO_ROOT / raw_path

    assert template_path.exists(), (
        f"Template file missing: {template_path} (registered as '{template_id}')"
    )
    tmpl = yaml.safe_load(template_path.read_text(encoding="utf-8"))

    assert tmpl.get("template_id") == template_id, (
        f"Template file template_id mismatch: expected '{template_id}', "
        f"got '{tmpl.get('template_id')}'"
    )
    assert tmpl.get("slot_bodies"), (
        f"Template '{template_id}' has empty slot_bodies."
    )
    assert tmpl.get("output_contract"), (
        f"Template '{template_id}' missing output_contract."
    )
    assert tmpl.get("allowed_stage"), (
        f"Template '{template_id}' missing allowed_stage."
    )
    assert tmpl.get("hash_fields"), (
        f"Template '{template_id}' missing hash_fields."
    )


# ---------------------------------------------------------------------------
# 26. company_brief_synthesis_v1 has real slot bodies (not placeholder)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_synthesis_template_has_real_slot_bodies() -> None:
    """company_brief_synthesis_v1 must have substantive S0/I0/C0/D0/R0 bodies.

    Detects placeholder templates that just say 'TODO' or single-line stubs.
    """
    registry_path = PA_DIR / "prompt_registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    raw_path = registry["templates"]["company_brief_synthesis_v1"]["path"]
    tmpl = yaml.safe_load((REPO_ROOT / raw_path).read_text(encoding="utf-8"))

    slot_bodies = tmpl.get("slot_bodies", {})
    required = ["S0", "I0", "C0", "D0", "R0"]
    for slot in required:
        body = slot_bodies.get(slot, "")
        assert isinstance(body, str) and len(body.strip()) > 50, (
            f"company_brief_synthesis_v1 slot {slot} body is empty or too short "
            f"(len={len(body.strip())}). Must be a real instruction body, not a placeholder."
        )
        assert "TODO" not in body and "PLACEHOLDER" not in body.upper(), (
            f"company_brief_synthesis_v1 slot {slot} body contains placeholder text."
        )

    # I0 must reference depth profile and grounding
    i0 = slot_bodies.get("I0", "")
    assert "depth_profile" in i0.lower() or "DEEP" in i0 or "DOSSIER" in i0, (
        "company_brief_synthesis_v1 I0 must reference depth profile constraints."
    )
    assert "citation" in i0.lower() or "C0" in i0, (
        "company_brief_synthesis_v1 I0 must reference citation requirements."
    )

    # C0 must declare evidence-only authority
    c0 = slot_bodies.get("C0", "")
    assert "data only" in c0.lower() or "evidence" in c0.lower(), (
        "company_brief_synthesis_v1 C0 must declare evidence-only authority."
    )


# ---------------------------------------------------------------------------
# 27. PA compiler exports required symbols
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_pa_compiler_exports_required_symbols() -> None:
    """research_pa_compiler.py must export compile_prompt and CompiledPromptArtifact."""
    compiler_path = PA_DIR / "research_pa_compiler.py"
    assert compiler_path.exists(), f"research_pa_compiler.py missing: {compiler_path}"

    src = compiler_path.read_text(encoding="utf-8")
    tree = ast.parse(src)

    # Check for class CompiledPromptArtifact
    class_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    }
    assert "CompiledPromptArtifact" in class_names, (
        "research_pa_compiler.py must define class CompiledPromptArtifact."
    )

    # Check for def compile_prompt
    func_names = {
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "compile_prompt" in func_names, (
        "research_pa_compiler.py must define compile_prompt()."
    )
    assert "compile_repair_prompt" in func_names, (
        "research_pa_compiler.py must define compile_repair_prompt() for E3 repair steps."
    )
    assert "PromptAssemblyError" in {
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    }, (
        "research_pa_compiler.py must define PromptAssemblyError."
    )


# ---------------------------------------------------------------------------
# 28. Compiler has no forbidden imports
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_pa_compiler_has_no_forbidden_imports() -> None:
    """research_pa_compiler.py must not import providers, retrieval, L4, or Exit."""
    compiler_path = PA_DIR / "research_pa_compiler.py"
    assert compiler_path.exists()
    src = compiler_path.read_text(encoding="utf-8")
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            else:
                names = [node.module or ""] + [alias.name for alias in node.names]
            for name in names:
                for forbidden in FORBIDDEN_COMPILER_IMPORTS:
                    if forbidden in (name or ""):
                        pytest.fail(
                            f"research_pa_compiler.py imports forbidden module "
                            f"'{forbidden}' at line {node.lineno}. "
                            "PA compiler must not import providers, retrieval, L4, or Exit."
                        )


# ---------------------------------------------------------------------------
# 29. compile_prompt produces artifact with populated hashes
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_compile_prompt_produces_valid_artifact() -> None:
    """compile_prompt() must return a CompiledPromptArtifact with populated hashes."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from apps_research.prompt_assembly.research_pa_compiler import (
        CompiledPromptArtifact,
        compile_prompt,
    )

    input_data: dict[str, Any] = {
        "target_entity": "Acme Corp",
        "depth_profile": "STANDARD",
        "c0_evidence_chunks": "[chunk_001] Acme Corp was founded in 2010.",
        "source_urls": "https://acmecorp.com",
        "research_request": "Provide a standard brief on Acme Corp.",
        "output_schema_ref": "ResearchBrief",
        "depth_profile_constraints": "Executive summary + key sections.",
        "emphasis_areas": "Products, leadership",
        "prior_brief_summary": "",
        "competitive_context": "",
    }
    context: dict[str, Any] = {
        "request_id": "req-test-001",
        "run_id": "run-test-001",
        "trace_id": "trace-test-001",
        "c0_bundle_hash": "abc123deadbeef",
        "depth_profile": "STANDARD",
        "route_id": "R3_SIMPLE_GROUNDED_READ",
        "audit_refs": [],
    }

    artifact = compile_prompt(
        template_id="company_brief_synthesis_v1",
        input_data=input_data,
        context=context,
    )

    assert isinstance(artifact, CompiledPromptArtifact), (
        f"compile_prompt must return CompiledPromptArtifact, got {type(artifact)}"
    )
    assert artifact.artifact_id, "CompiledPromptArtifact.artifact_id must be non-empty"
    assert artifact.prompt_bom_hash, "CompiledPromptArtifact.prompt_bom_hash must be non-empty"
    assert artifact.prompt_registry_hash, "CompiledPromptArtifact.prompt_registry_hash must be non-empty"
    assert artifact.template_hash, "CompiledPromptArtifact.template_hash must be non-empty"
    assert artifact.c0_bundle_hash == "abc123deadbeef", (
        "CompiledPromptArtifact.c0_bundle_hash must match context c0_bundle_hash"
    )
    assert artifact.canonical_slot_bytes_hash, "canonical_slot_bytes_hash must be non-empty"
    assert artifact.artifact_hash, "artifact_hash must be non-empty"
    assert artifact.template_id == "company_brief_synthesis_v1"
    assert artifact.route_id == "R3_SIMPLE_GROUNDED_READ"
    assert artifact.depth_profile == "STANDARD"
    # Rendered slots must contain S0, I0, C0, U0, D0, R0
    for slot in ("S0", "I0", "C0", "U0", "D0", "R0"):
        assert slot in artifact.rendered_slots, (
            f"CompiledPromptArtifact.rendered_slots missing slot {slot}"
        )
        assert artifact.rendered_slots[slot].strip(), (
            f"CompiledPromptArtifact.rendered_slots['{slot}'] is empty"
        )


# ---------------------------------------------------------------------------
# 30. Compiler rejects template with missing required slot body
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_compile_prompt_rejects_missing_slot() -> None:
    """compile_prompt() must raise PromptAssemblyError when a required slot body is absent."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    import copy
    import tempfile

    from apps_research.prompt_assembly.research_pa_compiler import (
        PromptAssemblyError,
        compile_prompt,
        load_prompt_registry,
        load_template,
    )

    # Load the real template and remove S0
    registry = load_prompt_registry()
    template = copy.deepcopy(load_template("company_brief_synthesis_v1", registry))
    del template["slot_bodies"]["S0"]

    # Write a temp template missing S0
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as tmp:
        import yaml as _yaml
        _yaml.dump(template, tmp)
        tmp_path = tmp.name

    # Write a temp registry pointing at the broken template
    broken_registry = {
        "schema_version": "1.0",
        "registry_id": "test_broken_registry",
        "templates": {
            "company_brief_synthesis_v1": {"path": tmp_path}
        },
        "hash_fields": ["schema_version", "registry_id"],
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as tmp_reg:
        _yaml.dump(broken_registry, tmp_reg)
        tmp_reg_path = tmp_reg.name

    with pytest.raises(PromptAssemblyError, match="missing slot bodies"):
        compile_prompt(
            template_id="company_brief_synthesis_v1",
            input_data={"x": "y"},
            context={"request_id": "r", "run_id": "r", "trace_id": "t"},
            registry_path=Path(tmp_reg_path),
        )


# ---------------------------------------------------------------------------
# 31. Compiler rejects missing required input field
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_compile_prompt_rejects_missing_input_field() -> None:
    """compile_prompt() must raise PromptAssemblyError when input_data is missing a required field."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from apps_research.prompt_assembly.research_pa_compiler import (
        PromptAssemblyError,
        compile_prompt,
    )

    # company_brief_synthesis_v1 requires 'target_entity' — omit it
    incomplete_input: dict[str, Any] = {
        "depth_profile": "STANDARD",
        # target_entity intentionally missing
    }
    context: dict[str, Any] = {
        "request_id": "req-x",
        "run_id": "run-x",
        "trace_id": "trace-x",
        "c0_bundle_hash": "hash123",
        "depth_profile": "STANDARD",
    }

    with pytest.raises(PromptAssemblyError, match="missing required fields"):
        compile_prompt(
            template_id="company_brief_synthesis_v1",
            input_data=incomplete_input,
            context=context,
        )
