"""Focused regression tests for the ADG MCP fix patch.

Covers exactly the five behavioral invariants introduced by the patch:

  1. ADG_REDIS_URL env override is honoured by ADGService.__init__.
  2. Latest-snapshot-only gate probe ignores stale / corrupt old snapshots.
  3. adg_reload() reports snapshot transition and clears Redis keys for old snapshot.
  4. Redis availability recovers after initial failure (TTL-gated reconnect).
  5. Health full_report() exposes graph_projection availability field.
"""

from __future__ import annotations

import importlib
import sqlite3
import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers shared across tests
# ---------------------------------------------------------------------------

# Inject .codex/governance/scripts onto sys.path so pre_mcp_gate is importable, matching
# the pattern used by test_pre_mcp_gate.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".codex" / "governance/scripts"))


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

    def test_sqlite_only_mode_when_nothing_set(self, monkeypatch):
        """When neither env nor arg is provided, Redis is skipped instead of defaulting localhost."""
        monkeypatch.delenv("ADG_REDIS_URL", raising=False)

        mock_sqlite = MagicMock()
        mock_sqlite.get_status.return_value = {"timestamp": "ts_003"}
        mock_sqlite.health.return_value = ("healthy", {})

        with patch("tools.adg.core.service.SQLiteBackend", return_value=mock_sqlite):
            with patch("tools.adg.core.service.RedisCache") as mock_redis_cls:
                mock_redis_cls.return_value._available = False
                from tools.adg.core.service import ADGService

                service = ADGService()

        mock_redis_cls.assert_not_called()
        assert service.health().mode == "sqlite_only"

    def test_empty_env_var_uses_sqlite_only_mode(self, monkeypatch):
        """ADG_REDIS_URL='' must not pass '' to RedisCache or collapse service startup."""
        monkeypatch.setenv("ADG_REDIS_URL", "")

        mock_sqlite = MagicMock()
        mock_sqlite.get_status.return_value = {"timestamp": "ts_004"}
        mock_sqlite.health.return_value = ("healthy", {})

        with patch("tools.adg.core.service.SQLiteBackend", return_value=mock_sqlite):
            with patch("tools.adg.core.service.RedisCache") as mock_redis_cls:
                mock_redis_cls.return_value._available = False
                from tools.adg.core.service import ADGService

                service = ADGService()

        mock_redis_cls.assert_not_called()
        assert service.health().redis == "unavailable"

    def test_unexpanded_env_placeholder_uses_sqlite_only_mode(self, monkeypatch):
        """Literal MCP placeholders must not be treated as Redis URLs."""
        monkeypatch.setenv("ADG_REDIS_URL", "${ADG_REDIS_URL}")

        mock_sqlite = MagicMock()
        mock_sqlite.get_status.return_value = {"timestamp": "ts_005"}
        mock_sqlite.health.return_value = ("healthy", {})

        with patch("tools.adg.core.service.SQLiteBackend", return_value=mock_sqlite):
            with patch("tools.adg.core.service.RedisCache") as mock_redis_cls:
                from tools.adg.core.service import ADGService

                service = ADGService()

        mock_redis_cls.assert_not_called()
        assert service.health().mode == "sqlite_only"

    def test_redis_cache_rejects_unexpanded_placeholder_before_client_connect(self, monkeypatch):
        """RedisCache must not pass literal MCP placeholders to redis.from_url."""
        monkeypatch.setenv("ADG_REDIS_URL", "${ADG_REDIS_URL}")

        with patch("tools.adg.cache.redis_cache.redis.from_url") as mock_from_url:
            from tools.adg.cache.redis_cache import RedisCache

            with pytest.raises(RuntimeError):
                RedisCache()

        mock_from_url.assert_not_called()


# ---------------------------------------------------------------------------
# Test 2 — Latest-snapshot-only gate probe
# ---------------------------------------------------------------------------


class TestLatestOnlyGateProbe:
    @pytest.fixture(autouse=True)
    def _clear_probe_cache(self):
        import pre_mcp_gate as _gate

        cache = getattr(_gate, "_PROBE_CACHE", None)
        if cache is not None:
            cache.clear()
        yield
        if cache is not None:
            cache.clear()

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


def _load_adg_server_module():
    """Import the server with an identity-decorator MCP test transport."""
    fake_mcp = MagicMock()
    fake_mcp.tool.side_effect = lambda *args, **kwargs: (
        lambda function: function
    )
    with patch(
        "tools.mcp.mcp_bootstrap.create_mcp_server",
        return_value=fake_mcp,
    ):
        return importlib.import_module("tools.adg.mcp.server")


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
        server_module = _load_adg_server_module()

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
        server_module = _load_adg_server_module()

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
        server_module = _load_adg_server_module()

        svc = self._make_mock_service(old_id="snap_old", new_id="snap_new")
        svc._redis._available = False  # Redis down

        with patch.object(server_module, "_init_service", return_value=svc):
            result = server_module.adg_reload()

        assert result["data"]["reloaded"] is True
        assert result["data"]["redis_cleared"] is False
        svc._redis.clear_snapshot.assert_not_called()

    def test_reload_redis_cleared_false_when_clear_snapshot_raises(self):
        """clear_snapshot() exception must not prevent reload succeeding — redis_cleared=False."""
        server_module = _load_adg_server_module()

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
    def test_hset_mapping_uses_single_field_hset_calls(self):
        """Redis 3 rejects multi-field HSET; cache writes must stay compatible."""
        from tools.adg.cache.redis_cache import RedisCache

        target = MagicMock()

        RedisCache._hset_mapping(target, "hash-key", {"a": 1, "b": 2})

        assert target.hset.call_args_list == [
            call("hash-key", "a", "__json__:1"),
            call("hash-key", "b", "__json__:2"),
        ]

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


class TestViewsMaterializedAt:
    """Regression f7ece2e937: health surfaces views_materialized_at from P-view presence."""

    def test_any_single_view_no_longer_satisfies_materialization(self, tmp_path: Path) -> None:
        db_path = tmp_path / "adg_indexed_20260611_120000.sqlite"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE VIEW mv_test_probe AS SELECT 1 AS ok")
        conn.commit()

        from tools.adg.core.sqlite_backend import SQLiteBackend

        backend = SQLiteBackend.__new__(SQLiteBackend)
        backend._lifecycle_lock = threading.RLock()
        backend._conn = conn
        backend._sqlite_path = db_path
        assert backend.get_views_materialized_at() is None
        assert backend.get_materialization_status()["status"] == "FAIL"

    def test_complete_materialization_families_return_snapshot_stem(
        self,
        tmp_path: Path,
    ) -> None:
        db_path = tmp_path / "adg_indexed_20260611_120000.sqlite"
        conn = sqlite3.connect(str(db_path))
        for index in range(30):
            conn.execute(
                f"CREATE TABLE mv_contract_{index} (id INTEGER)"
            )
        for index in range(3):
            conn.execute(
                f"CREATE VIEW v_p0_contract_{index} AS SELECT 1 AS ok"
            )
        conn.execute("CREATE TABLE infrastructure_wiring (id INTEGER)")
        conn.commit()

        from tools.adg.core.sqlite_backend import SQLiteBackend

        backend = SQLiteBackend.__new__(SQLiteBackend)
        backend._lifecycle_lock = threading.RLock()
        backend._conn = conn
        backend._sqlite_path = db_path
        assert (
            backend.get_views_materialized_at()
            == "20260611_120000"
        )

    def test_get_views_materialized_at_none_without_views(self, tmp_path: Path) -> None:
        db_path = tmp_path / "adg_indexed_20260611_120000.sqlite"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE nodes (id INTEGER)")
        conn.commit()

        from tools.adg.core.sqlite_backend import SQLiteBackend

        backend = SQLiteBackend.__new__(SQLiteBackend)
        backend._lifecycle_lock = threading.RLock()
        backend._conn = conn
        backend._sqlite_path = db_path
        assert backend.get_views_materialized_at() is None

    def test_health_report_includes_views_materialized_at(self) -> None:
        from tools.adg.core.models import ADGResponse, HealthStatus
        from tools.adg.mcp.health import HealthDiagnostics

        svc = MagicMock()
        svc.health.return_value = HealthStatus(
            mode="sqlite_only",
            sqlite="healthy",
            redis="unavailable",
            cache_hit_capable=False,
            schema_version="1.0",
            adg_snapshot_id="20260611_120000",
            views_materialized_at="20260611_120000",
        )
        svc.get_status.return_value = ADGResponse(
            status="ok",
            data={"timestamp": "20260611_120000", "node_count": 1, "edge_count": 0},
            backend_used="sqlite",
        )
        svc.get_projection_status.return_value = ADGResponse(
            status="ok",
            data={"available": False, "stale": False, "projection_path": None},
            backend_used="sqlite",
        )

        report = HealthDiagnostics(svc).full_report()
        assert report["views_materialized_at"] == "20260611_120000"

    def test_service_health_filters_non_string_views_materialized_at(self) -> None:
        """Pydantic v2 rejects MagicMock; service must coerce non-str to None."""
        mock_sqlite = MagicMock()
        mock_sqlite.get_status.return_value = {"timestamp": "ts_006"}
        mock_sqlite.health.return_value = ("healthy", {})
        mock_sqlite.get_views_materialized_at.return_value = MagicMock()

        with patch("tools.adg.core.service.SQLiteBackend", return_value=mock_sqlite):
            with patch("tools.adg.core.service.RedisCache") as mock_redis_cls:
                mock_redis_cls.return_value._available = False
                from tools.adg.core.service import ADGService

                health = ADGService().health()

        assert health.views_materialized_at is None


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


class TestToolHandlersAutoReload:
    """Ensure health/status surfaces auto-reload stale snapshot state."""

    def test_adg_health_invokes_runtime_reload_first(self):
        from tools.adg.mcp import tool_handlers

        with patch.object(
            tool_handlers.runtime, "reload_latest_snapshot", return_value={"status": "ok"}
        ) as reload_mock:
            with patch.object(
                tool_handlers.runtime.diagnostics,
                "full_report",
                return_value={"adg_snapshot_id": "04192026_0657"},
            ):
                result = tool_handlers.adg_health()

        reload_mock.assert_called_once()
        assert result["status"] == "ok"
        assert result["data"]["adg_snapshot_id"] == "04192026_0657"

    def test_adg_status_invokes_runtime_reload_first(self):
        from tools.adg.mcp import tool_handlers
        from tools.adg.core.models import ADGResponse

        response = ADGResponse(
            status="ok",
            data={
                "timestamp": "04192026_0657",
                "sqlite_path": "artifacts/adg/adg_indexed_04192026_0657.sqlite",
            },
            backend_used="sqlite",
        )
        with patch.object(
            tool_handlers.runtime, "reload_latest_snapshot", return_value={"status": "ok"}
        ) as reload_mock:
            with patch.object(tool_handlers.runtime.service, "get_status", return_value=response):
                result = tool_handlers.adg_status()

        reload_mock.assert_called_once()
        assert result["status"] == "ok"
        assert result["data"]["timestamp"] == "04192026_0657"


# ---------------------------------------------------------------------------
# Test 6 — Silent degraded fallback detection in post_agent_adg_audit.py
# ---------------------------------------------------------------------------


class TestSilentDegradedFallbackDetection:
    """Verify the audit correctly grades severity based on health-first compliance."""

    @staticmethod
    def _get_detect_violations():
        import sys
        from pathlib import Path

        scripts_dir = str(Path(__file__).resolve().parents[4] / ".codex" / "governance/scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from post_agent_adg_audit import detect_violations

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

    def test_cursor_grep_without_adg_grades_critical_when_snapshot_present(self, monkeypatch):
        """Cursor native Grep for imports with no ADG → critical when snapshot exists."""
        detect_violations = self._get_detect_violations()
        monkeypatch.setattr(
            "post_agent_adg_audit._adg_snapshot_available",
            lambda: True,
        )
        response = 'CallMcpTool Grep pattern="from apps_rg import" glob="*.py"'
        violations = detect_violations(response)
        assert violations, "expected violation for Cursor Grep dep analysis"
        assert violations[0]["severity"] == "critical"

    def test_cursor_adg_sqlite_mitigates_grep_to_warning(self, monkeypatch):
        """adg_sqlite MCP usage alongside Grep → warning not critical."""
        detect_violations = self._get_detect_violations()
        monkeypatch.setattr(
            "post_agent_adg_audit._adg_snapshot_available",
            lambda: True,
        )
        response = (
            'server: "adg_sqlite" toolName: "adg_nodes_by_file" '
            'Grep pattern="import redis_cache" glob="**/*.py"'
        )
        violations = detect_violations(response)
        assert violations, "expected supplementary grep violation"
        assert violations[0]["severity"] == "warning"
        assert violations[0]["adg_mcp_also_used"] is True


# ---------------------------------------------------------------------------
# Test 7 — adg_close_connections / adg_reopen_connections MCP tool lifecycle
# ---------------------------------------------------------------------------


class TestCloseReopenLifecycle:
    """Validate B3/B4: close_connections releases the service; reopen_connections
    creates a fresh one. Proves the operator-clear semantics documented in
    OPERATIONS.md (ADG generation lock-release workflow).

    Wave-7 refresh (2026-04-24): the four tests below were rewritten after
    the runtime-class refactor moved state from module-level
    ``server._service`` / ``_init_service`` to ``ADGServerRuntime`` on
    ``tool_handlers.runtime``. The prior tests ``AttributeError``-ed
    because those module-level symbols no longer exist.
    """

    def test_close_connections_when_service_active(self):
        """runtime.close_connections() must call service.close(), clear
        ``_service``, and return closed=True."""
        from tools.adg.mcp import tool_handlers

        runtime = tool_handlers.runtime
        mock_svc = MagicMock()
        original_service = runtime._service
        original_health = runtime._health
        try:
            runtime._service = mock_svc
            runtime._health = MagicMock()

            result = runtime.close_connections()

            assert result["status"] == "ok"
            assert result["data"]["closed"] is True
            mock_svc.close.assert_called_once()
            # Post-close: service is fully torn down.
            assert runtime._service is None
            assert runtime._health is None
        finally:
            runtime._service = original_service
            runtime._health = original_health

    def test_close_connections_when_no_service(self):
        """runtime.close_connections() when ``_service`` is already None
        must return closed=False without raising."""
        from tools.adg.mcp import tool_handlers

        runtime = tool_handlers.runtime
        original_service = runtime._service
        original_health = runtime._health
        try:
            runtime._service = None
            runtime._health = None

            result = runtime.close_connections()

            assert result["status"] == "ok"
            assert result["data"]["closed"] is False
        finally:
            runtime._service = original_service
            runtime._health = original_health

    def test_reopen_connections_calls_service_reopen(self):
        """runtime.reopen_connections() must invoke service.reopen() and
        return reopened=True. Also covers the F4 (W2.2) idempotency fast-path:
        when the stubbed sqlite backend reports snapshot/mtime drift, the
        slow path runs and ``reopen`` is called.
        """
        from tools.adg.mcp import tool_handlers

        runtime = tool_handlers.runtime
        mock_svc = MagicMock()
        # No _sqlite attr → idempotency check falls through to the slow path.
        mock_svc._sqlite = None
        original_service = runtime._service
        original_health = runtime._health
        try:
            runtime._service = mock_svc
            runtime._health = MagicMock()

            result = runtime.reopen_connections(timeout_s=5.0)

            assert result["status"] == "ok"
            assert result["data"]["reopened"] is True
            assert result["data"]["noop"] is False
            mock_svc.reopen.assert_called_once()
        finally:
            runtime._service = original_service
            runtime._health = original_health

    def test_close_then_reopen_roundtrip(self):
        """Full operator workflow: close releases service; reopen restores it."""
        from tools.adg.mcp import tool_handlers

        runtime = tool_handlers.runtime
        mock_svc = MagicMock()
        original_service = runtime._service
        original_health = runtime._health
        try:
            runtime._service = mock_svc
            runtime._health = MagicMock()

            close_result = runtime.close_connections()
            assert close_result["data"]["closed"] is True
            # Post-close: service torn down.
            assert runtime._service is None

            # Reopen: install a fresh stub, drive the reopen path.
            fresh_svc = MagicMock()
            fresh_svc._sqlite = None  # force slow path, skip idempotency
            runtime._service = fresh_svc

            reopen_result = runtime.reopen_connections(timeout_s=5.0)
            assert reopen_result["data"]["reopened"] is True
            fresh_svc.reopen.assert_called_once()
        finally:
            runtime._service = original_service
            runtime._health = original_health
