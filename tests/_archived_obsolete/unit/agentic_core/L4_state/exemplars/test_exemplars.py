"""W4 tests for exemplar bank + retriever + coverage gate."""

from __future__ import annotations

import pytest

from agentic_core.L4_state.exemplars import (
    ExemplarBank,
    ExemplarRecord,
    select_top_k,
)
from agentic_core.prompt_governance.validation.check_exemplar_coverage import (
    MINIMUM_EXAMPLES,
    check_exemplar_coverage,
)


def _rec(
    eid: str,
    cls: str,
    inp: str = "input",
    out: str = "output",
    tags: tuple[str, ...] = (),
) -> ExemplarRecord:
    return ExemplarRecord(
        exemplar_id=eid,
        task_class=cls,
        input_text=inp,
        output_text=out,
        tags=tags,
    )


class TestExemplarRecordValidation:
    def test_valid_record(self) -> None:
        r = _rec("ex-1", "rfp_draft", "Draft X", "Result")
        assert r.exemplar_id == "ex-1"

    @pytest.mark.parametrize(
        "kw",
        [
            {"exemplar_id": ""},
            {"task_class": ""},
            {"input_text": ""},
            {"output_text": ""},
        ],
    )
    def test_empty_fields_rejected(self, kw: dict[str, str]) -> None:
        defaults = {
            "exemplar_id": "ex",
            "task_class": "c",
            "input_text": "i",
            "output_text": "o",
        }
        defaults.update(kw)
        with pytest.raises(ValueError):
            ExemplarRecord(**defaults)

    @pytest.mark.parametrize(
        "forbidden_key",
        ["route_mode", "safety_threshold", "execution_tier", "auth_token"],
    )
    def test_forbidden_metadata_rejected(self, forbidden_key: str) -> None:
        with pytest.raises(ValueError, match="cannot carry"):
            ExemplarRecord(
                exemplar_id="e",
                task_class="c",
                input_text="i",
                output_text="o",
                metadata={forbidden_key: "x"},
            )


class TestExemplarBank:
    def test_add_and_query(self) -> None:
        bank = ExemplarBank()
        bank.add(_rec("ex-1", "rfp_draft"))
        bank.add(_rec("ex-2", "rfp_draft"))
        bank.add(_rec("ex-3", "judge"))
        assert bank.count("rfp_draft") == 2
        assert bank.count("judge") == 1
        assert bank.count() == 3
        assert bank.task_classes() == ("rfp_draft", "judge")

    def test_dedupe_by_exemplar_id(self) -> None:
        bank = ExemplarBank()
        bank.add(_rec("ex-1", "c", inp="first"))
        bank.add(_rec("ex-1", "c", inp="second"))  # dedup
        assert bank.count("c") == 1
        # First insert wins.
        assert bank.by_class("c")[0].input_text == "first"

    def test_clear(self) -> None:
        bank = ExemplarBank()
        bank.add(_rec("ex", "c"))
        bank.clear()
        assert bank.count() == 0

    def test_unknown_class_returns_empty(self) -> None:
        bank = ExemplarBank()
        assert bank.by_class("nope") == ()


class TestRetriever:
    def _populate(self, bank: ExemplarBank) -> None:
        bank.add(
            _rec(
                "ex-a",
                "draft",
                inp="security posture for SOC2",
                tags=("security", "soc2", "compliance"),
            )
        )
        bank.add(
            _rec(
                "ex-b",
                "draft",
                inp="marketing landing page copy",
                tags=("marketing", "copy"),
            )
        )
        bank.add(
            _rec(
                "ex-c",
                "draft",
                inp="security audit remediation plan",
                tags=("security", "audit", "plan"),
            )
        )

    def test_selects_most_similar(self) -> None:
        bank = ExemplarBank()
        self._populate(bank)
        chosen = select_top_k(
            query="Write a security section for a SOC2 audit",
            task_class="draft",
            bank=bank,
            k=2,
        )
        ids = [r.exemplar_id for r in chosen]
        # ex-a tagged security+soc2 should rank first.
        assert "ex-a" in ids
        assert "ex-b" not in ids  # marketing should be excluded at k=2.

    def test_k_zero_returns_empty(self) -> None:
        bank = ExemplarBank()
        self._populate(bank)
        assert select_top_k(query="x", task_class="draft", bank=bank, k=0) == ()

    def test_unknown_class_returns_empty(self) -> None:
        bank = ExemplarBank()
        self._populate(bank)
        assert select_top_k(query="x", task_class="unknown", bank=bank, k=3) == ()

    def test_deterministic_tiebreak(self) -> None:
        """Equal scores \u2014 should sort by exemplar_id ascending."""
        bank = ExemplarBank()
        for i, eid in enumerate(["ex-z", "ex-a", "ex-m"]):
            # All records share tags/content, so scores are equal.
            bank.add(_rec(eid, "c", inp="same", tags=("t",)))
        chosen = select_top_k(query="q", task_class="c", bank=bank, k=3)
        assert [r.exemplar_id for r in chosen] == ["ex-a", "ex-m", "ex-z"]


class TestCoverageGate:
    def test_eligible_with_enough_examples_passes(self) -> None:
        ok, errs = check_exemplar_coverage(
            task_class="rfp", exemplars_provided=MINIMUM_EXAMPLES, eligibility=True
        )
        assert ok
        assert errs == []

    def test_eligible_with_too_few_fails(self) -> None:
        ok, errs = check_exemplar_coverage(task_class="rfp", exemplars_provided=2, eligibility=True)
        assert not ok
        assert any("minimum" in e for e in errs)

    def test_ineligible_noop(self) -> None:
        ok, errs = check_exemplar_coverage(task_class="rfp", exemplars_provided=0, eligibility=False)
        assert ok
        assert errs == []

    def test_empty_class_rejected(self) -> None:
        ok, errs = check_exemplar_coverage(task_class="", exemplars_provided=5, eligibility=True)
        assert not ok
        assert any("task_class" in e for e in errs)

    def test_negative_count_rejected(self) -> None:
        ok, errs = check_exemplar_coverage(task_class="c", exemplars_provided=-1, eligibility=False)
        assert not ok
        assert any(">= 0" in e for e in errs)

    def test_minimum_constant(self) -> None:
        assert MINIMUM_EXAMPLES == 3
