# tests/unit/test_HealerAgent.py
"""Unit tests for HealerMixin - Phase 2 Assertion Injection."""
from __future__ import annotations
import pytest
from pathlib import Path
from typing import Any, Dict, Optional
import tempfile
import os


class TestHealerMixinStructure:
    """Test HealerMixin can be imported and has expected structure."""

    def test_healer_mixin_importable(self):
        """Test HealerMixin can be imported."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        assert HealerMixin is not None

    def test_healer_mixin_has_heal_method(self):
        """Test HealerMixin has heal method."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        assert hasattr(HealerMixin, 'heal')

    def test_healer_mixin_has_apply_fix_method(self):
        """Test HealerMixin has apply_fix method."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        assert hasattr(HealerMixin, 'apply_fix')

    def test_healer_mixin_has_healing_enabled_flag(self):
        """Test HealerMixin has _healing_enabled flag."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        assert hasattr(HealerMixin, '_healing_enabled')
        assert HealerMixin._healing_enabled is True  # Default ON


class TestHealerMixinBehavior:
    """Test HealerMixin healing behavior."""

    def test_healing_disabled_returns_false(self):
        """Test that healing returns False when disabled."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        
        class TestAgent(HealerMixin):
            _healing_enabled = False
        
        agent = TestAgent()
        violation = {'path': 'test.py', 'class_name': 'Test', 'violation_type': 'test'}
        result = agent.heal(violation)
        assert result is False

    def test_healing_budget_tracking(self):
        """Test that healing budget is tracked."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        
        class TestAgent(HealerMixin):
            pass
        
        agent = TestAgent()
        assert agent._healing_count == 0
        assert agent._max_healing_per_session == 50

    def test_healing_metrics_initialization(self):
        """Test that healing metrics are initialized."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        
        class TestAgent(HealerMixin):
            pass
        
        agent = TestAgent()
        metrics = agent.get_healing_metrics()
        assert metrics['count'] == 0
        assert metrics['avg_time'] == 0
        assert metrics['success_rate'] == 1.0

    def test_can_heal_prerequisite_check(self):
        """Test _can_heal prerequisite check."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        
        class TestAgent(HealerMixin):
            pass
        
        agent = TestAgent()
        assert agent._can_heal() is True
        
        agent._healing_enabled = False
        assert agent._can_heal() is False

    def test_disable_enable_healing_class_methods(self):
        """Test disable_healing and enable_healing class methods."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        
        class TestAgent(HealerMixin):
            pass
        
        # Initially enabled
        assert TestAgent._healing_enabled is True
        
        # Disable
        TestAgent.disable_healing()
        assert TestAgent._healing_enabled is False
        
        # Re-enable
        TestAgent.enable_healing()
        assert TestAgent._healing_enabled is True

    def test_reset_healing_budget(self):
        """Test reset_healing_budget resets the counter."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        
        class TestAgent(HealerMixin):
            pass
        
        agent = TestAgent()
        agent._healing_count = 10
        agent.reset_healing_budget()
        assert agent._healing_count == 0


class TestHealerMixinFileOperations:
    """Test HealerMixin file operations and rollback."""

    def test_heal_returns_false_for_nonexistent_file(self):
        """Test heal returns False for nonexistent file."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        
        class TestAgent(HealerMixin):
            def apply_fix(self, ast_tree: Any, violation: Dict[str, Any]) -> Optional[Any]:
                return ast_tree
        
        agent = TestAgent()
        violation = {'path': '/nonexistent/file.py', 'class_name': 'Test', 'violation_type': 'test'}
        result = agent.heal(violation)
        assert result is False

    def test_heal_handles_syntax_error_gracefully(self):
        """Test heal handles files with syntax errors gracefully."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        
        class TestAgent(HealerMixin):
            def apply_fix(self, ast_tree: Any, violation: Dict[str, Any]) -> Optional[Any]:
                return ast_tree
        
        # Create temp file with syntax error
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write('def broken(\n')  # Syntax error
            temp_path = f.name
        
        try:
            agent = TestAgent()
            violation = {'path': temp_path, 'class_name': 'Test', 'violation_type': 'test'}
            result = agent.heal(violation)
            assert result is False
        finally:
            os.unlink(temp_path)

    def test_apply_fix_default_returns_none(self):
        """Test default apply_fix returns None (no-op)."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        
        class TestAgent(HealerMixin):
            pass
        
        agent = TestAgent()
        result = agent.apply_fix(None, {})
        assert result is None
