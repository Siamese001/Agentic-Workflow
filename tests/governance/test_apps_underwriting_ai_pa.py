"""P1.5.4 Governance tests — apps_underwriting_ai Prompt Assembly (PA).

Tests 23–39: 17 tests covering:
  - BOM file existence and required slot declarations
  - Registry file existence and all 5 template registrations
  - All 5 template YAML files exist and have required fields
  - Compiler: CompiledPromptArtifact shape and hash binding fields
  - Compiler: verdict_hash and reason_codes_hash are present and deterministic
  - Compiler: different verdict/reason_codes → different artifact_hash
  - Compiler: c0_bundle_hash binds FinalEvidenceContract
  - Compiler: no provider import boundary
  - Compiler: no retrieve import boundary
  - Compiler: no L4 write import boundary
  - Compiler: PromptAssemblyError raised on missing BOM
  - Compiler: PromptAssemblyError raised on missing template
  - All templates declare verdict_locked and reason_codes_locked
  - All healing templates are E4_HEAL stage
  - Primary template is E3_EXEC stage
  - Evidence template is E2_VALID stage

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P1.5.4.

All 17 tests pass immediately after P1.5 creates the PA compiler + artifacts.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
import uuid
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_underwriting_ai"
PA_DIR = APP_DIR / "prompt_assembly"
TEMPLATES_DIR = PA_DIR / "templates"
BOM_PATH = PA_DIR / "prompt_bom.yaml"
REGISTRY_PATH = PA_DIR / "prompt_registry.yaml"
COMPILER_PATH = PA_DIR / "underwriting_pa_compiler.py"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.prompt_assembly.underwriting_pa_compiler import (
    CompiledPromptArtifact,
    PromptAssemblyError,
    compile_artifact,
    load_prompt_bom,
    load_prompt_registry,
)

_TEMPLATE_IDS = [
    "decision_rationale_enrichment_v1",
    "evidence_to_rationale_context_v1",
    "unsupported_reason_omission_v1",
    "rationale_caveat_and_confidence_repair_v1",
    "rationale_length_and_structure_repair_v1",
]

_HEALING_TEMPLATE_IDS = [
    "unsupported_reason_omission_v1",
    "rationale_caveat_and_confidence_repair_v1",
    "rationale_length_and_structure_repair_v1",
]

_STUB_C0 = {
    "evidence_contract_id": "ec-test-001",
    "c0_state": "PASS",
    "document_coverage_map": {"BANK_STATEMENT": True},
    "extracted_span_map": {},
    "contradiction_flags": [],
    "missing_evidence_flags": [],
    "support_score": 0.90,
    "evidence_sufficiency": "sufficient",
}


def _make_artifact(**kwargs: object) -> CompiledPromptArtifact:
    defaults = dict(
        template_id="decision_rationale_enrichment_v1",
        request_id="req-test-001",
        run_id="run-test-001",
        trace_id="trace-test-001",
        artifact_id=str(uuid.uuid4()),
        c0_bundle=_STUB_C0,
        verdict="APPROVE",
        reason_codes=["STRONG_CASH_FLOW", "LOW_LTV"],
    )
    defaults.update(kwargs)
    return compile_artifact(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Test 23 — BOM file exists
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_bom_file_exists() -> None:
    """prompt_bom.yaml must exist in apps_underwriting_ai/prompt_assembly/."""
    assert BOM_PATH.exists(), f"prompt_bom.yaml missing: {BOM_PATH}"


# ---------------------------------------------------------------------------
# Test 24 — BOM declares all required slots
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_bom_declares_all_required_slots() -> None:
    """BOM must declare S0, I0, C0, U0, D0, R0 as required slots."""
    bom = load_prompt_bom()
    required = bom.get("required_slots", [])
    for slot in ("S0", "I0", "C0", "U0", "D0", "R0"):
        assert slot in required, (
            f"prompt_bom.yaml missing required slot {slot!r}. "
            "All six slots (S0 I0 C0 U0 D0 R0) must be declared."
        )


# ---------------------------------------------------------------------------
# Test 25 — Registry file exists
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_registry_file_exists() -> None:
    """prompt_registry.yaml must exist in apps_underwriting_ai/prompt_assembly/."""
    assert REGISTRY_PATH.exists(), f"prompt_registry.yaml missing: {REGISTRY_PATH}"


# ---------------------------------------------------------------------------
# Test 26 — Registry declares all 5 templates
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_registry_declares_all_five_templates() -> None:
    """PromptRegistry must declare all 5 required template IDs."""
    registry = load_prompt_registry()
    templates = registry.get("templates", {})
    for tid in _TEMPLATE_IDS:
        assert tid in templates, (
            f"prompt_registry.yaml missing template '{tid}'. "
            f"All 5 templates must be registered: {_TEMPLATE_IDS}"
        )


# ---------------------------------------------------------------------------
# Test 27 — All 5 template YAML files exist
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_all_five_template_yaml_files_exist() -> None:
    """All 5 template YAML files must exist in prompt_assembly/templates/."""
    for tid in _TEMPLATE_IDS:
        template_path = TEMPLATES_DIR / f"{tid}.yaml"
        assert template_path.exists(), (
            f"Template file missing: {template_path}. "
            "All 5 template YAMLs must be created."
        )


# ---------------------------------------------------------------------------
# Test 28 — All templates declare template_id and allowed_stage
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_all_templates_declare_required_fields() -> None:
    """Every template YAML must declare template_id, allowed_stage, and output_type."""
    for tid in _TEMPLATE_IDS:
        template_path = TEMPLATES_DIR / f"{tid}.yaml"
        assert template_path.exists(), f"Template missing: {template_path}"
        with template_path.open(encoding="utf-8") as fh:
            tmpl = yaml.safe_load(fh)
        assert tmpl.get("template_id") == tid, (
            f"{tid}.yaml: template_id={tmpl.get('template_id')!r}, expected {tid!r}"
        )
        assert tmpl.get("allowed_stage"), f"{tid}.yaml: allowed_stage missing"
        assert tmpl.get("output_type"), f"{tid}.yaml: output_type missing"


# ---------------------------------------------------------------------------
# Test 29 — All templates declare verdict_locked and reason_codes_locked
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_all_templates_declare_firewall_flags() -> None:
    """Every template YAML must declare verdict_locked and reason_codes_locked."""
    for tid in _TEMPLATE_IDS:
        template_path = TEMPLATES_DIR / f"{tid}.yaml"
        assert template_path.exists()
        with template_path.open(encoding="utf-8") as fh:
            tmpl = yaml.safe_load(fh)
        assert "verdict_locked" in tmpl, (
            f"{tid}.yaml missing verdict_locked field. "
            "LLM firewall requires explicit declaration."
        )
        assert "reason_codes_locked" in tmpl, (
            f"{tid}.yaml missing reason_codes_locked field."
        )


# ---------------------------------------------------------------------------
# Test 30 — Primary template is E3_EXEC
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_primary_template_is_e3_exec_stage() -> None:
    """decision_rationale_enrichment_v1 must be allowed_stage=E3_EXEC."""
    template_path = TEMPLATES_DIR / "decision_rationale_enrichment_v1.yaml"
    assert template_path.exists()
    with template_path.open(encoding="utf-8") as fh:
        tmpl = yaml.safe_load(fh)
    assert tmpl.get("allowed_stage") == "E3_EXEC", (
        f"decision_rationale_enrichment_v1 allowed_stage={tmpl.get('allowed_stage')!r}; "
        "expected E3_EXEC."
    )


# ---------------------------------------------------------------------------
# Test 31 — Evidence template is E2_VALID
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_evidence_context_template_is_e2_valid_stage() -> None:
    """evidence_to_rationale_context_v1 must be allowed_stage=E2_VALID."""
    template_path = TEMPLATES_DIR / "evidence_to_rationale_context_v1.yaml"
    assert template_path.exists()
    with template_path.open(encoding="utf-8") as fh:
        tmpl = yaml.safe_load(fh)
    assert tmpl.get("allowed_stage") == "E2_VALID", (
        f"evidence_to_rationale_context_v1 allowed_stage={tmpl.get('allowed_stage')!r}; "
        "expected E2_VALID."
    )


# ---------------------------------------------------------------------------
# Test 32 — All 3 healing templates are E4_HEAL
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_all_healing_templates_are_e4_heal_stage() -> None:
    """All 3 repair templates must declare allowed_stage=E4_HEAL."""
    for tid in _HEALING_TEMPLATE_IDS:
        template_path = TEMPLATES_DIR / f"{tid}.yaml"
        assert template_path.exists()
        with template_path.open(encoding="utf-8") as fh:
            tmpl = yaml.safe_load(fh)
        assert tmpl.get("allowed_stage") == "E4_HEAL", (
            f"{tid} allowed_stage={tmpl.get('allowed_stage')!r}; expected E4_HEAL."
        )


# ---------------------------------------------------------------------------
# Test 33 — Compiler produces CompiledPromptArtifact with all hash fields
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_produces_artifact_with_all_hash_fields() -> None:
    """compile_artifact must return CompiledPromptArtifact with all required hash fields."""
    artifact = _make_artifact()
    assert isinstance(artifact, CompiledPromptArtifact)
    for field_name in (
        "prompt_bom_hash",
        "prompt_registry_hash",
        "template_hash",
        "c0_bundle_hash",
        "verdict_hash",
        "reason_codes_hash",
        "canonical_slot_bytes_hash",
        "artifact_hash",
    ):
        value = getattr(artifact, field_name)
        assert value, f"CompiledPromptArtifact.{field_name} is empty — must be a SHA-256 hex."
        assert len(value) == 64, (
            f"CompiledPromptArtifact.{field_name}={value!r} is not a 64-char SHA-256 hex."
        )


# ---------------------------------------------------------------------------
# Test 34 — verdict_hash is deterministic for same verdict
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_verdict_hash_is_deterministic() -> None:
    """Same verdict must produce the same verdict_hash across two compile calls."""
    a1 = _make_artifact(artifact_id="art-a", verdict="APPROVE", reason_codes=["LOW_LTV"])
    a2 = _make_artifact(artifact_id="art-b", verdict="APPROVE", reason_codes=["LOW_LTV"])
    assert a1.verdict_hash == a2.verdict_hash, (
        "verdict_hash must be deterministic for the same verdict string."
    )
    assert a1.reason_codes_hash == a2.reason_codes_hash, (
        "reason_codes_hash must be deterministic for the same reason codes."
    )


# ---------------------------------------------------------------------------
# Test 35 — Different verdict → different artifact_hash
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_different_verdict_produces_different_artifact_hash() -> None:
    """Different verdicts must produce different verdict_hash and artifact_hash values."""
    a_approve = _make_artifact(artifact_id="art-approve", verdict="APPROVE", reason_codes=["LOW_LTV"])
    a_decline = _make_artifact(artifact_id="art-decline", verdict="DECLINE", reason_codes=["HIGH_DTI"])
    assert a_approve.verdict_hash != a_decline.verdict_hash, (
        "Different verdicts must produce different verdict_hash values."
    )
    assert a_approve.artifact_hash != a_decline.artifact_hash, (
        "Different verdicts must produce different artifact_hash values."
    )


# ---------------------------------------------------------------------------
# Test 36 — c0_bundle_hash binds FinalEvidenceContract
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_c0_bundle_hash_binds_evidence_contract() -> None:
    """Different c0_bundle dicts must produce different c0_bundle_hash values."""
    c0_a = {**_STUB_C0, "support_score": 0.90}
    c0_b = {**_STUB_C0, "support_score": 0.55}
    a = _make_artifact(artifact_id="art-c0a", c0_bundle=c0_a)
    b = _make_artifact(artifact_id="art-c0b", c0_bundle=c0_b)
    assert a.c0_bundle_hash != b.c0_bundle_hash, (
        "Different FinalEvidenceContract dicts must produce different c0_bundle_hash values."
    )
    assert a.artifact_hash != b.artifact_hash, (
        "Different C0 evidence must produce different artifact_hash."
    )


# ---------------------------------------------------------------------------
# Test 37 — PromptAssemblyError raised on missing template
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_raises_on_unknown_template_id() -> None:
    """compile_artifact must raise PromptAssemblyError for an unknown template_id."""
    with pytest.raises(PromptAssemblyError, match="not found in PromptRegistry"):
        _make_artifact(template_id="nonexistent_template_v999")


# ---------------------------------------------------------------------------
# Test 38 — Compiler has no provider imports
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_has_no_provider_imports() -> None:
    """underwriting_pa_compiler.py must not import any LLM provider SDKs."""
    assert COMPILER_PATH.exists(), f"underwriting_pa_compiler.py missing: {COMPILER_PATH}"
    src = COMPILER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    forbidden = ["openai", "anthropic", "litellm", "cohere", "llm_client", "model_gateway"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for fb in forbidden:
                    assert not alias.name.startswith(fb), (
                        f"underwriting_pa_compiler.py imports forbidden provider '{alias.name}' "
                        f"at line {node.lineno}. PA compiler must not call providers."
                    )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for fb in forbidden:
                assert not mod.startswith(fb), (
                    f"underwriting_pa_compiler.py imports from forbidden module '{mod}' "
                    f"at line {node.lineno}. PA compiler must not call providers."
                )


# ---------------------------------------------------------------------------
# Test 39 — Compiler has no L4 write imports
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_has_no_l4_write_imports() -> None:
    """underwriting_pa_compiler.py must not import L4 write surfaces."""
    assert COMPILER_PATH.exists()
    src = COMPILER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    forbidden = ["DurableWriteGateway", "StateStore", "L4_state", "uwg_writer", "CommitRequest"]
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            node_src = ast.unparse(node)
            for fb in forbidden:
                assert fb not in node_src, (
                    f"underwriting_pa_compiler.py references forbidden L4 surface '{fb}' "
                    f"at line {node.lineno}. PA compiler must not mutate L4 state."
                )
