"""00C.9 Layer Integration & Invocation Map tests.

Doctrinal source:
``docs/reference/00C_Runtime_Gates_Current_Run_Mesh/00C.9_RG_Layer_Integration_Invocation_Map.md``

Implements all 8 test contracts grandfathered in
``ops_scripts/ci/baselines/reference_test_contract_baseline.json``:

- ``test_gate_invocation_map_covers_g01_to_g29``
- ``test_l2_e2_invokes_tool_arg_gate_before_tool_call``
- ``test_l2_e3_invokes_egress_gate_before_external_call``
- ``test_pa_airlock_invokes_content_trust_gate``
- ``test_c0_contract_invokes_evidence_quality_gate``
- ``test_exit_consumes_but_does_not_redefine_gate_verdicts``
- ``test_unknown_material_gate_routes_to_human_or_fail_closed``
- ``test_direct_write_attempt_triggers_g27_and_l2_rejected``

Plus invocation-map-shape and result-class-mapping coverage tests.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates.layer_invocation_map import (
    ALL_GATE_IDS,
    INVOCATION_MAP,
    RESULT_CLASS_MAPPING,
    covered_gates,
    coverage_gap,
    gates_invoked_by_layer,
    layers_invoking_gate,
    result_class_for,
)


# ============================================================================
# 9.T1 — invocation map covers G01..G29
# ============================================================================


def test_gate_invocation_map_covers_g01_to_g29() -> None:
    """00C.9 §INVOCATION MAP — every gate G01..G29 must be invoked at
    SOME layer / component / invocation_point.

    G06 (HITL Approval) is captured under the CROSS_CUTTING layer because
    doctrine 00C.9 lists no fixed invocation point for it; G06 fires
    reactively whenever an upstream gate emits ESCALATE_HITL.
    """
    assert tuple(sorted(covered_gates())) == ALL_GATE_IDS
    assert coverage_gap() == ()


# ============================================================================
# 9.T2 — L2 E2 (Validate) invokes tool argument gate before tool call
# ============================================================================


def test_l2_e2_invokes_tool_arg_gate_before_tool_call() -> None:
    """00C.9 lines 102-104: L2 E2 (Valid) must invoke G12 (tool argument
    sanity) and G11 (tool/model registry) before any tool call. E3
    (before_call) must also re-validate G11 and G12 immediately before
    invocation."""
    e2_gates = INVOCATION_MAP["L2"]["execution"]["e2_valid"]
    e3_gates = INVOCATION_MAP["L2"]["execution"]["e3_before_call"]
    assert "G12" in e2_gates, "G12 (tool args) missing from L2 E2"
    assert "G11" in e2_gates, "G11 (tool/model registry) missing from L2 E2"
    assert "G12" in e3_gates, "G12 (tool args) missing from L2 E3 before_call"
    assert "G11" in e3_gates, "G11 (tool/model registry) missing from L2 E3 before_call"


# ============================================================================
# 9.T3 — L2 E3 invokes egress gate before external call
# ============================================================================


def test_l2_e3_invokes_egress_gate_before_external_call() -> None:
    """00C.9 line 105: L2 E3 (before model/tool/script call) must invoke
    G14 (external egress) AND G15 (filesystem/shell). Both gates are
    canonical egress checks for the corresponding side-effect class."""
    e3 = INVOCATION_MAP["L2"]["execution"]["e3_before_call"]
    assert "G14" in e3, "G14 (external egress) missing from L2 E3 before_call"
    assert "G15" in e3, "G15 (filesystem/shell) missing from L2 E3 before_call"


# ============================================================================
# 9.T4 — PA airlock invokes content-trust gate
# ============================================================================


def test_pa_airlock_invokes_content_trust_gate() -> None:
    """00C.9 line 93: PA.3 airlock must invoke G13 (tool/retrieved output
    trust) AND G17 (privacy/cross-context) AND G23 (security/leakage)."""
    airlock = INVOCATION_MAP["PA"]["prompt_assembly"]["pa3_airlock"]
    assert "G13" in airlock, "G13 (content trust) missing from PA airlock"
    assert "G17" in airlock, "G17 (privacy) missing from PA airlock"
    assert "G23" in airlock, "G23 (security/leakage) missing from PA airlock"


# ============================================================================
# 9.T5 — C0 contract invokes evidence quality gate
# ============================================================================


def test_c0_contract_invokes_evidence_quality_gate() -> None:
    """00C.9 lines 86-89: C0 must invoke G09 (evidence quality) before
    emitting FinalEvidenceContract, AND G24 (replay readiness) where
    applicable."""
    contract_point = INVOCATION_MAP["C0"]["retrieval"]["before_final_evidence_contract"]
    assert "G09" in contract_point, "G09 (evidence quality) missing from C0 final-contract gate"
    assert "G24" in contract_point, "G24 (replay readiness) missing from C0 final-contract gate"


# ============================================================================
# 9.T6 — Exit consumes verdicts but does NOT redefine the gate family
# ============================================================================


def test_exit_consumes_but_does_not_redefine_gate_verdicts() -> None:
    """00C.9 line 113: 'X3 disposition aggregates verdicts but does not
    own G01-G29 family definitions.'

    Doctrinal claim has two parts:
      (a) Exit must not invent new gate IDs outside G01..G29.
      (b) Each Exit-invoked gate's *definition* (evaluator module) must
          live under ``agentic_core/L5_safety/runtime_gates/``, NOT under
          ``Exit/`` — proving Exit consumes pre-existing verdicts.

    Note: it is doctrinally legitimate for some gates (e.g., G22 output
    quality, G26 exit-eligibility) to be invoked ONLY at Exit per the
    layer table, because Exit is the natural invocation point. What
    matters is that the gate semantics live in the runtime_gates package,
    not in Exit code.
    """
    import importlib

    exit_gates = INVOCATION_MAP["Exit"]["checkout"]["x1a_x1j_consume_verdicts"]
    # (a) No fabricated IDs
    for gate_id in exit_gates:
        assert gate_id in ALL_GATE_IDS, f"Exit invokes {gate_id!r} which is not a canonical G01..G29 id"
    # (b) Every Exit-invoked gate has its evaluator defined in the
    # runtime_gates package, not in any Exit module.
    for gate_id in exit_gates:
        gate_num = int(gate_id[1:])
        # Module names follow agentic_core/L5_safety/runtime_gates/g<NN>_*.py
        # Discover by scanning the package's namespace.
        from agentic_core.L5_safety import runtime_gates as rg_pkg

        rg_dir = list(rg_pkg.__path__)[0]
        import pathlib

        matching = list(pathlib.Path(rg_dir).glob(f"g{gate_num:02d}_*.py"))
        assert matching, (
            f"Exit invokes {gate_id} but no evaluator module "
            f"g{gate_num:02d}_*.py exists under runtime_gates/ — "
            f"Exit would be defining the gate (violates 00C.9 line 113)"
        )
        # And the evaluator is importable (proves it isn't an empty stub)
        rel = matching[0].stem
        importlib.import_module(f"agentic_core.L5_safety.runtime_gates.{rel}")


# ============================================================================
# 9.T7 — UNKNOWN on material authority/safety routes to human OR fail-closed
# ============================================================================


def test_unknown_material_gate_routes_to_human_or_fail_closed() -> None:
    """00C.9 line 127: 'Gate UNKNOWN on material authority/safety ->
    NEEDS_HELP unless route policy says FAIL_TERMINAL.'

    Two-path enforcement: default route is NEEDS_HELP (escalate to human);
    when route policy is fail-terminal, route is FAIL_TERMINAL. Both are
    fail-closed (never PASS, never silent continue)."""
    # Default policy -> NEEDS_HELP
    assert result_class_for(gate_id="G02", result="UNKNOWN", route_fail_terminal=False) == "NEEDS_HELP"
    # Fail-terminal policy -> FAIL_TERMINAL
    assert result_class_for(gate_id="G02", result="UNKNOWN", route_fail_terminal=True) == "FAIL_TERMINAL"
    # Neither path is PASS — UNKNOWN never converts to PASS (00C.D.4)
    for policy in (False, True):
        outcome = result_class_for(gate_id="G02", result="UNKNOWN", route_fail_terminal=policy)
        assert outcome != "PASS"
        assert "PASS" not in outcome.upper().split("_")


# ============================================================================
# 9.T8 — Direct-write attempt triggers G27 and L2 REJECTED
# ============================================================================


def test_direct_write_attempt_triggers_g27_and_l2_rejected() -> None:
    """00C.9 line 132: 'G27 direct-write attempt -> REJECTED.'

    G27 (durable write sovereignty) is invoked at L2 E1 prep (state-diff
    candidate present) and at UWG before durable write. A direct write
    attempt without UWG admission must produce a REJECTED L2 result."""
    # G27 must be invoked at L2 (state_diff path) and UWG (before-write)
    g27_layers = layers_invoking_gate("G27")
    assert "L2" in g27_layers, "G27 not invoked at L2 — direct-write attempt path missing"
    assert "UWG" in g27_layers, "G27 not invoked at UWG — durable-write admission missing"
    # G27 FAIL must yield REJECTED at any stage (00C.9 line 132)
    assert result_class_for(gate_id="G27", result="FAIL", stage="before_e3") == "REJECTED"
    assert result_class_for(gate_id="G27", result="FAIL", stage="after_e3") == "REJECTED"
    assert result_class_for(gate_id="G27", result="FAIL", stage="seal") == "REJECTED"


# ============================================================================
# Invocation map shape, result-class mapping, helper coverage
# ============================================================================


class TestInvocationMapShape:
    """Structural invariants on INVOCATION_MAP."""

    def test_all_doctrine_layers_present(self) -> None:
        """00C.9 §INVOCATION MAP enumerates 10 ownership layers + the
        cross-cutting reactive bucket for G06."""
        expected = {"U0", "L1", "L0", "C0", "PA", "L3", "L2", "Exit", "UWG", "L6", "CROSS_CUTTING"}
        assert set(INVOCATION_MAP.keys()) == expected

    def test_every_invocation_point_is_a_tuple_of_strings(self) -> None:
        for layer, components in INVOCATION_MAP.items():
            for component, points in components.items():
                for point_name, gate_tuple in points.items():
                    assert isinstance(gate_tuple, tuple), f"{layer}.{component}.{point_name} is not a tuple"
                    for token in gate_tuple:
                        assert isinstance(token, str)
                        assert token.startswith("G"), (
                            f"{layer}.{component}.{point_name}: {token!r} is not a G* id"
                        )

    def test_no_duplicate_invocation_keys(self) -> None:
        """Each (layer, component, invocation_point) triple must be unique."""
        seen: set[tuple[str, str, str]] = set()
        for layer, components in INVOCATION_MAP.items():
            for component, points in components.items():
                for point_name in points:
                    key = (layer, component, point_name)
                    assert key not in seen, f"duplicate invocation key {key}"
                    seen.add(key)

    def test_g06_only_in_cross_cutting(self) -> None:
        """G06 (HITL Approval) is reactive — captured under CROSS_CUTTING
        rather than any concrete layer per 00C.2 doctrine."""
        assert layers_invoking_gate("G06") == ("CROSS_CUTTING",)


class TestResultClassMapping:
    """00C.9 §RESULT MAPPING TO L2 RESULT_CLASS — every line has a code lever."""

    def test_g23_security_fail_is_rejected_and_quarantine(self) -> None:
        assert result_class_for(gate_id="G23", result="FAIL") == "REJECTED_AND_QUARANTINE"

    def test_g24_replay_fail_default_is_fail_terminal(self) -> None:
        assert result_class_for(gate_id="G24", result="FAIL", route_fail_terminal=True) == "FAIL_TERMINAL"

    def test_g24_replay_fail_with_needs_help_policy(self) -> None:
        assert result_class_for(gate_id="G24", result="FAIL", route_fail_terminal=False) == "NEEDS_HELP"

    def test_g21_schema_fail_after_e3_with_repair_is_soft_repairable(self) -> None:
        assert (
            result_class_for(
                gate_id="G21",
                result="FAIL",
                stage="after_e3",
                same_authority_repair_allowed=True,
            )
            == "SOFT_REPAIRABLE"
        )

    def test_warn_non_material_continues_with_warning_preserved(self) -> None:
        assert result_class_for(gate_id="G22", result="WARN") == "CONTINUE_WITH_WARN_PRESERVED"

    def test_pass_and_not_applicable_are_passing(self) -> None:
        assert result_class_for(gate_id="G05", result="PASS") == "PASS"
        assert result_class_for(gate_id="G05", result="NOT_APPLICABLE") == "PASS"

    def test_invalid_result_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown result"):
            result_class_for(gate_id="G05", result="WAT")

    def test_mapping_constants_match_doctrine(self) -> None:
        # 00C.9 lines 126-132: the 7 listed mappings — plus 2 sub-cases for
        # UNKNOWN policy variants and 2 for G24 — total 9 keys.
        expected_keys = {
            "fail_before_e3",
            "unknown_material_default",
            "unknown_material_fail_terminal_policy",
            "warn_non_material_continue_with_policy",
            "g21_schema_fail_after_e3",
            "g23_security_leak_fail",
            "g24_replay_fail_default",
            "g24_replay_fail_needs_help",
            "g27_direct_write_attempt",
        }
        assert set(RESULT_CLASS_MAPPING.keys()) == expected_keys
