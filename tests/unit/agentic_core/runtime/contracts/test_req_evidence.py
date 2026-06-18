"""Unit tests for agentic_core/runtime/contracts/req_evidence.py.

REQ evidence emission is the runtime seam that binds call sites to requirement IDs
for the OTEL lifecycle bridge and coverage ledger. Silent no-ops or wrong logger
channels would break bidirectional REQ traceability across all governed apps.
"""
from __future__ import annotations

import logging

import pytest

from agentic_core.runtime.contracts import req_evidence as mod
from agentic_core.runtime.contracts.req_evidence import (
    emit_anti_bypass_observation,
    emit_req_evidence,
    install_and_tag,
)


class _CaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_emit_req_evidence_empty_iterable_is_noop() -> None:
    handler = _CaptureHandler()
    logger = logging.getLogger("adg.anti_bypass_observation")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        emit_req_evidence((), layer="L6_OBSERVABILITY", edge_kind="anti_bypass_observation")
        emit_req_evidence(["", None], layer="L6_OBSERVABILITY", edge_kind="anti_bypass_observation")  # type: ignore[list-item]
        assert handler.records == []
    finally:
        logger.removeHandler(handler)


def test_emit_req_evidence_logs_on_edge_kind_logger() -> None:
    handler = _CaptureHandler()
    edge = "route_contract_telemetry"
    logger = logging.getLogger(f"adg.{edge}")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        emit_req_evidence(
            ("REQ-L0-ROUTECONTRACT-TELEMETRY-001", "REQ-L0-ROUTECONTRACT-TELEMETRY-002"),
            layer="L0_ROUTING",
            edge_kind=edge,
            op="apps_rg.main",
            root_trace_id="trace-abc",
        )
        assert len(handler.records) == 1
        msg = handler.records[0].getMessage()
        assert "req_ids=REQ-L0-ROUTECONTRACT-TELEMETRY-001,REQ-L0-ROUTECONTRACT-TELEMETRY-002" in msg
        assert "layer=L0_ROUTING" in msg
        assert "edge_kind=route_contract_telemetry" in msg
        assert "op=apps_rg.main" in msg
        assert "root_trace_id=trace-abc" in msg
    finally:
        logger.removeHandler(handler)


def test_emit_anti_bypass_observation_uses_priority_req() -> None:
    handler = _CaptureHandler()
    logger = logging.getLogger("adg.anti_bypass_observation")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        emit_anti_bypass_observation("apps_eval.scripts.run_eval", root_trace_id="t1")
        assert len(handler.records) == 1
        assert "REQ-L6-OBS-ANTI-BYPASS-001" in handler.records[0].getMessage()
        assert "layer=L6_OBSERVABILITY" in handler.records[0].getMessage()
    finally:
        logger.removeHandler(handler)


def test_install_and_tag_returns_none_when_bridge_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    def _missing_install(*_a: object, **_k: object):
        raise ImportError("otel bridge stripped")

    monkeypatch.setitem(
        __import__("sys").modules,
        "agentic_core.runtime.contracts.otel_lifecycle_bridge",
        type(
            "Stub",
            (),
            {"install_bridge": staticmethod(_missing_install)},
        )(),
    )
    # Force install_and_tag's inner import to fail.
    import builtins

    real_import = builtins.__import__

    def _blocked_import(name: str, *args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        if name == "agentic_core.runtime.contracts.otel_lifecycle_bridge":
            raise ImportError("stripped")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked_import)
    assert install_and_tag("apps_eval") is None


def test_install_and_tag_emits_all_six_priority_reqs(monkeypatch: pytest.MonkeyPatch) -> None:
    emitted: list[tuple[str, str]] = []

    class _FakeBridge:
        pass

    monkeypatch.setattr(
        "agentic_core.runtime.contracts.otel_lifecycle_bridge.install_bridge",
        lambda **_: _FakeBridge(),
    )

    def _capture(req_ids, *, layer: str, edge_kind: str, op: str = "", root_trace_id: str = "") -> None:  # type: ignore[no-untyped-def]
        emitted.append((tuple(req_ids)[0], edge_kind))

    monkeypatch.setattr(mod, "emit_req_evidence", _capture)
    bridge = install_and_tag("apps_rg", op="apps_rg.main")
    assert bridge is not None
    assert len(emitted) == 6
    edges = {edge for _, edge in emitted}
    assert edges == {
        "anti_bypass_observation",
        "outcome_trajectory",
        "proposal_admission",
        "memory_promotion",
        "route_contract_telemetry",
        "audit_replay_consistency",
    }
