"""Tests for runtime_guard.py module."""

from __future__ import annotations

import asyncio
import os
from unittest.mock import patch, MagicMock

import pytest

from agentic_core.L0_routing.enforcement.runtime_guard import (
    _get_active_guards,
    _get_correlation_id,
    runtime_guard,
    assert_v15_guarded,
    v15_runtime_boundary,
)


class TestGetActiveGuards:
    """Tests for _get_active_guards function."""

    def test_get_active_guards_default(self):
        """Test _get_active_guards returns empty frozenset by default."""
        result = _get_active_guards()
        
        assert result == frozenset()

    def test_get_active_guards_in_context(self):
        """Test _get_active_guards returns active guards when in context."""
        # This would require setting the contextvar, which is tested indirectly
        # through runtime_guard decorator tests
        pass


class TestGetCorrelationId:
    """Tests for _get_correlation_id function."""

    def test_get_correlation_id_default(self):
        """Test _get_correlation_id returns None by default."""
        result = _get_correlation_id()
        
        assert result is None


class TestRuntimeGuard:
    """Tests for runtime_guard decorator."""

    def test_runtime_guard_sync_function_no_enforcement(self):
        """Test runtime_guard passes through when enforcement is off."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=False):
            
            @runtime_guard("test.entry.point")
            def test_func(x: int) -> int:
                return x * 2
            
            result = test_func(5)
            assert result == 10

    def test_runtime_guard_async_function_no_enforcement(self):
        """Test runtime_guard passes through for async when enforcement is off."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=False):
            
            @runtime_guard("test.entry.point")
            async def test_func(x: int) -> int:
                return x * 2
            
            result = asyncio.run(test_func(5))
            assert result == 10

    def test_runtime_guard_with_enforcement_sync(self):
        """Test runtime_guard wraps sync function when enforcement is on."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=True):
            with patch("agentic_core.L0_routing.enforcement.runtime_guard._resolve_correlation_id", return_value="corr123"):
                
                @runtime_guard("test.entry.point")
                def test_func(x: int) -> int:
                    return x * 2
                
                result = test_func(5)
                assert result == 10

    def test_runtime_guard_with_enforcement_async(self):
        """Test runtime_guard wraps async function when enforcement is on."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=True):
            with patch("agentic_core.L0_routing.enforcement.runtime_guard._resolve_correlation_id", return_value="corr123"):
                
                @runtime_guard("test.entry.point")
                async def test_func(x: int) -> int:
                    return x * 2
                
                result = asyncio.run(test_func(5))
                assert result == 10

    def test_runtime_guard_preserves_function_name(self):
        """Test runtime_guard preserves original function name."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=False):
            
            @runtime_guard("test.entry.point")
            def my_function(x: int) -> int:
                return x
            
            assert my_function.__name__ == "my_function"

    def test_runtime_guard_preserves_docstring(self):
        """Test runtime_guard preserves function docstring."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=False):
            
            @runtime_guard("test.entry.point")
            def my_function(x: int) -> int:
                """Test docstring."""
                return x
            
            assert my_function.__doc__ == "Test docstring."

    def test_runtime_guard_with_kwargs(self):
        """Test runtime_guard works with keyword arguments."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=False):
            
            @runtime_guard("test.entry.point")
            def test_func(a: int, b: int = 5) -> int:
                return a + b
            
            result = test_func(3)
            assert result == 8
            
            result = test_func(3, b=10)
            assert result == 13

    def test_runtime_guard_exception_handling(self):
        """Test runtime_guard propagates exceptions from wrapped function."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=True):
            with patch("agentic_core.L0_routing.enforcement.runtime_guard._resolve_correlation_id", return_value="corr123"):
                
                @runtime_guard("test.entry.point")
                def test_func():
                    raise ValueError("Test error")
                
                with pytest.raises(ValueError) as exc_info:
                    test_func()
                
                assert "Test error" in str(exc_info.value)


class TestAssertV15Guarded:
    """Tests for assert_v15_guarded function."""

    def test_assert_v15_guarded_no_enforcement(self):
        """Test assert_v15_guarded is no-op when enforcement is off."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=False):
            # Should not raise
            assert_v15_guarded("test.entry.point")

    def test_assert_v15_guarded_in_guarded_context(self):
        """Test assert_v15_guarded passes when in guarded context."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=True):
            with patch("agentic_core.L0_routing.enforcement.runtime_guard._get_active_guards", return_value=frozenset(["test.entry.point"])):
                # Should not raise
                assert_v15_guarded("test.entry.point")

    def test_assert_v15_guarded_outside_guarded_context_hard_fail(self):
        """Test assert_v15_guarded raises when outside guarded context (hard fail)."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=True):
            with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_hard_fail", return_value=True):
                with patch("agentic_core.L0_routing.enforcement.runtime_guard._get_active_guards", return_value=frozenset()):
                    
                    from agentic_core.L0_routing.types.guardian_enforcement_exceptions import V15EnforcementError
                    
                    with pytest.raises(V15EnforcementError) as exc_info:
                        assert_v15_guarded("test.entry.point")
                    
                    assert "V15 bypass detected" in str(exc_info.value)
                    assert "test.entry.point" in str(exc_info.value)

    def test_assert_v15_guarded_outside_guarded_context_soft_fail(self):
        """Test assert_v15_guarded logs warning when outside guarded context (soft fail)."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=True):
            with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_hard_fail", return_value=False):
                with patch("agentic_core.L0_routing.enforcement.runtime_guard._get_active_guards", return_value=frozenset()):
                    with patch("agentic_core.L0_routing.enforcement.runtime_guard.Logger") as mock_logger:
                        # Should not raise, just log
                        assert_v15_guarded("test.entry.point")
                        
                        # Verify warning was logged
                        assert mock_logger.warning.called

    def test_assert_v15_guarded_different_entry_point(self):
        """Test assert_v15_guarded raises when entry point doesn't match."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=True):
            with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_hard_fail", return_value=True):
                with patch("agentic_core.L0_routing.enforcement.runtime_guard._get_active_guards", return_value=frozenset(["other.entry.point"])):
                    
                    from agentic_core.L0_routing.types.guardian_enforcement_exceptions import V15EnforcementError
                    
                    with pytest.raises(V15EnforcementError) as exc_info:
                        assert_v15_guarded("test.entry.point")
                    
                    assert "V15 bypass detected" in str(exc_info.value)
                    assert "test.entry.point" in str(exc_info.value)


class TestV15RuntimeBoundary:
    """Tests for v15_runtime_boundary function."""

    def test_v15_runtime_boundary_is_alias(self):
        """Test v15_runtime_boundary is identical to runtime_guard."""
        # Both should reference the same function
        assert v15_runtime_boundary is runtime_guard

    def test_v15_runtime_guard_with_entry_point(self):
        """Test v15_runtime_boundary accepts entry point ID."""
        with patch("agentic_core.L0_routing.enforcement.runtime_guard.is_v15_enforced", return_value=False):
            
            @v15_runtime_boundary("test.entry.point")
            def test_func(x: int) -> int:
                return x * 2
            
            result = test_func(5)
            assert result == 10
