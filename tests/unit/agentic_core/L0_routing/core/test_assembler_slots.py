"""Runtime-hardened tests for PromptAssembler slot integrity."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def prompt_assembler_class():
    module = pytest.importorskip("agentic_core.prompt_governance.core.prompt_assembler")
    return module.PromptAssembler


@pytest.fixture()
def assemble(prompt_assembler_class):
    def _assemble(**overrides):
        assembler = prompt_assembler_class(
            **({"template": overrides.pop("template")} if "template" in overrides else {})
        )
        return assembler.assemble(
            role="Test",
            objective="Test slots",
            context_data={"key": "value"},
            injections=[],
            **overrides,
        )

    return _assemble


class TestAssemblerSlots:
    def test_prompt_assembler_slot_map_has_all_10_slots(self, assemble):
        result = assemble()

        for slot in ["S0", "D0", "M0", "I0", "E0", "C0", "Y0", "U0", "H0", "R0"]:
            assert f"<SLOT_{slot}>" in result, f"Missing SLOT_{slot}"
            assert result.count(f"<SLOT_{slot}>") == 1

    def test_prompt_assembler_missing_slot_raises(self, assemble):
        with pytest.raises(Exception) as exc_info:
            assemble(template="<SLOT_S0>test</SLOT_S0>", objective="Test")

        assert "SLOT" in str(exc_info.value) or "Missing expected tag" in str(exc_info.value)

    @pytest.mark.parametrize(
        ("field", "value", "slot"),
        [
            ("exemplars", "golden context content", "E0"),
            ("meta_cognitive", "chain of thought reasoning", "M0"),
            ("synthesis", "pattern analysis", "Y0"),
            ("healing_proposal", "correction plan", "H0"),
        ],
    )
    def test_optional_slot_content_is_placed_correctly(self, assemble, field, value, slot):
        result = assemble(**{field: value})

        assert value in result
        assert f"<SLOT_{slot}>" in result
