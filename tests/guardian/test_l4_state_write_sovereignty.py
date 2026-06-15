"""Guardian workflow coverage for L4 write-sovereignty enforcement."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write


def test_l4_persistent_write_is_blocked_without_test_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", raising=False)

    with pytest.raises(PermissionError, match="MUTATION_PROHIBITED:layer=L4"):
        assert_no_persistent_write("L4", "write_text", path="agentic_core/L4_state/state.json")


def test_l4_persistent_write_guard_honors_test_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")

    assert_no_persistent_write("L4", "write_text", path="agentic_core/L4_state/state.json")
