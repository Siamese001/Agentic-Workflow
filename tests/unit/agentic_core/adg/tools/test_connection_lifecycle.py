"""Connection lifecycle tests for ADG no-restart lock release tools."""

from unittest.mock import Mock

import pytest

from tools.adg.core.service import ADGService
from tools.adg.core.sqlite_backend import SQLiteBackend
from tools.adg.mcp import server as mcp_server


class TestSQLiteBackendReopen:
    """SQLite backend reopen lifecycle behavior."""

    def test_reopen_closes_then_connects_when_conn_exists(self):
        backend = object.__new__(SQLiteBackend)
        backend._conn = object()  # Simulate active connection
        backend.close = Mock()
        backend._connect = Mock()

        SQLiteBackend.reopen(backend)

        backend.close.assert_called_once()
        backend._connect.assert_called_once()

    def test_reopen_connects_when_no_conn_exists(self):
        backend = object.__new__(SQLiteBackend)
        backend._conn = None
        backend.close = Mock()
        backend._connect = Mock()

        SQLiteBackend.reopen(backend)

        backend.close.assert_not_called()
        backend._connect.assert_called_once()

    def test_reopen_failure_path_on_connect_error(self):
        """Verify reopen propagates _connect failure."""
        backend = object.__new__(SQLiteBackend)
        backend._conn = object()
        backend.close = Mock()
        backend._connect = Mock(side_effect=RuntimeError("Connect failed"))

        with pytest.raises(RuntimeError, match="Connect failed"):
            SQLiteBackend.reopen(backend)

        backend.close.assert_called_once()


class TestADGServiceReopen:
    """Service reopen forwards to sqlite backend."""

    def test_reopen_forwards_to_sqlite_backend(self):
        svc = object.__new__(ADGService)
        sqlite = Mock()
        svc._sqlite = sqlite

        ADGService.reopen(svc)

        sqlite.reopen.assert_called_once()

    def test_reopen_skips_when_sqlite_none(self):
        """Verify reopen gracefully handles None _sqlite."""
        svc = object.__new__(ADGService)
        svc._sqlite = None

        # Should not raise
        ADGService.reopen(svc)


class TestMCPConnectionLifecycleTools:
    """MCP tools expose close/reopen lifecycle without IDE restart."""

    def test_adg_close_connections_no_active_service(self):
        original_service = mcp_server._service
        original_health = mcp_server._health
        try:
            mcp_server._service = None
            mcp_server._health = None

            response = mcp_server.adg_close_connections()

            assert response["status"] == "ok"
            assert response["data"]["closed"] is False
        finally:
            mcp_server._service = original_service
            mcp_server._health = original_health

    def test_adg_close_connections_closes_active_service(self):
        original_service = mcp_server._service
        original_health = mcp_server._health

        class DummyService:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        dummy = DummyService()

        try:
            mcp_server._service = dummy
            mcp_server._health = object()

            response = mcp_server.adg_close_connections()

            assert response["status"] == "ok"
            assert response["data"]["closed"] is True
            assert dummy.closed is True
            assert mcp_server._service is None
            assert mcp_server._health is None
        finally:
            mcp_server._service = original_service
            mcp_server._health = original_health

    def test_adg_reopen_connections_reopens_service(self):
        original_init_service = mcp_server._init_service

        class DummyService:
            def __init__(self):
                self.reopened = False

            def reopen(self):
                self.reopened = True

        dummy = DummyService()

        try:
            mcp_server._init_service = lambda: dummy

            response = mcp_server.adg_reopen_connections()

            assert response["status"] == "ok"
            assert response["data"]["reopened"] is True
            assert dummy.reopened is True
        finally:
            mcp_server._init_service = original_init_service

    def test_adg_close_connections_exception_path(self):
        """Verify close_connections handles close() exception gracefully."""
        original_service = mcp_server._service
        original_health = mcp_server._health

        class FailingService:
            def close(self):
                raise RuntimeError("Close failed")

        failing = FailingService()

        try:
            mcp_server._service = failing
            mcp_server._health = object()

            response = mcp_server.adg_close_connections()

            assert response["status"] == "error"
            assert "Close failed" in response["message"]
        finally:
            mcp_server._service = original_service
            mcp_server._health = original_health

    def test_adg_reopen_connections_exception_path(self):
        """Verify reopen_connections handles _init_service exception gracefully."""
        original_init_service = mcp_server._init_service

        try:
            mcp_server._init_service = lambda: (_ for _ in ()).throw(RuntimeError("Init failed"))

            response = mcp_server.adg_reopen_connections()

            assert response["status"] == "error"
            assert "Init failed" in response["message"]
        finally:
            mcp_server._init_service = original_init_service

    def test_adg_close_connections_state_consistency(self):
        """Verify close_connections resets service and health to None."""
        original_service = mcp_server._service
        original_health = mcp_server._health

        class DummyService:
            def close(self):
                pass

        dummy = DummyService()

        try:
            mcp_server._service = dummy
            mcp_server._health = object()

            mcp_server.adg_close_connections()

            assert mcp_server._service is None
            assert mcp_server._health is None
        finally:
            mcp_server._service = original_service
            mcp_server._health = original_health
