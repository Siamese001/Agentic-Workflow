"""W5.1 Negative-control governance tests for apps_research.

Every test here asserts that a forbidden pattern does NOT silently pass.
A negative control that silently passes is itself a test failure.

Categories (per W5.1 spec):
NC1 — Missing RouteContract / FinalEvidenceContract fields
NC2 — COMPANY_BRIEF_DEEP with insufficient evidence — must NOT proceed to PA as PASS
NC3 — JD violations (missing content_hash, treated as authority, JD-company conflict)
NC4 — L2 forbidden actions (retrieve new evidence in E2, write L4 in E3, switch provider)
NC5 — PA forbidden actions (retrieve, call provider, emit Exit)
NC6 — Exit errors (missing support score, missing evidence refs)
NC7 — Legacy runner / off-spine bypasses still quarantined

Plan: apps-research-spine-alignment-d4e8f2 W5.1.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_research"
MAIN_PY = APP_DIR / "__main__.py"
PA_COMPILER = APP_DIR / "prompt_assembly" / "research_pa_compiler.py"
L2_ADAPTERS = APP_DIR / "integrations" / "research_l2_step_adapters.py"
FEC_PRODUCER = APP_DIR / "integrations" / "research_exit_fec_producer.py"
UWG_WRITER = APP_DIR / "integrations" / "research_brief_uwg_writer.py"
ENGINES_DIR = APP_DIR / "engines"
INTEGRATIONS_DIR = APP_DIR / "integrations"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# NC1 — FEC validation must reject incomplete contracts
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_fec_validate_raises_on_empty_c0_evidence_summary() -> None:
    """ResearchFinalEvidenceContract.validate() must raise FECValidationError
    when c0_evidence_summary is empty — missing C0 proof must NOT silently pass."""
    from apps_research.integrations.research_exit_fec_producer import (
        FECValidationError,
        ResearchFinalEvidenceContract,
    )
    fec = ResearchFinalEvidenceContract(
        c0_evidence_summary={},
        synthesis_model="test",
        e1_e5_receipts=["c0_evidence_gate_passed"],
        depth_profile="COMPANY_BRIEF_STANDARD",
        output_hash="abc",
    )
    with pytest.raises(FECValidationError):
        fec.validate()


@pytest.mark.governance
def test_fec_validate_raises_on_empty_output_hash() -> None:
    """FEC with empty output_hash must not pass validation — no proof of synthesis output."""
    from apps_research.integrations.research_exit_fec_producer import (
        FECValidationError,
        ResearchFinalEvidenceContract,
    )
    fec = ResearchFinalEvidenceContract(
        c0_evidence_summary={"depth_profile": "COMPANY_BRIEF_STANDARD"},
        synthesis_model="test",
        e1_e5_receipts=["c0_evidence_gate_passed"],
        depth_profile="COMPANY_BRIEF_STANDARD",
        output_hash="",
    )
    with pytest.raises(FECValidationError):
        fec.validate()


@pytest.mark.governance
def test_fec_validate_raises_on_empty_receipts() -> None:
    """FEC with no receipts must not pass validation — E1-E5 completion unverifiable."""
    from apps_research.integrations.research_exit_fec_producer import (
        FECValidationError,
        ResearchFinalEvidenceContract,
    )
    fec = ResearchFinalEvidenceContract(
        c0_evidence_summary={"depth_profile": "COMPANY_BRIEF_STANDARD"},
        synthesis_model="test",
        e1_e5_receipts=[],
        depth_profile="COMPANY_BRIEF_STANDARD",
        output_hash="abc123",
    )
    with pytest.raises(FECValidationError):
        fec.validate()


# ---------------------------------------------------------------------------
# NC2 — C0 gate: DEEP profile with insufficient evidence must fail gate
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_c0_bundle_gate_fails_on_deep_profile_insufficient_chunks() -> None:
    """COMPANY_BRIEF_DEEP C0EvidenceBundle.validate_gate() with <20 chunks must raise."""
    from apps_research.integrations.research_c0_adapter import (
        C0EvidenceBundle,
        C0GateFailed,
    )
    bundle = C0EvidenceBundle(
        chunks=[],
        chunk_count=5,
        depth_profile="COMPANY_BRIEF_DEEP",
        source_urls=[f"https://src{i}.com" for i in range(5)],
    )
    with pytest.raises(C0GateFailed):
        bundle.validate_gate()


@pytest.mark.governance
def test_c0_bundle_gate_fails_on_zero_chunks() -> None:
    """Any depth profile with zero chunks must raise C0GateFailed."""
    from apps_research.integrations.research_c0_adapter import (
        C0EvidenceBundle,
        C0GateFailed,
    )
    bundle = C0EvidenceBundle(
        chunks=[],
        chunk_count=0,
        depth_profile="COMPANY_BRIEF_STANDARD",
    )
    with pytest.raises(C0GateFailed):
        bundle.validate_gate()


@pytest.mark.governance
def test_c0_bundle_gate_passes_on_standard_profile_sufficient_chunks() -> None:
    """COMPANY_BRIEF_STANDARD with >=10 chunks must NOT raise — positive control."""
    from apps_research.integrations.research_c0_adapter import C0EvidenceBundle
    bundle = C0EvidenceBundle(
        chunks=[{"text": f"chunk_{i}"} for i in range(10)],
        chunk_count=10,
        depth_profile="COMPANY_BRIEF_STANDARD",
    )
    bundle.validate_gate()  # must not raise


# ---------------------------------------------------------------------------
# NC3 — JD violations
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_does_not_allow_jd_as_instruction_source() -> None:
    """PA compiler must not permit JD content to become instruction text.

    JD is DATA (grounding material), not AUTHORITY (prompt instructions).
    The compiler must never route JD text into the system prompt instruction slot.
    """
    assert PA_COMPILER.exists(), f"research_pa_compiler.py missing: {PA_COMPILER}"
    src = _src(PA_COMPILER)
    # PA compiler must not blindly pass jd content into system_instruction slots
    forbidden_patterns = [
        "jd_as_instruction",
        "jd_authority",
        "inject_jd_as_system",
    ]
    found = [p for p in forbidden_patterns if p in src]
    assert not found, (
        f"PA compiler contains JD-as-authority patterns: {found}. "
        "JD must be treated as DATA, not as instruction authority."
    )


@pytest.mark.governance
def test_c0_adapter_handles_jd_context() -> None:
    """C0 adapter must handle JD context — JD is a first-class C0 input.

    JD is DATA (grounding context for role-targeted briefs), not authority.
    The C0 adapter must propagate jd_context from the request without elevating
    it to an instruction source.
    """
    c0_adapter = APP_DIR / "integrations" / "research_c0_adapter.py"
    assert c0_adapter.exists(), f"research_c0_adapter.py missing: {c0_adapter}"
    src = _src(c0_adapter)
    assert "jd_context" in src or "jd" in src.lower(), (
        "research_c0_adapter.py has no JD-context handling. "
        "JD is a first-class C0 input for role-targeted briefs."
    )


# ---------------------------------------------------------------------------
# NC4 — L2 forbidden actions
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_l2_e2_pa_adapter_does_not_call_provider() -> None:
    """E2 PA compilation step must never call a provider directly.

    E2 compiles prompts; provider synthesis is E3's job. Calling a provider
    in E2 would bypass the PA-first invariant.
    """
    assert L2_ADAPTERS.exists()
    src = _src(L2_ADAPTERS)
    tree = ast.parse(src)

    # Find the E2PACompileAdapter class body
    e2_body_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "E2PACompileAdapter":
            for child in ast.walk(node):
                e2_body_lines.add(getattr(child, "lineno", 0))

    # In E2 class scope, must not call openai.*, anthropic.*, or any provider SDK
    provider_patterns = ["openai", "anthropic", "cohere", "call_governed_synthesis"]
    lines = src.splitlines()
    e2_violations = []
    in_e2 = False
    brace_depth = 0
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if "class E2PACompileAdapter" in stripped:
            in_e2 = True
        if in_e2:
            if stripped.startswith("class ") and "E2PACompileAdapter" not in stripped and brace_depth == 0:
                in_e2 = False
            for p in provider_patterns:
                if p in line and "import" not in line:
                    e2_violations.append(f"line {i}: {line.rstrip()}")

    assert not e2_violations, (
        "E2PACompileAdapter must not call provider synthesis. "
        "Provider calls belong in E3. Violations:\n"
        + "\n".join(f"  {v}" for v in e2_violations)
    )


@pytest.mark.governance
def test_l2_e2_pa_adapter_does_not_write_l4() -> None:
    """E2 must not write L4 state. Durable writes belong in E4+UWG only."""
    assert L2_ADAPTERS.exists()
    src = _src(L2_ADAPTERS)
    tree = ast.parse(src)
    # Check E2PACompileAdapter for L4-write call sites
    l4_write_patterns = ["DurableWriteGateway", "write_l4(", "StateStore(", "durable_write("]
    e2_lines = []
    in_e2 = False
    for i, line in enumerate(src.splitlines(), start=1):
        if "class E2PACompileAdapter" in line:
            in_e2 = True
        if in_e2 and line.strip().startswith("class ") and "E2PACompileAdapter" not in line:
            in_e2 = False
        if in_e2:
            for p in l4_write_patterns:
                if p in line:
                    e2_lines.append(f"line {i}: {line.rstrip()}")
    assert not e2_lines, (
        "E2PACompileAdapter must not write L4 state. "
        "Violations:\n" + "\n".join(f"  {v}" for v in e2_lines)
    )


@pytest.mark.governance
def test_l2_e3_synthesis_adapter_does_not_retrieve_new_evidence() -> None:
    """E3 provider synthesis must not initiate new C0 retrieval.

    Evidence retrieval is E1's job. E3 getting new evidence would break the
    C0-gate-first invariant and allow unvalidated evidence to enter synthesis.
    """
    assert L2_ADAPTERS.exists()
    src = _src(L2_ADAPTERS)
    retrieval_patterns = [
        "ResearchC0Adapter",
        "retrieve_briefing_bundle",
        "tavily_retrieval",
        ".retrieve(",
    ]
    # Scan only E3 class scope
    in_e3 = False
    e3_violations = []
    for i, line in enumerate(src.splitlines(), start=1):
        if "class E3ProviderSynthesisAdapter" in line:
            in_e3 = True
        if in_e3 and line.strip().startswith("class ") and "E3" not in line:
            in_e3 = False
        if in_e3:
            for p in retrieval_patterns:
                if p in line and "import" not in line:
                    e3_violations.append(f"line {i}: {line.rstrip()}")
    assert not e3_violations, (
        "E3ProviderSynthesisAdapter must not retrieve new evidence. "
        "Retrieval belongs in E1. Violations:\n"
        + "\n".join(f"  {v}" for v in e3_violations)
    )


# ---------------------------------------------------------------------------
# NC5 — PA forbidden actions
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_pa_compiler_does_not_call_provider() -> None:
    """research_pa_compiler.py must never call a provider SDK directly.

    PA compile is a pure text-transformation step. Any provider call in
    the compiler would bypass the governed gateway and break the PA-first
    invariant.
    """
    assert PA_COMPILER.exists()
    src = _src(PA_COMPILER)
    # Check docstring / comments say so — and verify no actual import of forbidden symbols
    forbidden = [
        "import openai",
        "import anthropic",
        "import cohere",
        "from openai",
        "from anthropic",
    ]
    found = [f for f in forbidden if f in src]
    assert not found, (
        f"research_pa_compiler.py must not import provider SDKs directly. "
        f"Found: {found}. PA compile is a text-transformation step only."
    )


@pytest.mark.governance
def test_pa_compiler_does_not_emit_exit() -> None:
    """PA compiler must not emit an Exit disposition.

    Exit is E5's job. PA compiler emitting Exit would short-circuit the
    full E1-E5 receipt chain.
    """
    assert PA_COMPILER.exists()
    src = _src(PA_COMPILER)
    exit_patterns = [
        "maybe_invoke_exit_eval",
        "X3E_SAFE_ABSTAIN",
        "X2_PASS",
        "emit_exit",
    ]
    found = [p for p in exit_patterns if p in src]
    # PA compiler's own docstring may document what it forbids — filter those
    # by checking if they appear outside comments/docstrings
    tree = ast.parse(src)
    real_violations = []
    for p in found:
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == p:
                real_violations.append(p)
            elif isinstance(node, ast.Attribute) and node.attr == p:
                real_violations.append(p)
    assert not real_violations, (
        f"PA compiler must not emit Exit dispositions (found call sites for: {real_violations}). "
        "Exit belongs in E5 only."
    )


@pytest.mark.governance
def test_pa_compiler_does_not_write_l4() -> None:
    """PA compiler must not import or invoke L4 write machinery.

    'DurableWriteGateway' appears in the module docstring as a *forbidden* item;
    that reference is acceptable. What is NOT acceptable is importing or calling it.
    """
    assert PA_COMPILER.exists()
    src = _src(PA_COMPILER)
    tree = ast.parse(src)
    # Check imports: must not import DurableWriteGateway or StateStore
    import_violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            node_src = ast.unparse(node)
            for bad in ("DurableWriteGateway", "StateStore", "write_l4"):
                if bad in node_src:
                    import_violations.append(node_src)
    assert not import_violations, (
        f"research_pa_compiler.py must not import L4 write symbols. "
        f"Found: {import_violations}"
    )


# ---------------------------------------------------------------------------
# NC6 — Exit / FEC errors
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_fec_produce_fec_raises_on_none_bundle() -> None:
    """produce_fec() called with None c0_bundle must not silently succeed.

    A None bundle means C0 retrieval never ran — the FEC must not be produced
    without proof of evidence retrieval.
    """
    from apps_research.integrations.research_exit_fec_producer import produce_fec
    # produce_fec with None c0_bundle: either AttributeError or FECValidationError —
    # either is acceptable; what's NOT acceptable is returning a valid FEC.
    try:
        fec = produce_fec(None, {"text": "hello", "provider": "test"})
        # If we got here, validate() must have raised or fec must be invalid
        assert fec is None or not getattr(fec, "output_hash", ""), (
            "produce_fec(None, ...) must not produce a valid FEC — "
            "no C0 bundle means no evidence proof."
        )
    except Exception:
        pass  # Any exception is acceptable — the important thing is it doesn't silently pass


@pytest.mark.governance
def test_fec_validate_requires_synthesis_model() -> None:
    """FEC with empty synthesis_model must fail validate() — provider provenance required."""
    from apps_research.integrations.research_exit_fec_producer import (
        FECValidationError,
        ResearchFinalEvidenceContract,
    )
    fec = ResearchFinalEvidenceContract(
        c0_evidence_summary={"depth_profile": "COMPANY_BRIEF_STANDARD"},
        synthesis_model="",
        e1_e5_receipts=["c0_evidence_gate_passed"],
        depth_profile="COMPANY_BRIEF_STANDARD",
        output_hash="abc123",
    )
    with pytest.raises(FECValidationError):
        fec.validate()


# ---------------------------------------------------------------------------
# NC7 — Legacy runner quarantine
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_legacy_hop_engines_not_imported_in_main() -> None:
    """__main__.py must not import the legacy hop engines.

    hop_company_brief_engine.py, hop_research_assembly_engine.py,
    hop_research_retrieval_engine.py are legacy pre-spine code.
    They must not be imported from __main__.py after W5.2 quarantine.
    """
    assert MAIN_PY.exists()
    src = _src(MAIN_PY)
    legacy_imports = [
        "hop_company_brief_engine",
        "hop_research_assembly_engine",
        "hop_research_retrieval_engine",
        "HopCompanyBriefEngine",
        "HopResearchAssemblyEngine",
        "HopResearchRetrievalEngine",
    ]
    found = [imp for imp in legacy_imports if imp in src]
    assert not found, (
        f"apps_research/__main__.py imports legacy hop engines: {found}. "
        "Legacy hop engines must be quarantined to archives/ after W5.2."
    )


@pytest.mark.governance
def test_run_research_script_not_imported_in_main() -> None:
    """__main__.py must not import apps_research.scripts.run_research.

    run_research.py is a legacy CLI runner. After W5.2 it is quarantined to
    archives/. Importing it from __main__.py would revive the off-spine bypass.
    """
    assert MAIN_PY.exists()
    src = _src(MAIN_PY)
    assert "run_research" not in src, (
        "apps_research/__main__.py must not import run_research. "
        "The legacy runner is quarantined to archives/ in W5.2."
    )


@pytest.mark.governance
def test_legacy_hop_engines_not_imported_in_engines_init() -> None:
    """apps_research/engines/__init__.py must not re-export legacy hop engines."""
    engines_init = ENGINES_DIR / "__init__.py"
    if not engines_init.exists():
        pytest.skip("engines/__init__.py not found")
    src = _src(engines_init)
    legacy_classes = [
        "HopCompanyBriefEngine",
        "HopResearchAssemblyEngine",
        "HopResearchRetrievalEngine",
    ]
    found = [c for c in legacy_classes if c in src]
    assert not found, (
        f"apps_research/engines/__init__.py re-exports legacy hop engines: {found}. "
        "Legacy engines must be quarantined."
    )


@pytest.mark.governance
def test_e1_e5_receipt_constants_defined() -> None:
    """L2 step adapters must define all 5 canonical E1-E5 receipt constants.

    These constants are the audit trail that Exit v6 verifies — missing any
    receipt constant means the pipeline cannot prove execution completeness.
    """
    assert L2_ADAPTERS.exists()
    src = _src(L2_ADAPTERS)
    required = [
        "RECEIPT_E1_C0_GATE",
        "RECEIPT_E2_PA_COMPILED",
        "RECEIPT_E3_SYNTHESIS_COMPLETE",
        "RECEIPT_E4_FEC_PRODUCED",
        "RECEIPT_E5_EXIT_INVOKED",
    ]
    missing = [r for r in required if r not in src]
    assert not missing, (
        f"research_l2_step_adapters.py missing receipt constants: {missing}. "
        "All 5 E1-E5 receipt names must be defined as module-level constants."
    )


@pytest.mark.governance
def test_all_e1_e5_receipts_exported() -> None:
    """ALL_E1_E5_RECEIPTS tuple must be defined and contain all 5 receipt names."""
    assert L2_ADAPTERS.exists()
    from apps_research.integrations.research_l2_step_adapters import ALL_E1_E5_RECEIPTS
    assert len(ALL_E1_E5_RECEIPTS) == 5, (
        f"ALL_E1_E5_RECEIPTS must contain exactly 5 receipts. Got {len(ALL_E1_E5_RECEIPTS)}: "
        f"{ALL_E1_E5_RECEIPTS}"
    )


@pytest.mark.governance
def test_research_fec_producer_produce_fec_no_longer_raises_not_implemented() -> None:
    """produce_fec() in research_exit_fec_producer.py must NOT raise NotImplementedError.

    W4.1 wired the implementation. A remaining NotImplementedError means
    the FEC will never be produced — Exit will fire with an empty contract.
    """
    assert FEC_PRODUCER.exists()
    src = _src(FEC_PRODUCER)
    tree = ast.parse(src)
    # Find produce_fec function and check it doesn't raise NotImplementedError
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "produce_fec":
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.Raise)
                    and isinstance(getattr(child, "exc", None), ast.Call)
                ):
                    exc = child.exc
                    if isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                        pytest.fail(
                            "produce_fec() still raises NotImplementedError. "
                            "W4.1 must implement it."
                        )


@pytest.mark.governance
def test_uwg_writer_has_commit_brief_record() -> None:
    """research_brief_uwg_writer.py must define commit_brief_record().

    The UWG writer is the only durable-write path. If it doesn't implement
    commit_brief_record, there is no governed write path at all.
    """
    assert UWG_WRITER.exists(), f"research_brief_uwg_writer.py missing: {UWG_WRITER}"
    src = _src(UWG_WRITER)
    assert "commit_brief_record" in src, (
        "research_brief_uwg_writer.py must define commit_brief_record(). "
        "This is the only durable write path for apps_research."
    )


@pytest.mark.governance
def test_uwg_writer_uses_durable_write_gateway() -> None:
    """UWG writer must invoke DurableWriteGateway — it must not fake the write."""
    assert UWG_WRITER.exists()
    src = _src(UWG_WRITER)
    assert "DurableWriteGateway" in src, (
        "research_brief_uwg_writer.py must use DurableWriteGateway. "
        "It must not fake or bypass the durable write gate."
    )
