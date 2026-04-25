"""E2 CHECKING LIBRARY CARDS — identity + tenant baseline.

Spec section: lines 207-260.
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L0_routing.intake.envelope import RawIngressEnvelope
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.stages import (
    IdentityResolution,
    default_identity_resolver,
    run_e2_identity,
)
from agentic_core.L0_routing.intake.verdicts import (
    AuthVerdict,
    PrincipalType,
    SourceClass,
)


# ----------------------------------------------------------------------
# Anonymous user paths
# ----------------------------------------------------------------------


def test_anonymous_user_chat_gets_anonymous_limited() -> None:
    env = RawIngressEnvelope(transport="chat", body_text="hi")
    res = run_e2_identity(env, SourceClass.USER)
    assert res.passed
    assert res.fields["auth_verdict"] is AuthVerdict.ANONYMOUS_LIMITED
    assert res.fields["principal_type"] is PrincipalType.ANONYMOUS
    assert res.fields["caller_scope_baseline"] == "anonymous:limited"


def test_service_call_without_credential_rejects() -> None:
    env = RawIngressEnvelope(transport="api", body_text="x")
    res = run_e2_identity(env, SourceClass.SERVICE)
    assert not res.passed
    assert IngressReasonCode.AUTH_REQUIRED in res.reason_codes


@pytest.mark.parametrize(
    "source_class",
    [SourceClass.SERVICE, SourceClass.BATCH, SourceClass.WEBHOOK, SourceClass.ALERT],
)
def test_machine_paths_require_credential(source_class: SourceClass) -> None:
    env = RawIngressEnvelope(transport="api", body_text="x")
    res = run_e2_identity(env, source_class)
    assert not res.passed
    assert IngressReasonCode.AUTH_REQUIRED in res.reason_codes


# ----------------------------------------------------------------------
# Authenticated user paths
# ----------------------------------------------------------------------


def test_user_with_credential_is_authenticated() -> None:
    env = RawIngressEnvelope(
        transport="chat",
        body_text="hi",
        auth_credential={"kind": "session", "token": "abc"},
        claimed_user_id="u-1",
    )
    res = run_e2_identity(env, SourceClass.USER)
    assert res.passed
    assert res.fields["auth_verdict"] is AuthVerdict.AUTHENTICATED
    assert res.fields["principal_type"] is PrincipalType.USER
    assert res.fields["principal_id"] == "u-1"


def test_service_with_credential_is_service_bound() -> None:
    env = RawIngressEnvelope(
        transport="api",
        body_text="x",
        auth_credential={"kind": "api_key", "token": "k", "principal_kind": "service"},
        claimed_service_id="svc-1",
    )
    res = run_e2_identity(env, SourceClass.SERVICE)
    assert res.passed
    assert res.fields["auth_verdict"] is AuthVerdict.SERVICE_BOUND
    assert res.fields["principal_type"] is PrincipalType.SERVICE


# ----------------------------------------------------------------------
# Failure modes
# ----------------------------------------------------------------------


def test_expired_credential_rejects() -> None:
    env = RawIngressEnvelope(
        transport="api",
        body_text="x",
        auth_credential={"kind": "oauth", "token": "t", "expires_at_unix": time.time() - 60},
    )
    res = run_e2_identity(env, SourceClass.SERVICE)
    assert not res.passed
    assert IngressReasonCode.AUTH_EXPIRED in res.reason_codes


def test_blocked_principal_rejects() -> None:
    env = RawIngressEnvelope(
        transport="chat",
        body_text="x",
        auth_credential={"kind": "session", "token": "t", "blocked": True},
    )
    res = run_e2_identity(env, SourceClass.USER)
    assert not res.passed
    assert IngressReasonCode.PRINCIPAL_BLOCKED in res.reason_codes


def test_tenant_mismatch_rejects() -> None:
    env = RawIngressEnvelope(
        transport="api",
        body_text="x",
        claimed_tenant_id="tenant-A",
        auth_credential={"kind": "api_key", "token": "k", "tenant_id": "tenant-B"},
    )
    res = run_e2_identity(env, SourceClass.SERVICE)
    assert not res.passed
    assert IngressReasonCode.TENANT_MISMATCH in res.reason_codes


# ----------------------------------------------------------------------
# Identity resolver injection
# ----------------------------------------------------------------------


def test_custom_identity_resolver_is_used() -> None:
    def reject_all(_env, _sc):
        return IdentityResolution(
            auth_verdict=AuthVerdict.REJECTED,
            principal_type=PrincipalType.UNKNOWN,
            principal_id=None,
            tenant_bind=None,
            workspace_bind=None,
            region_scope_baseline=None,
            baseline_entitlements=(),
            reason_code=IngressReasonCode.AUTH_REQUIRED,
        )

    env = RawIngressEnvelope(transport="chat", body_text="hi")
    res = run_e2_identity(env, SourceClass.USER, resolver=reject_all)
    assert not res.passed
    assert IngressReasonCode.AUTH_REQUIRED in res.reason_codes


def test_default_resolver_is_pure_function() -> None:
    """Resolver MUST NOT mutate envelope (frozen) or hit external services."""
    env = RawIngressEnvelope(transport="chat", body_text="hi")
    r1 = default_identity_resolver(env, SourceClass.USER)
    r2 = default_identity_resolver(env, SourceClass.USER)
    assert r1 == r2  # deterministic given same envelope
