"""X2 severity SSOT — soften_warn_only demotes only verified STYLE gates, never correctness.

Proves the slim-down END-TO-END at the deterministic layer (no live LLM run):
 - a demoted STYLE gate that FAILS is flipped to pass=True + WARN marker (telemetry);
 - a CORRECTNESS gate that FAILS is untouched (still blocks);
 - the exact X3 blocking computation (failed = [g for g in x2 if not g["pass"]]) excludes the
   demoted gate but keeps the correctness gate;
 - every id in STYLE_WARN_GATE_IDS is genuinely style (audit: none are correctness families).
"""
from __future__ import annotations

from apps_rg.runtime.validators.unify_bullets_x2 import X2GateResult
from apps_rg.runtime.validators.x2_severity import (
    STYLE_WARN_GATE_IDS,
    WARN_ONLY_MARKER,
    soften_warn_only,
    warn_only_fires,
)


def _fail(gate_id: str) -> X2GateResult:
    return X2GateResult(
        gate_id=gate_id,
        gate_type="deterministic",
        pass_=False,
        observed_value="bad",
        threshold="good",
        failure_reason=f"{gate_id} failed on weak payload",
        evidence_ref="test",
    )


def _ok(gate_id: str) -> X2GateResult:
    return X2GateResult(
        gate_id=gate_id,
        gate_type="deterministic",
        pass_=True,
        observed_value="good",
        threshold="good",
        failure_reason=None,
        evidence_ref="test",
    )


def test_demoted_style_gate_failure_is_softened_to_warn() -> None:
    out = soften_warn_only([_fail("x2_no_em_dash")])
    assert out[0].pass_ is True
    assert out[0].failure_reason.startswith(WARN_ONLY_MARKER)
    assert "x2_no_em_dash failed" in out[0].failure_reason  # original reason preserved (honest)


def test_correctness_gate_failure_is_never_softened() -> None:
    # A grounding/leakage gate must remain a hard FAIL even when it shares the lane.
    out = soften_warn_only([_fail("x2_unify_only_fact_scope")])
    assert out[0].pass_ is False
    assert not out[0].failure_reason.startswith(WARN_ONLY_MARKER)


def test_passing_demoted_gate_is_unchanged() -> None:
    out = soften_warn_only([_ok("x2_no_first_person")])
    assert out[0].pass_ is True
    assert out[0].failure_reason is None  # no marker when it did not fail


def test_x3_blocking_computation_excludes_demoted_keeps_correctness() -> None:
    raw = [
        _fail("x2_no_em_dash"),  # demoted STYLE
        _fail("x2_no_first_person"),  # demoted STYLE
        _fail("x2_unify_only_fact_scope"),  # CORRECTNESS — must still block
        _ok("x2_unify_bullet_count_6"),  # CORRECTNESS — passing
    ]
    dicts = [g.to_dict() for g in soften_warn_only(raw)]
    # This is exactly what aggregate_x3 computes (executive_summary_x3.py:132).
    failed = [g["gate_id"] for g in dicts if not g.get("pass")]
    assert "x2_unify_only_fact_scope" in failed  # correctness still blocks
    assert "x2_no_em_dash" not in failed  # style no longer blocks
    assert "x2_no_first_person" not in failed
    assert failed == ["x2_unify_only_fact_scope"]


def test_warn_only_fires_telemetry() -> None:
    raw = [_fail("x2_no_em_dash"), _ok("x2_no_first_person"), _fail("x2_unify_only_fact_scope")]
    fires = warn_only_fires(soften_warn_only(raw))
    assert fires == ["x2_no_em_dash"]  # only the demoted gate that actually fired


def test_dict_shaped_results_supported() -> None:
    raw = [{"gate_id": "x2_no_em_dash", "pass": False, "failure_reason": "had em-dash"}]
    out = soften_warn_only(raw)
    assert out[0]["pass"] is True
    assert out[0]["failure_reason"].startswith(WARN_ONLY_MARKER)


def test_no_correctness_family_ids_in_demote_set() -> None:
    # Guard: nothing in the set looks like a grounding/leakage/fabrication/metric/count gate.
    forbidden_substrings = (
        "fact_scope", "leakage", "claim_ledger", "source", "metric", "count",
        "real_llm", "provider", "graph_skill", "subset", "jd_only", "hydration",
        "bundle", "coverage", "parse", "required_top_level",
    )
    for gid in STYLE_WARN_GATE_IDS:
        low = gid.lower()
        assert not any(s in low for s in forbidden_substrings), f"correctness-looking id demoted: {gid}"
