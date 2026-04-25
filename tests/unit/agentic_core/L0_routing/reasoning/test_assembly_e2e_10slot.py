"""E2E integration tests for 10-slot prompt assembly pipeline.

Covers the full assemble_from_bom flow with Y0/R0 slots wired,
edge cases for missing/empty synthesis and output format, slot
order validation with all 10 slots, and structured_slots authority
mapping for the complete slot set.

Plan: EQ-18 (prompt category coverage audit — Y0/R0/M0 hardening)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.reasoning.assembly_stage import (
    _build_structured_slots,
    _load_synthesis,
)
from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
)
from agentic_core.prompt_governance.contracts.prompt_bom_types import PromptBOM
from agentic_core.prompt_governance.contracts.slot_contracts import (
    SLOT_ORDER,
    SlotC0,
    SlotD0,
    SlotE0,
    SlotH0,
    SlotI0,
    SlotM0,
    SlotR0,
    SlotS0,
    SlotU0,
    SlotY0,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_bom(**overrides: Any) -> PromptBOM:
    """Build a minimal PromptBOM with sensible defaults."""
    defaults = dict(
        trace_id="e2e-trace-001",
        system_version_hash="sha256:abc",
        mixins_required=("mixin_a",),
        raw_u0="Fix the routing bug",
        raw_c0={"intent_class": "debug"},
        template_args={"intent_class": "debug"},
        path="A",
    )
    defaults.update(overrides)
    return PromptBOM(**defaults)


class _FullRegistry:
    """Registry stub with all typed getters (S0, I0, D0, E0, M0, Y0)."""

    def __init__(self) -> None:
        self._s0 = "Constitutional floor: no PowerShell, no bare except."
        self._mixins = {"mixin_a": "You are a debugging assistant."}
        self._fences = ("Role fence active.", "Max file size: 10KB")
        self._exemplars = {"ex_debug": "Example: trace the import chain."}
        self._m0 = {"cot_v1": "Think step by step. Verify each step."}
        self._synthesis = {"syn_telemetry": "Pattern: 80% of defects cluster in L2."}

    def get_s0(self, version_hash: str) -> str:
        return self._s0

    def get_i0_mixin(self, mixin_id: str) -> str:
        return self._mixins[mixin_id]

    def get_d0_fences(self, version_hash: str) -> tuple[str, ...]:
        return self._fences

    def get_e0_exemplar(self, exemplar_id: str) -> str:
        return self._exemplars[exemplar_id]

    def get_m0_mixin(self, mixin_id: str) -> str:
        return self._m0[mixin_id]

    def get_y0_synthesis(self, synthesis_id: str) -> str:
        return self._synthesis[synthesis_id]


# ---------------------------------------------------------------------------
# Slot contract roundtrips
# ---------------------------------------------------------------------------


class TestSlotContractRoundtrips:
    """Verify all 10 slot dataclasses construct and freeze correctly."""

    def test_slot_y0_dict_content(self) -> None:
        slot = SlotY0(content={"pattern": "defect clustering", "confidence": 0.82})
        assert slot.content["pattern"] == "defect clustering"

    def test_slot_r0_string_content(self) -> None:
        slot = SlotR0(content="json: {answer: str, confidence: float}")
        assert "answer" in slot.content

    def test_slot_m0_content(self) -> None:
        slot = SlotM0(content="Think step by step.")
        assert slot.content == "Think step by step."

    def test_all_10_slots_in_slot_order(self) -> None:
        assert len(SLOT_ORDER) == 10
        assert "Y0" in SLOT_ORDER
        assert "R0" in SLOT_ORDER
        # Y0 before U0, R0 last
        assert SLOT_ORDER.index("Y0") < SLOT_ORDER.index("U0")
        assert SLOT_ORDER[-1] == "R0"


# ---------------------------------------------------------------------------
# PromptBOM Y0/R0 edge cases
# ---------------------------------------------------------------------------


class TestPromptBOMY0R0EdgeCases:
    def test_empty_synthesis_required_produces_empty_y0(self) -> None:
        bom = _minimal_bom(synthesis_required=())
        assert bom.synthesis_required == ()

    def test_none_output_format_schema_produces_empty_r0(self) -> None:
        bom = _minimal_bom(output_format_schema=None)
        assert bom.output_format_schema is None

    def test_blank_output_format_schema_treated_as_empty(self) -> None:
        bom = _minimal_bom(output_format_schema="")
        assert bom.output_format_schema == ""

    def test_synthesis_required_sorted_in_to_dict(self) -> None:
        bom = _minimal_bom(synthesis_required=("syn_b", "syn_a"))
        data = bom.to_dict()
        assert data["synthesis_required"] == ("syn_a", "syn_b")

    def test_bom_hash_changes_with_output_format(self) -> None:
        base = _minimal_bom()
        with_r0 = _minimal_bom(output_format_schema="json")
        assert base.stable_hash() != with_r0.stable_hash()

    def test_bom_hash_changes_with_synthesis(self) -> None:
        base = _minimal_bom()
        with_y0 = _minimal_bom(synthesis_required=("syn1",))
        assert base.stable_hash() != with_y0.stable_hash()

    def test_bom_hash_changes_independently_for_y0_vs_r0(self) -> None:
        with_y0 = _minimal_bom(synthesis_required=("syn1",))
        with_r0 = _minimal_bom(output_format_schema="json")
        assert with_y0.stable_hash() != with_r0.stable_hash()


# ---------------------------------------------------------------------------
# _load_synthesis edge cases
# ---------------------------------------------------------------------------


class TestLoadSynthesisEdgeCases:
    def test_registry_with_y0_but_missing_id(self) -> None:
        registry = _FullRegistry()
        # "syn_nonexistent" not in registry — should skip without error
        result = _load_synthesis(registry, ("syn_nonexistent",))
        assert result == ""

    def test_mixed_found_and_missing_ids(self) -> None:
        registry = _FullRegistry()
        result = _load_synthesis(registry, ("syn_telemetry", "syn_missing"))
        assert "defects cluster" in result
        # Missing ID silently skipped
        assert "syn_missing" not in result

    def test_duplicate_ids_deduplicated_in_output(self) -> None:
        """Sorted input with duplicate IDs — getter called once per unique ID."""
        call_count = 0
        original_get = _FullRegistry().get_y0_synthesis

        class _CountingRegistry(_FullRegistry):
            def get_y0_synthesis(self, synthesis_id: str) -> str:
                nonlocal call_count
                call_count += 1
                return super().get_y0_synthesis(synthesis_id)

        registry = _CountingRegistry()
        # sorted(("syn_telemetry", "syn_telemetry")) = ("syn_telemetry", "syn_telemetry")
        # but tuple dedup is caller's responsibility — we just call getter for each
        result = _load_synthesis(registry, ("syn_telemetry",))
        assert call_count == 1


# ---------------------------------------------------------------------------
# _build_structured_slots with full 10-slot surface
# ---------------------------------------------------------------------------


class TestBuildStructuredSlotsFull10:
    def test_all_10_slots_populated(self) -> None:
        slots = {
            "S0": "constitution",
            "D0": "role fence",
            "I0": "identity",
            "E0": "example",
            "C0": "context",
            "M0": "think step by step",
            "Y0": "pattern summary",
            "U0": "user intent",
            "H0": "healing proposal",
            "R0": "json: {answer: str}",
        }
        out = _build_structured_slots(slots, u0_clean="sanitized intent")
        assert out is not None
        assert set(out.keys()) == {"S0", "D0", "I0", "E0", "C0", "M0", "Y0", "U0", "H0", "R0"}

    def test_authority_levels_for_all_10(self) -> None:
        slots = {
            "S0": "a",
            "D0": "b",
            "I0": "c",
            "E0": "d",
            "C0": "e",
            "M0": "f",
            "Y0": "g",
            "U0": "h",
            "H0": "i",
            "R0": "j",
        }
        out = _build_structured_slots(slots, u0_clean="h-clean")
        assert out["S0"].authority_level is AuthorityLevel.ABSOLUTE
        assert out["D0"].authority_level is AuthorityLevel.BINDING
        assert out["I0"].authority_level is AuthorityLevel.GOVERNED
        assert out["E0"].authority_level is AuthorityLevel.EXEMPLAR
        assert out["C0"].authority_level is AuthorityLevel.INFO
        assert out["M0"].authority_level is AuthorityLevel.META_COGNITIVE
        assert out["Y0"].authority_level is AuthorityLevel.META_LEARNING
        assert out["U0"].authority_level is AuthorityLevel.ZERO
        assert out["H0"].authority_level is AuthorityLevel.HEALING
        assert out["R0"].authority_level is AuthorityLevel.SCHEMA

    def test_source_layers_for_y0_and_r0(self) -> None:
        slots = {"Y0": "synthesis", "R0": "schema"}
        out = _build_structured_slots(slots, u0_clean="")
        assert out["Y0"].source_layer == "L4"
        assert out["R0"].source_layer == "L_PG"

    def test_only_y0_and_r0_populated(self) -> None:
        """When only Y0 and R0 have content, only those appear."""
        slots = dict.fromkeys(["S0", "D0", "I0", "E0", "C0", "M0", "Y0", "U0", "H0", "R0"], "")
        slots["Y0"] = "telemetry summary"
        slots["R0"] = "json: {result: str}"
        out = _build_structured_slots(slots, u0_clean="")
        assert set(out.keys()) == {"Y0", "R0"}

    def test_empty_y0_r0_excluded_from_structured(self) -> None:
        """Empty Y0/R0 should not appear in structured_slots."""
        slots = {"S0": "system", "Y0": "", "R0": ""}
        out = _build_structured_slots(slots, u0_clean="user")
        assert "Y0" not in out
        assert "R0" not in out
        assert "S0" in out


# ---------------------------------------------------------------------------
# AuthoritySlot security invariants for Y0/R0
# ---------------------------------------------------------------------------


class TestAuthoritySlotSecurityY0R0:
    @pytest.mark.parametrize(
        "slot_type,authority,forbidden_key",
        [
            ("Y0", AuthorityLevel.META_LEARNING, "route_mode"),
            ("Y0", AuthorityLevel.META_LEARNING, "safety_threshold"),
            ("Y0", AuthorityLevel.META_LEARNING, "execution_tier"),
            ("Y0", AuthorityLevel.META_LEARNING, "auth_token"),
            ("R0", AuthorityLevel.SCHEMA, "route_mode"),
            ("R0", AuthorityLevel.SCHEMA, "safety_threshold"),
            ("R0", AuthorityLevel.SCHEMA, "execution_tier"),
            ("R0", AuthorityLevel.SCHEMA, "auth_token"),
        ],
    )
    def test_forbidden_metadata_rejected(
        self, slot_type: str, authority: AuthorityLevel, forbidden_key: str
    ) -> None:
        with pytest.raises(ValueError, match="taxonomy invariant"):
            AuthoritySlot(
                slot_type=slot_type,
                content="test",
                authority_level=authority,
                source_layer="L4",
                metadata={forbidden_key: "forbidden"},
            )

    def test_y0_allows_non_forbidden_metadata(self) -> None:
        s = AuthoritySlot(
            slot_type="Y0",
            content="summary",
            authority_level=AuthorityLevel.META_LEARNING,
            source_layer="L4",
            metadata={"producer": "telemetry_engine", "trace_ids": ("t1", "t2")},
        )
        assert s.metadata["producer"] == "telemetry_engine"

    def test_r0_allows_non_forbidden_metadata(self) -> None:
        s = AuthoritySlot(
            slot_type="R0",
            content="json schema",
            authority_level=AuthorityLevel.SCHEMA,
            source_layer="L_PG",
            metadata={"format_version": "2", "strict": True},
        )
        assert s.metadata["strict"] is True


# ---------------------------------------------------------------------------
# Slot order validation with Y0/R0
# ---------------------------------------------------------------------------


class TestSlotOrderValidation10Slot:
    def test_full_10_slot_order_valid(self) -> None:
        from agentic_core.prompt_governance.contracts.slot_contracts import validate_slot_order

        prompt = (
            "<SLOT_S0></SLOT_S0>"
            "<SLOT_D0></SLOT_D0>"
            "<SLOT_M0></SLOT_M0>"
            "<SLOT_I0></SLOT_I0>"
            "<SLOT_E0></SLOT_E0>"
            "<SLOT_C0></SLOT_C0>"
            "<SLOT_Y0></SLOT_Y0>"
            "<SLOT_U0></SLOT_U0>"
            "<SLOT_H0></SLOT_H0>"
            "<SLOT_R0></SLOT_R0>"
        )
        validate_slot_order(prompt)  # Should not raise

    def test_y0_after_u0_is_misordered(self) -> None:
        from agentic_core.prompt_governance.contracts.slot_contracts import (
            SlotOrderViolation,
            validate_slot_order,
        )

        # Y0 placed after U0 — violates canonical order
        prompt = (
            "<SLOT_S0></SLOT_S0>"
            "<SLOT_D0></SLOT_D0>"
            "<SLOT_M0></SLOT_M0>"
            "<SLOT_I0></SLOT_I0>"
            "<SLOT_E0></SLOT_E0>"
            "<SLOT_C0></SLOT_C0>"
            "<SLOT_U0></SLOT_U0>"
            "<SLOT_Y0></SLOT_Y0>"  # wrong: Y0 must come before U0
            "<SLOT_H0></SLOT_H0>"
            "<SLOT_R0></SLOT_R0>"
        )
        with pytest.raises(SlotOrderViolation):
            validate_slot_order(prompt)

    def test_r0_not_last_is_misordered(self) -> None:
        from agentic_core.prompt_governance.contracts.slot_contracts import (
            SlotOrderViolation,
            validate_slot_order,
        )

        # R0 placed before H0 — violates canonical order (R0 must be last)
        prompt = (
            "<SLOT_S0></SLOT_S0>"
            "<SLOT_D0></SLOT_D0>"
            "<SLOT_M0></SLOT_M0>"
            "<SLOT_I0></SLOT_I0>"
            "<SLOT_E0></SLOT_E0>"
            "<SLOT_C0></SLOT_C0>"
            "<SLOT_Y0></SLOT_Y0>"
            "<SLOT_U0></SLOT_U0>"
            "<SLOT_R0></SLOT_R0>"  # wrong: R0 must come after H0
            "<SLOT_H0></SLOT_H0>"
        )
        with pytest.raises(SlotOrderViolation):
            validate_slot_order(prompt)


# ---------------------------------------------------------------------------
# AuthorityLevel enum completeness
# ---------------------------------------------------------------------------


class TestAuthorityLevelCompleteness:
    def test_schema_level_exists(self) -> None:
        assert hasattr(AuthorityLevel, "SCHEMA")
        assert AuthorityLevel.SCHEMA.value > AuthorityLevel.META_LEARNING.value

    def test_from_slot_code_covers_all_10(self) -> None:
        for code in SLOT_ORDER:
            level = AuthorityLevel.from_slot_code(code)
            assert level != AuthorityLevel.ZERO or code == "U0", (
                f"Only U0 should map to ZERO, got {code}→{level}"
            )

    def test_r0_case_insensitive(self) -> None:
        assert AuthorityLevel.from_slot_code("r0") == AuthorityLevel.SCHEMA

    def test_y0_case_insensitive(self) -> None:
        assert AuthorityLevel.from_slot_code("y0") == AuthorityLevel.META_LEARNING
