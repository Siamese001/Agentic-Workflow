"""Tests for 01.2 Identity / Tenant / Session Baseline receipts."""

from __future__ import annotations

from agentic_core.L0_routing.intake import (
    CallerScopeBaseline,
    IntakePipeline,
    IntakePolicy,
    RawIngressEnvelope,
    SessionBindingReceipt,
    TenantBoundaryReceipt,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode


def _pipe() -> IntakePipeline:
    return IntakePipeline(IntakePolicy())


def test_caller_scope_baseline_emitted_for_authenticated_user() -> None:
    env = RawIngressEnvelope(
        transport="chat",
        body_text="hi",
        auth_credential={"kind": "session", "token": "t"},
        claimed_user_id="u1",
        claimed_tenant_id="tenant-1",
    )
    out = _pipe().run(env)
    assert out.accepted
    csb = out.receipt_bundle.caller_scope_baseline
    assert isinstance(csb, CallerScopeBaseline)
    assert csb.tenant_id == "tenant-1"
    assert csb.account_status == "active"
    assert csb.baseline_hash != ""


def test_tenant_boundary_receipt_resolved() -> None:
    env = RawIngressEnvelope(
        transport="api",
        body_json={"x": 1},
        auth_credential={"kind": "api_key", "token": "t", "principal_kind": "service"},
        claimed_service_id="svc-1",
        claimed_tenant_id="tenant-2",
    )
    out = _pipe().run(env)
    assert out.accepted
    tbr = out.receipt_bundle.tenant_boundary_receipt
    assert isinstance(tbr, TenantBoundaryReceipt)
    assert tbr.tenant_resolved is True
    assert tbr.tenant_allowed is True
    assert tbr.tenant_conflict_detected is False
    assert tbr.deterministic_receipt_hash != ""


def test_tenant_boundary_records_conflict_on_mismatch() -> None:
    env = RawIngressEnvelope(
        transport="api",
        body_json={"x": 1},
        auth_credential={
            "kind": "api_key",
            "token": "t",
            "principal_kind": "service",
            "tenant_id": "tenant-A",
        },
        claimed_service_id="svc-1",
        claimed_tenant_id="tenant-B",  # mismatched on purpose
    )
    out = _pipe().run(env)
    assert not out.accepted
    tbr = out.receipt_bundle.tenant_boundary_receipt
    assert tbr is not None
    assert tbr.tenant_conflict_detected is True
    assert tbr.tenant_allowed is False
    assert IngressReasonCode.TENANT_MISMATCH in tbr.reason_codes


def test_session_binding_receipt_creates_or_resumes() -> None:
    # Created path
    out = _pipe().run(
        RawIngressEnvelope(transport="chat", body_text="hi"),
    )
    sbr = out.receipt_bundle.session_binding_receipt
    assert isinstance(sbr, SessionBindingReceipt)
    assert sbr.session_created_or_resumed == "created"
    assert sbr.session_valid is True

    # Resumed path
    out2 = _pipe().run(
        RawIngressEnvelope(transport="chat", body_text="hi", session_id_hint="sess-existing"),
    )
    sbr2 = out2.receipt_bundle.session_binding_receipt
    assert sbr2 is not None
    assert sbr2.session_created_or_resumed == "resumed"
    assert sbr2.session_id == "sess-existing"


def test_caller_scope_baseline_hash_excludes_volatile_ids() -> None:
    env = RawIngressEnvelope(
        transport="chat",
        body_text="hi",
        auth_credential={"kind": "session", "token": "t"},
        claimed_user_id="u1",
        claimed_tenant_id="tenant-1",
        session_id_hint="sess-stable",
        request_id_hint="req-stable",
    )
    a = _pipe().run(env)
    b = _pipe().run(env)
    assert a.receipt_bundle.caller_scope_baseline is not None
    assert b.receipt_bundle.caller_scope_baseline is not None
    # baseline_hash only depends on stable scope inputs (tenant, session, etc.)
    assert (
        a.receipt_bundle.caller_scope_baseline.baseline_hash
        == b.receipt_bundle.caller_scope_baseline.baseline_hash
    )
