"""
Smoke tests for the 4 net-new G-concern skeleton modules introduced
by ADR-070 (L5 Guardrail Family Catalog, 2026-04-29).

Tests verify:
  - Modules import cleanly.
  - Public API surface (dataclasses, enums, protocol stubs) is intact.
  - Default factory functions raise NotImplementedError with the canonical
    message pointing to ADR-070 + the W4-P8 plan.

These are skeleton-stage tests — they assert the contract surface, not
behavior. Behavior tests land when the implementations are written in
subsequent W4-P8 phases.
"""

from __future__ import annotations

import pytest


def test_g05_a2a_imports() -> None:
    from agentic_core.L5_safety.a2a import (
        A2AHandoffValidator,
        HandoffContext,
        HandoffVerdict,
        default_validator,
    )
    assert A2AHandoffValidator is not None
    ctx = HandoffContext(
        source_agent="a", target_agent="b", user_identity="u",
        capability_token="t", risk_tier="low", payload_summary="p",
    )
    assert ctx.source_agent == "a"
    verdict = HandoffVerdict(allowed=True, reason_code="ok", detail="d")
    assert verdict.allowed is True
    # default_validator now returns a real validator (not NotImplementedError)
    v = default_validator()
    assert v is not None


def test_g06_permissions_imports() -> None:
    from agentic_core.L5_safety.permissions import (
        PermissionGrant,
        PermissionLadder,
        PermissionRung,
        PermissionVerdict,
        default_ladder,
    )
    assert PermissionLadder is not None
    assert PermissionRung.READ < PermissionRung.SUGGEST < PermissionRung.MUTATE < PermissionRung.EXECUTE

    grant = PermissionGrant(
        agent_id="a", target_resource="r", rung=PermissionRung.READ,
        granted_by="p", expires_at_iso="2026-01-01T00:00:00Z",
    )
    assert grant.rung == PermissionRung.READ

    verdict = PermissionVerdict(
        allowed=True, held_rung=PermissionRung.READ,
        requested_rung=PermissionRung.READ, reason="ok",
    )
    assert verdict.allowed is True

    # default_ladder now returns a real ladder (not NotImplementedError)
    ladder = default_ladder()
    assert ladder is not None


def test_g13_sanitization_imports() -> None:
    from agentic_core.L5_safety.sanitization import (
        DataPerimeterSanitizer,
        SanitizationResult,
        default_sanitizer,
    )
    assert DataPerimeterSanitizer is not None
    result = SanitizationResult(sanitized_text="clean")
    assert result.sanitized_text == "clean"
    assert result.findings == ()
    assert result.quarantined is False

    with pytest.raises(NotImplementedError, match=r"ADR-070"):
        default_sanitizer()


def test_g15_rule_tagging_disposition_check() -> None:
    from agentic_core.L5_safety.rules import (
        RuleDisposition,
        TaggedRule,
        assert_disposition,
    )

    hard_rule = TaggedRule(
        rule_id="G08-egress-pii-block",
        disposition=RuleDisposition.HARD,
        family="G08",
        description="block egress containing PII",
        rationale="PII leak is unrecoverable; HARD-fail prevents downstream contamination",
    )
    assert hard_rule.disposition is RuleDisposition.HARD

    # Positive: matching expected disposition is silent
    assert_disposition(hard_rule, RuleDisposition.HARD)

    # Negative: mismatch raises with ADR-070 in the message
    with pytest.raises(AssertionError, match=r"ADR-070"):
        assert_disposition(hard_rule, RuleDisposition.REMEDIABLE)


def test_g15_disposition_enum_is_exhaustive() -> None:
    """The HARD/REMEDIABLE taxonomy is intentionally exhaustive — adding
    a third disposition requires Author-Gate review per ADR-070."""
    from agentic_core.L5_safety.rules import RuleDisposition

    members = set(RuleDisposition)
    assert members == {RuleDisposition.HARD, RuleDisposition.REMEDIABLE}, (
        "G15 disposition taxonomy must remain exhaustive — see ADR-070"
    )
