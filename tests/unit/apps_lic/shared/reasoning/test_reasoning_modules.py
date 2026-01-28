"""
Unit tests for apps_lic.shared.reasoning module.
Ensures bounds enforcement and logic correctness.
"""

import pytest
from pydantic import ValidationError

from apps_lic.shared.reasoning.cot import expand_thought_process
from apps_lic.shared.reasoning.toggles import ReasoningToggles


class TestReasoningToggles:
    def test_default_initialization(self):
        """Test that default values are valid and set correctly."""
        toggles = ReasoningToggles()
        assert toggles.use_cot is True
        assert toggles.tot_branches == 3
        assert toggles.temperature_cap == 0.5

    def test_valid_custom_initialization(self):
        """Test valid custom overrides."""
        toggles = ReasoningToggles(tot_branches=5, temperature_cap=0.9, use_reflexion=False)
        assert toggles.tot_branches == 5
        assert toggles.temperature_cap == 0.9
        assert toggles.use_reflexion is False

    @pytest.mark.parametrize("branches", [0, 6, -1])
    def test_tot_branches_bounds(self, branches):
        """Test that tot_branches enforces [1, 5]."""
        with pytest.raises(ValidationError) as exc:
            ReasoningToggles(tot_branches=branches)
        assert "must be between 1 and 5" in str(exc.value)

    @pytest.mark.parametrize("depth", [0, 4])
    def test_min_tot_depth_bounds(self, depth):
        """Test that min_tot_depth enforces [1, 3]."""
        with pytest.raises(ValidationError) as exc:
            ReasoningToggles(min_tot_depth=depth)
        assert "must be between 1 and 3" in str(exc.value)

    def test_immutability(self):
        """Ensure the config object is frozen."""
        toggles = ReasoningToggles()
        with pytest.raises(ValidationError):
            toggles.tot_branches = 2


class TestCoTExpansion:
    def test_basic_expansion(self):
        """Test basic 3-step expansion."""
        steps = expand_thought_process("Draft email", steps=3)
        assert len(steps) == 3
        assert "Analyze context for 'Draft email'" in steps[0]
        assert "Step 1:" in steps[0]
        assert "Step 3:" in steps[2]

    def test_step_bounds_validation(self):
        """Test that step counts are validated."""
        with pytest.raises(ValueError, match="between 1 and 10"):
            expand_thought_process("Test", steps=11)

        with pytest.raises(ValueError, match="between 1 and 10"):
            expand_thought_process("Test", steps=0)

    def test_empty_prompt_handling(self):
        """Test handling of empty prompts."""
        steps = expand_thought_process("   ")
        assert len(steps) == 1
        assert "Analyze empty request" in steps[0]
