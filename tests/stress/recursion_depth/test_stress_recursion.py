"""Stress Tests for Recursion Depth."""

class TestStressRecursion:
    """Stress tests for recursion depth."""
    
    def test_deep_recursion_handling(self):
        """Test handling of deep recursion."""
        def recursive_sum(n, acc=0):
            if n <= 0:
                return acc
            return recursive_sum(n - 1, acc + n)
        
        result = recursive_sum(100)
        assert result == 5050
    
    def test_nested_structure_depth(self):
        """Test nested structure depth handling."""
        depth = 50
        nested = {}
        current = nested
        for i in range(depth):
            current["level"] = i
            current["child"] = {}
            current = current["child"]
        assert nested["level"] == 0
