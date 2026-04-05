"""Health tool tests — adg_health returns correct diagnostics."""
from tools.adg.core.service import ADGService
from tools.adg.mcp.health import HealthDiagnostics


class TestHealthTool:
    """Health diagnostics return expected structure."""

    def test_health_structure(self):
        """Health report has all required fields."""
        svc = ADGService()
        health = HealthDiagnostics(svc)

        report = health.full_report()

        assert "mode" in report
        assert "sqlite" in report
        assert "redis" in report
        assert "cache_hit_capable" in report
        assert "schema_version" in report
        assert "adg_snapshot_id" in report

    def test_quick_check_states(self):
        """Quick check returns appropriate state."""
        # With Redis (if available)
        svc_full = ADGService()
        health_full = HealthDiagnostics(svc_full)

        quick = health_full.quick_check()
        assert quick["status"] in ["healthy", "degraded"]

        # Without Redis
        svc_sqlite = ADGService(redis_url="redis://invalid:9999/0")
        health_sqlite = HealthDiagnostics(svc_sqlite)

        quick = health_sqlite.quick_check()
        assert quick["status"] == "degraded"
        assert "Redis unavailable" in quick["reason"]


class TestHealthModes:
    """Health check correctly identifies operation mode."""

    def test_full_mode_when_redis_healthy(self):
        """Mode is 'full' when Redis available."""
        svc = ADGService()
        health = svc.health()

        # If Redis is actually running, mode should be full
        if health.redis == "healthy":
            assert health.mode == "full"
            assert health.cache_hit_capable is True

    def test_sqlite_only_mode_when_redis_down(self):
        """Mode is 'sqlite_only' when Redis unavailable."""
        svc = ADGService(redis_url="redis://invalid:9999/0")
        health = svc.health()

        assert health.mode == "sqlite_only"
        assert health.sqlite == "healthy"
        assert health.redis == "unavailable"
        assert health.cache_hit_capable is False


class TestHealthWithADGData:
    """Health check includes ADG snapshot info."""

    def test_adg_snapshot_in_health(self):
        """Health report includes ADG snapshot metadata."""
        svc = ADGService()
        health = HealthDiagnostics(svc)

        report = health.full_report()

        assert "adg" in report
        assert report["adg_snapshot_id"] is not None
        assert report["schema_version"] == "1.0"
