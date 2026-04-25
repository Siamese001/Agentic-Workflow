"""EQ-3 — AirlockAssembler.assemble_from_bom E0/M0/H0 + structured_slots wiring.

Plan: ``.windsurf/plans/eq1-compiled-artifact-schema-d9a3e7.md``
ADR:  ADR-PROMPT-ASSEMBLY-001 Q1 (slot extension)

Covers:
- PromptBOM back-compat (5-slot construction still works unchanged).
- E0 exemplars pulled from registry populate the E0 slot.
- meta_cognitive_mixin_id pulled from registry populates the M0 slot.
- healing_context populates H0 on the user-turn side.
- structured_slots dict is populated with AuthoritySlot per live slot.
- Missing exemplar IDs are non-fatal (KeyError swallowed).
- structured_slots is None when only flat strings are populated (EQ-1
  manifest_hash fall-back path).
"""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L0_routing.reasoning.assembly_stage import (
    AirlockAssembler,
    _build_structured_slots,
    _load_exemplars,
    _load_meta_cognitive,
    _load_synthesis,
)
from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
)
from agentic_core.prompt_governance.contracts.prompt_bom_types import PromptBOM


# --------------------------------------------------------------------------
# Registry stubs.
# --------------------------------------------------------------------------


class _RegistryWithE0:
    """Registry stub that implements the EQ-3 get_e0_exemplar surface."""

    def __init__(self, exemplars: dict[str, str]):
        self._exemplars = exemplars

    def get_e0_exemplar(self, exemplar_id: str) -> str:
        return self._exemplars[exemplar_id]


class _RegistryWithoutE0:
    """Registry stub that falls back to get_i0_mixin for exemplars."""

    def __init__(self, mixins: dict[str, str]):
        self._mixins = mixins

    def get_i0_mixin(self, mixin_id: str) -> str:
        return self._mixins[mixin_id]


class _RegistryWithM0:
    """Registry stub that implements the EQ-3 get_m0_mixin surface."""

    def __init__(self, m0: dict[str, str]):
        self._m0 = m0

    def get_m0_mixin(self, mixin_id: str) -> str:
        return self._m0[mixin_id]


class _RegistryWithY0:
    """Registry stub that implements the EQ-18 get_y0_synthesis surface."""

    def __init__(self, synthesis: dict[str, str]):
        self._synthesis = synthesis

    def get_y0_synthesis(self, synthesis_id: str) -> str:
        return self._synthesis[synthesis_id]


# --------------------------------------------------------------------------
# _load_exemplars.
# --------------------------------------------------------------------------


class TestLoadExemplars:
    def test_empty_ids_returns_empty_string(self):
        registry = _RegistryWithE0({})
        assert _load_exemplars(registry, ()) == ""

    def test_uses_get_e0_exemplar_when_available(self):
        registry = _RegistryWithE0({"ex1": "first example", "ex2": "second"})
        out = _load_exemplars(registry, ("ex1", "ex2"))
        # Sorted -> "first example" comes first (ex1 < ex2 lexicographically).
        assert out == "first example\n\nsecond"

    def test_falls_back_to_get_i0_mixin(self):
        registry = _RegistryWithoutE0({"ex1": "fallback content"})
        out = _load_exemplars(registry, ("ex1",))
        assert out == "fallback content"

    def test_missing_exemplar_is_non_fatal(self):
        registry = _RegistryWithE0({"ex1": "only one"})
        # ex2 does NOT exist — should not raise.
        out = _load_exemplars(registry, ("ex1", "ex2"))
        assert out == "only one"

    def test_registry_without_getters_returns_empty(self):
        class _Bare:
            pass

        assert _load_exemplars(_Bare(), ("ex1",)) == ""


# --------------------------------------------------------------------------
# _load_meta_cognitive.
# --------------------------------------------------------------------------


class TestLoadMetaCognitive:
    def test_none_id_returns_empty(self):
        registry = _RegistryWithM0({"m1": "thinking"})
        assert _load_meta_cognitive(registry, None) == ""

    def test_uses_get_m0_mixin_when_available(self):
        registry = _RegistryWithM0({"cot_v1": "Think step by step."})
        assert _load_meta_cognitive(registry, "cot_v1") == "Think step by step."

    def test_falls_back_to_get_i0_mixin(self):
        registry = _RegistryWithoutE0({"cot_v1": "Think step by step."})
        assert _load_meta_cognitive(registry, "cot_v1") == "Think step by step."

    def test_missing_id_returns_empty(self):
        registry = _RegistryWithM0({"cot_v1": "present"})
        assert _load_meta_cognitive(registry, "cot_v2") == ""


# --------------------------------------------------------------------------
# _build_structured_slots.
# --------------------------------------------------------------------------


class TestBuildStructuredSlots:
    def test_skips_empty_slots(self):
        slots = {
            "S0": "system",
            "D0": "",
            "I0": "instr",
            "E0": "",
            "C0": "",
            "M0": "",
            "U0": "user",
            "H0": "",
        }
        out = _build_structured_slots(slots, u0_clean="user-clean")
        assert set(out.keys()) == {"S0", "I0", "U0"}

    def test_u0_uses_post_neutralizer_content(self):
        slots = {"S0": "s", "U0": "raw"}
        out = _build_structured_slots(slots, u0_clean="sanitized")
        assert out["U0"].content == "sanitized"

    def test_authority_levels_match_slot_codes(self):
        slots = {
            "S0": "a",
            "I0": "b",
            "D0": "c",
            "E0": "d",
            "C0": "e",
            "M0": "f",
            "U0": "g",
            "H0": "h",
        }
        out = _build_structured_slots(slots, u0_clean="g-clean")
        assert out["S0"].authority_level is AuthorityLevel.ABSOLUTE
        assert out["I0"].authority_level is AuthorityLevel.GOVERNED
        assert out["D0"].authority_level is AuthorityLevel.BINDING
        assert out["E0"].authority_level is AuthorityLevel.EXEMPLAR
        assert out["C0"].authority_level is AuthorityLevel.INFO
        assert out["M0"].authority_level is AuthorityLevel.META_COGNITIVE
        assert out["U0"].authority_level is AuthorityLevel.ZERO
        assert out["H0"].authority_level is AuthorityLevel.HEALING

    def test_returns_none_when_all_empty(self):
        slots = dict.fromkeys(["S0", "D0", "I0", "E0", "C0", "M0", "U0", "H0"], "")
        out = _build_structured_slots(slots, u0_clean="")
        assert out is None


# --------------------------------------------------------------------------
# PromptBOM back-compat.
# --------------------------------------------------------------------------


class TestPromptBOMBackCompat:
    def test_five_slot_construction_still_works(self):
        bom = PromptBOM(
            trace_id="t",
            system_version_hash="h",
            mixins_required=("m1",),
            raw_u0="hi",
            raw_c0={},
            template_args={},
            path="A",
        )
        assert bom.exemplars_required == ()
        assert bom.meta_cognitive_mixin_id is None
        assert bom.healing_context is None

    def test_new_fields_roundtrip_through_to_dict(self):
        bom = PromptBOM(
            trace_id="t",
            system_version_hash="h",
            mixins_required=(),
            raw_u0="hi",
            raw_c0={},
            template_args={},
            path="A",
            exemplars_required=("ex1",),
            meta_cognitive_mixin_id="cot_v1",
            healing_context="prior attempt failed because X",
        )
        data = bom.to_dict()
        assert data["meta_cognitive_mixin_id"] == "cot_v1"
        assert data["healing_context"] == "prior attempt failed because X"

    def test_stable_hash_differs_when_new_fields_change(self):
        base = PromptBOM(
            trace_id="t",
            system_version_hash="h",
            mixins_required=(),
            raw_u0="hi",
            raw_c0={},
            template_args={},
            path="A",
        )
        with_m0 = PromptBOM(
            trace_id="t",
            system_version_hash="h",
            mixins_required=(),
            raw_u0="hi",
            raw_c0={},
            template_args={},
            path="A",
            meta_cognitive_mixin_id="cot_v1",
        )
        assert base.stable_hash() != with_m0.stable_hash()

    def test_y0_and_r0_fields_default_absent(self):
        bom = PromptBOM(
            trace_id="t",
            system_version_hash="h",
            mixins_required=(),
            raw_u0="hi",
            raw_c0={},
            template_args={},
            path="A",
        )
        assert bom.synthesis_required == ()
        assert bom.output_format_schema is None

    def test_y0_and_r0_roundtrip_through_to_dict(self):
        bom = PromptBOM(
            trace_id="t",
            system_version_hash="h",
            mixins_required=(),
            raw_u0="hi",
            raw_c0={},
            template_args={},
            path="A",
            synthesis_required=("syn1", "syn2"),
            output_format_schema="json: {answer: str}",
        )
        data = bom.to_dict()
        assert data["synthesis_required"] == ("syn1", "syn2")
        assert data["output_format_schema"] == "json: {answer: str}"

    def test_stable_hash_differs_when_y0_changes(self):
        base = PromptBOM(
            trace_id="t",
            system_version_hash="h",
            mixins_required=(),
            raw_u0="hi",
            raw_c0={},
            template_args={},
            path="A",
        )
        with_y0 = PromptBOM(
            trace_id="t",
            system_version_hash="h",
            mixins_required=(),
            raw_u0="hi",
            raw_c0={},
            template_args={},
            path="A",
            synthesis_required=("syn1",),
        )
        assert base.stable_hash() != with_y0.stable_hash()


# --------------------------------------------------------------------------
# _load_synthesis (Y0).
# --------------------------------------------------------------------------


class TestLoadSynthesis:
    def test_empty_ids_returns_empty_string(self):
        registry = _RegistryWithY0({})
        assert _load_synthesis(registry, ()) == ""

    def test_uses_get_y0_synthesis_when_available(self):
        registry = _RegistryWithY0({"syn1": "pattern A", "syn2": "pattern B"})
        out = _load_synthesis(registry, ("syn1", "syn2"))
        assert out == "pattern A\n\npattern B"

    def test_falls_back_to_get_i0_mixin(self):
        registry = _RegistryWithoutE0({"syn1": "fallback synthesis"})
        out = _load_synthesis(registry, ("syn1",))
        assert out == "fallback synthesis"

    def test_missing_synthesis_is_non_fatal(self):
        registry = _RegistryWithY0({"syn1": "only one"})
        out = _load_synthesis(registry, ("syn1", "syn2"))
        assert out == "only one"

    def test_registry_without_getters_returns_empty(self):
        class _Bare:
            pass

        assert _load_synthesis(_Bare(), ("syn1",)) == ""


# --------------------------------------------------------------------------
# Y0/R0 in structured_slots.
# --------------------------------------------------------------------------


class TestY0R0StructuredSlots:
    def test_y0_meta_learning_authority(self):
        slots = {"Y0": "telemetry summary"}
        out = _build_structured_slots(slots, u0_clean="")
        assert out is not None
        assert out["Y0"].authority_level is AuthorityLevel.META_LEARNING
        assert out["Y0"].source_layer == "L4"

    def test_r0_schema_authority(self):
        slots = {"R0": "json: {answer: str}"}
        out = _build_structured_slots(slots, u0_clean="")
        assert out is not None
        assert out["R0"].authority_level is AuthorityLevel.SCHEMA
        assert out["R0"].source_layer == "L_PG"

    def test_y0_r0_in_forbidden_security_check(self):
        """Y0 and R0 must not carry routing/safety fields per taxonomy invariant."""
        from agentic_core.L2_execution.reasoning.compiled_artifact import AuthoritySlot

        # Y0 with forbidden metadata must raise
        with pytest.raises(ValueError, match="taxonomy invariant"):
            AuthoritySlot(
                slot_type="Y0",
                content="summary",
                authority_level=AuthorityLevel.META_LEARNING,
                source_layer="L4",
                metadata={"route_mode": "A"},
            )
        # R0 with forbidden metadata must raise
        with pytest.raises(ValueError, match="taxonomy invariant"):
            AuthoritySlot(
                slot_type="R0",
                content="schema",
                authority_level=AuthorityLevel.SCHEMA,
                source_layer="L_PG",
                metadata={"safety_threshold": 0.5},
            )
