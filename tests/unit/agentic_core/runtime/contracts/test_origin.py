"""Unit tests for agentic_core.runtime.contracts.origin.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 runtime-contract surface.
``origin`` (fan_in=16, L_RUNTIME) is the trust-boundary classification threaded
through every emit contract (airlock doctrine, ADR-023 §6). Pure enum + frozen
dataclass — exhaustive coverage.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.origin import Origin, OriginTaggedContent


class TestOriginEnum:
    def test_is_str_enum(self) -> None:
        assert isinstance(Origin.USER_INTENT, str)
        assert Origin.USER_INTENT == "USER_INTENT"

    def test_all_members_value_equals_name(self) -> None:
        for member in Origin:
            assert member.value == member.name

    def test_exact_member_set(self) -> None:
        assert {m.name for m in Origin} == {
            "USER_INTENT",
            "RETRIEVED_DATA",
            "TOOL_OUTPUT",
            "MODEL_GENERATION",
            "HUMAN_REVIEW_DATA",
            "SYSTEM_INTERNAL",
        }

    def test_serialises_as_plain_string(self) -> None:
        # str-valued enum → clean JSON/YAML round-trip
        assert f"{Origin.TOOL_OUTPUT}" == "Origin.TOOL_OUTPUT"
        assert Origin("RETRIEVED_DATA") is Origin.RETRIEVED_DATA


class TestOriginTaggedContent:
    def test_required_fields(self) -> None:
        c = OriginTaggedContent(content="hello", origin=Origin.USER_INTENT)
        assert c.content == "hello"
        assert c.origin == Origin.USER_INTENT

    def test_source_ref_defaults_empty(self) -> None:
        assert OriginTaggedContent(content="x", origin=Origin.SYSTEM_INTERNAL).source_ref == ""

    def test_is_user_controlled(self) -> None:
        assert OriginTaggedContent("u", Origin.USER_INTENT).is_user_controlled() is True
        assert OriginTaggedContent("s", Origin.SYSTEM_INTERNAL).is_user_controlled() is False

    def test_is_externally_retrieved(self) -> None:
        assert OriginTaggedContent("r", Origin.RETRIEVED_DATA).is_externally_retrieved() is True
        assert OriginTaggedContent("u", Origin.USER_INTENT).is_externally_retrieved() is False

    @pytest.mark.parametrize(
        "origin,expected",
        [
            (Origin.USER_INTENT, True),
            (Origin.MODEL_GENERATION, True),
            (Origin.RETRIEVED_DATA, False),
            (Origin.TOOL_OUTPUT, False),
            (Origin.HUMAN_REVIEW_DATA, False),
            (Origin.SYSTEM_INTERNAL, False),
        ],
    )
    def test_requires_hitl_clearance(self, origin: Origin, expected: bool) -> None:
        assert OriginTaggedContent("c", origin).requires_hitl_clearance() is expected

    def test_frozen(self) -> None:
        c = OriginTaggedContent("x", Origin.USER_INTENT)
        with pytest.raises(dataclasses.FrozenInstanceError):
            c.content = "y"  # type: ignore[misc]

    def test_slots_no_dict(self) -> None:
        assert not hasattr(OriginTaggedContent("x", Origin.USER_INTENT), "__dict__")
