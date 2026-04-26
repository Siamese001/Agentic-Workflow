"""00C.9 Runtime Gates Layer Integration & Invocation Map.

Doctrinal source:
``docs/reference/00C_Runtime_Gates_Current_Run_Mesh/00C.9_RG_Layer_Integration_Invocation_Map.md``

Defines WHERE the 29-gate mesh (G01-G29) is invoked across the 11 layers
(U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L6) WITHOUT moving ownership of
the gate semantics into those layers.

Ownership rule (00C.9 §UNIQUE OWNERSHIP SURFACE):
    00C owns reusable gate invocation law and GateVerdict receipt schema.
    Layer files own local receipts and may call gates, but do not redefine
    the G01-G29 gate family semantics.

This module is *data* (mappings + small pure helpers); it does not perform
gate evaluation. Evaluation is owned by the 29 evaluator modules
``g01_*.py``..``g29_*.py``.
"""

from __future__ import annotations

from typing import Mapping, Tuple

# ----------------------------------------------------------------------------
# INVOCATION MAP (00C.9 §INVOCATION MAP, lines 71-122)
# ----------------------------------------------------------------------------
# Schema: layer -> component -> invocation_point -> tuple[gate_id, ...]
#
# Tuples are exhaustive enumerations of the gates that MUST be invoked at the
# named invocation_point. Order is doctrine-stable.
# ----------------------------------------------------------------------------

INVOCATION_MAP: Mapping[str, Mapping[str, Mapping[str, Tuple[str, ...]]]] = {
    # U0 / Intake (00C.9 lines 71-73)
    "U0": {
        "intake": {
            "before_accepting_request": ("G01", "G02"),
            "before_handoff_to_l1": ("G03_lite", "G04_lite", "G17_lite"),
        },
    },
    # L1 / Planning (lines 75-78)
    "L1": {
        "planning": {
            "after_intent_frame": ("G03",),
            "after_risk_hints": ("G04", "G05"),
            "before_l1_plan_contract_emission": ("G18_pre",),
        },
    },
    # L0 / Routing (lines 80-84)
    "L0": {
        "routing": {
            "before_route_selection": ("G07",),
            "when_grounding_considered": ("G08",),
            "when_cache_considered": ("G10_cache",),
            "before_route_contract_emit": ("G20",),
        },
    },
    # 03A C0 (lines 86-89)
    "C0": {
        "retrieval": {
            "before_retrieval_plan": ("G08", "G17"),
            "after_fetch_shape": ("G09", "G13"),
            "before_final_evidence_contract": ("G09", "G24"),
        },
    },
    # 03B Prompt Assembly (lines 91-94)
    "PA": {
        "prompt_assembly": {
            "pa0_boundary": ("G10",),
            "pa3_airlock": ("G13", "G17", "G23"),
            "pa7_final_emit": ("G10", "G21"),
        },
    },
    # L3 Orchestration (lines 96-100)
    "L3": {
        "orchestration": {
            "workflow_expansion": ("G18",),
            "loop_retry_readiness": ("G19",),
            "budget_slo_before_dispatch": ("G20",),
            "anomaly_check_managed": ("G25",),
        },
    },
    # L2 Execute (lines 102-109)
    "L2": {
        "execution": {
            "e1_prep": ("G11", "G15", "G16", "G20", "G24"),
            "e2_valid": ("G11", "G12", "G14", "G15", "G17", "G23"),
            "e3_before_call": ("G11", "G12", "G14", "G15", "G20"),
            "e3_after_output_capture": ("G21", "G23"),
            "e4_heal": ("G19", "G24"),
            "e5_seal": ("G21", "G24", "G28"),
            "state_diff_candidate_present": ("G27_pre_eligibility",),
        },
    },
    # Exit (lines 111-113)
    "Exit": {
        "checkout": {
            "x1a_x1j_consume_verdicts": (
                "G21",
                "G22",
                "G23",
                "G24",
                "G25",
                "G26",
                "G27",
                "G28",
            ),
        },
    },
    # UWG / L4 (lines 115-117)
    "UWG": {
        "durable_write_admission": {
            "before_durable_write": ("G27",),
            "before_audit_receipt_completion": ("G28",),
        },
    },
    # L6 Observer / Learning Firewall (lines 119-122)
    "L6": {
        "observer": {
            "observer_isolation": ("G29",),
            "runtime_anomaly_pre_exit_only": ("G25",),
        },
    },
    # Cross-cutting reactive invocations (00C.2 §G06 HITL doctrine).
    # G06 is reactive: it fires whenever any upstream gate emits
    # ESCALATE_HITL or when policy requires human review. It does NOT
    # have a single fixed invocation point in 00C.9's layer table, so it
    # is captured here as the cross-cutting entry that closes the
    # G01-G29 coverage assertion.
    "CROSS_CUTTING": {
        "hitl_approval": {
            "on_any_escalate_hitl_disposition": ("G06",),
        },
    },
}


# ----------------------------------------------------------------------------
# RESULT_CLASS_MAPPING (00C.9 §RESULT MAPPING TO L2 RESULT_CLASS, lines 126-132)
# ----------------------------------------------------------------------------

RESULT_CLASS_MAPPING: Mapping[str, str] = {
    # Gate FAIL before E3 execution
    "fail_before_e3": "REJECTED",
    # Gate UNKNOWN on material authority/safety
    "unknown_material_default": "NEEDS_HELP",
    # Gate UNKNOWN on material authority/safety, when route policy says FAIL_TERMINAL
    "unknown_material_fail_terminal_policy": "FAIL_TERMINAL",
    # Gate WARN on non-material quality
    "warn_non_material_continue_with_policy": "CONTINUE_WITH_WARN_PRESERVED",
    # G21 schema fail after E3 (only if same-authority repair allowed)
    "g21_schema_fail_after_e3": "SOFT_REPAIRABLE",
    # G23 security/leak fail
    "g23_security_leak_fail": "REJECTED_AND_QUARANTINE",
    # G24 replay fail
    "g24_replay_fail_default": "FAIL_TERMINAL",
    "g24_replay_fail_needs_help": "NEEDS_HELP",
    # G27 direct-write attempt
    "g27_direct_write_attempt": "REJECTED",
}


# ----------------------------------------------------------------------------
# Canonical gate registry — full mesh
# ----------------------------------------------------------------------------

ALL_GATE_IDS: Tuple[str, ...] = tuple(f"G{i:02d}" for i in range(1, 30))


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

# Suffixes that mark "lite" / "pre-check" / "cache" / "pre-eligibility"
# variants. These are still counted as the underlying gate for coverage.
_VARIANT_SUFFIXES: Tuple[str, ...] = (
    "_lite",
    "_pre",
    "_cache",
    "_pre_eligibility",
)


def _canonicalize(gate_token: str) -> str:
    """Strip variant suffixes so ``G03_lite`` → ``G03``."""
    for suffix in _VARIANT_SUFFIXES:
        if gate_token.endswith(suffix):
            return gate_token[: -len(suffix)]
    return gate_token


def gates_invoked_by_layer(layer: str) -> Tuple[str, ...]:
    """Return all canonical gate IDs invoked anywhere within ``layer``."""
    if layer not in INVOCATION_MAP:
        return ()
    seen: list[str] = []
    for component in INVOCATION_MAP[layer].values():
        for invocations in component.values():
            for token in invocations:
                canon = _canonicalize(token)
                if canon not in seen:
                    seen.append(canon)
    return tuple(seen)


def layers_invoking_gate(gate_id: str) -> Tuple[str, ...]:
    """Return every layer whose invocation map references ``gate_id``."""
    seen: list[str] = []
    for layer, components in INVOCATION_MAP.items():
        for invocations in components.values():
            for tokens in invocations.values():
                if any(_canonicalize(t) == gate_id for t in tokens):
                    if layer not in seen:
                        seen.append(layer)
                    break
    return tuple(seen)


def covered_gates() -> Tuple[str, ...]:
    """Return the set of canonical gate IDs covered anywhere in the map."""
    seen: list[str] = []
    for layer in INVOCATION_MAP:
        for canon in gates_invoked_by_layer(layer):
            if canon not in seen:
                seen.append(canon)
    return tuple(sorted(seen))


def coverage_gap() -> Tuple[str, ...]:
    """Return canonical gate IDs in ``ALL_GATE_IDS`` NOT covered by the map."""
    covered = set(covered_gates())
    return tuple(g for g in ALL_GATE_IDS if g not in covered)


def result_class_for(
    *,
    gate_id: str,
    result: str,
    stage: str = "before_e3",
    route_fail_terminal: bool = False,
    same_authority_repair_allowed: bool = True,
) -> str:
    """Return the L2 result_class implied by a gate verdict per 00C.9 lines 126-132.

    Args:
        gate_id: Canonical gate identifier (G01-G29).
        result: One of {PASS, FAIL, WARN, UNKNOWN, NOT_APPLICABLE}.
        stage: Where in the L2 pipeline the verdict was emitted
            ('before_e3' | 'after_e3' | 'seal').
        route_fail_terminal: True if the route policy is FAIL_TERMINAL on
            unknown-material verdicts.
        same_authority_repair_allowed: True if G21 schema-fail can be repaired
            in-authority.

    Returns:
        The L2 result_class string per 00C.9 lines 126-132 (e.g., 'REJECTED',
        'NEEDS_HELP', 'SOFT_REPAIRABLE', 'FAIL_TERMINAL', 'PASS').
    """
    if result == "FAIL":
        if gate_id == "G23":
            return RESULT_CLASS_MAPPING["g23_security_leak_fail"]
        if gate_id == "G24":
            return (
                RESULT_CLASS_MAPPING["g24_replay_fail_needs_help"]
                if not route_fail_terminal
                else RESULT_CLASS_MAPPING["g24_replay_fail_default"]
            )
        if gate_id == "G27":
            return RESULT_CLASS_MAPPING["g27_direct_write_attempt"]
        if gate_id == "G21" and stage == "after_e3" and same_authority_repair_allowed:
            return RESULT_CLASS_MAPPING["g21_schema_fail_after_e3"]
        if stage == "before_e3":
            return RESULT_CLASS_MAPPING["fail_before_e3"]
        return "FAIL_TERMINAL"
    if result == "UNKNOWN":
        if route_fail_terminal:
            return RESULT_CLASS_MAPPING["unknown_material_fail_terminal_policy"]
        return RESULT_CLASS_MAPPING["unknown_material_default"]
    if result == "WARN":
        return RESULT_CLASS_MAPPING["warn_non_material_continue_with_policy"]
    if result in ("PASS", "NOT_APPLICABLE"):
        return "PASS"
    raise ValueError(f"Unknown result class: {result!r}")


__all__ = [
    "INVOCATION_MAP",
    "RESULT_CLASS_MAPPING",
    "ALL_GATE_IDS",
    "gates_invoked_by_layer",
    "layers_invoking_gate",
    "covered_gates",
    "coverage_gap",
    "result_class_for",
]
