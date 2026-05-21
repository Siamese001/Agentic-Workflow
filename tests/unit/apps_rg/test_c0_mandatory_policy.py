"""apps_rg mandatory C0.2 dense+sparse and C0.3 graph policy."""

from __future__ import annotations

import pytest

from apps_rg.runtime.c0_mandatory_policy import (
    C03_MANDATORY_SECTIONS,
    apps_rg_c0_dense_sparse_mandatory,
    apps_rg_c0_sparse_profile_enabled,
    apps_rg_c03_graph_mandatory,
    is_c03_mandatory_section,
)
from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError, c0_retrieve_apps_rg
from apps_rg.runtime.embedding_settings import bootstrap_apps_rg_embedding_env
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.route_contract import RouteContract


def _route() -> RouteContract:
    r = RouteContract.__new__(RouteContract)
    object.__setattr__(r, "grounding_required", True)
    object.__setattr__(r, "request_id", "mandatory-req")
    object.__setattr__(r, "run_id", "mandatory-run")
    object.__setattr__(r, "app_id", "apps_rg")
    object.__setattr__(r, "trace_id", "mandatory-trace")
    return r


def _validated() -> ValidatedRequest:
    vr = ValidatedRequest.__new__(ValidatedRequest)
    object.__setattr__(vr, "request_id", "mandatory-req")
    object.__setattr__(vr, "run_id", "mandatory-run")
    object.__setattr__(vr, "app_id", "apps_rg")
    object.__setattr__(vr, "trace_id", "mandatory-trace")
    object.__setattr__(vr, "app_payload", {"jd_payload": {"jd_text": "x"}, "resume_payload": {}})
    return vr


def test_bootstrap_sets_mandatory_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "APPS_RG_C0_DENSE_SPARSE_MANDATORY",
        "APPS_RG_C03_GRAPH_MANDATORY",
        "APPS_RG_C0_SPARSE_ENABLED",
    ):
        monkeypatch.delenv(key, raising=False)
    bootstrap_apps_rg_embedding_env()
    assert apps_rg_c0_dense_sparse_mandatory()
    assert apps_rg_c03_graph_mandatory()
    assert apps_rg_c0_sparse_profile_enabled()


def test_c03_mandatory_covers_all_generated_lanes() -> None:
    from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

    assert set(GENERATED_LANES) == set(C03_MANDATORY_SECTIONS)
    assert is_c03_mandatory_section("headline")


def test_dense_sparse_mandatory_requires_chroma(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_C0_DENSE_SPARSE_MANDATORY", "1")
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    with pytest.raises(C0EvidenceGapError, match="CHROMA_PERSIST_DIR"):
        c0_retrieve_apps_rg(_route(), _validated(), chromadb_path=None)
