"""Redis degradation tests — Server survives Redis failures."""
import pytest
from tools.adg.core.service import ADGService


class TestRedisDegradation:
    """Server must degrade gracefully when Redis fails."""
    
    def test_starts_with_redis_down(self):
        """Service initializes when Redis unavailable."""
        svc = ADGService(redis_url="redis://invalid:9999/0")
        
        health = svc.health()
        assert health.sqlite == "healthy"
        assert health.redis == "unavailable"
        assert health.mode == "sqlite_only"
    
    def test_queries_work_in_sqlite_only_mode(self):
        """All queries work when Redis down."""
        svc = ADGService(redis_url="redis://invalid:9999/0")
        
        resp = svc.get_status()
        assert resp.status == "ok"
        assert resp.backend_used == "sqlite"
    
    def test_redis_timeout_handling(self):
        """Slow Redis doesn't block queries."""
        # Use a URL that hangs (blackhole IP)
        svc = ADGService(redis_url="redis://10.255.255.1:6379/0")
        
        # Query should still work via SQLite fallback
        resp = svc.get_node("1")
        assert resp.status in ["ok", "error"]  # May not find node, but shouldn't hang
    
    def test_health_reports_degraded(self):
        """Health check reports degraded status when Redis down."""
        svc = ADGService(redis_url="redis://invalid:9999/0")
        
        health = svc.health()
        assert health.mode == "sqlite_only"
        assert health.cache_hit_capable is False


class TestRedisFailureModes:
    """Test various Redis failure scenarios."""
    
    def test_connection_refused(self):
        """Connection refused handled gracefully."""
        svc = ADGService(redis_url="redis://localhost:9998/0")
        
        health = svc.health()
        assert health.sqlite == "healthy"
        assert health.redis in ["unavailable", "degraded"]
    
    def test_invalid_url(self):
        """Invalid Redis URL handled gracefully."""
        svc = ADGService(redis_url="not-a-valid-url")
        
        health = svc.health()
        assert health.sqlite == "healthy"
        # Should still work even with garbage URL
        resp = svc.get_status()
        assert resp.status == "ok"
    
    def test_none_url(self):
        """None Redis URL handled gracefully."""
        svc = ADGService(redis_url=None)
        
        health = svc.health()
        assert health.sqlite == "healthy"
        assert health.mode == "sqlite_only"


class TestCacheBackfill:
    """Cache backfill behavior when Redis available."""
    
    def test_no_backfill_when_redis_down(self):
        """No cache backfill attempts when Redis unavailable."""
        svc = ADGService(redis_url="redis://invalid:9999/0")
        
        # Should complete without error
        resp = svc.get_node("1")
        # Result may be error (node not found) or ok
        assert resp.backend_used == "sqlite"
