from infra.control_plane.models import SafetyContext, PolicyRule
from infra.control_plane.decisions import RulesEngineResult, RuleMatch
from infra.control_plane.judge_engine import evaluate_with_guard_model


def test_judge_engine_unsafe_on_high_severity():
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
