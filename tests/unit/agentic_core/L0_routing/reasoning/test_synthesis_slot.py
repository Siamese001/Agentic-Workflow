"""Y1 synthesis slot tests."""

from __future__ import annotations

from typing import Iterable

from agentic_core.L0_routing.reasoning.synthesis_slot import (
    SynthesisFragment,
    compose_from_fragments,
    compose_synthesis_slot,
)


class _StaticProvider:
    def __init__(self, fragments: list[SynthesisFragment]) -> None:
        self._fragments = fragments

    def collect(self) -> Iterable[SynthesisFragment]:
        return list(self._fragments)


class _RaisingProvider:
    def collect(self) -> Iterable[SynthesisFragment]:
        raise RuntimeError("boom")


class TestComposeSynthesisSlot:
    def test_empty_providers_returns_empty(self):
        assert compose_synthesis_slot([]) == ""

    def test_single_provider_single_fragment(self):
        prov = _StaticProvider([SynthesisFragment("pattern A")])
        result = compose_synthesis_slot([prov])
        assert result == "pattern A"

    def test_multiple_fragments_separated_by_blank_lines(self):
        prov = _StaticProvider([SynthesisFragment("a"), SynthesisFragment("b"), SynthesisFragment("c")])
        result = compose_synthesis_slot([prov])
        assert result == "a\n\nb\n\nc"

    def test_priority_orders_higher_first(self):
        prov = _StaticProvider(
            [
                SynthesisFragment("low", priority=0.1),
                SynthesisFragment("high", priority=0.9),
                SynthesisFragment("mid", priority=0.5),
            ]
        )
        result = compose_synthesis_slot([prov])
        assert result.split("\n\n") == ["high", "mid", "low"]

    def test_insertion_order_breaks_priority_ties(self):
        prov = _StaticProvider(
            [
                SynthesisFragment("first", priority=0.5),
                SynthesisFragment("second", priority=0.5),
            ]
        )
        result = compose_synthesis_slot([prov])
        assert result == "first\n\nsecond"

    def test_max_tokens_truncates_at_fragment_boundary(self):
        prov = _StaticProvider(
            [
                SynthesisFragment("aaaa", priority=1.0),  # 4 chars
                SynthesisFragment("bbbb", priority=0.5),  # would push over budget
            ]
        )
        # budget = 5 tokens × 4 chars/token = 20 chars; first fragment fits, second
        # fragment + sep would total 4+2+4 = 10, fits. Use tighter budget:
        # 1 token × 4 = 4 chars → only first fragment fits.
        result = compose_synthesis_slot([prov], max_tokens=1, chars_per_token=4)
        assert result == "aaaa"
        assert "bbbb" not in result

    def test_zero_max_tokens_returns_empty(self):
        prov = _StaticProvider([SynthesisFragment("x")])
        assert compose_synthesis_slot([prov], max_tokens=0) == ""

    def test_empty_fragment_text_skipped(self):
        prov = _StaticProvider([SynthesisFragment(""), SynthesisFragment("   "), SynthesisFragment("real")])
        result = compose_synthesis_slot([prov])
        assert result == "real"

    def test_raising_provider_does_not_crash(self):
        good = _StaticProvider([SynthesisFragment("ok")])
        bad = _RaisingProvider()
        result = compose_synthesis_slot([bad, good])
        assert result == "ok"

    def test_multiple_providers_aggregated(self):
        a = _StaticProvider([SynthesisFragment("from-a")])
        b = _StaticProvider([SynthesisFragment("from-b")])
        result = compose_synthesis_slot([a, b])
        assert "from-a" in result
        assert "from-b" in result

    def test_deterministic_output(self):
        prov = _StaticProvider([SynthesisFragment("x", priority=0.3), SynthesisFragment("y", priority=0.7)])
        a = compose_synthesis_slot([prov])
        b = compose_synthesis_slot([prov])
        assert a == b


class TestComposeFromFragments:
    def test_convenience_helper(self):
        fragments = [SynthesisFragment("a"), SynthesisFragment("b")]
        assert compose_from_fragments(fragments) == "a\n\nb"

    def test_empty_input(self):
        assert compose_from_fragments([]) == ""
