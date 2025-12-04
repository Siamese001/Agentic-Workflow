"""Stress Tests for Recursion Depth."""

class TestRecursionDepth:
    """Stress tests for recursion depth limits."""
    
    def test_deep_recursion_handling(self):
        """Test handling of deep recursion."""
        def recursive_func(n, acc=0):
            if n <= 0:
                return acc
            return recursive_func(n - 1, acc + 1)
        
        result = recursive_func(100)
        assert result == 100
