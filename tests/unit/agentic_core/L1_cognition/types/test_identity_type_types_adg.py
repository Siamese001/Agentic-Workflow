"""Behavioral tests for identity_type_types_adg."""

from __future__ import annotations

from agentic_core.identity_type_types_adg import IdentityType


def test_identity_type_enum_contains_expected_members():
    assert {member.value for member in IdentityType} == {"system", "user", "tool"}
