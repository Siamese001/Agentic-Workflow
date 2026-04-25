"""Exemplar bank tests — registry, retrieval, formatting, similarity."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.reasoning.exemplar_bank import (
    Exemplar,
    ExemplarBank,
    format_for_e0,
    get_global_bank,
    static_similarity_score,
)


@pytest.fixture
def bank() -> ExemplarBank:
    return ExemplarBank()


@pytest.fixture
def sample_exemplars() -> list[Exemplar]:
    return [
        Exemplar(task="What is 2+2?", response="4", weight=0.5),
        Exemplar(task="Capital of France?", response="Paris", weight=0.9),
        Exemplar(task="Sort [3,1,2]", response="[1,2,3]", weight=0.7),
    ]


class TestExemplarBank:
    def test_register_and_retrieve(self, bank, sample_exemplars):
        bank.register("qa", "agent-1", sample_exemplars)
        result = bank.get("qa", "agent-1")
        assert len(result) == 3

    def test_retrieval_sorted_by_weight_desc(self, bank, sample_exemplars):
        bank.register("qa", "agent-1", sample_exemplars)
        result = bank.get("qa", "agent-1")
        weights = [e.weight for e in result]
        assert weights == sorted(weights, reverse=True)

    def test_max_count_truncates(self, bank, sample_exemplars):
        bank.register("qa", "agent-1", sample_exemplars)
        result = bank.get("qa", "agent-1", max_count=2)
        assert len(result) == 2

    def test_unknown_key_returns_empty_tuple(self, bank):
        assert bank.get("unknown", "agent-x") == ()

    def test_duplicate_registration_skipped(self, bank, sample_exemplars):
        bank.register("qa", "agent-1", sample_exemplars)
        bank.register("qa", "agent-1", sample_exemplars)
        result = bank.get("qa", "agent-1")
        assert len(result) == 3  # not 6

    def test_has_enough_threshold(self, bank, sample_exemplars):
        bank.register("qa", "agent-1", sample_exemplars)
        assert bank.has_enough("qa", "agent-1")
        assert bank.has_enough("qa", "agent-1", threshold=2)
        assert not bank.has_enough("qa", "agent-1", threshold=10)

    def test_has_enough_unknown_key_returns_false(self, bank):
        assert not bank.has_enough("unknown", "agent-x")

    def test_register_empty_intent_raises(self, bank):
        with pytest.raises(ValueError):
            bank.register("", "agent-1", [])

    def test_register_empty_agent_raises(self, bank):
        with pytest.raises(ValueError):
            bank.register("qa", "", [])

    def test_clear_resets_registry(self, bank, sample_exemplars):
        bank.register("qa", "agent-1", sample_exemplars)
        bank.clear()
        assert bank.get("qa", "agent-1") == ()

    def test_deterministic_retrieval(self, bank, sample_exemplars):
        bank.register("qa", "agent-1", sample_exemplars)
        a = bank.get("qa", "agent-1")
        b = bank.get("qa", "agent-1")
        assert a == b

    def test_tie_break_by_insertion_order(self, bank):
        ex_a = Exemplar(task="a", response="1", weight=0.5)
        ex_b = Exemplar(task="b", response="2", weight=0.5)
        bank.register("qa", "agent-1", [ex_a, ex_b])
        result = bank.get("qa", "agent-1")
        # Same weight → insertion order preserved
        assert result[0].task == "a"
        assert result[1].task == "b"


class TestFormatForE0:
    def test_empty_input_returns_empty_string(self):
        assert format_for_e0([]) == ""

    def test_renders_xml_examples_block(self):
        ex = [Exemplar(task="t", response="r")]
        result = format_for_e0(ex)
        assert "<examples>" in result
        assert "</examples>" in result
        assert "<example>" in result
        assert "<task>t</task>" in result
        assert "<response>r</response>" in result

    def test_xml_escapes_special_chars(self):
        ex = [Exemplar(task="<bad>", response="a&b")]
        result = format_for_e0(ex)
        assert "&lt;bad&gt;" in result
        assert "a&amp;b" in result

    def test_quote_escaped(self):
        ex = [Exemplar(task='say "hi"', response="ok")]
        result = format_for_e0(ex)
        assert "&quot;" in result

    def test_multiple_exemplars(self):
        ex = [
            Exemplar(task="q1", response="a1"),
            Exemplar(task="q2", response="a2"),
        ]
        result = format_for_e0(ex)
        assert result.count("<example>") == 2


class TestStaticSimilarity:
    def test_identical_strings_perfect_score(self):
        ex = Exemplar(task="hello world", response="r")
        assert static_similarity_score("hello world", ex) == 1.0

    def test_no_overlap_zero_score(self):
        ex = Exemplar(task="cats dogs", response="r")
        assert static_similarity_score("xyz qrs", ex) == 0.0

    def test_partial_overlap_jaccard(self):
        ex = Exemplar(task="hello world", response="r")
        # query "hello python" → intersect {hello}, union {hello, world, python}
        score = static_similarity_score("hello python", ex)
        assert 0.0 < score < 1.0
        assert abs(score - 1 / 3) < 1e-9

    def test_empty_query_zero(self):
        ex = Exemplar(task="hello", response="r")
        assert static_similarity_score("", ex) == 0.0

    def test_empty_exemplar_task_zero(self):
        ex = Exemplar(task="", response="r")
        assert static_similarity_score("hello", ex) == 0.0

    def test_case_insensitive(self):
        ex = Exemplar(task="HELLO", response="r")
        assert static_similarity_score("hello", ex) == 1.0


class TestGlobalBank:
    def test_global_bank_is_singleton(self):
        a = get_global_bank()
        b = get_global_bank()
        assert a is b

    def test_global_bank_is_exemplar_bank(self):
        assert isinstance(get_global_bank(), ExemplarBank)
