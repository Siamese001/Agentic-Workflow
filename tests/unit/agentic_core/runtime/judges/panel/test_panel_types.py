"""Unit tests for agentic_core.runtime.judges.panel.panel_types.

Wave 6.1 (P2 untested-module coverage) — frozen dataclass types for the
multi-provider judge panel harness. No behaviour, only construction; tests
cover required-field construction, defaults, frozen immutability, and
__all__ export completeness.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.judges.panel import panel_types
from agentic_core.runtime.judges.panel.panel_types import (
    PanelJudgeOutcome,
    ReconciliationReceipt,
    TransportParityViolation,
    TransportReceipt,
)


class TestTransportReceipt:
    def test_construction_and_default_attempt(self) -> None:
        r = TransportReceipt(
            provider_key="prov-a",
            contract_hash="ch",
            max_output_tokens=512,
            temperature=0.0,
            json_output_lock="strict",
            finish_or_stop_reason="stop",
            parse_status="ok",
        )
        assert r.attempt == 1
        assert r.temperature == 0.0

    def test_temperature_nullable(self) -> None:
        r = TransportReceipt(
            provider_key="p",
            contract_hash="c",
            max_output_tokens=1,
            temperature=None,
            json_output_lock="x",
            finish_or_stop_reason=None,
            parse_status="ok",
        )
        assert r.temperature is None
        assert r.finish_or_stop_reason is None

    def test_frozen(self) -> None:
        r = TransportReceipt(
            provider_key="p",
            contract_hash="c",
            max_output_tokens=1,
            temperature=0.0,
            json_output_lock="x",
            finish_or_stop_reason="stop",
            parse_status="ok",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.attempt = 2  # type: ignore[misc]


class TestPanelJudgeOutcome:
    def test_defaults(self) -> None:
        o = PanelJudgeOutcome(
            provider_key="p",
            contract_hash="c",
            input_hash="i",
            evaluator_mode="llm",
            provider_status="ok",
            score=0.9,
            score_scale="0-1",
            threshold=0.5,
            pass_=True,
            decisive_failure=False,
        )
        assert o.findings == ()
        assert o.cited_sentence_indexes == ()
        assert o.remediation_suggestions == ()
        assert o.transport_receipt is None
        assert o.raw_body is None

    def test_nullable_score(self) -> None:
        o = PanelJudgeOutcome(
            provider_key="p",
            contract_hash="c",
            input_hash="i",
            evaluator_mode="llm",
            provider_status="error",
            score=None,
            score_scale="0-1",
            threshold=0.5,
            pass_=False,
            decisive_failure=True,
        )
        assert o.score is None
        assert o.decisive_failure is True

    def test_frozen(self) -> None:
        o = PanelJudgeOutcome(
            provider_key="p",
            contract_hash="c",
            input_hash="i",
            evaluator_mode="llm",
            provider_status="ok",
            score=0.9,
            score_scale="0-1",
            threshold=0.5,
            pass_=True,
            decisive_failure=False,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            o.pass_ = False  # type: ignore[misc]


class TestReconciliationReceipt:
    def test_construction(self) -> None:
        r = ReconciliationReceipt(
            policy_version="v1",
            original_score=0.4,
            original_pass=False,
            final_score=0.6,
            final_pass=True,
            suppressed_findings=("f1",),
            preserved_findings=("f2",),
        )
        assert r.final_pass is True
        assert r.suppressed_findings == ("f1",)


class TestTransportParityViolation:
    def test_default_provider_key(self) -> None:
        v = TransportParityViolation(code="E1", detail="mismatch")
        assert v.provider_key == ""

    def test_frozen(self) -> None:
        v = TransportParityViolation(code="E1", detail="d")
        with pytest.raises(dataclasses.FrozenInstanceError):
            v.code = "E2"  # type: ignore[misc]


def test_all_exports_present() -> None:
    for name in panel_types.__all__:
        assert hasattr(panel_types, name)
