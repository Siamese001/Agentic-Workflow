"""Tests for L0_routing.reasoning.route_gates module."""

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.reasoning import route_gates


class TestRouteGates:
    """Test suite for route gates (D1 exact cache, D2 semantic cache)."""

    def test_check_d1_exact_cache_hit(self):
        """Test D1 exact cache returns hit when found."""
        request = {"key": "value"}
        mock_cache = MagicMock()
        mock_cache.get.return_value = MagicMock(
            response='{"result": "cached"}', cache_key="key123", query_hash="hash123", hit_timestamp=123456, ttl_seconds=3600
        )
        
        with patch(
            "agentic_core.L0_routing.reasoning.route_gates.get_global_l1_cache",
            return_value=mock_cache,
        ):
            with patch.dict("os.environ", {"EXACT_CACHE_D1_ENABLED": "1"}):
                result = route_gates.check_d1_exact_cache(request)
                
                assert result is not None
                assert result["response"] == {"result": "cached"}

    def test_check_d1_exact_cache_miss(self):
        """Test D1 exact cache returns miss when not found."""
        request = {"key": "value"}
        mock_cache = MagicMock()
        mock_cache.get.return_value = None
        
        with patch(
            "agentic_core.L0_routing.reasoning.route_gates.get_global_l1_cache",
            return_value=mock_cache,
        ):
            with patch.dict("os.environ", {"EXACT_CACHE_D1_ENABLED": "1"}):
                result = route_gates.check_d1_exact_cache(request)
                
                assert result is None

    def test_check_d1_exact_cache_disabled(self):
        """Test D1 exact cache returns miss when disabled."""
        request = {"key": "value"}
        
        with patch.dict("os.environ", {"EXACT_CACHE_D1_ENABLED": "0"}):
            result = route_gates.check_d1_exact_cache(request)
            
            assert result is None

    def test_check_d2_semantic_cache_hit(self):
        """Test D2 semantic cache returns hit when similarity above threshold."""
        request = {"query": "test"}
        mock_cache = MagicMock()
        mock_cache.recall.return_value = {"response": "cached_result", "similarity": 0.99}
        
        with patch(
            "agentic_core.L0_routing.reasoning.route_gates.SemanticCacheManager",
            return_value=mock_cache,
        ):
            with patch.dict("os.environ", {"SEMANTIC_CACHE_D2_ENABLED": "1"}):
                with patch("agentic_core.L0_routing.reasoning.route_gates.get_threshold", return_value=0.95):
                    result = route_gates.check_d2_semantic_cache(
                        request, namespace="test_namespace"
                    )
                    
                    assert result is not None
                    assert result["response"] == "cached_result"

    def test_check_d2_semantic_cache_miss_below_threshold(self):
        """Test D2 semantic cache returns miss when similarity below threshold."""
        request = {"query": "test"}
        mock_cache = MagicMock()
        mock_cache.recall.return_value = {"response": "cached_result", "similarity": 0.80}
        
        with patch(
            "agentic_core.L0_routing.reasoning.route_gates.SemanticCacheManager",
            return_value=mock_cache,
        ):
            with patch.dict("os.environ", {"SEMANTIC_CACHE_D2_ENABLED": "1"}):
                with patch("agentic_core.L0_routing.reasoning.route_gates.get_threshold", return_value=0.95):
                    result = route_gates.check_d2_semantic_cache(
                        request, namespace="test_namespace"
                    )
                    
                    assert result is None

    def test_check_d2_semantic_cache_miss_no_result(self):
        """Test D2 semantic cache returns miss when no result."""
        request = {"query": "test"}
        mock_cache = MagicMock()
        mock_cache.recall.return_value = None
        
        with patch(
            "agentic_core.L0_routing.reasoning.route_gates.SemanticCacheManager",
            return_value=mock_cache,
        ):
            with patch.dict("os.environ", {"SEMANTIC_CACHE_D2_ENABLED": "1"}):
                result = route_gates.check_d2_semantic_cache(
                    request, namespace="test_namespace"
                )
                
                assert result is None

    def test_check_d2_semantic_cache_disabled(self):
        """Test D2 semantic cache returns miss when disabled."""
        request = {"query": "test"}
        
        with patch.dict("os.environ", {"SEMANTIC_CACHE_D2_ENABLED": "0"}):
            result = route_gates.check_d2_semantic_cache(
                request, namespace="test_namespace"
            )
            
            assert result is None

    def test_check_route_gates_d1_hit(self):
        """Test composed route gates returns D1 hit when D1 matches."""
        request = {"key": "value"}
        mock_cache = MagicMock()
        mock_cache.get.return_value = MagicMock(
            response='{"result": "cached"}', cache_key="key123", query_hash="hash123", hit_timestamp=123456, ttl_seconds=3600
        )
        
        with patch(
            "agentic_core.L0_routing.reasoning.route_gates.get_global_l1_cache",
            return_value=mock_cache,
        ):
            with patch.dict("os.environ", {"EXACT_CACHE_D1_ENABLED": "1"}):
                result = route_gates.check_route_gates(request, namespace="test")
                
                assert result is not None
                assert result[0].selected_route == "R1A"

    def test_check_route_gates_d2_hit(self):
        """Test composed route gates returns D2 hit when D2 matches."""
        request = {"query": "test"}
        mock_d1_cache = MagicMock()
        mock_d1_cache.get.return_value = None
        mock_d2_cache = MagicMock()
        mock_d2_cache.recall.return_value = {"response": "cached_result", "similarity": 0.99}
        
        with patch(
            "agentic_core.L0_routing.reasoning.route_gates.get_global_l1_cache",
            return_value=mock_d1_cache,
        ):
            with patch(
                "agentic_core.L0_routing.reasoning.route_gates.SemanticCacheManager",
                return_value=mock_d2_cache,
            ):
                with patch.dict("os.environ", {"EXACT_CACHE_D1_ENABLED": "1", "SEMANTIC_CACHE_D2_ENABLED": "1"}):
                    with patch("agentic_core.L0_routing.reasoning.route_gates.get_threshold", return_value=0.95):
                        result = route_gates.check_route_gates(request, namespace="test")
                        
                        assert result is not None
                        assert result[0].selected_route == "R1B"

    def test_check_route_gates_both_miss(self):
        """Test composed route gates returns miss when both caches miss."""
        request = {"query": "test"}
        mock_d1_cache = MagicMock()
        mock_d1_cache.get.return_value = None
        mock_d2_cache = MagicMock()
        mock_d2_cache.recall.return_value = None
        
        with patch(
            "agentic_core.L0_routing.reasoning.route_gates.get_global_l1_cache",
            return_value=mock_d1_cache,
        ):
            with patch(
                "agentic_core.L0_routing.reasoning.route_gates.SemanticCacheManager",
                return_value=mock_d2_cache,
            ):
                with patch.dict("os.environ", {"EXACT_CACHE_D1_ENABLED": "1", "SEMANTIC_CACHE_D2_ENABLED": "1"}):
                    result = route_gates.check_route_gates(request, namespace="test")
                    
                    assert result is None

    def test_canonical_request_hash(self):
        """Test canonical request hash generation."""
        request1 = {"key": "value", "nested": {"a": 1}}
        request2 = {"nested": {"a": 1}, "key": "value"}  # Different order
        
        hash1 = route_gates.canonical_request_hash(request1)
        hash2 = route_gates.canonical_request_hash(request2)
        
        assert hash1 == hash2  # Same hash regardless of key order

    def test_public_api_exports(self):
        """Test that public API functions are exported."""
        assert hasattr(route_gates, "check_d1_exact_cache")
        assert hasattr(route_gates, "check_d2_semantic_cache")
        assert hasattr(route_gates, "check_route_gates")
        assert hasattr(route_gates, "canonical_request_hash")
