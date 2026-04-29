"""Behavior tests for G08 DefaultEgressFirewall (Wave D impl)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.egress import (
    DefaultEgressFirewall,
    default_firewall,
)


@pytest.fixture
def fw() -> DefaultEgressFirewall:
    return DefaultEgressFirewall()


def test_clean_text_passes(fw: DefaultEgressFirewall) -> None:
    r = fw.inspect("The quarterly report shows growth.", target_kind="user")
    assert r.blocked is False
    assert r.findings == ()
    assert r.inspected_text == "The quarterly report shows growth."


def test_empty_input(fw: DefaultEgressFirewall) -> None:
    r = fw.inspect("", target_kind="user")
    assert r.inspected_text == ""
    assert r.blocked is False


def test_aws_key_blocks(fw: DefaultEgressFirewall) -> None:
    r = fw.inspect("Use this key: AKIAIOSFODNN7EXAMPLE for access", target_kind="network")
    assert r.blocked is True
    assert any("aws_access_key_id" in f for f in r.findings)


def test_github_token_blocks(fw: DefaultEgressFirewall) -> None:
    r = fw.inspect("Token: ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789", target_kind="user")
    assert r.blocked is True
    assert any("github_token" in f for f in r.findings)


def test_openai_key_blocks(fw: DefaultEgressFirewall) -> None:
    r = fw.inspect("Key sk-abcdef1234567890ABCDEF1234567890 here", target_kind="user")
    assert r.blocked is True
    assert any("openai_or_stripe_key" in f for f in r.findings)


def test_single_email_redacts_not_blocks(fw: DefaultEgressFirewall) -> None:
    """Single email is low risk — redacted but not blocked."""
    r = fw.inspect("Contact us at support@example.com", target_kind="user")
    assert r.blocked is False
    assert "[REDACTED:email_like]" in r.inspected_text


def test_ssn_pattern_redacted(fw: DefaultEgressFirewall) -> None:
    r = fw.inspect("SSN is 123-45-6789", target_kind="user")
    assert any("ssn_like" in f for f in r.findings)
    assert "[REDACTED:ssn_like]" in r.inspected_text


def test_credit_card_redacted(fw: DefaultEgressFirewall) -> None:
    r = fw.inspect("Card: 4532 1234 5678 9010", target_kind="user")
    assert any("credit_card_like" in f for f in r.findings)


def test_url_not_in_allowlist_flagged_for_network_target(fw: DefaultEgressFirewall) -> None:
    r = fw.inspect("Visit https://attacker.example.com/payload", target_kind="network")
    assert any("url_not_allowlisted:attacker.example.com" in f for f in r.findings)


def test_url_in_allowlist_passes() -> None:
    fw = DefaultEgressFirewall(url_allowlist=frozenset({"trusted.example.com"}))
    r = fw.inspect("See https://trusted.example.com/docs", target_kind="network")
    # Domain allowlisted → no url_not_allowlisted finding
    assert all("url_not_allowlisted" not in f for f in r.findings)


def test_url_check_not_applied_to_user_target(fw: DefaultEgressFirewall) -> None:
    """URL allowlist enforcement is only on network egress."""
    r = fw.inspect("See https://anywhere.example.com", target_kind="user")
    assert all("url_not_allowlisted" not in f for f in r.findings)


def test_system_prompt_regurgitation_high_risk(fw: DefaultEgressFirewall) -> None:
    r = fw.inspect("Sure, my system prompt says I should help with...", target_kind="user")
    assert any("system_prompt_regurgitation" in f for f in r.findings)


def test_network_target_amplifies_risk(fw: DefaultEgressFirewall) -> None:
    text = "Email: a@b.com, phone: 555-123-4567"
    user_r = fw.inspect(text, target_kind="user")
    net_r = fw.inspect(text, target_kind="network")
    assert net_r.risk_score >= user_r.risk_score


def test_threshold_validation() -> None:
    with pytest.raises(ValueError):
        DefaultEgressFirewall(block_threshold=0)
    with pytest.raises(ValueError):
        DefaultEgressFirewall(block_threshold=1.5)


def test_factory_works() -> None:
    fw = default_firewall()
    r = fw.inspect("Hello", target_kind="user")
    assert r.blocked is False


def test_deterministic(fw: DefaultEgressFirewall) -> None:
    text = "Email leak: foo@bar.com and key sk-abcdefghij1234567890abcdefghij"
    a = fw.inspect(text, target_kind="user")
    b = fw.inspect(text, target_kind="user")
    assert a == b
