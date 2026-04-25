"""Unit tests for agentic_core.L5_safety.exit_control.hitl_classes.

Targets Wave-5 / Phase P15. Source: 54 lines, fan_in=26 (L5, impact 52.0).
Small module — exhaustive coverage.
"""

from __future__ import annotations

from enum import Enum

import pytest

from agentic_core.L5_safety.exit_control.hitl_classes import (
    ALL_CLASSES,
    CLASS_NAMES,
    HitlClass,
    HitlClassName,
    is_valid_class,
)


class TestHitlClassEnum:
    def test_is_enum_subclass(self) -> None:
        assert issubclass(HitlClass, Enum)

    def test_is_str_subclass(self) -> None:
        assert issubclass(HitlClass, str)

    def test_expected_members(self) -> None:
        assert {c.value for c in HitlClass} == {
            "financial",
            "safety",
            "regulated",
            "novel_context",
            "low_confidence",
            "policy_override",
        }

    def test_member_count(self) -> None:
        assert len(list(HitlClass)) == 6

    @pytest.mark.parametrize(
        "member,value",
        [
            (HitlClass.FINANCIAL, "financial"),
            (HitlClass.SAFETY, "safety"),
            (HitlClass.REGULATED, "regulated"),
            (HitlClass.NOVEL_CONTEXT, "novel_context"),
            (HitlClass.LOW_CONFIDENCE, "low_confidence"),
            (HitlClass.POLICY_OVERRIDE, "policy_override"),
        ],
    )
    def test_member_values(self, member: HitlClass, value: str) -> None:
        assert member.value == value
        assert member == value  # str equality

    def test_from_string_roundtrip(self) -> None:
        assert HitlClass("financial") == HitlClass.FINANCIAL
        assert HitlClass("safety") == HitlClass.SAFETY

    def test_invalid_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            HitlClass("nonexistent")


class TestAllClasses:
    def test_all_classes_tuple_type(self) -> None:
        assert isinstance(ALL_CLASSES, tuple)

    def test_all_classes_count(self) -> None:
        assert len(ALL_CLASSES) == 6

    def test_all_classes_matches_enum(self) -> None:
        assert set(ALL_CLASSES) == set(HitlClass)


class TestClassNames:
    def test_class_names_frozen_set(self) -> None:
        assert isinstance(CLASS_NAMES, frozenset)

    def test_class_names_content(self) -> None:
        assert CLASS_NAMES == {
            "financial",
            "safety",
            "regulated",
            "novel_context",
            "low_confidence",
            "policy_override",
        }


class TestIsValidClass:
    @pytest.mark.parametrize(
        "name",
        [
            "financial",
            "safety",
            "regulated",
            "novel_context",
            "low_confidence",
            "policy_override",
        ],
    )
    def test_recognized_names_accepted(self, name: str) -> None:
        assert is_valid_class(name) is True

    @pytest.mark.parametrize(
        "name",
        [
            "",
            "Financial",
            "FINANCIAL",
            "fraud",
            "foo",
            "safetty",
        ],
    )
    def test_unrecognized_names_rejected(self, name: str) -> None:
        assert is_valid_class(name) is False


class TestHitlClassNameAlias:
    def test_is_str_alias(self) -> None:
        # HitlClassName is declared as `str` (type alias)
        assert HitlClassName is str
