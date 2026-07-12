"""Fail-closed consumer-state contracts for authoritative ADG queries."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tools.adg.core.graph_projection_backend import (
    ProjectionStaleError,
    ProjectionUnavailableError,
)
from tools.adg.core.models import ADGResponse, QueryMeta
from tools.adg.core.service import ADGService
from tools.adg.core.sqlite_backend import SQLiteBackend


def _service() -> tuple[ADGService, MagicMock]:
    service = object.__new__(ADGService)
    backend = MagicMock()
    backend.get_status.return_value = {
        "artifact_digest": "certified-digest",
        "schema_version": "4.0.0",
    }
    backend.get_projection_status.return_value = {
        "available": False,
        "stale": False,
        "result_state": "UNAVAILABLE",
        "source_artifact_digest": None,
        "proj_schema_version": "1.2",
    }
    service._sqlite = backend
    service._adg_snapshot_id = "certified-digest:canonical-4.0.0"
    return service, backend


def test_unavailable_blast_radius_never_substitutes_zero() -> None:
    service, backend = _service()
    backend.get_blast_radius.side_effect = ProjectionUnavailableError(
        "projection missing"
    )

    response = service.get_blast_radius("module")

    assert response.status == "error"
    assert response.query_meta.result_state == "UNAVAILABLE"
    assert response.query_meta.selected_artifact_digest == "certified-digest"
    assert response.data["blast_radius_direct"] is None
    assert response.data["blast_radius_2hop"] is None
    assert response.data["reachability_rows"] is None


def test_stale_projection_is_not_empty() -> None:
    service, backend = _service()
    backend.get_projection_status.return_value.update(
        {
            "available": True,
            "stale": True,
            "result_state": "STALE",
            "source_artifact_digest": "repair-digest",
        }
    )
    backend.get_reachability.side_effect = ProjectionStaleError(
        "digest mismatch"
    )

    response = service.get_reachability("module")

    assert response.status == "error"
    assert response.query_meta.result_state == "STALE"
    assert response.data["reachability"] is None
    assert response.data["count"] is None


def test_fresh_absent_scc_is_typed_empty() -> None:
    service, backend = _service()
    backend.get_projection_status.return_value.update(
        {
            "available": True,
            "result_state": "COMPLETE",
            "source_artifact_digest": "certified-digest",
        }
    )
    backend.get_scc.return_value = None

    response = service.get_scc("module")

    assert response.status == "ok"
    assert response.query_meta.result_state == "EMPTY"
    assert response.data == {"adg_name": "module", "scc": None}


def test_sqlite_backend_rejects_missing_projection() -> None:
    backend = object.__new__(SQLiteBackend)
    backend._graph_store = None

    with pytest.raises(ProjectionUnavailableError):
        backend.get_blast_radius("module")


def test_mcp_serializer_forwards_query_metadata() -> None:
    from tools.adg.mcp import tool_handlers

    response = ADGResponse(
        status="ok",
        data={"adg_name": "module", "scc": None},
        backend_used="projection",
        query_meta=QueryMeta(
            result_state="EMPTY",
            selected_artifact_digest="certified-digest",
        ),
    )
    service = MagicMock()
    service.get_scc.return_value = response

    with patch.object(tool_handlers.runtime, "_service", service):
        result = tool_handlers.adg_scc("module")

    assert result["query_meta"]["result_state"] == "EMPTY"
    assert (
        result["query_meta"]["selected_artifact_digest"]
        == "certified-digest"
    )
