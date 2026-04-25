"""Unit tests for PA observability events."""

from __future__ import annotations

from agentic_core.prompt_governance.prompt_assembly.observability_events import (
    PA_EVENT_TYPES,
    CompiledPromptArtifactSigned,
    EventBuffer,
    PromptAssemblyBlocked,
    PromptAssemblyDispatched,
    PromptAssemblyStarted,
    PromptBOMResolved,
    PromptBudgetCompleted,
    PromptRenderedForProvider,
    PromptSecurityPassCompleted,
    PromptSlotValidationCompleted,
)


def test_all_nine_event_types_registered():
    # Spec lists 8 events; we ship 9 (PromptSlotValidationCompleted is part of PA.4 too).
    expected = {
        "PromptAssemblyStarted",
        "PromptBOMResolved",
        "PromptSecurityPassCompleted",
        "PromptSlotValidationCompleted",
        "PromptBudgetCompleted",
        "PromptRenderedForProvider",
        "CompiledPromptArtifactSigned",
        "PromptAssemblyBlocked",
        "PromptAssemblyDispatched",
    }
    assert {t.__name__ for t in PA_EVENT_TYPES} == expected


def test_started_event_fields():
    e = PromptAssemblyStarted(
        request_id="r1",
        plan_id="p1",
        route_id="R3",
        policy_hash="ph-x",
        provider_lane="anthropic",
    )
    assert e.event_type == "PromptAssemblyStarted"
    assert e.request_id == "r1"
    # Frozen invariant
    try:
        e.request_id = "other"  # type: ignore[misc]
    except Exception:
        pass
    assert e.request_id == "r1"


def test_bom_resolved_with_missing_slots():
    e = PromptBOMResolved(
        bom_id="bom-1",
        slots_requested=("S0", "D0", "I0", "C0", "U0"),
        slots_available=("S0", "D0", "I0", "U0"),
        slots_missing=("C0",),
    )
    assert e.slots_missing == ("C0",)


def test_security_pass_event_records_counts():
    e = PromptSecurityPassCompleted(
        u0_disposition="neutralized",
        c0_classifier_disposition="STRIP",
        h0_disposition="absent",
        stripped_count=2,
        quarantined_count=1,
    )
    assert e.stripped_count == 2
    assert e.quarantined_count == 1


def test_validation_event():
    e = PromptSlotValidationCompleted(
        validation_status="pass",
        failed_checks=(),
        authority_violations=(),
        schema_status="bound",
        tool_status="bound",
        evidence_status="pass",
    )
    assert e.validation_status == "pass"


def test_budget_event():
    e = PromptBudgetCompleted(
        input_token_estimate=1000,
        output_token_reserve=2000,
        trim_actions=("step_3:remove_optional_exemplars",),
        overflow_status="TRIMMED",
    )
    assert e.overflow_status == "TRIMMED"


def test_rendered_event_flags():
    e = PromptRenderedForProvider(
        provider_adapter_id="anthropic-v1",
        model_id="claude-sonnet",
        schema_bound=True,
        tools_bound=False,
    )
    assert e.schema_bound is True
    assert e.tools_bound is False


def test_signed_event_artifact_hash():
    e = CompiledPromptArtifactSigned(
        artifact_id="art-1",
        manifest_hash="abcd",
        signature_status="ok",
        replay_key="replay-1",
    )
    assert e.signature_status == "ok"


def test_blocked_event_reason_code():
    e = PromptAssemblyBlocked(
        reason_code="policy_hash_mismatch",
        policy_hash="ph-x",
        plan_id="p1",
        route_id="R3",
        recommended_disposition="BLOCKED_POLICY",
    )
    assert e.reason_code == "policy_hash_mismatch"


def test_dispatched_event_target():
    e = PromptAssemblyDispatched(
        artifact_id="art-2",
        l2_target="sovereign_llm_gateway",
        trace_root="trace-1",
    )
    assert e.l2_target == "sovereign_llm_gateway"


def test_event_buffer_emit_and_types():
    buf = EventBuffer()
    buf.emit(PromptAssemblyStarted(plan_id="p1"))
    buf.emit(PromptAssemblyDispatched(artifact_id="a"))
    assert buf.types() == ("PromptAssemblyStarted", "PromptAssemblyDispatched")
    dicts = buf.to_dicts()
    assert dicts[0]["event_type"] == "PromptAssemblyStarted"
    assert dicts[0]["plan_id"] == "p1"
    assert dicts[1]["artifact_id"] == "a"
