from __future__ import annotations

from typing import Any

from core.models.models import SafetyResult, SafetyFinding, CouncilVote, SafetyPolicy
from l5 import arbitrate_safety


def _make_safety_result(findings: list[SafetyFinding]) -> SafetyResult:
    return SafetyResult(findings=findings)


def test_arbitrate_safety_maps_verdicts_to_legacy_decisions() -> None:
    # block -> block
    block_result = _make_safety_result(
        [SafetyFinding(check_id="c1", category="policy", severity="high", message="bad")]
    )
    neutral_council = CouncilVote(members=0, selected_id="pass", scores={}, ties=[], reason="neutral")
    policy = SafetyPolicy()

    out_block = arbitrate_safety(block_result, neutral_council, policy, ctx=None)
    assert out_block["decision"] == "block"

    # warn -> replan (medium severity)
    warn_result = _make_safety_result(
        [SafetyFinding(check_id="c2", category="policy", severity="medium", message="meh")]
    )
    out_warn = arbitrate_safety(warn_result, neutral_council, policy, ctx=None)
    assert out_warn["decision"] == "replan"

    # pass -> allow
    pass_result = _make_safety_result([])
    out_pass = arbitrate_safety(pass_result, neutral_council, policy, ctx=None)
    assert out_pass["decision"] == "allow"


def test_arbitrate_safety_handles_missing_fields_safely() -> None:
    class FakeEvent:
        def __init__(self, verdict: Any = None, reason: Any = None) -> None:
            self.verdict = verdict
            self.reason = reason

    # Monkeypatch run_l5 to return a fake event with missing/None fields.
    from l5 import run_l5 as real_run_l5  # type: ignore[import]
    import l5 as l5_mod

    def fake_run_l5(*_args: Any, **_kwargs: Any) -> Any:
        return FakeEvent(verdict=None, reason=None)

    try:
        l5_mod.run_l5 = fake_run_l5  # type: ignore[assignment]
        result = arbitrate_safety(
            _make_safety_result([]),
            CouncilVote(members=0, selected_id="pass", scores={}, ties=[], reason="neutral"),
            SafetyPolicy(),
            ctx=None,
        )
        assert result["decision"] == "allow"
        assert isinstance(result["reason"], str)
    finally:
        l5_mod.run_l5 = real_run_l5  # type: ignore[assignment]






