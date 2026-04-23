"""W3 tests for E0 (exemplars), M0 (meta-cognitive), H0 (healing) slots."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.reasoning.authority_validator import AuthorityValidator
from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
)
from agentic_core.L2_execution.reasoning.slot_assembly_engine import SlotAssemblyEngine


class TestAuthorityLevelExtensions:
    @pytest.mark.parametrize(
        "code,expected",
        [
            ("E0", AuthorityLevel.EXEMPLAR),
            ("M0", AuthorityLevel.META_COGNITIVE),
            ("H0", AuthorityLevel.HEALING),
            ("e0", AuthorityLevel.EXEMPLAR),  # case-insensitive
            ("m0", AuthorityLevel.META_COGNITIVE),
            ("h0", AuthorityLevel.HEALING),
        ],
    )
    def test_from_slot_code_maps_new_slots(
        self, code: str, expected: AuthorityLevel
    ) -> None:
        assert AuthorityLevel.from_slot_code(code) is expected

    def test_preexisting_slots_unchanged(self) -> None:
        # Regression: existing mappings must not drift.
        assert AuthorityLevel.from_slot_code("S0") is AuthorityLevel.ABSOLUTE
        assert AuthorityLevel.from_slot_code("I0") is AuthorityLevel.GOVERNED
        assert AuthorityLevel.from_slot_code("D0") is AuthorityLevel.BINDING
        assert AuthorityLevel.from_slot_code("C0") is AuthorityLevel.INFO
        assert AuthorityLevel.from_slot_code("U0") is AuthorityLevel.ZERO


class TestAuthoritySlotInstantiation:
    @pytest.mark.parametrize(
        "slot_code,level",
        [
            ("E0", AuthorityLevel.EXEMPLAR),
            ("M0", AuthorityLevel.META_COGNITIVE),
            ("H0", AuthorityLevel.HEALING),
        ],
    )
    def test_new_slots_can_be_constructed(
        self, slot_code: str, level: AuthorityLevel
    ) -> None:
        slot = AuthoritySlot(
            slot_type=slot_code,
            content="payload",
            authority_level=level,
            source_layer="L4",
        )
        assert slot.slot_type == slot_code

    @pytest.mark.parametrize("slot_code", ["E0", "M0", "H0"])
    def test_new_slots_reject_forbidden_metadata(self, slot_code: str) -> None:
        """E0/M0/H0 are informational — must not carry routing/safety fields."""
        with pytest.raises(ValueError, match="cannot carry"):
            AuthoritySlot(
                slot_type=slot_code,
                content="x",
                authority_level=AuthorityLevel.from_slot_code(slot_code),
                source_layer="L4",
                metadata={"route_mode": "direct"},
            )

    def test_new_slots_accept_benign_metadata(self) -> None:
        slot = AuthoritySlot(
            slot_type="E0",
            content="example 1...",
            authority_level=AuthorityLevel.EXEMPLAR,
            source_layer="L4",
            metadata={"exemplar_id": "ex-001", "similarity": 0.92},
        )
        assert slot.metadata["similarity"] == 0.92


class TestSlotOrderExtensions:
    def test_slot_order_contains_new_slots(self) -> None:
        assert "E0" in AuthorityValidator.SLOT_ORDER
        assert "M0" in AuthorityValidator.SLOT_ORDER
        assert "H0" in AuthorityValidator.SLOT_ORDER

    def test_slot_order_positions(self) -> None:
        order = AuthorityValidator.SLOT_ORDER
        assert order.index("E0") == order.index("C0") + 1
        assert order.index("M0") == order.index("E0") + 1
        assert order.index("H0") == order.index("M0") + 1
        assert order.index("U0") == order.index("H0") + 1

    def test_new_slots_in_authority_rank(self) -> None:
        rank = AuthorityValidator.AUTHORITY_RANK
        # E0 > M0 > H0 > ZERO; all below INFO (C0).
        assert rank[AuthorityLevel.EXEMPLAR] < rank[AuthorityLevel.INFO]
        assert (
            rank[AuthorityLevel.EXEMPLAR]
            > rank[AuthorityLevel.META_COGNITIVE]
            > rank[AuthorityLevel.HEALING]
            > rank[AuthorityLevel.ZERO]
        )

    def test_valid_full_order_accepted(self) -> None:
        slots = [
            AuthoritySlot("S0", "sys", AuthorityLevel.ABSOLUTE, "L0"),
            AuthoritySlot("I0", "inst", AuthorityLevel.GOVERNED, "L1"),
            AuthoritySlot("D0", "con", AuthorityLevel.BINDING, "L5"),
            AuthoritySlot("C0", "ctx", AuthorityLevel.INFO, "L4"),
            AuthoritySlot("E0", "ex", AuthorityLevel.EXEMPLAR, "L4"),
            AuthoritySlot("M0", "think", AuthorityLevel.META_COGNITIVE, "L1"),
            AuthoritySlot("H0", "heal", AuthorityLevel.HEALING, "L5"),
            AuthoritySlot("U0", "user", AuthorityLevel.ZERO, "L0"),
        ]
        validator = AuthorityValidator()
        assert validator.validate_authority_chain(slots) is True, validator.get_errors()

    def test_e0_after_u0_rejected(self) -> None:
        slots = [
            AuthoritySlot("S0", "sys", AuthorityLevel.ABSOLUTE, "L0"),
            AuthoritySlot("U0", "user", AuthorityLevel.ZERO, "L0"),
            AuthoritySlot("E0", "ex", AuthorityLevel.EXEMPLAR, "L4"),
        ]
        validator = AuthorityValidator()
        assert validator.validate_slots(slots) is False
        assert any("out of order" in e for e in validator.get_errors())


class TestSlotAssemblyEngineRenders:
    def _build_slot(self, code: str, content: str) -> AuthoritySlot:
        return AuthoritySlot(
            slot_type=code,
            content=content,
            authority_level=AuthorityLevel.from_slot_code(code),
            source_layer="L4",
        )

    def test_e0_rendered_as_examples_section(self) -> None:
        engine = SlotAssemblyEngine(secret_key=b"x" * 32)
        engine.add_slot(self._build_slot("S0", "you are helpful"))
        engine.add_slot(self._build_slot("E0", "ex1 -> out1"))
        engine.add_slot(self._build_slot("U0", "do it"))
        artifact = engine.assemble()
        assert "[EXAMPLES]" in artifact.final_system_string
        assert "ex1 -> out1" in artifact.final_system_string

    def test_m0_rendered_as_thinking_approach(self) -> None:
        engine = SlotAssemblyEngine(secret_key=b"x" * 32)
        engine.add_slot(self._build_slot("S0", "sys"))
        engine.add_slot(self._build_slot("M0", "think step by step"))
        engine.add_slot(self._build_slot("U0", "go"))
        artifact = engine.assemble()
        assert "[THINKING_APPROACH]" in artifact.final_system_string
        assert "think step by step" in artifact.final_system_string

    def test_h0_rendered_as_recovery_context(self) -> None:
        engine = SlotAssemblyEngine(secret_key=b"x" * 32)
        engine.add_slot(self._build_slot("S0", "sys"))
        engine.add_slot(self._build_slot("H0", "prior attempt failed at step 3"))
        engine.add_slot(self._build_slot("U0", "retry"))
        artifact = engine.assemble()
        assert "[RECOVERY_CONTEXT]" in artifact.final_system_string
        assert "prior attempt failed at step 3" in artifact.final_system_string

    def test_slots_used_lists_new_codes(self) -> None:
        engine = SlotAssemblyEngine(secret_key=b"x" * 32)
        for code, content in [
            ("S0", "sys"),
            ("E0", "ex"),
            ("M0", "think"),
            ("H0", "heal"),
            ("U0", "user"),
        ]:
            engine.add_slot(self._build_slot(code, content))
        artifact = engine.assemble()
        for code in ("S0", "E0", "M0", "H0", "U0"):
            assert code in artifact.slots_used

    def test_legacy_five_slot_shape_still_works(self) -> None:
        """Regression: W3 changes must not break S0/I0/D0/C0/U0 legacy shape."""
        engine = SlotAssemblyEngine(secret_key=b"x" * 32)
        engine.add_slot(self._build_slot("S0", "sys"))
        engine.add_slot(self._build_slot("I0", "inst"))
        engine.add_slot(self._build_slot("D0", "constraint"))
        engine.add_slot(self._build_slot("C0", "ctx"))
        engine.add_slot(self._build_slot("U0", "user"))
        artifact = engine.assemble()
        assert "[CONSTRAINTS]" in artifact.final_system_string
        assert "[CONTEXT]" in artifact.final_user_string
        # No E0/M0/H0 markers when those slots aren't provided.
        assert "[EXAMPLES]" not in artifact.final_system_string
        assert "[THINKING_APPROACH]" not in artifact.final_system_string
        assert "[RECOVERY_CONTEXT]" not in artifact.final_system_string
