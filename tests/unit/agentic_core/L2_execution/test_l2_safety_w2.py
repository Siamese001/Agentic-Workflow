"""W2 unit tests for the L2 best-practices gap plan (b7c4e2).

Covers:
- Egress proxy allowlist / denylist / scheme gate / fail-closed default
- egress_scope context manager nesting
- CredentialMint issue / verify / expiry / revocation / rotation / audience
- StepIdentity derivation + escalation guards
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L2_execution.capability.scoped_credential_mint import (
    CredentialExpired,
    CredentialMint,
    CredentialRevoked,
    InvalidCredential,
)
from agentic_core.L2_execution.capability.step_scoped_identity import (
    AudienceEscalation,
    CapabilityEscalation,
    IdentityDerivation,
    derive_step_identity,
    subset_from,
)
from agentic_core.L2_execution.enforcement.egress_proxy import (
    EgressDenied,
    build_policy,
    check_url,
    current_policy,
    egress_scope,
    install_egress_policy,
    uninstall_egress_policy,
)


# ---------------------------------------------------------------------------
# Egress proxy
# ---------------------------------------------------------------------------


class TestEgressProxy:
    def setup_method(self) -> None:
        uninstall_egress_policy()

    def teardown_method(self) -> None:
        uninstall_egress_policy()

    def test_fail_closed_when_no_policy(self) -> None:
        assert current_policy() is None
        with pytest.raises(EgressDenied) as exc:
            check_url("https://api.example.com/x")
        assert "fail-closed default" in exc.value.reason

    def test_allowlist_match(self) -> None:
        install_egress_policy(
            build_policy(name="p1", allowed_hosts={"api.example.com"})
        )
        d = check_url("https://api.example.com/x")
        assert d.allowed is True
        assert d.matched_pattern == "api.example.com"

    def test_glob_allowlist(self) -> None:
        install_egress_policy(
            build_policy(name="p1", allowed_hosts={"*.example.com"})
        )
        assert check_url("https://a.example.com/").allowed is True
        with pytest.raises(EgressDenied):
            check_url("https://example.com/")  # glob *.example.com does not match bare

    def test_denylist_overrides_allowlist(self) -> None:
        install_egress_policy(
            build_policy(
                name="p1",
                allowed_hosts={"*.example.com"},
                denied_hosts={"secrets.example.com"},
            )
        )
        with pytest.raises(EgressDenied) as exc:
            check_url("https://secrets.example.com/")
        assert "denylist" in exc.value.reason

    def test_scheme_gate(self) -> None:
        install_egress_policy(
            build_policy(name="p1", allowed_hosts={"api.example.com"})
        )
        with pytest.raises(EgressDenied):
            check_url("http://api.example.com/")  # http not in default https-only
        install_egress_policy(
            build_policy(
                name="p1",
                allowed_hosts={"api.example.com"},
                allowed_schemes=("https", "http"),
            )
        )
        assert check_url("http://api.example.com/").allowed is True

    def test_raise_on_deny_false_returns_decision(self) -> None:
        install_egress_policy(build_policy(name="p1", allowed_hosts=set()))
        d = check_url("https://nope.example.com/", raise_on_deny=False)
        assert d.allowed is False

    def test_egress_scope_restores_prior(self) -> None:
        outer = build_policy(name="outer", allowed_hosts={"outer.com"})
        inner = build_policy(name="inner", allowed_hosts={"inner.com"})
        install_egress_policy(outer)
        with egress_scope(inner):
            assert current_policy() is inner
            assert check_url("https://inner.com/").allowed is True
            with pytest.raises(EgressDenied):
                check_url("https://outer.com/")
        assert current_policy() is outer
        assert check_url("https://outer.com/").allowed is True

    def test_egress_scope_restores_fail_closed(self) -> None:
        inner = build_policy(name="inner", allowed_hosts={"inner.com"})
        with egress_scope(inner):
            assert current_policy() is inner
        assert current_policy() is None
        with pytest.raises(EgressDenied):
            check_url("https://inner.com/")

    def test_invalid_url(self) -> None:
        install_egress_policy(build_policy(name="p", allowed_hosts={"*"}))
        with pytest.raises(EgressDenied) as exc:
            check_url("not-a-url")
        assert "invalid url" in exc.value.reason


# ---------------------------------------------------------------------------
# Credential mint
# ---------------------------------------------------------------------------


class TestCredentialMint:
    def test_issue_and_verify(self) -> None:
        mint = CredentialMint()
        cred = mint.issue(step_id="step-1", audience="svc.A")
        mint.verify(cred, expected_audience="svc.A")
        # Token is flat and contains the scope tuple
        assert cred.step_id in cred.token
        assert cred.audience in cred.token
        assert cred.to_header_value().startswith("Bearer ")

    def test_signature_mismatch_raises(self) -> None:
        mint1 = CredentialMint()
        mint2 = CredentialMint()
        cred = mint1.issue(step_id="s", audience="a")
        with pytest.raises(InvalidCredential):
            mint2.verify(cred)

    def test_audience_mismatch_raises(self) -> None:
        mint = CredentialMint()
        cred = mint.issue(step_id="s", audience="svc.A")
        with pytest.raises(InvalidCredential):
            mint.verify(cred, expected_audience="svc.B")

    def test_expiry(self) -> None:
        mint = CredentialMint(default_ttl_s=0.01)
        cred = mint.issue(step_id="s", audience="a")
        time.sleep(0.05)
        with pytest.raises(CredentialExpired):
            mint.verify(cred)

    def test_revocation(self) -> None:
        mint = CredentialMint()
        cred = mint.issue(step_id="s", audience="a")
        mint.revoke(cred)
        with pytest.raises(CredentialRevoked):
            mint.verify(cred)

    def test_rotation_invalidates_outstanding(self) -> None:
        mint = CredentialMint()
        cred = mint.issue(step_id="s", audience="a")
        mint.rotate_secret()
        with pytest.raises(InvalidCredential):
            mint.verify(cred)

    def test_to_dict_omits_signature(self) -> None:
        mint = CredentialMint()
        cred = mint.issue(step_id="s", audience="a")
        d = cred.to_dict()
        assert "signature" not in d
        assert d["audience"] == "a"

    def test_invalid_inputs(self) -> None:
        mint = CredentialMint()
        with pytest.raises(ValueError):
            mint.issue(step_id="", audience="a")
        with pytest.raises(ValueError):
            mint.issue(step_id="s", audience="a", ttl_s=0)
        with pytest.raises(ValueError):
            CredentialMint(secret=b"too-short")


# ---------------------------------------------------------------------------
# Step-scoped identity
# ---------------------------------------------------------------------------


class TestStepScopedIdentity:
    def test_derives_narrow_subset(self) -> None:
        d = IdentityDerivation(
            step_id="t-1",
            parent_agent_id="agent-A",
            parent_capabilities=frozenset({"cap.read", "cap.write", "cap.admin"}),
            parent_audiences=frozenset({"aud.a", "aud.b", "aud.c"}),
            requested_capabilities=frozenset({"cap.read"}),
            requested_audiences=frozenset({"aud.a"}),
        )
        ident = derive_step_identity(d)
        assert ident.has_capability("cap.read") is True
        assert ident.has_capability("cap.admin") is False
        assert ident.can_reach("aud.a") is True
        assert ident.can_reach("aud.b") is False
        assert len(ident.narrow_hash) == 24

    def test_capability_escalation_blocked(self) -> None:
        d = IdentityDerivation(
            step_id="t-1",
            parent_agent_id="agent-A",
            parent_capabilities=frozenset({"cap.read"}),
            parent_audiences=frozenset({"aud.a"}),
            requested_capabilities=frozenset({"cap.admin"}),  # not in parent
            requested_audiences=frozenset({"aud.a"}),
        )
        with pytest.raises(CapabilityEscalation):
            derive_step_identity(d)

    def test_audience_escalation_blocked(self) -> None:
        d = IdentityDerivation(
            step_id="t-1",
            parent_agent_id="agent-A",
            parent_capabilities=frozenset({"cap.read"}),
            parent_audiences=frozenset({"aud.a"}),
            requested_capabilities=frozenset({"cap.read"}),
            requested_audiences=frozenset({"aud.nope"}),
        )
        with pytest.raises(AudienceEscalation):
            derive_step_identity(d)

    def test_subset_from_helper(self) -> None:
        assert subset_from({"a", "b", "c"}, {"a"}) == frozenset({"a"})
        with pytest.raises(CapabilityEscalation):
            subset_from({"a"}, {"a", "b"})

    def test_to_dict_roundtrip(self) -> None:
        d = IdentityDerivation(
            step_id="t-1",
            parent_agent_id="agent-A",
            parent_capabilities=frozenset({"cap.read"}),
            parent_audiences=frozenset({"aud.a"}),
            requested_capabilities=frozenset({"cap.read"}),
            requested_audiences=frozenset({"aud.a"}),
            metadata={"note": "test"},
        )
        ident = derive_step_identity(d)
        snap = ident.to_dict()
        assert snap["parent_agent_id"] == "agent-A"
        assert snap["allowed_capabilities"] == ["cap.read"]
        assert snap["metadata"]["note"] == "test"
