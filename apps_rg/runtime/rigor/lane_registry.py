"""SSOT: generated-lane rigor contracts (artifacts, critical X2 gates, weak-fail anchors)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES, REQUIRED_RELATIVE
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape

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

def _lane_critical_gates_from_product_shape() -> dict[str, frozenset[str]]:
    """Regression anchors stay aligned with section_product_shape SSOT (W5A rigor tests)."""
    return {
        lane: frozenset(section_product_shape(lane).required_gate_ids) for lane in GENERATED_LANES
    }


LANE_CRITICAL_GATES: dict[str, frozenset[str]] = _lane_critical_gates_from_product_shape()


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
        "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md",
    )
    common_tail = ("--allow-non-allow-exit-zero",)
    specs: list[LaneRigorSpec] = []
    for lane in GENERATED_LANES:
        provider_mode: ProviderMode = "qwen_live"
        targeting = (*jd_common, *brief_default)
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
                | LANE_CRITICAL_GATES[lane]
                | frozenset(section_product_shape(lane).required_gate_ids),
            )
        )
    return tuple(specs)


def spec_for_lane(lane: str) -> LaneRigorSpec:
    for spec in lane_specs():
        if spec.lane == lane:
            return spec
    raise KeyError(lane)


