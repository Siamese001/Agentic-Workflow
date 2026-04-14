"""Foundational behavioral tests for agentic_core/action_request_types.py."""

from __future__ import annotations

from dataclasses import is_dataclass

import pytest

from agentic_core.action_request_types import ActionRequest, validate_action_request


class TestActionRequestContract:
    def test_is_dataclass(self):
        assert is_dataclass(ActionRequest)

    def test_field_names_present(self):
        field_names = {field.name for field in ActionRequest.__dataclass_fields__.values()}
        assert field_names == {"action", "target", "metadata"}

    def test_is_not_none(self):
        request = ActionRequest(action="retrieve", target="codebase")
        assert request is not None

    def test_validate_round_trip(self):
        request = ActionRequest(action="retrieve", target="docs")
        assert validate_action_request(request) is request

    def test_empty_action_raises(self):
        with pytest.raises(ValueError):
            ActionRequest(action="", target="docs").validate()
