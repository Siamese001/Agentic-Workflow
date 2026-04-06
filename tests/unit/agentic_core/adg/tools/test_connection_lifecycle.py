"""Connection lifecycle tests for ADG no-restart lock release tools."""

from unittest.mock import Mock

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


class TestADGServiceReopen:
    """Service reopen forwards to sqlite backend."""

    def test_reopen_forwards_to_sqlite_backend(self):
        svc = object.__new__(ADGService)
        sqlite = Mock()
        svc._sqlite = sqlite

        ADGService.reopen(svc)

        sqlite.reopen.assert_called_once()


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
