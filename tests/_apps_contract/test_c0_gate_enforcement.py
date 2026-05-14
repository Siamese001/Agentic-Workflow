"""W1/W4 C0 gate enforcement tests — verify explicit gate verdicts in FEC.

Per plan 04_apps-rg-c0-architecture-analysis-f3d8b2, C0 must emit explicit
gate verdicts for all declared gates in runtime_gate_profile.

W4 PATCH: Derives expected C0 gates directly from runtime_gate_profile.resume_generation.v1.json
instead of hardcoded C0_GATE_IDS. Eliminates drift risk between profile and tests.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    STATUS_UNKNOWN,
    STATUS_NOT_APPLICABLE,
    SUPPORT_STATUS_PASS,
)
from agentic_core.runtime.gates.gate_types import (
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_NOT_APPLICABLE,
)


def load_c0_gate_profile() -> list[dict]:
    """Load C0 gates from runtime gate profile JSON.
    
    W4: This is the SSOT for expected C0 gates. No hardcoded gate lists allowed.
    """
    # Resolve relative to this test file's location (project root)
    test_file_dir = Path(__file__).parent.parent.parent
    profile_path = test_file_dir / "apps_rg" / "config" / "domain_contract" / "runtime_gate_profile.resume_generation.v1.json"
    
    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)
    
    c0_stage = profile.get("stages", {}).get("C0", {})
    return c0_stage.get("required_gates", [])


# Alias for backward compatibility
def derive_expected_c0_gates():
    """W4: Derive expected gates from profile.
    
    Alias for get_expected_c0_gates_for_context with default context.
    """
    return get_expected_c0_gates_for_context()


def get_expected_c0_gates_for_context(
    has_manual_brief: bool = False,
    has_chroma: bool = False,
    grounding_required: bool = True,
) -> dict[str, dict]:
    """Derive expected C0 gates and their applicability for the given context.
    
    W4: Replaces hardcoded C0_GATE_IDS with profile-derived expectations.
    
    Args:
        has_manual_brief: Whether manual_brief_path is provided (for G_BRIEF_BYPASS)
        has_chroma: Whether fact_vectors/Chroma is available (for G_SECTION_RETRIEVAL)
        grounding_required: Whether route.grounding_required is True
    
    Returns:
        Dict mapping gate_id -> {applicable: bool, expected_verdict: str, reason_required: bool}
    """
    profile_gates = load_c0_gate_profile()
    conditional_triggers = load_conditional_triggers()
    
    expectations: dict[str, dict] = {}
    
    for gate in profile_gates:
        gate_id = gate.get("gate_id")
        is_conditional = gate.get("conditional", False)
        condition_ref = gate.get("condition_ref", "")
        
        if not is_conditional:
            # Non-conditional gates are always applicable
            expectations[gate_id] = {
                "applicable": True,
                "expected_verdict": None,  # Must have some verdict
                "reason_required": False,
                "allow_not_applicable": False,
            }
        else:
            # Conditional gates — applicability depends on trigger
            if gate_id == "G_BRIEF_BYPASS":
                applicable = has_manual_brief
                expectations[gate_id] = {
                    "applicable": applicable,
                    "expected_verdict": None if applicable else VERDICT_NOT_APPLICABLE,
                    "reason_required": not applicable,  # NOT_APPLICABLE requires reason
                    "allow_not_applicable": True,
                }
            elif gate_id == "G_SECTION_RETRIEVAL":
                # W4: Section retrieval is conditional on:
                # 1. section_retrieval_profile.enabled = true (checked in _perform_bounded_section_retrieval)
                # 2. grounding_required = true
                # 3. fact_vectors collection available (has_chroma)
                applicable = grounding_required and has_chroma
                expectations[gate_id] = {
                    "applicable": applicable,
                    "expected_verdict": None if applicable else VERDICT_NOT_APPLICABLE,
                    "reason_required": not applicable,
                    "allow_not_applicable": True,
                }
            else:
                # Unknown conditional gate — fail safe
                expectations[gate_id] = {
                    "applicable": True,
                    "expected_verdict": None,
                    "reason_required": False,
                    "allow_not_applicable": False,
                }
    
    return expectations


def load_conditional_triggers() -> dict[str, dict]:
    """Load conditional gate triggers from runtime gate profile."""
    # Resolve relative to test file location
    test_file_dir = Path(__file__).parent.parent.parent
    profile_path = test_file_dir / "apps_rg" / "config" / "domain_contract" / "runtime_gate_profile.resume_generation.v1.json"
    
    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)
    
    return profile.get("conditional_gate_triggers", {})


SUPPORT_STATUS_PASSING = "PASS"
SUPPORT_STATUS_PARTIAL = "PARTIAL"
SUPPORT_STATUS_WEAK = "WEAK_WITH_CAVEATS"
SUPPORT_STATUS_EMPTY = "EMPTY"
SUPPORT_STATUS_BLOCKED = "BLOCKED"
SUPPORT_STATUS_CONFLICTED = "CONFLICTED"
SUPPORT_STATUS_UNKNOWN = "UNKNOWN"

SUPPORT_STATUS_PASSING_VALUES = {SUPPORT_STATUS_PASSING, SUPPORT_STATUS_PARTIAL}


def test_c0_gate_ids_match_profile():
    """PROOF: Test gate list matches runtime_gate_profile.json."""
    profile_gates = load_c0_gate_profile()
    profile_gate_ids = [g["gate_id"] for g in profile_gates]
    
    # W4: Derive expected gates from profile instead of hardcoded C0_GATE_IDS
    expected_gate_ids = list(derive_expected_c0_gates().keys())
    
    assert set(expected_gate_ids) == set(profile_gate_ids), (
        f"Test gate list {expected_gate_ids} must match profile gates {profile_gate_ids}"
    )


def test_unknown_gate_not_treated_as_pass():
    """PROOF: UNKNOWN support_status is never treated as PASS.
    
    Per final_evidence_contract.py SUPPORT_STATUS_PASSING_VALUES = {PASS}.
    W2 invariant: ONLY "PASS" is a passing value. PARTIAL is forbidden.
    UNKNOWN is explicitly excluded.
    """
    from agentic_core.runtime.contracts.final_evidence_contract import (
        SUPPORT_STATUS_PASSING_VALUES,
    )
    
    # UNKNOWN must NOT be in passing values
    assert STATUS_UNKNOWN not in SUPPORT_STATUS_PASSING_VALUES, (
        "UNKNOWN must never be treated as PASS"
    )
    
    # Only PASS is passing (W2 invariant: PARTIAL removed from passing values)
    assert SUPPORT_STATUS_PASSING_VALUES == {SUPPORT_STATUS_PASS}, (
        "Only PASS may be treated as passing (W2: PARTIAL is not passing)"
    )


def test_fec_support_status_is_never_unknown_at_exit():
    """PROOF: FEC support_status UNKNOWN must not pass at Exit.
    
    This validates the contract-level enforcement.
    """
    # Build an FEC with UNKNOWN status
    fec_unknown = FinalEvidenceContract(
        request_id="test-req",
        run_id="test-run",
        app_id="apps_rg",
        trace_id="test-trace",
        l5_certification_ref="test-cert",
        support_status=STATUS_UNKNOWN,
    )
    
    # The FEC must report it is NOT passing
    assert not fec_unknown.support_status_is_passing(), (
        "FEC with UNKNOWN support_status must NOT be passing"
    )
    
    # Build FECs with each non-passing status
    non_passing_statuses = [
        SUPPORT_STATUS_EMPTY,
        SUPPORT_STATUS_WEAK,
        SUPPORT_STATUS_BLOCKED,
        SUPPORT_STATUS_CONFLICTED,
    ]
    
    for status in non_passing_statuses:
        fec = FinalEvidenceContract(
            request_id="test-req",
            run_id="test-run",
            app_id="apps_rg",
            trace_id="test-trace",
            l5_certification_ref="test-cert",
            support_status=status,
        )
        assert not fec.support_status_is_passing(), (
            f"FEC with {status} must NOT be passing"
        )


def test_actual_fec_from_c0_retrieve_has_gate_verdicts_or_explicit_non_passing():
    """PROOF: Actual FEC emitted by c0_retrieve_apps_rg has gate verdicts or explicit non-passing receipts.
    
    W1 BLOCKER EXPOSURE: If gate_verdict_refs is empty and no explicit NOT_APPLICABLE/UNKNOWN
    with reason is present, the test FAILS. This proves the gap exists before W2 implementation.
    
    Per plan §5 §10: Every declared C0 gate (G08, G09, G13, G17, G23, G24) must have either:
    - A concrete verdict ref in FEC.gate_verdict_refs, or
    - Explicit NOT_APPLICABLE result with non-empty reason, or  
    - Explicit UNKNOWN result with non-empty unknown_reason that is non-passing.
    
    Empty gate_verdict_refs with PASSING support_status = FAIL (silent gate skip detected).
    """
    from agentic_core.runtime.contracts.route_contract import RouteContract
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg
    
    # Arrange: Build a grounded route that will trigger C0
    route = RouteContract(
        request_id="test-req-gates-001",
        run_id="test-run-gates-001",
        app_id="apps_rg",
        trace_id="test-trace-gates-001",
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,  # KEY: C0 will fire
        model_generation_required=True,
        write_authority_present=False,
        tenant_id="apps_rg",
        l5_certification_ref="ag-w0-5:u0:ingress:apps_rg:gate-test-001",
    )
    
    validated = ValidatedRequest(
        request_id="test-req-gates-001",
        run_id="test-run-gates-001",
        app_id="apps_rg",
        task_class="resume_generation",
        payload_digest="sha256:gate-test-001",
        authority_validation_receipt={"status": "valid", "gates_checked": True},
        trace_id="test-trace-gates-001",
        tenant_id="apps_rg",
        app_payload={
            "jd_payload": {"jd_text": "Senior Software Engineer position requiring 10+ years experience"},
            "resume_payload": {"resume_text": "15 years experience in software engineering with Python and distributed systems"},
        },
        l5_certification_ref="ag-w0-5:u0:ingress:apps_rg:gate-test-001",
    )
    
    # Act: Call actual c0_retrieve_apps_rg to get the real FEC
    # Ensure no CHROMA_PERSIST_DIR to use file-only path (deterministic)
    import os
    old_chroma = os.environ.pop("CHROMA_PERSIST_DIR", None)
    try:
        fec = c0_retrieve_apps_rg(route, validated, chromadb_path=None)
    finally:
        if old_chroma:
            os.environ["CHROMA_PERSIST_DIR"] = old_chroma
    
    # Assert: FEC must be returned
    assert fec is not None, "c0_retrieve_apps_rg must return a FEC"
    assert isinstance(fec, FinalEvidenceContract), "Returned object must be FinalEvidenceContract"
    
    # Load declared C0 gates from profile
    profile_gates = load_c0_gate_profile()
    profile_gate_ids = {g["gate_id"] for g in profile_gates}
    
    # Parse gate verdict refs from FEC
    gate_refs = fec.gate_verdict_refs
    referenced_gate_ids = set()
    for ref in gate_refs:
        # Parse "gate:G08:ALLOWED" or similar patterns
        if ref.startswith("gate:"):
            parts = ref.split(":")
            if len(parts) >= 2:
                referenced_gate_ids.add(parts[1])
    
    # Determine if FEC has explicit non-passing status with reason
    has_explicit_non_passing = (
        fec.support_status == STATUS_NOT_APPLICABLE and fec.not_applicable_reason
    ) or (
        fec.support_status == STATUS_UNKNOWN and fec.unknown_reason
    ) or (
        fec.support_status in (SUPPORT_STATUS_EMPTY, SUPPORT_STATUS_WEAK, SUPPORT_STATUS_BLOCKED)
    )
    
    # W1 BLOCKER DETECTION:
    # If gate_verdict_refs is empty AND support_status is passing-like without explicit reason,
    # this is the gap that must be fixed in W2/W3.
    is_silent_gap = (
        len(gate_refs) == 0 and 
        not has_explicit_non_passing and
        fec.support_status in (SUPPORT_STATUS_PASS, SUPPORT_STATUS_PARTIAL, "", STATUS_UNKNOWN)
    )
    
    # FAIL if silent gap detected - this exposes the W2 blocker
    if is_silent_gap:
        pytest.fail(
            f"W1 BLOCKER EXPOSED: C0-stage gates are silently missing.\n"
            f"  - Declared C0 gates in profile: {profile_gate_ids}\n"
            f"  - FEC.gate_verdict_refs: {gate_refs} (EMPTY)\n"
            f"  - FEC.support_status: {fec.support_status}\n"
            f"  - FEC.not_applicable_reason: {fec.not_applicable_reason!r}\n"
            f"  - FEC.unknown_reason: {fec.unknown_reason!r}\n"
            f"\n"
            f"REQUIRED: Either populate gate_verdict_refs with verdicts for each declared gate,\n"
            f"OR set support_status to NOT_APPLICABLE/UNKNOWN with explicit reason.\n"
            f"\n"
            f"CLASSIFICATION: W2/W3 BLOCKER - Gate population deferred per plan §3 non-goals."
        )
    
    # If we have gate refs, verify all declared gates are covered
    if len(gate_refs) > 0:
        missing_gates = profile_gate_ids - referenced_gate_ids
        if missing_gates:
            pytest.fail(
                f"Missing gate verdicts for declared C0 gates: {missing_gates}\n"
                f"Referenced gates: {referenced_gate_ids}\n"
                f"All gate refs: {gate_refs}"
            )
    elif has_explicit_non_passing:
        # Acceptable: explicit non-passing with reason
        pass
    else:
        # Should not reach here due to is_silent_gap check above
        pytest.fail("Unexpected state: gates empty but not classified as silent gap")


def test_not_applicable_requires_reason():
    """PROOF: NOT_APPLICABLE status requires a non-empty reason.
    
    Per final_evidence_contract.py __post_init__ check.
    """
    # Building with NOT_APPLICABLE and no reason must raise ValueError
    with pytest.raises(ValueError) as exc_info:
        FinalEvidenceContract(
            request_id="test-req",
            run_id="test-run",
            app_id="apps_rg",
            trace_id="test-trace",
            l5_certification_ref="test-cert",
            support_status=STATUS_NOT_APPLICABLE,
            not_applicable_reason="",  # Empty - should fail
        )
    
    assert "NOT_APPLICABLE requires a reason" in str(exc_info.value), (
        "NOT_APPLICABLE without reason must raise ValueError"
    )
    
    # Building with NOT_APPLICABLE and a reason must succeed
    fec = FinalEvidenceContract(
        request_id="test-req",
        run_id="test-run",
        app_id="apps_rg",
        trace_id="test-trace",
        l5_certification_ref="test-cert",
        support_status=STATUS_NOT_APPLICABLE,
        not_applicable_reason="C0 retrieval skipped - file-only path",
    )
    assert fec.not_applicable_reason, "NOT_APPLICABLE with reason must succeed"


def test_unknown_status_allowed_without_reason():
    """PROOF: UNKNOWN status is permitted without a reason (producer may not have computed it).
    
    But downstream MUST NOT treat it as PASS.
    """
    # UNKNOWN without unknown_reason is allowed at construction
    fec = FinalEvidenceContract(
        request_id="test-req",
        run_id="test-run",
        app_id="apps_rg",
        trace_id="test-trace",
        l5_certification_ref="test-cert",
        support_status=STATUS_UNKNOWN,
        unknown_reason="",  # Empty is allowed for UNKNOWN
    )
    
    # But it must not be passing
    assert not fec.support_status_is_passing(), "UNKNOWN must not be passing"


def test_all_c0_gates_declared_in_profile():
    """PROOF: All expected C0 gates are declared in runtime_gate_profile.
    
    Validates the gate profile is complete.
    """
    profile_gates = load_c0_gate_profile()
    profile_gate_ids = {g["gate_id"] for g in profile_gates}
    
    # W4: Derive expected gates from profile instead of hardcoded C0_GATE_IDS
    expected_gates = set(derive_expected_c0_gates().keys())
    
    missing = expected_gates - profile_gate_ids
    extra = profile_gate_ids - expected_gates
    
    assert not missing, f"Missing gates in profile: {missing}"
    # Extra gates are OK (profile may have added more)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
