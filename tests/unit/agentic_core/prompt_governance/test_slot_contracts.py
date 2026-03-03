"""Negative-first tests for Phase 4 Wave 1 — typed slot contracts + airlock."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# SlotS0
# ---------------------------------------------------------------------------


def test_slot_s0_requires_content():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotS0

    with pytest.raises(TypeError):
        SlotS0()  # missing required field


def test_slot_s0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotS0

    s = SlotS0(content="system directive")
    with pytest.raises((AttributeError, TypeError)):
        s.content = "mutated"  # type: ignore[misc]


def test_slot_s0_wrong_type_still_constructs_but_is_typed():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotS0

    s = SlotS0(content="valid")
    assert isinstance(s, SlotS0)
    assert s.content == "valid"


# ---------------------------------------------------------------------------
# SlotD0
# ---------------------------------------------------------------------------


def test_slot_d0_requires_content_and_authority():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotD0

    with pytest.raises(TypeError):
        SlotD0()  # missing both fields

    with pytest.raises(TypeError):
        SlotD0(content="fence")  # missing authority


def test_slot_d0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotD0

    d = SlotD0(content="fence", authority="BINDING")
    with pytest.raises((AttributeError, TypeError)):
        d.authority = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SlotI0
# ---------------------------------------------------------------------------


def test_slot_i0_requires_content():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotI0

    with pytest.raises(TypeError):
        SlotI0()


def test_slot_i0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotI0

    i = SlotI0(content="capability manual")
    with pytest.raises((AttributeError, TypeError)):
        i.content = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SlotC0
# ---------------------------------------------------------------------------


def test_slot_c0_requires_content():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotC0

    with pytest.raises(TypeError):
        SlotC0()


def test_slot_c0_content_is_dict():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotC0

    c = SlotC0(content={"namespace": "ns1", "max_k": 5})
    assert isinstance(c.content, dict)


def test_slot_c0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotC0

    c = SlotC0(content={})
    with pytest.raises((AttributeError, TypeError)):
        c.content = {"mutated": True}  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SlotU0
# ---------------------------------------------------------------------------


def test_slot_u0_requires_content():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotU0

    with pytest.raises(TypeError):
        SlotU0()


def test_slot_u0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotU0

    u = SlotU0(content="user intent")
    with pytest.raises((AttributeError, TypeError)):
        u.content = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SLOT_ORDER
# ---------------------------------------------------------------------------


def test_slot_order_is_tuple():
    from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

    assert isinstance(SLOT_ORDER, tuple)


def test_slot_order_cannot_be_mutated():
    from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

    with pytest.raises((AttributeError, TypeError)):
        SLOT_ORDER[0] = "X"  # type: ignore[index]


def test_slot_order_contains_all_five_slots():
    from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

    assert set(SLOT_ORDER) == {"S0", "D0", "I0", "C0", "U0"}


def test_slot_order_sequence():
    from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

    assert SLOT_ORDER == ("S0", "D0", "I0", "C0", "U0")


# ---------------------------------------------------------------------------
# AirlockViolationError
# ---------------------------------------------------------------------------


def test_airlock_violation_error_is_exception():
    from agentic_core.prompt_governance.contracts.slot_contracts import AirlockViolationError

    assert issubclass(AirlockViolationError, Exception)


def test_airlock_violation_error_can_be_raised():
    from agentic_core.prompt_governance.contracts.slot_contracts import AirlockViolationError

    with pytest.raises(AirlockViolationError, match="AIRLOCK_VIOLATION"):
        raise AirlockViolationError("AIRLOCK_VIOLATION")


def test_airlock_violation_error_carries_message():
    from agentic_core.prompt_governance.contracts.slot_contracts import AirlockViolationError

    err = AirlockViolationError("bypass detected")
    assert "bypass detected" in str(err)


# ---------------------------------------------------------------------------
# contracts/__init__.py exports
# ---------------------------------------------------------------------------


def test_contracts_package_exports_all_slots():
    from agentic_core.prompt_governance import contracts

    for name in ("SlotS0", "SlotD0", "SlotI0", "SlotC0", "SlotU0", "SLOT_ORDER", "AirlockViolationError"):
        assert hasattr(contracts, name), f"contracts missing export: {name}"
