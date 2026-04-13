"""Focused regression tests for the ADG MCP fix patch.

Covers exactly the five behavioral invariants introduced by the patch:

  1. ADG_REDIS_URL env override is honoured by ADGService.__init__.
  2. Latest-snapshot-only gate probe ignores stale / corrupt old snapshots.
  3. adg_reload() reports snapshot transition and clears Redis keys for old snapshot.
  4. Redis availability recovers after initial failure (TTL-gated reconnect).
  5. Health full_report() exposes graph_projection availability field.
"""

from __future__ import annotations

import sqlite3
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers shared across tests
# ---------------------------------------------------------------------------

# Inject .windsurf/scripts onto sys.path so pre_mcp_gate is importable, matching
# the pattern used by test_pre_mcp_gate.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".windsurf" / "scripts"))


def _make_sqlite(adg_dir: Path, name: str) -> Path:
    """Create a minimal real SQLite DB that survives a read probe."""
    db_path = adg_dir / name
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS probe (id INTEGER)")
    conn.commit()
    conn.close()
    return db_path


# ---------------------------------------------------------------------------
# Test 1 — ADG_REDIS_URL env override
# ---------------------------------------------------------------------------


class TestRedisUrlEnvOverride:
    def test_env_var_takes_precedence_over_default(self, monkeypatch):
        """ADGService must read ADG_REDIS_URL env before using localhost default."""
        monkeypatch.setenv("ADG_REDIS_URL", "redis://env-host:7777/3")

        mock_sqlite = MagicMock()
        mock_sqlite.get_status.return_value = {"timestamp": "ts_001"}
        mock_sqlite.health.return_value = ("healthy", {})

        with patch("tools.adg.core.service.SQLiteBackend", return_value=mock_sqlite):
            with patch("tools.adg.core.service.RedisCache") as mock_redis_cls:
                mock_redis_cls.return_value._available = False
                from tools.adg.core.service import ADGService

                ADGService()

        mock_redis_cls.assert_called_once_with("redis://env-host:7777/3")

    def test_explicit_arg_used_when_env_absent(self, monkeypatch):
        """When ADG_REDIS_URL is unset, explicit arg wins over localhost default."""
        monkeypatch.delenv("ADG_REDIS_URL", raising=False)

        mock_sqlite = MagicMock()
        mock_sqlite.get_status.return_value = {"timestamp": "ts_002"}
        mock_sqlite.health.return_value = ("healthy", {})

        with patch("tools.adg.core.service.SQLiteBackend", return_value=mock_sqlite):
            with patch("tools.adg.core.service.RedisCache") as mock_redis_cls:
                mock_redis_cls.return_value._available = False
                from tools.adg.core.service import ADGService

                ADGService(redis_url="redis://explicit:1234/0")

        mock_redis_cls.assert_called_once_with("redis://explicit:1234/0")

    def test_localhost_default_when_nothing_set(self, monkeypatch):
        """Fallback to redis://localhost:6379/0 when neither env nor arg provided."""
        monkeypatch.delenv("ADG_REDIS_URL", raising=False)

        mock_sqlite = MagicMock()
        mock_sqlite.get_status.return_value = {"timestamp": "ts_003"}
        mock_sqlite.health.return_value = ("healthy", {})

        with patch("tools.adg.core.service.SQLiteBackend", return_value=mock_sqlite):
            with patch("tools.adg.core.service.RedisCache") as mock_redis_cls:
                mock_redis_cls.return_value._available = False
                from tools.adg.core.service import ADGService

                ADGService()

        mock_redis_cls.assert_called_once_with("redis://localhost:6379/0")

    def test_empty_env_var_falls_through_to_localhost_default(self, monkeypatch):
        """ADG_REDIS_URL='' must fall through to localhost default, not pass '' to RedisCache."""
        monkeypatch.setenv("ADG_REDIS_URL", "")

        mock_sqlite = MagicMock()
        mock_sqlite.get_status.return_value = {"timestamp": "ts_004"}

        with patch("tools.adg.core.service.SQLiteBackend", return_value=mock_sqlite):
            with patch("tools.adg.core.service.RedisCache") as mock_redis_cls:
                mock_redis_cls.return_value._available = False
                from tools.adg.core.service import ADGService

                ADGService()

        mock_redis_cls.assert_called_once_with("redis://localhost:6379/0")


# ---------------------------------------------------------------------------
# Test 2 — Latest-snapshot-only gate probe
# ---------------------------------------------------------------------------


class TestLatestOnlyGateProbe:
    @pytest.fixture(autouse=True)
    def _clear_probe_cache(self):
        import pre_mcp_gate as _gate

        _gate._PROBE_CACHE.clear()
        yield
        _gate._PROBE_CACHE.clear()

    def test_stale_corrupt_old_snapshot_does_not_block(self, tmp_path):
        """Gate must NOT block when old snapshot is corrupt but latest is healthy."""
        from pre_mcp_gate import _check_sqlite_access

        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)

        # Older file — corrupt bytes, would fail a read probe
        old_db = adg / "adg_indexed_20250101_000000.sqlite"
        old_db.write_bytes(b"not a valid sqlite database")

        # Latest file — healthy, sorts after the old one alphabetically
        _make_sqlite(adg, "adg_indexed_20260101_000000.sqlite")

        blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
        assert blocked is False, f"Gate blocked unexpectedly on healthy latest: {reason}"

    def test_corrupt_latest_still_blocks(self, tmp_path):
        """Gate blocks when the LATEST (only probed) snapshot is unreadable."""
        from pre_mcp_gate import _check_sqlite_access

        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)

        # Healthy old file — irrelevant after patch
        _make_sqlite(adg, "adg_indexed_20250101_000000.sqlite")

        # Latest file — corrupt
        latest_db = adg / "adg_indexed_20260101_000000.sqlite"
        latest_db.write_bytes(b"not a valid sqlite database")

        blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
        assert blocked is True
        assert "latest snapshot" in reason

    def test_single_healthy_db_not_blocked(self, tmp_path):
        """Sanity: single healthy DB → gate allows."""
        from pre_mcp_gate import _check_sqlite_access

        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _make_sqlite(adg, "adg_indexed_20260101_000000.sqlite")

        blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
        assert blocked is False


# ---------------------------------------------------------------------------
# Test 3 — adg_reload snapshot transition + Redis clear
# ---------------------------------------------------------------------------


class TestAdgReloadHygiene:
    def _make_mock_service(self, *, old_id: str, new_id: str) -> MagicMock:
        """Build a mock ADGService that simulates a stale-snapshot transition."""
        svc = MagicMock()
        svc._adg_snapshot_id = old_id
        svc._redis._available = True

        # First health() call → stale
        svc._sqlite.health.return_value = (
            "healthy",
            {"is_stale": True, "path": "/old.sqlite", "latest_path": "/new.sqlite"},
        )

        def _reopen_side_effect():
            svc._adg_snapshot_id = new_id
            svc._sqlite.health.return_value = (
                "healthy",
                {"is_stale": False, "path": "/new.sqlite"},
            )

        svc.reopen.side_effect = _reopen_side_effect
        return svc

    def test_reload_clears_old_snapshot_redis_keys(self):
        """adg_reload must call clear_snapshot(old_id) when reload occurs."""
        import tools.adg.mcp.server as server_module

        svc = self._make_mock_service(old_id="snap_old", new_id="snap_new")

        with patch.object(server_module, "_init_service", return_value=svc):
            result = server_module.adg_reload()

        assert result["status"] == "ok"
        assert result["data"]["reloaded"] is True
        assert result["data"]["old_snapshot_id"] == "snap_old"
        assert result["data"]["new_snapshot_id"] == "snap_new"
        assert result["data"]["redis_cleared"] is True
        svc._redis.clear_snapshot.assert_called_once_with("snap_old")

    def test_reload_not_needed_redis_not_touched(self):
        """When already on latest snapshot, clear_snapshot must NOT be called."""
        import tools.adg.mcp.server as server_module

        svc = MagicMock()
        svc._adg_snapshot_id = "snap_current"
        svc._sqlite.health.return_value = (
            "healthy",
            {"is_stale": False, "path": "/current.sqlite"},
        )

        with patch.object(server_module, "_init_service", return_value=svc):
            result = server_module.adg_reload()

        assert result["data"]["reloaded"] is False
        assert result["data"]["redis_cleared"] is False
        svc._redis.clear_snapshot.assert_not_called()

    def test_reload_redis_cleared_false_when_redis_unavailable(self):
        """redis_cleared must be False when Redis is not available."""
        import tools.adg.mcp.server as server_module

        svc = self._make_mock_service(old_id="snap_old", new_id="snap_new")
        svc._redis._available = False  # Redis down

        with patch.object(server_module, "_init_service", return_value=svc):
            result = server_module.adg_reload()

        assert result["data"]["reloaded"] is True
        assert result["data"]["redis_cleared"] is False
        svc._redis.clear_snapshot.assert_not_called()

    def test_reload_redis_cleared_false_when_clear_snapshot_raises(self):
        """clear_snapshot() exception must not prevent reload succeeding — redis_cleared=False."""
        import tools.adg.mcp.server as server_module

        svc = self._make_mock_service(old_id="snap_old", new_id="snap_new")
        svc._redis.clear_snapshot.side_effect = RuntimeError("Redis SCAN failed")

        with patch.object(server_module, "_init_service", return_value=svc):
            result = server_module.adg_reload()

        assert result["status"] == "ok"
        assert result["data"]["reloaded"] is True
        assert result["data"]["redis_cleared"] is False
        assert result["data"]["redis_cache_state"] == "cold"


# ---------------------------------------------------------------------------
# Test 4 — Redis availability recovers without server restart
# ---------------------------------------------------------------------------


class TestRedisAvailabilityRefresh:
    def test_maybe_reconnect_fires_after_backoff_window(self):
        """_maybe_reconnect() must re-probe Redis once the 30s backoff elapses
        and reset consecutive_errors to 0 on successful reconnect."""
        from tools.adg.cache.redis_cache import RedisCache, _RECONNECT_BACKOFF_S

        cache = RedisCache.__new__(RedisCache)
        cache._redis_url = "redis://initially-down:9999/0"
        cache._available = False
        cache._client = None
        cache._consecutive_errors = 3  # non-zero: proves reset fires, not just initial state
        # Place last attempt far enough in the past to trigger reconnect
        cache._last_reconnect_attempt = time.monotonic() - (_RECONNECT_BACKOFF_S + 1)

        # Simulate Redis coming back up on reconnect attempt
        with patch.object(cache, "_attempt_connect", side_effect=lambda: setattr(cache, "_available", True)):
            cache._maybe_reconnect()

        assert cache._available is True
        assert cache._consecutive_errors == 0  # reset fires on successful reconnect

    def test_maybe_reconnect_respects_backoff_window(self):
        """_maybe_reconnect() must NOT re-probe within the backoff window."""
        from tools.adg.cache.redis_cache import RedisCache

        cache = RedisCache.__new__(RedisCache)
        cache._available = False
        cache._client = None
        cache._consecutive_errors = 0
        # Very recent attempt — still within backoff window
        cache._last_reconnect_attempt = time.monotonic() - 1.0

        with patch.object(cache, "_attempt_connect") as mock_connect:
            cache._maybe_reconnect()

        mock_connect.assert_not_called()
        assert cache._available is False

    def test_record_error_marks_unavailable_after_threshold(self):
        """After _MAX_CONSECUTIVE_ERRORS failures, _available becomes False and counter resets to 0."""
        from tools.adg.cache.redis_cache import RedisCache, _MAX_CONSECUTIVE_ERRORS

        cache = RedisCache.__new__(RedisCache)
        cache._available = True
        cache._consecutive_errors = 0

        for _ in range(_MAX_CONSECUTIVE_ERRORS):
            cache._record_error()

        assert cache._available is False
        assert cache._consecutive_errors == 0  # reset fires after marking unavailable

    def test_get_node_calls_maybe_reconnect_when_unavailable(self):
        """get_node must trigger _maybe_reconnect when _available is False."""
        from tools.adg.cache.redis_cache import RedisCache, _RECONNECT_BACKOFF_S

        cache = RedisCache.__new__(RedisCache)
        cache._redis_url = "redis://unused:9999/0"
        cache._available = False
        cache._client = None
        cache._consecutive_errors = 0
        cache._last_reconnect_attempt = time.monotonic() - (_RECONNECT_BACKOFF_S + 1)

        reconnected = []

        def _fake_attempt_connect():
            cache._available = True
            cache._client = MagicMock()
            cache._client.hgetall.return_value = {}
            reconnected.append(True)

        with patch.object(cache, "_attempt_connect", side_effect=_fake_attempt_connect):
            result = cache.get_node("n1", "snap1")

        assert reconnected, "_maybe_reconnect did not fire (no reconnect attempt)"
        # Result is None (cache miss) but connection was re-established
        assert result is None
        assert cache._available is True

    def test_get_nodes_by_layer_exception_increments_consecutive_errors(self):
        """get_nodes_by_layer exception path must call _record_error() (diff-added line)."""
        from tools.adg.cache.redis_cache import RedisCache

        cache = RedisCache.__new__(RedisCache)
        cache._available = True
        cache._client = MagicMock()
        cache._client.get.side_effect = RuntimeError("connection timeout")
        cache._consecutive_errors = 0
        cache._last_reconnect_attempt = 0.0

        result = cache.get_nodes_by_layer("L0", "snap_test")

        assert result is None
        assert cache._consecutive_errors == 1


# ---------------------------------------------------------------------------
# Test 5 — Health report exposes graph projection availability
# ---------------------------------------------------------------------------


class TestHealthGraphProjectionVisibility:
    def _make_service_mock(self, *, proj_available: bool, proj_stale: bool = False) -> MagicMock:
        from tools.adg.core.models import ADGResponse, HealthStatus

        svc = MagicMock()
        svc.health.return_value = HealthStatus(
            mode="sqlite_only",
            sqlite="healthy",
            redis="unavailable",
            cache_hit_capable=False,
            schema_version="1.0",
            adg_snapshot_id="snap_test",
        )
        svc.get_status.return_value = ADGResponse(
            status="ok",
            data={"timestamp": "snap_test", "node_count": 42, "edge_count": 100},
            backend_used="sqlite",
        )
        svc.get_projection_status.return_value = ADGResponse(
            status="ok",
            data={
                "available": proj_available,
                "stale": proj_stale,
                "projection_path": "/path/to/adg_graph.sqlite" if proj_available else None,
            },
            backend_used="sqlite",
        )
        return svc

    def test_full_report_contains_graph_projection_key(self):
        """full_report() must include 'graph_projection' in its response."""
        from tools.adg.mcp.health import HealthDiagnostics

        svc = self._make_service_mock(proj_available=True)
        diag = HealthDiagnostics(svc)
        report = diag.full_report()

        assert "graph_projection" in report

    def test_full_report_projection_available_true(self):
        """full_report() graph_projection.available must reflect projection status."""
        from tools.adg.mcp.health import HealthDiagnostics

        svc = self._make_service_mock(proj_available=True)
        report = HealthDiagnostics(svc).full_report()

        assert report["graph_projection"]["available"] is True
        assert report["graph_projection"]["stale"] is False
        assert report["graph_projection"]["projection_path"] is not None

    def test_full_report_projection_available_false(self):
        """full_report() graph_projection.available=False when no projection built."""
        from tools.adg.mcp.health import HealthDiagnostics

        svc = self._make_service_mock(proj_available=False)
        report = HealthDiagnostics(svc).full_report()

        assert report["graph_projection"]["available"] is False
        assert report["graph_projection"]["projection_path"] is None

    def test_full_report_degrades_gracefully_when_projection_raises(self):
        """full_report() must return degraded graph_projection when get_projection_status() raises."""
        from tools.adg.mcp.health import HealthDiagnostics

        svc = self._make_service_mock(proj_available=True)
        svc.get_projection_status.side_effect = RuntimeError("projection table missing")

        report = HealthDiagnostics(svc).full_report()

        assert "graph_projection" in report
        assert report["graph_projection"]["available"] is False
        assert report["graph_projection"]["projection_path"] is None


# ---------------------------------------------------------------------------
# Test 6 — Silent degraded fallback detection in post_cascade_adg_audit.py
# ---------------------------------------------------------------------------


class TestSilentDegradedFallbackDetection:
    """Verify the audit correctly grades severity based on health-first compliance."""

    @staticmethod
    def _get_detect_violations():
        import sys
        from pathlib import Path

        scripts_dir = str(Path(__file__).resolve().parents[4] / ".windsurf" / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from post_cascade_adg_audit import detect_violations

        return detect_violations

    def test_silent_fallback_grades_critical(self):
        """grep-for-deps with no ADG, no health check, no reason code → severity: critical."""
        detect_violations = self._get_detect_violations()
        response = "grep_search imports from redis_cache.py in *.py files"
        violations = detect_violations(response)
        assert violations, "expected at least one violation"
        assert violations[0]["severity"] == "critical"
        assert violations[0]["silent_fallback"] is True

    def test_fallback_with_health_check_grades_error(self):
        """grep-for-deps after mcp1_adg_health was called but no DEGRADED_FALLBACK → severity: error."""
        detect_violations = self._get_detect_violations()
        response = "mcp1_adg_health() returned red. grep_search imports from redis_cache.py in *.py files"
        violations = detect_violations(response)
        assert violations, "expected at least one violation"
        assert violations[0]["severity"] == "error"
        assert violations[0]["adg_health_checked"] is True
        assert violations[0]["silent_fallback"] is False

    def test_fallback_with_degraded_marker_grades_error(self):
        """grep-for-deps with DEGRADED_FALLBACK: reason=adg_red → severity: error (partial compliance)."""
        detect_violations = self._get_detect_violations()
        response = "DEGRADED_FALLBACK: reason=adg_red\ngrep_search imports from redis_cache.py in *.py files"
        violations = detect_violations(response)
        assert violations, "expected at least one violation"
        assert violations[0]["severity"] == "error"
        assert violations[0]["degraded_fallback_declared"] is True
        assert violations[0]["silent_fallback"] is False

    def test_adg_mcp_also_used_grades_warning(self):
        """grep-for-deps alongside mcp1_adg_edge_fanin → severity: warning (supplementary)."""
        detect_violations = self._get_detect_violations()
        response = (
            "mcp1_adg_edge_fanin(tgt_id='redis_cache', relation_type='imports') returned results. "
            "grep_search imports from redis_cache.py in *.py files"
        )
        violations = detect_violations(response)
        assert violations, "expected at least one violation"
        assert violations[0]["severity"] == "warning"
        assert violations[0]["adg_mcp_also_used"] is True

    def test_literal_grep_no_violation(self):
        """grep for TODO comments must not trigger a violation."""
        detect_violations = self._get_detect_violations()
        response = 'grep_search Query: "TODO" in tests/'
        violations = detect_violations(response)
        assert violations == [], f"unexpected violations for literal grep: {violations}"

    def test_adg_mcp_used_wins_when_health_also_checked(self):
        """adg_mcp_used=True takes precedence over adg_health_checked=True → severity: warning."""
        detect_violations = self._get_detect_violations()
        response = (
            "mcp1_adg_health() called. mcp1_adg_edge_fanin returned results. "
            "grep_search imports from redis_cache.py in *.py files"
        )
        violations = detect_violations(response)
        assert violations, "expected at least one violation"
        assert violations[0]["severity"] == "warning"
        assert violations[0]["adg_mcp_also_used"] is True
        assert violations[0]["adg_health_checked"] is True
        assert violations[0]["silent_fallback"] is False


# ---------------------------------------------------------------------------
# Test 7 — adg_close_connections / adg_reopen_connections MCP tool lifecycle
# ---------------------------------------------------------------------------


class TestCloseReopenLifecycle:
    """Validate B3/B4: close_connections releases the service; reopen_connections
    creates a fresh one.  These prove the operator-clear semantics documented in
    OPERATIONS.md (ADG generation lock-release workflow)."""

    def test_close_connections_when_service_active(self):
        """adg_close_connections() must call service.close(), set _service=None,
        and return closed=True."""
        import tools.adg.mcp.server as server_module

        mock_svc = MagicMock()
        original_service = server_module._service
        original_health = server_module._health
        try:
            server_module._service = mock_svc
            server_module._health = MagicMock()

            result = server_module.adg_close_connections()

        finally:
            # Restore module-level globals so other tests are not affected
            server_module._service = original_service
            server_module._health = original_health

        assert result["status"] == "ok"
        assert result["data"]["closed"] is True
        mock_svc.close.assert_called_once()

    def test_close_connections_when_no_service(self):
        """adg_close_connections() when _service is already None must return
        closed=False without raising."""
        import tools.adg.mcp.server as server_module

        original_service = server_module._service
        original_health = server_module._health
        try:
            server_module._service = None
            server_module._health = None

            result = server_module.adg_close_connections()

        finally:
            server_module._service = original_service
            server_module._health = original_health

        assert result["status"] == "ok"
        assert result["data"]["closed"] is False

    def test_reopen_connections_initializes_service(self):
        """adg_reopen_connections() must call _init_service() and svc.reopen(),
        and return reopened=True."""
        import tools.adg.mcp.server as server_module

        mock_svc = MagicMock()
        with patch.object(server_module, "_init_service", return_value=mock_svc):
            result = server_module.adg_reopen_connections()

        assert result["status"] == "ok"
        assert result["data"]["reopened"] is True
        mock_svc.reopen.assert_called_once()

    def test_close_then_reopen_roundtrip(self):
        """Full operator workflow: close releases service; reopen creates a new one."""
        import tools.adg.mcp.server as server_module

        mock_svc = MagicMock()
        original_service = server_module._service
        original_health = server_module._health
        try:
            server_module._service = mock_svc
            server_module._health = MagicMock()

            close_result = server_module.adg_close_connections()
            assert close_result["data"]["closed"] is True
            # Service must be torn down after close
            assert server_module._service is None

            # Now reopen
            fresh_svc = MagicMock()
            with patch.object(server_module, "_init_service", return_value=fresh_svc):
                reopen_result = server_module.adg_reopen_connections()

            assert reopen_result["data"]["reopened"] is True
            fresh_svc.reopen.assert_called_once()

        finally:
            server_module._service = original_service
            server_module._health = original_health
