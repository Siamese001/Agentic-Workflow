"""W3: section_prompt_adapter compiles PA artifacts without dispatch wiring."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
import yaml

from apps_rg.prompt_assembly import EvidenceSource, PromptAssemblyError, PromptAssemblyInput
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt


@pytest.fixture
def _facts_jd():
    cand = EvidenceSource(
        source_type="candidate_facts",
        content="Fact: Widget Corp; Role: Engineer.",
        confidence=1.0,
        source_tag="candidate_facts",
    )
    jd = EvidenceSource(
        source_type="jd_requirements",
        content="JD: needs Python.",
        confidence=1.0,
        source_tag="jd_requirements",
    )
    return cand, jd


@pytest.fixture
def headline_assembly_input(_facts_jd):
    cand, jd = _facts_jd
    return PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id="w3-req",
        run_id="w3-run",
        trace_root="w3-trace",
        s0_system_preamble="""# NO FABRICATION OATH
You must not invent facts. NO FABRICATION.""",
        d0_fences="# Boundary\nOnly candidate_facts prove experience.",
        i0_instructions="Write a one-line professional headline.",
        e0_examples="# Example\nSVP | AI Platforms",
        y0_style_preferences="Concise.",
        c0_candidate_facts=cand,
        c0_jd_requirements=jd,
        u0_user_task="Compose headline aligned to JD without new facts.",
        r0_response_schema='{"type": "object", "properties": {"headline": {"type": "string"}}}',
    )


def test_compile_section_prompt_exposes_compiled_prompt_artifact_fields(headline_assembly_input):
    out = compile_section_prompt(headline_assembly_input, section_id="headline")
    assert isinstance(out, SectionCompiledPrompt)
    assert out.section_id == "headline"
    assert "headline_tailor_v1" in out.apps_rg_prompt_template_ref
    art = out.artifact
    assert art.prompt_hash
    assert isinstance(art.slot_lineage_map, dict) and art.slot_lineage_map
    assert isinstance(art.provider_render_manifest, dict) and art.provider_render_manifest
    assert isinstance(art.replay_manifest, dict) and art.replay_manifest
    assert art.response_schema_ref


def test_locked_section_fails_closed():
    cand = EvidenceSource(
        source_type="candidate_facts",
        content="x",
        confidence=1.0,
        source_tag="candidate_facts",
    )
    jd = EvidenceSource(
        source_type="jd_requirements",
        content="y",
        confidence=1.0,
        source_tag="jd_requirements",
    )
    assembly = PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id="r",
        run_id="n",
        trace_root="t",
        s0_system_preamble="NO FABRICATION OATH",
        i0_instructions="i",
        c0_candidate_facts=cand,
        c0_jd_requirements=jd,
        u0_user_task="u",
        r0_response_schema="{}",
    )
    with pytest.raises(PromptAssemblyError) as ei:
        compile_section_prompt(assembly, section_id="education")
    assert ei.value.code == "SECTION_NON_LLM_LOCKED"


def test_companion_requires_u_tier(headline_assembly_input):
    path = (
        Path(__file__).resolve().parents[2]
        / "apps_rg/prompt_assembly/section_prompt_contracts/unify_bullets.contract.yaml"
    )
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert raw["companion_context_allowed"] is False

    with pytest.raises(PromptAssemblyError) as ei:
        compile_section_prompt(
            headline_assembly_input,
            section_id="unify_bullets",
            companion_u_tier="forbidden companion",
        )
    assert ei.value.code == "COMPANION_NOT_ALLOWED"


def test_no_dispatch_lane_imports_section_prompt_adapter():
    root = Path(__file__).resolve().parents[2]
    dispatch_dir = root / "apps_rg/runtime/dispatch"
    for py_file in sorted(dispatch_dir.glob("*_dispatch.py")):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    roots.add(alias.name.partition(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.partition(".")[0])
        assert "section_prompt_adapter" not in roots
        txt = py_file.read_text(encoding="utf-8")
        assert "compile_section_prompt" not in txt


def test_section_prompt_adapter_has_no_agentic_core_import():
    path = Path(__file__).resolve().parents[2] / "apps_rg/runtime/bindings/section_prompt_adapter.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(a.name.partition(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.partition(".")[0])
    assert "agentic_core" not in imports

