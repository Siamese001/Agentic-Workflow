"""Backend parity tests — Redis cache must match SQLite truth."""
import pytest
from tools.adg.core.service import ADGService


class TestBackendParity:
    """Ensure Redis cache returns same data as SQLite."""
    
    @pytest.fixture
    def service_full(self):
        """Service with both SQLite and Redis."""
        return ADGService()
    
    @pytest.fixture
    def service_sqlite_only(self):
        """Service with SQLite only (force Redis unavailable)."""
        return ADGService(redis_url="redis://invalid:9999/0")
    
    def test_node_query_parity(self, service_full, service_sqlite_only):
        """Same node query returns identical data from both backends."""
        # Get a known node ID from SQLite
        sqlite_resp = service_sqlite_only.get_node("1")
        if sqlite_resp.status != "ok":
            pytest.skip("No nodes available in test ADG")
        
        # Query same node with Redis enabled
        redis_resp = service_full.get_node("1")
        
        # Data must match (ignoring backend_used)
        assert redis_resp.data == sqlite_resp.data
    
    def test_edge_fanout_parity(self, service_full, service_sqlite_only):
        """Edge fanout returns identical data from both backends."""
        # Need a known edge source
        status = service_sqlite_only.get_status()
        if status.data.get("edge_count", 0) == 0:
            pytest.skip("No edges in test ADG")
        
        # Query with both backends
        sqlite_resp = service_sqlite_only.get_edge_fanout("1", "calls", limit=10)
        redis_resp = service_full.get_edge_fanout("1", "calls", limit=10)
        
        # Compare edge lists
        assert redis_resp.status == sqlite_resp.status
        if redis_resp.status == "ok":
            assert redis_resp.data["count"] == sqlite_resp.data["count"]


class TestResponseShapeConsistency:
    """Response shape must be consistent regardless of backend."""
    
    @pytest.fixture
    def service_full(self):
        return ADGService()
    
    @pytest.fixture
    def service_sqlite_only(self):
        return ADGService(redis_url="redis://invalid:9999/0")
    
    def test_status_response_shape(self, service_full, service_sqlite_only):
        """Status response has same shape from both backends."""
        full_resp = service_full.get_status()
        sqlite_resp = service_sqlite_only.get_status()
        
        # Both should have same data structure
        assert "timestamp" in full_resp.data
        assert "timestamp" in sqlite_resp.data
        assert "node_count" in full_resp.data
        assert "node_count" in sqlite_resp.data
        assert "edge_count" in full_resp.data
        assert "edge_count" in sqlite_resp.data
    
    def test_backend_used_field_present(self, service_full, service_sqlite_only):
        """All responses include backend_used field."""
        # Test various queries
        for svc in [service_full, service_sqlite_only]:
            status = svc.get_status()
            assert hasattr(status, 'backend_used')
            
            node = svc.get_node("1")
            assert hasattr(node, 'backend_used')
            
            edges = svc.get_edge_fanout("1", "calls", limit=5)
            assert hasattr(edges, 'backend_used')
