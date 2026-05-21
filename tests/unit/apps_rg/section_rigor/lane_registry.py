"""SSOT: generated-lane rigor contracts (artifacts, critical X2 gates, weak-fail anchors)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES, REQUIRED_RELATIVE

ProviderMode = Literal["qwen_live"]

# Artifacts every mock/stub lane run must emit (rollup + section proof completeness).
COMMON_PROOF_ARTIFACTS: tuple[str, ...] = (
    *REQUIRED_RELATIVE,
    "parsed_output.json",
    "provider_request.json",
    "provider_response.json",
    "run_manifest.json",
    "c0_metrics.json",
)

C0_CRITICAL_GATES: frozenset[str] = frozenset(
    {
        "x2_c0_metrics_artifact_present",
        "x2_c0_support_status_gate",
    }
)

# Gates that must exist in x2_gate_outputs.json (regression anchors — not whack-a-mole one-offs).
UNIVERSAL_CRITICAL_GATES: frozenset[str] = frozenset(
    {
        "x2_json_parse_valid",
        "x2_x1d_required_judges_present",
        "x2_x1d_schema_valid",
    }
)

# Style gates shared by most lanes (executive_summary uses x2_first_person_zero instead).
STYLE_CRITICAL_GATES: frozenset[str] = frozenset(
    {
        "x2_no_first_person",
        "x2_no_em_dash",
    }
)

LANE_CRITICAL_GATES: dict[str, frozenset[str]] = {
    "headline": frozenset(
        {
            "x2_headline_exactly_one_line",
            "x2_headline_pipe_four_segments",
            "x2_headline_word_count_10_to_13",
            "x2_headline_claim_ledger_rows_present",
        }
    ),
    "executive_summary": frozenset(
        {
            "x2_exec_summary_sentence_count_2_3",
            "x2_claim_ledger_claim_text_non_empty",
            "x2_first_person_zero",
        }
    ),
    "unify_bullets": frozenset(
        {
            "x2_unify_bullet_count_6",
            "x2_claim_ledger_claim_text_non_empty",
            "x2_text_claim_coverage_integrity",
        }
    ),
    "unify_narrative": frozenset(
        {
            "x2_unify_narrative_exactly_one_sentence",
            "x2_claim_ledger_claim_text_non_empty",
        }
    ),
    "ibm_bullets": frozenset(
        {
            "x2_ibm_bullet_count_5",
            "x2_claim_ledger_claim_text_non_empty",
        }
    ),
    "ibm_narrative": frozenset(
        {
            "x2_ibm_narrative_exactly_one_sentence",
            "x2_claim_ledger_claim_text_non_empty",
        }
    ),
    "competencies": frozenset(
        {
            "x2_competencies_min_category_count",
            "x2_competencies_min_items_per_category",
            "x2_competencies_no_low_rigor_two_word_items",
            "x2_competencies_no_credential_relisting",
            "x2_competencies_role_alignment_terms",
            "x2_competencies_no_all_generic_skill_phrase",
            "x2_competencies_keyword_repetition_limit",
            "x2_claim_ledger_claim_text_non_empty",
            "x2_gate_rows_are_internally_consistent",
        }
    ),
}


@dataclass(frozen=True)
class LaneRigorSpec:
    lane: str
    provider_mode: ProviderMode
    extra_cli_args: tuple[str, ...] = ()
    extra_artifacts: tuple[str, ...] = ()
    critical_gates: frozenset[str] = frozenset()


def lane_specs() -> tuple[LaneRigorSpec, ...]:
    targeting_company = (
        "--target-company",
        "Brown & Brown",
        "--target-role",
        "SVP IT Strategy & Innovation",
    )
    jd_common = (
        "--jd",
        "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt",
    )
    brief_default = (
        "--manual-brief",
        "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.txt",
    )
    brief_exec = (
        "--manual-brief",
        "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.txt",
    )
    common_tail = ("--allow-non-allow-exit-zero",)
    specs: list[LaneRigorSpec] = []
    for lane in GENERATED_LANES:
        provider_mode: ProviderMode = "qwen_live"
        targeting = (*jd_common, *(brief_exec if lane == "executive_summary" else brief_default))
        style = STYLE_CRITICAL_GATES if lane != "executive_summary" else frozenset()
        extra = (*targeting_company, *targeting, "--provider", "qwen_vllm", *common_tail)
        specs.append(
            LaneRigorSpec(
                lane=lane,
                provider_mode=provider_mode,
                extra_cli_args=extra,
                critical_gates=UNIVERSAL_CRITICAL_GATES
                | C0_CRITICAL_GATES
                | style
                | LANE_CRITICAL_GATES[lane],
            )
        )
    return tuple(specs)


def spec_for_lane(lane: str) -> LaneRigorSpec:
    for spec in lane_specs():
        if spec.lane == lane:
            return spec
    raise KeyError(lane)


@dataclass(frozen=True)
class WeakFailCase:
    lane: str
    gate_id: str
    run_gates: Callable[[], list]


def weak_fail_cases() -> tuple[WeakFailCase, ...]:
    """Deliberately weak payloads must fail named gates (unit-level rigor, not CLI)."""
    from tests.unit.apps_rg.section_rigor import weak_payloads as wp

    return wp.all_weak_fail_cases()

