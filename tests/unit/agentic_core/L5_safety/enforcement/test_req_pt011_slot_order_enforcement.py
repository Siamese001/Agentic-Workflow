"""Test REQ-PT-011: Slot Order Enforcement.

REQ-PT-011: Tampered slot order MUST be detected and rejected at assembly time.
Fail-closed: missing or misordered slots abort prompt assembly.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReqPt011SlotOrderEnforcement:
    """Test REQ-PT-011 slot order enforcement via validate_slot_order."""

    def test_validate_slot_order_detects_missing_slot(self):
        """REQ-PT-011: Missing slot must raise SlotOrderViolation."""
        from agentic_core.prompt_governance.contracts.slot_contracts import (
            SlotOrderViolation,
            validate_slot_order,
        )
        # Prompt missing M0 through R0
        prompt = "<SLOT_S0>system</SLOT_S0><SLOT_D0>directives</SLOT_D0><SLOT_I0>inst</SLOT_I0>"
        with pytest.raises(SlotOrderViolation) as exc_info:
            validate_slot_order(prompt)
        assert "SLOT_MISSING" in str(exc_info.value)

    def test_validate_slot_order_detects_misordered_slots(self):
        """REQ-PT-011: Misordered slots must raise SlotOrderViolation."""
        from agentic_core.prompt_governance.contracts.slot_contracts import (
            SlotOrderViolation,
            validate_slot_order,
        )
        # U0 (user) appearing before S0 (system) with all slots present - security violation
        prompt = "<SLOT_U0>user</SLOT_U0><SLOT_S0>system</SLOT_S0><SLOT_D0>d</SLOT_D0><SLOT_M0>m</SLOT_M0><SLOT_I0>i</SLOT_I0><SLOT_E0>e</SLOT_E0><SLOT_C0>c</SLOT_C0><SLOT_Y0>y</SLOT_Y0><SLOT_H0>h</SLOT_H0><SLOT_R0>r</SLOT_R0>"
        with pytest.raises(SlotOrderViolation) as exc_info:
            validate_slot_order(prompt)
        assert "SLOT_ORDER_VIOLATED" in str(exc_info.value)

    def test_validate_slot_order_accepts_correct_order(self):
        """REQ-PT-011: Correct slot order passes validation."""
        from agentic_core.prompt_governance.contracts.slot_contracts import validate_slot_order
        # All 10 slots in correct order
        prompt = (
            "<SLOT_S0>system</SLOT_S0>"
            "<SLOT_D0>directives</SLOT_D0>"
            "<SLOT_M0>meta</SLOT_M0>"
            "<SLOT_I0>instructional</SLOT_I0>"
            "<SLOT_E0>exemplars</SLOT_E0>"
            "<SLOT_C0>context</SLOT_C0>"
            "<SLOT_Y0>synthesis</SLOT_Y0>"
            "<SLOT_U0>user</SLOT_U0>"
            "<SLOT_H0>healing</SLOT_H0>"
            "<SLOT_R0>output</SLOT_R0>"
        )
        validate_slot_order(prompt)  # Should not raise

    def test_prompt_assembler_enforces_slot_order(self):
        """REQ-PT-011: PromptAssembler.validate_slot_order called during assembly."""
        from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler

        pa = PromptAssembler()
        # This calls validate_slot_order internally via _slot_map validation
        result = pa.assemble(
            role="Test",
            objective="Test enforcement",
            context_data={"test": "data"},
            injections=[],
        )
        # Verify all slots present in correct order
        slot_positions = []
        for slot in ["S0", "D0", "M0", "I0", "E0", "C0", "Y0", "U0", "H0", "R0"]:
            pos = result.find(f"<SLOT_{slot}>")
            assert pos != -1, f"Missing SLOT_{slot}"
            slot_positions.append((slot, pos))
        # Verify ascending order
        for i in range(1, len(slot_positions)):
            assert slot_positions[i][1] > slot_positions[i-1][1]

    def test_slot_order_violation_message_includes_positions(self):
        """REQ-PT-011: Error message includes position details for debugging."""
        from agentic_core.prompt_governance.contracts.slot_contracts import (
            SlotOrderViolation,
            validate_slot_order,
        )
        # Include all slots but E0 before S0 (misordered)
        prompt = "<SLOT_E0>early</SLOT_E0><SLOT_S0>late</SLOT_S0><SLOT_D0>d</SLOT_D0><SLOT_M0>m</SLOT_M0><SLOT_I0>i</SLOT_I0><SLOT_C0>c</SLOT_C0><SLOT_Y0>y</SLOT_Y0><SLOT_U0>u</SLOT_U0><SLOT_H0>h</SLOT_H0><SLOT_R0>r</SLOT_R0>"
        with pytest.raises(SlotOrderViolation) as exc_info:
            validate_slot_order(prompt)
        msg = str(exc_info.value)
        assert "SLOT_ORDER_VIOLATED" in msg
        assert "pos" in msg.lower() or "SLOT_E0" in msg
