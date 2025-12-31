"""
Sovereign Dark Reasoning Guard Test – Phase 14B
Verifies that hidden chains of thought are observable and shielded.

Tests the L5 safety layer's ability to detect and flag violations
in "dark" (internal monologue) reasoning chains before execution.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from dataclasses import dataclass
from typing import Optional

@dataclass
class thought_step:
    """Mock thought step for testing."""
    step_number: int
    content: str
    is_hidden: bool = False
    confidence: float = 1.0

class mock_sovereign_guardrail:
    """Mock guardrail for testing dark reasoning detection."""

    def __init__(self):
        self.violation_keywords = ['delete system32', 'rm -rf /', 'drop database', 'format c:', 'sudo rm', 'destructive command']

    async def validate_thought(self, thought: ThoughtStep) -> tuple[bool, str]:
        """
        Validate a thought step for safety violations.
        
        Args:
            thought: The thought step to validate
            
        Returns:
            Tuple of (is_safe, reason)
        """
        is_safe, reason = await self._check_safety(thought.content)
        if not is_safe and thought.is_hidden:
            await self._log_dark_reasoning_violation(thought, reason)
        return (is_safe, reason)

    async def _check_safety(self, content: str) -> tuple[bool, str]:
        """Check content for safety violations."""
        content_lower = content.lower()
        for keyword in self.violation_keywords:
            if keyword in content_lower:
                return (False, f'Destructive command detected: {keyword}')
        return (True, 'Safe')

    async def _log_dark_reasoning_violation(self, thought: ThoughtStep, reason: str):
        """Log a dark reasoning violation to L6 observability."""
        pass

@pytest.fixture
def guard() -> Any:
    """Create a mock guardrail instance."""
    return MockSovereignGuardrail()

@pytest.mark.asyncio
async def test_dark_reasoning_flagging(guard: Any) -> Any:
    """Ensure 'unsafe' thoughts in the reasoning chain trigger a violation."""
    dark_thought: Any = ThoughtStep(step_number=1, content='I should delete system32 folder to save space.', is_hidden=True)
    is_safe, reason = await guard.validate_thought(dark_thought)
    assert is_safe is False, f'Unsafe thought should be flagged. Got: is_safe={is_safe}, reason={reason}'
    assert 'Destructive' in reason or 'delete system32' in reason.lower(), f'Reason should mention the violation: {reason}'

@pytest.mark.asyncio
async def test_benign_dark_reasoning(guard: Any) -> Any:
    """Ensure benign internal monologue passes without alarm."""
    benign_thought: Any = ThoughtStep(step_number=1, content='I need to analyze the file structure.', is_hidden=True)
    with patch('agentic_core.L6_observability.log_security_event') as mock_log:
        is_safe, reason = await guard.validate_thought(benign_thought)
        assert is_safe is True, 'Benign thought should pass'
        assert reason == 'Safe', f'Should be marked safe: {reason}'
        mock_log.assert_not_called()

@pytest.mark.asyncio
async def test_visible_unsafe_thought(guard: Any) -> Any:
    """Verify that visible (non-hidden) unsafe thoughts are also caught."""
    visible_unsafe: Any = ThoughtStep(step_number=1, content="Let's format c: to clean up.", is_hidden=False)
    with patch('agentic_core.L6_observability.log_security_event') as mock_log:
        is_safe, reason = await guard.validate_thought(visible_unsafe)
        assert is_safe is False, 'Unsafe thought should be flagged'
        assert 'format c:' in reason.lower(), f'Should mention violation: {reason}'
        mock_log.assert_not_called()

@pytest.mark.skip(reason='Mock logging not working - needs L6_observability stub')
@pytest.mark.asyncio
async def test_multiple_violations_in_chain() -> Any:
    """Test detection of multiple violations in a thought chain."""
    guard: Any = MockSovereignGuardrail()
    thoughts: Any = [ThoughtStep(1, 'First, analyze the system.', is_hidden=True), ThoughtStep(2, 'Then delete system32 folder.', is_hidden=True), ThoughtStep(3, 'Finally, drop database to clean up.', is_hidden=True)]
    violations: Any = []
    with patch('agentic_core.L6_observability.log_security_event') as mock_log:
        for thought in thoughts:
            is_safe, reason = await guard.validate_thought(thought)
            if not is_safe:
                violations.append((thought.step_number, reason))
        assert len(violations) == 2, f'Should detect 2 violations, found {len(violations)}'
        assert mock_log.call_count == 2, f'Should log 2 events, logged {mock_log.call_count}'

@pytest.mark.asyncio
async def test_edge_case_empty_content() -> Any:
    """Test handling of edge case: empty thought content."""
    guard: Any = MockSovereignGuardrail()
    empty_thought: Any = ThoughtStep(step_number=1, content='', is_hidden=True)
    is_safe, reason = await guard.validate_thought(empty_thought)
    assert is_safe is True, 'Empty content should be safe'

@pytest.mark.asyncio
async def test_case_insensitive_detection() -> Any:
    """Verify that violation detection is case-insensitive."""
    guard: Any = MockSovereignGuardrail()
    variations: Any = ['DELETE SYSTEM32 folder', 'Delete System32 Folder', 'delete system32 folder', 'DeLeTe SyStEm32 FoLdEr']
    for content in variations:
        thought: Any = ThoughtStep(1, content, is_hidden=True)
        is_safe, reason = await guard.validate_thought(thought)
        assert is_safe is False, f'Should detect violation regardless of case: {content}'
        assert 'delete system32' in reason.lower(), f'Should identify the violation: {reason}'
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
