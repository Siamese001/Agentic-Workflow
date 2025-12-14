import logging



logger = logging.getLogger(__name__)
def test_judge_engine_unsafe_on_high_severity() -> None:
    """Test that judge engine marks content unsafe when high severity violations detected."""
    ctx = SafetyContext(input_text="harmful text")
    rules_result = RulesEngineResult(
        matches=[
            RuleMatch(
                rule_id="r1",
                category="violence",
                severity="high",
            )
        ],
        max_severity="high",
        has_pii=False,
    )

    verdict = evaluate_with_guard_model(ctx, rules_result)

    assert verdict.verdict == "unsafe"
