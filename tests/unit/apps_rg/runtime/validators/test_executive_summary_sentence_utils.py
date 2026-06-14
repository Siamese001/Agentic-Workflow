"""Wave 4.2 — unit tests for executive_summary_sentence_utils.

Covers robust sentence splitting with abbreviation guards, decimal protection,
and the round-trip join helper used by executive_summary X2 gates.
"""

from __future__ import annotations

import pytest

from apps_rg.runtime.validators.executive_summary_sentence_utils import (
    join_executive_summary_sentences,
    split_sentences,
)


class TestSplitSentencesBasics:
    @pytest.mark.parametrize("empty", ["", "   ", "\n\t", None])
    def test_empty_returns_empty_list(self, empty) -> None:
        assert split_sentences(empty) == []

    def test_single_sentence_no_terminal_punct(self) -> None:
        assert split_sentences("hello world") == ["hello world"]

    def test_two_sentences(self) -> None:
        assert split_sentences("First. Second.") == ["First.", "Second."]

    def test_question_and_exclamation_boundaries(self) -> None:
        assert split_sentences("What? Yes! Done.") == ["What?", "Yes!", "Done."]

    def test_whitespace_stripped_per_part(self) -> None:
        assert split_sentences("  A.   B.  ") == ["A.", "B."]

    def test_newline_boundary(self) -> None:
        assert split_sentences("A.\nB.") == ["A.", "B."]


class TestAbbreviationGuards:
    def test_us_abbreviation_not_split(self) -> None:
        out = split_sentences("Worked in the U.S. on policy.")
        assert out == ["Worked in the U.S. on policy."]

    def test_usa_abbreviation_not_split(self) -> None:
        out = split_sentences("Born in the U.S.A. and stayed.")
        assert out == ["Born in the U.S.A. and stayed."]

    def test_eg_abbreviation_not_split(self) -> None:
        out = split_sentences("Used tools, e.g. pytest, daily.")
        assert out == ["Used tools, e.g. pytest, daily."]

    def test_phd_and_dr_not_split(self) -> None:
        out = split_sentences("Dr. Smith holds a Ph.D. degree.")
        assert out == ["Dr. Smith holds a Ph.D. degree."]

    def test_abbreviation_then_real_boundary(self) -> None:
        out = split_sentences("Led in the U.S. market. Grew revenue.")
        assert out == ["Led in the U.S. market.", "Grew revenue."]


class TestDecimalProtection:
    def test_decimal_not_treated_as_boundary(self) -> None:
        out = split_sentences("Grew margin by 3.5 points.")
        assert out == ["Grew margin by 3.5 points."]

    def test_decimal_preserved_in_output(self) -> None:
        out = split_sentences("Revenue 12.75 million. Done.")
        assert out == ["Revenue 12.75 million.", "Done."]

    def test_multiple_decimals_restored(self) -> None:
        out = split_sentences("A 1.1 and 2.2 result.")
        assert out == ["A 1.1 and 2.2 result."]


class TestNoSentinelLeakage:
    def test_private_use_sentinels_absent(self) -> None:
        #  /  are internal guards — they must never leak to output.
        for sentence in split_sentences("Ph.D. in the U.S. with 3.5 GPA. Next."):
            assert "" not in sentence
            assert "" not in sentence


class TestJoin:
    def test_join_round_trip(self) -> None:
        text = "First. Second. Third."
        assert join_executive_summary_sentences(split_sentences(text)) == text

    def test_join_strips_and_filters_empty(self) -> None:
        assert join_executive_summary_sentences(["  A. ", "", "  ", "B."]) == "A. B."

    def test_join_empty_list(self) -> None:
        assert join_executive_summary_sentences([]) == ""
