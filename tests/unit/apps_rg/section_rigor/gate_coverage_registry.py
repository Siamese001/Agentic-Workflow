"""SSOT: where each lane-critical X2 gate is proven (weak payload vs dedicated test module).

Weak-fail cases live in ``weak_payloads.py`` and run via ``test_section_rigor_weak_gates.py``.
Dedicated modules hold section-specific nuance tests under ``section_rigor/lanes/`` plus
historical validators/contract tests referenced by path fragment.
"""

from __future__ import annotations

from tests.unit.apps_rg.section_rigor.lane_registry import LANE_CRITICAL_GATES

# Per-lane dedicated test path fragments (repo-relative). Any critical gate not in
# WEAK_FAIL_GATES must appear as a string literal in at least one of these files.
SECTION_DEDICATED_TEST_FRAGMENTS: dict[str, tuple[str, ...]] = {
    "headline": (
        "tests/unit/apps_rg/section_rigor/lanes/test_headline_section.py",
        "tests/unit/apps_rg/validators/test_headline_x2_fixed_prefix_contract.py",
        "tests/unit/apps_rg/validators/test_headline_proof_accounting.py",
        "tests/unit/apps_rg/claim_ledger/test_headline_claim_ledger.py",
        "tests/unit/apps_rg/runtime/sections/test_headline_lane_hardening.py",
    ),
    "executive_summary": (
        "tests/unit/apps_rg/section_rigor/lanes/test_executive_summary_section.py",
        "tests/unit/apps_rg/test_executive_summary_product_shape_x2.py",
        "tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py",
        "tests/_apps_contract/test_section_x2_x1d_drift_ci.py",
        "tests/_apps_contract/test_executive_summary_x2_x1d_drift_ci.py",
        "tests/unit/apps_rg/test_executive_summary_x2_x1d_adversarial.py",
        "tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py",
        "tests/_apps_contract/test_exec_summary_runtime_slice.py",
        "tests/unit/apps_rg/test_executive_summary_prompt_ssot.py",
        "tests/unit/apps_rg/runtime/sections/test_executive_summary_token_budget.py",
    ),
    "unify_bullets": (
        "tests/unit/apps_rg/section_rigor/lanes/test_unify_bullets_section.py",
        "tests/unit/apps_rg/runtime/validators/test_unify_mechanism_stack_x2.py",
        "tests/_apps_contract/test_unify_bullets_text_claim_coverage.py",
        "tests/_apps_contract/test_unify_bullets_section_pipeline.py",
        "tests/_apps_contract/test_unify_ibm_lanes_e2e.py",
    ),
    "unify_narrative": (
        "tests/unit/apps_rg/section_rigor/lanes/test_unify_narrative_section.py",
        "tests/unit/apps_rg/section_rigor/test_unify_ibm_companion_chain.py",
        "tests/_apps_contract/test_unify_narrative_north_star_contract.py",
        "tests/_apps_contract/test_unify_narrative_section_pipeline.py",
        "tests/_apps_contract/test_unify_ibm_lanes_e2e.py",
    ),
    "ibm_bullets": (
        "tests/unit/apps_rg/section_rigor/lanes/test_ibm_bullets_section.py",
        "tests/_apps_contract/test_ibm_bullets_text_claim_coverage.py",
        "tests/_apps_contract/test_ibm_bullets_section_pipeline.py",
        "tests/_apps_contract/test_unify_ibm_lanes_e2e.py",
    ),
    "ibm_narrative": (
        "tests/unit/apps_rg/section_rigor/lanes/test_ibm_narrative_section.py",
        "tests/unit/apps_rg/test_ibm_narrative_word_budget_x2.py",
        "tests/unit/apps_rg/runtime/validators/test_ibm_narrative_display_x2.py",
        "tests/unit/apps_rg/section_rigor/test_unify_ibm_companion_chain.py",
        "tests/_apps_contract/test_unify_ibm_lanes_e2e.py",
    ),
    "competencies": (
        "tests/unit/apps_rg/section_rigor/lanes/test_competencies_section.py",
        "tests/unit/apps_rg/test_competencies_rigor_x2.py",
        "tests/unit/apps_rg/test_competencies_certification_category_x2.py",
        "tests/unit/apps_rg/test_section_prompt_product_shape_drift.py",
        "tests/unit/apps_rg/test_section_prompt_judge_lockstep.py",
    ),
}


def weak_fail_gate_ids_by_lane() -> dict[str, frozenset[str]]:
    from tests.unit.apps_rg.section_rigor.weak_payloads import all_weak_fail_cases

    out: dict[str, set[str]] = {}
    for case in all_weak_fail_cases():
        out.setdefault(case.lane, set()).add(case.gate_id)
    return {lane: frozenset(gates) for lane, gates in out.items()}


def uncovered_critical_gates(repo_root) -> list[tuple[str, str]]:
    """Return (lane, gate_id) pairs with no weak-fail and no dedicated-test reference."""
    from pathlib import Path

    root = Path(repo_root)
    weak_by_lane = weak_fail_gate_ids_by_lane()
    missing: list[tuple[str, str]] = []

    for lane, critical in LANE_CRITICAL_GATES.items():
        weak = weak_by_lane.get(lane, frozenset())
        fragments = SECTION_DEDICATED_TEST_FRAGMENTS.get(lane, ())
        file_texts: list[str] = []
        for frag in fragments:
            path = root / frag.replace("/", "\\") if "\\" in str(root) else root / frag
            if path.is_file():
                file_texts.append(path.read_text(encoding="utf-8", errors="replace"))
        blob = "\n".join(file_texts)
        for gate_id in sorted(critical):
            if gate_id in weak:
                continue
            if gate_id in blob:
                continue
            missing.append((lane, gate_id))
    return missing


from tests.unit.apps_rg.section_rigor.rigor_gate_maps import (  # noqa: E402
    C0_SIDECAR_GATE_IDS,
    RETIRED_GATE_REFS,
    RetiredGateRef,
    gate_accounting_status,
    is_gate_verdict_known,
    validate_retired_gate_ref,
)

__all__ = [
    "LANE_CRITICAL_GATES",
    "SECTION_DEDICATED_TEST_FRAGMENTS",
    "C0_SIDECAR_GATE_IDS",
    "RETIRED_GATE_REFS",
    "RetiredGateRef",
    "gate_accounting_status",
    "is_gate_verdict_known",
    "uncovered_critical_gates",
    "validate_retired_gate_ref",
    "weak_fail_gate_ids_by_lane",
]
