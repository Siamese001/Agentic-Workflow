"""Unit tests for agentic_core.L2_execution.observability.l2_spans.

Wave 6.1 (P2 untested-module coverage) — L2 OTEL span vocabulary SSOT.
``l2_spans`` (L2_execution/observability) is the single source of truth for
canonical L2 span names + the required-attribute schema. Pure / deterministic:
constant span-name tuples, the ``all_l2_span_names`` aggregator, and
``validate_span_attributes`` (always-required + conditional-attribute checks,
unknown-span rejection).
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.observability.l2_spans import (
    L2_E1_SPANS,
    L2_E2_SPANS,
    L2_E3_SPANS,
    L2_E4_SPANS,
    L2_E5_SPANS,
    L2_LOCAL_CRITIQUE_SPANS,
    L2_MUTATION_SPANS,
    L2_PTC_SPANS,
    L2_REQUIRED_SPAN_ATTRIBUTES,
    L2_RESOLUTION_SPANS,
    L2_SEQUENCER_SPANS,
    L2SpanAttributeViolation,
    all_l2_span_names,
    validate_span_attributes,
)

_ALWAYS = (
    "trace_id",
    "span_id",
    "parent_span_id",
    "request_id",
    "run_id",
    "route_id",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "capability_token_ref",
    "sandbox_envelope_ref",
    "side_effect_class",
    "latency_ms",
)


def _full_attrs(**overrides: object) -> dict[str, object]:
    attrs = {k: f"<{k}>" for k in _ALWAYS}
    attrs.update(overrides)
    return attrs


class TestSpanConstants:
    @pytest.mark.parametrize(
        "group",
        [
            L2_E1_SPANS,
            L2_E2_SPANS,
            L2_E3_SPANS,
            L2_E4_SPANS,
            L2_E5_SPANS,
            L2_PTC_SPANS,
            L2_RESOLUTION_SPANS,
            L2_SEQUENCER_SPANS,
            L2_MUTATION_SPANS,
            L2_LOCAL_CRITIQUE_SPANS,
        ],
    )
    def test_groups_are_nonempty_tuples_of_str(self, group: tuple[str, ...]) -> None:
        assert isinstance(group, tuple) and group
        assert all(isinstance(s, str) and s.startswith("l2.") for s in group)

    def test_required_attributes_is_always_required(self) -> None:
        assert L2_REQUIRED_SPAN_ATTRIBUTES == _ALWAYS


class TestAllSpanNames:
    def test_aggregates_every_group(self) -> None:
        names = all_l2_span_names()
        expected_len = sum(
            len(g)
            for g in (
                L2_E1_SPANS,
                L2_E2_SPANS,
                L2_E3_SPANS,
                L2_E4_SPANS,
                L2_RESOLUTION_SPANS,
                L2_E5_SPANS,
                L2_PTC_SPANS,
                L2_SEQUENCER_SPANS,
                L2_MUTATION_SPANS,
                L2_LOCAL_CRITIQUE_SPANS,
            )
        )
        assert len(names) == expected_len

    def test_names_are_unique(self) -> None:
        names = all_l2_span_names()
        assert len(set(names)) == len(names)

    def test_deterministic(self) -> None:
        assert all_l2_span_names() == all_l2_span_names()

    @pytest.mark.parametrize(
        "sample",
        ["l2.e1.prep.receive", "l2.e5.seal.terminal_stamp", "l2.heal.executed"],
    )
    def test_known_spans_present(self, sample: str) -> None:
        assert sample in all_l2_span_names()


class TestValidateSpanAttributes:
    def test_unknown_span_raises(self) -> None:
        with pytest.raises(L2SpanAttributeViolation, match="unknown L2 span name"):
            validate_span_attributes(span_name="l2.bogus.span", attrs={})

    def test_violation_is_value_error(self) -> None:
        assert issubclass(L2SpanAttributeViolation, ValueError)

    def test_full_attrs_no_missing(self) -> None:
        missing = validate_span_attributes(
            span_name="l2.e1.prep.receive", attrs=_full_attrs()
        )
        assert missing == ()

    def test_empty_attrs_reports_all_required(self) -> None:
        missing = validate_span_attributes(span_name="l2.e1.prep.receive", attrs={})
        assert set(missing) == set(_ALWAYS)

    @pytest.mark.parametrize("bad_value", [None, ""])
    def test_empty_or_none_value_counts_as_missing(self, bad_value: object) -> None:
        attrs = _full_attrs(trace_id=bad_value)
        missing = validate_span_attributes(span_name="l2.e1.prep.receive", attrs=attrs)
        assert "trace_id" in missing

    def test_conditional_workflow_required_when_flagged(self) -> None:
        missing = validate_span_attributes(
            span_name="l2.e3.exec.model_call",
            attrs=_full_attrs(),
            has_workflow=True,
        )
        assert set(missing) == {"workflow_id", "step_id"}

    def test_conditional_not_required_when_unflagged(self) -> None:
        missing = validate_span_attributes(
            span_name="l2.e3.exec.model_call",
            attrs=_full_attrs(),
            has_workflow=False,
        )
        assert missing == ()

    def test_conditional_satisfied_when_present(self) -> None:
        missing = validate_span_attributes(
            span_name="l2.e3.exec.model_call",
            attrs=_full_attrs(workflow_id="w1", step_id="s1"),
            has_workflow=True,
        )
        assert missing == ()

    def test_terminal_flag_requires_terminal_class_and_reason_codes(self) -> None:
        missing = validate_span_attributes(
            span_name="l2.e5.seal.terminal_stamp",
            attrs=_full_attrs(),
            has_terminal=True,
        )
        assert set(missing) == {"terminal_class", "reason_codes"}

    @pytest.mark.parametrize(
        "flag,expected",
        [
            ("has_attempt", {"attempt_id"}),
            ("has_invocation", {"invocation_kind"}),
            ("has_artifacts", {"artifact_refs"}),
        ],
    )
    def test_each_conditional_flag(self, flag: str, expected: set[str]) -> None:
        missing = validate_span_attributes(
            span_name="l2.e3.exec.attempt_open",
            attrs=_full_attrs(),
            **{flag: True},
        )
        assert set(missing) == expected
