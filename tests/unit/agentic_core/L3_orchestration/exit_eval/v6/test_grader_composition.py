"""Tests for v6 grader composition primitives — Wave 3 of exit-eval-v6 deferred-scope.

Covers grader_composition_spec sections:
- §1 GraderClass taxonomy
- §2 RubricDimension + Rubric construction
- §3 Composition modes (BINARY/WEIGHTED/HYBRID)
- §4 Partial credit (dimension_vector preserved)
- §5.1 Abstain protocol (UNKNOWN routes via JUDGE_ABSTAINED reason code)
- §7 BUS-P row contract
- Per-gate composition mode table
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6 import (
    ABSTAIN_REASON_CODE,
    GATE_COMPOSITION_MODE,
    BusPRow,
    CompositionMode,
    CompositionResult,
    DimensionScore,
    GraderClass,
    Rubric,
    RubricDimension,
    compose,
)


# ============================================================
# §1 GraderClass taxonomy
# ============================================================


def test_grader_class_three_values() -> None:
    assert {g.value for g in GraderClass} == {"code_based", "model_based", "human"}


# ============================================================
# §2 RubricDimension construction
# ============================================================


def test_dimension_minimal_construction() -> None:
    d = RubricDimension(name="schema", grader_class=GraderClass.CODE_BASED)
    assert d.name == "schema"
    assert d.weight == 1.0
    assert d.threshold == 0.0
    assert d.is_hard_gate is False
    assert d.abstain_allowed is False


def test_dimension_abstain_only_for_model_based() -> None:
    """§5.1: abstain protocol is for model-based dimensions only."""
    with pytest.raises(ValueError, match="abstain_allowed only valid"):
        RubricDimension(
            name="schema", grader_class=GraderClass.CODE_BASED, abstain_allowed=True
        )


def test_dimension_model_based_can_abstain() -> None:
    d = RubricDimension(
        name="groundedness",
        grader_class=GraderClass.MODEL_BASED,
        abstain_allowed=True,
    )
    assert d.abstain_allowed is True


def test_dimension_rejects_invalid_scale() -> None:
    with pytest.raises(ValueError, match="scale_min"):
        RubricDimension(
            name="x",
            grader_class=GraderClass.CODE_BASED,
            scale_min=1.0,
            scale_max=1.0,
        )


# ============================================================
# §2 Rubric construction + invariants
# ============================================================


def _x1d_rubric() -> Rubric:
    """The §2 example X1D rubric — weighted composition."""
    return Rubric(
        rubric_id="X1D@v3",
        gate="X1D",
        version=3,
        composition=CompositionMode.WEIGHTED,
        aggregate_threshold=0.75,
        dimensions=[
            RubricDimension(
                name="groundedness",
                grader_class=GraderClass.MODEL_BASED,
                weight=0.4,
                threshold=0.80,
                abstain_allowed=True,
            ),
            RubricDimension(
                name="citation_support",
                grader_class=GraderClass.CODE_BASED,
                weight=0.3,
                threshold=1.0,
                is_hard_gate=False,  # in §2 example this IS hard, here pure weighted
            ),
            RubricDimension(
                name="faithfulness",
                grader_class=GraderClass.MODEL_BASED,
                weight=0.3,
                threshold=0.70,
                abstain_allowed=True,
            ),
        ],
    )


def test_rubric_construction() -> None:
    r = _x1d_rubric()
    assert r.gate == "X1D"
    assert r.composition is CompositionMode.WEIGHTED
    assert len(r.dimensions) == 3


def test_rubric_rejects_empty_dimensions() -> None:
    with pytest.raises(ValueError, match=">=1 dimension"):
        Rubric(
            rubric_id="x",
            gate="X1A",
            version=1,
            composition=CompositionMode.BINARY,
            dimensions=[],
        )


def test_rubric_hybrid_requires_hard_gate() -> None:
    """§3.3: HYBRID composition needs at least one is_hard_gate dimension."""
    with pytest.raises(ValueError, match="hybrid composition requires"):
        Rubric(
            rubric_id="X1B@v1",
            gate="X1B",
            version=1,
            composition=CompositionMode.HYBRID,
            aggregate_threshold=0.7,
            dimensions=[
                RubricDimension(
                    name="d1", grader_class=GraderClass.CODE_BASED, weight=1.0
                ),
            ],
        )


def test_rubric_weighted_aggregate_threshold_validated() -> None:
    with pytest.raises(ValueError, match="aggregate_threshold must be in"):
        Rubric(
            rubric_id="x",
            gate="X1D",
            version=1,
            composition=CompositionMode.WEIGHTED,
            aggregate_threshold=1.5,  # invalid
            dimensions=[
                RubricDimension(name="d1", grader_class=GraderClass.CODE_BASED)
            ],
        )


# ============================================================
# §3.1 BINARY composition
# ============================================================


def _x1a_binary_rubric() -> Rubric:
    return Rubric(
        rubric_id="X1A@v1",
        gate="X1A",
        version=1,
        composition=CompositionMode.BINARY,
        dimensions=[
            RubricDimension(
                name="policy_match",
                grader_class=GraderClass.CODE_BASED,
                threshold=1.0,
            ),
            RubricDimension(
                name="baselines_present",
                grader_class=GraderClass.CODE_BASED,
                threshold=1.0,
            ),
        ],
    )


def test_binary_all_pass_passes() -> None:
    r = _x1a_binary_rubric()
    scores = [
        DimensionScore("policy_match", GraderClass.CODE_BASED, 1.0, 1.0, 1.0, True),
        DimensionScore(
            "baselines_present", GraderClass.CODE_BASED, 1.0, 1.0, 1.0, True
        ),
    ]
    res = compose(r, scores)
    assert res.passed is True
    assert res.composition is CompositionMode.BINARY
    assert res.failed_dimension_names == []


def test_binary_one_fails_denies() -> None:
    r = _x1a_binary_rubric()
    scores = [
        DimensionScore("policy_match", GraderClass.CODE_BASED, 1.0, 1.0, 1.0, True),
        DimensionScore(
            "baselines_present", GraderClass.CODE_BASED, 0.0, 1.0, 1.0, False
        ),
    ]
    res = compose(r, scores)
    assert res.passed is False
    assert "baselines_present" in res.failed_dimension_names


# ============================================================
# §3.2 WEIGHTED composition
# ============================================================


def test_weighted_all_high_passes() -> None:
    r = _x1d_rubric()
    scores = [
        DimensionScore("groundedness", GraderClass.MODEL_BASED, 0.95, 0.4, 0.80, True),
        DimensionScore(
            "citation_support", GraderClass.CODE_BASED, 1.0, 0.3, 1.0, True
        ),
        DimensionScore(
            "faithfulness", GraderClass.MODEL_BASED, 0.85, 0.3, 0.70, True
        ),
    ]
    res = compose(r, scores)
    assert res.passed is True
    # Aggregate is weighted average: 0.4*0.95 + 0.3*1.0 + 0.3*0.85 = 0.935
    assert abs(res.aggregate_score - 0.935) < 0.001


def test_weighted_below_threshold_denies() -> None:
    r = _x1d_rubric()  # threshold 0.75
    scores = [
        DimensionScore("groundedness", GraderClass.MODEL_BASED, 0.4, 0.4, 0.80, False),
        DimensionScore(
            "citation_support", GraderClass.CODE_BASED, 0.5, 0.3, 1.0, False
        ),
        DimensionScore(
            "faithfulness", GraderClass.MODEL_BASED, 0.3, 0.3, 0.70, False
        ),
    ]
    res = compose(r, scores)
    assert res.passed is False
    # 0.4*0.4 + 0.3*0.5 + 0.3*0.3 = 0.40 < 0.75
    assert res.aggregate_score < r.aggregate_threshold


def test_weighted_at_exact_threshold_passes() -> None:
    """Boundary: aggregate == threshold should pass (>= comparison)."""
    r = Rubric(
        rubric_id="X1D@v_test",
        gate="X1D",
        version=99,
        composition=CompositionMode.WEIGHTED,
        aggregate_threshold=0.75,
        dimensions=[
            RubricDimension(name="a", grader_class=GraderClass.CODE_BASED, weight=1.0),
        ],
    )
    scores = [DimensionScore("a", GraderClass.CODE_BASED, 0.75, 1.0, 0.0, True)]
    res = compose(r, scores)
    assert res.passed is True
    assert abs(res.aggregate_score - 0.75) < 1e-9


# ============================================================
# §3.3 HYBRID composition
# ============================================================


def _x1b_hybrid_rubric() -> Rubric:
    return Rubric(
        rubric_id="X1B@v1",
        gate="X1B",
        version=1,
        composition=CompositionMode.HYBRID,
        aggregate_threshold=0.7,
        dimensions=[
            RubricDimension(
                name="schema_complete",
                grader_class=GraderClass.CODE_BASED,
                weight=0.0,  # hard gates don't contribute to soft sum
                threshold=1.0,
                is_hard_gate=True,
            ),
            RubricDimension(
                name="instruction_following",
                grader_class=GraderClass.MODEL_BASED,
                weight=1.0,
                threshold=0.7,
                abstain_allowed=True,
            ),
        ],
    )


def test_hybrid_hard_gate_failure_denies_even_if_soft_passes() -> None:
    """§3.3: hard_pass AND soft_pass — both must hold."""
    r = _x1b_hybrid_rubric()
    scores = [
        # schema_complete fails (hard gate)
        DimensionScore("schema_complete", GraderClass.CODE_BASED, 0.0, 0.0, 1.0, False),
        # instruction_following passes (soft)
        DimensionScore(
            "instruction_following", GraderClass.MODEL_BASED, 0.95, 1.0, 0.7, True
        ),
    ]
    res = compose(r, scores)
    assert res.passed is False
    assert "schema_complete" in res.failed_dimension_names


def test_hybrid_hard_passes_soft_fails_denies() -> None:
    r = _x1b_hybrid_rubric()
    scores = [
        DimensionScore("schema_complete", GraderClass.CODE_BASED, 1.0, 0.0, 1.0, True),
        DimensionScore(
            "instruction_following", GraderClass.MODEL_BASED, 0.3, 1.0, 0.7, False
        ),
    ]
    res = compose(r, scores)
    assert res.passed is False


def test_hybrid_both_pass_passes() -> None:
    r = _x1b_hybrid_rubric()
    scores = [
        DimensionScore("schema_complete", GraderClass.CODE_BASED, 1.0, 0.0, 1.0, True),
        DimensionScore(
            "instruction_following", GraderClass.MODEL_BASED, 0.85, 1.0, 0.7, True
        ),
    ]
    res = compose(r, scores)
    assert res.passed is True


# ============================================================
# §5.1 Abstain protocol
# ============================================================


def test_abstain_flips_result_abstain_flag() -> None:
    """§5.1: any dimension UNKNOWN -> result.abstain=True + JUDGE_ABSTAINED reason."""
    r = _x1d_rubric()
    scores = [
        DimensionScore(
            "groundedness", GraderClass.MODEL_BASED, 0.0, 0.4, 0.80, False, abstain=True
        ),
        DimensionScore(
            "citation_support", GraderClass.CODE_BASED, 1.0, 0.3, 1.0, True
        ),
        DimensionScore(
            "faithfulness", GraderClass.MODEL_BASED, 0.85, 0.3, 0.70, True
        ),
    ]
    res = compose(r, scores)
    assert res.abstain is True
    assert "groundedness" in res.abstained_dimension_names
    assert ABSTAIN_REASON_CODE in res.reason_codes
    assert ABSTAIN_REASON_CODE == "JUDGE_ABSTAINED"
    # Even though aggregate may pass numerically, abstain flag forces NOT passed
    assert res.passed is False


def test_abstain_does_not_pass_even_when_aggregate_above_threshold() -> None:
    """§5.1: abstain MUST route to X3B, not produce false-positive pass."""
    r = _x1d_rubric()
    scores = [
        # Numeric aggregate is high enough (0.4*0.95 + 0.3*1.0 + 0.3*0.85 = 0.935 > 0.75)
        DimensionScore(
            "groundedness", GraderClass.MODEL_BASED, 0.95, 0.4, 0.80, True, abstain=True
        ),
        DimensionScore(
            "citation_support", GraderClass.CODE_BASED, 1.0, 0.3, 1.0, True
        ),
        DimensionScore(
            "faithfulness", GraderClass.MODEL_BASED, 0.85, 0.3, 0.70, True
        ),
    ]
    res = compose(r, scores)
    assert res.aggregate_score > r.aggregate_threshold
    assert res.passed is False  # abstain wins


# ============================================================
# §3 table — per-gate composition mode
# ============================================================


@pytest.mark.parametrize(
    "gate,mode",
    [
        ("X1A", CompositionMode.BINARY),
        ("X1B", CompositionMode.HYBRID),
        ("X1C", CompositionMode.BINARY),
        ("X1D", CompositionMode.WEIGHTED),
        ("X1E", CompositionMode.HYBRID),
        ("X1F", CompositionMode.HYBRID),
        ("X1G", CompositionMode.BINARY),
    ],
)
def test_gate_composition_mode_table(gate: str, mode: CompositionMode) -> None:
    """grader_composition_spec §3 per-gate table."""
    assert GATE_COMPOSITION_MODE[gate] is mode


# ============================================================
# §4 Partial credit — dimension_vector preserved
# ============================================================


def test_dimension_vector_preserved_on_partial_credit() -> None:
    """§4: per-dimension scores remain on the result so HITL packets can show
    WHICH dimension produced the escalation."""
    r = _x1d_rubric()
    scores = [
        DimensionScore("groundedness", GraderClass.MODEL_BASED, 0.95, 0.4, 0.80, True),
        DimensionScore(
            "citation_support", GraderClass.CODE_BASED, 1.0, 0.3, 1.0, True
        ),
        DimensionScore(
            "faithfulness", GraderClass.MODEL_BASED, 0.62, 0.3, 0.70, False
        ),
    ]
    res = compose(r, scores)
    assert len(res.dimension_vector) == 3
    failed = [d for d in res.dimension_vector if not d.passed]
    assert len(failed) == 1
    assert failed[0].name == "faithfulness"


def test_compose_rejects_missing_dimension_score() -> None:
    r = _x1d_rubric()
    scores = [
        DimensionScore("groundedness", GraderClass.MODEL_BASED, 0.95, 0.4, 0.80, True),
        DimensionScore(
            "citation_support", GraderClass.CODE_BASED, 1.0, 0.3, 1.0, True
        ),
        # missing faithfulness
    ]
    with pytest.raises(ValueError, match="missing for dimensions"):
        compose(r, scores)


# ============================================================
# §7 BUS-P row contract
# ============================================================


def test_bus_p_row_emitted_from_composition_result() -> None:
    """§7: every gate emits one BUS-P row per run with this exact shape."""
    r = _x1d_rubric()
    scores = [
        DimensionScore("groundedness", GraderClass.MODEL_BASED, 0.91, 0.4, 0.80, True),
        DimensionScore(
            "citation_support", GraderClass.CODE_BASED, 1.0, 0.3, 1.0, True
        ),
        DimensionScore(
            "faithfulness", GraderClass.MODEL_BASED, 0.62, 0.3, 0.70, False
        ),
    ]
    res = compose(r, scores)
    row = BusPRow.from_composition(
        run_id="run-42",
        rubric=r,
        result=res,
        track="regression",
        trajectory_class="support_ticket_with_refund",
    )
    assert row.run_id == "run-42"
    assert row.gate == "X1D"
    assert row.rubric_version == "X1D@v3"
    assert row.composition == "weighted"
    assert row.track == "regression"
    assert row.trajectory_class == "support_ticket_with_refund"
    assert len(row.dimension_vector) == 3
    # Dimension vector is dict-shape per spec §7
    assert all(isinstance(d, dict) for d in row.dimension_vector)
    assert {"name", "score", "weight", "threshold", "passed", "grader_class", "abstain"} <= set(
        row.dimension_vector[0]
    )


def test_bus_p_row_reason_codes_carry_through() -> None:
    """§7: reason_codes from CompositionResult flow into BUS-P row."""
    r = _x1d_rubric()
    scores = [
        DimensionScore(
            "groundedness", GraderClass.MODEL_BASED, 0.0, 0.4, 0.80, False, abstain=True
        ),
        DimensionScore(
            "citation_support", GraderClass.CODE_BASED, 1.0, 0.3, 1.0, True
        ),
        DimensionScore(
            "faithfulness", GraderClass.MODEL_BASED, 0.85, 0.3, 0.70, True
        ),
    ]
    res = compose(r, scores)
    row = BusPRow.from_composition(run_id="r1", rubric=r, result=res)
    assert ABSTAIN_REASON_CODE in row.reason_codes
    assert row.abstain is True


# ============================================================
# Integration: package exports
# ============================================================


def test_v6_package_exports_grader_composition_symbols() -> None:
    from agentic_core.L3_orchestration.exit_eval import v6

    for name in [
        "ABSTAIN_REASON_CODE",
        "GATE_COMPOSITION_MODE",
        "BusPRow",
        "CompositionMode",
        "CompositionResult",
        "DimensionScore",
        "GraderClass",
        "Rubric",
        "RubricDimension",
        "compose",
    ]:
        assert hasattr(v6, name), f"v6.{name} missing"
        assert name in v6.__all__, f"{name} not in v6.__all__"
