"""Executive-summary extensions for X2/X1D contract (synthesis, judge packet, repair loop).

Generic per-lane checks: ``section_x2_x1d_contract``. CI: ``check_section_x2_x1d_drift.py``.
"""

from __future__ import annotations

import ast
from pathlib import Path

from apps_rg.runtime.judges import executive_summary_judge_packet as judge_packet_mod
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    build_deterministic_gate_summary,
)
from apps_rg.runtime.sections import executive_summary_lane as lane_mod
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    format_judge_regen_x2_floor,
)
from apps_rg.runtime.sections.section_product_shape_parity import (
    audit_ssot_seam_parity,
    judge_rubric_shape_constraints,
)
from apps_rg.runtime.sections.section_product_shape_ssot import (
    RETIRED_EXEC_SUMMARY_X2_GATE_IDS,
    section_product_shape,
)
from apps_rg.runtime.sections.executive_summary_x1d_judge_contract import (
    audit_executive_summary_x1d_judge_coherence,
)
from apps_rg.runtime.sections.section_x2_x1d_contract import (
    X2X1dDriftViolation,
    assert_all_generated_lanes_x2_x1d_contract,
    audit_all_generated_lanes_x2_x1d_drift,
    audit_lane_x2_x1d_drift,
    extract_runtime_x2_gate_ids,
)

SYNTHESIS_CHECK_TO_X2_GATE: dict[str, str] = {
    "check_synthesis_quality": "x2_executive_summary_synthesis_quality",
    "check_exec_summary_mechanical_opener_stack": "x2_exec_summary_mechanical_opener_stack_zero",
    "check_exec_summary_robotic_transition_stack": "x2_exec_summary_robotic_transition_stack_zero",
    "check_cross_fact_display_conflation": "x2_exec_summary_cross_fact_conflation_zero",
    "check_exec_summary_meta_filler_patterns": "x2_exec_summary_meta_filler_zero",
    "check_resume_display_colon_space_discipline": "x2_exec_summary_colon_stitch_zero",
    "check_exec_summary_sentence_count_6": "x2_exec_summary_sentence_count_6",
    "check_exec_summary_evidence_utilization": "x2_exec_summary_evidence_utilization",
    "check_exec_summary_paragraph_max_words": "x2_exec_summary_paragraph_max_words",
    "check_human_exec_voice": "x2_exec_summary_human_exec_voice",
    "check_exec_summary_no_mechanism_inventory": "x2_exec_summary_no_mechanism_inventory",
    "check_exec_summary_no_credential_dump": "x2_exec_summary_no_credential_dump",
    "check_north_star_style_example_echo_unsupported": "x2_north_star_style_echo_unsupported_zero",
    "check_inferred_bridge_claims": "x2_no_inferred_bridge_claims",
    "check_claim_ledger_materialized_or_gap_excused": "x2_claim_ledger_materialized_or_gap_excused",
    "check_claim_ledger_row_count_matches_sentence_count": (
        "x2_claim_ledger_row_count_matches_sentence_count"
    ),
    "check_exec_summary_no_sentence_fragment": "x2_exec_summary_no_sentence_fragment",
    "check_exec_summary_display_override_compliance": (
        "x2_exec_summary_display_override_compliance"
    ),
    "check_exec_summary_strategy_no_commercialization_thread": (
        "x2_exec_summary_strategy_no_commercialization_thread"
    ),
    "check_exec_summary_s5_no_derivatives_inventory": (
        "x2_exec_summary_s5_no_derivatives_inventory"
    ),
    "check_exec_summary_stock_bridge_count": "x2_exec_summary_stock_bridge_max_two",
}

SYNTHESIS_IMPLICIT_X2_GATES: frozenset[str] = frozenset(
    {"x2_first_person_zero", "x2_generic_filler_zero"}
)

JUDGE_PACKET_REQUIRED_GATE_KEYS: frozenset[str] = frozenset(
    {
        "x2_exec_summary_sentence_count_6",
        "x2_exec_summary_paragraph_max_words",
        "x2_exec_summary_evidence_utilization",
        "x2_exec_summary_no_credential_dump",
        "x2_exec_summary_no_mechanism_inventory",
        "x2_exec_summary_meta_filler_zero",
        "x2_executive_summary_synthesis_quality",
        "x2_exec_summary_mechanical_opener_stack_zero",
        "x2_exec_summary_robotic_transition_stack_zero",
        "x2_schema_valid",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_claim_ledger_orphan_zero",
    }
)

JUDGE_PACKET_ALLOWED_EXTRA_KEYS: frozenset[str] = frozenset({"x2_json_parse_valid", "product_shape_note"})

REPAIR_LOOP_PHASE_MARKERS: tuple[tuple[str, str], ...] = (
    ("synthesis_regen_pre_x2", 'write_json(artifact_dir / "synthesis_regen_receipt.json"'),
    ("run_x2", "for g in run_x2_gates("),
    ("post_x2_x1d_refresh", 'write_json(artifact_dir / "post_x2_x1d_refresh_receipt.json"'),
    ("judge_regen_cycle", "repair_judge_regen_after_x2_fail("),
)

JUDGE_REMEDIATION_SOFT_PRESERVATION_MARKERS: tuple[str, ...] = (
    "MATERIAL_PRESERVATION",
    "not a word-count floor",
    "Weave unused allowed facts",
    "claim_ledger",
    "Exactly 6 sentences",
)

# Backward-compatible alias for drift audits.
JUDGE_REMEDIATION_X2_FLOOR_MARKERS = JUDGE_REMEDIATION_SOFT_PRESERVATION_MARKERS


def _repo_read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_synthesis_check_names() -> frozenset[str]:
    src = _repo_read(Path(lane_mod.__file__))
    tree = ast.parse(src)
    check_names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_synthesis_shape_reject_reason":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    func = sub.func
                    if isinstance(func, ast.Name) and func.id.startswith("check_"):
                        check_names.add(func.id)
                    elif isinstance(func, ast.Attribute) and func.attr.startswith("check_"):
                        check_names.add(func.attr)
            break
    return frozenset(check_names)


def judge_packet_pre_x2_gate_keys() -> frozenset[str]:
    text = (
        "Engineering executive building governed agentic AI platforms for regulated enterprise delivery "
        "with traceable execution, commercial discipline, and accountable operating cadence across "
        "large programs. "
        "The platform generated proof-backed revenue and margin outcomes while scaling engineering "
        "delivery across enterprise programs and cross-functional product portfolios. "
        "Implementation of Basel III and CCAR data lineage frameworks reduced regulatory reporting errors "
        "and improved audit readiness for risk and finance stakeholders. "
        "Re-architected risk analytics with containerized microservices achieved faster calculations, "
        "real-time stress testing, and more reliable decision support for senior leadership. "
        "Quantitative actuarial depth informs governance and delivery trade-offs across complex programs. "
        "Governed runtime delivery stays audit-ready without weakening commercial velocity."
    )
    summary = build_deterministic_gate_summary(
        resume_display_text=text,
        parsed_output={"resume_display_text": text},
        claim_ledger=[
            {
                "claim_text": "Governed platform delivery.",
                "source_fact_ids": ["fact_engineering_platform_001"],
            }
        ],
        allowed_fact_ids={"fact_engineering_platform_001"},
    )
    return frozenset(k for k in summary if k not in JUDGE_PACKET_ALLOWED_EXTRA_KEYS)


def _audit_judge_packet(runtime_gates: frozenset[str]) -> list[X2X1dDriftViolation]:
    out: list[X2X1dDriftViolation] = []
    packet_keys = judge_packet_pre_x2_gate_keys()
    missing_required = sorted(JUDGE_PACKET_REQUIRED_GATE_KEYS - packet_keys)
    if missing_required:
        out.append(
            X2X1dDriftViolation(
                "executive_summary",
                "judge_packet_missing_gates",
                f"build_deterministic_gate_summary missing keys: {missing_required}",
                judge_packet_mod.__file__ or "",
            )
        )
    unknown_keys = sorted(packet_keys - runtime_gates - JUDGE_PACKET_ALLOWED_EXTRA_KEYS)
    if unknown_keys:
        out.append(
            X2X1dDriftViolation(
                "executive_summary",
                "judge_packet_unknown_gate",
                f"pre-X2 snapshot keys not in run_x2_gates: {unknown_keys}",
                judge_packet_mod.__file__ or "",
            )
        )
    retired_in_packet = sorted(RETIRED_EXEC_SUMMARY_X2_GATE_IDS & packet_keys)
    if retired_in_packet:
        out.append(
            X2X1dDriftViolation(
                "executive_summary",
                "judge_packet_retired_gate",
                f"retired gates in pre-X2 snapshot: {retired_in_packet}",
                judge_packet_mod.__file__ or "",
            )
        )
    return out


def _audit_synthesis_parity(runtime_gates: frozenset[str]) -> list[X2X1dDriftViolation]:
    out: list[X2X1dDriftViolation] = []
    check_names = _extract_synthesis_check_names()
    mapped_gates: set[str] = set(SYNTHESIS_IMPLICIT_X2_GATES)
    unmapped_checks: list[str] = []
    for check_name in check_names:
        gate_id = SYNTHESIS_CHECK_TO_X2_GATE.get(check_name)
        if gate_id:
            mapped_gates.add(gate_id)
        else:
            unmapped_checks.append(check_name)
    if unmapped_checks:
        out.append(
            X2X1dDriftViolation(
                "executive_summary",
                "synthesis_unmapped_check",
                f"add to SYNTHESIS_CHECK_TO_X2_GATE: {sorted(unmapped_checks)}",
                lane_mod.__file__ or "",
            )
        )
    missing_in_synthesis = sorted(
        (JUDGE_PACKET_REQUIRED_GATE_KEYS & runtime_gates)
        - mapped_gates
        - {"x2_schema_valid", "x2_claim_ledger_claim_text_non_empty", "x2_claim_ledger_orphan_zero"}
    )
    if missing_in_synthesis:
        out.append(
            X2X1dDriftViolation(
                "executive_summary",
                "synthesis_missing_critical_gate",
                f"pre-X2 shape should mirror X2 checks for: {missing_in_synthesis}",
                lane_mod.__file__ or "",
            )
        )
    for gate_id in mapped_gates:
        if gate_id not in runtime_gates and gate_id not in RETIRED_EXEC_SUMMARY_X2_GATE_IDS:
            out.append(
                X2X1dDriftViolation(
                    "executive_summary",
                    "synthesis_maps_unknown_gate",
                    f"{gate_id} not in run_x2_gates",
                    lane_mod.__file__ or "",
                )
            )
    return out


def _audit_judge_remediation_contract() -> list[X2X1dDriftViolation]:
    out: list[X2X1dDriftViolation] = []
    remediation_path = Path(lane_mod.__file__).parent / "executive_summary_judge_remediation.py"
    src = _repo_read(remediation_path)
    floor_sample = format_judge_regen_x2_floor(prior_word_count=100, prior_ledger_rows=6)
    for marker in JUDGE_REMEDIATION_SOFT_PRESERVATION_MARKERS:
        if marker not in floor_sample:
            out.append(
                X2X1dDriftViolation(
                    "executive_summary",
                    "soft_preservation_marker_missing",
                    f"format_judge_regen_soft_material_preservation missing {marker!r}",
                    str(remediation_path),
                )
            )
    if "words minimum" in floor_sample.lower() or "≥" in floor_sample and "words" in floor_sample:
        out.append(
            X2X1dDriftViolation(
                "executive_summary",
                "hard_word_count_floor_forbidden",
                "judge regen must not include hard prior word-count floor",
                str(remediation_path),
            )
        )
    if "format_judge_regen_x2_floor" not in src and "format_judge_regen_soft_material_preservation" not in src:
        out.append(
            X2X1dDriftViolation(
                "executive_summary",
                "judge_remediation_missing_soft_preservation",
                "build_judge_remediation_user_message must call soft material preservation helper",
                str(remediation_path),
            )
        )
    if "repair_judge_regen_after_x2_fail" not in src:
        out.append(
            X2X1dDriftViolation(
                "executive_summary",
                "judge_remediation_missing_x2_repair",
                "repair_judge_regen_after_x2_fail not defined",
                str(remediation_path),
            )
        )
    lane_src = _repo_read(Path(lane_mod.__file__))
    if "repair_judge_regen_after_x2_fail" not in lane_src:
        out.append(
            X2X1dDriftViolation(
                "executive_summary",
                "lane_missing_x2_repair",
                "lane must call repair_judge_regen_after_x2_fail before revert",
                lane_mod.__file__ or "",
            )
        )
    return out


def _audit_repair_loop_order() -> list[X2X1dDriftViolation]:
    out: list[X2X1dDriftViolation] = []
    lane_src = _repo_read(Path(lane_mod.__file__))
    positions: list[tuple[str, int]] = []
    for phase, marker in REPAIR_LOOP_PHASE_MARKERS:
        idx = lane_src.find(marker)
        if idx < 0:
            out.append(
                X2X1dDriftViolation(
                    "executive_summary",
                    "repair_loop_marker_missing",
                    f"lane missing execution marker for phase {phase}: {marker!r}",
                    lane_mod.__file__ or "",
                )
            )
            continue
        positions.append((phase, idx))
    for (prev_phase, prev_idx), (phase, idx) in zip(positions, positions[1:]):
        if idx < prev_idx:
            out.append(
                X2X1dDriftViolation(
                    "executive_summary",
                    "repair_loop_order_inverted",
                    f"{phase} (@{idx}) appears before {prev_phase} (@{prev_idx})",
                    lane_mod.__file__ or "",
                )
            )
    return out


def _audit_exec_judge_packet_rubrics() -> list[X2X1dDriftViolation]:
    out: list[X2X1dDriftViolation] = []
    shape = section_product_shape("executive_summary")
    for rubric_name, rubric in (
        ("SRFS_GRADE_ONLY_RUBRIC", judge_packet_mod.SRFS_GRADE_ONLY_RUBRIC),
        ("GRAPH_ONLY_GRADE_ONLY_RUBRIC", judge_packet_mod.GRAPH_ONLY_GRADE_ONLY_RUBRIC),
    ):
        issues = judge_rubric_shape_constraints(shape, rubric)
        if issues:
            out.append(
                X2X1dDriftViolation(
                    "executive_summary",
                    "judge_rubric_looser_than_ssot",
                    f"{rubric_name}: {issues}",
                    judge_packet_mod.__file__ or "",
                )
            )
        retired_hits = sorted(g for g in RETIRED_EXEC_SUMMARY_X2_GATE_IDS if g in rubric)
        if retired_hits:
            out.append(
                X2X1dDriftViolation(
                    "executive_summary",
                    "judge_rubric_retired_gate_id",
                    f"{rubric_name} mentions retired gates: {retired_hits}",
                    judge_packet_mod.__file__ or "",
                )
            )
    return out


def _audit_seam_parity() -> list[X2X1dDriftViolation]:
    return [
        X2X1dDriftViolation("executive_summary", "ssot_seam_parity", m.detail, m.seam)
        for m in audit_ssot_seam_parity()
    ]


def audit_executive_summary_extended_drift(
    runtime_gates: frozenset[str] | None = None,
) -> list[X2X1dDriftViolation]:
    """Executive-summary-only checks (synthesis, judge packet, repair loop)."""
    gates = runtime_gates or extract_runtime_x2_gate_ids(
        x2_module_ref="apps_rg/runtime/validators/executive_summary_x2.py",
        x2_run_function="run_x2_gates",
    )
    violations: list[X2X1dDriftViolation] = []
    violations.extend(_audit_judge_packet(gates))
    violations.extend(_audit_synthesis_parity(gates))
    violations.extend(_audit_judge_remediation_contract())
    violations.extend(_audit_repair_loop_order())
    violations.extend(_audit_exec_judge_packet_rubrics())
    violations.extend(_audit_seam_parity())
    violations.extend(audit_executive_summary_x1d_judge_coherence())
    return violations


def audit_executive_summary_x2_x1d_drift() -> list[X2X1dDriftViolation]:
    """Full executive_summary audit (generic lane checks + extensions)."""
    return audit_lane_x2_x1d_drift("executive_summary")


def assert_executive_summary_x2_x1d_contract() -> None:
    violations = audit_executive_summary_x2_x1d_drift()
    if violations:
        lines = "\n".join(f"  [{v.kind}] {v.detail} ({v.path})" for v in violations)
        raise AssertionError(f"executive_summary X2/X1D contract drift:\n{lines}")


__all__ = [
    "JUDGE_PACKET_REQUIRED_GATE_KEYS",
    "REPAIR_LOOP_PHASE_MARKERS",
    "SYNTHESIS_CHECK_TO_X2_GATE",
    "X2X1dDriftViolation",
    "assert_all_generated_lanes_x2_x1d_contract",
    "assert_executive_summary_x2_x1d_contract",
    "audit_all_generated_lanes_x2_x1d_drift",
    "audit_executive_summary_extended_drift",
    "audit_executive_summary_x2_x1d_drift",
    "audit_lane_x2_x1d_drift",
    "extract_runtime_x2_gate_ids",
    "judge_packet_pre_x2_gate_keys",
]
