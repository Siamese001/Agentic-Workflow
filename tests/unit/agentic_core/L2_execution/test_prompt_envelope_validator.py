"""Tests for PromptEnvelope posture validator (C0 J5 enforcement)."""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L2_execution.prompt_envelope_validator import (
    CITATION_MODE_MANUAL,
    CITATION_MODE_NATIVE,
    PostureValidationResult,
    PromptEnvelopePostureError,
    TOOL_USE_CLOSED,
    TOOL_USE_OPEN,
    assert_prompt_envelope_posture,
    validate_prompt_envelope_posture,
)
from agentic_core.knowledge.retrieval.prompt_envelope import (
    PromptAssemblyStatus,
    PromptEnvelope,
)
from apps_shared.enforcement.prompt_envelope_gate import (
    enforce_prompt_envelope_posture,
)


def _make_envelope(metadata: dict[str, Any] | None = None) -> PromptEnvelope:
    """Construct a minimal PromptEnvelope with the given metadata dict."""
    return PromptEnvelope(
        envelope_id="env-1",
        trace_id="trace-1",
        query_id="query-1",
        verified_chunks=(),
        cited_spans=(),
        coverage_score=1.0,
        gaps=(),
        contradiction_status="none",
        abstain_recommended=False,
        next_action_hint="proceed",
        task_spec="",
        system_blocks=(),
        replay_key="rk",
        policy_hash="ph",
        plan_id="plan",
        assembly_status=PromptAssemblyStatus(),
        metadata=metadata if metadata is not None else {},
    )


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("citation_mode", "tool_use"),
    [
        (CITATION_MODE_NATIVE, TOOL_USE_OPEN),
        (CITATION_MODE_NATIVE, TOOL_USE_CLOSED),
        (CITATION_MODE_MANUAL, TOOL_USE_OPEN),
        (CITATION_MODE_MANUAL, TOOL_USE_CLOSED),
    ],
)
def test_valid_posture_all_combinations(citation_mode: str, tool_use: str) -> None:
    envelope = _make_envelope({"citation_mode": citation_mode, "tool_use": tool_use})
    result = validate_prompt_envelope_posture(envelope)
    assert result.is_valid is True
    assert result.citation_mode == citation_mode
    assert result.tool_use == tool_use
    assert result.violations == ()


def test_assert_returns_result_on_valid_posture() -> None:
    envelope = _make_envelope({"citation_mode": "native", "tool_use": "closed"})
    result = assert_prompt_envelope_posture(envelope)
    assert isinstance(result, PostureValidationResult)
    assert result.is_valid


def test_gate_returns_result_on_valid_posture() -> None:
    envelope = _make_envelope({"citation_mode": "manual", "tool_use": "open"})
    result = enforce_prompt_envelope_posture(envelope)
    assert result.is_valid
    assert result.citation_mode == "manual"
    assert result.tool_use == "open"


def test_extra_metadata_keys_are_ignored() -> None:
    envelope = _make_envelope(
        {
            "citation_mode": "native",
            "tool_use": "open",
            "support_score": 0.9,
            "citation_count": 3,
        }
    )
    result = validate_prompt_envelope_posture(envelope)
    assert result.is_valid


# ---------------------------------------------------------------------------
# Soft violations (validator returns is_valid=False, does not raise)
# ---------------------------------------------------------------------------


def test_missing_citation_mode() -> None:
    envelope = _make_envelope({"tool_use": "open"})
    result = validate_prompt_envelope_posture(envelope)
    assert not result.is_valid
    assert result.citation_mode is None
    assert any("citation_mode" in v for v in result.violations)


def test_missing_tool_use() -> None:
    envelope = _make_envelope({"citation_mode": "native"})
    result = validate_prompt_envelope_posture(envelope)
    assert not result.is_valid
    assert result.tool_use is None
    assert any("tool_use" in v for v in result.violations)


def test_missing_both_fields_reports_both_violations() -> None:
    envelope = _make_envelope({})
    result = validate_prompt_envelope_posture(envelope)
    assert not result.is_valid
    assert len(result.violations) == 2


def test_invalid_citation_mode_value() -> None:
    envelope = _make_envelope({"citation_mode": "webhook", "tool_use": "open"})
    result = validate_prompt_envelope_posture(envelope)
    assert not result.is_valid
    assert result.citation_mode == "webhook"
    assert any("webhook" in v for v in result.violations)


def test_invalid_tool_use_value() -> None:
    envelope = _make_envelope({"citation_mode": "native", "tool_use": "partial"})
    result = validate_prompt_envelope_posture(envelope)
    assert not result.is_valid
    assert result.tool_use == "partial"
    assert any("partial" in v for v in result.violations)


def test_non_string_citation_mode() -> None:
    envelope = _make_envelope({"citation_mode": 42, "tool_use": "open"})
    result = validate_prompt_envelope_posture(envelope)
    assert not result.is_valid
    assert result.citation_mode is None
    assert any("must be str" in v for v in result.violations)


def test_non_string_tool_use() -> None:
    envelope = _make_envelope({"citation_mode": "native", "tool_use": True})
    result = validate_prompt_envelope_posture(envelope)
    assert not result.is_valid
    assert result.tool_use is None
    assert any("must be str" in v for v in result.violations)


# ---------------------------------------------------------------------------
# Hard errors (validator raises)
# ---------------------------------------------------------------------------


def test_wrong_type_raises() -> None:
    with pytest.raises(PromptEnvelopePostureError, match="expected PromptEnvelope"):
        validate_prompt_envelope_posture({"citation_mode": "native", "tool_use": "open"})


def test_none_envelope_raises() -> None:
    with pytest.raises(PromptEnvelopePostureError):
        validate_prompt_envelope_posture(None)


# ---------------------------------------------------------------------------
# assert_* and gate behavior on invalid posture
# ---------------------------------------------------------------------------


def test_assert_raises_on_missing_posture() -> None:
    envelope = _make_envelope({})
    with pytest.raises(PromptEnvelopePostureError, match="citation_mode"):
        assert_prompt_envelope_posture(envelope)


def test_assert_raises_on_invalid_value() -> None:
    envelope = _make_envelope({"citation_mode": "native", "tool_use": "half-open"})
    with pytest.raises(PromptEnvelopePostureError, match="tool_use"):
        assert_prompt_envelope_posture(envelope)


def test_gate_is_fail_closed_on_invalid() -> None:
    envelope = _make_envelope({"citation_mode": "unknown", "tool_use": "open"})
    with pytest.raises(PromptEnvelopePostureError):
        enforce_prompt_envelope_posture(envelope)


def test_gate_rejects_non_envelope_input() -> None:
    with pytest.raises(PromptEnvelopePostureError):
        enforce_prompt_envelope_posture("not-an-envelope")
