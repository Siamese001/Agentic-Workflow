"""Unit tests for L2 handoff contract."""

from __future__ import annotations

from agentic_core.prompt_governance.prompt_assembly.l2_handoff import (
    L2_MUST,
    L2_MUST_NOT,
    validate_l2_handoff,
)


def _ok_kwargs(**overrides):
    base = dict(
        artifact_signature_verified=True,
        artifact_bytes_match=True,
        replay_key_matches=True,
        provider_lane_used="anthropic",
        artifact_provider_lane="anthropic",
        model_id_used="claude-sonnet",
        artifact_model_id="claude-sonnet",
        tools_used=("search",),
        artifact_tools=("search", "lookup"),
        schema_used={"type": "object"},
        artifact_schema={"type": "object"},
        budget_ceiling=4096,
        tokens_emitted=1000,
        spans_emitted_with_trace_root=True,
        grounding_required=False,
        grounded_output=True,
    )
    base.update(overrides)
    return base


def test_must_lists_are_non_empty():
    assert len(L2_MUST) >= 8
    assert len(L2_MUST_NOT) >= 8


def test_handoff_passes_when_all_satisfied():
    res = validate_l2_handoff(**_ok_kwargs())
    assert res.valid is True
    assert res.violations == ()


def test_modified_artifact_flagged():
    res = validate_l2_handoff(**_ok_kwargs(artifact_bytes_match=False))
    assert res.valid is False
    assert "modify_any_slot_content" in res.violations


def test_signature_skip_flagged():
    res = validate_l2_handoff(**_ok_kwargs(artifact_signature_verified=False))
    assert res.valid is False
    assert "skip_signature_verification" in res.violations


def test_provider_swap_flagged():
    res = validate_l2_handoff(**_ok_kwargs(provider_lane_used="openai_chat"))
    assert res.valid is False
    assert "swap_provider_or_model" in res.violations


def test_model_swap_flagged():
    res = validate_l2_handoff(**_ok_kwargs(model_id_used="other-model"))
    assert res.valid is False
    assert "swap_provider_or_model" in res.violations


def test_unauthorized_tool_flagged():
    res = validate_l2_handoff(**_ok_kwargs(tools_used=("search", "rogue"), artifact_tools=("search",)))
    assert res.valid is False
    assert "add_or_remove_tools" in res.violations


def test_schema_drift_flagged():
    res = validate_l2_handoff(**_ok_kwargs(schema_used={"type": "object", "extra": "x"}))
    assert res.valid is False
    assert "add_or_remove_schema_fields" in res.violations


def test_token_overrun_flagged():
    res = validate_l2_handoff(**_ok_kwargs(budget_ceiling=1000, tokens_emitted=2000))
    assert res.valid is False


def test_grounding_required_no_grounded_output_flagged():
    res = validate_l2_handoff(**_ok_kwargs(grounding_required=True, grounded_output=False))
    assert res.valid is False
    assert "execute_non_grounded_outputs_as_facts_when_grounding_required" in res.violations
