"""Test AssemblerSlots functionality - PromptAssembler slot validation."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAssemblerSlots:
    """Test PromptAssembler slot map validation."""

    def test_prompt_assembler_slot_map_has_all_10_slots(self):
        """Test PromptAssembler._slot_map includes all 10 slots."""
        from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler

        pa = PromptAssembler()
        result = pa.assemble(
            role="Test",
            objective="Test slots",
            context_data={"key": "value"},
            injections=[],
        )
        # All 10 slots should be in output
        for slot in ["S0", "D0", "M0", "I0", "E0", "C0", "Y0", "U0", "H0", "R0"]:
            assert f"<SLOT_{slot}>" in result, f"Missing SLOT_{slot}"

    def test_prompt_assembler_missing_slot_raises(self):
        """Test that removing a slot from custom template raises error."""
        from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler

        # Template missing most slots - will fail validate_template_integrity
        pa = PromptAssembler(template="<SLOT_S0>test</SLOT_S0>")
        with pytest.raises(Exception) as exc_info:  # SecurityIntegrityError or ValueError
            pa.assemble(
                role="Test",
                objective="Test",
                context_data={"key": "value"},
                injections=[],
            )
        # Should get either SLOT_MISSING from _slot_map or missing tag from integrity check
        assert "SLOT" in str(exc_info.value) or "Missing expected tag" in str(exc_info.value)

    def test_prompt_assembler_e0_slot_content(self):
        """Test exemplars content appears in E0 slot."""
        from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler

        pa = PromptAssembler()
        result = pa.assemble(
            role="Test",
            objective="Test",
            context_data={"key": "value"},
            injections=[],
            exemplars="golden context content",
        )
        assert "golden context content" in result
        assert "<SLOT_E0>" in result

    def test_prompt_assembler_m0_slot_content(self):
        """Test meta_cognitive content appears in M0 slot."""
        from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler

        pa = PromptAssembler()
        result = pa.assemble(
            role="Test",
            objective="Test",
            context_data={"key": "value"},
            injections=[],
            meta_cognitive="chain of thought reasoning",
        )
        assert "chain of thought reasoning" in result
        assert "<SLOT_M0>" in result

    def test_prompt_assembler_y0_slot_content(self):
        """Test synthesis content appears in Y0 slot."""
        from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler

        pa = PromptAssembler()
        result = pa.assemble(
            role="Test",
            objective="Test",
            context_data={"key": "value"},
            injections=[],
            synthesis="pattern analysis",
        )
        assert "pattern analysis" in result
        assert "<SLOT_Y0>" in result

    def test_prompt_assembler_h0_slot_content(self):
        """Test healing_proposal content appears in H0 slot."""
        from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler

        pa = PromptAssembler()
        result = pa.assemble(
            role="Test",
            objective="Test",
            context_data={"key": "value"},
            injections=[],
            healing_proposal="correction plan",
        )
        assert "correction plan" in result
        assert "<SLOT_H0>" in result
