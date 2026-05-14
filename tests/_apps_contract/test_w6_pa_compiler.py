"""W6: apps_rg PA Compiler tests — local compile/validation path.

Tests that verify:
- Registry resolves all 4 E3 templates
- Compiler emits stable prompt_hash for same input
- S0 precedes U0 and C0
- C0 has separate candidate_facts and jd_requirements tags
- R0 schema ref is present
- missing template_id fails closed
- missing required slot fails closed
- compiler.py has no agentic_core imports
"""

import ast
import hashlib
import json
from pathlib import Path

import pytest

from apps_rg.prompt_assembly import (
    CANONICAL_SLOT_ORDER,
    EvidenceSource,
    PromptAssemblyError,
    PromptAssemblyInput,
    PromptCompiler,
    compile_prompt,
    map_slots,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def valid_candidate_facts():
    """Sample candidate facts evidence source."""
    return EvidenceSource(
        source_type="candidate_facts",
        content="""Name: Amit Ayer
Role: SVP AI Solutions
Experience: 15 years in enterprise AI/ML
Employers: TechCorp, DataSystems Inc
Skills: Python, Machine Learning, System Design
Projects: Led AI transformation for 3 Fortune 500 companies
Metrics: Reduced inference latency by 40%, scaled to 10M daily predictions""",
        confidence=1.0,
        source_tag="candidate_facts",
    )


@pytest.fixture
def valid_jd_requirements():
    """Sample JD requirements evidence source."""
    return EvidenceSource(
        source_type="jd_requirements",
        content="""Title: SVP Engineering
Required Skills: Python, ML, System Design, Leadership
Seniority: Executive
Domain: Enterprise AI
Responsibilities: Lead AI strategy, build high-performing teams""",
        confidence=1.0,
        source_tag="jd_requirements",
    )


@pytest.fixture
def valid_input(valid_candidate_facts, valid_jd_requirements):
    """Sample valid PromptAssemblyInput."""
    return PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id="req-001",
        run_id="run-001",
        trace_root="trace-001",
        s0_system_preamble="""# NO FABRICATION OATH

You are a resume tailoring assistant. You must NEVER:
1. Invent employers, titles, dates, or achievements
2. Fabricate metrics or scope beyond candidate's evidence
3. Treat JD requirements as proof of candidate's experience

Candidate facts are GROUND TRUTH.""",
        d0_fences="""# DATA BOUNDARY
- Only use candidate_facts for factual claims
- JD is targeting context, not experience proof
- No external knowledge allowed""",
        i0_instructions="""Tailor the professional summary and experience bullets to align with the target role while preserving all facts exactly as stated in candidate_facts.""",
        e0_examples="""# EXAMPLE OUTPUT FORMAT
## Executive Summary Example
Results-driven technology leader with 15+ years scaling AI/ML platforms...""",
        y0_style_preferences="Use strong action verbs. Avoid passive voice.",
        c0_candidate_facts=valid_candidate_facts,
        c0_jd_requirements=valid_jd_requirements,
        u0_user_task="Create an executive-level tailored resume",
        r0_response_schema="""{"type": "object", "properties": {"summary": {"type": "string"}}}""",
        render_context={"target_company": "TechCorp", "target_role": "SVP Engineering"},
    )


@pytest.fixture
def compiler():
    """PromptCompiler instance."""
    return PromptCompiler()


# =============================================================================
# Registry Resolution Tests
# =============================================================================

class TestRegistryResolution:
    """Tests for template registry resolution."""
    
    def test_registry_resolves_strategic_tailor_v1(self, compiler):
        """Registry must resolve strategic_tailor_v1 template."""
        template = compiler.resolve_template("strategic_tailor_v1")
        assert template["template_id"] == "strategic_tailor_v1"
        assert "path" in template
    
    def test_registry_resolves_tailor_existing_v1(self, compiler):
        """Registry must resolve tailor_existing_v1 template."""
        template = compiler.resolve_template("tailor_existing_v1")
        assert template["template_id"] == "tailor_existing_v1"
        assert "path" in template
    
    def test_registry_resolves_generate_scratch_v1(self, compiler):
        """Registry must resolve generate_scratch_v1 template."""
        template = compiler.resolve_template("generate_scratch_v1")
        assert template["template_id"] == "generate_scratch_v1"
        assert "path" in template
    
    def test_registry_resolves_enhance_current_v1(self, compiler):
        """Registry must resolve enhance_current_v1 template."""
        template = compiler.resolve_template("enhance_current_v1")
        assert template["template_id"] == "enhance_current_v1"
        assert "path" in template
    
    def test_registry_fails_on_unknown_template(self, compiler):
        """Unknown template_id must fail closed."""
        with pytest.raises(PromptAssemblyError) as exc_info:
            compiler.resolve_template("nonexistent_template")
        
        assert exc_info.value.code == "UNKNOWN_TEMPLATE_ID"
        assert "nonexistent_template" in exc_info.value.message


# =============================================================================
# Compiler Stability Tests
# =============================================================================

class TestCompilerStability:
    """Tests for prompt hash stability."""
    
    def test_compiler_emits_stable_hash_for_same_input(self, valid_input):
        """Same input must produce identical prompt_hash."""
        artifact1 = compile_prompt(valid_input)
        artifact2 = compile_prompt(valid_input)
        
        assert artifact1.prompt_hash == artifact2.prompt_hash
        assert len(artifact1.prompt_hash) == 32  # SHA256 truncated
    
    def test_different_inputs_produce_different_hashes(self, valid_input):
        """Different inputs must produce different prompt_hashes."""
        artifact1 = compile_prompt(valid_input)
        
        # Modify the input content (not just metadata) to change hash
        # Changing u0_user_task changes the compiled system_prompt
        modified_input = PromptAssemblyInput(
            template_id=valid_input.template_id,
            request_id=valid_input.request_id,
            run_id=valid_input.run_id,
            trace_root=valid_input.trace_root,
            s0_system_preamble=valid_input.s0_system_preamble,
            d0_fences=valid_input.d0_fences,
            i0_instructions=valid_input.i0_instructions,
            e0_examples=valid_input.e0_examples,
            y0_style_preferences=valid_input.y0_style_preferences,
            c0_candidate_facts=valid_input.c0_candidate_facts,
            c0_jd_requirements=valid_input.c0_jd_requirements,
            u0_user_task="Different user task content",  # Different - affects system_prompt
            r0_response_schema=valid_input.r0_response_schema,
        )
        
        artifact2 = compile_prompt(modified_input)
        
        assert artifact1.prompt_hash != artifact2.prompt_hash


# =============================================================================
# Slot Ordering Tests
# =============================================================================

class TestSlotOrdering:
    """Tests for canonical slot ordering."""
    
    def test_s0_precedes_u0_and_c0(self, valid_input):
        """S0 must come before U0 and C0 in canonical order."""
        artifact = compile_prompt(valid_input)
        
        order = artifact.canonical_slot_order
        s0_idx = order.index("S0")
        
        if "U0" in order:
            assert s0_idx < order.index("U0"), "S0 must precede U0"
        if "C0" in order:
            assert s0_idx < order.index("C0"), "S0 must precede C0"
    
    def test_canonical_slot_order_matches_definition(self):
        """CANONICAL_SLOT_ORDER must match expected precedence."""
        expected = ["S0", "D0", "I0", "C0", "E0", "Y0", "U0", "R0", "H0", "M0"]
        assert CANONICAL_SLOT_ORDER == expected
    
    def test_artifact_includes_canonical_order(self, valid_input):
        """CompiledPromptArtifact must include canonical_slot_order."""
        artifact = compile_prompt(valid_input)
        
        assert len(artifact.canonical_slot_order) > 0
        assert "S0" in artifact.canonical_slot_order
        assert artifact.canonical_slot_order[0] == "S0"  # S0 must be first


# =============================================================================
# C0 Source Separation Tests
# =============================================================================

class TestC0SourceSeparation:
    """Tests for C0 candidate_facts/jd_requirements separation."""
    
    def test_c0_has_separate_candidate_facts_tag(self, valid_input):
        """C0 must contain separate candidate_facts tag."""
        artifact = compile_prompt(valid_input)
        
        c0_content = None
        for payload in artifact.slot_payloads:
            if payload.slot_id == "C0":
                c0_content = payload.content
                break
        
        assert c0_content is not None
        assert "<candidate_facts" in c0_content
    
    def test_c0_has_separate_jd_requirements_tag(self, valid_input):
        """C0 must contain separate jd_requirements tag."""
        artifact = compile_prompt(valid_input)
        
        c0_content = None
        for payload in artifact.slot_payloads:
            if payload.slot_id == "C0":
                c0_content = payload.content
                break
        
        assert c0_content is not None
        assert "<jd_requirements" in c0_content
    
    def test_c0_has_confidence_attribute(self, valid_input):
        """C0 tags must include confidence attribute."""
        artifact = compile_prompt(valid_input)
        
        c0_content = None
        for payload in artifact.slot_payloads:
            if payload.slot_id == "C0":
                c0_content = payload.content
                break
        
        assert c0_content is not None
        assert 'confidence="1.0"' in c0_content
    
    def test_artifact_has_source_separation_flag(self, valid_input):
        """CompiledPromptArtifact must set has_source_separation flag."""
        artifact = compile_prompt(valid_input)
        assert artifact.has_source_separation is True


# =============================================================================
# R0 Schema Tests
# =============================================================================

class TestR0Schema:
    """Tests for R0 schema reference."""
    
    def test_r0_schema_ref_is_present(self, valid_input):
        """R0 schema reference must be present in artifact."""
        artifact = compile_prompt(valid_input)
        
        assert artifact.response_schema_ref != ""
        assert "schema" in artifact.response_schema_ref.lower() or "json" in artifact.response_schema_ref.lower()
    
    def test_artifact_has_schema_reference_flag(self, valid_input):
        """CompiledPromptArtifact must set has_schema_reference flag."""
        artifact = compile_prompt(valid_input)
        assert artifact.has_schema_reference is True


# =============================================================================
# Validation Tests
# =============================================================================

class TestValidationFailures:
    """Tests for fail-closed validation."""
    
    def test_missing_template_id_fails_closed(self, valid_candidate_facts, valid_jd_requirements):
        """Missing template_id must fail closed."""
        with pytest.raises(PromptAssemblyError) as exc_info:
            # Empty template_id should fail
            PromptAssemblyInput(
                template_id="",  # Missing
                request_id="req-001",
                run_id="run-001",
                trace_root="trace-001",
                s0_system_preamble="NO FABRICATION oath here",
                i0_instructions="Test instructions",
                c0_candidate_facts=valid_candidate_facts,
                c0_jd_requirements=valid_jd_requirements,
                u0_user_task="Test task",
                r0_response_schema="{}",
            )
            # If construction passes, compile should fail
            compile_prompt(
                PromptAssemblyInput(
                    template_id="",
                    request_id="req-001",
                    run_id="run-001",
                    trace_root="trace-001",
                    s0_system_preamble="NO FABRICATION oath here",
                    i0_instructions="Test instructions",
                    c0_candidate_facts=valid_candidate_facts,
                    c0_jd_requirements=valid_jd_requirements,
                    u0_user_task="Test task",
                    r0_response_schema="{}",
                )
            )
        
        assert exc_info.value.code in ["MISSING_TEMPLATE_ID", "MISSING_NO_FABRICATION_OATH", "C0_MISSING_SOURCE_TAG"]
    
    def test_missing_no_fabrication_oath_fails_on_input(self, valid_candidate_facts, valid_jd_requirements):
        """Missing NO FABRICATION oath in S0 must fail on input creation."""
        with pytest.raises(PromptAssemblyError) as exc_info:
            PromptAssemblyInput(
                template_id="strategic_tailor_v1",
                request_id="req-001",
                run_id="run-001",
                trace_root="trace-001",
                s0_system_preamble="This lacks the required oath",  # Missing NO FABRICATION
                i0_instructions="Test instructions",
                c0_candidate_facts=valid_candidate_facts,
                c0_jd_requirements=valid_jd_requirements,
                u0_user_task="Test task",
                r0_response_schema="{}",
            )
        
        assert exc_info.value.code == "MISSING_NO_FABRICATION_OATH"
        assert "S0" in str(exc_info.value)
    
    def test_missing_c0_source_tag_fails(self):
        """Missing C0 source_tag must fail."""
        facts_without_tag = EvidenceSource(
            source_type="candidate_facts",
            content="Some facts",
            source_tag="",  # Missing
        )
        
        jd_without_tag = EvidenceSource(
            source_type="jd_requirements",
            content="Some requirements",
            source_tag="",  # Missing
        )
        
        with pytest.raises(PromptAssemblyError) as exc_info:
            PromptAssemblyInput(
                template_id="strategic_tailor_v1",
                request_id="req-001",
                run_id="run-001",
                trace_root="trace-001",
                s0_system_preamble="NO FABRICATION oath here",
                i0_instructions="Test instructions",
                c0_candidate_facts=facts_without_tag,
                c0_jd_requirements=jd_without_tag,
                u0_user_task="Test task",
                r0_response_schema="{}",
            )
        
        assert exc_info.value.code == "C0_MISSING_SOURCE_TAG"


# =============================================================================
# Component Hash Map Tests
# =============================================================================

class TestComponentHashMap:
    """Tests for component_hash_map."""
    
    def test_component_hash_map_is_populated(self, valid_input):
        """component_hash_map must be populated with hashes."""
        artifact = compile_prompt(valid_input)
        
        assert artifact.component_hash_map.s0_hash != ""
        assert artifact.component_hash_map.i0_hash != ""
        assert artifact.component_hash_map.c0_candidate_hash != ""
        assert artifact.component_hash_map.c0_jd_hash != ""
        assert artifact.component_hash_map.u0_hash != ""
        assert artifact.component_hash_map.r0_hash != ""
        assert artifact.component_hash_map.template_hash != ""
    
    def test_component_hashes_are_deterministic(self, valid_input):
        """Same input must produce same component hashes."""
        artifact1 = compile_prompt(valid_input)
        artifact2 = compile_prompt(valid_input)
        
        assert artifact1.component_hash_map.s0_hash == artifact2.component_hash_map.s0_hash
        assert artifact1.component_hash_map.c0_candidate_hash == artifact2.component_hash_map.c0_candidate_hash


# =============================================================================
# No agentic_core Imports Test
# =============================================================================

def test_compiler_has_no_agentic_core_imports():
    """compiler.py must not import from agentic_core."""
    compiler_path = Path(__file__).parent.parent.parent / "apps_rg" / "prompt_assembly" / "compiler.py"
    
    assert compiler_path.exists(), f"compiler.py not found at {compiler_path}"
    
    tree = ast.parse(compiler_path.read_text())
    
    bad_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("agentic_core"):
                    bad_imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("agentic_core"):
                bad_imports.append(node.module)
    
    assert not bad_imports, f"agentic_core imports found in compiler.py: {bad_imports}"


def test_contracts_has_no_agentic_core_imports():
    """contracts.py must not import from agentic_core."""
    contracts_path = Path(__file__).parent.parent.parent / "apps_rg" / "prompt_assembly" / "contracts.py"
    
    assert contracts_path.exists(), f"contracts.py not found at {contracts_path}"
    
    tree = ast.parse(contracts_path.read_text())
    
    bad_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("agentic_core"):
                    bad_imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("agentic_core"):
                bad_imports.append(node.module)
    
    assert not bad_imports, f"agentic_core imports found in contracts.py: {bad_imports}"


# =============================================================================
# Map Slots Function Tests
# =============================================================================

class TestMapSlots:
    """Tests for map_slots convenience function."""
    
    def test_map_slots_returns_dict(self, valid_input):
        """map_slots must return a dictionary of slot contents."""
        slots = map_slots(valid_input)
        
        assert isinstance(slots, dict)
        assert "S0" in slots
        assert "I0" in slots
        assert "C0" in slots
        assert "U0" in slots
        assert "R0" in slots
    
    def test_map_slots_includes_c0_with_tags(self, valid_input):
        """map_slots C0 must include tagged sources."""
        slots = map_slots(valid_input)
        
        c0_content = slots.get("C0", "")
        assert "<candidate_facts" in c0_content
        assert "<jd_requirements" in c0_content


# =============================================================================
# Artifact Structure Tests
# =============================================================================

class TestArtifactStructure:
    """Tests for CompiledPromptArtifact structure."""
    
    def test_artifact_has_slot_payloads(self, valid_input):
        """artifact.slot_payloads must be populated."""
        artifact = compile_prompt(valid_input)
        
        assert len(artifact.slot_payloads) > 0
        for payload in artifact.slot_payloads:
            assert payload.slot_id is not None
            assert payload.content is not None
            assert payload.content_hash is not None
    
    def test_artifact_has_slot_lineage_map(self, valid_input):
        """artifact.slot_lineage_map must be populated."""
        artifact = compile_prompt(valid_input)
        
        assert len(artifact.slot_lineage_map) > 0
        for slot_id, lineage in artifact.slot_lineage_map.items():
            assert slot_id in lineage  # lineage should include slot_id
    
    def test_artifact_has_provider_render_manifest(self, valid_input):
        """artifact.provider_render_manifest must be populated."""
        artifact = compile_prompt(valid_input)
        
        assert isinstance(artifact.provider_render_manifest, dict)
        assert "max_tokens" in artifact.provider_render_manifest
    
    def test_artifact_has_replay_manifest(self, valid_input):
        """artifact.replay_manifest must be populated."""
        artifact = compile_prompt(valid_input)
        
        assert isinstance(artifact.replay_manifest, dict)
        assert "prompt_hash" in artifact.replay_manifest
    
    def test_artifact_has_messages_format(self, valid_input):
        """artifact.messages must follow chat format."""
        artifact = compile_prompt(valid_input)
        
        assert isinstance(artifact.messages, list)
        assert len(artifact.messages) > 0
        assert artifact.messages[0]["role"] == "system"
        assert "content" in artifact.messages[0]
    
    def test_system_prompt_contains_slot_markers(self, valid_input):
        """system_prompt must contain slot markers."""
        artifact = compile_prompt(valid_input)
        
        assert "<!-- SLOT: S0 -->" in artifact.system_prompt
        assert "S0" in artifact.system_prompt
        assert "I0" in artifact.system_prompt or "C0" in artifact.system_prompt


# =============================================================================
# No Fabrication Oath Tests
# =============================================================================

class TestNoFabricationOath:
    """Tests for S0 no-fabrication oath."""
    
    def test_artifact_has_no_fabrication_flag(self, valid_input):
        """artifact.has_no_fabrication_oath must be True when oath present."""
        artifact = compile_prompt(valid_input)
        assert artifact.has_no_fabrication_oath is True
